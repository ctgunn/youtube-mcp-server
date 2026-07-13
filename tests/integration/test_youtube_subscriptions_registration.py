"""Integration tests for registering and invoking subscription tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.subscriptions import (
    SubscriptionsListToolError,
    build_subscriptions_list_tool_descriptor,
)


def _register_subscriptions_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete subscriptions list tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the subscriptions list tool.
    """
    descriptor = build_subscriptions_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_subscriptions_list_descriptor_registers_as_executable_public_tool():
    """Register and execute ``subscriptions_list`` for public channel listing."""
    dispatcher = _register_subscriptions_list()

    result = dispatcher.call_tool("subscriptions_list", {"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "subscriptions.list"
    assert result["quotaCost"] == 1
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert result["items"][0]["id"] == "subscription-123"
    assert result["empty"] is False


def test_subscriptions_list_descriptor_executes_user_context_request():
    """Register and execute ``subscriptions_list`` for OAuth-backed listing."""
    dispatcher = _register_subscriptions_list(oauth_token="local-oauth-token")

    result = dispatcher.call_tool("subscriptions_list", {"part": "snippet", "mine": True})

    assert result["endpoint"] == "subscriptions.list"
    assert result["auth"] == {"mode": "oauth_required", "path": "user_context"}
    assert result["selectorContext"]["selector"] == "mine"


def test_subscriptions_list_dispatcher_rejects_invalid_request_safely():
    """Reject conflicting selectors through the registered dispatcher handler."""
    dispatcher = _register_subscriptions_list()

    with pytest.raises(SubscriptionsListToolError) as exc_info:
        dispatcher.call_tool("subscriptions_list", {"part": "snippet", "channelId": "UC123", "mine": True})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == "selector"


def test_subscriptions_list_dispatcher_rejects_missing_user_context_access_safely():
    """Reject user-context dispatch calls when OAuth access is unavailable."""
    dispatcher = _register_subscriptions_list(oauth_token=None)

    with pytest.raises(SubscriptionsListToolError) as exc_info:
        dispatcher.call_tool("subscriptions_list", {"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authPath": "user_context", "authMode": "oauth_required"}


def test_subscriptions_list_dispatcher_maps_safe_upstream_failure():
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

    dispatcher = _register_subscriptions_list(wrapper=FailingWrapper())

    with pytest.raises(SubscriptionsListToolError) as exc_info:
        dispatcher.call_tool("subscriptions_list", {"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_subscriptions_list_dispatcher_preserves_empty_success():
    """Keep accessible empty subscription collections successful after registration."""

    class EmptyWrapper:
        """Return an empty subscription collection for dispatcher checks."""

        def call(self, executor, *, arguments, auth_context):
            """Return an empty upstream-shaped subscription list result.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :return: Empty upstream-shaped subscription list result.
            """
            return {"items": [], "pageInfo": {"totalResults": 0, "resultsPerPage": 0}}

    dispatcher = _register_subscriptions_list(wrapper=EmptyWrapper())

    result = dispatcher.call_tool("subscriptions_list", {"part": "snippet", "channelId": "UC_NO_PUBLIC_SUBSCRIPTIONS"})

    assert result["endpoint"] == "subscriptions.list"
    assert result["items"] == []
    assert result["empty"] is True
