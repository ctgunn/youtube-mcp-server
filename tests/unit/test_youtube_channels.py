"""Unit tests for the concrete Layer 2 ``channels_list`` tool."""

import pytest

from mcp_server.tools.youtube_common.channels import (
    CHANNELS_LIST_INPUT_SCHEMA,
    ChannelsListToolError,
    build_channels_list_tool_descriptor,
    map_channels_list_result,
    validate_channels_list_arguments,
)


def test_channels_list_schema_preserves_parts_selectors_and_pagination_inputs():
    """Expose the upstream-like request fields for ``channels_list``."""
    properties = CHANNELS_LIST_INPUT_SCHEMA["properties"]

    assert CHANNELS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "id", "mine", "forHandle", "forUsername", "maxResults", "pageToken"}.issubset(properties)
    assert CHANNELS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_map_channels_list_result_preserves_items_parts_selector_and_pagination():
    """Preserve near-raw channel collection fields in the mapped result."""
    result = map_channels_list_result(
        {
            "items": [{"id": "UC123"}],
            "nextPageToken": "NEXT",
            "prevPageToken": "PREV",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet,contentDetails", "id": "UC123"},
    )

    assert result["items"] == [{"id": "UC123"}]
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["nextPageToken"] == "NEXT"
    assert result["prevPageToken"] == "PREV"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}
    assert result["endpoint"] == "channels.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"name": "id"}


def test_map_channels_list_result_preserves_empty_collection_success():
    """Treat a valid empty channel response as a successful collection."""
    result = map_channels_list_result({"items": []}, {"part": "snippet", "forHandle": "@Example"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "forHandle"}


def test_channels_list_handler_invokes_wrapper_for_public_request():
    """Call the injected Layer 1 wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a paginated result.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped channel list response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"items": [{"id": "UC123"}], "nextPageToken": "NEXT"}

    descriptor = build_channels_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"]({"part": "snippet", "id": "UC123"})

    assert result["items"] == [{"id": "UC123"}]
    assert result["nextPageToken"] == "NEXT"
    assert calls[0][1] == {"part": "snippet", "id": "UC123"}
    assert calls[0][2] == "api_key"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"id": "UC123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "id": ""}, "id"),
        ({"part": "snippet", "forHandle": ""}, "forHandle"),
        ({"part": "snippet", "forUsername": ""}, "forUsername"),
        ({"part": "snippet", "id": "UC123", "mine": True}, "selector"),
        ({"part": "snippet", "id": "UC123", "maxResults": 51}, "maxResults"),
        ({"part": "snippet", "id": "UC123", "unexpected": "value"}, "unexpected"),
    ],
)
def test_validate_channels_list_rejects_invalid_arguments(arguments, field):
    """Reject invalid ``channels_list`` requests before Layer 1 execution."""
    with pytest.raises(ChannelsListToolError) as exc_info:
        validate_channels_list_arguments(arguments, oauth_token="oauth-token")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_validate_channels_list_requires_oauth_for_mine_selector():
    """Reject owner-scoped lookup when OAuth authorization is unavailable."""
    with pytest.raises(ChannelsListToolError) as exc_info:
        validate_channels_list_arguments({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine"}


def test_channels_list_handler_rejects_api_key_for_owner_scoped_lookup():
    """Keep owner-scoped lookup from falling back to public API-key auth."""
    descriptor = build_channels_list_tool_descriptor(api_key="public-key", oauth_token=None)

    with pytest.raises(ChannelsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine"}


def test_channels_list_handler_uses_oauth_for_owner_scoped_lookup():
    """Use OAuth credentials when the ``mine`` selector is authorized."""
    calls = []

    class FakeWrapper:
        """Capture auth context selected for owner-scoped channel lookup."""

        def call(self, executor, *, arguments, auth_context):
            """Record auth context details and return an empty collection.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped empty channel list response.
            """
            calls.append((executor, arguments, auth_context.mode.value, auth_context.credentials.oauth_token))
            return {"items": []}

    descriptor = build_channels_list_tool_descriptor(
        wrapper=FakeWrapper(),
        executor=object(),
        api_key="public-key",
        oauth_token="oauth-token",
    )

    result = descriptor["handler"]({"part": "snippet", "mine": True})

    assert result["selector"] == {"name": "mine"}
    assert calls[0][2:] == ("oauth_required", "oauth-token")
