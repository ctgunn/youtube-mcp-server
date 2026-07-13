"""Unit tests for the Layer 2 ``subscriptions_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.subscriptions import (
    SubscriptionsListToolError,
    build_subscriptions_list_handler,
    map_subscriptions_list_result,
    validate_subscriptions_list_arguments,
)


def test_validate_subscriptions_list_accepts_supported_public_requests():
    """Accept supported public subscription list request shapes."""
    cases = [
        {"part": "snippet", "channelId": "UC123"},
        {"part": "id,snippet", "id": "subscription-123"},
        {"part": "snippet,contentDetails", "channelId": "UC123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        {"part": "snippet", "channelId": "UC123", "order": "alphabetical"},
    ]

    for case in cases:
        assert validate_subscriptions_list_arguments(case)["part"] == case["part"]


def test_validate_subscriptions_list_accepts_user_context_requests():
    """Accept supported OAuth-backed subscription selector modes."""
    cases = [
        {"part": "snippet", "mine": True},
        {"part": "subscriberSnippet", "myRecentSubscribers": True, "maxResults": 25},
        {"part": "subscriberSnippet", "mySubscribers": True, "order": "relevance"},
    ]

    for case in cases:
        normalized = validate_subscriptions_list_arguments(case)
        assert any(normalized.get(field) is True for field in ("mine", "myRecentSubscribers", "mySubscribers"))


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"channelId": "UC123"}, "part"),
        ({"part": "statistics", "channelId": "UC123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "channelId": "UC123", "mine": True}, "selector"),
        ({"part": "snippet", "channelId": ""}, "channelId"),
        ({"part": "snippet", "id": ""}, "id"),
        ({"part": "snippet", "mine": False}, "selector"),
        ({"part": "snippet", "channelId": "UC123", "includeChannelStatistics": True}, "includeChannelStatistics"),
        ({"part": "snippet", "channelId": "UC123", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": 51}, "maxResults"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": "25"}, "maxResults"),
        ({"part": "snippet", "channelId": "UC123", "order": "newest"}, "order"),
        ({"part": "snippet", "channelId": "UC123", "onBehalfOfContentOwner": "owner"}, "onBehalfOfContentOwner"),
    ],
)
def test_validate_subscriptions_list_rejects_invalid_request_shapes(arguments, field):
    """Reject malformed or unsupported request shapes with field details."""
    with pytest.raises(SubscriptionsListToolError) as exc_info:
        validate_subscriptions_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_validate_subscriptions_list_rejects_paging_for_id_lookup():
    """Reject collection paging controls for direct subscription id lookup."""
    with pytest.raises(SubscriptionsListToolError) as exc_info:
        validate_subscriptions_list_arguments({"part": "snippet", "id": "subscription-123", "pageToken": "NEXT"})

    assert exc_info.value.details == {"field": "paging", "selector": "id"}


def test_map_subscriptions_list_result_preserves_safe_context_and_paging():
    """Map upstream subscription payloads to near-raw public results."""
    result = map_subscriptions_list_result(
        {
            "kind": "youtube#subscriptionListResponse",
            "etag": "etag-subscriptions",
            "nextPageToken": "NEXT_PAGE",
            "items": [{"id": "subscription-123", "snippet": {"title": "Example channel"}}],
            "pageInfo": {"totalResults": 42, "resultsPerPage": 25},
        },
        {"part": "snippet,contentDetails", "channelId": "UC123", "pageToken": "PAGE_1", "maxResults": 25},
        auth_mode="api_key",
    )

    assert result["endpoint"] == "subscriptions.list"
    assert result["quotaCost"] == 1
    assert result["items"][0]["id"] == "subscription-123"
    assert result["empty"] is False
    assert result["selectorContext"]["selector"] == "channelId"
    assert result["selectorContext"]["channelId"] == "UC123"
    assert result["pagination"]["pageToken"] == "PAGE_1"
    assert result["pagination"]["maxResults"] == 25
    assert result["pagination"]["nextPageToken"] == "NEXT_PAGE"
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert "analytics" not in result


def test_map_subscriptions_list_result_preserves_empty_success():
    """Keep accessible empty subscription collections successful."""
    result = map_subscriptions_list_result(
        {"items": [], "pageInfo": {"totalResults": 0}},
        {"part": "snippet", "channelId": "UC_NO_PUBLIC_SUBSCRIPTIONS"},
    )

    assert result["items"] == []
    assert result["empty"] is True
    assert result["pageInfo"] == {"totalResults": 0}


def test_subscriptions_list_handler_selects_public_and_user_context_auth_paths():
    """Execute public and user-context calls with the correct Layer 1 auth mode."""

    class RecordingWrapper:
        """Record auth modes used for fake wrapper calls."""

        def __init__(self):
            """Initialize the fake wrapper call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Record one call and return a representative payload.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :return: Representative subscription result payload.
            """
            self.calls.append((arguments, auth_context))
            return {"items": [{"id": "subscription-123"}]}

    wrapper = RecordingWrapper()
    handler = build_subscriptions_list_handler(wrapper=wrapper, api_key="public-key", oauth_token="oauth-token")

    public_result = handler({"part": "snippet", "channelId": "UC123"})
    user_context_result = handler({"part": "snippet", "mine": True})

    assert public_result["auth"] == {"mode": "api_key", "path": "public"}
    assert user_context_result["auth"] == {"mode": "oauth_required", "path": "user_context"}
    assert [call[1].mode.value for call in wrapper.calls] == ["api_key", "oauth_required"]
    assert all("token" not in str(result).lower() for result in (public_result, user_context_result))


def test_subscriptions_list_handler_rejects_missing_user_context_oauth_safely():
    """Reject user-context selectors when OAuth access is unavailable."""
    handler = build_subscriptions_list_handler(oauth_token=None)

    with pytest.raises(SubscriptionsListToolError) as exc_info:
        handler({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authPath": "user_context", "authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("quota", "quota_exhausted"),
        ("accountClosed", "authorization_failed"),
        ("accountSuspended", "authorization_failed"),
        ("subscriptionForbidden", "authorization_failed"),
        ("subscriberNotFound", "not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("surprising", "upstream_failure"),
    ],
)
def test_subscriptions_list_handler_maps_safe_upstream_failures(category, expected):
    """Map upstream failures without leaking unsafe diagnostic details."""

    class FailingWrapper:
        """Raise one normalized failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a sanitized upstream failure for handler mapping.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(category, category, True, 403, {"api_key": "secret", "reason": category})

    handler = build_subscriptions_list_handler(wrapper=FailingWrapper())

    with pytest.raises(SubscriptionsListToolError) as exc_info:
        handler({"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"reason": category}
