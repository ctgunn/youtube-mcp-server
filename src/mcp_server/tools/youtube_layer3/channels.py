"""Channel-family scaffolding for Layer 3 public YouTube tools.

This module declares channel-family placement metadata only. Concrete channel
tool handlers such as ``channels_findCreators`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_layer3.families import get_layer3_family

FAMILY_SCAFFOLDING = get_layer3_family("channels")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
