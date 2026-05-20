"""Playlist item resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    PlaylistItemsDeleteWrapper,
    PlaylistItemsInsertWrapper,
    PlaylistItemsListWrapper,
    PlaylistItemsUpdateWrapper,
    build_playlist_items_delete_wrapper,
    build_playlist_items_insert_wrapper,
    build_playlist_items_list_wrapper,
    build_playlist_items_update_wrapper,
)

FAMILY_NAME = "playlist_items"
RESOURCE_NAMES = ("playlistItems",)
BUILDER_FUNCTIONS = {
    "playlistItems.list": build_playlist_items_list_wrapper,
    "playlistItems.insert": build_playlist_items_insert_wrapper,
    "playlistItems.update": build_playlist_items_update_wrapper,
    "playlistItems.delete": build_playlist_items_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistItemsDeleteWrapper",
    "PlaylistItemsInsertWrapper",
    "PlaylistItemsListWrapper",
    "PlaylistItemsUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlist_items_delete_wrapper",
    "build_playlist_items_insert_wrapper",
    "build_playlist_items_list_wrapper",
    "build_playlist_items_update_wrapper",
]
