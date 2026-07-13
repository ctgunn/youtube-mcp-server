"""Concrete Layer 2 tool support for the YouTube ``search`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.search import build_search_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


SEARCH_LIST_TOOL_NAME = "search_list"
SEARCH_LIST_QUOTA_COST = 100
SEARCH_LIST_MAX_RESULTS = 50
SEARCH_LIST_REQUIRED_FIELDS = ("part", "q")
SEARCH_LIST_RESTRICTED_FILTERS = ("forContentOwner", "forDeveloper", "forMine")
SEARCH_LIST_VIDEO_ONLY_FILTERS = (
    "videoCaption",
    "videoDefinition",
    "videoDuration",
    "videoEmbeddable",
    "videoLicense",
    "videoPaidProductPlacement",
    "videoSyndicated",
    "videoType",
)
SEARCH_LIST_OPTIONAL_FIELDS = (
    "type",
    "channelId",
    "publishedAfter",
    "publishedBefore",
    "regionCode",
    "relevanceLanguage",
    "safeSearch",
    "order",
    "pageToken",
    "maxResults",
    *SEARCH_LIST_RESTRICTED_FILTERS,
    *SEARCH_LIST_VIDEO_ONLY_FILTERS,
)
SEARCH_LIST_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

SEARCH_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": list(SEARCH_LIST_REQUIRED_FIELDS),
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "q": {"type": "string", "minLength": 1},
        "type": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "publishedAfter": {"type": "string", "minLength": 1},
        "publishedBefore": {"type": "string", "minLength": 1},
        "regionCode": {"type": "string", "minLength": 1},
        "relevanceLanguage": {"type": "string", "minLength": 1},
        "safeSearch": {"type": "string", "minLength": 1},
        "order": {"type": "string", "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": SEARCH_LIST_MAX_RESULTS},
        "forContentOwner": {"type": "boolean"},
        "forDeveloper": {"type": "boolean"},
        "forMine": {"type": "boolean"},
        "videoCaption": {"type": "string", "minLength": 1},
        "videoDefinition": {"type": "string", "minLength": 1},
        "videoDuration": {"type": "string", "minLength": 1},
        "videoEmbeddable": {"type": "string", "minLength": 1},
        "videoLicense": {"type": "string", "minLength": 1},
        "videoPaidProductPlacement": {"type": "string", "minLength": 1},
        "videoSyndicated": {"type": "string", "minLength": 1},
        "videoType": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

SEARCH_LIST_DESCRIPTION = (
    "Search YouTube resources. Endpoint: search.list. "
    "Quota cost: 100. Auth: mixed/conditional."
)

SEARCH_LIST_USAGE_NOTES = (
    "Quota cost: 100. Use part and q for baseline public search with API-key access.",
    "Quota cost: 100. Use forContentOwner, forDeveloper, or forMine only with eligible OAuth authorization.",
    "Quota cost: 100. Use pageToken and maxResults only to continue a compatible search result set.",
    "Quota cost: 100. Valid accessible requests that match no search results return a successful empty item collection.",
)

SEARCH_LIST_CAVEATS = (
    "Official quota guidance differs between public overview and endpoint reference pages for search.list.",
    "part and q are required by the supported Layer 2 search_list contract.",
    "Restricted filters forContentOwner, forDeveloper, and forMine are mutually exclusive and require OAuth authorization.",
    "Video-specific refinements require type=video.",
    "This tool returns search result references and does not hydrate videos, channels, playlists, transcripts, analytics, "
    "rankings, summaries, recommendations, research syntheses, or cross-endpoint enrichments.",
)

SEARCH_LIST_CALLER_EXAMPLES = (
    {
        "name": "public_keyword_search",
        "description": "Quota cost: 100. Search public YouTube resources with API-key access.",
        "arguments": {"part": "snippet", "q": "mcp server"},
        "result": {"endpoint": "search.list", "itemsPath": "items", "authPath": "public"},
        "quotaCost": 100,
    },
    {
        "name": "type_filtered_video_search",
        "description": "Quota cost: 100. Restrict public results to videos.",
        "arguments": {"part": "snippet", "q": "mcp server", "type": "video"},
        "result": {"endpoint": "search.list", "queryContext": {"type": "video"}},
        "quotaCost": 100,
    },
    {
        "name": "channel_scoped_search",
        "description": "Quota cost: 100. Search within one channel without hydrating channel or video details.",
        "arguments": {"part": "snippet", "q": "release notes", "channelId": "UC123"},
        "result": {"endpoint": "search.list", "queryContext": {"channelId": "UC123"}},
        "quotaCost": 100,
    },
    {
        "name": "date_and_locale_refinement",
        "description": "Quota cost: 100. Refine by publishedAfter, regionCode, and relevanceLanguage.",
        "arguments": {
            "part": "snippet",
            "q": "conference keynote",
            "publishedAfter": "2026-01-01T00:00:00Z",
            "regionCode": "US",
            "relevanceLanguage": "en",
        },
        "quotaCost": 100,
    },
    {
        "name": "restricted_oauth_search",
        "description": "Quota cost: 100. Use forMine only with OAuth-backed restricted access.",
        "arguments": {"part": "snippet", "q": "private uploads", "forMine": True},
        "result": {"endpoint": "search.list", "authPath": "restricted"},
        "quotaCost": 100,
    },
    {
        "name": "paginated_search",
        "description": "Quota cost: 100. Continue compatible search traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "q": "mcp server", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 100,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 100. An accessible empty search collection remains a successful list result.",
        "arguments": {"part": "snippet", "q": "unlikely empty query"},
        "result": {"endpoint": "search.list", "items": []},
        "quotaCost": 100,
    },
    {
        "name": "missing_query",
        "description": "Reject search requests missing required q.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "q"},
    },
    {
        "name": "missing_part",
        "description": "Reject search requests missing required part.",
        "arguments": {"q": "mcp server"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "incompatible_video_filter",
        "description": "Reject video-specific refinements unless type=video.",
        "arguments": {"part": "snippet", "q": "mcp server", "videoDuration": "short"},
        "error": {"category": "invalid_request", "field": "type"},
    },
    {
        "name": "restricted_filter_conflict",
        "description": "Reject mutually exclusive restricted search filters.",
        "arguments": {"part": "snippet", "q": "mcp server", "forMine": True, "forDeveloper": True},
        "error": {"category": "invalid_request", "field": "restricted_filter"},
    },
    {
        "name": "invalid_pagination",
        "description": "Reject invalid pagination controls before execution.",
        "arguments": {"part": "snippet", "q": "mcp server", "pageToken": ""},
        "error": {"category": "invalid_request", "field": "pageToken"},
    },
    {
        "name": "access_failure",
        "description": "Map missing OAuth for restricted search to safe authentication errors.",
        "arguments": {"part": "snippet", "q": "private uploads", "forMine": True},
        "error": {"category": "authentication_failed", "authPath": "restricted"},
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Map quota and upstream search failures to safe categories.",
        "arguments": {"part": "snippet", "q": "mcp server"},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "out_of_scope_enrichment_request",
        "description": "Transcript retrieval, hydration, ranking, summarization, analytics, and recommendation are out of scope.",
        "arguments": {"part": "snippet", "q": "mcp server", "includeTranscript": True},
        "error": {"category": "invalid_request", "field": "includeTranscript"},
    },
)


class SearchListToolError(ValueError):
    """Represent a safe caller-facing ``search_list`` failure.

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
        """Initialize a sanitized search list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_search_error_details(details or {})


def _sanitize_search_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove search credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in SEARCH_LIST_UNSAFE_DETAIL_KEYS
    }


def _require_text_field(arguments: dict[str, Any], field: str) -> str:
    """Return a stripped required text field from search arguments.

    :param arguments: Candidate tool arguments.
    :param field: Required field name to validate.
    :return: Stripped field value.
    :raises SearchListToolError: If the field is absent or not non-empty text.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SearchListToolError(f"search_list requires {field}", details={"field": field})
    return value.strip()


