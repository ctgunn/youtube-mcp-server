"""Shared scaffolding for endpoint-backed YouTube MCP tools."""

from mcp_server.tools.youtube_common.contracts import (
    AuthMode,
    AvailabilityState,
    validate_safe_public_metadata,
    YouTubeToolContract,
    YouTubeToolContractError,
    derive_tool_name,
)
from mcp_server.tools.youtube_common.conventions import (
    ErrorCategory,
    InputConvention,
    ResponseBoundary,
    ResponseBoundaryKind,
    ResponseConvention,
    ResponseKind,
    sanitize_error_details,
)
from mcp_server.tools.youtube_common.examples import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
from mcp_server.tools.youtube_common.families import (
    REQUIRED_YOUTUBE_RESOURCE_FAMILIES,
    RESOURCE_FAMILY_REGISTRY,
    SHARED_YOUTUBE_HELPER_BOUNDARY,
    YouTubeResourceFamily,
    build_representative_tool_descriptor,
    get_resource_family,
)

__all__ = [
    "AuthMode",
    "AvailabilityState",
    "ErrorCategory",
    "InputConvention",
    "YouTubeToolContractError",
    "YouTubeResourceFamily",
    "YouTubeToolContract",
    "REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS",
    "REQUIRED_YOUTUBE_RESOURCE_FAMILIES",
    "RESOURCE_FAMILY_REGISTRY",
    "ResponseBoundary",
    "ResponseBoundaryKind",
    "ResponseConvention",
    "ResponseKind",
    "SHARED_YOUTUBE_HELPER_BOUNDARY",
    "build_representative_tool_descriptor",
    "derive_tool_name",
    "get_resource_family",
    "sanitize_error_details",
    "validate_safe_public_metadata",
]
