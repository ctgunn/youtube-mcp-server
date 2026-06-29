"""Concrete Layer 2 tool support for the YouTube ``commentThreads`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.comment_threads import build_comment_threads_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


COMMENT_THREADS_LIST_TOOL_NAME = "commentThreads_list"
COMMENT_THREADS_LIST_QUOTA_COST = 1
COMMENT_THREADS_LIST_SELECTORS = ("videoId", "allThreadsRelatedToChannelId", "id")
COMMENT_THREADS_LIST_TEXT_FORMATS = ("html", "plainText")
COMMENT_THREADS_LIST_MODERATION_STATUSES = ("heldForReview", "likelySpam", "published")
COMMENT_THREADS_LIST_ORDERS = ("time", "relevance")

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


def _default_comment_threads_transport(execution) -> dict[str, Any]:
    """Return a safe comment-thread response for local default execution.

    :param execution: Layer 1 execution request containing endpoint arguments.
    :return: Upstream-shaped comment-thread response.
    :raises NormalizedUpstreamError: If a representative upstream failure is requested.
    """
    arguments = execution.arguments
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


__all__ = [
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
    "CommentThreadsListToolError",
    "build_comment_threads_list_contract",
    "build_comment_threads_list_handler",
    "build_comment_threads_list_tool_descriptor",
    "map_comment_threads_list_result",
    "validate_comment_threads_list_arguments",
]
