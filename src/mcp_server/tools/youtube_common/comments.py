"""Concrete Layer 2 tool support for the YouTube ``comments`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.comments import (
    build_comments_insert_wrapper,
    build_comments_list_wrapper,
    build_comments_set_moderation_status_wrapper,
    build_comments_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


COMMENTS_LIST_TOOL_NAME = "comments_list"
COMMENTS_LIST_QUOTA_COST = 1
COMMENTS_LIST_SELECTORS = ("id", "parentId")
COMMENTS_LIST_TEXT_FORMATS = ("html", "plainText")
COMMENTS_INSERT_TOOL_NAME = "comments_insert"
COMMENTS_INSERT_QUOTA_COST = 50
COMMENTS_UPDATE_TOOL_NAME = "comments_update"
COMMENTS_UPDATE_QUOTA_COST = 50
COMMENTS_UPDATE_SUPPORTED_PARTS = ("snippet",)
COMMENTS_SET_MODERATION_STATUS_TOOL_NAME = "comments_setModerationStatus"
COMMENTS_SET_MODERATION_STATUS_QUOTA_COST = 50
COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES = ("heldForReview", "published", "rejected")

COMMENTS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "parentId": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
        "pageToken": {"type": "string", "minLength": 1},
        "textFormat": {"type": "string", "enum": list(COMMENTS_LIST_TEXT_FORMATS)},
    },
    "oneOf": [{"required": [selector]} for selector in COMMENTS_LIST_SELECTORS],
    "additionalProperties": False,
}

COMMENTS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["parentId", "textOriginal"],
                    "properties": {
                        "parentId": {"type": "string", "minLength": 1},
                        "textOriginal": {"type": "string", "minLength": 1},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

COMMENTS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "snippet": {
                    "type": "object",
                    "required": ["textOriginal"],
                    "properties": {
                        "textOriginal": {"type": "string", "minLength": 1},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id", "moderationStatus"],
    "properties": {
        "id": {
            "oneOf": [
                {"type": "string", "minLength": 1},
                {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
            ]
        },
        "moderationStatus": {"type": "string", "enum": list(COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES)},
        "banAuthor": {"type": "boolean"},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

COMMENTS_LIST_DESCRIPTION = (
    "List YouTube comments. Endpoint: comments.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)
COMMENTS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Provide part and exactly one selector: id or parentId.",
    "Quota cost: 1. Use id for direct comment lookup; maxResults and pageToken are unsupported with id.",
    "Quota cost: 1. Use parentId for reply lookup with optional maxResults, pageToken, and textFormat.",
    "Quota cost: 1. textFormat may be html or plainText; html is the default upstream format.",
)
COMMENTS_LIST_CAVEATS = (
    "comments_list has mixed/conditional auth: public retrieval uses API-key access, while access-sensitive comments can fail with authorization or not-found outcomes.",
    "Exactly one selector is required: id for direct comment lookup or parentId for replies to a parent comment.",
    "maxResults and pageToken are supported only with parentId and must not be sent with id.",
    "The tool does not perform comment-thread discovery, reply creation, comment updates, moderation status changes, deletion, search, sentiment analysis, ranking, summarization, enrichment, or cross-endpoint aggregation.",
)
COMMENTS_LIST_CALLER_EXAMPLES = (
    {
        "name": "id_lookup",
        "description": "Quota cost: 1. Retrieve one comment by id.",
        "arguments": {"part": "id,snippet", "id": "comment-123"},
        "result": {"endpoint": "comments.list", "quotaCost": 1, "selector": {"name": "id"}},
        "quotaCost": 1,
    },
    {
        "name": "parent_reply_lookup",
        "description": "Quota cost: 1. Retrieve replies under one parent comment.",
        "arguments": {"part": "snippet", "parentId": "comment-parent-123"},
        "result": {"endpoint": "comments.list", "quotaCost": 1, "selector": {"name": "parentId"}},
        "quotaCost": 1,
    },
    {
        "name": "paginated_parent_lookup",
        "description": "Quota cost: 1. Retrieve a parent reply page with maxResults and pageToken.",
        "arguments": {
            "part": "snippet",
            "parentId": "comment-parent-123",
            "maxResults": 25,
            "pageToken": "NEXT_PAGE",
        },
        "result": {"endpoint": "comments.list", "quotaCost": 1, "nextPageToken": "NEXT_PAGE"},
        "quotaCost": 1,
    },
    {
        "name": "plain_text_parent_lookup",
        "description": "Quota cost: 1. Retrieve reply text with plainText formatting.",
        "arguments": {"part": "snippet", "parentId": "comment-parent-123", "textFormat": "plainText"},
        "result": {"endpoint": "comments.list", "quotaCost": 1, "textFormat": "plainText"},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. Preserve empty reply collections as successful results.",
        "arguments": {"part": "snippet", "parentId": "comment-parent-without-replies"},
        "result": {"endpoint": "comments.list", "quotaCost": 1, "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_selector",
        "description": "Quota cost: 1. Reject requests without id or parentId.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
        "quotaCost": 1,
    },
    {
        "name": "conflicting_selectors",
        "description": "Quota cost: 1. Reject requests that combine id and parentId.",
        "arguments": {"part": "snippet", "id": "comment-123", "parentId": "comment-parent-123"},
        "error": {"category": "invalid_request", "field": "selector"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_id",
        "description": "Quota cost: 1. Reject empty comment identifiers.",
        "arguments": {"part": "snippet", "id": ""},
        "error": {"category": "invalid_request", "field": "id"},
        "quotaCost": 1,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 1. Reject unsupported search, sort, moderation, mutation, or enrichment options.",
        "arguments": {"part": "snippet", "parentId": "comment-parent-123", "body": {}},
        "error": {"category": "invalid_request", "field": "body"},
        "quotaCost": 1,
    },
    {
        "name": "access_sensitive_failure",
        "description": "Quota cost: 1. Map inaccessible comments to safe authorization or not-found failures.",
        "arguments": {"part": "snippet", "id": "private-comment-123"},
        "error": {"category": "authorization_failed"},
        "quotaCost": 1,
    },
)

COMMENTS_INSERT_DESCRIPTION = (
    "Create a YouTube comment reply. Endpoint: comments.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires body.snippet.parentId and body.snippet.textOriginal."
)
COMMENTS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and a reply body.",
    "Quota cost: 50. body.snippet.parentId identifies the existing parent comment being answered.",
    "Quota cost: 50. body.snippet.textOriginal contains the reply text to publish.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegated owner context when supported by eligible OAuth authorization.",
)
COMMENTS_INSERT_CAVEATS = (
    "comments_insert creates replies to existing comments and requires eligible OAuth authorization.",
    "Top-level comment-thread creation belongs to commentThreads.insert and is outside this tool boundary.",
    "Private, missing, inaccessible, or non-replyable parent comments are surfaced as safe validation, authorization, or missing-resource failures.",
    "The tool does not perform comment listing, updates, moderation status changes, deletion, generated replies, search, sentiment analysis, ranking, summarization, enrichment, or cross-endpoint aggregation.",
)
COMMENTS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_reply_creation",
        "description": "Quota cost: 50. Create a reply to an existing parent comment with eligible OAuth.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "parentId": "comment-parent-123",
                    "textOriginal": "Thanks for the feedback.",
                }
            },
        },
        "result": {"endpoint": "comments.insert", "quotaCost": 50, "created": True},
        "quotaCost": 50,
    },
    {
        "name": "delegated_owner_context",
        "description": "Quota cost: 50. Create a reply with safe delegated owner context.",
        "arguments": {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {
                "snippet": {
                    "parentId": "comment-parent-123",
                    "textOriginal": "Thanks from the channel team.",
                }
            },
        },
        "result": {"endpoint": "comments.insert", "quotaCost": 50, "delegation": {"onBehalfOfContentOwner": True}},
        "quotaCost": 50,
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Reject reply creation when eligible OAuth is unavailable.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
        },
        "error": {"category": "authentication_failed", "field": "auth"},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject requests without part selection.",
        "arguments": {"body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}}},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "missing_parent_comment",
        "description": "Quota cost: 50. Reject requests without body.snippet.parentId.",
        "arguments": {"part": "snippet", "body": {"snippet": {"textOriginal": "Reply text"}}},
        "error": {"category": "invalid_request", "field": "body.snippet.parentId"},
        "quotaCost": 50,
    },
    {
        "name": "missing_reply_text",
        "description": "Quota cost: 50. Reject requests without body.snippet.textOriginal.",
        "arguments": {"part": "snippet", "body": {"snippet": {"parentId": "comment-parent-123"}}},
        "error": {"category": "invalid_request", "field": "body.snippet.textOriginal"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_top_level_create_shape",
        "description": "Quota cost: 50. Top-level creation belongs to commentThreads.insert.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "parentId": "comment-parent-123",
                    "textOriginal": "Reply text",
                    "topLevelComment": {},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.topLevelComment"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 50. Reject unsupported update, moderation, delete, search, or generated reply options.",
        "arguments": {
            "part": "snippet",
            "moderationStatus": "published",
            "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
        },
        "error": {"category": "invalid_request", "field": "moderationStatus"},
        "quotaCost": 50,
    },
    {
        "name": "parent_comment_not_found",
        "description": "Quota cost: 50. Preserve missing parent comment failures as safe public errors.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"parentId": "missing-parent-comment", "textOriginal": "Reply text"}},
        },
        "error": {"category": "resource_not_found", "reason": "parentCommentNotFound"},
        "quotaCost": 50,
    },
)

COMMENTS_UPDATE_DESCRIPTION = (
    "Update an existing YouTube comment. Endpoint: comments.update. "
    "Quota cost: 50. Auth: oauth_required. Requires part, body.id, and body.snippet.textOriginal."
)
COMMENTS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and an update body.",
    "Quota cost: 50. body.id identifies the existing comment being updated.",
    "Quota cost: 50. body.snippet.textOriginal is the only supported writable comment field.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegated owner context when supported by eligible OAuth authorization.",
)
COMMENTS_UPDATE_CAVEATS = (
    "comments_update edits the text of an existing comment and requires eligible OAuth authorization.",
    "Only the snippet part is supported for writable updates; read-only fields such as author, published time, parentId, moderation status, and like counts are outside this tool boundary.",
    "Missing, inaccessible, ineligible, or non-editable target comments are surfaced as safe validation, authorization, or missing-resource failures.",
    "The tool does not perform comment listing, reply creation, top-level comment-thread creation via commentThreads.insert, moderation status changes, deletion, generated rewrites, search, sentiment analysis, ranking, summarization, enrichment, or cross-endpoint aggregation.",
)
COMMENTS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "authorized_comment_update",
        "description": "Quota cost: 50. Update an existing comment's text with eligible OAuth.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
        "result": {"endpoint": "comments.update", "quotaCost": 50, "updated": True},
        "quotaCost": 50,
    },
    {
        "name": "delegated_owner_context",
        "description": "Quota cost: 50. Update a comment with safe delegated owner context.",
        "arguments": {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated by channel team."}},
        },
        "result": {"endpoint": "comments.update", "quotaCost": 50, "delegation": {"onBehalfOfContentOwner": True}},
        "quotaCost": 50,
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Reject comment updates when eligible OAuth is unavailable.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
        "error": {"category": "authentication_failed", "field": "auth"},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject requests without part selection.",
        "arguments": {"body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}}},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "missing_target_comment_id",
        "description": "Quota cost: 50. Reject requests without body.id.",
        "arguments": {"part": "snippet", "body": {"snippet": {"textOriginal": "Updated comment text."}}},
        "error": {"category": "invalid_request", "field": "body.id"},
        "quotaCost": 50,
    },
    {
        "name": "missing_updated_text",
        "description": "Quota cost: 50. Reject requests without body.snippet.textOriginal.",
        "arguments": {"part": "snippet", "body": {"id": "comment-123", "snippet": {}}},
        "error": {"category": "invalid_request", "field": "body.snippet.textOriginal"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_writable_part",
        "description": "Quota cost: 50. Reject update parts other than snippet.",
        "arguments": {
            "part": "statistics",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "read_only_field_failure",
        "description": "Quota cost: 50. Reject read-only or immutable body fields such as parentId.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "comment-123", "snippet": {"parentId": "comment-parent-123", "textOriginal": "Text"}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.parentId"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 50. Reject unsupported listing, moderation, delete, search, or generated rewrite options.",
        "arguments": {
            "part": "snippet",
            "moderationStatus": "published",
            "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
        },
        "error": {"category": "invalid_request", "field": "moderationStatus"},
        "quotaCost": 50,
    },
    {
        "name": "target_comment_failure",
        "description": "Quota cost: 50. Preserve missing target comment failures as safe public errors.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "missing-comment", "snippet": {"textOriginal": "Updated comment text."}},
        },
        "error": {"category": "resource_not_found", "reason": "commentNotFound"},
        "quotaCost": 50,
    },
)

COMMENTS_SET_MODERATION_STATUS_DESCRIPTION = (
    "Set YouTube comment moderation status. Endpoint: comments.setModerationStatus. "
    "Quota cost: 50. Auth: oauth_required. Requires id and moderationStatus."
)
COMMENTS_SET_MODERATION_STATUS_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide one or more id values and one moderationStatus.",
    "Quota cost: 50. moderationStatus must be heldForReview, published, or rejected.",
    "Quota cost: 50. banAuthor is optional and only valid when moderationStatus is rejected.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegated owner context when supported by eligible OAuth authorization.",
)
COMMENTS_SET_MODERATION_STATUS_CAVEATS = (
    "comments_setModerationStatus changes moderation state for existing comments and requires eligible OAuth authorization.",
    "The request uses query-only fields; a request body is outside this tool boundary.",
    "Missing, duplicate, inaccessible, unsupported, or already ineligible target comments are surfaced as safe validation, authorization, or missing-resource failures.",
    "The tool does not perform comment listing, reply creation, comment editing, deletion, automated moderation, sentiment analysis, ranking, summarization, enrichment, or cross-endpoint aggregation.",
)
COMMENTS_SET_MODERATION_STATUS_CALLER_EXAMPLES = (
    {
        "name": "authorized_publish",
        "description": "Quota cost: 50. Publish a held comment with eligible OAuth.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "published"},
        "result": {"endpoint": "comments.setModerationStatus", "quotaCost": 50, "moderated": True},
        "quotaCost": 50,
    },
    {
        "name": "authorized_hold_for_review",
        "description": "Quota cost: 50. Move one or more comments to heldForReview.",
        "arguments": {"id": ["comment-123", "comment-456"], "moderationStatus": "heldForReview"},
        "result": {"endpoint": "comments.setModerationStatus", "quotaCost": 50, "moderationStatus": "heldForReview"},
        "quotaCost": 50,
    },
    {
        "name": "authorized_rejection_with_ban_author",
        "description": "Quota cost: 50. Reject a comment and request author ban handling.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "rejected", "banAuthor": True},
        "result": {"endpoint": "comments.setModerationStatus", "quotaCost": 50, "banAuthor": True},
        "quotaCost": 50,
    },
    {
        "name": "delegated_owner_context",
        "description": "Quota cost: 50. Moderate a comment with safe delegated owner context.",
        "arguments": {
            "id": ["comment-123"],
            "moderationStatus": "published",
            "onBehalfOfContentOwner": "content-owner-id",
        },
        "result": {"endpoint": "comments.setModerationStatus", "delegation": {"onBehalfOfContentOwner": True}},
        "quotaCost": 50,
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Reject moderation when eligible OAuth is unavailable.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "published"},
        "error": {"category": "authentication_failed", "field": "auth"},
        "quotaCost": 50,
    },
    {
        "name": "missing_target",
        "description": "Quota cost: 50. Reject moderation without a target comment id.",
        "arguments": {"moderationStatus": "published"},
        "error": {"category": "invalid_request", "field": "id"},
        "quotaCost": 50,
    },
    {
        "name": "duplicate_target",
        "description": "Quota cost: 50. Reject duplicate target comment ids.",
        "arguments": {"id": ["comment-123", "comment-123"], "moderationStatus": "rejected"},
        "error": {"category": "invalid_request", "field": "id"},
        "quotaCost": 50,
    },
    {
        "name": "missing_status",
        "description": "Quota cost: 50. Reject moderation without moderationStatus.",
        "arguments": {"id": ["comment-123"]},
        "error": {"category": "invalid_request", "field": "moderationStatus"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_status",
        "description": "Quota cost: 50. Reject moderationStatus values outside heldForReview, published, or rejected.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "spam"},
        "error": {"category": "invalid_request", "field": "moderationStatus"},
        "quotaCost": 50,
    },
    {
        "name": "incompatible_ban_author",
        "description": "Quota cost: 50. Reject banAuthor unless moderationStatus is rejected.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "published", "banAuthor": True},
        "error": {"category": "invalid_request", "field": "banAuthor"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_body",
        "description": "Quota cost: 50. Reject request body fields; moderation uses query-only inputs.",
        "arguments": {"id": ["comment-123"], "moderationStatus": "rejected", "body": {}},
        "error": {"category": "invalid_request", "field": "body"},
        "quotaCost": 50,
    },
    {
        "name": "target_comment_failure",
        "description": "Quota cost: 50. Preserve missing target comment failures as safe public errors.",
        "arguments": {"id": ["missing-comment"], "moderationStatus": "published"},
        "error": {"category": "resource_not_found", "reason": "commentNotFound"},
        "quotaCost": 50,
    },
)


class CommentsListToolError(ValueError):
    """Represent a safe caller-facing ``comments_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comments-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class CommentsInsertToolError(ValueError):
    """Represent a safe caller-facing ``comments_insert`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comments-insert error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class CommentsUpdateToolError(ValueError):
    """Represent a safe caller-facing ``comments_update`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comments-update error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class CommentsSetModerationStatusToolError(ValueError):
    """Represent a safe caller-facing ``comments_setModerationStatus`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comments moderation error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_comments_transport(execution) -> dict[str, Any]:
    """Return a safe comments response for local default execution.

    :param execution: Layer 1 execution request containing endpoint arguments.
    :return: Upstream-shaped comment response.
    """
    arguments = execution.arguments
    if execution.metadata.operation_name == "insert":
        parent_id = arguments.get("body", {}).get("snippet", {}).get("parentId")
        if parent_id == "missing-parent-comment":
            raise NormalizedUpstreamError(
                "parent comment not found",
                category="not_found",
                retryable=False,
                upstream_status=404,
                details={"reason": "parentCommentNotFound"},
            )
        if parent_id == "private-parent-comment":
            raise NormalizedUpstreamError(
                "parent comment is private",
                category="invalid_request",
                retryable=False,
                upstream_status=400,
                details={"reason": "parentCommentIsPrivate"},
            )
        if parent_id == "disabled-replies-comment":
            raise NormalizedUpstreamError(
                "operation not supported",
                category="invalid_request",
                retryable=False,
                upstream_status=400,
                details={"reason": "operationNotSupported"},
            )
        if parent_id == "quota-exhausted-comment":
            raise NormalizedUpstreamError(
                "quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={"reason": "quotaExceeded"},
            )
        if parent_id == "forbidden-parent-comment":
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"reason": "forbidden"},
            )
        return {
            "kind": "youtube#comment",
            "etag": "etag-123",
            "id": "created-comment-123",
            "snippet": {
                "parentId": parent_id or "comment-parent-123",
                "textOriginal": arguments.get("body", {}).get("snippet", {}).get("textOriginal", "Reply text"),
            },
        }
    if execution.metadata.operation_name == "update":
        body = arguments.get("body", {})
        comment_id = body.get("id")
        if comment_id == "missing-comment":
            raise NormalizedUpstreamError(
                "comment not found",
                category="not_found",
                retryable=False,
                upstream_status=404,
                details={"reason": "commentNotFound"},
            )
        if comment_id == "inaccessible-comment":
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"reason": "forbidden"},
            )
        if comment_id == "ineligible-account-comment":
            raise NormalizedUpstreamError(
                "ineligible account",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"reason": "ineligibleAccount"},
            )
        if comment_id == "quota-exhausted-comment":
            raise NormalizedUpstreamError(
                "quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={"reason": "quotaExceeded"},
            )
        return {
            "kind": "youtube#comment",
            "etag": "etag-123",
            "id": comment_id or "comment-123",
            "snippet": {
                "textOriginal": body.get("snippet", {}).get("textOriginal", "Updated comment text."),
            },
        }
    if execution.metadata.operation_name == "setModerationStatus":
        target_ids = _normalized_moderation_target_ids(arguments.get("id"))
        if "missing-comment" in target_ids:
            raise NormalizedUpstreamError(
                "comment not found",
                category="not_found",
                retryable=False,
                upstream_status=404,
                details={"reason": "commentNotFound"},
            )
        if "limited-moderation-comment" in target_ids:
            raise NormalizedUpstreamError(
                "operation not supported",
                category="invalid_request",
                retryable=False,
                upstream_status=400,
                details={"reason": "operationNotSupported"},
            )
        if "quota-exhausted-comment" in target_ids:
            raise NormalizedUpstreamError(
                "quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={"reason": "quotaExceeded"},
            )
        if "forbidden-comment" in target_ids or "inaccessible-comment" in target_ids:
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"reason": "forbidden"},
            )
        return {}
    if arguments.get("id") == "comment-empty" or arguments.get("parentId") == "comment-parent-without-replies":
        return {"items": []}
    if arguments.get("parentId"):
        return {
            "items": [{"id": "reply-123"}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }
    return {
        "kind": "youtube#commentListResponse",
        "etag": "etag-123",
        "items": [{"id": "comment-123"}],
    }


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by concrete comments tools.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_comments_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_comments_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``comments_list``.

    :return: Validated Layer 2 tool contract for ``comments_list``.
    """
    return YouTubeToolContract(
        tool_name=COMMENTS_LIST_TOOL_NAME,
        upstream_resource="comments",
        upstream_method="list",
        operation_key="comments.list",
        description=COMMENTS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=COMMENTS_LIST_QUOTA_COST,
        resource_family="comments",
        input_contract=COMMENTS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "pageInfo"],
            "selectorFields": list(COMMENTS_LIST_SELECTORS),
            "textFormatFields": list(COMMENTS_LIST_TEXT_FORMATS),
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "requestedParts",
                "selector",
                "textFormat",
                "items",
                "kind",
                "etag",
                "nextPageToken",
                "pageInfo",
            ),
            preserved_upstream_fields=("kind", "etag", "nextPageToken", "pageInfo", "items"),
            disallowed_behavior=(
                "comment_thread_discovery",
                "reply_creation",
                "comment_update",
                "comment_moderation",
                "comment_delete",
                "comment_search",
                "sentiment_analysis",
                "ranking",
                "summarization",
                "enrichment",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=COMMENTS_LIST_USAGE_NOTES,
        caveats=COMMENTS_LIST_CAVEATS,
    )


def build_comments_insert_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``comments_insert``.

    :return: Validated Layer 2 tool contract for ``comments_insert``.
    """
    return YouTubeToolContract(
        tool_name=COMMENTS_INSERT_TOOL_NAME,
        upstream_resource="comments",
        upstream_method="insert",
        operation_key="comments.insert",
        description=COMMENTS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=COMMENTS_INSERT_QUOTA_COST,
        resource_family="comments",
        input_contract=COMMENTS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "item",
            "requiredBodyFields": ["body.snippet.parentId", "body.snippet.textOriginal"],
            "delegationFields": ["onBehalfOfContentOwner"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "created",
                "requestedParts",
                "item",
                "auth",
                "delegation",
                "kind",
                "etag",
            ),
            preserved_upstream_fields=("kind", "etag", "id", "snippet"),
            disallowed_behavior=(
                "comment_listing",
                "top_level_thread_creation",
                "comment_update",
                "comment_moderation",
                "comment_delete",
                "generated_replies",
                "comment_search",
                "sentiment_analysis",
                "ranking",
                "summarization",
                "enrichment",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=COMMENTS_INSERT_USAGE_NOTES,
        caveats=COMMENTS_INSERT_CAVEATS,
    )


def build_comments_update_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``comments_update``.

    :return: Validated Layer 2 tool contract for ``comments_update``.
    """
    return YouTubeToolContract(
        tool_name=COMMENTS_UPDATE_TOOL_NAME,
        upstream_resource="comments",
        upstream_method="update",
        operation_key="comments.update",
        description=COMMENTS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=COMMENTS_UPDATE_QUOTA_COST,
        resource_family="comments",
        input_contract=COMMENTS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "requiredBodyFields": ["body.id", "body.snippet.textOriginal"],
            "supportedWritableParts": list(COMMENTS_UPDATE_SUPPORTED_PARTS),
            "writableBodyFields": ["body.snippet.textOriginal"],
            "delegationFields": ["onBehalfOfContentOwner"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "updated",
                "requestedParts",
                "writableFields",
                "item",
                "auth",
                "delegation",
                "kind",
                "etag",
            ),
            preserved_upstream_fields=("kind", "etag", "id", "snippet"),
            disallowed_behavior=(
                "comment_listing",
                "reply_creation",
                "top_level_thread_creation",
                "comment_moderation",
                "comment_delete",
                "generated_rewrites",
                "comment_search",
                "sentiment_analysis",
                "ranking",
                "summarization",
                "enrichment",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=COMMENTS_UPDATE_USAGE_NOTES,
        caveats=COMMENTS_UPDATE_CAVEATS,
    )


def build_comments_set_moderation_status_contract() -> YouTubeToolContract:
    """Build public contract metadata for ``comments_setModerationStatus``.

    :return: Validated Layer 2 tool contract for comment moderation.
    """
    return YouTubeToolContract(
        tool_name=COMMENTS_SET_MODERATION_STATUS_TOOL_NAME,
        upstream_resource="comments",
        upstream_method="setModerationStatus",
        operation_key="comments.setModerationStatus",
        description=COMMENTS_SET_MODERATION_STATUS_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=COMMENTS_SET_MODERATION_STATUS_QUOTA_COST,
        resource_family="comments",
        input_contract=COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA,
        response_convention={
            "resultKind": "mutation_acknowledgment",
            "successStatus": 204,
            "bodyPolicy": "no_upstream_body",
            "targetFields": ["id"],
            "requiredFields": ["id", "moderationStatus"],
            "supportedModerationStatuses": list(COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES),
            "optionalFlagRules": {"banAuthor": "only_with_rejected"},
            "delegationFields": ["onBehalfOfContentOwner"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "moderated",
                "targetIds",
                "moderationStatus",
                "banAuthor",
                "auth",
                "delegation",
                "statusCode",
            ),
            preserved_upstream_fields=(),
            disallowed_behavior=(
                "comment_listing",
                "reply_creation",
                "comment_editing",
                "comment_delete",
                "automated_moderation",
                "sentiment_analysis",
                "ranking",
                "summarization",
                "enrichment",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=COMMENTS_SET_MODERATION_STATUS_USAGE_NOTES,
        caveats=COMMENTS_SET_MODERATION_STATUS_CAVEATS,
    )


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested comment part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, str]]:
    """Return active comment retrieval selectors from one request.

    :param arguments: Caller-supplied ``comments_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, str]] = []
    for selector in COMMENTS_LIST_SELECTORS:
        value = arguments.get(selector)
        if isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
        elif selector in arguments:
            active.append((selector, ""))
    return active


