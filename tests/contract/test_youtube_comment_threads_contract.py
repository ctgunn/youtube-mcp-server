"""Contract tests for concrete Layer 2 ``commentThreads`` tools."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.comment_threads import (
    COMMENT_THREADS_INSERT_CALLER_EXAMPLES,
    COMMENT_THREADS_LIST_CALLER_EXAMPLES,
    COMMENT_THREADS_LIST_INPUT_SCHEMA,
    COMMENT_THREADS_LIST_TOOL_NAME,
    CommentThreadsListToolError,
    build_comment_threads_list_contract,
    build_comment_threads_list_tool_descriptor,
)


def test_concrete_comment_threads_module_exports_public_tool_contract():
    """Require the concrete commentThreads Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import comment_threads

    assert comment_threads.COMMENT_THREADS_LIST_TOOL_NAME == "commentThreads_list"
    assert youtube_common.COMMENT_THREADS_LIST_TOOL_NAME == "commentThreads_list"
    assert callable(comment_threads.build_comment_threads_list_tool_descriptor)


def test_comment_threads_list_contract_exposes_identity_quota_auth_and_selectors():
    """Expose public metadata required before ``commentThreads_list`` invocation."""
    contract = build_comment_threads_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENT_THREADS_LIST_TOOL_NAME
    assert contract.upstream_resource == "commentThreads"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "commentThreads.list"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"videoId", "allThreadsRelatedToChannelId", "id"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_comment_threads_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_comment_threads_list_tool_descriptor()

    assert descriptor["name"] == "commentThreads_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "commentThreads.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {
        "videoId",
        "allThreadsRelatedToChannelId",
        "id",
        "maxResults",
        "moderationStatus",
        "order",
        "pageToken",
        "searchTerms",
        "textFormat",
    }.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_comment_threads_list_contract_documents_video_result_shape():
    """Require video retrieval to preserve near-raw comment-thread fields."""
    result = build_comment_threads_list_tool_descriptor()["handler"](
        {"part": "snippet,replies", "videoId": "video-123"}
    )

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-video-123", "snippet": {"videoId": "video-123"}}]
    assert result["requestedParts"] == ["snippet", "replies"]
    assert result["selector"] == {"name": "videoId"}
    assert result["textFormat"] == "html"


def test_comment_threads_list_contract_documents_channel_result_shape():
    """Require channel-related retrieval to preserve paging and formatting context."""
    result = build_comment_threads_list_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "allThreadsRelatedToChannelId": "channel-123",
            "maxResults": 2,
            "pageToken": "NEXT_PAGE",
            "textFormat": "plainText",
        }
    )

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-channel-123", "snippet": {"channelId": "channel-123"}}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "allThreadsRelatedToChannelId"}
    assert result["textFormat"] == "plainText"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_comment_threads_list_contract_documents_id_result_shape():
    """Require ID-based retrieval to preserve direct thread lookup context."""
    result = build_comment_threads_list_tool_descriptor()["handler"](
        {"part": "id,snippet", "id": "thread-123"}
    )

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}


