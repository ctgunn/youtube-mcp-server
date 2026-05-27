"""Unit tests for the concrete Layer 2 ``activities_list`` tool."""

import pytest

from mcp_server.tools.youtube_common.activities import (
    ACTIVITIES_LIST_INPUT_SCHEMA,
    ActivitiesListToolError,
    build_activities_list_tool_descriptor,
    map_activities_list_result,
    validate_activities_list_arguments,
)


def test_activities_list_schema_preserves_channel_parts_and_pagination_inputs():
    """Expose the upstream-like request fields for ``activities_list``."""
    properties = ACTIVITIES_LIST_INPUT_SCHEMA["properties"]

    assert ACTIVITIES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "channelId", "mine", "home", "maxResults", "pageToken"}.issubset(properties)
    assert ACTIVITIES_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_activities_list_arguments_accepts_channel_request():
    """Map a public channel request to the channel selector path."""
    selected = validate_activities_list_arguments(
        {"part": "snippet,contentDetails", "channelId": "UC123", "maxResults": 5}
    )

    assert selected == ("channelId", "UC123")


def test_map_activities_list_result_preserves_items_parts_and_pagination():
    """Preserve near-raw activity collection fields in the mapped result."""
    result = map_activities_list_result(
        {
            "items": [{"id": "activity-1"}],
            "nextPageToken": "NEXT",
            "prevPageToken": "PREV",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet,contentDetails", "channelId": "UC123"},
    )

    assert result["items"] == [{"id": "activity-1"}]
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["nextPageToken"] == "NEXT"
    assert result["prevPageToken"] == "PREV"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}
    assert result["endpoint"] == "activities.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"name": "channelId"}


def test_map_activities_list_result_preserves_empty_collection_success():
    """Treat a valid empty activity response as a successful collection."""
    result = map_activities_list_result({"items": []}, {"part": "snippet", "channelId": "UC123"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_activities_list_handler_invokes_wrapper_for_channel_request():
    """Call the injected Layer 1 wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a paginated result.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped activity list response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"items": [{"id": "activity-1"}], "nextPageToken": "NEXT"}

    descriptor = build_activities_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"]({"part": "snippet", "channelId": "UC123"})

    assert result["items"] == [{"id": "activity-1"}]
    assert result["nextPageToken"] == "NEXT"
    assert calls[0][1] == {"part": "snippet", "channelId": "UC123"}
    assert calls[0][2] == "api_key"


def test_validate_activities_list_arguments_rejects_missing_selector():
    """Reject requests without an activity selector."""
    with pytest.raises(ActivitiesListToolError, match="requires exactly one selector"):
        validate_activities_list_arguments({"part": "snippet"})


def test_validate_activities_list_arguments_rejects_multiple_selectors():
    """Reject requests with more than one activity selector."""
    with pytest.raises(ActivitiesListToolError, match="requires exactly one selector"):
        validate_activities_list_arguments({"part": "snippet", "channelId": "UC123", "mine": True})


def test_validate_activities_list_arguments_rejects_invalid_max_results():
    """Reject page-size values outside the upstream range."""
    with pytest.raises(ActivitiesListToolError, match="maxResults must be between 0 and 50"):
        validate_activities_list_arguments({"part": "snippet", "channelId": "UC123", "maxResults": 51})
