"""Concrete Layer 2 tool support for the YouTube ``comments`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.comments import build_comments_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


COMMENTS_LIST_TOOL_NAME = "comments_list"
COMMENTS_LIST_QUOTA_COST = 1
COMMENTS_LIST_SELECTORS = ("id", "parentId")
COMMENTS_LIST_TEXT_FORMATS = ("html", "plainText")

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


def _default_comments_transport(execution) -> dict[str, Any]:
    """Return a safe comment collection for local default execution.

    :param execution: Layer 1 execution request containing endpoint arguments.
    :return: Upstream-shaped comment list response.
    """
    arguments = execution.arguments
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
    """Build the default Layer 1 executor used by ``comments_list``.

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


def _map_comments_list_upstream_error(error: NormalizedUpstreamError) -> CommentsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``comments_list`` error.
    """
    categories = {
        "invalid_request": "invalid_request",
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


__all__ = [
    "COMMENTS_LIST_CALLER_EXAMPLES",
    "COMMENTS_LIST_CAVEATS",
    "COMMENTS_LIST_DESCRIPTION",
    "COMMENTS_LIST_INPUT_SCHEMA",
    "COMMENTS_LIST_QUOTA_COST",
    "COMMENTS_LIST_SELECTORS",
    "COMMENTS_LIST_TEXT_FORMATS",
    "COMMENTS_LIST_TOOL_NAME",
    "COMMENTS_LIST_USAGE_NOTES",
    "CommentsListToolError",
    "build_comments_list_contract",
    "build_comments_list_handler",
    "build_comments_list_tool_descriptor",
    "map_comments_list_result",
    "validate_comments_list_arguments",
]
