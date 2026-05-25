"""Shared scaffolding for Layer 2 YouTube MCP tools."""

from mcp_server.tools.youtube_common.contracts import (
    AuthMode,
    AvailabilityState,
    Layer2ContractError,
    Layer2ToolContract,
    derive_tool_name,
    validate_safe_public_metadata,
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
from mcp_server.tools.youtube_common.examples import REPRESENTATIVE_LAYER2_CONTRACTS
from mcp_server.tools.youtube_common.families import (
    REQUIRED_LAYER2_RESOURCE_FAMILIES,
    RESOURCE_FAMILY_REGISTRY,
    SHARED_LAYER2_HELPER_BOUNDARY,
    Layer2ResourceFamily,
    build_representative_tool_descriptor,
    get_resource_family,
)

__all__ = [
    "AuthMode",
    "AvailabilityState",
    "ErrorCategory",
    "InputConvention",
    "Layer2ContractError",
    "Layer2ResourceFamily",
    "Layer2ToolContract",
    "REPRESENTATIVE_LAYER2_CONTRACTS",
    "REQUIRED_LAYER2_RESOURCE_FAMILIES",
    "RESOURCE_FAMILY_REGISTRY",
    "ResponseBoundary",
    "ResponseBoundaryKind",
    "ResponseConvention",
    "ResponseKind",
    "SHARED_LAYER2_HELPER_BOUNDARY",
    "build_representative_tool_descriptor",
    "derive_tool_name",
    "get_resource_family",
    "sanitize_error_details",
    "validate_safe_public_metadata",
]
