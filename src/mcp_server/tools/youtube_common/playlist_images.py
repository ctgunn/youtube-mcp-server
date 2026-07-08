"""Concrete Layer 2 tool support for the YouTube ``playlistImages`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlist_images import build_playlist_images_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLIST_IMAGES_LIST_TOOL_NAME = "playlistImages_list"
PLAYLIST_IMAGES_LIST_QUOTA_COST = 1
PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS = ("id", "snippet")
PLAYLIST_IMAGES_LIST_SELECTORS = ("playlistId", "id")
PLAYLIST_IMAGES_LIST_MAX_RESULTS = 50

PLAYLIST_IMAGES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "playlistId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLIST_IMAGES_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLIST_IMAGES_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLIST_IMAGES_LIST_DESCRIPTION = (
    "List YouTube playlist image resources. Endpoint: playlistImages.list. "
    "Quota cost: 1. Auth: oauth_required."
)

PLAYLIST_IMAGES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: oauth_required. Provide part and exactly one selector: playlistId or id.",
    "Quota cost: 1. Use playlistId for playlist-scoped image retrieval with optional pageToken and maxResults.",
    "Quota cost: 1. Use id for direct playlist image lookup; pageToken and maxResults are rejected with id.",
)

PLAYLIST_IMAGES_LIST_CAVEATS = (
    "This tool only retrieves playlist image resources through playlistImages.list.",
    "playlist image insertion, update, deletion, media upload, thumbnail replacement, and playlist management are out of scope.",
    "Playlist-item expansion, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint aggregation are out of scope.",
)

PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES = (
    {
        "name": "playlist_scoped_image_listing",
        "description": "Quota cost: 1. List playlist images for one playlistId.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistImages.list", "selector": "playlistId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_image_lookup",
        "description": "Quota cost: 1. Retrieve one playlist image by id.",
        "arguments": {"part": "id,snippet", "id": "playlist-image-123"},
        "result": {"endpoint": "playlistImages.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_image_listing",
        "description": "Quota cost: 1. Continue a playlist-scoped image traversal with paging controls.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An empty playlist-image collection remains a successful list result.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistImages.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required playlist-image part selection.",
        "arguments": {"playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside id and snippet.",
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
        "arguments": {"part": "snippet", "playlistId": "PL123", "id": "playlist-image-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "playlist-image-123", "pageToken": "NEXT_PAGE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access to safe authentication or authorization errors.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "out_of_scope_image_management_request",
        "description": "Playlist image mutation, upload, thumbnail replacement, and analytics requests are out of scope.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "media": {"content": "raw"}},
        "errorCategory": "invalid_request",
    },
)


class PlaylistImagesListToolError(ValueError):
    """Represent a safe caller-facing ``playlistImages_list`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist-image part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlist_images_parts(part: Any) -> str:
    """Validate and normalize the requested playlist-image parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistImagesListToolError: If part is missing or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistImagesListToolError("playlistImages_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if not parts or len(set(parts)) != len(parts) or any(item not in PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS for item in parts):
        raise PlaylistImagesListToolError(
            "playlistImages_list part must use id, snippet, or both",
            details={"field": "part", "allowed": list(PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def validate_playlist_images_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistImages_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistImagesListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistImagesListToolError("playlistImages_list arguments must be an object")

    allowed = {"part", "playlistId", "id", "pageToken", "maxResults"}
    for field in arguments:
        if field not in allowed:
            raise PlaylistImagesListToolError(
                f"unsupported field for playlistImages_list: {field}",
                details={"field": field},
            )

    part = _validate_playlist_images_parts(arguments.get("part"))
    selected = [
        selector
        for selector in PLAYLIST_IMAGES_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise PlaylistImagesListToolError(
            "playlistImages_list requires exactly one selector: playlistId or id",
            details={"field": "selector", "allowed": list(PLAYLIST_IMAGES_LIST_SELECTORS)},
        )

    selector = selected[0]
    normalized: dict[str, Any] = {"part": part, selector: arguments[selector].strip()}

    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistImagesListToolError(
            "pageToken and maxResults are only supported with playlistId",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistImagesListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistImagesListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLIST_IMAGES_LIST_MAX_RESULTS:
            raise PlaylistImagesListToolError(
                f"maxResults must be between 0 and {PLAYLIST_IMAGES_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLIST_IMAGES_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def map_playlist_images_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist-image payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-image list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlist_images_list_arguments(arguments)
    selector = "playlistId" if "playlistId" in normalized else "id"
    result = {
        "endpoint": "playlistImages.list",
        "quotaCost": PLAYLIST_IMAGES_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": "oauth_required"},
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


def _map_playlist_images_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistImagesListToolError:
    """Map a normalized upstream failure to a safe ``playlistImages_list`` error.

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
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistImagesListToolError(str(error), category=category, details=error.details)


def _playlist_images_list_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistImages_list``.

    :param oauth_token: OAuth token used for playlist-image retrieval.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistImagesListToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistImagesListToolError(
            "playlistImages_list requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_playlist_images_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistImages_list``.

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
            "playlist_image_insertion",
            "playlist_image_update",
            "playlist_image_deletion",
            "media_upload",
            "thumbnail_replacement",
            "playlist_management",
            "playlist_item_expansion",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_IMAGES_LIST_TOOL_NAME,
        upstream_resource="playlistImages",
        upstream_method="list",
        operation_key="playlistImages.list",
        description=PLAYLIST_IMAGES_LIST_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_IMAGES_LIST_QUOTA_COST,
        resource_family="playlist_images",
        input_contract=PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLIST_IMAGES_LIST_SELECTORS),
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
        usage_notes=PLAYLIST_IMAGES_LIST_USAGE_NOTES,
        caveats=PLAYLIST_IMAGES_LIST_CAVEATS,
    )


def _default_playlist_images_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-image calls.

    :return: Integration executor returning representative playlist-image data.
    """

    def transport(execution):
        """Return a representative playlist-image list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistImageListResponse",
            "etag": "etag-playlist-images",
            "items": [
                {
                    "kind": "youtube#playlistImage",
                    "id": "playlist-image-123",
                    "snippet": {
                        "playlistId": execution.arguments.get("playlistId", "PL123"),
                        "type": "medium",
                    },
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlist_images_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistImages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps playlist-image requests.
    """
    selected_wrapper = wrapper or build_playlist_images_list_wrapper()
    selected_executor = executor or _default_playlist_images_list_executor()
    auth_context = _playlist_images_list_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistImages_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-image list result.
        :raises PlaylistImagesListToolError: If validation or execution fails.
        """
        normalized = validate_playlist_images_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_images_list_upstream_error(exc) from exc
        return map_playlist_images_list_result(payload, normalized)

    return handler


def build_playlist_images_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistImages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_images_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_IMAGES_LIST_TOOL_NAME,
        "description": PLAYLIST_IMAGES_LIST_DESCRIPTION,
        "inputSchema": PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
        "handler": build_playlist_images_list_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES",
    "PLAYLIST_IMAGES_LIST_CAVEATS",
    "PLAYLIST_IMAGES_LIST_DESCRIPTION",
    "PLAYLIST_IMAGES_LIST_INPUT_SCHEMA",
    "PLAYLIST_IMAGES_LIST_MAX_RESULTS",
    "PLAYLIST_IMAGES_LIST_QUOTA_COST",
    "PLAYLIST_IMAGES_LIST_SELECTORS",
    "PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS",
    "PLAYLIST_IMAGES_LIST_TOOL_NAME",
    "PLAYLIST_IMAGES_LIST_USAGE_NOTES",
    "PlaylistImagesListToolError",
    "build_playlist_images_list_contract",
    "build_playlist_images_list_handler",
    "build_playlist_images_list_tool_descriptor",
    "map_playlist_images_list_result",
    "validate_playlist_images_list_arguments",
]
