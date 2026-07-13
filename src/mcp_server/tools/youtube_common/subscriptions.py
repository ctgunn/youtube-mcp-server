"""Concrete Layer 2 tool support for the YouTube ``subscriptions`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.subscriptions import build_subscriptions_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


SUBSCRIPTIONS_LIST_TOOL_NAME = "subscriptions_list"
SUBSCRIPTIONS_LIST_QUOTA_COST = 1
SUBSCRIPTIONS_LIST_MAX_RESULTS = 50
SUBSCRIPTIONS_LIST_SUPPORTED_PARTS = ("contentDetails", "id", "snippet", "subscriberSnippet")
SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS = ("channelId", "id")
SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS = ("mine", "myRecentSubscribers", "mySubscribers")
SUBSCRIPTIONS_LIST_SELECTORS = (*SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS, *SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS)
SUBSCRIPTIONS_LIST_ORDER_VALUES = ("alphabetical", "relevance", "unread")
SUBSCRIPTIONS_LIST_COLLECTION_SELECTORS = ("channelId", "mine", "myRecentSubscribers", "mySubscribers")
SUBSCRIPTIONS_LIST_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

SUBSCRIPTIONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "myRecentSubscribers": {"type": "boolean"},
        "mySubscribers": {"type": "boolean"},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": SUBSCRIPTIONS_LIST_MAX_RESULTS},
        "order": {"type": "string", "enum": list(SUBSCRIPTIONS_LIST_ORDER_VALUES)},
    },
    "oneOf": [{"required": [selector]} for selector in SUBSCRIPTIONS_LIST_SELECTORS],
    "additionalProperties": False,
}

SUBSCRIPTIONS_LIST_DESCRIPTION = (
    "List YouTube subscription resources. Endpoint: subscriptions.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)

SUBSCRIPTIONS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId or id for public-compatible subscription lookup with API-key access.",
    "Quota cost: 1. Use mine, myRecentSubscribers, or mySubscribers with eligible OAuth authorization.",
    "Quota cost: 1. Use pageToken and maxResults only to continue a compatible subscription list.",
    "Quota cost: 1. Valid accessible requests that match no subscriptions return a successful empty item collection.",
)

SUBSCRIPTIONS_LIST_CAVEATS = (
    "Exactly one selector is required: channelId, id, mine, myRecentSubscribers, or mySubscribers.",
    "User-context selectors mine, myRecentSubscribers, and mySubscribers require OAuth authorization.",
    "Private subscriber visibility and account state can limit returned subscriber data even for authorized callers.",
    "This tool only retrieves subscription resources through subscriptions.list.",
    "Subscription creation, deletion, partner-only delegation, channel enrichment, subscriber analytics, ranking, "
    "summarization, recommendation, and cross-endpoint aggregation are out of scope.",
    "Returned subscription fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

SUBSCRIPTIONS_LIST_CALLER_EXAMPLES = (
    {
        "name": "channel_subscription_listing",
        "description": "Quota cost: 1. List subscriptions for one channelId with API-key access.",
        "arguments": {"part": "snippet,contentDetails", "channelId": "UC123"},
        "result": {"endpoint": "subscriptions.list", "selector": "channelId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_subscription_lookup",
        "description": "Quota cost: 1. Retrieve subscriptions by subscription id with API-key access.",
        "arguments": {"part": "id,snippet", "id": "subscription-123"},
        "result": {"endpoint": "subscriptions.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "current_user_subscriptions",
        "description": "Quota cost: 1. List the authenticated user's subscriptions with OAuth-backed access.",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "subscriptions.list", "selector": "mine", "authPath": "user_context"},
        "quotaCost": 1,
    },
    {
        "name": "recent_subscribers",
        "description": "Quota cost: 1. List recent subscribers for the authenticated user with OAuth-backed access.",
        "arguments": {"part": "subscriberSnippet", "myRecentSubscribers": True, "maxResults": 25},
        "result": {"endpoint": "subscriptions.list", "selector": "myRecentSubscribers"},
        "quotaCost": 1,
    },
    {
        "name": "subscriber_list",
        "description": "Quota cost: 1. List subscribers for the authenticated user with ordering when supported.",
        "arguments": {"part": "subscriberSnippet", "mySubscribers": True, "order": "relevance"},
        "result": {"endpoint": "subscriptions.list", "selector": "mySubscribers"},
        "quotaCost": 1,
    },
    {
        "name": "paginated_subscription_listing",
        "description": "Quota cost: 1. Continue compatible subscription traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "channelId": "UC123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An accessible empty subscription collection remains a successful list result.",
        "arguments": {"part": "snippet", "channelId": "UC_NO_PUBLIC_SUBSCRIPTIONS"},
        "result": {"endpoint": "subscriptions.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject subscription requests missing required part selection.",
        "arguments": {"channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside supported subscription resource sections.",
        "arguments": {"part": "statistics", "channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_selector",
        "description": "Reject requests missing channelId, id, mine, myRecentSubscribers, and mySubscribers selectors.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "conflicting_selector",
        "description": "Reject requests that combine multiple subscription selectors.",
        "arguments": {"part": "snippet", "channelId": "UC123", "mine": True},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "false_boolean_selector",
        "description": "Reject false-only boolean selectors because no active selector is present.",
        "arguments": {"part": "snippet", "mine": False},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "invalid_pagination",
        "description": "Reject invalid pagination controls before execution.",
        "arguments": {"part": "snippet", "channelId": "UC123", "maxResults": 51},
        "error": {"category": "invalid_request", "field": "maxResults"},
    },
    {
        "name": "unsupported_order",
        "description": "Reject unsupported ordering values before execution.",
        "arguments": {"part": "snippet", "channelId": "UC123", "order": "newest"},
        "error": {"category": "invalid_request", "field": "order"},
    },
    {
        "name": "access_failure",
        "description": "Map missing OAuth for user-context selectors to safe authentication errors.",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "authPath": "user_context"},
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Map quota and upstream subscription list failures to safe categories.",
        "arguments": {"part": "snippet", "channelId": "UC123"},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "not_found_failure",
        "description": "Map missing subscriber or subscription targets to safe not_found errors.",
        "arguments": {"part": "snippet", "id": "missing-subscription"},
        "error": {"category": "not_found"},
    },
    {
        "name": "out_of_scope_enrichment_request",
        "description": "Channel enrichment, subscriber analytics, ranking, summarization, and recommendation are out of scope.",
        "arguments": {"part": "snippet", "channelId": "UC123", "includeChannelStatistics": True},
        "error": {"category": "invalid_request", "field": "includeChannelStatistics"},
    },
)


class SubscriptionsListToolError(ValueError):
    """Represent a safe caller-facing ``subscriptions_list`` failure.

    :param message: Human-readable failure summary.
    :param category: Stable safe failure category.
    :param details: Optional structured details with secret-bearing keys removed.
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "invalid_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a sanitized subscriptions list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_subscriptions_error_details(details or {})


