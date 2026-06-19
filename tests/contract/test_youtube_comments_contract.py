"""Contract tests for the concrete Layer 2 ``comments`` tools."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.comments import (
    COMMENTS_DELETE_CALLER_EXAMPLES,
    COMMENTS_DELETE_INPUT_SCHEMA,
    COMMENTS_DELETE_TOOL_NAME,
    COMMENTS_INSERT_CALLER_EXAMPLES,
    COMMENTS_INSERT_INPUT_SCHEMA,
    COMMENTS_INSERT_TOOL_NAME,
    COMMENTS_SET_MODERATION_STATUS_CALLER_EXAMPLES,
    COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA,
    COMMENTS_SET_MODERATION_STATUS_TOOL_NAME,
    COMMENTS_UPDATE_CALLER_EXAMPLES,
    COMMENTS_UPDATE_INPUT_SCHEMA,
    COMMENTS_UPDATE_TOOL_NAME,
    COMMENTS_LIST_CALLER_EXAMPLES,
    COMMENTS_LIST_INPUT_SCHEMA,
    COMMENTS_LIST_TOOL_NAME,
    CommentsDeleteToolError,
    CommentsInsertToolError,
    CommentsListToolError,
    CommentsSetModerationStatusToolError,
    CommentsUpdateToolError,
    build_comments_delete_contract,
    build_comments_delete_tool_descriptor,
    build_comments_insert_contract,
    build_comments_insert_tool_descriptor,
    build_comments_set_moderation_status_contract,
    build_comments_set_moderation_status_tool_descriptor,
    build_comments_update_contract,
    build_comments_update_tool_descriptor,
    build_comments_list_contract,
    build_comments_list_tool_descriptor,
)


def test_concrete_comments_module_exports_public_tool_contract():
    """Require the concrete comments Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import comments

    assert comments.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert youtube_common.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert callable(comments.build_comments_list_tool_descriptor)
    assert comments.COMMENTS_INSERT_TOOL_NAME == "comments_insert"
    assert youtube_common.COMMENTS_INSERT_TOOL_NAME == "comments_insert"
    assert callable(comments.build_comments_insert_tool_descriptor)
    assert comments.COMMENTS_UPDATE_TOOL_NAME == "comments_update"
    assert youtube_common.COMMENTS_UPDATE_TOOL_NAME == "comments_update"
    assert callable(comments.build_comments_update_tool_descriptor)
    assert comments.COMMENTS_SET_MODERATION_STATUS_TOOL_NAME == "comments_setModerationStatus"
    assert youtube_common.COMMENTS_SET_MODERATION_STATUS_TOOL_NAME == "comments_setModerationStatus"
    assert callable(comments.build_comments_set_moderation_status_tool_descriptor)
    assert comments.COMMENTS_DELETE_TOOL_NAME == "comments_delete"
    assert youtube_common.COMMENTS_DELETE_TOOL_NAME == "comments_delete"
    assert callable(comments.build_comments_delete_tool_descriptor)


def test_comments_delete_contract_exposes_identity_quota_auth_and_target_rules():
    """Expose public metadata required before ``comments_delete`` invocation."""
    contract = build_comments_delete_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_DELETE_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "delete"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.delete"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_comments_delete_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public delete contract."""
    descriptor = build_comments_delete_tool_descriptor()

    assert descriptor["name"] == "comments_delete"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.delete"
    assert descriptor["inputSchema"]["required"] == ["id"]
    assert {"id", "onBehalfOfContentOwner"}.issubset(descriptor["inputSchema"]["properties"])
    assert "body" not in descriptor["inputSchema"]["properties"]
    assert callable(descriptor["handler"])


def test_comments_delete_contract_documents_successful_acknowledgment_shape():
    """Require successful deletion results to preserve safe acknowledgment context."""
    result = build_comments_delete_tool_descriptor()["handler"]({"id": "comment-123"})

    assert result["endpoint"] == "comments.delete"
    assert result["quotaCost"] == 50
    assert result["deleted"] is True
    assert result["targetId"] == "comment-123"
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["statusCode"] == 204
    assert "item" not in result
    assert "items" not in result


