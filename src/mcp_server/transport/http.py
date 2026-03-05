"""HTTP transport for MCP requests."""

from __future__ import annotations

from time import perf_counter

from mcp_server.config import StartupValidationResult
from mcp_server.health import health_payload, readiness_payload
from mcp_server.observability import InMemoryObservability, build_request_context
from mcp_server.protocol.envelope import error_response
from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class MCPHTTPTransport:
    """Simple transport wrapper exposing /mcp request handling."""

    def __init__(self, dispatcher=None, server_metadata=None, startup_validation=None):
        self.dispatcher = dispatcher or InMemoryToolDispatcher(server_metadata=server_metadata)
        self.observability = InMemoryObservability()
        self.startup_validation = startup_validation or StartupValidationResult(
            is_valid=True,
            profile="dev",
            failures=(),
            checked_at="unknown",
        )

    def handle(self, path: str, payload: dict) -> dict:
        context = build_request_context(path, payload)
        started_at = perf_counter()

        if path == "/healthz":
            response = health_payload()
        elif path == "/readyz":
            response = readiness_payload(self.startup_validation)
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
            if isinstance(response, dict):
                meta = response.get("meta")
                if isinstance(meta, dict) and not meta.get("requestId"):
                    meta["requestId"] = context.request_id

        outcome = "success"
        if isinstance(response, dict):
            if response.get("success") is False:
                outcome = "error"
            elif response.get("status") == "not_ready":
                outcome = "error"

        self.observability.record(
            context=context,
            outcome=outcome,
            latency_ms=(perf_counter() - started_at) * 1000.0,
        )
        return response
