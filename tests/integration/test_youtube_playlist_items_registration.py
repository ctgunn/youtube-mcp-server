"""Integration tests for registering and invoking playlist-items tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.playlist_items import (
    PlaylistItemsDeleteToolError,
    PlaylistItemsInsertToolError,
    PlaylistItemsListToolError,
    PlaylistItemsUpdateToolError,
    build_playlist_items_delete_tool_descriptor,
    build_playlist_items_insert_tool_descriptor,
    build_playlist_items_update_tool_descriptor,
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


def _register_playlist_items_insert(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-items insert tool in a fresh dispatcher."""
    descriptor = build_playlist_items_insert_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_playlist_items_update(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-items update tool in a fresh dispatcher."""
    descriptor = build_playlist_items_update_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_playlist_items_delete(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlist-items delete tool in a fresh dispatcher."""
    descriptor = build_playlist_items_delete_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _insert_arguments(**overrides):
    """Build a representative ``playlistItems_insert`` dispatcher request."""
    arguments = {
        "part": "snippet",
        "body": {
            "snippet": {
                "playlistId": "PL123",
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
            }
        },
    }
    arguments.update(overrides)
    return arguments


def _update_arguments(**overrides):
    """Build a representative ``playlistItems_update`` dispatcher request."""
    arguments = {
        "part": "snippet",
        "body": {
            "id": "playlist-item-123",
            "snippet": {
                "playlistId": "PL123",
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
            },
        },
    }
    arguments.update(overrides)
    return arguments


def _delete_arguments(**overrides):
    """Build a representative ``playlistItems_delete`` dispatcher request."""
    arguments = {"id": "playlist-item-123"}
    arguments.update(overrides)
    return arguments


def test_playlist_items_delete_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistItems_delete`` for playlist-item deletion."""
    dispatcher = _register_playlist_items_delete()

    result = dispatcher.call_tool("playlistItems_delete", _delete_arguments())

    assert result == {
        "endpoint": "playlistItems.delete",
        "quotaCost": 50,
        "target": {"id": "playlist-item-123"},
        "auth": {"mode": "oauth_required"},
        "deleted": True,
        "acknowledged": True,
    }


def test_playlist_items_delete_default_registry_exposes_executable_tool():
    """Expose ``playlistItems_delete`` in the default dispatcher registry."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_delete" in listed
    metadata = listed["playlistItems_delete"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "playlistItems.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]

    result = dispatcher.call_tool("playlistItems_delete", _delete_arguments())
    assert result["endpoint"] == "playlistItems.delete"
    assert result["acknowledged"] is True


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"id": ""},
        {"id": 123},
        {"id": "playlist-item-123", "part": "snippet"},
        {"id": "playlist-item-123", "body": {}},
        {"id": "playlist-item-123", "playlistId": "PL123"},
    ],
)
def test_playlist_items_delete_descriptor_rejects_invalid_requests(arguments):
    """Reject malformed delete calls through dispatcher-safe validation."""
    dispatcher = _register_playlist_items_delete()

    with pytest.raises((PlaylistItemsDeleteToolError, ValueError)):
        dispatcher.call_tool("playlistItems_delete", arguments)


def test_playlist_items_delete_descriptor_rejects_missing_oauth_access():
    """Surface missing OAuth access as a safe delete authentication failure."""
    with pytest.raises(PlaylistItemsDeleteToolError) as exc_info:
        _register_playlist_items_delete(oauth_token=None)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}


def test_playlist_items_delete_descriptor_maps_safe_upstream_failure():
    """Surface safe errors from registered ``playlistItems_delete`` calls."""

    class FailingWrapper:
        """Raise a normalized missing-resource failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured missing-resource failure."""
            raise NormalizedUpstreamError(
                "not found",
                "not_found",
                False,
                404,
                {"oauth_token": "secret", "resource": "playlistItem"},
            )

    dispatcher = _register_playlist_items_delete(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsDeleteToolError) as exc_info:
        dispatcher.call_tool("playlistItems_delete", _delete_arguments())

    assert exc_info.value.category == "resource_not_found"
    assert exc_info.value.details == {"resource": "playlistItem"}


