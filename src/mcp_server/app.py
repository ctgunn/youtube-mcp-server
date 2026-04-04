"""Application entrypoint for MCP server."""

from __future__ import annotations

import os
from typing import Mapping, TextIO

from mcp_server.config import ConfigValidationError, StartupValidationResult, ensure_runtime_config, load_hosted_runtime_settings
from mcp_server.health import initialize_runtime_lifecycle
from mcp_server.transport.http import MCPHTTPTransport


def load_server_metadata(env: Mapping[str, str]) -> dict:
    """Load server metadata from environment with safe defaults.

    :param env: Environment-style mapping containing optional server metadata.
    :return: A normalized metadata dictionary used by the transport layer.
    """
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
    """Build a stable startup validation error message.

    :param validation: Failed startup validation result.
    :return: Human-readable error text summarizing the invalid keys.
    """
    failure_keys = ", ".join(item.key for item in validation.failures) or "unknown"
    return f"Startup configuration validation failed for profile '{validation.profile}': {failure_keys}"


def create_app(
    env: Mapping[str, str] | None = None,
    validate_startup: bool = True,
    runtime_stdout: TextIO | None = None,
    runtime_stderr: TextIO | None = None,
) -> MCPHTTPTransport:
    """Create the in-process transport used by local flows and tests.

    :param env: Optional environment mapping to evaluate instead of ``os.environ``.
    :param validate_startup: Whether invalid startup config should raise immediately.
    :param runtime_stdout: Optional structured-log stdout stream.
    :param runtime_stderr: Optional structured-log stderr stream.
    :return: Configured HTTP transport instance.
    :raises RuntimeError: If startup validation fails while strict validation is enabled.
    """
    runtime_env = dict(os.environ if env is None else env)
    runtime_settings = load_hosted_runtime_settings(runtime_env)
    try:
        validation = ensure_runtime_config(runtime_env)
    except ConfigValidationError as exc:
        if validate_startup:
            raise RuntimeError(_build_startup_error(exc.result)) from exc
        validation = exc.result
    lifecycle = initialize_runtime_lifecycle(validation)

    return MCPHTTPTransport(
        server_metadata=load_server_metadata(runtime_env),
        startup_validation=validation,
        runtime_lifecycle=lifecycle,
        runtime_settings=runtime_settings,
        runtime_env=runtime_env,
        runtime_stdout=runtime_stdout,
        runtime_stderr=runtime_stderr,
    )
