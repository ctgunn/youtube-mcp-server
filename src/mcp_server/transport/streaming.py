"""In-memory session and SSE helpers for streamable MCP transport."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import uuid

SSE_CONTENT_TYPE = "text/event-stream"
JSON_CONTENT_TYPE = "application/json"
MCP_SESSION_ID_HEADER = "MCP-Session-Id"
MCP_PROTOCOL_VERSION_HEADER = "MCP-Protocol-Version"
SUPPORTED_MCP_PROTOCOL_VERSIONS = ("2025-11-25",)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    events: list[StreamEvent] = field(default_factory=list)


@dataclass
class HostedMCPSession:
    session_id: str
    protocol_version: str
    created_at: str
    last_activity_at: str
    state: str
    client_metadata: dict | None = None
    stream_ids: list[str] = field(default_factory=list)


class InvalidSessionError(KeyError):
    """Raised when a session does not exist."""


class StreamManager:
    """Tracks active sessions and per-stream SSE events in memory."""

    def __init__(self):
        self._sessions: dict[str, HostedMCPSession] = {}
        self._streams: dict[str, StreamChannel] = {}

    @property
    def sessions(self) -> dict[str, HostedMCPSession]:
        return self._sessions

    @property
    def streams(self) -> dict[str, StreamChannel]:
        return self._streams

    def create_session(self, *, protocol_version: str, client_metadata: dict | None = None) -> HostedMCPSession:
        now = _timestamp()
        session = HostedMCPSession(
            session_id=generate_session_id(),
            protocol_version=protocol_version,
            created_at=now,
            last_activity_at=now,
            state="active",
            client_metadata=client_metadata,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> HostedMCPSession:
        session = self._sessions.get(session_id)
        if session is None or session.state == "closed":
            raise InvalidSessionError(session_id)
        return session

    def has_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        return session is not None and session.state != "closed"

    def touch_session(self, session_id: str) -> HostedMCPSession:
        session = self.get_session(session_id)
        session.last_activity_at = _timestamp()
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
                stream = self._streams.get(stream_id)
                if stream and stream.origin_method == "GET" and stream.state in {"open", "idle", "reconnecting"}:
                    stream.state = "open"
                    return stream

        stream = StreamChannel(
            stream_id=uuid.uuid4().hex,
            session_id=session_id,
            origin_method=origin_method,
            state="open",
            created_at=_timestamp(),
            pending_response_id=pending_response_id,
        )
        self._streams[stream.stream_id] = stream
        session.stream_ids.append(stream.stream_id)
        return stream

    def close_stream(self, stream_id: str, *, completed: bool = False) -> None:
        stream = self._streams.get(stream_id)
        if stream is None:
            return
        stream.state = "completed" if completed else "closed"

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
            stream = self._streams[stream_id]
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
        candidate_streams = [self._streams[stream_id] for stream_id in session.stream_ids if stream_id in self._streams]
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
                        return stream, replay or [self.ensure_primer_event(stream)]

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
        self.close_stream(stream.stream_id, completed=True)
        return stream, [primer, response_event]


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
