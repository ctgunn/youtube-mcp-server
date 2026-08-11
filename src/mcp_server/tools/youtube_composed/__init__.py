"""Shared scaffolding for higher-level public YouTube MCP tools.

The package exposes representative contracts and family placement metadata only.
Concrete public tool execution is intentionally reserved for later YT-302+
slices so this package remains a safe dependency for planning and validation.
"""

from mcp_server.tools.youtube_composed.contracts import (
    CONCRETE_TOOL_EXECUTION_ENABLED,
    PLANNED_TOOL_NAMES,
    PLANNED_TOOLS_BY_FAMILY,
    SHARED_HELPER_BOUNDARY,
    ToolContract,
    ToolContractError,
    ToolFamily,
    infer_family,
    validate_tool_name,
    validate_safe_public_metadata,
)
from mcp_server.tools.youtube_composed.examples import (
    REPRESENTATIVE_TOOL_CONTRACTS,
    build_representative_tool_descriptor,
)
from mcp_server.tools.youtube_composed.families import (
    FAMILY_SCAFFOLDING,
    REQUIRED_FAMILIES,
    FamilyScaffolding,
    get_family_for_tool_name,
    get_family,
)
from . import channels, playlists, transcripts, videos
from .videos import (
    VIDEOS_GET_VIDEO_INPUT_SCHEMA,
    VIDEOS_GET_VIDEO_TOOL_NAME,
    VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA,
    VIDEOS_SEARCH_VIDEOS_TOOL_NAME,
    VideosGetVideoToolError,
    VideosSearchVideosToolError,
    build_videos_get_video_handler,
    build_videos_get_video_metadata,
    build_videos_get_video_tool_descriptor,
    build_videos_search_videos_handler,
    build_videos_search_videos_metadata,
    build_videos_search_videos_tool_descriptor,
    normalize_videos_get_video_result,
    validate_videos_get_video_arguments,
    validate_videos_search_videos_arguments,
)

__all__ = [
    "CONCRETE_TOOL_EXECUTION_ENABLED",
    "FAMILY_SCAFFOLDING",
    "PLANNED_TOOL_NAMES",
    "PLANNED_TOOLS_BY_FAMILY",
    "REQUIRED_FAMILIES",
    "REPRESENTATIVE_TOOL_CONTRACTS",
    "SHARED_HELPER_BOUNDARY",
    "FamilyScaffolding",
    "ToolContract",
    "ToolContractError",
    "ToolFamily",
    "VIDEOS_GET_VIDEO_INPUT_SCHEMA",
    "VIDEOS_GET_VIDEO_TOOL_NAME",
    "VIDEOS_SEARCH_VIDEOS_INPUT_SCHEMA",
    "VIDEOS_SEARCH_VIDEOS_TOOL_NAME",
    "VideosGetVideoToolError",
    "VideosSearchVideosToolError",
    "build_representative_tool_descriptor",
    "build_videos_get_video_handler",
    "build_videos_get_video_metadata",
    "build_videos_get_video_tool_descriptor",
    "build_videos_search_videos_handler",
    "build_videos_search_videos_metadata",
    "build_videos_search_videos_tool_descriptor",
    "channels",
    "get_family",
    "get_family_for_tool_name",
    "infer_family",
    "playlists",
    "normalize_videos_get_video_result",
    "transcripts",
    "validate_tool_name",
    "validate_safe_public_metadata",
    "validate_videos_get_video_arguments",
    "validate_videos_search_videos_arguments",
    "videos",
]
