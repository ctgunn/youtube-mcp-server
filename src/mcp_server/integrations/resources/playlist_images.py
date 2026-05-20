"""Playlist image resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    PlaylistImagesDeleteWrapper,
    PlaylistImagesInsertWrapper,
    PlaylistImagesListWrapper,
    PlaylistImagesUpdateWrapper,
    build_playlist_images_delete_wrapper,
    build_playlist_images_insert_wrapper,
    build_playlist_images_list_wrapper,
    build_playlist_images_update_wrapper,
)

FAMILY_NAME = "playlist_images"
RESOURCE_NAMES = ("playlistImages",)
BUILDER_FUNCTIONS = {
    "playlistImages.list": build_playlist_images_list_wrapper,
    "playlistImages.insert": build_playlist_images_insert_wrapper,
    "playlistImages.update": build_playlist_images_update_wrapper,
    "playlistImages.delete": build_playlist_images_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistImagesDeleteWrapper",
    "PlaylistImagesInsertWrapper",
    "PlaylistImagesListWrapper",
    "PlaylistImagesUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlist_images_delete_wrapper",
    "build_playlist_images_insert_wrapper",
    "build_playlist_images_list_wrapper",
    "build_playlist_images_update_wrapper",
]
