"""Integration tests for registering and invoking ``playlistImages_list``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.playlist_images import (
    PlaylistImagesListToolError,
    build_playlist_images_insert_tool_descriptor,
    build_playlist_images_list_tool_descriptor,
)


def _register_playlist_images_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-images list tool in a fresh dispatcher."""
    descriptor = build_playlist_images_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_playlist_images_insert(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-images insert tool in a fresh dispatcher."""
    descriptor = build_playlist_images_insert_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_playlist_images_list_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistImages_list`` for playlist-scoped retrieval."""
    dispatcher = _register_playlist_images_list()

    result = dispatcher.call_tool("playlistImages_list", {"part": "snippet", "playlistId": "PL123"})

    assert result["endpoint"] == "playlistImages.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["items"][0]["id"] == "playlist-image-123"


def test_playlist_images_insert_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistImages_insert`` for playlist-image creation."""
    dispatcher = _register_playlist_images_insert()

    result = dispatcher.call_tool(
        "playlistImages_insert",
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
    )

    assert result["endpoint"] == "playlistImages.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["bodyContext"] == {"hasSnippet": True, "playlistId": "PL123"}
    assert result["mediaContext"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-image-123"
    assert "fake-image-content" not in str(result)


def test_playlist_images_list_descriptor_executes_direct_id_lookup():
    """Register and execute ``playlistImages_list`` for direct image lookup."""
    dispatcher = _register_playlist_images_list()

    result = dispatcher.call_tool("playlistImages_list", {"part": "id", "id": "playlist-image-123"})

    assert result["selector"] == {"name": "id", "value": "playlist-image-123"}
    assert result["requestedParts"] == ["id"]
    assert "paging" not in result


def test_playlist_images_list_dispatcher_rejects_missing_required_fields():
    """Reject incomplete playlist-image list calls before handler execution."""
    dispatcher = _register_playlist_images_list()

    with pytest.raises(ValueError, match="part"):
        dispatcher.call_tool("playlistImages_list", {"playlistId": "PL123"})


def test_playlist_images_list_dispatcher_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for selector-incompatible paging."""
    dispatcher = _register_playlist_images_list()

    with pytest.raises(PlaylistImagesListToolError) as exc_info:
        dispatcher.call_tool("playlistImages_list", {"part": "snippet", "id": "img-123", "pageToken": "NEXT_PAGE"})

    assert exc_info.value.category == "invalid_request"
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_playlist_images_list_dispatcher_propagates_safe_access_failures():
    """Propagate safe upstream access failures from the registered handler."""
    class FailingWrapper:
        """Raise an access failure from a registered dispatcher tool."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized access failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="playlist image access required",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"field": "playlistId", "oauth_token": "secret"},
            )

    dispatcher = _register_playlist_images_list(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesListToolError) as exc_info:
        dispatcher.call_tool("playlistImages_list", {"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "playlistId"}
