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


def build_initialize_payload(request_id, client_name="client", client_version="1.0.0", *, params_override=None):
    params = {
        "clientInfo": {
            "name": client_name,
            "version": client_version,
        }
    }
    if params_override is not None:
        params = params_override
    return {
        "id": request_id,
        "method": "initialize",
        "params": params,
    }


def stream_headers(session_id=None, *, include_json=True, protocol_version=None, origin=None):
    accept = "application/json, text/event-stream" if include_json else "text/event-stream"
    headers = {"Accept": accept}
    if session_id:
        headers["MCP-Session-Id"] = session_id
    if protocol_version:
        headers["MCP-Protocol-Version"] = protocol_version
    if origin:
        headers["Origin"] = origin
    return headers


__all__ = [
    "make_app_with_dispatcher",
    "build_tool_call_payload",
    "build_initialize_payload",
    "stream_headers",
    "parse_sse_payload",
]
