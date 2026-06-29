"""Unit tests for the concrete Layer 2 ``commentThreads_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.comment_threads import (
    COMMENT_THREADS_LIST_INPUT_SCHEMA,
    CommentThreadsListToolError,
    build_comment_threads_list_tool_descriptor,
    map_comment_threads_list_result,
    validate_comment_threads_list_arguments,
)


def test_comment_threads_list_schema_preserves_selectors_and_modifier_inputs():
    """Expose the upstream-like request fields for ``commentThreads_list``."""
    properties = COMMENT_THREADS_LIST_INPUT_SCHEMA["properties"]

    assert COMMENT_THREADS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {
        "part",
        "videoId",
        "allThreadsRelatedToChannelId",
        "id",
        "maxResults",
        "moderationStatus",
        "order",
        "pageToken",
        "searchTerms",
        "textFormat",
    }.issubset(properties)
    assert COMMENT_THREADS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_comment_threads_list_arguments_accepts_video_request():
    """Accept video-based comment-thread retrieval arguments."""
    selected = validate_comment_threads_list_arguments({"part": "snippet", "videoId": "video-123"})

    assert selected == ("videoId", "video-123")


def test_validate_comment_threads_list_arguments_accepts_channel_request():
    """Accept channel-related comment-thread retrieval arguments."""
    selected = validate_comment_threads_list_arguments(
        {"part": "snippet", "allThreadsRelatedToChannelId": "channel-123", "maxResults": 25}
    )

    assert selected == ("allThreadsRelatedToChannelId", "channel-123")


def test_validate_comment_threads_list_arguments_accepts_id_request():
    """Accept direct thread identifier retrieval arguments."""
    selected = validate_comment_threads_list_arguments({"part": "id,snippet", "id": "thread-123"})

    assert selected == ("id", "thread-123")


def test_map_comment_threads_list_result_preserves_video_items_parts_and_selector():
    """Map upstream video results into a safe near-raw list result."""
    result = map_comment_threads_list_result(
        {"items": [{"id": "thread-video-123"}], "kind": "youtube#commentThreadListResponse"},
        {"part": "snippet,replies", "videoId": "video-123"},
    )

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-video-123"}]
    assert result["kind"] == "youtube#commentThreadListResponse"
    assert result["requestedParts"] == ["snippet", "replies"]
    assert result["selector"] == {"name": "videoId"}
    assert result["textFormat"] == "html"


def test_map_comment_threads_list_result_preserves_channel_pagination_and_text_format():
    """Map upstream channel-related results with page and format context."""
    result = map_comment_threads_list_result(
        {
            "items": [{"id": "thread-channel-123"}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {
            "part": "snippet",
            "allThreadsRelatedToChannelId": "channel-123",
            "maxResults": 2,
            "pageToken": "NEXT_PAGE",
            "textFormat": "plainText",
        },
    )

    assert result["selector"] == {"name": "allThreadsRelatedToChannelId"}
    assert result["textFormat"] == "plainText"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_map_comment_threads_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful no-match results."""
    result = map_comment_threads_list_result({"items": []}, {"part": "snippet", "videoId": "video-123"})

    assert result["items"] == []
    assert result["selector"] == {"name": "videoId"}


def test_comment_threads_list_handler_invokes_wrapper_for_video_request():
    """Execute one valid video lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``commentThreads_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative thread list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: API-key auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "thread-video-123", "snippet": {"videoId": arguments["videoId"]}}]}

    wrapper = FakeWrapper()
    descriptor = build_comment_threads_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet", "videoId": "video-123"})

    assert result["items"] == [{"id": "thread-video-123", "snippet": {"videoId": "video-123"}}]
    assert wrapper.calls[0][1] == {"part": "snippet", "videoId": "video-123"}
    assert wrapper.calls[0][2].mode.value == "api_key"


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({}, "requires part"),
        ({"part": ""}, "requires part"),
        ({"part": "snippet"}, "requires exactly one selector"),
        ({"part": "snippet", "videoId": "video-123", "id": "thread-123"}, "requires exactly one selector"),
        ({"part": "snippet", "videoId": ""}, "videoId"),
        ({"part": "snippet", "allThreadsRelatedToChannelId": ""}, "allThreadsRelatedToChannelId"),
        ({"part": "snippet", "id": ""}, "id"),
        ({"part": "snippet", "id": "thread-123", "maxResults": 25}, "does not support maxResults with id"),
        (
            {"part": "snippet", "id": "thread-123", "moderationStatus": "published"},
            "does not support moderationStatus with id",
        ),
        ({"part": "snippet", "id": "thread-123", "order": "time"}, "does not support order with id"),
        ({"part": "snippet", "id": "thread-123", "pageToken": "NEXT_PAGE"}, "does not support pageToken with id"),
        ({"part": "snippet", "id": "thread-123", "searchTerms": "launch"}, "does not support searchTerms with id"),
        ({"part": "snippet", "videoId": "video-123", "maxResults": 0}, "maxResults"),
        ({"part": "snippet", "videoId": "video-123", "moderationStatus": "spam"}, "moderationStatus"),
        ({"part": "snippet", "videoId": "video-123", "order": "rating"}, "order"),
        ({"part": "snippet", "videoId": "video-123", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "videoId": "video-123", "searchTerms": ""}, "searchTerms"),
        ({"part": "snippet", "videoId": "video-123", "textFormat": "markdown"}, "textFormat"),
        ({"part": "snippet", "videoId": "video-123", "body": {}}, "body"),
    ],
)
def test_validate_comment_threads_list_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported ``commentThreads_list`` request shapes."""
    with pytest.raises(CommentThreadsListToolError, match=match):
        validate_comment_threads_list_arguments(arguments)


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("authorization", "authorization_failed"),
        ("rate_limit", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_comment_threads_list_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream failures into safe public categories."""
    class FailingWrapper:
        """Raise one normalized upstream error."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a fake upstream error.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to the wrapper.
            :param auth_context: API-key auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "upstream failed",
                category=category,
                retryable=False,
                details={"reason": "commentsDisabled", "apiKey": "secret", "stackTrace": "traceback"},
            )

    descriptor = build_comment_threads_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentThreadsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "videoId": "video-123"})

    assert exc_info.value.category == expected
    assert "api" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
