"""Concrete Layer 2 tool support for the YouTube ``playlistItems`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlist_items import build_playlist_items_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLIST_ITEMS_LIST_TOOL_NAME = "playlistItems_list"
PLAYLIST_ITEMS_LIST_QUOTA_COST = 1
PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS = ("contentDetails", "id", "snippet", "status")
PLAYLIST_ITEMS_LIST_SELECTORS = ("playlistId", "id")
PLAYLIST_ITEMS_LIST_MAX_RESULTS = 50

PLAYLIST_ITEMS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS)},
        "playlistId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLIST_ITEMS_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLIST_ITEMS_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLIST_ITEMS_LIST_DESCRIPTION = (
    "List YouTube playlist item resources. Endpoint: playlistItems.list. "
    "Quota cost: 1. Auth: api_key."
)

PLAYLIST_ITEMS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part and exactly one selector: playlistId or id.",
    "Quota cost: 1. Use playlistId for playlist-scoped traversal with optional pageToken and maxResults.",
    "Quota cost: 1. Use id for direct playlist-item lookup; pageToken and maxResults are rejected with id.",
    "Quota cost: 1. Valid empty item collections remain successful list results.",
)

PLAYLIST_ITEMS_LIST_CAVEATS = (
    "This tool only retrieves playlist item resources through playlistItems.list.",
    "playlist item mutation, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, "
    "recommendation, ranking, summarization, enrichment, and cross-endpoint aggregation are out of scope.",
    "Returned playlist item fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES = (
    {
        "name": "playlist_scoped_item_listing",
        "description": "Quota cost: 1. List playlist items for one playlistId with API-key access.",
        "arguments": {"part": "snippet,contentDetails", "playlistId": "PL123"},
        "result": {"endpoint": "playlistItems.list", "selector": "playlistId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_item_lookup",
        "description": "Quota cost: 1. Retrieve playlist items by item id with API-key access.",
        "arguments": {"part": "id,snippet", "id": "playlist-item-123"},
        "result": {"endpoint": "playlistItems.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_item_listing",
        "description": "Quota cost: 1. Continue playlist-scoped traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An accessible empty playlist item collection remains a successful list result.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistItems.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing required playlist-item part selection.",
        "arguments": {"playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside contentDetails, id, snippet, and status.",
        "arguments": {"part": "statistics", "playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_selector",
        "description": "Reject requests missing both playlistId and id selectors.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "conflicting_selector",
        "description": "Reject requests that provide both playlistId and id.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "id": "playlist-item-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "playlist-item-123", "pageToken": "NEXT_PAGE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing, invalid, or insufficient API-key access to safe access errors.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "out_of_scope_playlist_item_workflow",
        "description": "playlist item mutation, video enrichment, analytics, and recommendation requests are out of scope.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "insert": {"videoId": "video-123"}},
        "errorCategory": "invalid_request",
    },
)


class PlaylistItemsListToolError(ValueError):
    """Represent a safe caller-facing ``playlistItems_list`` failure.

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
        """Initialize a sanitized playlist-items list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist-item part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlist_items_parts(part: Any) -> str:
    """Validate and normalize requested playlist-item parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistItemsListToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistItemsListToolError("playlistItems_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistItemsListToolError(
            "playlistItems_list part must use contentDetails, id, snippet, status, or a comma-delimited subset",
            details={"field": "part", "allowed": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def validate_playlist_items_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistItems_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistItemsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistItemsListToolError("playlistItems_list arguments must be an object")

    allowed = {"part", "playlistId", "id", "pageToken", "maxResults"}
    for field in arguments:
        if field not in allowed:
            raise PlaylistItemsListToolError(
                f"unsupported field for playlistItems_list: {field}",
                details={"field": field},
            )

    part = _validate_playlist_items_parts(arguments.get("part"))
    selected = [
        selector
        for selector in PLAYLIST_ITEMS_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise PlaylistItemsListToolError(
            "playlistItems_list requires exactly one selector: playlistId or id",
            details={"field": "selector", "allowed": list(PLAYLIST_ITEMS_LIST_SELECTORS)},
        )

    selector = selected[0]
    normalized: dict[str, Any] = {"part": part, selector: arguments[selector].strip()}
    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistItemsListToolError(
            "pageToken and maxResults are only supported with playlistId",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistItemsListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistItemsListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLIST_ITEMS_LIST_MAX_RESULTS:
            raise PlaylistItemsListToolError(
                f"maxResults must be between 0 and {PLAYLIST_ITEMS_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLIST_ITEMS_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def map_playlist_items_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist-items payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-items list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlist_items_list_arguments(arguments)
    selector = "playlistId" if "playlistId" in normalized else "id"
    result = {
        "endpoint": "playlistItems.list",
        "quotaCost": PLAYLIST_ITEMS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": "api_key"},
        "items": payload.get("items", []),
    }
    paging = {
        field: normalized[field]
        for field in ("pageToken", "maxResults")
        if field in normalized
    }
    if paging:
        result["paging"] = paging
    for field in ("kind", "etag", "nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_playlist_items_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistItemsListToolError:
    """Map a normalized upstream failure to a safe ``playlistItems_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistItemsListToolError(str(error), category=category, details=error.details)


def _playlist_items_list_access_context(api_key: str | None) -> AuthContext:
    """Build the API-key auth context for ``playlistItems_list``.

    :param api_key: API key used for playlist-item retrieval.
    :return: Layer 1 auth context configured for API-key execution.
    :raises PlaylistItemsListToolError: If no API key is available.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise PlaylistItemsListToolError(
            "playlistItems_list requires API-key access",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.API_KEY,
        credentials=CredentialBundle(api_key=api_key.strip()),
    )


def build_playlist_items_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistItems_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "selector",
            "paging",
            "auth",
            "items",
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "playlist_item_insertion",
            "playlist_item_update",
            "playlist_item_deletion",
            "playlist_mutation",
            "playlist_search",
            "video_enrichment",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_ITEMS_LIST_TOOL_NAME,
        upstream_resource="playlistItems",
        upstream_method="list",
        operation_key="playlistItems.list",
        description=PLAYLIST_ITEMS_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=PLAYLIST_ITEMS_LIST_QUOTA_COST,
        resource_family="playlist_items",
        input_contract=PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLIST_ITEMS_LIST_SELECTORS),
            "pagingFields": ["pageToken", "maxResults", "nextPageToken", "prevPageToken", "pageInfo"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "invalid_request",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLIST_ITEMS_LIST_USAGE_NOTES,
        caveats=PLAYLIST_ITEMS_LIST_CAVEATS,
    )


def _default_playlist_items_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-item calls.

    :return: Integration executor returning representative playlist-item data.
    """

    def transport(execution):
        """Return a representative playlist-item list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistItemListResponse",
            "etag": "etag-playlist-items",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "etag-playlist-item",
                    "id": execution.arguments.get("id", "playlist-item-123"),
                    "snippet": {
                        "playlistId": execution.arguments.get("playlistId", "PL123"),
                        "title": "Representative playlist item",
                        "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                    },
                    "contentDetails": {"videoId": "video-123"},
                    "status": {"privacyStatus": "public"},
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlist_items_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``playlistItems_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps playlist-item requests.
    """
    selected_wrapper = wrapper or build_playlist_items_list_wrapper()
    selected_executor = executor or _default_playlist_items_list_executor()
    auth_context = _playlist_items_list_access_context(api_key)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistItems_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-item list result.
        :raises PlaylistItemsListToolError: If validation or execution fails.
        """
        normalized = validate_playlist_items_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_items_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistItemsListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistItems.list"},
            ) from exc
        return map_playlist_items_list_result(payload, normalized)

    return handler


def build_playlist_items_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistItems_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_items_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_ITEMS_LIST_TOOL_NAME,
        "description": PLAYLIST_ITEMS_LIST_DESCRIPTION,
        "inputSchema": PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
        "handler": build_playlist_items_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES",
    "PLAYLIST_ITEMS_LIST_CAVEATS",
    "PLAYLIST_ITEMS_LIST_DESCRIPTION",
    "PLAYLIST_ITEMS_LIST_INPUT_SCHEMA",
    "PLAYLIST_ITEMS_LIST_MAX_RESULTS",
    "PLAYLIST_ITEMS_LIST_QUOTA_COST",
    "PLAYLIST_ITEMS_LIST_SELECTORS",
    "PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS",
    "PLAYLIST_ITEMS_LIST_TOOL_NAME",
    "PLAYLIST_ITEMS_LIST_USAGE_NOTES",
    "PlaylistItemsListToolError",
    "build_playlist_items_list_contract",
    "build_playlist_items_list_handler",
    "build_playlist_items_list_tool_descriptor",
    "map_playlist_items_list_result",
    "validate_playlist_items_list_arguments",
]
