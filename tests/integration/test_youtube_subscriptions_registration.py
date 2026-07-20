"""Integration tests for registering and invoking subscription tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.subscriptions import (
    SubscriptionsDeleteToolError,
    SubscriptionsInsertToolError,
    SubscriptionsListToolError,
    build_subscriptions_delete_tool_descriptor,
    build_subscriptions_insert_tool_descriptor,
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


def _register_subscriptions_insert(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete subscriptions insert tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the subscriptions insert tool.
    """
    descriptor = build_subscriptions_insert_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_subscriptions_delete(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete subscriptions delete tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the subscriptions delete tool.
    """
    descriptor = build_subscriptions_delete_tool_descriptor(**descriptor_kwargs)
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


def test_subscriptions_insert_descriptor_registers_as_executable_public_tool():
    """Register and execute ``subscriptions_insert`` for OAuth-backed creation."""
    dispatcher = _register_subscriptions_insert()

    result = dispatcher.call_tool(
        "subscriptions_insert",
        {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
    )

    assert result["endpoint"] == "subscriptions.insert"
    assert result["quotaCost"] == 50
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["created"] is True
    assert result["creation"]["targetChannelId"] == "UC123"


def test_subscriptions_insert_dispatcher_rejects_missing_oauth_safely():
    """Reject subscription creation when OAuth access is unavailable."""
    dispatcher = _register_subscriptions_insert(oauth_token=None)

    with pytest.raises(SubscriptionsInsertToolError) as exc_info:
        dispatcher.call_tool(
            "subscriptions_insert",
            {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        )

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}


def test_subscriptions_insert_dispatcher_rejects_invalid_request_safely():
    """Reject malformed subscription insert requests through the dispatcher."""
    dispatcher = _register_subscriptions_insert()

    with pytest.raises(SubscriptionsInsertToolError) as exc_info:
        dispatcher.call_tool("subscriptions_insert", {"part": "snippet", "body": {"snippet": {"resourceId": {}}}})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == "body.snippet.resourceId.channelId"


def test_subscriptions_insert_dispatcher_maps_safe_upstream_failure():
    """Preserve safe upstream failure categories through insert dispatcher execution."""

    class FailingWrapper:
        """Raise one normalized duplicate-target failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a sanitized duplicate-target failure for dispatcher mapping.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                "already subscribed",
                "duplicate_or_ineligible_target",
                True,
                409,
                {"oauth_token": "secret", "target": "UC123"},
            )

    dispatcher = _register_subscriptions_insert(wrapper=FailingWrapper())

    with pytest.raises(SubscriptionsInsertToolError) as exc_info:
        dispatcher.call_tool(
            "subscriptions_insert",
            {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        )

    assert exc_info.value.category == "duplicate_target"
    assert exc_info.value.details == {"target": "UC123"}


def test_subscriptions_delete_descriptor_registers_as_executable_public_tool():
    """Register and execute ``subscriptions_delete`` for OAuth-backed deletion."""
    dispatcher = _register_subscriptions_delete()

    result = dispatcher.call_tool("subscriptions_delete", {"id": "subscription-123"})

    assert result["endpoint"] == "subscriptions.delete"
    assert result["quotaCost"] == 50
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["deleted"] is True
    assert result["deletion"]["id"] == "subscription-123"


def test_subscriptions_delete_dispatcher_rejects_missing_oauth_safely():
    """Reject subscription deletion when OAuth access is unavailable."""
    dispatcher = _register_subscriptions_delete(oauth_token=None)

    with pytest.raises(SubscriptionsDeleteToolError) as exc_info:
        dispatcher.call_tool("subscriptions_delete", {"id": "subscription-123"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
