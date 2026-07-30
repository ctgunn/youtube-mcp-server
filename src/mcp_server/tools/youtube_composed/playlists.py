"""Playlist-family scaffolding for higher-level public YouTube tools.

This module declares playlist-family placement metadata only. Concrete playlist
tool handlers such as ``playlists_searchItems`` belong to later YT-302+ slices.
"""

from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("playlists")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
