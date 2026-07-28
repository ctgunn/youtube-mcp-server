"""Video-family scaffolding for Layer 3 public YouTube tools.

This module declares video-family placement metadata only. Concrete video tool
handlers such as ``videos_getVideo`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_layer3.families import get_layer3_family

FAMILY_SCAFFOLDING = get_layer3_family("videos")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
