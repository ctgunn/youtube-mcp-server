"""HTTP transport for MCP requests."""

from __future__ import annotations

from mcp_server.protocol.envelope import error_response
from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class MCPHTTPTransport:
    """Simple transport wrapper exposing /mcp request handling."""

    def __init__(self, dispatcher=None, server_metadata=None):
        self.dispatcher = dispatcher or InMemoryToolDispatcher(server_metadata=server_metadata)

    def handle(self, path: str, payload: dict) -> dict:
        if path != "/mcp":
            request_id = payload.get("id") if isinstance(payload, dict) else None
            return error_response(
                "RESOURCE_NOT_FOUND",
                "Path not found.",
                request_id=request_id,
                details={"path": path},
            )
        return route_mcp_request(payload, self.dispatcher)
