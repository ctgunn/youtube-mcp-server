"""Concrete Layer 2 tool support for the YouTube ``playlists`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlists import build_playlists_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLISTS_LIST_TOOL_NAME = "playlists_list"
PLAYLISTS_LIST_QUOTA_COST = 1
PLAYLISTS_LIST_SELECTORS = ("channelId", "id", "mine")
PLAYLISTS_LIST_SUPPORTED_PARTS = ("contentDetails", "id", "localizations", "player", "snippet", "status")
PLAYLISTS_LIST_MAX_RESULTS = 50
PLAYLISTS_LIST_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

PLAYLISTS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLISTS_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLISTS_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLISTS_LIST_DESCRIPTION = (
    "List YouTube playlist resources. Endpoint: playlists.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)

PLAYLISTS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId or id for public playlist lookup with API-key access.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for owner-scoped playlist retrieval.",
    "Quota cost: 1. Use pageToken and maxResults only with collection-style channelId or mine requests.",
    "Quota cost: 1. Valid accessible requests that match no playlists return a successful empty item collection.",
)

PLAYLISTS_LIST_CAVEATS = (
    "Exactly one selector is required: channelId, id, or mine.",
    "This tool only retrieves playlist resources through playlists.list.",
    "Playlist insertion, update, deletion, playlist item traversal, playlist image handling, playlist search, "
    "video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, "
    "and cross-endpoint aggregation are out of scope.",
    "Returned playlist fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLISTS_LIST_CALLER_EXAMPLES = (
    {
        "name": "channel_scoped_playlist_listing",
        "description": "Quota cost: 1. List playlists for one channelId with API-key access.",
        "arguments": {"part": "snippet,contentDetails", "channelId": "UC123"},
        "result": {"endpoint": "playlists.list", "selector": "channelId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_playlist_lookup",
        "description": "Quota cost: 1. Retrieve playlists by playlist id with API-key access.",
        "arguments": {"part": "id,snippet", "id": "PL123"},
        "result": {"endpoint": "playlists.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "owner_scoped_playlist_listing",
        "description": "Quota cost: 1. List the authorized user's playlists with OAuth-backed access.",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "playlists.list", "selector": "mine", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_listing",
        "description": "Quota cost: 1. Continue channel-scoped traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "channelId": "UC123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An accessible empty playlist collection remains a successful list result.",
        "arguments": {"part": "snippet", "channelId": "UC_NO_PLAYLISTS"},
        "result": {"endpoint": "playlists.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing required playlist part selection.",
        "arguments": {"channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside supported playlist resource sections.",
        "arguments": {"part": "statistics", "channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_selector",
        "description": "Reject requests missing channelId, id, and mine selectors.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "conflicting_selector",
        "description": "Reject requests that combine channelId, id, or mine selectors.",
        "arguments": {"part": "snippet", "channelId": "UC123", "id": "PL123"},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "PL123", "pageToken": "NEXT_PAGE"},
        "error": {"category": "invalid_request", "field": "paging"},
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access for mine to safe access errors.",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "selector": "mine"},
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Map quota and upstream playlist list failures to safe categories.",
        "arguments": {"part": "snippet", "channelId": "UC123"},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Playlist mutation, playlist item traversal, enrichment, analytics, and recommendation are out of scope.",
        "arguments": {"part": "snippet", "channelId": "UC123", "includePlaylistItems": True},
        "error": {"category": "invalid_request", "field": "includePlaylistItems"},
    },
)


class PlaylistsListToolError(ValueError):
    """Represent a safe caller-facing ``playlists_list`` failure.

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
        """Initialize a sanitized playlists list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_playlists_error_details(details or {})


def _sanitize_playlists_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove playlist-list credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in PLAYLISTS_LIST_UNSAFE_DETAIL_KEYS
    }


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlists_parts(part: Any) -> str:
    """Validate and normalize requested playlist parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistsListToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistsListToolError("playlists_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLISTS_LIST_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistsListToolError(
            "playlists_list part must use supported playlist resource sections",
            details={"field": "part", "allowed": list(PLAYLISTS_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active playlists selectors from one request.

    :param arguments: Caller-supplied ``playlists_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in PLAYLISTS_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "mine":
            if value is True:
                active.append((selector, True))
        elif isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
    return active


def validate_playlists_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlists_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsListToolError("playlists_list arguments must be an object")

    allowed = set(PLAYLISTS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise PlaylistsListToolError(
                f"unsupported field for playlists_list: {field}",
                details={"field": field},
            )

    part = _validate_playlists_parts(arguments.get("part"))
    provided_selectors: list[str] = []
    for selector in PLAYLISTS_LIST_SELECTORS:
        if selector not in arguments:
            continue
        value = arguments[selector]
        if selector == "mine":
            if value is not True:
                raise PlaylistsListToolError(
                    "playlists_list mine selector must be true when present",
                    details={"field": "mine"},
                )
        elif not isinstance(value, str) or not value.strip():
            raise PlaylistsListToolError(
                f"playlists_list requires a non-empty {selector}",
                details={"field": selector},
            )
        provided_selectors.append(selector)

    active = _active_selectors(arguments)
    if len(provided_selectors) != 1 or len(active) != 1:
        raise PlaylistsListToolError(
            "playlists_list requires exactly one selector: channelId, id, or mine",
            details={"field": "selector", "allowed": list(PLAYLISTS_LIST_SELECTORS)},
        )

    selector, value = active[0]
    normalized: dict[str, Any] = {"part": part, selector: value}
    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistsListToolError(
            "pageToken and maxResults are only supported with channelId or mine",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistsListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistsListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLISTS_LIST_MAX_RESULTS:
            raise PlaylistsListToolError(
                f"maxResults must be between 0 and {PLAYLISTS_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLISTS_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def _selector_name(arguments: dict[str, Any]) -> str:
    """Return the active selector name from normalized arguments.

    :param arguments: Normalized ``playlists_list`` arguments.
    :return: Active selector name.
    :raises PlaylistsListToolError: If no supported selector is active.
    """
    for selector in PLAYLISTS_LIST_SELECTORS:
        if selector in arguments:
            return selector
    raise PlaylistsListToolError("playlists_list requires a selector", details={"field": "selector"})


def _auth_context_for_selector(
    selector: str,
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for a playlists selector.

    :param selector: Selected playlists selector.
    :param api_key: API key value available for public selector access.
    :param oauth_token: OAuth token available for owner-scoped lookup.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises PlaylistsListToolError: If required credentials are unavailable.
    """
    if selector in {"channelId", "id"}:
        if not isinstance(api_key, str) or not api_key.strip():
            raise PlaylistsListToolError(
                f"{selector} requires public API-key access",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))

    if selector == "mine":
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise PlaylistsListToolError(
                "mine requires eligible OAuth authorization",
                category="authentication_failed",
                details={"selector": selector, "authMode": "oauth_required"},
            )
        return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token.strip()))

    raise PlaylistsListToolError("playlists_list requires a supported selector", details={"field": "selector"})


def map_playlists_list_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    auth_mode: str | None = None,
) -> dict[str, Any]:
    """Map an upstream playlists payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlists list payload.
    :param arguments: Validated caller arguments used for the request.
    :param auth_mode: Safe auth mode selected for execution.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlists_list_arguments(arguments)
    selector = _selector_name(normalized)
    selected_auth_mode = auth_mode or ("oauth_required" if selector == "mine" else "api_key")
    items = payload.get("items", [])
    result: dict[str, Any] = {
        "endpoint": "playlists.list",
        "quotaCost": PLAYLISTS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": selected_auth_mode},
        "items": items,
        "empty": not bool(items),
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


def _map_playlists_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistsListToolError:
    """Map a normalized upstream failure to a safe ``playlists_list`` error.

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
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistsListToolError(str(error), category=category, details=error.details)


def build_playlists_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlists_list``.

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
            "empty",
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "playlist_insertion",
            "playlist_update",
            "playlist_deletion",
            "playlist_item_traversal",
            "playlist_image_handling",
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
        tool_name=PLAYLISTS_LIST_TOOL_NAME,
        upstream_resource="playlists",
        upstream_method="list",
        operation_key="playlists.list",
        description=PLAYLISTS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=PLAYLISTS_LIST_QUOTA_COST,
        resource_family="playlists",
        input_contract=PLAYLISTS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLISTS_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLISTS_LIST_SELECTORS),
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
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLISTS_LIST_USAGE_NOTES,
        caveats=PLAYLISTS_LIST_CAVEATS,
    )


def _default_playlists_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist calls.

    :return: Integration executor returning representative playlist data.
    """

    def transport(execution):
        """Return a representative playlist list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistListResponse",
            "etag": "etag-playlists",
            "items": [
                {
                    "kind": "youtube#playlist",
                    "etag": "etag-playlist",
                    "id": execution.arguments.get("id", "PL123"),
                    "snippet": {
                        "channelId": execution.arguments.get("channelId", "UC123"),
                        "title": "Representative playlist",
                    },
                    "contentDetails": {"itemCount": 3},
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlists_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlists_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used for public selector access.
    :param oauth_token: OAuth token value used for owner-scoped lookup.
    :return: Callable that validates, executes, and maps playlist requests.
    """
    selected_wrapper = wrapper or build_playlists_list_wrapper()
    selected_executor = executor or _default_playlists_list_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlists_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlists list result.
        :raises PlaylistsListToolError: If validation or execution fails.
        """
        normalized = validate_playlists_list_arguments(arguments)
        selector = _selector_name(normalized)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlists_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistsListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlists.list", "selector": selector},
            ) from exc
        return map_playlists_list_result(payload, normalized, auth_mode=auth_context.mode.value)

    return handler


def build_playlists_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlists_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlists_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLISTS_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLISTS_LIST_TOOL_NAME,
        "description": PLAYLISTS_LIST_DESCRIPTION,
        "inputSchema": PLAYLISTS_LIST_INPUT_SCHEMA,
        "handler": build_playlists_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLISTS_LIST_CALLER_EXAMPLES",
    "PLAYLISTS_LIST_CAVEATS",
    "PLAYLISTS_LIST_DESCRIPTION",
    "PLAYLISTS_LIST_INPUT_SCHEMA",
    "PLAYLISTS_LIST_MAX_RESULTS",
    "PLAYLISTS_LIST_QUOTA_COST",
    "PLAYLISTS_LIST_SELECTORS",
    "PLAYLISTS_LIST_SUPPORTED_PARTS",
    "PLAYLISTS_LIST_TOOL_NAME",
    "PLAYLISTS_LIST_USAGE_NOTES",
    "PlaylistsListToolError",
    "build_playlists_list_contract",
    "build_playlists_list_handler",
    "build_playlists_list_tool_descriptor",
    "map_playlists_list_result",
    "validate_playlists_list_arguments",
]
