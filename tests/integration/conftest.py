import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.transport.http import MCPHTTPTransport


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
