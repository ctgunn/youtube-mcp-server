"""Shared Layer 3 scaffolding for higher-level public YouTube MCP tools.

The package exposes representative contracts and family placement metadata only.
Concrete public tool execution is intentionally reserved for later YT-302+
slices so this package remains a safe dependency for planning and validation.
"""

from mcp_server.tools.youtube_layer3.contracts import (
    CONCRETE_LAYER3_TOOL_EXECUTION_ENABLED,
    PLANNED_LAYER3_TOOL_NAMES,
    PLANNED_LAYER3_TOOLS_BY_FAMILY,
    SHARED_LAYER3_HELPER_BOUNDARY,
    Layer3ToolContract,
    Layer3ToolContractError,
    Layer3ToolFamily,
    infer_layer3_family,
    validate_layer3_tool_name,
    validate_safe_public_metadata,
)
from mcp_server.tools.youtube_layer3.examples import (
    REPRESENTATIVE_LAYER3_TOOL_CONTRACTS,
    build_representative_layer3_tool_descriptor,
)
from mcp_server.tools.youtube_layer3.families import (
    LAYER3_FAMILY_SCAFFOLDING,
    REQUIRED_LAYER3_FAMILIES,
    Layer3FamilyScaffolding,
    get_family_for_tool_name,
    get_layer3_family,
)
from mcp_server.tools.youtube_layer3 import channels, playlists, transcripts, videos

__all__ = [
    "CONCRETE_LAYER3_TOOL_EXECUTION_ENABLED",
    "LAYER3_FAMILY_SCAFFOLDING",
    "PLANNED_LAYER3_TOOL_NAMES",
    "PLANNED_LAYER3_TOOLS_BY_FAMILY",
    "REQUIRED_LAYER3_FAMILIES",
    "REPRESENTATIVE_LAYER3_TOOL_CONTRACTS",
    "SHARED_LAYER3_HELPER_BOUNDARY",
    "Layer3FamilyScaffolding",
    "Layer3ToolContract",
    "Layer3ToolContractError",
    "Layer3ToolFamily",
    "build_representative_layer3_tool_descriptor",
    "channels",
    "get_family_for_tool_name",
    "get_layer3_family",
    "infer_layer3_family",
    "playlists",
    "transcripts",
    "validate_layer3_tool_name",
    "validate_safe_public_metadata",
    "videos",
]