def test_comments_delete_contract_documents_delegated_context():
    """Preserve safe delegated context for authorized comment deletion."""
    result = build_comments_delete_tool_descriptor()["handler"](
        {"id": "comment-123", "onBehalfOfContentOwner": "content-owner-id"}
    )

    assert result["endpoint"] == "comments.delete"
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_comments_delete_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``comments_delete``."""
    properties = COMMENTS_DELETE_INPUT_SCHEMA["properties"]

    assert COMMENTS_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert {"id", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["id"]["type"] == "string"
    assert "body" not in properties
    assert COMMENTS_DELETE_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_delete_metadata_exposes_cost_oauth_destructive_rules_and_caveats():
    """Expose quota, OAuth, no-body, destructive behavior, delegation, and exclusions."""
    metadata = build_comments_delete_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert metadata["responseConvention"]["targetFields"] == ["id"]
    assert metadata["responseConvention"]["delegationFields"] == ["onBehalfOfContentOwner"]
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "comment editing" in metadata_text
    assert "moderation status" in metadata_text
    assert "deletion recovery" in metadata_text


def test_comments_delete_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required delete scenario."""
    examples = {example["name"]: example for example in COMMENTS_DELETE_CALLER_EXAMPLES}

    assert {
        "authorized_comment_deletion",
        "delegated_owner_context",
        "missing_oauth",
        "missing_target",
        "empty_target",
        "conflicting_target_shape",
        "unsupported_body",
        "unsupported_option",
        "inaccessible_target",
        "already_deleted_target",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 50 or "Quota cost: 50" in str(example)
        for example in COMMENTS_DELETE_CALLER_EXAMPLES
    )


def test_comments_delete_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in delete metadata."""
    metadata = build_comments_delete_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "rawRequestBody" not in str(metadata)


def test_comments_delete_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials, raw bodies, or diagnostics from delete errors."""

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
                details={
                    "apiKey": "secret",
                    "oauthToken": "secret",
                    "stackTrace": "traceback",
                    "rawRequestBody": {"id": "secret-comment"},
                },
            )

    descriptor = build_comments_delete_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsDeleteToolError) as exc_info:
        descriptor["handler"]({"id": "comment-123"})

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "raw" not in str(exc_info.value.details).lower()