def _active_restricted_filters(arguments: dict[str, Any]) -> list[str]:
    """Return restricted filters active in one search request.

    :param arguments: Normalized or candidate search arguments.
    :return: Active restricted filter names.
    """
    active: list[str] = []
    for field in SEARCH_LIST_RESTRICTED_FILTERS:
        value = arguments.get(field)
        if value is True or (isinstance(value, str) and value.strip()):
            active.append(field)
        elif field in arguments and value not in (False, None, ""):
            raise SearchListToolError(
                f"{field} must be a boolean when present",
                details={"field": field},
            )
    return active


def _uses_video_only_filters(arguments: dict[str, Any]) -> bool:
    """Return whether one request uses video-specific search refinements.

    :param arguments: Candidate search arguments.
    :return: ``True`` when any video-only refinement is present.
    """
    return any(arguments.get(field) not in (None, "") for field in SEARCH_LIST_VIDEO_ONLY_FILTERS)


def validate_search_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``search_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises SearchListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise SearchListToolError("search_list arguments must be an object")

    allowed = set(SEARCH_LIST_INPUT_SCHEMA["properties"])
    normalized: dict[str, Any] = {}
    for field, value in arguments.items():
        if field not in allowed:
            raise SearchListToolError(
                f"unsupported field for search_list: {field}",
                details={"field": field},
            )
        if isinstance(value, str):
            if not value.strip():
                raise SearchListToolError(f"{field} must be non-empty when present", details={"field": field})
            normalized[field] = value.strip()
        else:
            normalized[field] = value

    normalized["part"] = _require_text_field(normalized, "part")
    normalized["q"] = _require_text_field(normalized, "q")

    restricted = _active_restricted_filters(normalized)
    if len(restricted) > 1:
        raise SearchListToolError(
            "restricted search filters are mutually exclusive",
            details={"field": "restricted_filter", "filters": restricted},
        )

    if _uses_video_only_filters(normalized) and normalized.get("type") != "video":
        raise SearchListToolError(
            "video-specific refinements require type=video",
            details={"field": "type", "required": "video"},
        )

    page_token = normalized.get("pageToken")
    if page_token is not None and (not isinstance(page_token, str) or not page_token.strip()):
        raise SearchListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})

    max_results = normalized.get("maxResults")
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise SearchListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > SEARCH_LIST_MAX_RESULTS:
            raise SearchListToolError(
                f"maxResults must be between 0 and {SEARCH_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": SEARCH_LIST_MAX_RESULTS},
            )

    return normalized