def _sanitize_subscriptions_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove subscription credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in SUBSCRIPTIONS_LIST_UNSAFE_DETAIL_KEYS
    }


def _require_text_field(arguments: dict[str, Any], field: str) -> str:
    """Return a stripped required text field from subscription arguments.

    :param arguments: Candidate tool arguments.
    :param field: Required field name to validate.
    :return: Stripped field value.
    :raises SubscriptionsListToolError: If the field is absent or not non-empty text.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SubscriptionsListToolError(f"subscriptions_list requires {field}", details={"field": field})
    return value.strip()


def _split_parts(part: str) -> list[str]:
    """Split a comma-delimited subscription part string.

    :param part: Caller-provided part selection.
    :return: Stripped part names.
    :raises SubscriptionsListToolError: If any part is unsupported.
    """
    parts = [item.strip() for item in part.split(",") if item.strip()]
    if not parts:
        raise SubscriptionsListToolError("subscriptions_list requires part", details={"field": "part"})
    unsupported = [item for item in parts if item not in SUBSCRIPTIONS_LIST_SUPPORTED_PARTS]
    if unsupported:
        raise SubscriptionsListToolError(
            "unsupported subscription part",
            details={"field": "part", "unsupported": unsupported},
        )
    return parts


def _active_selectors(arguments: dict[str, Any]) -> list[str]:
    """Return active selector fields in one subscription request.

    :param arguments: Normalized or candidate subscription arguments.
    :return: Active selector field names.
    :raises SubscriptionsListToolError: If a selector value has an invalid shape.
    """
    active: list[str] = []
    for field in SUBSCRIPTIONS_LIST_SELECTORS:
        value = arguments.get(field)
        if field in SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS:
            if isinstance(value, str) and value.strip():
                active.append(field)
            elif field in arguments:
                raise SubscriptionsListToolError(f"{field} must be a non-empty string", details={"field": field})
            continue
        if value is True:
            active.append(field)
        elif field in arguments and value not in (False, None):
            raise SubscriptionsListToolError(f"{field} must be a boolean when present", details={"field": field})
    return active


def _selected_selector(arguments: dict[str, Any]) -> str:
    """Return the exactly-one selector selected by normalized arguments.

    :param arguments: Normalized subscription arguments.
    :return: Active selector field.
    :raises SubscriptionsListToolError: If no selector or multiple selectors are active.
    """
    selectors = _active_selectors(arguments)
    if not selectors:
        raise SubscriptionsListToolError(
            "subscriptions_list requires exactly one selector",
            details={"field": "selector", "selectors": list(SUBSCRIPTIONS_LIST_SELECTORS)},
        )
    if len(selectors) > 1:
        raise SubscriptionsListToolError(
            "subscription selectors are mutually exclusive",
            details={"field": "selector", "selectors": selectors},
        )
    return selectors[0]


def validate_subscriptions_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``subscriptions_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises SubscriptionsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise SubscriptionsListToolError("subscriptions_list arguments must be an object")

    allowed = set(SUBSCRIPTIONS_LIST_INPUT_SCHEMA["properties"])
    normalized: dict[str, Any] = {}
    for field, value in arguments.items():
        if field not in allowed:
            raise SubscriptionsListToolError(
                f"unsupported field for subscriptions_list: {field}",
                details={"field": field},
            )
        if isinstance(value, str):
            if not value.strip():
                raise SubscriptionsListToolError(f"{field} must be non-empty when present", details={"field": field})
            normalized[field] = value.strip()
        else:
            normalized[field] = value

    normalized["part"] = _require_text_field(normalized, "part")
    _split_parts(normalized["part"])
    selector = _selected_selector(normalized)

    page_token = normalized.get("pageToken")
    if page_token is not None and (not isinstance(page_token, str) or not page_token.strip()):
        raise SubscriptionsListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})

    max_results = normalized.get("maxResults")
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise SubscriptionsListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > SUBSCRIPTIONS_LIST_MAX_RESULTS:
            raise SubscriptionsListToolError(
                f"maxResults must be between 0 and {SUBSCRIPTIONS_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": SUBSCRIPTIONS_LIST_MAX_RESULTS},
            )

    order = normalized.get("order")
    if order is not None:
        if not isinstance(order, str) or order not in SUBSCRIPTIONS_LIST_ORDER_VALUES:
            raise SubscriptionsListToolError(
                "unsupported subscription order",
                details={"field": "order", "allowed": list(SUBSCRIPTIONS_LIST_ORDER_VALUES)},
            )

    if selector == "id" and any(field in normalized for field in ("pageToken", "maxResults", "order")):
        raise SubscriptionsListToolError(
            "pagination and ordering are not supported for direct subscription id lookup",
            details={"field": "paging", "selector": selector},
        )

    return normalized


def _auth_path(arguments: dict[str, Any]) -> str:
    """Return the public auth path used by normalized subscription arguments.

    :param arguments: Normalized subscription arguments.
    :return: ``user_context`` when OAuth-backed selectors are used, else ``public``.
    """
    return "user_context" if _selected_selector(arguments) in SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS else "public"


def _auth_context_for_subscriptions(
    arguments: dict[str, Any],
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for one subscription list request.

    :param arguments: Normalized subscription arguments.
    :param api_key: API key value available for public-compatible access.
    :param oauth_token: OAuth token available for user-context access.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises SubscriptionsListToolError: If required credentials are unavailable.
    """
    if _auth_path(arguments) == "user_context":
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise SubscriptionsListToolError(
                "user-context subscription listing requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authPath": "user_context", "authMode": "oauth_required"},
            )
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )

    if not isinstance(api_key, str) or not api_key.strip():
        raise SubscriptionsListToolError(
            "public subscription listing requires API-key access",
            category="authentication_failed",
            details={"authPath": "public", "authMode": "api_key"},
        )
    return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))


