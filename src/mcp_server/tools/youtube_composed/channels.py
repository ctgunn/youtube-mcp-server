"""Channel-family scaffolding for higher-level public YouTube tools.

This module declares channel-family placement metadata only. Concrete channel
tool handlers such as ``channels_findCreators`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("channels")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