def _auth_path(arguments: dict[str, Any]) -> str:
    """Return the public auth path used by normalized search arguments.

    :param arguments: Normalized search arguments.
    :return: ``restricted`` when OAuth-backed filters are used, else ``public``.
    """
    return "restricted" if _active_restricted_filters(arguments) else "public"


def _auth_context_for_search(
    arguments: dict[str, Any],
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for one search request.

    :param arguments: Normalized search arguments.
    :param api_key: API key value available for public search access.
    :param oauth_token: OAuth token available for restricted search access.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises SearchListToolError: If required credentials are unavailable.
    """
    if _auth_path(arguments) == "restricted":
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise SearchListToolError(
                "restricted search requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authPath": "restricted", "authMode": "oauth_required"},
            )
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )

    if not isinstance(api_key, str) or not api_key.strip():
        raise SearchListToolError(
            "public search requires API-key access",
            category="authentication_failed",
            details={"authPath": "public", "authMode": "api_key"},
        )
    return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))


def _safe_query_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe query and filter context for public search results.

    :param arguments: Normalized search arguments.
    :return: JSON-compatible context for caller-facing results.
    """
    return {
        key: value
        for key, value in arguments.items()
        if value not in (None, "")
        and key
        in {
            "part",
            "q",
            "type",
            "channelId",
            "publishedAfter",
            "publishedBefore",
            "regionCode",
            "relevanceLanguage",
            "safeSearch",
            "order",
            "pageToken",
            "maxResults",
            *SEARCH_LIST_RESTRICTED_FILTERS,
            *SEARCH_LIST_VIDEO_ONLY_FILTERS,
        }
    }


def _search_pagination(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Return request and response pagination context for search results.

    :param payload: Upstream or Layer 1 payload.
    :param arguments: Normalized search arguments.
    :return: Safe pagination context, or an empty mapping.
    """
    pagination: dict[str, Any] = {}
    for field in ("pageToken", "maxResults"):
        if field in arguments:
            pagination[field] = arguments[field]
    for field in ("nextPageToken", "prevPageToken"):
        if field in payload:
            pagination[field] = payload[field]
    return pagination


def map_search_list_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    auth_mode: str | None = None,
) -> dict[str, Any]:
    """Map an upstream search payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 search list payload.
    :param arguments: Validated caller arguments used for the request.
    :param auth_mode: Safe auth mode selected for execution.
    :return: Near-raw search list result with safe operation context.
    """
    normalized = validate_search_list_arguments(arguments)
    items = payload.get("items", [])
    path = _auth_path(normalized)
    selected_auth_mode = auth_mode or ("oauth_required" if path == "restricted" else "api_key")
    result: dict[str, Any] = {
        "endpoint": "search.list",
        "quotaCost": SEARCH_LIST_QUOTA_COST,
        "items": items,
        "empty": not bool(items),
        "queryContext": payload.get("queryContext") or _safe_query_context(normalized),
        "auth": {"mode": selected_auth_mode, "path": path},
    }
    pagination = _search_pagination(payload, normalized)
    if pagination:
        result["pagination"] = pagination
    for field in ("kind", "etag", "nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_search_list_upstream_error(error: NormalizedUpstreamError) -> SearchListToolError:
    """Map a normalized upstream failure to a safe ``search_list`` error.

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
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return SearchListToolError(str(error), category=category, details=error.details or {})


def build_search_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``search_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "items",
            "empty",
            "queryContext",
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
            "video_hydration",
            "channel_hydration",
            "playlist_hydration",
            "transcript_retrieval",
            "analytics",
            "ranking",
            "summarization",
            "recommendation",
            "research_synthesis",
            "cross_endpoint_enrichment",
        ),
    )
    return YouTubeToolContract(
        tool_name=SEARCH_LIST_TOOL_NAME,
        upstream_resource="search",
        upstream_method="list",
        operation_key="search.list",
        description=SEARCH_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=SEARCH_LIST_QUOTA_COST,
        resource_family="search",
        input_contract=SEARCH_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requiredFields": list(SEARCH_LIST_REQUIRED_FIELDS),
            "filterFields": list(SEARCH_LIST_OPTIONAL_FIELDS),
            "restrictedFields": list(SEARCH_LIST_RESTRICTED_FILTERS),
            "videoOnlyFields": list(SEARCH_LIST_VIDEO_ONLY_FILTERS),
            "pagingFields": ["pageToken", "maxResults", "nextPageToken", "prevPageToken", "pageInfo"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "invalid_request",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.DOCUMENTATION_CAVEAT,
        usage_notes=SEARCH_LIST_USAGE_NOTES,
        caveats=SEARCH_LIST_CAVEATS,
    )


def _default_search_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default search calls.

    :return: Integration executor returning representative search data.
    """

    def transport(execution):
        """Return a representative search list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        query = execution.arguments.get("q", "mcp server")
        if query == "unlikely empty query":
            return {
                "kind": "youtube#searchListResponse",
                "etag": "etag-search-empty",
                "items": [],
                "pageInfo": {"totalResults": 0, "resultsPerPage": 0},
            }
        return {
            "kind": "youtube#searchListResponse",
            "etag": "etag-search",
            "nextPageToken": "NEXT_PAGE",
            "items": [
                {
                    "kind": "youtube#searchResult",
                    "etag": "etag-search-result",
                    "id": {"kind": "youtube#video", "videoId": "abc123"},
                    "snippet": {
                        "title": f"Representative result for {query}",
                        "channelId": execution.arguments.get("channelId", "UC123"),
                    },
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_search_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``search_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used for public search access.
    :param oauth_token: OAuth token value used for restricted search access.
    :return: Callable that validates, executes, and maps search requests.
    """
    selected_wrapper = wrapper or build_search_list_wrapper()
    selected_executor = executor or _default_search_list_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``search_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 search list result.
        :raises SearchListToolError: If validation or execution fails.
        """
        normalized = validate_search_list_arguments(arguments)
        auth_context = _auth_context_for_search(normalized, api_key=api_key, oauth_token=oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_search_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise SearchListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "search.list", "authPath": _auth_path(normalized)},
            ) from exc
        return map_search_list_result(payload, normalized, auth_mode=auth_context.mode.value)

    return handler


def build_search_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``search_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_search_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(SEARCH_LIST_CALLER_EXAMPLES)
    return {
        "name": SEARCH_LIST_TOOL_NAME,
        "description": SEARCH_LIST_DESCRIPTION,
        "inputSchema": SEARCH_LIST_INPUT_SCHEMA,
        "handler": build_search_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


__all__ = [
    "SEARCH_LIST_CALLER_EXAMPLES",
    "SEARCH_LIST_CAVEATS",
    "SEARCH_LIST_DESCRIPTION",
    "SEARCH_LIST_INPUT_SCHEMA",
    "SEARCH_LIST_MAX_RESULTS",
    "SEARCH_LIST_OPTIONAL_FIELDS",
    "SEARCH_LIST_QUOTA_COST",
    "SEARCH_LIST_REQUIRED_FIELDS",
    "SEARCH_LIST_RESTRICTED_FILTERS",
    "SEARCH_LIST_TOOL_NAME",
    "SEARCH_LIST_USAGE_NOTES",
    "SEARCH_LIST_VIDEO_ONLY_FILTERS",
    "SearchListToolError",
    "build_search_list_contract",
    "build_search_list_handler",
    "build_search_list_tool_descriptor",
    "map_search_list_result",
    "validate_search_list_arguments",
]