def test_comments_set_moderation_status_contract_exposes_identity_quota_auth_and_status_rules():
    """Expose public metadata required before moderation invocation."""
    contract = build_comments_set_moderation_status_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_SET_MODERATION_STATUS_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "setModerationStatus"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.setModerationStatus"
    assert metadata["inputContract"]["required"] == ["id", "moderationStatus"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_comments_set_moderation_status_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public moderation contract."""
    descriptor = build_comments_set_moderation_status_tool_descriptor()

    assert descriptor["name"] == "comments_setModerationStatus"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.setModerationStatus"
    assert descriptor["inputSchema"]["required"] == ["id", "moderationStatus"]
    assert {"id", "moderationStatus", "banAuthor", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert "body" not in descriptor["inputSchema"]["properties"]
    assert callable(descriptor["handler"])


def test_comments_set_moderation_status_contract_documents_successful_acknowledgment_shape():
    """Require successful moderation results to preserve safe acknowledgment context."""
    result = build_comments_set_moderation_status_tool_descriptor()["handler"](
        {"id": ["comment-123"], "moderationStatus": "published"}
    )

    assert result["endpoint"] == "comments.setModerationStatus"
    assert result["quotaCost"] == 50
    assert result["moderated"] is True
    assert result["targetIds"] == ["comment-123"]
    assert result["moderationStatus"] == "published"
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["statusCode"] == 204
    assert "item" not in result
    assert "items" not in result


def test_comments_set_moderation_status_contract_documents_delegated_and_ban_author_context():
    """Preserve safe delegated and optional author-ban context for moderation."""
    result = build_comments_set_moderation_status_tool_descriptor()["handler"](
        {
            "id": ["comment-123"],
            "moderationStatus": "rejected",
            "banAuthor": True,
            "onBehalfOfContentOwner": "content-owner-id",
        }
    )

    assert result["endpoint"] == "comments.setModerationStatus"
    assert result["banAuthor"] is True
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_comments_set_moderation_status_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for moderation."""
    properties = COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["properties"]

    assert COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["required"] == ["id", "moderationStatus"]
    assert {"id", "moderationStatus", "banAuthor", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["moderationStatus"]["enum"] == ["heldForReview", "published", "rejected"]
    assert properties["banAuthor"]["type"] == "boolean"
    assert "body" not in properties
    assert COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_set_moderation_status_metadata_exposes_cost_oauth_status_rules_and_caveats():
    """Expose quota, OAuth, moderation-state rules, delegation, and exclusions."""
    metadata = build_comments_set_moderation_status_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert metadata["responseConvention"]["supportedModerationStatuses"] == [
        "heldForReview",
        "published",
        "rejected",
    ]
    assert metadata["responseConvention"]["delegationFields"] == ["onBehalfOfContentOwner"]
    assert "heldForReview" in metadata_text
    assert "published" in metadata_text
    assert "rejected" in metadata_text
    assert "banAuthor" in metadata_text
    assert "request body" in metadata_text
    assert "comment editing" in metadata_text
    assert "automated moderation" in metadata_text


def test_comments_set_moderation_status_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required moderation scenario."""
    examples = {example["name"]: example for example in COMMENTS_SET_MODERATION_STATUS_CALLER_EXAMPLES}

    assert {
        "authorized_publish",
        "authorized_hold_for_review",
        "authorized_rejection_with_ban_author",
        "delegated_owner_context",
        "missing_oauth",
        "missing_target",
        "duplicate_target",
        "missing_status",
        "unsupported_status",
        "incompatible_ban_author",
        "unsupported_body",
        "target_comment_failure",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 50 or "Quota cost: 50" in str(example)
        for example in COMMENTS_SET_MODERATION_STATUS_CALLER_EXAMPLES
    )


def test_comments_set_moderation_status_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in moderation metadata."""
    metadata = build_comments_set_moderation_status_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "rawRequestBody" not in str(metadata)


def test_comments_set_moderation_status_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials, raw bodies, or diagnostics from moderation errors."""

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
                details={
                    "apiKey": "secret",
                    "oauthToken": "secret",
                    "stackTrace": "traceback",
                    "rawRequestBody": {"id": ["secret-comment"]},
                },
            )

    descriptor = build_comments_set_moderation_status_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsSetModerationStatusToolError) as exc_info:
        descriptor["handler"]({"id": ["comment-123"], "moderationStatus": "published"})

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "raw" not in str(exc_info.value.details).lower()


def test_comments_update_contract_exposes_identity_quota_auth_and_body_rules():
    """Expose public metadata required before ``comments_update`` invocation."""
    contract = build_comments_update_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_UPDATE_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "update"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.update"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_comments_update_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public update contract."""
    descriptor = build_comments_update_tool_descriptor()

    assert descriptor["name"] == "comments_update"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.update"
    assert descriptor["inputSchema"]["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_comments_update_contract_documents_successful_updated_result_shape():
    """Require successful update results to preserve updated comment fields."""
    result = build_comments_update_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        }
    )

    assert result["endpoint"] == "comments.update"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["writableFields"] == ["body.snippet.textOriginal"]
    assert result["item"]["id"] == "comment-123"
    assert result["item"]["snippet"]["textOriginal"] == "Updated comment text."
    assert result["auth"] == {"mode": "oauth_required"}


def test_comments_update_contract_documents_delegated_result_shape():
    """Preserve safe delegated context for authorized comment updates."""
    result = build_comments_update_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated by channel team."}},
        }
    )

    assert result["endpoint"] == "comments.update"
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_comments_update_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``comments_update``."""
    properties = COMMENTS_UPDATE_INPUT_SCHEMA["properties"]

    assert COMMENTS_UPDATE_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(properties)
    body = properties["body"]
    assert body["required"] == ["id", "snippet"]
    assert body["properties"]["snippet"]["required"] == ["textOriginal"]
    assert COMMENTS_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_update_metadata_exposes_cost_oauth_writable_rules_and_caveats():
    """Expose quota, OAuth, update-body rules, delegation, and exclusions."""
    metadata = build_comments_update_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["requiredBodyFields"] == [
        "body.id",
        "body.snippet.textOriginal",
    ]
    assert metadata["responseConvention"]["supportedWritableParts"] == ["snippet"]
    assert metadata["responseConvention"]["writableBodyFields"] == ["body.snippet.textOriginal"]
    assert metadata["responseConvention"]["delegationFields"] == ["onBehalfOfContentOwner"]
    assert "body.id" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "read-only" in metadata_text
    assert "commentThreads.insert" in metadata_text
    assert "generated rewrites" in metadata_text


def test_comments_update_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required update scenario."""
    examples = {example["name"]: example for example in COMMENTS_UPDATE_CALLER_EXAMPLES}

    assert {
        "authorized_comment_update",
        "delegated_owner_context",
        "missing_oauth",
        "missing_part",
        "missing_target_comment_id",
        "missing_updated_text",
        "unsupported_writable_part",
        "read_only_field_failure",
        "unsupported_option",
        "target_comment_failure",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 50 or "Quota cost: 50" in str(example)
        for example in COMMENTS_UPDATE_CALLER_EXAMPLES
    )


