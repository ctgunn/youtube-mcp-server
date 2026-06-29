"""Concrete Layer 2 tool support for the YouTube ``commentThreads`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.comment_threads import (
    build_comment_threads_insert_wrapper,
    build_comment_threads_list_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


COMMENT_THREADS_LIST_TOOL_NAME = "commentThreads_list"
COMMENT_THREADS_LIST_QUOTA_COST = 1
COMMENT_THREADS_LIST_SELECTORS = ("videoId", "allThreadsRelatedToChannelId", "id")
COMMENT_THREADS_LIST_TEXT_FORMATS = ("html", "plainText")
COMMENT_THREADS_LIST_MODERATION_STATUSES = ("heldForReview", "likelySpam", "published")
COMMENT_THREADS_LIST_ORDERS = ("time", "relevance")
COMMENT_THREADS_INSERT_TOOL_NAME = "commentThreads_insert"
COMMENT_THREADS_INSERT_QUOTA_COST = 50
COMMENT_THREADS_INSERT_SUPPORTED_PARTS = ("id", "snippet", "replies")

COMMENT_THREADS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "videoId": {"type": "string", "minLength": 1},
        "allThreadsRelatedToChannelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
        "moderationStatus": {"type": "string", "enum": list(COMMENT_THREADS_LIST_MODERATION_STATUSES)},
        "order": {"type": "string", "enum": list(COMMENT_THREADS_LIST_ORDERS)},
        "pageToken": {"type": "string", "minLength": 1},
        "searchTerms": {"type": "string", "minLength": 1},
        "textFormat": {"type": "string", "enum": list(COMMENT_THREADS_LIST_TEXT_FORMATS)},
    },
    "oneOf": [{"required": [selector]} for selector in COMMENT_THREADS_LIST_SELECTORS],
    "additionalProperties": False,
}

COMMENT_THREADS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(COMMENT_THREADS_INSERT_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["channelId", "videoId", "topLevelComment"],
                    "properties": {
                        "channelId": {"type": "string", "minLength": 1},
                        "videoId": {"type": "string", "minLength": 1},
                        "topLevelComment": {
                            "type": "object",
                            "required": ["snippet"],
                            "properties": {
                                "snippet": {
                                    "type": "object",
                                    "required": ["textOriginal"],
                                    "properties": {"textOriginal": {"type": "string", "minLength": 1}},
                                    "additionalProperties": False,
                                }
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

COMMENT_THREADS_LIST_DESCRIPTION = (
    "List YouTube comment threads. Endpoint: commentThreads.list. "
    "Quota cost: 1. Auth: api_key. Supports videoId, allThreadsRelatedToChannelId, or id selectors."
)

COMMENT_THREADS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part and exactly one selector: videoId, "
    "allThreadsRelatedToChannelId, or id.",
    "Quota cost: 1. Use maxResults, pageToken, order, searchTerms, moderationStatus, "
    "and textFormat only with videoId or allThreadsRelatedToChannelId selectors.",
    "Quota cost: 1. textFormat defaults to html; pass plainText when caller-readable text is preferred.",
    "Quota cost: 1. Empty upstream item collections are returned as successful no-match results.",
)

COMMENT_THREADS_LIST_CAVEATS = (
    "This is a read-only list wrapper; it does not create, update, delete, moderate, or summarize comments.",
    "id lookup does not support maxResults, moderationStatus, order, pageToken, or searchTerms.",
    "moderationStatus can be access-sensitive upstream; unauthorized or unavailable states are surfaced as safe errors.",
    "reply-only listing belongs to comments_list, not commentThreads_list.",
    "Higher-level behavior such as ranking, enrichment, cross-endpoint aggregation, and summarization is out of scope.",
)

COMMENT_THREADS_LIST_CALLER_EXAMPLES = (
    {
        "name": "video_lookup",
        "description": "Quota cost: 1. List comment threads for one video.",
        "arguments": {"part": "snippet,replies", "videoId": "video-123"},
        "result": {"endpoint": "commentThreads.list", "selector": "videoId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "channel_related_lookup",
        "description": "Quota cost: 1. List comment threads related to a channel.",
        "arguments": {"part": "snippet", "allThreadsRelatedToChannelId": "channel-123"},
        "result": {"endpoint": "commentThreads.list", "selector": "allThreadsRelatedToChannelId"},
        "quotaCost": 1,
    },
    {
        "name": "id_lookup",
        "description": "Quota cost: 1. Retrieve a specific comment thread by id.",
        "arguments": {"part": "id,snippet", "id": "thread-123"},
        "result": {"endpoint": "commentThreads.list", "selector": "id"},
        "quotaCost": 1,
    },
    {
        "name": "paginated_video_lookup",
        "description": "Quota cost: 1. Continue video-thread retrieval with pageToken.",
        "arguments": {"part": "snippet", "videoId": "video-123", "maxResults": 25, "pageToken": "NEXT_PAGE"},
        "quotaCost": 1,
    },
    {
        "name": "ordered_search_lookup",
        "description": "Quota cost: 1. Search video threads and order them by relevance.",
        "arguments": {"part": "snippet", "videoId": "video-123", "order": "relevance", "searchTerms": "launch"},
        "quotaCost": 1,
    },
    {
        "name": "plain_text_lookup",
        "description": "Quota cost: 1. Request plainText comment thread snippets.",
        "arguments": {"part": "snippet", "videoId": "video-123", "textFormat": "plainText"},
        "quotaCost": 1,
    },
    {
        "name": "moderation_status_lookup",
        "description": "Quota cost: 1. Request an access-sensitive moderationStatus view.",
        "arguments": {"part": "snippet", "videoId": "video-123", "moderationStatus": "published"},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. Preserve empty thread collections as successful empty items.",
        "arguments": {"part": "snippet", "videoId": "video-without-threads"},
        "result": {"items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_selector",
        "description": "Quota cost: 1. Reject requests without a selector.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
        "quotaCost": 1,
    },
    {
        "name": "conflicting_selectors",
        "description": "Quota cost: 1. Reject requests with multiple selectors.",
        "arguments": {"part": "snippet", "videoId": "video-123", "id": "thread-123"},
        "error": {"category": "invalid_request", "field": "selector"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_id",
        "description": "Quota cost: 1. Surface missing or invalid thread identifiers safely.",
        "arguments": {"part": "snippet", "id": "missing-thread"},
        "error": {"category": "resource_not_found", "reason": "commentThreadNotFound"},
        "quotaCost": 1,
    },
    {
        "name": "unsupported_id_option",
        "description": "Quota cost: 1. Reject id lookup with pagination or search modifiers.",
        "arguments": {"part": "snippet", "id": "thread-123", "maxResults": 25},
        "error": {"category": "invalid_request", "field": "maxResults"},
        "quotaCost": 1,
    },
    {
        "name": "disabled_comments",
        "description": "Quota cost: 1. Preserve disabled-comments failures as safe invalid requests.",
        "arguments": {"part": "snippet", "videoId": "comments-disabled-video"},
        "error": {"category": "invalid_request", "reason": "commentsDisabled"},
        "quotaCost": 1,
    },
    {
        "name": "access_sensitive_failure",
        "description": "Quota cost: 1. Preserve access-sensitive upstream failures without exposing secrets.",
        "arguments": {"part": "snippet", "videoId": "restricted-video", "moderationStatus": "heldForReview"},
        "error": {"category": "authorization_failed", "reason": "forbidden"},
        "quotaCost": 1,
    },
)

COMMENT_THREADS_INSERT_DESCRIPTION = (
    "Create a YouTube top-level comment thread. Endpoint: commentThreads.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires part and a body with channelId, videoId, "
    "and topLevelComment.snippet.textOriginal."
)

COMMENT_THREADS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and body.snippet.channelId, "
    "body.snippet.videoId, and body.snippet.topLevelComment.snippet.textOriginal.",
    "Quota cost: 50. commentThreads_insert creates top-level comments only; reply creation belongs to comments_insert.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegation context when eligible OAuth access supports it.",
    "Quota cost: 50. Successful results preserve the created commentThread resource with safe target and auth context.",
)

COMMENT_THREADS_INSERT_CAVEATS = (
    "This is a write operation and requires eligible OAuth authorization; API-key-only access is unsupported.",
    "The tool creates top-level comment threads and does not list threads, create replies, edit comments, delete comments, or moderate comments.",
    "body.snippet.channelId, body.snippet.videoId, and body.snippet.topLevelComment.snippet.textOriginal are required.",
    "Missing channels, missing videos, disabled comments, invalid metadata, text validation failures, quota failures, and authorization failures are surfaced as safe errors.",
    "Higher-level behavior such as generated responses, sentiment analysis, ranking, summarization, enrichment, analytics, and cross-endpoint aggregation is out of scope.",
)

COMMENT_THREADS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_top_level_create",
        "description": "Quota cost: 50. Create a top-level comment thread with eligible OAuth access.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Great walkthrough."}},
                }
            },
        },
        "result": {"endpoint": "commentThreads.insert", "created": True, "itemPath": "item"},
        "quotaCost": 50,
    },
    {
        "name": "delegated_owner_context",
        "description": "Quota cost: 50. Create with optional delegated owner context.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Posting from the channel team."}},
                }
            },
            "onBehalfOfContentOwner": "CONTENT_OWNER_ID",
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Reject creation when OAuth access is unavailable.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject requests without part.",
        "arguments": {
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            }
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "missing_channel",
        "description": "Quota cost: 50. Reject requests without body.snippet.channelId.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.channelId"},
        "quotaCost": 50,
    },
    {
        "name": "missing_video",
        "description": "Quota cost: 50. Reject requests without body.snippet.videoId.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.videoId"},
        "quotaCost": 50,
    },
    {
        "name": "missing_top_level_text",
        "description": "Quota cost: 50. Reject requests without top-level comment text.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {}},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.topLevelComment.snippet.textOriginal"},
        "quotaCost": 50,
    },
    {
        "name": "invalid_target_context",
        "description": "Quota cost: 50. Reject requests whose body does not provide one clear channel/video target.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": " ",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "target"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_reply_shape",
        "description": "Quota cost: 50. Reject reply-style requests; replies belong to comments_insert.",
        "arguments": {"part": "snippet", "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply"}}},
        "error": {"category": "invalid_request", "field": "body.snippet.parentId"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 50. Reject list, moderation, search, and generated-response options.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
            "moderationStatus": "published",
        },
        "error": {"category": "invalid_request", "field": "moderationStatus"},
        "quotaCost": 50,
    },
    {
        "name": "disabled_comments",
        "description": "Quota cost: 50. Preserve disabled-comments failures as safe invalid requests.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "channel-123",
                    "videoId": "comments-disabled-video",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "invalid_request", "reason": "commentsDisabled"},
        "quotaCost": 50,
    },
    {
        "name": "access_sensitive_failure",
        "description": "Quota cost: 50. Preserve access failures without exposing secrets.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "channelId": "restricted-channel",
                    "videoId": "video-123",
                    "topLevelComment": {"snippet": {"textOriginal": "Top-level comment text"}},
                }
            },
        },
        "error": {"category": "authorization_failed", "reason": "forbidden"},
        "quotaCost": 50,
    },
)


class CommentThreadsListToolError(ValueError):
    """Represent a safe caller-facing ``commentThreads_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comment-threads-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class CommentThreadsInsertToolError(ValueError):
    """Represent a safe caller-facing ``commentThreads_insert`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe comment-threads-insert error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_comment_threads_transport(execution) -> dict[str, Any]:
    """Return a safe comment-thread response for local default execution.

    :param execution: Layer 1 execution request containing endpoint arguments.
    :return: Upstream-shaped comment-thread response.
    :raises NormalizedUpstreamError: If a representative upstream failure is requested.
    """
    arguments = execution.arguments
    operation_key = getattr(execution.metadata, "operation_key", "")
    if operation_key == "commentThreads.insert":
        body = arguments.get("body", {})
        snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        video_id = snippet.get("videoId")
        channel_id = snippet.get("channelId")
        text = (
            snippet.get("topLevelComment", {})
            .get("snippet", {})
            .get("textOriginal", "Top-level comment text")
            if isinstance(snippet.get("topLevelComment"), dict)
            else "Top-level comment text"
        )
        if video_id == "comments-disabled-video":
            raise NormalizedUpstreamError(
                "comments disabled",
                category="invalid_request",
                retryable=False,
                upstream_status=403,
                details={"reason": "commentsDisabled"},
            )
        if video_id == "missing-video":
            raise NormalizedUpstreamError(
                "video not found",
                category="not_found",
                retryable=False,
                upstream_status=404,
                details={"reason": "videoNotFound"},
            )
        if channel_id == "missing-channel":
            raise NormalizedUpstreamError(
                "channel not found",
                category="not_found",
                retryable=False,
                upstream_status=404,
                details={"reason": "channelNotFound"},
            )
        if channel_id == "restricted-channel":
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"reason": "forbidden"},
            )
        if video_id == "quota-exhausted-video":
            raise NormalizedUpstreamError(
                "quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={"reason": "quotaExceeded"},
            )
        return {
            "kind": "youtube#commentThread",
            "id": "thread-video-123",
            "snippet": {
                "channelId": channel_id or "channel-123",
                "videoId": video_id or "video-123",
                "topLevelComment": {"snippet": {"textOriginal": text}},
            },
        }

    video_id = arguments.get("videoId")
    channel_id = arguments.get("allThreadsRelatedToChannelId")
    thread_id = arguments.get("id")

    if video_id == "comments-disabled-video":
        raise NormalizedUpstreamError(
            "comments disabled",
            category="invalid_request",
            retryable=False,
            upstream_status=403,
            details={"reason": "commentsDisabled"},
        )
    if video_id == "missing-video":
        raise NormalizedUpstreamError(
            "video not found",
            category="not_found",
            retryable=False,
            upstream_status=404,
            details={"reason": "videoNotFound"},
        )
    if video_id == "restricted-video":
        raise NormalizedUpstreamError(
            "forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={"reason": "forbidden"},
        )
    if channel_id == "missing-channel":
        raise NormalizedUpstreamError(
            "channel not found",
            category="not_found",
            retryable=False,
            upstream_status=404,
            details={"reason": "channelNotFound"},
        )
    if thread_id == "missing-thread":
        raise NormalizedUpstreamError(
            "comment thread not found",
            category="not_found",
            retryable=False,
            upstream_status=404,
            details={"reason": "commentThreadNotFound"},
        )
    if thread_id == "quota-exhausted-thread":
        raise NormalizedUpstreamError(
            "quota exceeded",
            category="rate_limit",
            retryable=False,
            upstream_status=403,
            details={"reason": "quotaExceeded"},
        )
    if video_id == "video-without-threads" or channel_id == "channel-without-threads":
        return {"items": []}
    if channel_id:
        return {
            "items": [{"id": "thread-channel-123", "snippet": {"channelId": channel_id}}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }
    if thread_id:
        return {"items": [{"id": thread_id}]}
    return {
        "kind": "youtube#commentThreadListResponse",
        "etag": "etag-123",
        "items": [{"id": "thread-video-123", "snippet": {"videoId": video_id or "video-123"}}],
    }


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by concrete comment-thread tools.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_comment_threads_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_comment_threads_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``commentThreads_list``.

    :return: Validated Layer 2 tool contract for ``commentThreads_list``.
    """
    return YouTubeToolContract(
        tool_name=COMMENT_THREADS_LIST_TOOL_NAME,
        upstream_resource="commentThreads",
        upstream_method="list",
        operation_key="commentThreads.list",
        description=COMMENT_THREADS_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=COMMENT_THREADS_LIST_QUOTA_COST,
        resource_family="comment_threads",
        input_contract=COMMENT_THREADS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "pageInfo"],
            "selectorFields": list(COMMENT_THREADS_LIST_SELECTORS),
            "textFormatFields": list(COMMENT_THREADS_LIST_TEXT_FORMATS),
            "optionalContextFields": ["maxResults", "moderationStatus", "order", "pageToken", "searchTerms"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
            "bodyPolicy": "no_request_body",
            "idUnsupportedFields": ["maxResults", "moderationStatus", "order", "pageToken", "searchTerms"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "requestedParts",
                "selector",
                "textFormat",
                "options",
                "items",
                "kind",
                "etag",
                "nextPageToken",
                "pageInfo",
            ),
            preserved_upstream_fields=("kind", "etag", "nextPageToken", "pageInfo", "items"),
            disallowed_behavior=(
                "reply-only listing",
                "comment_creation",
                "comment_update",
                "comment_moderation",
                "comment_delete",
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
        usage_notes=COMMENT_THREADS_LIST_USAGE_NOTES,
        caveats=COMMENT_THREADS_LIST_CAVEATS,
    )


def build_comment_threads_insert_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``commentThreads_insert``.

    :return: Validated Layer 2 tool contract for ``commentThreads_insert``.
    """
    return YouTubeToolContract(
        tool_name=COMMENT_THREADS_INSERT_TOOL_NAME,
        upstream_resource="commentThreads",
        upstream_method="insert",
        operation_key="commentThreads.insert",
        description=COMMENT_THREADS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=COMMENT_THREADS_INSERT_QUOTA_COST,
        resource_family="comment_threads",
        input_contract=COMMENT_THREADS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "item",
            "requiredBodyFields": [
                "body.snippet.channelId",
                "body.snippet.videoId",
                "body.snippet.topLevelComment.snippet.textOriginal",
            ],
            "targetFields": ["body.snippet.channelId", "body.snippet.videoId"],
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
                "target",
                "delegation",
                "kind",
                "etag",
            ),
            preserved_upstream_fields=("kind", "etag", "id", "snippet", "replies"),
            disallowed_behavior=(
                "thread_listing",
                "reply_creation",
                "comment_update",
                "comment_moderation",
                "comment_delete",
                "generated_responses",
                "sentiment_analysis",
                "ranking",
                "summarization",
                "enrichment",
                "analytics",
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
        usage_notes=COMMENT_THREADS_INSERT_USAGE_NOTES,
        caveats=COMMENT_THREADS_INSERT_CAVEATS,
    )


def _raise_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``commentThreads_list`` validation.

    :param message: Caller-facing validation message.
    :param field: Input field associated with the failure.
    :param details: Additional safe validation details.
    :raises CommentThreadsListToolError: Always raised.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentThreadsListToolError(message, category="invalid_request", details=payload)


def _raise_insert_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``commentThreads_insert`` validation.

    :param message: Caller-facing validation message.
    :param field: Input field associated with the failure.
    :param details: Additional safe validation details.
    :raises CommentThreadsInsertToolError: Always raised.
    """
    payload = {"field": field}
    payload.update(details)
    raise CommentThreadsInsertToolError(message, category="invalid_request", details=payload)


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, str]]:
    """Return active comment-thread selector fields and stripped values.

    :param arguments: Caller-supplied tool arguments.
    :return: Selector names with normalized non-empty string values.
    """
    active = []
    for selector in COMMENT_THREADS_LIST_SELECTORS:
        value = arguments.get(selector)
        if isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
        elif selector in arguments:
            active.append((selector, ""))
    return active


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Normalize a comma-separated ``part`` request into public metadata.

    :param arguments: Caller-supplied tool arguments.
    :return: Ordered non-empty requested part names.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _comment_threads_insert_snippet(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return the validated top-level insert snippet.

    :param arguments: Caller-supplied ``commentThreads_insert`` arguments.
    :return: Request body snippet containing target and comment content.
    :raises CommentThreadsInsertToolError: If body or snippet fields are invalid.
    """
    body = arguments.get("body")
    if not isinstance(body, dict):
        _raise_insert_invalid("commentThreads_insert requires body.", "body")

    body_allowed = set(COMMENT_THREADS_INSERT_INPUT_SCHEMA["properties"]["body"]["properties"])
    for field in body:
        if field not in body_allowed:
            _raise_insert_invalid(f"commentThreads_insert does not support body.{field}.", f"body.{field}")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        _raise_insert_invalid("commentThreads_insert requires body.snippet.", "body.snippet")

    snippet_allowed = set(COMMENT_THREADS_INSERT_INPUT_SCHEMA["properties"]["body"]["properties"]["snippet"]["properties"])
    for field in snippet:
        if field not in snippet_allowed:
            _raise_insert_invalid(
                f"commentThreads_insert does not support body.snippet.{field}.",
                f"body.snippet.{field}",
            )
    return snippet


def _top_level_comment_text(snippet: dict[str, Any]) -> str:
    """Return validated top-level comment text from a snippet.

    :param snippet: Validated ``body.snippet`` mapping.
    :return: Top-level comment text after whitespace validation.
    :raises CommentThreadsInsertToolError: If nested comment fields are invalid.
    """
    top_level_comment = snippet.get("topLevelComment")
    if not isinstance(top_level_comment, dict):
        _raise_insert_invalid(
            "commentThreads_insert requires body.snippet.topLevelComment.",
            "body.snippet.topLevelComment",
        )
    top_level_allowed = COMMENT_THREADS_INSERT_INPUT_SCHEMA["properties"]["body"]["properties"]["snippet"][
        "properties"
    ]["topLevelComment"]["properties"]
    for field in top_level_comment:
        if field not in top_level_allowed:
            _raise_insert_invalid(
                f"commentThreads_insert does not support body.snippet.topLevelComment.{field}.",
                f"body.snippet.topLevelComment.{field}",
            )
    comment_snippet = top_level_comment.get("snippet")
    if not isinstance(comment_snippet, dict):
        _raise_insert_invalid(
            "commentThreads_insert requires body.snippet.topLevelComment.snippet.",
            "body.snippet.topLevelComment.snippet",
        )
    comment_allowed = top_level_allowed["snippet"]["properties"]
    for field in comment_snippet:
        if field not in comment_allowed:
            _raise_insert_invalid(
                f"commentThreads_insert does not support body.snippet.topLevelComment.snippet.{field}.",
                f"body.snippet.topLevelComment.snippet.{field}",
            )
    text = comment_snippet.get("textOriginal")
    if not isinstance(text, str) or not text.strip():
        _raise_insert_invalid(
            "commentThreads_insert requires body.snippet.topLevelComment.snippet.textOriginal.",
            "body.snippet.topLevelComment.snippet.textOriginal",
        )
    return text.strip()


def _validate_comment_threads_insert_parts(arguments: dict[str, Any]) -> list[str]:
    """Validate requested ``commentThreads_insert`` resource parts.

    :param arguments: Caller-supplied ``commentThreads_insert`` arguments.
    :return: Ordered non-empty requested part names.
    :raises CommentThreadsInsertToolError: If ``part`` is missing or unsupported.
    """
    parts = _requested_parts(arguments)
    if not parts:
        _raise_insert_invalid("commentThreads_insert requires part.", "part")
    unsupported = [part for part in parts if part not in COMMENT_THREADS_INSERT_SUPPORTED_PARTS]
    if unsupported:
        _raise_insert_invalid(
            "commentThreads_insert part must be id, snippet, or replies.",
            "part",
            allowed=list(COMMENT_THREADS_INSERT_SUPPORTED_PARTS),
            unsupported=unsupported,
        )
    return parts


def validate_comment_threads_list_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate ``commentThreads_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :return: Selected selector name and safe value.
    :raises CommentThreadsListToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENT_THREADS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_invalid(f"commentThreads_list does not support {field}.", field)

    if not isinstance(arguments.get("part"), str) or not arguments.get("part", "").strip():
        _raise_invalid("commentThreads_list requires part.", "part")

    active = _active_selectors(arguments)
    if len(active) != 1:
        raise CommentThreadsListToolError(
            "commentThreads_list requires exactly one selector: videoId, allThreadsRelatedToChannelId, or id.",
            category="invalid_request",
            details={"field": "selector", "selectors": [name for name, _value in active]},
        )

    selector, value = active[0]
    if not value:
        _raise_invalid(f"commentThreads_list requires a non-empty {selector}.", selector)

    if selector == "id":
        for field in ("maxResults", "moderationStatus", "order", "pageToken", "searchTerms"):
            if field in arguments:
                _raise_invalid(f"commentThreads_list does not support {field} with id.", field, selector="id")

    max_results = arguments.get("maxResults")
    if max_results is not None and (not isinstance(max_results, int) or max_results < 1 or max_results > 100):
        _raise_invalid("maxResults must be between 1 and 100.", "maxResults")

    moderation_status = arguments.get("moderationStatus")
    if moderation_status is not None and moderation_status not in COMMENT_THREADS_LIST_MODERATION_STATUSES:
        _raise_invalid(
            "commentThreads_list moderationStatus must be heldForReview, likelySpam, or published.",
            "moderationStatus",
            allowed=list(COMMENT_THREADS_LIST_MODERATION_STATUSES),
        )

    order = arguments.get("order")
    if order is not None and order not in COMMENT_THREADS_LIST_ORDERS:
        _raise_invalid("commentThreads_list order must be time or relevance.", "order", allowed=list(COMMENT_THREADS_LIST_ORDERS))

    page_token = arguments.get("pageToken")
    if page_token is not None and (not isinstance(page_token, str) or not page_token.strip()):
        _raise_invalid("commentThreads_list requires a non-empty pageToken.", "pageToken")

    search_terms = arguments.get("searchTerms")
    if search_terms is not None and (not isinstance(search_terms, str) or not search_terms.strip()):
        _raise_invalid("commentThreads_list requires non-empty searchTerms.", "searchTerms")

    text_format = arguments.get("textFormat")
    if text_format is not None and text_format not in COMMENT_THREADS_LIST_TEXT_FORMATS:
        _raise_invalid(
            "commentThreads_list textFormat must be html or plainText.",
            "textFormat",
            allowed=list(COMMENT_THREADS_LIST_TEXT_FORMATS),
        )

    return selector, value


def validate_comment_threads_insert_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate ``commentThreads_insert`` arguments and return target context.

    :param arguments: Caller-supplied tool arguments.
    :return: Target channel ID and video ID after whitespace validation.
    :raises CommentThreadsInsertToolError: If arguments are invalid or unsupported.
    """
    allowed = set(COMMENT_THREADS_INSERT_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            _raise_insert_invalid(f"commentThreads_insert does not support {field}.", field)

    if not isinstance(arguments.get("part"), str):
        _raise_insert_invalid("commentThreads_insert requires part.", "part")
    _validate_comment_threads_insert_parts(arguments)

    snippet = _comment_threads_insert_snippet(arguments)
    channel_id = snippet.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        _raise_insert_invalid("commentThreads_insert requires body.snippet.channelId.", "body.snippet.channelId")

    video_id = snippet.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        _raise_insert_invalid("commentThreads_insert requires body.snippet.videoId.", "body.snippet.videoId")

    _top_level_comment_text(snippet)

    delegated_owner = arguments.get("onBehalfOfContentOwner")
    if delegated_owner is not None and (not isinstance(delegated_owner, str) or not delegated_owner.strip()):
        _raise_insert_invalid(
            "commentThreads_insert requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
        )

    return channel_id.strip(), video_id.strip()


def _comment_threads_list_auth_context(*, api_key: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``commentThreads_list``.

    :param api_key: API-key value available for public comment-thread retrieval.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentThreadsListToolError: If API-key credentials are unavailable.
    """
    if not api_key:
        raise CommentThreadsListToolError(
            "commentThreads_list requires public API-key access.",
            category="authentication_failed",
            details={"authMode": "api_key"},
        )
    return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))


def _comment_threads_insert_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``commentThreads_insert``.

    :param oauth_token: OAuth token available for top-level thread creation.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises CommentThreadsInsertToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise CommentThreadsInsertToolError(
            "commentThreads_insert requires OAuth access.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _safe_options_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe optional request context included in successful results.

    :param arguments: Caller-supplied ``commentThreads_list`` arguments.
    :return: Safe optional modifiers without selector identifiers.
    """
    options = {}
    for field in ("maxResults", "moderationStatus", "order", "pageToken", "searchTerms"):
        if field in arguments:
            options[field] = arguments[field]
    return options


def _safe_insert_delegation_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe delegation flags for one comment-thread insert request.

    :param arguments: Caller-supplied ``commentThreads_insert`` arguments.
    :return: Safe delegation flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_comment_threads_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 comment-thread response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw comment-thread collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "commentThreads.list",
        "quotaCost": COMMENT_THREADS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
        "textFormat": arguments.get("textFormat") or "html",
    }
    options = _safe_options_context(arguments)
    if options:
        result["options"] = options
    for field in ("kind", "etag", "nextPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def map_comment_threads_insert_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 comment-thread insert response to the public result shape.

    :param response: Upstream-shaped created comment-thread resource.
    :param arguments: Original validated tool arguments.
    :return: Near-raw created comment-thread result with safe MCP clarity fields.
    """
    channel_id, video_id = validate_comment_threads_insert_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "commentThreads.insert",
        "quotaCost": COMMENT_THREADS_INSERT_QUOTA_COST,
        "created": True,
        "requestedParts": _requested_parts(arguments),
        "item": response,
        "auth": {"mode": "oauth_required"},
        "target": {"channelId": channel_id, "videoId": video_id},
    }
    delegation_context = _safe_insert_delegation_context(arguments)
    if delegation_context:
        result["delegation"] = delegation_context
    for field in ("kind", "etag"):
        if field in response:
            result[field] = response[field]
    return result


def _map_comment_threads_list_upstream_error(error: NormalizedUpstreamError) -> CommentThreadsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``commentThreads_list`` error.
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
        "unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentThreadsListToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def _map_comment_threads_insert_upstream_error(error: NormalizedUpstreamError) -> CommentThreadsInsertToolError:
    """Map a normalized upstream error to the public insert error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``commentThreads_insert`` error.
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
        "unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    details = dict(error.details or {})
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    return CommentThreadsInsertToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details=sanitize_error_details(details),
    )


def build_comment_threads_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-comment-thread-access",
):
    """Build the concrete ``commentThreads_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public comment-thread retrieval.
    :return: Callable dispatcher handler.
    """
    comment_threads_wrapper = wrapper or build_comment_threads_list_wrapper()
    comment_threads_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``commentThreads_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 comment-thread collection result.
        :raises CommentThreadsListToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comment_threads_list_arguments(arguments)
        auth_context = _comment_threads_list_auth_context(api_key=api_key)
        try:
            response = comment_threads_wrapper.call(
                comment_threads_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_comment_threads_list_upstream_error(error) from error
        except ValueError as error:
            raise CommentThreadsListToolError(
                str(error),
                category="invalid_request",
                details={"field": "selector"},
            ) from error
        return map_comment_threads_list_result(response, arguments)

    return handler


def build_comment_threads_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-thread-write",
):
    """Build the concrete ``commentThreads_insert`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for top-level thread creation.
    :return: Callable dispatcher handler.
    """
    comment_threads_wrapper = wrapper or build_comment_threads_insert_wrapper()
    comment_threads_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``commentThreads_insert`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 created comment-thread result.
        :raises CommentThreadsInsertToolError: If validation, authorization, or upstream execution fails.
        """
        validate_comment_threads_insert_arguments(arguments)
        auth_context = _comment_threads_insert_auth_context(oauth_token=oauth_token)
        try:
            response = comment_threads_wrapper.call(
                comment_threads_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_comment_threads_insert_upstream_error(error) from error
        except ValueError as error:
            raise CommentThreadsInsertToolError(
                str(error),
                category="invalid_request",
                details={"field": "body"},
            ) from error
        except Exception as error:
            raise CommentThreadsInsertToolError(
                "commentThreads_insert upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_comment_threads_insert_result(response, arguments)

    return handler


def build_comment_threads_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-comment-thread-access",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``commentThreads_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public comment-thread retrieval.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comment_threads_list_contract()
    return {
        "name": COMMENT_THREADS_LIST_TOOL_NAME,
        "description": COMMENT_THREADS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENT_THREADS_LIST_INPUT_SCHEMA,
        "handler": build_comment_threads_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
    }


def build_comment_threads_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-comment-thread-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``commentThreads_insert`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for top-level thread creation.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_comment_threads_insert_contract()
    return {
        "name": COMMENT_THREADS_INSERT_TOOL_NAME,
        "description": COMMENT_THREADS_INSERT_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": COMMENT_THREADS_INSERT_INPUT_SCHEMA,
        "handler": build_comment_threads_insert_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
    }


__all__ = [
    "COMMENT_THREADS_INSERT_CALLER_EXAMPLES",
    "COMMENT_THREADS_INSERT_CAVEATS",
    "COMMENT_THREADS_INSERT_DESCRIPTION",
    "COMMENT_THREADS_INSERT_INPUT_SCHEMA",
    "COMMENT_THREADS_INSERT_QUOTA_COST",
    "COMMENT_THREADS_INSERT_TOOL_NAME",
    "COMMENT_THREADS_INSERT_USAGE_NOTES",
    "COMMENT_THREADS_LIST_CALLER_EXAMPLES",
    "COMMENT_THREADS_LIST_CAVEATS",
    "COMMENT_THREADS_LIST_DESCRIPTION",
    "COMMENT_THREADS_LIST_INPUT_SCHEMA",
    "COMMENT_THREADS_LIST_MODERATION_STATUSES",
    "COMMENT_THREADS_LIST_ORDERS",
    "COMMENT_THREADS_LIST_QUOTA_COST",
    "COMMENT_THREADS_LIST_SELECTORS",
    "COMMENT_THREADS_LIST_TEXT_FORMATS",
    "COMMENT_THREADS_LIST_TOOL_NAME",
    "COMMENT_THREADS_LIST_USAGE_NOTES",
    "CommentThreadsInsertToolError",
    "CommentThreadsListToolError",
    "build_comment_threads_insert_contract",
    "build_comment_threads_insert_handler",
    "build_comment_threads_insert_tool_descriptor",
    "build_comment_threads_list_contract",
    "build_comment_threads_list_handler",
    "build_comment_threads_list_tool_descriptor",
    "map_comment_threads_insert_result",
    "map_comment_threads_list_result",
    "validate_comment_threads_insert_arguments",
    "validate_comment_threads_list_arguments",
]
