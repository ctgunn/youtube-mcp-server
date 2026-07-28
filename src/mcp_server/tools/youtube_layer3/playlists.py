"""Playlist-family scaffolding for Layer 3 public YouTube tools.

This module declares playlist-family placement metadata only. Concrete playlist
tool handlers such as ``playlists_searchItems`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_layer3.families import get_layer3_family

FAMILY_SCAFFOLDING = get_layer3_family("playlists")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
