"""Integration tests for registering and invoking ``playlistItems_list``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.playlist_items import (
    PlaylistItemsListToolError,
    build_playlist_items_list_tool_descriptor,
)


def _register_playlist_items_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-items list tool in a fresh dispatcher."""
    descriptor = build_playlist_items_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_playlist_items_list_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistItems_list`` for playlist-scoped retrieval."""
    dispatcher = _register_playlist_items_list()

    result = dispatcher.call_tool("playlistItems_list", {"part": "snippet,contentDetails", "playlistId": "PL123"})

    assert result["endpoint"] == "playlistItems.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"][0]["id"] == "playlist-item-123"
    assert result["items"][0]["snippet"]["playlistId"] == "PL123"


def test_playlist_items_list_descriptor_executes_direct_id_lookup():
    """Register and execute ``playlistItems_list`` for direct item lookup."""
    dispatcher = _register_playlist_items_list()

    result = dispatcher.call_tool("playlistItems_list", {"part": "id,snippet", "id": "playlist-item-123"})

    assert result["selector"] == {"name": "id", "value": "playlist-item-123"}
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["items"][0]["id"] == "playlist-item-123"
    assert "paging" not in result


def test_playlist_items_list_descriptor_executes_paged_playlist_lookup():
    """Register and execute ``playlistItems_list`` with playlist-scoped paging."""
    dispatcher = _register_playlist_items_list()

    result = dispatcher.call_tool(
        "playlistItems_list",
        {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
    )

    assert result["paging"] == {"pageToken": "NEXT_PAGE", "maxResults": 25}
    assert result["pageInfo"]["resultsPerPage"] == 1


def test_playlist_items_list_default_registry_exposes_executable_tool():
    """Expose ``playlistItems_list`` in the default dispatcher registry."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_list" in listed
    metadata = listed["playlistItems_list"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "playlistItems.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"

    result = dispatcher.call_tool("playlistItems_list", {"part": "snippet", "playlistId": "PL123"})
    assert result["endpoint"] == "playlistItems.list"


@pytest.mark.parametrize(
    "arguments",
    [
        {"playlistId": "PL123"},
        {"part": "snippet"},
        {"part": "snippet", "playlistId": "PL123", "id": "playlist-item-123"},
        {"part": "snippet", "id": "playlist-item-123", "maxResults": 5},
    ],
)
def test_playlist_items_list_descriptor_rejects_invalid_requests(arguments):
    """Reject malformed calls through dispatcher-safe validation."""
    dispatcher = _register_playlist_items_list()

    with pytest.raises((PlaylistItemsListToolError, ValueError)):
        dispatcher.call_tool("playlistItems_list", arguments)


def test_playlist_items_list_descriptor_maps_safe_upstream_failure():
    """Surface safe errors from registered ``playlistItems_list`` calls."""

    class FailingWrapper:
        """Raise a normalized quota failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured quota failure."""
            raise NormalizedUpstreamError("quota", "quota", True, 429, {"api_key": "secret", "quota": "daily"})

    dispatcher = _register_playlist_items_list(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsListToolError) as exc_info:
        dispatcher.call_tool("playlistItems_list", {"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}
