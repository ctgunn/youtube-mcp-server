"""HTTP transport for MCP requests."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import TextIO

from mcp_server.config import HostedRuntimeSettings, StartupValidationResult
from mcp_server.health import RuntimeLifecycleState, health_payload, initialize_runtime_lifecycle, readiness_payload
from mcp_server.observability import InMemoryObservability, build_request_context
from mcp_server.protocol.envelope import error_response
from mcp_server.protocol.methods import route_mcp_request
from mcp_server.transport.streaming import StreamManager
from mcp_server.tools.dispatcher import InMemoryToolDispatcher

JSON_CONTENT_TYPE = "application/json"
SUPPORTED_HOSTED_METHODS = {
    "/health": {"GET"},
    "/ready": {"GET"},
    "/mcp": {"GET", "POST"},
}
SECURITY_STATUS_CODES = {
    "unauthenticated": 401,
    "invalid_credential": 403,
    "origin_denied": 403,
    "malformed_security_input": 400,
}


@dataclass(frozen=True)
class HostedRequestClassification:
    path_class: str
    method_class: str
    media_type_class: str
    body_class: str
    outcome_class: str


def _normalize_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower() or None


def classify_hosted_request(
    *,
    method: str,
    path: str,
    content_type: str | None = None,
    body_present: bool = False,
    body_valid: bool = True,
) -> HostedRequestClassification:
    normalized_method = (method or "").upper()
    if path not in SUPPORTED_HOSTED_METHODS:
        return HostedRequestClassification(
            path_class="unknown",
            method_class="unsupported",
            media_type_class="not_applicable",
            body_class="ignored",
            outcome_class="not_found",
        )

    path_class = path.lstrip("/")
    if normalized_method not in SUPPORTED_HOSTED_METHODS[path]:
        return HostedRequestClassification(
            path_class=path_class,
            method_class="unsupported",
            media_type_class="not_applicable" if path != "/mcp" else "supported",
            body_class="ignored",
            outcome_class="method_not_allowed",
        )

    if path != "/mcp":
        return HostedRequestClassification(
            path_class=path_class,
            method_class="supported",
            media_type_class="not_applicable",
            body_class="ignored",
            outcome_class="success",
        )

    normalized_content_type = _normalize_content_type(content_type)
    if normalized_content_type != JSON_CONTENT_TYPE:
        return HostedRequestClassification(
            path_class=path_class,
            method_class="supported",
            media_type_class="unsupported",
            body_class="valid" if body_valid else "malformed",
            outcome_class="unsupported_media_type",
        )

    if body_present and not body_valid:
        return HostedRequestClassification(
            path_class=path_class,
            method_class="supported",
            media_type_class="supported",
            body_class="malformed",
            outcome_class="bad_request",
        )

    return HostedRequestClassification(
        path_class=path_class,
        method_class="supported",
        media_type_class="supported",
        body_class="valid" if body_present else "missing",
        outcome_class="success",
    )


def hosted_status_code(classification: HostedRequestClassification, response: dict | None = None) -> int:
    if classification.outcome_class == "not_found":
        return 404
    if classification.outcome_class == "method_not_allowed":
        return 405
    if classification.outcome_class == "unsupported_media_type":
        return 415
    if classification.outcome_class == "bad_request":
        return 400
    if classification.path_class == "ready" and isinstance(response, dict) and response.get("status") == "not_ready":
        return 503
    if classification.path_class == "mcp" and isinstance(response, dict) and "error" in response:
        return 400
    return 200


def hosted_security_status_code(decision_category: str) -> int:
    return SECURITY_STATUS_CODES.get(decision_category, 403)


class MCPHTTPTransport:
    """Simple transport wrapper exposing /mcp request handling."""

    def __init__(
        self,
        dispatcher=None,
        server_metadata=None,
        startup_validation=None,
        runtime_lifecycle: RuntimeLifecycleState | None = None,
        runtime_settings: HostedRuntimeSettings | None = None,
        runtime_stdout: TextIO | None = None,
        runtime_stderr: TextIO | None = None,
    ):
        self.dispatcher = dispatcher or InMemoryToolDispatcher(server_metadata=server_metadata)
        self.observability = InMemoryObservability(runtime_stdout=runtime_stdout, runtime_stderr=runtime_stderr)
        self.stream_manager = StreamManager()
        self.startup_validation = startup_validation or StartupValidationResult(
            is_valid=True,
            profile="dev",
            failures=(),
            checked_at="unknown",
        )
        self.runtime_lifecycle = runtime_lifecycle or initialize_runtime_lifecycle(self.startup_validation)
        self.runtime_settings = runtime_settings

    def handle(self, path: str, payload: dict) -> dict:
        context = build_request_context(path, payload)
        started_at = perf_counter()

        if path == "/health":
            response = health_payload(self.runtime_lifecycle)
        elif path == "/ready":
            response = readiness_payload(self.startup_validation, self.runtime_lifecycle)
        elif path != "/mcp":
            response = error_response(
                "RESOURCE_NOT_FOUND",
                "Path not found.",
                request_id=context.request_id,
                details={"path": path},
            )
        else:
            mcp_payload = payload if isinstance(payload, dict) else payload
            if isinstance(mcp_payload, dict) and not mcp_payload.get("id"):
                mcp_payload = {**mcp_payload, "id": context.request_id}
            response = route_mcp_request(mcp_payload, self.dispatcher)

        outcome = "success"
        if isinstance(response, dict):
            if "error" in response:
                outcome = "error"
            elif response.get("status") == "not_ready":
                outcome = "error"

        self.observability.record(
            context=context,
            outcome=outcome,
            latency_ms=(perf_counter() - started_at) * 1000.0,
        )
        return response

    def queue_server_event(self, session_id: str, payload: dict) -> None:
        self.stream_manager.enqueue_event(
            session_id=session_id,
            payload=payload,
            event_type="message",
            payload_class="jsonrpc_notification",
        )
