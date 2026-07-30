"""Video-family scaffolding for higher-level public YouTube tools.

This module declares video-family placement metadata only. Concrete video tool
handlers such as ``videos_getVideo`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("videos")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
