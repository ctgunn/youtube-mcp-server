"""Concrete Layer 2 tool support for the YouTube ``subscriptions`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.subscriptions import (
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
)
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

SUBSCRIPTIONS_INSERT_TOOL_NAME = "subscriptions_insert"
SUBSCRIPTIONS_INSERT_QUOTA_COST = 50
SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS = ("snippet",)
SUBSCRIPTIONS_INSERT_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

SUBSCRIPTIONS_DELETE_TOOL_NAME = "subscriptions_delete"
SUBSCRIPTIONS_DELETE_QUOTA_COST = 50
SUBSCRIPTIONS_DELETE_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

SUBSCRIPTIONS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["resourceId"],
                    "properties": {
                        "resourceId": {
                            "type": "object",
                            "required": ["channelId"],
                            "properties": {
                                "kind": {"type": "string", "enum": ["youtube#channel"]},
                                "channelId": {"type": "string", "minLength": 1},
                            },
                            "additionalProperties": False,
                        }
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

SUBSCRIPTIONS_DELETE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

SUBSCRIPTIONS_INSERT_DESCRIPTION = (
    "Create a YouTube subscription. Endpoint: subscriptions.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires body.snippet.resourceId.channelId."
)

SUBSCRIPTIONS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part=snippet and body.snippet.resourceId.channelId.",
    "Quota cost: 50. Successful calls create subscription relationships for the authorized account.",
    "Quota cost: 50. body.snippet.resourceId.kind may be omitted or set to youtube#channel.",
    "Quota cost: 50. Duplicate or ineligible targets can be rejected by the upstream service.",
)

SUBSCRIPTIONS_INSERT_CAVEATS = (
    "subscriptions_insert creates one subscription relationship through subscriptions.insert and requires OAuth authorization.",
    "Use subscriptions_list for retrieval and subscriptions_delete for deletion; this tool only performs subscriptions.insert.",
    "body.snippet.resourceId.channelId is required for supported subscription creation requests.",
    "Unsupported write fields such as body.title, body.status, extra body.snippet mappings, or extra resourceId fields are out of scope.",
    "Channel search, recommendation, notification management, subscriber analytics, ranking, summarization, enrichment, idempotency, "
    "duplicate prevention, and cross-endpoint behavior are out of scope.",
    "Returned subscription fields depend on selected parts and upstream availability; missing optional fields are not fabricated.",
)

SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "oauth_subscription_creation",
        "description": "Quota cost: 50. Create a subscription relationship with OAuth authorization.",
        "arguments": {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        "result": {"endpoint": "subscriptions.insert", "quotaCost": 50, "created": True},
        "quotaCost": 50,
    },
    {
        "name": "oauth_subscription_creation_with_kind",
        "description": "Quota cost: 50. Create a subscription with explicit youtube#channel resource kind.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"kind": "youtube#channel", "channelId": "UC123"}}},
        },
        "result": {"endpoint": "subscriptions.insert", "targetResourceKind": "youtube#channel"},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject subscription creation requests missing required part selection.",
        "arguments": {"body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 50. Reject writable parts outside the supported snippet create path.",
        "arguments": {"part": "contentDetails", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_body",
        "description": "Quota cost: 50. Reject subscription creation requests missing a writable body.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "body"},
    },
    {
        "name": "missing_target_channel",
        "description": "Quota cost: 50. Reject creation requests missing body.snippet.resourceId.channelId.",
        "arguments": {"part": "snippet", "body": {"snippet": {"resourceId": {}}}},
        "error": {"category": "invalid_request", "field": "body.snippet.resourceId.channelId"},
    },
    {
        "name": "invalid_resource_kind",
        "description": "Quota cost: 50. Reject target resources that are not youtube#channel.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"kind": "youtube#playlist", "channelId": "UC123"}}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.resourceId.kind"},
    },
    {
        "name": "unsupported_write_field",
        "description": "Quota cost: 50. Reject optional write fields not supported by this slice.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"channelId": "UC123"}, "title": "Unsupported"}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.title"},
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
        "arguments": {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
    },
    {
        "name": "duplicate_or_ineligible_target",
        "description": "Quota cost: 50. Map duplicate, self-subscription, blocked, or ineligible targets safely.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"channelId": "UC_ALREADY_SUBSCRIBED"}}},
        },
        "error": {"category": "duplicate_target"},
    },
    {
        "name": "quota_or_upstream_create_failure",
        "description": "Quota cost: 50. Map quota and upstream create failures to safe categories.",
        "arguments": {"part": "snippet", "body": {"snippet": {"resourceId": {"channelId": "UC123"}}}},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "out_of_scope_subscription_management_request",
        "description": "Quota cost: 50. Listing, deletion, notification management, analytics, and enrichment are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
            "deleteExistingSubscription": True,
        },
        "error": {"category": "invalid_request", "field": "deleteExistingSubscription"},
    },
)

SUBSCRIPTIONS_DELETE_DESCRIPTION = (
    "Delete a YouTube subscription. Endpoint: subscriptions.delete. "
    "Quota cost: 50. Auth: oauth_required. Requires one subscription relationship id and returns a deletion "
    "acknowledgment."
)

SUBSCRIPTIONS_DELETE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide one id for the subscription relationship being deleted.",
    "Quota cost: 50. subscriptions.delete accepts query-only inputs and no request body.",
    "Quota cost: 50. Successful deletion returns an acknowledgment without a deleted subscription resource.",
    "Quota cost: 50. Already-removed, missing, or non-removable targets can be rejected by the upstream service.",
)

SUBSCRIPTIONS_DELETE_CAVEATS = (
    "subscriptions_delete is a destructive operation and requires eligible OAuth authorization.",
    "The request accepts exactly one target subscription relationship id; listing, lookup, bulk deletion, and discovery "
    "belong outside this tool boundary.",
    "Missing, already-removed, inaccessible, not-owned, blocked, or otherwise non-removable subscription relationships "
    "are surfaced as safe validation, authorization, missing-target, or non-removable-target failures.",
    "The tool does not perform subscription listing, creation, channel search, notification management, subscriber "
    "analytics, ranking, summarization, enrichment, preflight lookup, idempotency, bulk deletion, or cross-endpoint "
    "aggregation.",
)

SUBSCRIPTIONS_DELETE_CALLER_EXAMPLES = (
    {
        "name": "oauth_subscription_deletion",
        "description": "Quota cost: 50. Delete one subscription relationship with OAuth authorization.",
        "arguments": {"id": "subscription-123"},
        "result": {
            "endpoint": "subscriptions.delete",
            "quotaCost": 50,
            "deleted": True,
            "deletion": {"id": "subscription-123"},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_id",
        "description": "Quota cost: 50. Reject deletion requests missing the required subscription id.",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "id"},
        "quotaCost": 50,
    },
    {
        "name": "empty_id",
        "description": "Quota cost: 50. Reject deletion requests with an empty subscription id.",
        "arguments": {"id": ""},
        "error": {"category": "invalid_request", "field": "id"},
        "quotaCost": 50,
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
        "arguments": {"id": "subscription-123"},
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
        "quotaCost": 50,
    },
    {
        "name": "already_removed_or_missing_target",
        "description": "Quota cost: 50. Map missing or already-removed subscriptions to safe target-state errors.",
        "arguments": {"id": "subscription-missing"},
        "error": {"category": "not_found"},
        "quotaCost": 50,
    },
    {
        "name": "non_removable_target",
        "description": "Quota cost: 50. Map ownership, policy, blocked, or account-state deletion failures safely.",
        "arguments": {"id": "subscription-blocked"},
        "error": {"category": "non_removable_target"},
        "quotaCost": 50,
    },
    {
        "name": "quota_or_upstream_delete_failure",
        "description": "Quota cost: 50. Map quota and upstream delete failures to safe categories.",
        "arguments": {"id": "subscription-123"},
        "error": {"category": "quota_exhausted"},
        "quotaCost": 50,
    },
    {
        "name": "out_of_scope_subscription_management_request",
        "description": "Quota cost: 50. Listing, creation, notification management, analytics, and enrichment are out of scope.",
        "arguments": {"id": "subscription-123", "includeChannelStatistics": True},
        "error": {"category": "invalid_request", "field": "includeChannelStatistics"},
        "quotaCost": 50,
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


class SubscriptionsInsertToolError(ValueError):
    """Represent a safe caller-facing ``subscriptions_insert`` failure.

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
        """Initialize a sanitized subscriptions insert tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_subscriptions_error_details(details or {})


class SubscriptionsDeleteToolError(ValueError):
    """Represent a safe caller-facing ``subscriptions_delete`` failure.

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
        """Initialize a sanitized subscriptions delete tool error.

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
        if key.lower()
        not in (
            SUBSCRIPTIONS_LIST_UNSAFE_DETAIL_KEYS
            | SUBSCRIPTIONS_INSERT_UNSAFE_DETAIL_KEYS
            | SUBSCRIPTIONS_DELETE_UNSAFE_DETAIL_KEYS
        )
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


def _validate_subscriptions_insert_part(part: Any) -> str:
    """Validate the writable part selection for subscription creation.

    :param part: Candidate part selection value.
    :return: Normalized part selection.
    :raises SubscriptionsInsertToolError: If the part is missing or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise SubscriptionsInsertToolError("subscriptions_insert requires part", details={"field": "part"})
    parts = [item.strip() for item in part.strip().split(",") if item.strip()]
    if (
        not parts
        or len(parts) != 1
        or len(set(parts)) != len(parts)
        or any(item not in SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS for item in parts)
    ):
        raise SubscriptionsInsertToolError(
            "subscriptions_insert part must use the supported snippet create path",
            details={"field": "part", "allowed": list(SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS)},
        )
    return parts[0]


