"""Integration tests for registering and invoking search tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.search import SearchListToolError, build_search_list_tool_descriptor


def _register_search_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete search list tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the search list tool.
    """
    descriptor = build_search_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_search_list_descriptor_registers_as_executable_public_tool():
    """Register and execute ``search_list`` for public keyword search."""
    dispatcher = _register_search_list()

    result = dispatcher.call_tool("search_list", {"part": "snippet", "q": "mcp server"})

    assert result["endpoint"] == "search.list"
    assert result["quotaCost"] == 100
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert result["items"][0]["id"]["videoId"] == "abc123"
    assert result["empty"] is False


def test_search_list_descriptor_executes_restricted_request():
    """Register and execute ``search_list`` for restricted OAuth search."""
    dispatcher = _register_search_list(oauth_token="local-oauth-token")

    result = dispatcher.call_tool("search_list", {"part": "snippet", "q": "private uploads", "forMine": True})

    assert result["endpoint"] == "search.list"
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["queryContext"]["forMine"] is True


def test_search_list_dispatcher_rejects_invalid_request_safely():
    """Reject incompatible filters through the registered dispatcher handler."""
    dispatcher = _register_search_list()

    with pytest.raises(SearchListToolError) as exc_info:
        dispatcher.call_tool("search_list", {"part": "snippet", "q": "mcp server", "videoDuration": "short"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "type", "required": "video"}


def test_search_list_dispatcher_rejects_missing_restricted_access_safely():
    """Reject restricted dispatch calls when OAuth access is unavailable."""
    dispatcher = _register_search_list(oauth_token=None)

    with pytest.raises(SearchListToolError) as exc_info:
        dispatcher.call_tool("search_list", {"part": "snippet", "q": "private uploads", "forMine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authPath": "restricted", "authMode": "oauth_required"}


def test_search_list_dispatcher_maps_safe_upstream_failure():
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

    dispatcher = _register_search_list(wrapper=FailingWrapper())

    with pytest.raises(SearchListToolError) as exc_info:
        dispatcher.call_tool("search_list", {"part": "snippet", "q": "mcp server"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_search_list_dispatcher_preserves_empty_success():
    """Keep accessible empty search collections successful after registration."""

    class EmptyWrapper:
        """Return an empty search collection for dispatcher checks."""

        def call(self, executor, *, arguments, auth_context):
            """Return an empty upstream-shaped search list result.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :return: Empty upstream-shaped search list result.
            """
            return {"items": [], "pageInfo": {"totalResults": 0, "resultsPerPage": 0}}

    dispatcher = _register_search_list(wrapper=EmptyWrapper())

    result = dispatcher.call_tool("search_list", {"part": "snippet", "q": "unlikely empty query"})

    assert result["endpoint"] == "search.list"
    assert result["items"] == []
    assert result["empty"] is True
