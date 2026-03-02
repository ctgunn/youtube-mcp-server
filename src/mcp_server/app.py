"""Application entrypoint for MCP server."""

from __future__ import annotations

import os

from mcp_server.transport.http import MCPHTTPTransport


def load_server_metadata() -> dict:
    """Load server metadata from environment with safe defaults."""
    return {
        "version": os.getenv("MCP_SERVER_VERSION", "0.1.0"),
        "environment": os.getenv("MCP_ENVIRONMENT", "dev"),
        "build": {
            "buildId": os.getenv("MCP_BUILD_ID", "local"),
            "commit": os.getenv("MCP_BUILD_COMMIT", "unknown"),
            "buildTime": os.getenv("MCP_BUILD_TIME", "unknown"),
        },
    }


def create_app() -> MCPHTTPTransport:
    """Create an app-like transport object for local execution and tests."""
    return MCPHTTPTransport(server_metadata=load_server_metadata())