def test_comment_threads_list_metadata_exposes_cost_auth_selectors_and_caveats():
    """Expose quota, auth, selectors, modifiers, formatting, and exclusions."""
    metadata = build_comment_threads_list_contract().to_tool_metadata()
    metadata_text = " ".join(
        [
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert "videoId" in metadata_text
    assert "allThreadsRelatedToChannelId" in metadata_text
    assert "maxResults" in metadata_text
    assert "moderationStatus" in metadata_text
    assert "pageToken" in metadata_text
    assert "searchTerms" in metadata_text
    assert "plainText" in metadata_text
    assert "reply-only listing" in metadata_text
    assert "summarization" in metadata_text


def test_comment_threads_list_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required caller scenario."""
    examples = {example["name"]: example for example in COMMENT_THREADS_LIST_CALLER_EXAMPLES}

    assert {
        "video_lookup",
        "channel_related_lookup",
        "id_lookup",
        "paginated_video_lookup",
        "ordered_search_lookup",
        "plain_text_lookup",
        "moderation_status_lookup",
        "empty_success",
        "missing_selector",
        "conflicting_selectors",
        "invalid_id",
        "unsupported_id_option",
        "disabled_comments",
        "access_sensitive_failure",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 1 or "Quota cost: 1" in str(example)
        for example in COMMENT_THREADS_LIST_CALLER_EXAMPLES
    )


def test_comment_threads_list_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in public metadata."""
    metadata = build_comment_threads_list_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "raw_media" not in str(metadata).lower()


def test_comment_threads_list_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials or raw diagnostics from public errors."""
    class FailingWrapper:
        """Raise a normalized upstream error with unsafe-looking details."""

        def call(self, executor, *, arguments, auth_context):
            """Raise one fake upstream authorization failure.

            :param executor: Executor passed by the handler.
            :param arguments: Arguments forwarded to the wrapper.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"apiKey": "secret", "oauthToken": "secret", "stackTrace": "traceback"},
            )

    descriptor = build_comment_threads_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentThreadsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "videoId": "video-123"})

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_comment_threads_list_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``commentThreads_list``."""
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
    assert properties["maxResults"]["maximum"] == 100
    assert properties["moderationStatus"]["enum"] == ["heldForReview", "likelySpam", "published"]
    assert properties["order"]["enum"] == ["time", "relevance"]
    assert properties["textFormat"]["enum"] == ["html", "plainText"]
    assert COMMENT_THREADS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_commentThreads_insert_contract_exposes_identity_quota_auth_and_schema():
    """Expose public metadata required before ``commentThreads_insert`` invocation."""
    from mcp_server.tools.youtube_common.comment_threads import (
        COMMENT_THREADS_INSERT_TOOL_NAME,
        build_comment_threads_insert_contract,
    )

    contract = build_comment_threads_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENT_THREADS_INSERT_TOOL_NAME
    assert contract.upstream_resource == "commentThreads"
    assert contract.upstream_method == "insert"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "commentThreads.insert"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_commentThreads_insert_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the insert contract."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_insert_tool_descriptor

    descriptor = build_comment_threads_insert_tool_descriptor()

    assert descriptor["name"] == "commentThreads_insert"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "commentThreads.insert"
    assert descriptor["inputSchema"]["required"] == ["part", "body"]
    assert "body" in descriptor["inputSchema"]["properties"]
    assert callable(descriptor["handler"])


def test_commentThreads_insert_contract_documents_created_thread_result_shape():
    """Require top-level creation to preserve near-raw comment-thread fields."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_insert_tool_descriptor

    result = build_comment_threads_insert_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Great walkthrough."}},
                }
            },
        }
    )

    assert result["endpoint"] == "commentThreads.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["target"] == {"channelId": "channel-123", "videoId": "video-123"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "thread-video-123"
    assert result["item"]["snippet"]["videoId"] == "video-123"


def test_commentThreads_insert_metadata_documents_cost_oauth_delegation_and_boundaries():
    """Expose caller-facing cost, auth, delegation, response, and scope boundaries."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_insert_contract

    metadata = build_comment_threads_insert_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"
    assert metadata["responseConvention"]["delegationFields"] == ["onBehalfOfContentOwner"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "body.snippet.channelId" in metadata_text
    assert "body.snippet.videoId" in metadata_text
    assert "body.snippet.topLevelComment.snippet.textOriginal" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "comments_insert" in metadata_text
    assert "does not list threads" in metadata_text
    assert "generated responses" in metadata_text


def test_commentThreads_insert_caller_examples_cover_discovery_and_exclusion_scenarios():
    """Expose representative success, delegation, validation, and safe-failure examples."""
    examples = {example["name"]: example for example in COMMENT_THREADS_INSERT_CALLER_EXAMPLES}

    assert {
        "authorized_top_level_create",
        "delegated_owner_context",
        "missing_oauth",
        "missing_part",
        "missing_channel",
        "missing_video",
        "missing_top_level_text",
        "invalid_target_context",
        "unsupported_reply_shape",
        "unsupported_option",
        "disabled_comments",
        "access_sensitive_failure",
    }.issubset(examples)
    assert examples["authorized_top_level_create"]["quotaCost"] == 50
    assert examples["delegated_owner_context"]["arguments"]["onBehalfOfContentOwner"]
    assert examples["invalid_target_context"]["error"]["field"] == "target"
    assert examples["unsupported_option"]["error"]["field"] == "moderationStatus"
    assert all(
        example.get("quotaCost") == 50 or "Quota cost: 50" in str(example)
        for example in COMMENT_THREADS_INSERT_CALLER_EXAMPLES
    )


def test_commentThreads_insert_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials or raw diagnostics from insert public errors."""
    from mcp_server.tools.youtube_common.comment_threads import (
        CommentThreadsInsertToolError,
        build_comment_threads_insert_tool_descriptor,
    )

    class FailingWrapper:
        """Raise a normalized upstream error with unsafe-looking details."""

        def call(self, executor, *, arguments, auth_context):
            """Raise one fake upstream insert failure.

            :param executor: Executor passed by the handler.
            :param arguments: Arguments forwarded to the wrapper.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={
                    "reason": "forbidden",
                    "oauthToken": "secret",
                    "apiKey": "secret",
                    "stackTrace": "traceback",
                    "rawCredentialPayload": {"token": "secret"},
                },
            )

    descriptor = build_comment_threads_insert_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentThreadsInsertToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "channelId": "restricted-channel",
                        "videoId": "video-123",
                        "topLevelComment": {"snippet": {"textOriginal": "Safe public text."}},
                    }
                },
            }
        )

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details["reason"] == "forbidden"
    assert "token" not in str(exc_info.value.details).lower()
    assert "api" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "credential" not in str(exc_info.value.details).lower()