def test_playlist_items_update_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistItems_update`` for playlist-item updates."""
    dispatcher = _register_playlist_items_update()

    result = dispatcher.call_tool("playlistItems_update", _update_arguments())

    assert result["endpoint"] == "playlistItems.update"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["target"] == {
        "playlistItemId": "playlist-item-123",
        "playlistId": "PL123",
        "videoId": "video-123",
        "resourceKind": "youtube#video",
    }
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-item-123"


def test_playlist_items_update_default_registry_exposes_executable_tool():
    """Expose ``playlistItems_update`` in the default dispatcher registry."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_update" in listed
    metadata = listed["playlistItems_update"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "playlistItems.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"

    result = dispatcher.call_tool("playlistItems_update", _update_arguments())
    assert result["endpoint"] == "playlistItems.update"


@pytest.mark.parametrize(
    "arguments",
    [
        {"body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet"},
        {"part": "snippet", "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet", "body": {"id": "playlist-item-123", "snippet": {"resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet", "body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123"}}},
        {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}, "position": 0},
            },
        },
        {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            },
            "rankPlaylist": True,
        },
    ],
)
def test_playlist_items_update_descriptor_rejects_invalid_requests(arguments):
    """Reject malformed update calls through dispatcher-safe validation."""
    dispatcher = _register_playlist_items_update()

    with pytest.raises((PlaylistItemsUpdateToolError, ValueError)):
        dispatcher.call_tool("playlistItems_update", arguments)


def test_playlist_items_update_descriptor_rejects_missing_oauth_access():
    """Surface missing OAuth access as a safe update authentication failure."""
    with pytest.raises(PlaylistItemsUpdateToolError) as exc_info:
        _register_playlist_items_update(oauth_token=None)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}


def test_playlist_items_update_descriptor_maps_safe_upstream_failure():
    """Surface safe errors from registered ``playlistItems_update`` calls."""

    class FailingWrapper:
        """Raise a normalized quota failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured quota failure."""
            raise NormalizedUpstreamError("quota", "quota", True, 429, {"oauth_token": "secret", "quota": "daily"})

    dispatcher = _register_playlist_items_update(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsUpdateToolError) as exc_info:
        dispatcher.call_tool("playlistItems_update", _update_arguments())

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_playlist_items_insert_descriptor_registers_as_executable_tool():
    """Register and execute ``playlistItems_insert`` for playlist-item creation."""
    dispatcher = _register_playlist_items_insert()

    result = dispatcher.call_tool("playlistItems_insert", _insert_arguments())

    assert result["endpoint"] == "playlistItems.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["assignment"] == {"playlistId": "PL123", "videoId": "video-123", "resourceKind": "youtube#video"}
    assert result["placement"] == {"position": 0}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-item-123"


def test_playlist_items_insert_default_registry_exposes_executable_tool():
    """Expose ``playlistItems_insert`` in the default dispatcher registry."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_insert" in listed
    metadata = listed["playlistItems_insert"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "playlistItems.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"

    result = dispatcher.call_tool("playlistItems_insert", _insert_arguments())
    assert result["endpoint"] == "playlistItems.insert"


@pytest.mark.parametrize(
    "arguments",
    [
        {"body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet"},
        {"part": "snippet", "body": {"snippet": {"resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}},
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            "generatePlaylist": True,
        },
    ],
)
def test_playlist_items_insert_descriptor_rejects_invalid_requests(arguments):
    """Reject malformed insert calls through dispatcher-safe validation."""
    dispatcher = _register_playlist_items_insert()

    with pytest.raises((PlaylistItemsInsertToolError, ValueError)):
        dispatcher.call_tool("playlistItems_insert", arguments)


def test_playlist_items_insert_descriptor_maps_safe_upstream_failure():
    """Surface safe errors from registered ``playlistItems_insert`` calls."""

    class FailingWrapper:
        """Raise a normalized quota failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured quota failure."""
            raise NormalizedUpstreamError("quota", "quota", True, 429, {"oauth_token": "secret", "quota": "daily"})

    dispatcher = _register_playlist_items_insert(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsInsertToolError) as exc_info:
        dispatcher.call_tool("playlistItems_insert", _insert_arguments())

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


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
