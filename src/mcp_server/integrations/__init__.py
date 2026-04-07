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
from mcp_server.integrations.wrappers import (
    RepresentativeEndpointWrapper,
    build_activities_list_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)
from mcp_server.integrations.youtube import (
    build_youtube_data_api_executor,
    build_youtube_data_api_request,
    build_youtube_data_api_transport,
)

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
    "build_activities_list_wrapper",
    "build_captions_download_wrapper",
    "build_captions_insert_wrapper",
    "build_captions_list_wrapper",
    "build_captions_update_wrapper",
    "build_youtube_data_api_executor",
    "build_youtube_data_api_request",
    "build_youtube_data_api_transport",
    "RepresentativeHigherLayerConsumer",
    "RequestExecution",
    "RetryPolicy",
    "build_observability_hooks",
    "normalize_upstream_error",
    "timed_execution",
]
