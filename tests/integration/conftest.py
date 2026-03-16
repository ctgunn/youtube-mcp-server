import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.transport.http import MCPHTTPTransport
from tests.unit.conftest import parse_sse_payload


def make_app_with_dispatcher(dispatcher=None):
    if dispatcher is None:
        os.environ["MCP_ENVIRONMENT"] = "dev"
        return create_app()
    return MCPHTTPTransport(dispatcher=dispatcher)


def build_tool_call_payload(request_id, tool_name, arguments=None):
    return {
        "id": request_id,
        "method": "tools/call",
        "params": {
            "toolName": tool_name,
            "arguments": arguments or {},
        },
    }


def stream_headers(session_id=None, *, include_json=True):
    accept = "application/json, text/event-stream" if include_json else "text/event-stream"
    headers = {"Accept": accept}
    if session_id:
        headers["MCP-Session-Id"] = session_id
    return headers


__all__ = ["make_app_with_dispatcher", "build_tool_call_payload", "stream_headers", "parse_sse_payload"]