def test_comments_insert_contract_exposes_identity_quota_auth_and_body_rules():
    """Expose public metadata required before ``comments_insert`` invocation."""
    contract = build_comments_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_INSERT_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "insert"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.insert"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_comments_insert_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public insert contract."""
    descriptor = build_comments_insert_tool_descriptor()

    assert descriptor["name"] == "comments_insert"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.insert"
    assert descriptor["inputSchema"]["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_comments_insert_contract_documents_successful_created_result_shape():
    """Require successful insert results to preserve created comment fields."""
    result = build_comments_insert_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {
                "snippet": {
                    "parentId": "comment-parent-123",
                    "textOriginal": "Thanks for the feedback.",
                }
            },
        }
    )

    assert result["endpoint"] == "comments.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["item"]["id"] == "created-comment-123"
    assert result["auth"] == {"mode": "oauth_required"}


def test_comments_insert_contract_documents_delegated_result_shape():
    """Preserve safe delegated context for authorized reply creation."""
    result = build_comments_insert_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {
                "snippet": {
                    "parentId": "comment-parent-123",
                    "textOriginal": "Thanks from the channel team.",
                }
            },
        }
    )

    assert result["endpoint"] == "comments.insert"
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_comments_insert_metadata_exposes_cost_oauth_reply_rules_and_caveats():
    """Expose quota, OAuth, reply-body rules, delegation, and exclusions."""
    metadata = build_comments_insert_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["requiredBodyFields"] == [
        "body.snippet.parentId",
        "body.snippet.textOriginal",
    ]
    assert "body.snippet.parentId" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "commentThreads.insert" in metadata_text
    assert "sentiment" in metadata_text


def test_comments_insert_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required insert scenario."""
    examples = {example["name"]: example for example in COMMENTS_INSERT_CALLER_EXAMPLES}

    assert {
        "authorized_reply_creation",
        "delegated_owner_context",
        "missing_oauth",
        "missing_part",
        "missing_parent_comment",
        "missing_reply_text",
        "unsupported_top_level_create_shape",
        "unsupported_option",
        "parent_comment_not_found",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 50 or "Quota cost: 50" in str(example)
        for example in COMMENTS_INSERT_CALLER_EXAMPLES
    )


def test_comments_insert_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in insert metadata."""
    metadata = build_comments_insert_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "raw_media" not in str(metadata).lower()


