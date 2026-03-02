"""Application entrypoint for MCP server."""

from mcp_server.transport.http import MCPHTTPTransport


def create_app() -> MCPHTTPTransport:
    """Create an app-like transport object for local execution and tests."""
    return MCPHTTPTransport()
