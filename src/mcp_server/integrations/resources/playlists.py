"""Playlists resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    PlaylistsDeleteWrapper,
    PlaylistsInsertWrapper,
    PlaylistsListWrapper,
    PlaylistsUpdateWrapper,
    build_playlists_delete_wrapper,
    build_playlists_insert_wrapper,
    build_playlists_list_wrapper,
    build_playlists_update_wrapper,
)

FAMILY_NAME = "playlists"
RESOURCE_NAMES = ("playlists",)
BUILDER_FUNCTIONS = {
    "playlists.list": build_playlists_list_wrapper,
    "playlists.insert": build_playlists_insert_wrapper,
    "playlists.update": build_playlists_update_wrapper,
    "playlists.delete": build_playlists_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistsDeleteWrapper",
    "PlaylistsInsertWrapper",
    "PlaylistsListWrapper",
    "PlaylistsUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlists_delete_wrapper",
    "build_playlists_insert_wrapper",
    "build_playlists_list_wrapper",
    "build_playlists_update_wrapper",
]