def _raise_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``comments_list`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field responsible for the failure.
    :param details: Additional safe details to expose with the error.
    :raises CommentsListToolError: Always raised with ``invalid_request``.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentsListToolError(message, category="invalid_request", details=payload)


def _raise_insert_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``comments_insert`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field responsible for the failure.
    :param details: Additional safe details to expose with the error.
    :raises CommentsInsertToolError: Always raised with ``invalid_request``.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentsInsertToolError(message, category="invalid_request", details=payload)


def _raise_update_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``comments_update`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field responsible for the failure.
    :param details: Additional safe details to expose with the error.
    :raises CommentsUpdateToolError: Always raised with ``invalid_request``.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentsUpdateToolError(message, category="invalid_request", details=payload)


def _raise_set_moderation_status_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for moderation validation.

    :param message: Caller-facing validation message.
    :param field: Request field responsible for the failure.
    :param details: Additional safe details to expose with the error.
    :raises CommentsSetModerationStatusToolError: Always raised with ``invalid_request``.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentsSetModerationStatusToolError(message, category="invalid_request", details=payload)


def _normalized_moderation_target_ids(raw_ids: Any) -> tuple[str, ...]:
    """Return validated moderation target ids.

    :param raw_ids: Caller-supplied ``id`` value as a string or sequence.
    :return: Ordered, stripped comment ids.
    :raises CommentsSetModerationStatusToolError: If ids are missing, empty, or duplicated.
    """
    if isinstance(raw_ids, str):
        values = [raw_ids]
    elif isinstance(raw_ids, list | tuple):
        values = list(raw_ids)
    else:
        _raise_set_moderation_status_invalid("comments_setModerationStatus requires id.", "id")

    normalized_ids: list[str] = []
    for raw_value in values:
        if not isinstance(raw_value, str) or not raw_value.strip():
            _raise_set_moderation_status_invalid("comments_setModerationStatus requires id.", "id")
        normalized = raw_value.strip()
        if normalized in normalized_ids:
            _raise_set_moderation_status_invalid(
                "comments_setModerationStatus does not support duplicate target ids.",
                "id",
            )
        normalized_ids.append(normalized)
    if not normalized_ids:
        _raise_set_moderation_status_invalid("comments_setModerationStatus requires id.", "id")
    return tuple(normalized_ids)


def validate_comments_list_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate ``comments_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :return: Selected selector name and safe value.
    :raises CommentsListToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENTS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_invalid(f"comments_list does not support {field}.", field)

    if not isinstance(arguments.get("part"), str) or not arguments.get("part", "").strip():
        _raise_invalid("comments_list requires part.", "part")

    active = _active_selectors(arguments)
    if len(active) != 1:
        raise CommentsListToolError(
            "comments_list requires exactly one selector: id or parentId.",
            category="invalid_request",
            details={"field": "selector", "selectors": [name for name, _value in active]},
        )

    selector, value = active[0]
    if not value:
        _raise_invalid(f"comments_list requires a non-empty {selector}.", selector)

    if selector == "id":
        for field in ("maxResults", "pageToken"):
            if field in arguments:
                _raise_invalid(f"comments_list does not support {field} with id.", field, selector="id")

    max_results = arguments.get("maxResults")
    if max_results is not None and (not isinstance(max_results, int) or max_results < 1 or max_results > 100):
        _raise_invalid("maxResults must be between 1 and 100.", "maxResults")

    page_token = arguments.get("pageToken")
    if page_token is not None and (not isinstance(page_token, str) or not page_token.strip()):
        _raise_invalid("comments_list requires a non-empty pageToken.", "pageToken")

    text_format = arguments.get("textFormat")
    if text_format is not None and text_format not in COMMENTS_LIST_TEXT_FORMATS:
        _raise_invalid(
            "comments_list textFormat must be html or plainText.",
            "textFormat",
            allowed=list(COMMENTS_LIST_TEXT_FORMATS),
        )

    return selector, value


def _comments_list_auth_context(*, api_key: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``comments_list``.

    :param api_key: API-key value available for public comment retrieval.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentsListToolError: If API-key credentials are unavailable.
    """
    if not api_key:
        raise CommentsListToolError(
            "comments_list requires public API-key access.",
            category="authentication_failed",
            details={"authMode": "api_key"},
        )
    return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))


def validate_comments_insert_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate ``comments_insert`` arguments and return reply context.

    :param arguments: Caller-supplied tool arguments.
    :return: Parent comment id and reply text after whitespace validation.
    :raises CommentsInsertToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENTS_INSERT_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_insert_invalid(f"comments_insert does not support {field}.", field)

    if not isinstance(arguments.get("part"), str) or not arguments.get("part", "").strip():
        _raise_insert_invalid("comments_insert requires part.", "part")

    body = arguments.get("body")
    if not isinstance(body, dict):
        _raise_insert_invalid("comments_insert requires body.", "body")

    body_allowed = set(COMMENTS_INSERT_INPUT_SCHEMA["properties"]["body"]["properties"])
    for field in body:
        if field not in body_allowed:
            _raise_insert_invalid(f"comments_insert does not support body.{field}.", f"body.{field}")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        _raise_insert_invalid("comments_insert requires body.snippet.", "body.snippet")

    snippet_allowed = set(COMMENTS_INSERT_INPUT_SCHEMA["properties"]["body"]["properties"]["snippet"]["properties"])
    for field in snippet:
        if field not in snippet_allowed:
            _raise_insert_invalid(
                f"comments_insert does not support body.snippet.{field}.",
                f"body.snippet.{field}",
            )

    parent_id = snippet.get("parentId")
    if not isinstance(parent_id, str) or not parent_id.strip():
        _raise_insert_invalid("comments_insert requires body.snippet.parentId.", "body.snippet.parentId")

    reply_text = snippet.get("textOriginal")
    if not isinstance(reply_text, str) or not reply_text.strip():
        _raise_insert_invalid("comments_insert requires body.snippet.textOriginal.", "body.snippet.textOriginal")

    delegated_owner = arguments.get("onBehalfOfContentOwner")
    if delegated_owner is not None and (not isinstance(delegated_owner, str) or not delegated_owner.strip()):
        _raise_insert_invalid(
            "comments_insert requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
        )

    return parent_id.strip(), reply_text.strip()


def _comments_insert_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``comments_insert``.

    :param oauth_token: OAuth token available for reply creation.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentsInsertToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise CommentsInsertToolError(
            "comments_insert requires OAuth access.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def validate_comments_update_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate ``comments_update`` arguments and return update context.

    :param arguments: Caller-supplied tool arguments.
    :return: Target comment id and updated text after whitespace validation.
    :raises CommentsUpdateToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENTS_UPDATE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_update_invalid(f"comments_update does not support {field}.", field)

    requested_parts = _requested_parts(arguments)
    if not requested_parts:
        _raise_update_invalid("comments_update requires part.", "part")
    unsupported_parts = [part for part in requested_parts if part not in COMMENTS_UPDATE_SUPPORTED_PARTS]
    if unsupported_parts:
        _raise_update_invalid(
            "comments_update supports only the snippet part.",
            "part",
            allowed=list(COMMENTS_UPDATE_SUPPORTED_PARTS),
            requested=unsupported_parts,
        )

    body = arguments.get("body")
    if not isinstance(body, dict):
        _raise_update_invalid("comments_update requires body.", "body")

    body_allowed = set(COMMENTS_UPDATE_INPUT_SCHEMA["properties"]["body"]["properties"])
    for field in body:
        if field not in body_allowed:
            _raise_update_invalid(f"comments_update does not support body.{field}.", f"body.{field}")

    comment_id = body.get("id")
    if not isinstance(comment_id, str) or not comment_id.strip():
        _raise_update_invalid("comments_update requires body.id.", "body.id")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        _raise_update_invalid("comments_update requires body.snippet.", "body.snippet")

    snippet_allowed = set(COMMENTS_UPDATE_INPUT_SCHEMA["properties"]["body"]["properties"]["snippet"]["properties"])
    for field in snippet:
        if field not in snippet_allowed:
            _raise_update_invalid(
                f"comments_update does not support body.snippet.{field}.",
                f"body.snippet.{field}",
            )

    updated_text = snippet.get("textOriginal")
    if not isinstance(updated_text, str) or not updated_text.strip():
        _raise_update_invalid("comments_update requires body.snippet.textOriginal.", "body.snippet.textOriginal")

    delegated_owner = arguments.get("onBehalfOfContentOwner")
    if delegated_owner is not None and (not isinstance(delegated_owner, str) or not delegated_owner.strip()):
        _raise_update_invalid(
            "comments_update requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
        )

    return comment_id.strip(), updated_text.strip()


def _comments_update_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``comments_update``.

    :param oauth_token: OAuth token available for comment editing.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentsUpdateToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise CommentsUpdateToolError(
            "comments_update requires OAuth access.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def validate_comments_set_moderation_status_arguments(arguments: dict[str, Any]) -> tuple[tuple[str, ...], str]:
    """Validate moderation arguments and return target ids and status.

    :param arguments: Caller-supplied moderation arguments.
    :return: Target comment ids and moderation status after validation.
    :raises CommentsSetModerationStatusToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_set_moderation_status_invalid(
                f"comments_setModerationStatus does not support {field}.",
                field,
            )

    target_ids = _normalized_moderation_target_ids(arguments.get("id"))

    moderation_status = arguments.get("moderationStatus")
    if not isinstance(moderation_status, str) or not moderation_status.strip():
        _raise_set_moderation_status_invalid(
            "comments_setModerationStatus requires moderationStatus.",
            "moderationStatus",
        )
    moderation_status = moderation_status.strip()
    if moderation_status not in COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES:
        _raise_set_moderation_status_invalid(
            f"unsupported moderationStatus: {moderation_status}",
            "moderationStatus",
            allowed=list(COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES),
        )

    ban_author = arguments.get("banAuthor")
    if ban_author is not None and not isinstance(ban_author, bool):
        _raise_set_moderation_status_invalid("banAuthor must be a boolean when provided.", "banAuthor")
    if ban_author and moderation_status != "rejected":
        _raise_set_moderation_status_invalid(
            "banAuthor is only supported when moderationStatus is rejected.",
            "banAuthor",
        )

    delegated_owner = arguments.get("onBehalfOfContentOwner")
    if delegated_owner is not None and (not isinstance(delegated_owner, str) or not delegated_owner.strip()):
        _raise_set_moderation_status_invalid(
            "comments_setModerationStatus requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
        )

    return target_ids, moderation_status


def _comments_set_moderation_status_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for comment moderation.

    :param oauth_token: OAuth token available for moderation status changes.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentsSetModerationStatusToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise CommentsSetModerationStatusToolError(
            "comments_setModerationStatus requires OAuth access.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def map_comments_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 comment response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw comment collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "comments.list",
        "quotaCost": COMMENTS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
        "textFormat": arguments.get("textFormat") or "html",
    }
    for field in ("kind", "etag", "nextPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def _safe_insert_delegation_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe delegation flags for one insert request.

    :param arguments: Caller-supplied ``comments_insert`` arguments.
    :return: Safe delegation flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_comments_insert_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 comment insert response to the public result shape.

    :param response: Upstream-shaped created comment resource.
    :param arguments: Original validated tool arguments.
    :return: Near-raw created comment result with safe MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "comments.insert",
        "quotaCost": COMMENTS_INSERT_QUOTA_COST,
        "created": True,
        "requestedParts": _requested_parts(arguments),
        "item": response,
        "auth": {"mode": "oauth_required"},
    }
    delegation_context = _safe_insert_delegation_context(arguments)
    if delegation_context:
        result["delegation"] = delegation_context
    for field in ("kind", "etag"):
        if field in response:
            result[field] = response[field]
    return result


def _safe_update_delegation_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe delegation flags for one update request.

    :param arguments: Caller-supplied ``comments_update`` arguments.
    :return: Safe delegation flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_comments_update_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 comment update response to the public result shape.

    :param response: Upstream-shaped updated comment resource.
    :param arguments: Original validated tool arguments.
    :return: Near-raw updated comment result with safe MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "comments.update",
        "quotaCost": COMMENTS_UPDATE_QUOTA_COST,
        "updated": True,
        "requestedParts": _requested_parts(arguments),
        "writableFields": ["body.snippet.textOriginal"],
        "item": response,
        "auth": {"mode": "oauth_required"},
    }
    delegation_context = _safe_update_delegation_context(arguments)
    if delegation_context:
        result["delegation"] = delegation_context
    for field in ("kind", "etag"):
        if field in response:
            result[field] = response[field]
    return result


def _safe_set_moderation_status_delegation_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe delegation flags for one moderation request.

    :param arguments: Caller-supplied moderation arguments.
    :return: Safe delegation flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_comments_set_moderation_status_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a moderation success response to the public acknowledgment shape.

    :param response: Empty upstream-shaped no-content response.
    :param arguments: Original validated tool arguments.
    :return: Safe mutation acknowledgment with target and status context.
    """
    target_ids = _normalized_moderation_target_ids(arguments.get("id"))
    result: dict[str, Any] = {
        "endpoint": "comments.setModerationStatus",
        "quotaCost": COMMENTS_SET_MODERATION_STATUS_QUOTA_COST,
        "moderated": True,
        "targetIds": list(target_ids),
        "moderationStatus": str(arguments.get("moderationStatus", "")).strip(),
        "auth": {"mode": "oauth_required"},
        "statusCode": 204,
    }
    if "banAuthor" in arguments:
        result["banAuthor"] = bool(arguments["banAuthor"])
    delegation_context = _safe_set_moderation_status_delegation_context(arguments)
    if delegation_context:
        result["delegation"] = delegation_context
    return result


def _map_comments_list_upstream_error(error: NormalizedUpstreamError) -> CommentsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``comments_list`` error.
    """
    categories = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentsListToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def _map_comments_insert_upstream_error(error: NormalizedUpstreamError) -> CommentsInsertToolError:
    """Map a normalized upstream error to the public insert error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``comments_insert`` error.
    """
    categories = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentsInsertToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def _map_comments_update_upstream_error(error: NormalizedUpstreamError) -> CommentsUpdateToolError:
    """Map a normalized upstream error to the public update error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``comments_update`` error.
    """
    categories = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentsUpdateToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def _map_comments_set_moderation_status_upstream_error(
    error: NormalizedUpstreamError,
) -> CommentsSetModerationStatusToolError:
    """Map a normalized upstream error to the public moderation error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``comments_setModerationStatus`` error.
    """
    categories = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentsSetModerationStatusToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def build_comments_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-comment-access",
):
    """Build the concrete ``comments_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public comment retrieval.
    :return: Callable dispatcher handler.
    """
    comments_wrapper = wrapper or build_comments_list_wrapper()
    comments_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``comments_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 comment collection result.
        :raises CommentsListToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comments_list_arguments(arguments)
        auth_context = _comments_list_auth_context(api_key=api_key)
        try:
            response = comments_wrapper.call(comments_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_comments_list_upstream_error(error) from error
        except ValueError as error:
            raise CommentsListToolError(
                str(error),
                category="invalid_request",
                details={"field": "selector"},
            ) from error
        return map_comments_list_result(response, arguments)

    return handler


def build_comments_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-write",
):
    """Build the concrete ``comments_insert`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for reply creation.
    :return: Callable dispatcher handler.
    """
    comments_wrapper = wrapper or build_comments_insert_wrapper()
    comments_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``comments_insert`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 created comment result.
        :raises CommentsInsertToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comments_insert_arguments(arguments)
        auth_context = _comments_insert_auth_context(oauth_token=oauth_token)
        try:
            response = comments_wrapper.call(comments_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_comments_insert_upstream_error(error) from error
        except ValueError as error:
            raise CommentsInsertToolError(
                str(error),
                category="invalid_request",
                details={"field": "body"},
            ) from error
        except Exception as error:
            raise CommentsInsertToolError(
                "comments_insert upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_comments_insert_result(response, arguments)

    return handler


def build_comments_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-write",
):
    """Build the concrete ``comments_update`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for comment editing.
    :return: Callable dispatcher handler.
    """
    comments_wrapper = wrapper or build_comments_update_wrapper()
    comments_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``comments_update`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 updated comment result.
        :raises CommentsUpdateToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comments_update_arguments(arguments)
        auth_context = _comments_update_auth_context(oauth_token=oauth_token)
        try:
            response = comments_wrapper.call(comments_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_comments_update_upstream_error(error) from error
        except ValueError as error:
            raise CommentsUpdateToolError(
                str(error),
                category="invalid_request",
                details={"field": "body"},
            ) from error
        except Exception as error:
            raise CommentsUpdateToolError(
                "comments_update upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_comments_update_result(response, arguments)

    return handler


def build_comments_set_moderation_status_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-moderation",
):
    """Build the concrete ``comments_setModerationStatus`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for moderation status changes.
    :return: Callable dispatcher handler.
    """
    comments_wrapper = wrapper or build_comments_set_moderation_status_wrapper()
    comments_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``comments_setModerationStatus`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 moderation acknowledgment result.
        :raises CommentsSetModerationStatusToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comments_set_moderation_status_arguments(arguments)
        auth_context = _comments_set_moderation_status_auth_context(oauth_token=oauth_token)
        try:
            response = comments_wrapper.call(comments_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_comments_set_moderation_status_upstream_error(error) from error
        except ValueError as error:
            raise CommentsSetModerationStatusToolError(
                str(error),
                category="invalid_request",
                details={"field": "id"},
            ) from error
        except Exception as error:
            raise CommentsSetModerationStatusToolError(
                "comments_setModerationStatus upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_comments_set_moderation_status_result(response, arguments)

    return handler


def build_comments_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-comment-access",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``comments_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public comment retrieval.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comments_list_contract()
    return {
        "name": COMMENTS_LIST_TOOL_NAME,
        "description": COMMENTS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENTS_LIST_INPUT_SCHEMA,
        "handler": build_comments_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
    }


def build_comments_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``comments_insert`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for reply creation.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comments_insert_contract()
    return {
        "name": COMMENTS_INSERT_TOOL_NAME,
        "description": COMMENTS_INSERT_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENTS_INSERT_INPUT_SCHEMA,
        "handler": build_comments_insert_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
    }


def build_comments_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``comments_update`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for comment editing.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comments_update_contract()
    return {
        "name": COMMENTS_UPDATE_TOOL_NAME,
        "description": COMMENTS_UPDATE_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENTS_UPDATE_INPUT_SCHEMA,
        "handler": build_comments_update_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
    }


def build_comments_set_moderation_status_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-moderation",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for ``comments_setModerationStatus``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for moderation status changes.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comments_set_moderation_status_contract()
    return {
        "name": COMMENTS_SET_MODERATION_STATUS_TOOL_NAME,
        "description": COMMENTS_SET_MODERATION_STATUS_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA,
        "handler": build_comments_set_moderation_status_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "COMMENTS_INSERT_CALLER_EXAMPLES",
    "COMMENTS_INSERT_CAVEATS",
    "COMMENTS_INSERT_DESCRIPTION",
    "COMMENTS_INSERT_INPUT_SCHEMA",
    "COMMENTS_INSERT_QUOTA_COST",
    "COMMENTS_INSERT_TOOL_NAME",
    "COMMENTS_INSERT_USAGE_NOTES",
    "COMMENTS_SET_MODERATION_STATUS_CALLER_EXAMPLES",
    "COMMENTS_SET_MODERATION_STATUS_CAVEATS",
    "COMMENTS_SET_MODERATION_STATUS_DESCRIPTION",
    "COMMENTS_SET_MODERATION_STATUS_INPUT_SCHEMA",
    "COMMENTS_SET_MODERATION_STATUS_QUOTA_COST",
    "COMMENTS_SET_MODERATION_STATUS_SUPPORTED_STATUSES",
    "COMMENTS_SET_MODERATION_STATUS_TOOL_NAME",
    "COMMENTS_SET_MODERATION_STATUS_USAGE_NOTES",
    "COMMENTS_UPDATE_CALLER_EXAMPLES",
    "COMMENTS_UPDATE_CAVEATS",
    "COMMENTS_UPDATE_DESCRIPTION",
    "COMMENTS_UPDATE_INPUT_SCHEMA",
    "COMMENTS_UPDATE_QUOTA_COST",
    "COMMENTS_UPDATE_SUPPORTED_PARTS",
    "COMMENTS_UPDATE_TOOL_NAME",
    "COMMENTS_UPDATE_USAGE_NOTES",
    "COMMENTS_LIST_CALLER_EXAMPLES",
    "COMMENTS_LIST_CAVEATS",
    "COMMENTS_LIST_DESCRIPTION",
    "COMMENTS_LIST_INPUT_SCHEMA",
    "COMMENTS_LIST_QUOTA_COST",
    "COMMENTS_LIST_SELECTORS",
    "COMMENTS_LIST_TEXT_FORMATS",
    "COMMENTS_LIST_TOOL_NAME",
    "COMMENTS_LIST_USAGE_NOTES",
    "CommentsInsertToolError",
    "CommentsListToolError",
    "CommentsSetModerationStatusToolError",
    "CommentsUpdateToolError",
    "build_comments_insert_contract",
    "build_comments_insert_handler",
    "build_comments_insert_tool_descriptor",
    "build_comments_set_moderation_status_contract",
    "build_comments_set_moderation_status_handler",
    "build_comments_set_moderation_status_tool_descriptor",
    "build_comments_update_contract",
    "build_comments_update_handler",
    "build_comments_update_tool_descriptor",
    "build_comments_list_contract",
    "build_comments_list_handler",
    "build_comments_list_tool_descriptor",
    "map_comments_insert_result",
    "map_comments_set_moderation_status_result",
    "map_comments_update_result",
    "map_comments_list_result",
    "validate_comments_insert_arguments",
    "validate_comments_set_moderation_status_arguments",
    "validate_comments_update_arguments",
    "validate_comments_list_arguments",
]
