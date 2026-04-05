"""Internal integration foundations for layered YouTube capabilities."""

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.consumer import RepresentativeHigherLayerConsumer
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.executor import (
    IntegrationExecutor,
    IntegrationHooks,
    RequestExecution,
    build_observability_hooks,
    timed_execution,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper

__all__ = [
    "AuthContext",
    "AuthMode",
    "CredentialBundle",
    "EndpointMetadata",
    "EndpointRequestShape",
    "IntegrationExecutor",
    "IntegrationHooks",
    "NormalizedUpstreamError",
    "RepresentativeEndpointWrapper",
    "RepresentativeHigherLayerConsumer",
    "RequestExecution",
    "RetryPolicy",
    "build_observability_hooks",
    "normalize_upstream_error",
    "timed_execution",
]
