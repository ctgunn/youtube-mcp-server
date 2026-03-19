"""Session and SSE helpers for streamable MCP transport."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
import json
import uuid

from mcp_server.config import HostedSessionSettings
from mcp_server.transport.session_store import BaseSessionStore, InMemorySessionStore, SessionStoreStatus, create_session_store

SSE_CONTENT_TYPE = "text/event-stream"
JSON_CONTENT_TYPE = "application/json"
MCP_SESSION_ID_HEADER = "MCP-Session-Id"
MCP_PROTOCOL_VERSION_HEADER = "MCP-Protocol-Version"
SUPPORTED_MCP_PROTOCOL_VERSIONS = ("2025-11-25",)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _add_seconds(timestamp: str, seconds: int) -> str:
    return (datetime.fromisoformat(timestamp) + timedelta(seconds=seconds)).isoformat()


def _is_past(timestamp: str | None) -> bool:
    if not timestamp:
        return False
    return datetime.fromisoformat(timestamp) <= datetime.now(timezone.utc)


def generate_session_id() -> str:
    return uuid.uuid4().hex


@dataclass
class StreamEvent:
    event_id: str
    stream_id: str
    event_type: str
    payload_class: str
    payload: dict | None
    created_at: str
    delivery_state: str = "queued"


@dataclass
class StreamChannel:
    stream_id: str
    session_id: str
    origin_method: str
    state: str
    created_at: str
    last_event_id: str | None = None
    retry_ms: int | None = None
    pending_response_id: str | None = None
    replay_window_ends_at: str | None = None
    events: list[StreamEvent] = field(default_factory=list)


@dataclass
class HostedMCPSession:
    session_id: str
    protocol_version: str
    created_at: str
    last_activity_at: str
    expires_at: str
    state: str
    continuity_mode: str
    client_metadata: dict | None = None
    stream_ids: list[str] = field(default_factory=list)


class InvalidSessionError(KeyError):
    """Raised when a session does not exist."""


class ExpiredSessionError(KeyError):
    """Raised when a session exists but can no longer be continued."""


class ReplayUnavailableError(KeyError):
    """Raised when a replay cursor is no longer available."""


class StreamManager:
    """Tracks hosted sessions and stream events through a configurable backing store."""

    def __init__(
        self,
        *,
        store: BaseSessionStore | None = None,
        session_ttl_seconds: int = 1800,
        replay_ttl_seconds: int = 300,
    ):
        self._store = store or InMemorySessionStore()
        self._session_ttl_seconds = session_ttl_seconds
        self._replay_ttl_seconds = replay_ttl_seconds

    @classmethod
    def from_session_settings(cls, settings: HostedSessionSettings) -> "StreamManager":
        return cls(
            store=create_session_store(backend=settings.backend, store_url=settings.store_url),
            session_ttl_seconds=settings.session_ttl_seconds,
            replay_ttl_seconds=settings.replay_ttl_seconds,
        )

    @property
    def sessions(self) -> dict[str, HostedMCPSession]:
        return {
            session_id: self._session_from_record(record)
            for session_id, record in self._store.list_sessions().items()
            if record.get("state") != "closed"
        }

    @property
    def streams(self) -> dict[str, StreamChannel]:
        return {
            stream_id: self._stream_from_record(record)
            for stream_id, record in self._store.list_streams().items()
        }

    def session_store_status(self) -> SessionStoreStatus:
        return self._store.status()

    def durability_status(self, *, required: bool) -> dict[str, object]:
        status = self.session_store_status()
        available = status.healthy and (status.shared or not required)
        if required and not status.shared:
            available = False
        reason = None
        if not available:
            if required and not status.shared:
                reason = {
                    "code": "SESSION_DURABILITY_UNAVAILABLE",
                    "message": "Durable hosted sessions require a shared session backend.",
                }
            else:
                reason = status.reason or {
                    "code": "SESSION_DURABILITY_UNAVAILABLE",
                    "message": "Durable hosted session state is not available.",
                }
        return {
            "backend": status.backend,
            "configured": status.configured,
            "healthy": status.healthy,
            "shared": status.shared,
            "available": available,
            "continuityMode": status.continuity_mode,
            "supportedTopology": status.supported_topology,
            "reason": reason,
        }

    def create_session(self, *, protocol_version: str, client_metadata: dict | None = None) -> HostedMCPSession:
        now = _timestamp()
        status = self.session_store_status()
        session = HostedMCPSession(
            session_id=generate_session_id(),
            protocol_version=protocol_version,
            created_at=now,
            last_activity_at=now,
            expires_at=_add_seconds(now, self._session_ttl_seconds),
            state="active",
            continuity_mode=status.continuity_mode,
            client_metadata=client_metadata,
        )
        self._store.save_session(session.session_id, self._session_record(session))
        return session

    def get_session(self, session_id: str) -> HostedMCPSession:
        session = self._load_session(session_id)
        if session.state == "closed":
            raise InvalidSessionError(session_id)
        if _is_past(session.expires_at) or session.state == "expired":
            session.state = "expired"
            self._store.save_session(session.session_id, self._session_record(session))
            raise ExpiredSessionError(session_id)
        return session

    def has_session(self, session_id: str) -> bool:
        try:
            self.get_session(session_id)
            return True
        except (InvalidSessionError, ExpiredSessionError):
            return False

    def touch_session(self, session_id: str) -> HostedMCPSession:
        session = self.get_session(session_id)
        session.last_activity_at = _timestamp()
        session.expires_at = _add_seconds(session.last_activity_at, self._session_ttl_seconds)
        self._store.save_session(session.session_id, self._session_record(session))
        return session

    def open_stream(
        self,
        session_id: str,
        *,
        origin_method: str,
        pending_response_id: str | None = None,
    ) -> StreamChannel:
        session = self.touch_session(session_id)
        if origin_method == "GET":
            for stream_id in reversed(session.stream_ids):
                stream = self._load_stream_optional(stream_id)
                if stream and stream.origin_method == "GET" and stream.state in {"open", "idle", "reconnecting"}:
                    if not _is_past(stream.replay_window_ends_at):
                        stream.state = "open"
                        self._store.save_stream(stream.stream_id, self._stream_record(stream))
                        return stream

        stream = StreamChannel(
            stream_id=uuid.uuid4().hex,
            session_id=session_id,
            origin_method=origin_method,
            state="open",
            created_at=_timestamp(),
            pending_response_id=pending_response_id,
            replay_window_ends_at=_add_seconds(_timestamp(), self._replay_ttl_seconds),
        )
        session.stream_ids.append(stream.stream_id)
        self._store.save_session(session.session_id, self._session_record(session))
        self._store.save_stream(stream.stream_id, self._stream_record(stream))
        return stream

    def close_stream(self, stream_id: str, *, completed: bool = False) -> None:
        stream = self._load_stream_optional(stream_id)
        if stream is None:
            return
        stream.state = "completed" if completed else "closed"
        self._store.save_stream(stream.stream_id, self._stream_record(stream))

    def enqueue_event(
        self,
        *,
        session_id: str,
        payload: dict | None,
        event_type: str = "message",
        payload_class: str = "jsonrpc_notification",
        stream_id: str | None = None,
    ) -> StreamEvent:
        if stream_id is None:
            stream = self.open_stream(session_id, origin_method="GET")
        else:
            stream = self._load_stream(stream_id)
            self.touch_session(session_id)
        event = StreamEvent(
            event_id=f"{stream.stream_id}:{len(stream.events) + 1}",
            stream_id=stream.stream_id,
            event_type=event_type,
            payload_class=payload_class,
            payload=payload,
            created_at=_timestamp(),
        )
        stream.events.append(event)
        stream.last_event_id = event.event_id
        stream.replay_window_ends_at = _add_seconds(_timestamp(), self._replay_ttl_seconds)
        self._store.save_stream(stream.stream_id, self._stream_record(stream))
        return event

    def ensure_primer_event(self, stream: StreamChannel) -> StreamEvent:
        if stream.events:
            return stream.events[0]
        return self.enqueue_event(
            session_id=stream.session_id,
            payload=None,
            event_type="message",
            payload_class="empty",
            stream_id=stream.stream_id,
        )

    def events_after(self, session_id: str, last_event_id: str | None = None) -> tuple[StreamChannel, list[StreamEvent]]:
        session = self.get_session(session_id)
        candidate_streams: list[StreamChannel] = []
        expired_cursor_seen = False
        for stream_id in session.stream_ids:
            stream = self._load_stream_optional(stream_id)
            if stream is None:
                expired_cursor_seen = True
                continue
            if _is_past(stream.replay_window_ends_at):
                expired_cursor_seen = True
                continue
            candidate_streams.append(stream)

        if not candidate_streams and last_event_id:
            raise ReplayUnavailableError(last_event_id)

        if not candidate_streams:
            stream = self.open_stream(session_id, origin_method="GET")
            return stream, [self.ensure_primer_event(stream)]

        if last_event_id:
            for stream in reversed(candidate_streams):
                for index, event in enumerate(stream.events):
                    if event.event_id == last_event_id:
                        stream.state = "open"
                        replay = stream.events[index + 1 :]
                        for item in replay:
                            item.delivery_state = "replayed"
                        self._store.save_stream(stream.stream_id, self._stream_record(stream))
                        return stream, replay or [self.ensure_primer_event(stream)]
            if expired_cursor_seen or candidate_streams:
                raise ReplayUnavailableError(last_event_id)

        stream = self.open_stream(session_id, origin_method="GET")
        return stream, list(stream.events) or [self.ensure_primer_event(stream)]

    def build_post_response_stream(self, session_id: str, request_id: str, response_payload: dict) -> tuple[StreamChannel, list[StreamEvent]]:
        stream = self.open_stream(session_id, origin_method="POST", pending_response_id=request_id)
        primer = self.ensure_primer_event(stream)
        response_event = self.enqueue_event(
            session_id=session_id,
            payload=response_payload,
            event_type="message",
            payload_class="jsonrpc_response",
            stream_id=stream.stream_id,
        )
        response_event.delivery_state = "sent"
        primer.delivery_state = "sent"
        stream = self._load_stream(stream.stream_id)
        stream.events[0].delivery_state = "sent"
        stream.events[-1].delivery_state = "sent"
        self._store.save_stream(stream.stream_id, self._stream_record(stream))
        self.close_stream(stream.stream_id, completed=True)
        refreshed = self._load_stream(stream.stream_id)
        return refreshed, refreshed.events[:2]

    def _load_session(self, session_id: str) -> HostedMCPSession:
        record = self._store.load_session(session_id)
        if record is None:
            raise InvalidSessionError(session_id)
        return self._session_from_record(record)

    def _load_stream(self, stream_id: str) -> StreamChannel:
        record = self._store.load_stream(stream_id)
        if record is None:
            raise ReplayUnavailableError(stream_id)
        return self._stream_from_record(record)

    def _load_stream_optional(self, stream_id: str) -> StreamChannel | None:
        record = self._store.load_stream(stream_id)
        return self._stream_from_record(record) if record is not None else None

    def _session_record(self, session: HostedMCPSession) -> dict:
        return asdict(session)

    def _stream_record(self, stream: StreamChannel) -> dict:
        payload = asdict(stream)
        payload["events"] = [asdict(event) for event in stream.events]
        return payload

    def _session_from_record(self, record: dict) -> HostedMCPSession:
        return HostedMCPSession(
            session_id=record["session_id"],
            protocol_version=record["protocol_version"],
            created_at=record["created_at"],
            last_activity_at=record["last_activity_at"],
            expires_at=record.get("expires_at", record["last_activity_at"]),
            state=record["state"],
            continuity_mode=record.get("continuity_mode", "process_local"),
            client_metadata=record.get("client_metadata"),
            stream_ids=list(record.get("stream_ids", [])),
        )

    def _stream_from_record(self, record: dict) -> StreamChannel:
        return StreamChannel(
            stream_id=record["stream_id"],
            session_id=record["session_id"],
            origin_method=record["origin_method"],
            state=record["state"],
            created_at=record["created_at"],
            last_event_id=record.get("last_event_id"),
            retry_ms=record.get("retry_ms"),
            pending_response_id=record.get("pending_response_id"),
            replay_window_ends_at=record.get("replay_window_ends_at"),
            events=[
                StreamEvent(
                    event_id=event["event_id"],
                    stream_id=event["stream_id"],
                    event_type=event["event_type"],
                    payload_class=event["payload_class"],
                    payload=event.get("payload"),
                    created_at=event["created_at"],
                    delivery_state=event.get("delivery_state", "queued"),
                )
                for event in record.get("events", [])
            ],
        )


def encode_sse(events: list[StreamEvent]) -> str:
    lines: list[str] = []
    for event in events:
        lines.append(f"id: {event.event_id}")
        if event.event_type and event.event_type != "message":
            lines.append(f"event: {event.event_type}")
        data = "" if event.payload is None else json.dumps(event.payload, sort_keys=True)
        lines.append(f"data: {data}")
        lines.append("")
    return "\n".join(lines)


def normalize_accept_header(header_value: str | None) -> set[str]:
    if not header_value:
        return set()
    values = set()
    for part in header_value.split(","):
        token = part.split(";", 1)[0].strip().lower()
        if token:
            values.add(token)
    return values