def _safe_selector_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe selector context for public subscription results.

    :param arguments: Normalized subscription arguments.
    :return: JSON-compatible selector context for caller-facing results.
    """
    selector = _selected_selector(arguments)
    context: dict[str, Any] = {"part": arguments["part"], "selector": selector}
    for field in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers", "pageToken", "maxResults", "order"):
        if field in arguments and arguments[field] not in (None, ""):
            context[field] = arguments[field]
    return context


def _subscriptions_pagination(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Return request and response pagination context for subscription results.

    :param payload: Upstream or Layer 1 payload.
    :param arguments: Normalized subscription arguments.
    :return: Safe pagination context, or an empty mapping.
    """
    pagination: dict[str, Any] = {}
    for field in ("pageToken", "maxResults", "order"):
        if field in arguments:
            pagination[field] = arguments[field]
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            pagination[field] = payload[field]
    return pagination


def map_subscriptions_list_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    auth_mode: str | None = None,
) -> dict[str, Any]:
    """Map an upstream subscription payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 subscription list payload.
    :param arguments: Validated caller arguments used for the request.
    :param auth_mode: Safe auth mode selected for execution.
    :return: Near-raw subscription list result with safe operation context.
    """
    normalized = validate_subscriptions_list_arguments(arguments)
    items = payload.get("items", [])
    path = _auth_path(normalized)
    selected_auth_mode = auth_mode or ("oauth_required" if path == "user_context" else "api_key")
    result: dict[str, Any] = {
        "endpoint": "subscriptions.list",
        "quotaCost": SUBSCRIPTIONS_LIST_QUOTA_COST,
        "items": items,
        "empty": not bool(items),
        "selectorContext": payload.get("selectorContext") or _safe_selector_context(normalized),
        "auth": {"mode": selected_auth_mode, "path": path},
    }
    pagination = _subscriptions_pagination(payload, normalized)
    if pagination:
        result["pagination"] = pagination
    for field in ("kind", "etag", "nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_subscriptions_list_upstream_error(error: NormalizedUpstreamError) -> SubscriptionsListToolError:
    """Map a normalized upstream failure to a safe ``subscriptions_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "subscriptionForbidden": "authorization_failed",
        "accountClosed": "authorization_failed",
        "accountSuspended": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "not_found",
        "subscriberNotFound": "not_found",
        "resource_not_found": "not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return SubscriptionsListToolError(str(error), category=category, details=error.details or {})


def build_subscriptions_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``subscriptions_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "items",
            "empty",
            "selectorContext",
            "pagination",
            "auth",
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "subscription_creation",
            "subscription_deletion",
            "partner_delegation",
            "channel_enrichment",
            "subscriber_analytics",
            "ranking",
            "summarization",
            "recommendation",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=SUBSCRIPTIONS_LIST_TOOL_NAME,
        upstream_resource="subscriptions",
        upstream_method="list",
        operation_key="subscriptions.list",
        description=SUBSCRIPTIONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=SUBSCRIPTIONS_LIST_QUOTA_COST,
        resource_family="subscriptions",
        input_contract=SUBSCRIPTIONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requiredFields": ["part"],
            "selectorFields": list(SUBSCRIPTIONS_LIST_SELECTORS),
            "publicSelectors": list(SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS),
            "userContextSelectors": list(SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS),
            "supportedParts": list(SUBSCRIPTIONS_LIST_SUPPORTED_PARTS),
            "orderValues": list(SUBSCRIPTIONS_LIST_ORDER_VALUES),
            "pagingFields": ["pageToken", "maxResults", "nextPageToken", "prevPageToken", "pageInfo"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "invalid_request",
            "not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=SUBSCRIPTIONS_LIST_USAGE_NOTES,
        caveats=SUBSCRIPTIONS_LIST_CAVEATS,
    )


def _default_subscriptions_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default subscription calls.

    :return: Integration executor returning representative subscription data.
    """

    def transport(execution):
        """Return a representative subscription list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        if execution.arguments.get("channelId") == "UC_NO_PUBLIC_SUBSCRIPTIONS":
            return {
                "kind": "youtube#subscriptionListResponse",
                "etag": "etag-subscriptions-empty",
                "items": [],
                "pageInfo": {"totalResults": 0, "resultsPerPage": 0},
            }
        selector = _selected_selector(execution.arguments)
        return {
            "kind": "youtube#subscriptionListResponse",
            "etag": "etag-subscriptions",
            "nextPageToken": "NEXT_PAGE",
            "items": [
                {
                    "kind": "youtube#subscription",
                    "etag": "etag-subscription",
                    "id": execution.arguments.get("id", "subscription-123"),
                    "snippet": {
                        "title": "Representative subscription",
                        "channelId": execution.arguments.get("channelId", "UC123"),
                    },
                    "contentDetails": {"totalItemCount": 42},
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
            "selectorContext": {"selector": selector, "part": execution.arguments.get("part", "snippet")},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_subscriptions_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``subscriptions_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used for public-compatible access.
    :param oauth_token: OAuth token value used for user-context access.
    :return: Callable that validates, executes, and maps subscription requests.
    """
    selected_wrapper = wrapper or build_subscriptions_list_wrapper()
    selected_executor = executor or _default_subscriptions_list_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``subscriptions_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 subscriptions list result.
        :raises SubscriptionsListToolError: If validation or execution fails.
        """
        normalized = validate_subscriptions_list_arguments(arguments)
        auth_context = _auth_context_for_subscriptions(normalized, api_key=api_key, oauth_token=oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_subscriptions_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise SubscriptionsListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "subscriptions.list", "authPath": _auth_path(normalized)},
            ) from exc
        return map_subscriptions_list_result(payload, normalized, auth_mode=auth_context.mode.value)

    return handler


def build_subscriptions_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``subscriptions_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_subscriptions_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(SUBSCRIPTIONS_LIST_CALLER_EXAMPLES)
    return {
        "name": SUBSCRIPTIONS_LIST_TOOL_NAME,
        "description": SUBSCRIPTIONS_LIST_DESCRIPTION,
        "inputSchema": SUBSCRIPTIONS_LIST_INPUT_SCHEMA,
        "handler": build_subscriptions_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


__all__ = [
    "SUBSCRIPTIONS_LIST_CALLER_EXAMPLES",
    "SUBSCRIPTIONS_LIST_CAVEATS",
    "SUBSCRIPTIONS_LIST_COLLECTION_SELECTORS",
    "SUBSCRIPTIONS_LIST_DESCRIPTION",
    "SUBSCRIPTIONS_LIST_INPUT_SCHEMA",
    "SUBSCRIPTIONS_LIST_MAX_RESULTS",
    "SUBSCRIPTIONS_LIST_ORDER_VALUES",
    "SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS",
    "SUBSCRIPTIONS_LIST_QUOTA_COST",
    "SUBSCRIPTIONS_LIST_SELECTORS",
    "SUBSCRIPTIONS_LIST_SUPPORTED_PARTS",
    "SUBSCRIPTIONS_LIST_TOOL_NAME",
    "SUBSCRIPTIONS_LIST_USAGE_NOTES",
    "SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS",
    "SubscriptionsListToolError",
    "build_subscriptions_list_contract",
    "build_subscriptions_list_handler",
    "build_subscriptions_list_tool_descriptor",
    "map_subscriptions_list_result",
    "validate_subscriptions_list_arguments",
]
