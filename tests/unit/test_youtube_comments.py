"""Unit tests for the concrete Layer 2 ``comments_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.comments import (
    COMMENTS_DELETE_INPUT_SCHEMA,
    COMMENTS_INSERT_INPUT_SCHEMA,
    COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA,
    COMMENTS_UPDATE_INPUT_SCHEMA,
    CommentsDeleteToolError,
    CommentsInsertToolError,
    CommentsSetModerationStatusToolError,
    CommentsUpdateToolError,
    COMMENTS_LIST_INPUT_SCHEMA,
    CommentsListToolError,
    build_comments_delete_tool_descriptor,
    build_comments_insert_tool_descriptor,
    build_comments_set_moderation_status_tool_descriptor,
    build_comments_update_tool_descriptor,
    map_comments_delete_result,
    map_comments_set_moderation_status_result,
    build_comments_list_tool_descriptor,
    map_comments_insert_result,
    map_comments_update_result,
    map_comments_list_result,
    validate_comments_delete_arguments,
    validate_comments_insert_arguments,
    validate_comments_set_moderation_status_arguments,
    validate_comments_update_arguments,
    validate_comments_list_arguments,
)


def test_comments_list_schema_preserves_selectors_pagination_and_format_inputs():
    """Expose the upstream-like request fields for ``comments_list``."""
    properties = COMMENTS_LIST_INPUT_SCHEMA["properties"]

    assert COMMENTS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(properties)
    assert COMMENTS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_insert_schema_preserves_reply_create_inputs():
    """Expose the upstream-like request fields for ``comments_insert``."""
    properties = COMMENTS_INSERT_INPUT_SCHEMA["properties"]

    assert COMMENTS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["body"]["properties"]["snippet"]["required"] == ["parentId", "textOriginal"]
    assert COMMENTS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_update_schema_preserves_comment_edit_inputs():
    """Expose the upstream-like request fields for ``comments_update``."""
    properties = COMMENTS_UPDATE_INPUT_SCHEMA["properties"]

    assert COMMENTS_UPDATE_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["body"]["required"] == ["id", "snippet"]
    assert properties["body"]["properties"]["snippet"]["required"] == ["textOriginal"]
    assert COMMENTS_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_set_moderation_status_schema_preserves_moderation_inputs():
    """Expose the upstream-like request fields for moderation status changes."""
    properties = COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["properties"]

    assert COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["required"] == ["id", "moderationStatus"]
    assert {"id", "moderationStatus", "banAuthor", "onBehalfOfContentOwner"}.issubset(properties)
    assert "body" not in properties
    assert properties["moderationStatus"]["enum"] == ["heldForReview", "published", "rejected"]
    assert COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_delete_schema_preserves_delete_inputs():
    """Expose the upstream-like request fields for ``comments_delete``."""
    properties = COMMENTS_DELETE_INPUT_SCHEMA["properties"]

    assert COMMENTS_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert {"id", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["id"]["type"] == "string"
    assert "body" not in properties
    assert COMMENTS_DELETE_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_comments_insert_arguments_accepts_reply_request():
    """Map a public reply-create request to parent and text values."""
    selected = validate_comments_insert_arguments(
        {
            "part": "snippet",
            "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
        }
    )

    assert selected == ("comment-parent-123", "Reply text")


def test_validate_comments_update_arguments_accepts_comment_edit_request():
    """Map a public comment update request to target comment and text values."""
    selected = validate_comments_update_arguments(
        {
            "part": "snippet",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        }
    )

    assert selected == ("comment-123", "Updated comment text.")


def test_validate_comments_set_moderation_status_arguments_accepts_moderation_request():
    """Map a public moderation request to target IDs and status."""
    selected = validate_comments_set_moderation_status_arguments(
        {"id": ["comment-123", "comment-456"], "moderationStatus": "rejected", "banAuthor": True}
    )

    assert selected == (("comment-123", "comment-456"), "rejected")


def test_validate_comments_delete_arguments_accepts_delete_request():
    """Map a public delete request to one target comment ID."""
    selected = validate_comments_delete_arguments({"id": "comment-123"})

    assert selected == "comment-123"


def test_map_comments_insert_result_preserves_created_item_parts_and_context():
    """Preserve near-raw created comment fields for reply creation."""
    result = map_comments_insert_result(
        {
            "kind": "youtube#comment",
            "etag": "etag-123",
            "id": "created-comment-123",
            "snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"},
        },
        {
            "part": "id,snippet",
            "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
        },
    )

    assert result["endpoint"] == "comments.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["item"]["id"] == "created-comment-123"
    assert result["item"]["snippet"]["parentId"] == "comment-parent-123"
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["kind"] == "youtube#comment"
    assert result["etag"] == "etag-123"


def test_map_comments_update_result_preserves_updated_item_parts_and_context():
    """Preserve near-raw updated comment fields for comment edits."""
    result = map_comments_update_result(
        {
            "kind": "youtube#comment",
            "etag": "etag-123",
            "id": "comment-123",
            "snippet": {"textOriginal": "Updated comment text."},
        },
        {
            "part": "id,snippet",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
    )

    assert result["endpoint"] == "comments.update"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["writableFields"] == ["body.snippet.textOriginal"]
    assert result["item"]["id"] == "comment-123"
    assert result["item"]["snippet"]["textOriginal"] == "Updated comment text."
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["kind"] == "youtube#comment"
    assert result["etag"] == "etag-123"


def test_map_comments_set_moderation_status_result_preserves_acknowledgment_context():
    """Preserve safe moderation acknowledgment context."""
    result = map_comments_set_moderation_status_result(
        {},
        {"id": ["comment-123", "comment-456"], "moderationStatus": "heldForReview"},
    )

    assert result["endpoint"] == "comments.setModerationStatus"
    assert result["quotaCost"] == 50
    assert result["moderated"] is True
    assert result["targetIds"] == ["comment-123", "comment-456"]
    assert result["moderationStatus"] == "heldForReview"
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["statusCode"] == 204
    assert "item" not in result


def test_map_comments_delete_result_preserves_acknowledgment_context():
    """Preserve safe deletion acknowledgment context."""
    result = map_comments_delete_result({}, {"id": "comment-123"})

    assert result["endpoint"] == "comments.delete"
    assert result["quotaCost"] == 50
    assert result["deleted"] is True
    assert result["targetId"] == "comment-123"
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["statusCode"] == 204
    assert "item" not in result


def test_map_comments_insert_result_preserves_delegation_context():
    """Preserve safe delegated owner context without exposing credentials."""
    result = map_comments_insert_result(
        {"id": "created-comment-123"},
        {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
        },
    )

    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_map_comments_update_result_preserves_delegation_context():
    """Preserve safe delegated owner context without exposing credentials."""
    result = map_comments_update_result(
        {"id": "comment-123"},
        {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
    )

    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_map_comments_set_moderation_status_result_preserves_delegation_and_ban_context():
    """Preserve safe delegated and author-ban context without exposing credentials."""
    result = map_comments_set_moderation_status_result(
        {},
        {
            "id": ["comment-123"],
            "moderationStatus": "rejected",
            "banAuthor": True,
            "onBehalfOfContentOwner": "content-owner-id",
        },
    )

    assert result["banAuthor"] is True
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_map_comments_delete_result_preserves_delegation_context():
    """Preserve safe delegated owner context without exposing credentials."""
    result = map_comments_delete_result(
        {},
        {"id": "comment-123", "onBehalfOfContentOwner": "content-owner-id"},
    )

    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_comments_insert_handler_invokes_wrapper_for_reply_request():
    """Call the injected Layer 1 wrapper through the insert handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 insert handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a created comment.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped created comment response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"id": "created-comment-123"}

    descriptor = build_comments_insert_tool_descriptor(wrapper=FakeWrapper(), executor=object())
    arguments = {
        "part": "snippet",
        "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
    }

    result = descriptor["handler"](arguments)

    assert result["item"] == {"id": "created-comment-123"}
    assert calls[0][1] == arguments
    assert calls[0][2] == "oauth_required"


