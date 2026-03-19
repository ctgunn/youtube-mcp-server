"""Shared session-store abstractions for hosted MCP session durability."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from threading import RLock
from typing import Any

try:  # pragma: no cover - optional dependency
    import redis
except ImportError:  # pragma: no cover - optional dependency
    redis = None


@dataclass(frozen=True)
class SessionStoreStatus:
    backend: str
    configured: bool
    healthy: bool
    shared: bool
    reason: dict[str, str] | None = None

    @property
    def continuity_mode(self) -> str:
        if self.shared and self.healthy:
            return "shared_state"
        return "process_local"

    @property
    def supported_topology(self) -> str:
        if self.shared and self.healthy:
            return "multi_instance_shared_state"
        return "single_instance_only"


class BaseSessionStore:
    def status(self) -> SessionStoreStatus:
        raise NotImplementedError

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def save_session(self, session_id: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    def load_stream(self, stream_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def save_stream(self, stream_id: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    def list_sessions(self) -> dict[str, dict[str, Any]]:
        return {}

    def list_streams(self) -> dict[str, dict[str, Any]]:
        return {}


_SHARED_MEMORY_STORES: dict[str, dict[str, dict[str, Any]]] = {}
_SHARED_MEMORY_LOCK = RLock()


def reset_memory_session_store_registry() -> None:
    with _SHARED_MEMORY_LOCK:
        _SHARED_MEMORY_STORES.clear()


class InMemorySessionStore(BaseSessionStore):
    def __init__(self, *, shared_name: str | None = None):
        self._shared_name = shared_name
        if shared_name:
            with _SHARED_MEMORY_LOCK:
                state = _SHARED_MEMORY_STORES.setdefault(shared_name, {"sessions": {}, "streams": {}})
            self._state = state
            self._lock = _SHARED_MEMORY_LOCK
        else:
            self._state = {"sessions": {}, "streams": {}}
            self._lock = RLock()

    def status(self) -> SessionStoreStatus:
        return SessionStoreStatus(
            backend="memory",
            configured=True,
            healthy=True,
            shared=bool(self._shared_name),
        )

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            payload = self._state["sessions"].get(session_id)
            return deepcopy(payload) if payload is not None else None

    def save_session(self, session_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._state["sessions"][session_id] = deepcopy(payload)

    def load_stream(self, stream_id: str) -> dict[str, Any] | None:
        with self._lock:
            payload = self._state["streams"].get(stream_id)
            return deepcopy(payload) if payload is not None else None

    def save_stream(self, stream_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._state["streams"][stream_id] = deepcopy(payload)

    def list_sessions(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return deepcopy(self._state["sessions"])

    def list_streams(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return deepcopy(self._state["streams"])


class RedisSessionStore(BaseSessionStore):
    def __init__(self, store_url: str | None):
        self._store_url = store_url
        self._client = None
        self._status = SessionStoreStatus(
            backend="redis",
            configured=bool(store_url),
            healthy=False,
            shared=True,
            reason={"code": "SESSION_STORE_UNAVAILABLE", "message": "Redis-backed durable session store is not available."},
        )
        if not store_url:
            self._status = SessionStoreStatus(
                backend="redis",
                configured=False,
                healthy=False,
                shared=True,
                reason={"code": "SESSION_STORE_NOT_CONFIGURED", "message": "Redis-backed durable session store URL is missing."},
            )
            return
        if redis is None:
            self._status = SessionStoreStatus(
                backend="redis",
                configured=True,
                healthy=False,
                shared=True,
                reason={"code": "SESSION_STORE_CLIENT_MISSING", "message": "Redis client dependency is not installed."},
            )
            return
        try:  # pragma: no cover - exercised only when redis is available
            self._client = redis.from_url(store_url, decode_responses=True)
            self._client.ping()
            self._status = SessionStoreStatus(backend="redis", configured=True, healthy=True, shared=True)
        except Exception as exc:  # pragma: no cover - depends on external runtime
            self._status = SessionStoreStatus(
                backend="redis",
                configured=True,
                healthy=False,
                shared=True,
                reason={"code": "SESSION_STORE_UNAVAILABLE", "message": f"Redis-backed durable session store is unavailable: {exc}"},
            )

    def status(self) -> SessionStoreStatus:
        return self._status

    def _get_json(self, key: str) -> dict[str, Any] | None:
        if self._client is None:
            return None
        raw = self._client.get(key)
        if raw is None:
            return None
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else None

    def _set_json(self, key: str, payload: dict[str, Any]) -> None:
        if self._client is None:
            return
        self._client.set(key, json.dumps(payload, sort_keys=True))

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        return self._get_json(f"mcp:session:{session_id}")

    def save_session(self, session_id: str, payload: dict[str, Any]) -> None:
        self._set_json(f"mcp:session:{session_id}", payload)

    def load_stream(self, stream_id: str) -> dict[str, Any] | None:
        return self._get_json(f"mcp:stream:{stream_id}")

    def save_stream(self, stream_id: str, payload: dict[str, Any]) -> None:
        self._set_json(f"mcp:stream:{stream_id}", payload)


def create_session_store(*, backend: str, store_url: str | None) -> BaseSessionStore:
    normalized_backend = (backend or "memory").strip().lower()
    if normalized_backend == "redis":
        return RedisSessionStore(store_url)
    shared_name = None
    if store_url and store_url.startswith("memory://"):
        shared_name = store_url
    return InMemorySessionStore(shared_name=shared_name)
