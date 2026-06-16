"""Unit tests for the concrete Layer 2 ``comments_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.comments import (
    COMMENTS_LIST_INPUT_SCHEMA,
    CommentsListToolError,
    build_comments_list_tool_descriptor,
    map_comments_list_result,
    validate_comments_list_arguments,
)


def test_comments_list_schema_preserves_selectors_pagination_and_format_inputs():
    """Expose the upstream-like request fields for ``comments_list``."""
    properties = COMMENTS_LIST_INPUT_SCHEMA["properties"]

    assert COMMENTS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(properties)
    assert COMMENTS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_comments_list_arguments_accepts_id_request():
    """Map a public ID request to the ID selector path."""
    selected = validate_comments_list_arguments({"part": "id,snippet", "id": "comment-123"})

    assert selected == ("id", "comment-123")


def test_validate_comments_list_arguments_accepts_parent_request():
    """Map a public parent-comment request to the parent selector path."""
    selected = validate_comments_list_arguments(
        {"part": "snippet", "parentId": "comment-parent-123", "maxResults": 10, "textFormat": "plainText"}
    )

    assert selected == ("parentId", "comment-parent-123")


def test_map_comments_list_result_preserves_id_items_parts_and_selector():
    """Preserve near-raw comment collection fields for ID retrieval."""
    result = map_comments_list_result(
        {
            "kind": "youtube#commentListResponse",
            "etag": "etag-123",
            "items": [{"id": "comment-123"}],
        },
        {"part": "id,snippet", "id": "comment-123"},
    )

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "comment-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}
    assert result["textFormat"] == "html"
    assert result["kind"] == "youtube#commentListResponse"
    assert result["etag"] == "etag-123"


def test_map_comments_list_result_preserves_parent_pagination_and_text_format():
    """Preserve reply paging and formatting context for parent-comment retrieval."""
    result = map_comments_list_result(
        {
            "items": [{"id": "reply-123"}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet", "parentId": "comment-parent-123", "textFormat": "plainText"},
    )

    assert result["items"] == [{"id": "reply-123"}]
    assert result["selector"] == {"name": "parentId"}
    assert result["textFormat"] == "plainText"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_map_comments_list_result_preserves_empty_collection_success():
    """Treat a valid empty comment response as a successful collection."""
    result = map_comments_list_result({"items": []}, {"part": "snippet", "parentId": "comment-parent-123"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "parentId"}


def test_comments_list_handler_invokes_wrapper_for_id_request():
    """Call the injected Layer 1 wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return an ID result.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped comment list response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"items": [{"id": "comment-123"}]}

    descriptor = build_comments_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"]({"part": "id,snippet", "id": "comment-123"})

    assert result["items"] == [{"id": "comment-123"}]
    assert calls[0][1] == {"part": "id,snippet", "id": "comment-123"}
    assert calls[0][2] == "api_key"


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({"id": "comment-123"}, "requires part"),
        ({"part": "snippet"}, "requires exactly one selector"),
        ({"part": "snippet", "id": "comment-123", "parentId": "parent-123"}, "requires exactly one selector"),
        ({"part": "snippet", "id": ""}, "requires a non-empty id"),
        ({"part": "snippet", "parentId": ""}, "requires a non-empty parentId"),
        ({"part": "snippet", "id": "comment-123", "maxResults": 5}, "does not support maxResults with id"),
        ({"part": "snippet", "id": "comment-123", "pageToken": "NEXT"}, "does not support pageToken with id"),
        ({"part": "snippet", "parentId": "parent-123", "maxResults": 0}, "maxResults must be between 1 and 100"),
        ({"part": "snippet", "parentId": "parent-123", "textFormat": "markdown"}, "textFormat"),
        ({"part": "snippet", "parentId": "parent-123", "body": {}}, "does not support body"),
    ],
)
def test_validate_comments_list_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported ``comments_list`` request shapes."""
    with pytest.raises(CommentsListToolError, match=match):
        validate_comments_list_arguments(arguments)


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("not_found", "resource_not_found"),
        ("rate_limit", "quota_exhausted"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("upstream_service", "upstream_failure"),
    ],
)
def test_comments_list_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream failures to public Layer 2 categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for handler tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured fake upstream failure.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError("upstream failed", category=category, retryable=False, upstream_status=400)

    descriptor = build_comments_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "id": "comment-123"})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}
