"""Unit tests for the concrete Layer 2 ``channelSections_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.channel_sections import (
    CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
    ChannelSectionsListToolError,
    build_channel_sections_list_tool_descriptor,
    map_channel_sections_list_result,
    validate_channel_sections_list_arguments,
)


def test_channel_sections_list_schema_preserves_parts_selectors_and_caveat_inputs():
    """Expose the upstream-like request fields for ``channelSections_list``."""
    properties = CHANNEL_SECTIONS_LIST_INPUT_SCHEMA["properties"]

    assert CHANNEL_SECTIONS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "channelId", "id", "mine", "hl", "onBehalfOfContentOwner"}.issubset(properties)
    assert CHANNEL_SECTIONS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_map_channel_sections_list_result_preserves_items_parts_selector_and_caveats():
    """Preserve near-raw channel-section collection fields in the mapped result."""
    result = map_channel_sections_list_result(
        {
            "items": [{"id": "section-123"}],
            "nextPageToken": "NEXT",
            "prevPageToken": "PREV",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet,contentDetails", "channelId": "UC123", "hl": "es"},
    )

    assert result["items"] == [{"id": "section-123"}]
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["nextPageToken"] == "NEXT"
    assert result["prevPageToken"] == "PREV"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}
    assert result["endpoint"] == "channelSections.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"name": "channelId"}
    assert result["caveats"]["hlDeprecated"] is True


def test_map_channel_sections_list_result_preserves_empty_collection_success():
    """Treat a valid empty channel-section response as a successful collection."""
    result = map_channel_sections_list_result({"items": []}, {"part": "snippet", "id": "section-123"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "id"}


def test_channel_sections_list_handler_invokes_wrapper_for_public_request():
    """Call the injected Layer 1 wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a continuation result.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped channel-section list response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"items": [{"id": "section-123"}], "nextPageToken": "NEXT"}

    descriptor = build_channel_sections_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"]({"part": "snippet", "channelId": "UC123"})

    assert result["items"] == [{"id": "section-123"}]
    assert result["nextPageToken"] == "NEXT"
    assert calls[0][1] == {"part": "snippet", "channelId": "UC123"}
    assert calls[0][2] == "api_key"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"channelId": "UC123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "channelId": ""}, "channelId"),
        ({"part": "snippet", "id": ""}, "id"),
        ({"part": "snippet", "channelId": "UC123", "id": "section-123"}, "selector"),
        ({"part": "snippet", "mine": False}, "mine"),
        ({"part": "snippet", "forUsername": "legacy-user"}, "forUsername"),
        ({"part": "snippet", "channelId": "UC123", "expandVideos": True}, "expandVideos"),
        ({"part": "snippet", "channelId": "UC123", "pageToken": "NEXT"}, "pageToken"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": 10}, "maxResults"),
    ],
)
def test_validate_channel_sections_list_rejects_invalid_arguments(arguments, field):
    """Reject invalid ``channelSections_list`` requests before Layer 1 execution."""
    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        validate_channel_sections_list_arguments(arguments, oauth_token="oauth-token")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_validate_channel_sections_list_rejects_content_owner_context_safely():
    """Reject partner-scoped content-owner context without exposing account details."""
    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        validate_channel_sections_list_arguments(
            {"part": "snippet", "channelId": "UC123", "onBehalfOfContentOwner": "cms-secret-owner"},
            oauth_token="oauth-token",
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "onBehalfOfContentOwner", "partnerScoped": True}
    assert "cms-secret-owner" not in str(exc_info.value)


def test_validate_channel_sections_list_requires_oauth_for_mine_selector():
    """Reject owner-scoped lookup when OAuth authorization is unavailable."""
    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        validate_channel_sections_list_arguments({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine"}


def test_channel_sections_list_handler_rejects_api_key_for_owner_scoped_lookup():
    """Keep owner-scoped lookup from falling back to public API-key auth."""
    descriptor = build_channel_sections_list_tool_descriptor(api_key="public-key", oauth_token=None)

    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine"}


def test_channel_sections_list_handler_uses_oauth_for_owner_scoped_lookup():
    """Use OAuth credentials when the ``mine`` selector is authorized."""
    calls = []

    class FakeWrapper:
        """Capture auth context selected for owner-scoped channel-section lookup."""

        def call(self, executor, *, arguments, auth_context):
            """Record auth context details and return an empty collection.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped empty channel-section list response.
            """
            calls.append((arguments, auth_context.mode.value, bool(auth_context.credentials.oauth_token)))
            return {"items": []}

    descriptor = build_channel_sections_list_tool_descriptor(
        wrapper=FakeWrapper(),
        executor=object(),
        oauth_token="oauth-token",
    )

    result = descriptor["handler"]({"part": "snippet", "mine": True})

    assert result["items"] == []
    assert result["selector"] == {"name": "mine"}
    assert calls == [({"part": "snippet", "mine": True}, "oauth_required", True)]


@pytest.mark.parametrize(
    ("upstream_category", "upstream_status", "safe_category"),
    [
        ("auth", 403, "authorization_failed"),
        ("not_found", 404, "resource_not_found"),
        ("rate_limit", 429, "quota_exhausted"),
        ("transient", 503, "endpoint_unavailable"),
        ("upstream_service", 500, "upstream_failure"),
    ],
)
def test_channel_sections_list_handler_maps_upstream_errors_safely(
    upstream_category,
    upstream_status,
    safe_category,
):
    """Map Layer 1 failures to safe public categories without leaking secrets."""

    class FakeWrapper:
        """Raise one normalized upstream error for mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized upstream error containing unsafe text.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                message="upstream failed with oauth-token and Traceback (most recent call last)",
                category=upstream_category,
                retryable=False,
                upstream_status=upstream_status,
                details={"token": "oauth-token"},
            )

    descriptor = build_channel_sections_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == safe_category
    assert exc_info.value.details == {"upstreamStatus": upstream_status}
    assert "oauth-token" not in str(exc_info.value)
    assert "Traceback" not in str(exc_info.value)
