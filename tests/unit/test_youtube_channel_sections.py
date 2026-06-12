"""Unit tests for the concrete Layer 2 ``channelSections_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.channel_sections import (
    CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA,
    CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
    ChannelSectionsInsertToolError,
    ChannelSectionsListToolError,
    build_channel_sections_insert_tool_descriptor,
    build_channel_sections_list_tool_descriptor,
    map_channel_sections_insert_result,
    map_channel_sections_list_result,
    validate_channel_sections_insert_arguments,
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


def test_channel_sections_insert_schema_preserves_parts_body_and_partner_context():
    """Expose upstream-like request fields for ``channelSections_insert``."""
    properties = CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA["properties"]

    assert CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"}.issubset(properties)
    assert CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_map_channel_sections_insert_result_preserves_created_resource_parts_and_partner_flags():
    """Preserve near-raw created channel-section fields in the mapped result."""
    upstream_item = {
        "kind": "youtube#channelSection",
        "etag": "etag-123",
        "id": "section-123",
        "snippet": {"type": "multiplePlaylists", "title": "Featured"},
        "contentDetails": {"playlists": ["PL1", "PL2"]},
    }

    result = map_channel_sections_insert_result(
        upstream_item,
        {
            "part": "snippet, contentDetails",
            "body": {"snippet": {"type": "multiplePlaylists"}},
            "onBehalfOfContentOwner": "cms-secret-owner",
            "onBehalfOfContentOwnerChannel": "UC-secret-channel",
        },
    )

    assert result["endpoint"] == "channelSections.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["item"] == upstream_item
    assert result["partnerContext"] == {"onBehalfOfContentOwner": True, "onBehalfOfContentOwnerChannel": True}
    assert "cms-secret-owner" not in str(result)
    assert "UC-secret-channel" not in str(result)


def test_channel_sections_insert_handler_invokes_wrapper_with_oauth_context():
    """Call the injected Layer 1 insert wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 insert handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake insert call and return a created resource.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped created channel-section resource.
            """
            calls.append((executor, arguments, auth_context.mode.value, bool(auth_context.credentials.oauth_token)))
            return {"kind": "youtube#channelSection", "id": "section-123"}

    descriptor = build_channel_sections_insert_tool_descriptor(
        wrapper=FakeWrapper(),
        executor=object(),
        oauth_token="oauth-token",
    )

    arguments = {
        "part": "snippet,contentDetails",
        "body": {
            "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
            "contentDetails": {"playlists": ["PL123"]},
        },
    }
    result = descriptor["handler"](arguments)

    assert result["item"] == {"kind": "youtube#channelSection", "id": "section-123"}
    assert calls == [(calls[0][0], arguments, "oauth_required", True)]


def test_validate_channel_sections_insert_requires_oauth():
    """Reject channel-section creation when OAuth authorization is unavailable."""
    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        validate_channel_sections_insert_arguments(
            {"part": "snippet", "body": {"snippet": {"type": "singlePlaylist"}}},
            oauth_token=None,
        )

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth"}


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}}}, "part"),
        (
            {
                "part": "snippet,status",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
            },
            "part",
        ),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": "not-an-object"}, "body"),
        ({"part": "snippet", "body": {"contentDetails": {"playlists": ["PL123"]}}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": {"channelId": "UC123"}}}, "body.snippet.type"),
        ({"part": "snippet", "body": {"snippet": {"type": "singlePlaylist"}}}, "body.snippet.channelId"),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}, "status": {}},
            },
            "body.status",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123", "description": "Nope"}},
            },
            "body.snippet.description",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
                "playlistItems": {"list": True},
            },
            "playlistItems",
        ),
    ],
)
def test_validate_channel_sections_insert_rejects_invalid_body_and_part_arguments(arguments, field):
    """Reject malformed ``channelSections_insert`` requests before Layer 1 execution."""
    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        validate_channel_sections_insert_arguments(arguments, oauth_token="oauth-token")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                    "contentDetails": {"playlists": []},
                },
            },
            "body.contentDetails.playlists",
        ),
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                    "contentDetails": {"playlists": ["PL1", "PL2"]},
                },
            },
            "body.contentDetails.playlists",
        ),
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "multiplePlaylists", "channelId": "UC123"},
                    "contentDetails": {"playlists": ["PL1"]},
                },
            },
            "body.snippet.title",
        ),
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related"},
                    "contentDetails": {"playlists": ["PL1"]},
                },
            },
            "body.contentDetails.playlists",
        ),
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related"},
                    "contentDetails": {"channels": ["UC1", "UC1"]},
                },
            },
            "body.contentDetails.channels",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related"}},
            },
            "body.contentDetails.channels",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123", "position": -1}},
            },
            "body.snippet.position",
        ),
        (
            {
                "part": "contentDetails",
                "body": {
                    "snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related"},
                    "contentDetails": {"channels": [f"UC{i}" for i in range(51)]},
                },
            },
            "body.contentDetails.channels",
        ),
    ],
)
def test_validate_channel_sections_insert_rejects_invalid_content_rules(arguments, field):
    """Reject section-type content mismatches and invalid reference sets."""
    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        validate_channel_sections_insert_arguments(arguments, oauth_token="oauth-token")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        (
            {
                "part": "snippet",
                "onBehalfOfContentOwner": "cms-secret-owner",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
            },
            "onBehalfOfContentOwnerChannel",
        ),
        (
            {
                "part": "snippet",
                "onBehalfOfContentOwnerChannel": "UC-secret-channel",
                "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
            },
            "onBehalfOfContentOwner",
        ),
    ],
)
def test_validate_channel_sections_insert_rejects_invalid_partner_context(arguments, field):
    """Reject unpaired delegated owner/channel context without leaking identifiers."""
    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        validate_channel_sections_insert_arguments(arguments, oauth_token="oauth-token")

    error_text = f"{exc_info.value} {exc_info.value.details}"
    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "cms-secret-owner" not in error_text
    assert "UC-secret-channel" not in error_text


@pytest.mark.parametrize(
    ("upstream_category", "upstream_status", "safe_category"),
    [
        ("auth", 403, "authorization_failed"),
        ("not_found", 404, "resource_not_found"),
        ("rate_limit", 429, "quota_exhausted"),
        ("transient", 503, "endpoint_unavailable"),
        ("upstream_service", 500, "upstream_failure"),
        ("validation", 400, "invalid_request"),
    ],
)
def test_channel_sections_insert_handler_maps_upstream_errors_safely(
    upstream_category,
    upstream_status,
    safe_category,
):
    """Map insert failures to safe public categories without leaking secrets."""

    class FakeWrapper:
        """Raise one normalized upstream error for insert mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized upstream error containing unsafe text.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                message="private channel oauth-token cms-account UC-secret Traceback (most recent call last)",
                category=upstream_category,
                retryable=False,
                upstream_status=upstream_status,
                details={"token": "oauth-token", "owner": "cms-account", "channel": "UC-secret"},
            )

    descriptor = build_channel_sections_insert_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {
                    "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                    "contentDetails": {"playlists": ["PL123"]},
                },
            }
        )

    error_text = f"{exc_info.value} {exc_info.value.details}"
    assert exc_info.value.category == safe_category
    assert exc_info.value.details == {"upstreamStatus": upstream_status}
    assert "oauth-token" not in error_text
    assert "cms-account" not in error_text
    assert "UC-secret" not in error_text
    assert "Traceback" not in error_text
