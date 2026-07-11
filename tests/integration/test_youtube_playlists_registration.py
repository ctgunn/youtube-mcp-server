"""Integration tests for registering and invoking playlists tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError, build_playlists_list_tool_descriptor


def _register_playlists_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete playlists list tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the playlists list tool.
    """
    descriptor = build_playlists_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_playlists_list_descriptor_registers_as_executable_tool():
    """Register and execute ``playlists_list`` for playlist retrieval."""
    dispatcher = _register_playlists_list()

    result = dispatcher.call_tool("playlists_list", {"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "playlists.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"name": "channelId", "value": "UC123"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"][0]["id"] == "PL123"


def test_playlists_list_descriptor_executes_owner_scoped_request():
    """Register and execute ``playlists_list`` for owner-scoped playlists."""
    dispatcher = _register_playlists_list(oauth_token="local-oauth-token")

    result = dispatcher.call_tool("playlists_list", {"part": "snippet", "mine": True})

    assert result["endpoint"] == "playlists.list"
    assert result["selector"] == {"name": "mine", "value": True}
    assert result["auth"] == {"mode": "oauth_required"}


def test_playlists_list_dispatcher_rejects_invalid_request_safely():
    """Reject selector conflicts through the registered dispatcher handler."""
    dispatcher = _register_playlists_list()

    with pytest.raises(PlaylistsListToolError) as exc_info:
        dispatcher.call_tool("playlists_list", {"part": "snippet", "channelId": "UC123", "id": "PL123"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == "selector"


def test_playlists_list_dispatcher_rejects_missing_owner_access_safely():
    """Reject owner-scoped dispatch calls when OAuth access is unavailable."""
    dispatcher = _register_playlists_list(oauth_token=None)

    with pytest.raises(PlaylistsListToolError) as exc_info:
        dispatcher.call_tool("playlists_list", {"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine", "authMode": "oauth_required"}


def test_playlists_list_dispatcher_maps_safe_upstream_failure():
    """Preserve safe upstream failure categories through dispatcher execution."""

    class FailingWrapper:
        """Raise one normalized quota failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a sanitized quota failure for dispatcher mapping.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError("quota", "quota", True, 429, {"oauth_token": "secret", "quota": "daily"})

    dispatcher = _register_playlists_list(wrapper=FailingWrapper())

    with pytest.raises(PlaylistsListToolError) as exc_info:
        dispatcher.call_tool("playlists_list", {"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_playlists_list_dispatcher_preserves_empty_success():
    """Keep accessible empty playlist collections successful after registration."""

    class EmptyWrapper:
        """Return an empty playlist collection for dispatcher checks."""

        def call(self, executor, *, arguments, auth_context):
            """Return an empty upstream-shaped playlist list result.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :return: Empty upstream-shaped playlist list result.
            """
            return {"items": [], "pageInfo": {"totalResults": 0, "resultsPerPage": 0}}

    dispatcher = _register_playlists_list(wrapper=EmptyWrapper())

    result = dispatcher.call_tool("playlists_list", {"part": "snippet", "channelId": "UC_EMPTY"})

    assert result["endpoint"] == "playlists.list"
    assert result["items"] == []
    assert result["empty"] is True