def validate_subscriptions_insert_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``subscriptions_insert`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises SubscriptionsInsertToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise SubscriptionsInsertToolError("subscriptions_insert arguments must be an object")

    allowed = set(SUBSCRIPTIONS_INSERT_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise SubscriptionsInsertToolError(
                f"unsupported field for subscriptions_insert: {field}",
                details={"field": field},
            )

    part = _validate_subscriptions_insert_part(arguments.get("part"))
    body = arguments.get("body")
    if not isinstance(body, dict):
        raise SubscriptionsInsertToolError("subscriptions_insert requires body", details={"field": "body"})
    unsupported_body = [field for field in body if field != "snippet"]
    if unsupported_body:
        raise SubscriptionsInsertToolError(
            f"unsupported body field for subscriptions_insert: {unsupported_body[0]}",
            details={"field": f"body.{unsupported_body[0]}"},
        )
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise SubscriptionsInsertToolError(
            "subscriptions_insert requires body.snippet",
            details={"field": "body.snippet"},
        )
    unsupported_snippet = [field for field in snippet if field != "resourceId"]
    if unsupported_snippet:
        raise SubscriptionsInsertToolError(
            f"unsupported snippet field for subscriptions_insert: {unsupported_snippet[0]}",
            details={"field": f"body.snippet.{unsupported_snippet[0]}"},
        )
    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise SubscriptionsInsertToolError(
            "subscriptions_insert requires body.snippet.resourceId",
            details={"field": "body.snippet.resourceId"},
        )
    unsupported_resource_id = [field for field in resource_id if field not in {"kind", "channelId"}]
    if unsupported_resource_id:
        raise SubscriptionsInsertToolError(
            f"unsupported resourceId field for subscriptions_insert: {unsupported_resource_id[0]}",
            details={"field": f"body.snippet.resourceId.{unsupported_resource_id[0]}"},
        )
    kind = resource_id.get("kind")
    if kind not in (None, "", "youtube#channel"):
        raise SubscriptionsInsertToolError(
            "body.snippet.resourceId.kind must be youtube#channel when provided",
            details={"field": "body.snippet.resourceId.kind"},
        )
    channel_id = resource_id.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise SubscriptionsInsertToolError(
            "subscriptions_insert requires body.snippet.resourceId.channelId",
            details={"field": "body.snippet.resourceId.channelId"},
        )

    normalized_resource_id: dict[str, str] = {"channelId": channel_id.strip()}
    if isinstance(kind, str) and kind.strip():
        normalized_resource_id["kind"] = kind.strip()
    return {
        "part": part,
        "body": {"snippet": {"resourceId": normalized_resource_id}},
    }


def validate_subscriptions_delete_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``subscriptions_delete`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises SubscriptionsDeleteToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise SubscriptionsDeleteToolError("subscriptions_delete arguments must be an object")

    allowed = set(SUBSCRIPTIONS_DELETE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise SubscriptionsDeleteToolError(
                f"unsupported field for subscriptions_delete: {field}",
                details={"field": field},
            )

    subscription_id = arguments.get("id")
    if not isinstance(subscription_id, str) or not subscription_id.strip():
        raise SubscriptionsDeleteToolError("subscriptions_delete requires id", details={"field": "id"})
    return {"id": subscription_id.strip()}


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


def _subscriptions_insert_creation_context(arguments: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Return safe subscription creation context for an insert request.

    :param arguments: Validated ``subscriptions_insert`` arguments.
    :param payload: Upstream or Layer 1 subscription insert payload.
    :return: Safe creation context with target channel and writable fields.
    """
    request_resource_id = arguments["body"]["snippet"]["resourceId"]
    target_channel_id = payload.get("targetChannelId") or request_resource_id["channelId"]
    target_resource_kind = payload.get("targetResourceKind") or request_resource_id.get("kind") or "youtube#channel"
    return {
        "writableFields": ["body.snippet.resourceId.channelId"],
        "targetChannelId": target_channel_id,
        "targetResourceKind": target_resource_kind,
    }


def map_subscriptions_insert_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream subscription creation payload to the public result.

    :param payload: Upstream or Layer 1 subscriptions insert payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw created-resource result with safe operation context.
    """
    normalized = validate_subscriptions_insert_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "subscriptions.insert",
        "quotaCost": SUBSCRIPTIONS_INSERT_QUOTA_COST,
        "created": True,
        "requestedParts": _split_parts(normalized["part"]),
        "creation": _subscriptions_insert_creation_context(normalized, payload),
        "auth": {"mode": "oauth_required"},
        "subscription": payload,
    }
    for field in ("kind", "etag", "subscriptionId", "targetChannelId", "targetResourceKind"):
        if field in payload:
            result[field] = payload[field]
    return result


def map_subscriptions_delete_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream subscription deletion payload to the public result.

    :param payload: Upstream or Layer 1 subscriptions delete acknowledgment payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw deletion acknowledgment with safe operation context.
    """
    normalized = validate_subscriptions_delete_arguments(arguments)
    safe_upstream = _sanitize_subscriptions_error_details(dict(payload or {}))
    return {
        "endpoint": "subscriptions.delete",
        "quotaCost": SUBSCRIPTIONS_DELETE_QUOTA_COST,
        "deleted": True,
        "deletion": {"id": normalized["id"]},
        "auth": {"mode": "oauth_required"},
        "upstream": safe_upstream,
    }


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


def _map_subscriptions_insert_upstream_error(error: NormalizedUpstreamError) -> SubscriptionsInsertToolError:
    """Map a normalized upstream failure to a safe ``subscriptions_insert`` error.

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
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "duplicate": "duplicate_target",
        "conflict": "duplicate_target",
        "duplicate_or_ineligible_target": "duplicate_target",
        "ineligible_target": "ineligible_target",
        "not_found": "not_found",
        "resource_not_found": "not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return SubscriptionsInsertToolError(str(error), category=category, details=error.details or {})


def _map_subscriptions_delete_upstream_error(error: NormalizedUpstreamError) -> SubscriptionsDeleteToolError:
    """Map a normalized upstream failure to a safe ``subscriptions_delete`` error.

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
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "not_found",
        "resource_not_found": "not_found",
        "already_removed": "not_found",
        "already_deleted": "not_found",
        "missing_target": "not_found",
        "non_removable_target": "non_removable_target",
        "blocked_target": "non_removable_target",
        "not_owned": "non_removable_target",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return SubscriptionsDeleteToolError(str(error), category=category, details=error.details or {})


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


def build_subscriptions_insert_contract() -> YouTubeToolContract:
    """Build the public contract for ``subscriptions_insert``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "created",
            "requestedParts",
            "creation",
            "auth",
            "subscription",
            "kind",
            "etag",
            "subscriptionId",
            "targetChannelId",
            "targetResourceKind",
        ),
        preserved_upstream_fields=(
            "kind",
            "etag",
            "id",
            "snippet",
            "subscriptionId",
            "targetChannelId",
            "targetResourceKind",
        ),
        disallowed_behavior=(
            "subscription_listing",
            "subscription_deletion",
            "channel_search",
            "recommendation",
            "notification_management",
            "subscriber_analytics",
            "ranking",
            "summarization",
            "enrichment",
            "idempotency",
            "duplicate_prevention",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=SUBSCRIPTIONS_INSERT_TOOL_NAME,
        upstream_resource="subscriptions",
        upstream_method="insert",
        operation_key="subscriptions.insert",
        description=SUBSCRIPTIONS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=SUBSCRIPTIONS_INSERT_QUOTA_COST,
        resource_family="subscriptions",
        input_contract=SUBSCRIPTIONS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "subscription",
            "requestedParts": list(SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS),
            "supportedWritableParts": ["snippet"],
            "writableFields": ["body.snippet.resourceId.channelId"],
            "targetField": "body.snippet.resourceId.channelId",
            "targetResourceKind": "youtube#channel",
            "duplicateCreatePolicy": "not_idempotent",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "duplicate_target",
            "ineligible_target",
            "not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=SUBSCRIPTIONS_INSERT_USAGE_NOTES,
        caveats=SUBSCRIPTIONS_INSERT_CAVEATS,
    )