def test_comments_update_handler_invokes_wrapper_for_comment_edit_request():
    """Call the injected Layer 1 wrapper through the update handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 update handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return an updated comment.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped updated comment response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"id": "comment-123", "snippet": {"textOriginal": arguments["body"]["snippet"]["textOriginal"]}}

    descriptor = build_comments_update_tool_descriptor(wrapper=FakeWrapper(), executor=object())
    arguments = {
        "part": "snippet",
        "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
    }

    result = descriptor["handler"](arguments)

    assert result["item"] == {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}}
    assert calls[0][1] == arguments
    assert calls[0][2] == "oauth_required"


def test_comments_set_moderation_status_handler_invokes_wrapper_for_moderation_request():
    """Call the injected Layer 1 wrapper through the moderation handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the moderation handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return no-content success.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Empty upstream-shaped moderation response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {}

    descriptor = build_comments_set_moderation_status_tool_descriptor(wrapper=FakeWrapper(), executor=object())
    arguments = {"id": ["comment-123"], "moderationStatus": "published"}

    result = descriptor["handler"](arguments)

    assert result["targetIds"] == ["comment-123"]
    assert result["moderationStatus"] == "published"
    assert calls[0][1] == arguments
    assert calls[0][2] == "oauth_required"


def test_comments_delete_handler_invokes_wrapper_for_delete_request():
    """Call the injected Layer 1 wrapper through the delete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the delete handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return no-content success.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Empty upstream-shaped delete response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {}

    descriptor = build_comments_delete_tool_descriptor(wrapper=FakeWrapper(), executor=object())
    arguments = {"id": "comment-123"}

    result = descriptor["handler"](arguments)

    assert result["targetId"] == "comment-123"
    assert result["deleted"] is True
    assert calls[0][1] == arguments
    assert calls[0][2] == "oauth_required"


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
    ("arguments", "match"),
    [
        ({"body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}}}, "requires part"),
        ({"part": "snippet"}, "requires body"),
        ({"part": "snippet", "body": {}}, "requires body.snippet"),
        ({"part": "snippet", "body": {"snippet": {"textOriginal": "Reply text"}}}, "parentId"),
        ({"part": "snippet", "body": {"snippet": {"parentId": "comment-parent-123"}}}, "textOriginal"),
        (
            {"part": "snippet", "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": ""}}},
            "textOriginal",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "parentId": "comment-parent-123",
                        "textOriginal": "Reply text",
                        "topLevelComment": {},
                    }
                },
            },
            "topLevelComment",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
                "moderationStatus": "published",
            },
            "moderationStatus",
        ),
    ],
)
def test_validate_comments_insert_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported ``comments_insert`` request shapes."""
    with pytest.raises(CommentsInsertToolError, match=match):
        validate_comments_insert_arguments(arguments)


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        (
            {"body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}}},
            "requires part",
        ),
        ({"part": "snippet"}, "requires body"),
        ({"part": "snippet", "body": {"snippet": {"textOriginal": "Updated text"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": "comment-123"}}, "body.snippet"),
        (
            {"part": "snippet", "body": {"id": "comment-123", "snippet": {"textOriginal": ""}}},
            "textOriginal",
        ),
        (
            {"part": "statistics", "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}}},
            "snippet part",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "comment-123",
                    "snippet": {"textOriginal": "Updated text", "authorDisplayName": "Read-only"},
                },
            },
            "authorDisplayName",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "comment-123",
                    "snippet": {"textOriginal": "Updated text", "parentId": "comment-parent-123"},
                },
            },
            "parentId",
        ),
        (
            {
                "part": "snippet",
                "moderationStatus": "published",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
            "moderationStatus",
        ),
        (
            {
                "part": "snippet",
                "delete": True,
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
            "delete",
        ),
        (
            {
                "part": "snippet",
                "parentId": "comment-parent-123",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
            "parentId",
        ),
        (
            {
                "part": "snippet",
                "searchTerms": "needle",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
            "searchTerms",
        ),
        (
            {
                "part": "snippet",
                "rewriteTone": "friendly",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
            "rewriteTone",
        ),
    ],
)
def test_validate_comments_update_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported ``comments_update`` request shapes."""
    with pytest.raises(CommentsUpdateToolError, match=match):
        validate_comments_update_arguments(arguments)


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({"moderationStatus": "published"}, "requires id"),
        ({"id": "", "moderationStatus": "published"}, "requires id"),
        ({"id": ["comment-123", "comment-123"], "moderationStatus": "rejected"}, "duplicate"),
        ({"id": ["comment-123"]}, "moderationStatus"),
        ({"id": ["comment-123"], "moderationStatus": "spam"}, "unsupported moderationStatus"),
        ({"id": ["comment-123"], "moderationStatus": "rejected", "banAuthor": "yes"}, "banAuthor"),
        (
            {"id": ["comment-123"], "moderationStatus": "published", "banAuthor": True},
            "banAuthor is only supported",
        ),
        (
            {"id": ["comment-123"], "moderationStatus": "rejected", "body": {}},
            "body",
        ),
        (
            {"id": ["comment-123"], "moderationStatus": "rejected", "part": "snippet"},
            "part",
        ),
        (
            {"id": ["comment-123"], "moderationStatus": "rejected", "onBehalfOfContentOwner": ""},
            "onBehalfOfContentOwner",
        ),
    ],
)
def test_validate_comments_set_moderation_status_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported moderation request shapes."""
    with pytest.raises(CommentsSetModerationStatusToolError, match=match):
        validate_comments_set_moderation_status_arguments(arguments)


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({}, "requires id"),
        ({"id": ""}, "requires id"),
        ({"id": "   "}, "requires id"),
        ({"id": ["comment-123"]}, "requires id"),
        ({"id": "comment-123,comment-456"}, "exactly one target"),
        ({"id": "comment-123", "body": {}}, "body"),
        ({"id": "comment-123", "moderationStatus": "rejected"}, "moderationStatus"),
        ({"id": "comment-123", "part": "snippet"}, "part"),
        ({"id": "comment-123", "delete": True}, "delete"),
        ({"id": "comment-123", "recover": True}, "recover"),
        ({"id": "comment-123", "recommendReplacement": True}, "recommendReplacement"),
        ({"id": "comment-123", "searchTerms": "needle"}, "searchTerms"),
        ({"id": "comment-123", "onBehalfOfContentOwner": ""}, "onBehalfOfContentOwner"),
    ],
)
def test_validate_comments_delete_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid or unsupported ``comments_delete`` request shapes."""
    with pytest.raises(CommentsDeleteToolError, match=match):
        validate_comments_delete_arguments(arguments)


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


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("authentication", "authentication_failed"),
        ("not_found", "resource_not_found"),
        ("rate_limit", "quota_exhausted"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("upstream_service", "upstream_failure"),
        ("unknown", "upstream_failure"),
    ],
)
def test_comments_delete_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream delete failures to public Layer 2 categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for delete handler tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured fake upstream delete failure.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError("upstream failed", category=category, retryable=False, upstream_status=400)

    descriptor = build_comments_delete_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsDeleteToolError) as exc_info:
        descriptor["handler"]({"id": "comment-123"})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}


def test_comments_delete_handler_rejects_missing_oauth():
    """Report missing OAuth credentials without invoking deletion."""
    descriptor = build_comments_delete_tool_descriptor(oauth_token=None)

    with pytest.raises(CommentsDeleteToolError) as exc_info:
        descriptor["handler"]({"id": "comment-123"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("target_id", "expected"),
    [
        ("missing-comment", "resource_not_found"),
        ("already-deleted-comment", "resource_not_found"),
        ("inaccessible-comment", "authorization_failed"),
        ("quota-exhausted-comment", "quota_exhausted"),
        ("processing-failure-comment", "invalid_request"),
    ],
)
def test_comments_delete_default_wrapper_maps_representative_target_failures(target_id, expected):
    """Map default wrapper delete target failures to stable public categories."""
    descriptor = build_comments_delete_tool_descriptor()

    with pytest.raises(CommentsDeleteToolError) as exc_info:
        descriptor["handler"]({"id": target_id})

    assert exc_info.value.category == expected


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("authentication", "authentication_failed"),
        ("not_found", "resource_not_found"),
        ("rate_limit", "quota_exhausted"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("upstream_service", "upstream_failure"),
    ],
)
def test_comments_insert_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream insert failures to public Layer 2 categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for insert handler tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured fake upstream insert failure.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError("upstream failed", category=category, retryable=False, upstream_status=400)

    descriptor = build_comments_insert_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsInsertToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
            }
        )

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("authentication", "authentication_failed"),
        ("not_found", "resource_not_found"),
        ("rate_limit", "quota_exhausted"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("upstream_service", "upstream_failure"),
    ],
)
def test_comments_update_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream update failures to public Layer 2 categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for update handler tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured fake upstream update failure.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError("upstream failed", category=category, retryable=False, upstream_status=400)

    descriptor = build_comments_update_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsUpdateToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            }
        )

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("auth", "authorization_failed"),
        ("authentication", "authentication_failed"),
        ("not_found", "resource_not_found"),
        ("rate_limit", "quota_exhausted"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("upstream_service", "upstream_failure"),
    ],
)
def test_comments_set_moderation_status_handler_maps_upstream_errors(category, expected):
    """Map normalized upstream moderation failures to public Layer 2 categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for moderation handler tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured fake upstream moderation failure.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError("upstream failed", category=category, retryable=False, upstream_status=400)

    descriptor = build_comments_set_moderation_status_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsSetModerationStatusToolError) as exc_info:
        descriptor["handler"]({"id": ["comment-123"], "moderationStatus": "published"})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}