def test_comments_insert_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials or raw diagnostics from insert errors."""

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

    descriptor = build_comments_insert_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsInsertToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
            }
        )

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_comments_insert_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``comments_insert``."""
    properties = COMMENTS_INSERT_INPUT_SCHEMA["properties"]

    assert COMMENTS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner"}.issubset(properties)
    body = properties["body"]
    assert body["required"] == ["snippet"]
    assert body["properties"]["snippet"]["required"] == ["parentId", "textOriginal"]
    assert COMMENTS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_comments_list_contract_exposes_identity_quota_auth_and_selectors():
    """Expose public metadata required before ``comments_list`` invocation."""
    contract = build_comments_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_LIST_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.list"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "parentId"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_comments_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_comments_list_tool_descriptor()

    assert descriptor["name"] == "comments_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {"id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_comments_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw comment collection fields."""
    result = build_comments_list_tool_descriptor()["handler"]({"part": "id,snippet", "id": "comment-123"})

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "comment-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}
    assert result["textFormat"] == "html"


def test_comments_list_contract_documents_parent_reply_result_shape():
    """Require parent-comment retrieval to preserve paging and formatting context."""
    result = build_comments_list_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "parentId": "comment-parent-123",
            "maxResults": 2,
            "pageToken": "NEXT_PAGE",
            "textFormat": "plainText",
        }
    )

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "reply-123"}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "parentId"}
    assert result["textFormat"] == "plainText"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_comments_list_metadata_exposes_lookup_cost_auth_and_caveats():
    """Expose quota, auth, selectors, pagination, formatting, and exclusions."""
    metadata = build_comments_list_contract().to_tool_metadata()
    metadata_text = " ".join(
        [
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert "id" in metadata_text
    assert "parentId" in metadata_text
    assert "maxResults" in metadata_text
    assert "pageToken" in metadata_text
    assert "textFormat" in metadata_text
    assert "plainText" in metadata_text
    assert "comment-thread discovery" in metadata_text
    assert "summarization" in metadata_text


def test_comments_list_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required caller scenario."""
    examples = {example["name"]: example for example in COMMENTS_LIST_CALLER_EXAMPLES}

    assert {
        "id_lookup",
        "parent_reply_lookup",
        "paginated_parent_lookup",
        "plain_text_parent_lookup",
        "empty_success",
        "missing_selector",
        "conflicting_selectors",
        "invalid_id",
        "unsupported_option",
        "access_sensitive_failure",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 1 or "Quota cost: 1" in str(example)
        for example in COMMENTS_LIST_CALLER_EXAMPLES
    )


def test_comments_list_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in public metadata."""
    metadata = build_comments_list_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "raw_media" not in str(metadata).lower()


def test_comments_list_safe_errors_do_not_leak_secret_details():
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

    descriptor = build_comments_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "id": "comment-123"})

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_comments_update_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in update metadata."""
    metadata = build_comments_update_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "raw_media" not in str(metadata).lower()


def test_comments_update_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials, raw bodies, or diagnostics from update errors."""

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
                details={
                    "apiKey": "secret",
                    "oauthToken": "secret",
                    "stackTrace": "traceback",
                    "rawRequestBody": {"body": {"snippet": {"textOriginal": "secret draft"}}},
                },
            )

    descriptor = build_comments_update_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsUpdateToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            }
        )

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "raw" not in str(exc_info.value.details).lower()


def test_comments_list_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``comments_list``."""
    properties = COMMENTS_LIST_INPUT_SCHEMA["properties"]

    assert COMMENTS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(properties)
    assert properties["maxResults"]["maximum"] == 100
    assert properties["textFormat"]["enum"] == ["html", "plainText"]
    assert COMMENTS_LIST_INPUT_SCHEMA["additionalProperties"] is False