def build_subscriptions_delete_contract() -> YouTubeToolContract:
    """Build the public contract for ``subscriptions_delete``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "deleted",
            "deletion",
            "auth",
            "upstream",
        ),
        preserved_upstream_fields=("operationStatus", "etag"),
        disallowed_behavior=(
            "subscription_listing",
            "subscription_creation",
            "subscription_lookup",
            "channel_search",
            "recommendation",
            "notification_management",
            "subscriber_analytics",
            "ranking",
            "summarization",
            "enrichment",
            "idempotency",
            "preflight_lookup",
            "bulk_deletion",
            "cross_endpoint_aggregation",
            "resource_fabrication",
        ),
    )
    return YouTubeToolContract(
        tool_name=SUBSCRIPTIONS_DELETE_TOOL_NAME,
        upstream_resource="subscriptions",
        upstream_method="delete",
        operation_key="subscriptions.delete",
        description=SUBSCRIPTIONS_DELETE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=SUBSCRIPTIONS_DELETE_QUOTA_COST,
        resource_family="subscriptions",
        input_contract=SUBSCRIPTIONS_DELETE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "deletion_acknowledgment",
            "successStatus": 204,
            "bodyPolicy": "no_upstream_body",
            "idField": "id",
            "targetFields": ["id"],
            "acknowledgmentFields": ["deleted"],
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "not_found",
            "non_removable_target",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=SUBSCRIPTIONS_DELETE_USAGE_NOTES,
        caveats=SUBSCRIPTIONS_DELETE_CAVEATS,
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


def _default_subscriptions_insert_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default subscription inserts.

    :return: Integration executor returning representative created subscription data.
    """

    def transport(execution):
        """Return a representative created subscription response.

        :param execution: Request execution context.
        :return: Fake upstream created-resource response for local invocation.
        """
        resource_id = execution.arguments.get("body", {}).get("snippet", {}).get("resourceId", {})
        channel_id = resource_id.get("channelId", "UC123")
        kind = resource_id.get("kind", "youtube#channel")
        return {
            "kind": "youtube#subscription",
            "etag": "etag-created-subscription",
            "id": "subscription-123",
            "snippet": {
                "resourceId": {
                    "kind": kind,
                    "channelId": channel_id,
                }
            },
            "subscriptionId": "subscription-123",
            "targetChannelId": channel_id,
            "targetResourceKind": kind,
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_subscriptions_delete_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default subscription deletes.

    :return: Integration executor returning representative deletion acknowledgment data.
    """

    def transport(execution):
        """Return a representative subscription deletion acknowledgment.

        :param execution: Request execution context.
        :return: Fake upstream deletion acknowledgment for local invocation.
        """
        return {"operationStatus": "deleted", "id": execution.arguments.get("id")}

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


def build_subscriptions_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``subscriptions_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for subscription creation.
    :return: Callable that validates, executes, and maps subscription insert requests.
    """
    selected_wrapper = wrapper or build_subscriptions_insert_wrapper()
    selected_executor = executor or _default_subscriptions_insert_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``subscriptions_insert`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 subscriptions insert result.
        :raises SubscriptionsInsertToolError: If validation or execution fails.
        """
        normalized = validate_subscriptions_insert_arguments(arguments)
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise SubscriptionsInsertToolError(
                "subscriptions_insert requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authMode": "oauth_required"},
            )
        auth_context = AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_subscriptions_insert_upstream_error(exc) from exc
        except ValueError as exc:
            raise SubscriptionsInsertToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "subscriptions.insert"},
            ) from exc
        return map_subscriptions_insert_result(payload, normalized)

    return handler


def build_subscriptions_delete_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``subscriptions_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for subscription deletion.
    :return: Callable that validates, executes, and maps subscription delete requests.
    """
    selected_wrapper = wrapper or build_subscriptions_delete_wrapper()
    selected_executor = executor or _default_subscriptions_delete_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``subscriptions_delete`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 subscriptions delete result.
        :raises SubscriptionsDeleteToolError: If validation or execution fails.
        """
        normalized = validate_subscriptions_delete_arguments(arguments)
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise SubscriptionsDeleteToolError(
                "subscriptions_delete requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authMode": "oauth_required"},
            )
        auth_context = AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_subscriptions_delete_upstream_error(exc) from exc
        except ValueError as exc:
            raise SubscriptionsDeleteToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "subscriptions.delete"},
            ) from exc
        return map_subscriptions_delete_result(payload, normalized)

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


def build_subscriptions_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``subscriptions_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_subscriptions_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES)
    return {
        "name": SUBSCRIPTIONS_INSERT_TOOL_NAME,
        "description": SUBSCRIPTIONS_INSERT_DESCRIPTION,
        "inputSchema": SUBSCRIPTIONS_INSERT_INPUT_SCHEMA,
        "handler": build_subscriptions_insert_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


def build_subscriptions_delete_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``subscriptions_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_subscriptions_delete_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(SUBSCRIPTIONS_DELETE_CALLER_EXAMPLES)
    return {
        "name": SUBSCRIPTIONS_DELETE_TOOL_NAME,
        "description": SUBSCRIPTIONS_DELETE_DESCRIPTION,
        "inputSchema": SUBSCRIPTIONS_DELETE_INPUT_SCHEMA,
        "handler": build_subscriptions_delete_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


__all__ = [
    "SUBSCRIPTIONS_DELETE_CALLER_EXAMPLES",
    "SUBSCRIPTIONS_DELETE_CAVEATS",
    "SUBSCRIPTIONS_DELETE_DESCRIPTION",
    "SUBSCRIPTIONS_DELETE_INPUT_SCHEMA",
    "SUBSCRIPTIONS_DELETE_QUOTA_COST",
    "SUBSCRIPTIONS_DELETE_TOOL_NAME",
    "SUBSCRIPTIONS_DELETE_USAGE_NOTES",
    "SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES",
    "SUBSCRIPTIONS_INSERT_CAVEATS",
    "SUBSCRIPTIONS_INSERT_DESCRIPTION",
    "SUBSCRIPTIONS_INSERT_INPUT_SCHEMA",
    "SUBSCRIPTIONS_INSERT_QUOTA_COST",
    "SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS",
    "SUBSCRIPTIONS_INSERT_TOOL_NAME",
    "SUBSCRIPTIONS_INSERT_USAGE_NOTES",
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
    "SubscriptionsDeleteToolError",
    "SubscriptionsInsertToolError",
    "SubscriptionsListToolError",
    "build_subscriptions_delete_contract",
    "build_subscriptions_delete_handler",
    "build_subscriptions_delete_tool_descriptor",
    "build_subscriptions_insert_contract",
    "build_subscriptions_insert_handler",
    "build_subscriptions_insert_tool_descriptor",
    "build_subscriptions_list_contract",
    "build_subscriptions_list_handler",
    "build_subscriptions_list_tool_descriptor",
    "map_subscriptions_delete_result",
    "map_subscriptions_insert_result",
    "map_subscriptions_list_result",
    "validate_subscriptions_delete_arguments",
    "validate_subscriptions_insert_arguments",
    "validate_subscriptions_list_arguments",
]
