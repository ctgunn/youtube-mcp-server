"""Application entrypoint for MCP server."""

from __future__ import annotations

import os
from typing import Mapping, TextIO

from mcp_server.config import ConfigValidationError, StartupValidationResult, ensure_runtime_config
from mcp_server.transport.http import MCPHTTPTransport


def load_server_metadata(env: Mapping[str, str]) -> dict:
    """Load server metadata from environment with safe defaults."""
    return {
        "version": env.get("MCP_SERVER_VERSION", "0.1.0"),
        "environment": env.get("MCP_ENVIRONMENT", "dev"),
        "build": {
            "buildId": env.get("MCP_BUILD_ID", "local"),
            "commit": env.get("MCP_BUILD_COMMIT", "unknown"),
            "buildTime": env.get("MCP_BUILD_TIME", "unknown"),
        },
    }


def _build_startup_error(validation: StartupValidationResult) -> str:
    failure_keys = ", ".join(item.key for item in validation.failures) or "unknown"
    return f"Startup configuration validation failed for profile '{validation.profile}': {failure_keys}"


def create_app(
    env: Mapping[str, str] | None = None,
    validate_startup: bool = True,
    runtime_stdout: TextIO | None = None,
    runtime_stderr: TextIO | None = None,
) -> MCPHTTPTransport:
    """Create an app-like transport object for local execution and tests."""
    runtime_env = dict(os.environ if env is None else env)
    try:
        validation = ensure_runtime_config(runtime_env)
    except ConfigValidationError as exc:
        if validate_startup:
            raise RuntimeError(_build_startup_error(exc.result)) from exc
        validation = exc.result

    return MCPHTTPTransport(
        server_metadata=load_server_metadata(runtime_env),
        startup_validation=validation,
        runtime_stdout=runtime_stdout,
        runtime_stderr=runtime_stderr,
    )
