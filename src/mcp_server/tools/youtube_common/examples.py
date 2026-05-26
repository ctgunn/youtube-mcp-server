"""Representative shared YouTube contract examples for shared validation."""

from __future__ import annotations

from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract, derive_tool_name
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


def _contract(
    *,
    resource: str,
    method: str,
    description: str,
    auth_mode: AuthMode,
    quota_cost: int,
    resource_family: str,
    input_contract: dict,
    response_convention: dict,
    error_categories: tuple[str, ...],
    response_boundary: dict | None = None,
    availability_state: AvailabilityState = AvailabilityState.ACTIVE,
    usage_notes: tuple[str, ...] = (),
    caveats: tuple[str, ...] = (),
) -> YouTubeToolContract:
    """Build a representative shared YouTube contract example.

    :param resource: Upstream YouTube resource name.
    :param method: Upstream YouTube method name.
    :param description: Caller-facing example description.
    :param auth_mode: Declared credential mode.
    :param quota_cost: Official quota-unit cost.
    :param resource_family: Owning resource-family label.
    :param input_contract: Representative input contract metadata.
    :param response_convention: Representative response convention metadata.
    :param error_categories: Safe error categories for the example.
    :param response_boundary: Representative response-boundary metadata.
    :param availability_state: Public availability status for the example.
    :param usage_notes: Optional caller-facing usage notes with quota details.
    :param caveats: Optional caveat notes for the example.
    :return: A validated representative YouTube tool contract.
    """
    notes = usage_notes or (f"Quota cost: {quota_cost}. Auth: {auth_mode.value}.",)
    boundary = response_boundary or _default_response_boundary(response_convention)
    return YouTubeToolContract(
        tool_name=derive_tool_name(resource, method),
        upstream_resource=resource,
        upstream_method=method,
        operation_key=f"{resource}.{method}",
        description=description,
        auth_mode=auth_mode,
        quota_cost=quota_cost,
        resource_family=resource_family,
        input_contract=input_contract,
        response_convention=response_convention,
        response_boundary=boundary,
        error_categories=error_categories,
        availability_state=availability_state,
        usage_notes=notes,
        caveats=caveats,
    )


def _default_response_boundary(response_convention: dict) -> dict:
    """Build response-boundary metadata from a representative result kind.

    :param response_convention: Representative response convention metadata.
    :return: JSON-compatible response-boundary metadata.
    """
    result_kind = response_convention.get("resultKind")
    if result_kind == "list":
        return ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            preserved_upstream_fields=("items", "nextPageToken", "requestedParts"),
        ).to_metadata()
    if result_kind == "lookup":
        return ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            preserved_upstream_fields=("items", "requestedParts"),
        ).to_metadata()
    if result_kind == "mutation_acknowledgment":
        return ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
            allowed_wrapper_fields=("endpoint", "quotaCost", "acknowledgment"),
            preserved_upstream_fields=("operationStatus",),
        ).to_metadata()
    if result_kind == "upload_result":
        return ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
            allowed_wrapper_fields=("endpoint", "quotaCost", "mediaResult"),
            preserved_upstream_fields=("id", "resource"),
        ).to_metadata()
    if result_kind == "download_wrapper":
        return ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
            allowed_wrapper_fields=("endpoint", "quotaCost", "contentPolicy"),
            preserved_upstream_fields=("content", "metadata"),
        ).to_metadata()
    return ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
        allowed_wrapper_fields=("endpoint", "quotaCost"),
        preserved_upstream_fields=("resource",),
    ).to_metadata()


REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS: tuple[YouTubeToolContract, ...] = (
    _contract(
        resource="activities",
        method="list",
        description="List channel activities. Endpoint: activities.list. Quota cost: 1. Auth: mixed/conditional.",
        auth_mode=AuthMode.MIXED,
        quota_cost=1,
        resource_family="activities",
        input_contract={"required": ["part"], "properties": {"part": {"type": "string"}}},
        response_convention={"resultKind": "list", "itemsPath": "items", "pagingFields": ["nextPageToken"]},
        error_categories=("invalid_request", "authentication_failed", "quota_exhausted"),
    ),
    _contract(
        resource="comments",
        method="setModerationStatus",
        description=(
            "Set comment moderation status. Endpoint: comments.setModerationStatus. "
            "Quota cost: 50. Auth: oauth_required."
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="comments",
        input_contract={
            "required": ["id", "moderationStatus"],
            "properties": {"id": {"type": "string"}, "moderationStatus": {"type": "string"}},
        },
        response_convention={"resultKind": "mutation_acknowledgment"},
        error_categories=("invalid_request", "authorization_failed", "resource_not_found"),
    ),
    _contract(
        resource="videos",
        method="getRating",
        description="Get video rating. Endpoint: videos.getRating. Quota cost: 1. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        resource_family="videos",
        input_contract={"required": ["id"], "properties": {"id": {"type": "string"}}},
        response_convention={"resultKind": "lookup", "itemsPath": "items"},
        error_categories=("invalid_request", "authorization_failed", "resource_not_found"),
    ),
    _contract(
        resource="watermarks",
        method="unset",
        description="Remove a channel watermark. Endpoint: watermarks.unset. Quota cost: 50. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="watermarks",
        input_contract={"required": [], "properties": {"onBehalfOfContentOwner": {"type": "string"}}},
        response_convention={"resultKind": "mutation_acknowledgment"},
        error_categories=("invalid_request", "authorization_failed", "endpoint_unavailable"),
        availability_state=AvailabilityState.OWNER_ONLY,
        caveats=("Availability may depend on channel ownership and current upstream support.",),
    ),
    _contract(
        resource="playlistItems",
        method="list",
        description="List playlist items. Endpoint: playlistItems.list. Quota cost: 1. Auth: mixed/conditional.",
        auth_mode=AuthMode.MIXED,
        quota_cost=1,
        resource_family="playlist_items",
        input_contract={
            "required": ["part"],
            "properties": {"part": {"type": "string"}, "pageToken": {"type": "string"}},
        },
        response_convention={"resultKind": "list", "itemsPath": "items", "pagingFields": ["nextPageToken"]},
        error_categories=("invalid_request", "quota_exhausted", "resource_not_found"),
    ),
    _contract(
        resource="videos",
        method="update",
        description="Update video metadata. Endpoint: videos.update. Quota cost: 50. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="videos",
        input_contract={"required": ["part", "body"], "properties": {"part": {"type": "string"}}},
        response_convention={"resultKind": "mutation_acknowledgment"},
        error_categories=("invalid_request", "authorization_failed", "resource_not_found"),
    ),
    _contract(
        resource="playlists",
        method="insert",
        description="Create a playlist. Endpoint: playlists.insert. Quota cost: 50. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="playlists",
        input_contract={"required": ["part", "body"], "properties": {"part": {"type": "string"}}},
        response_convention={"resultKind": "mutation_acknowledgment"},
        error_categories=("invalid_request", "authorization_failed", "quota_exhausted"),
    ),
    _contract(
        resource="videos",
        method="insert",
        description="Upload a video. Endpoint: videos.insert. Quota cost: 1600. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1600,
        resource_family="videos",
        input_contract={"required": ["part", "media"], "properties": {"media": {"type": "string"}}},
        response_convention={"resultKind": "upload_result", "mediaResult": True},
        error_categories=("invalid_request", "authorization_failed", "quota_exhausted"),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
        usage_notes=("Quota cost: 1600. Auth: oauth_required. High quota cost; confirm intent before use.",),
        caveats=("High quota cost; endpoint-specific slices must warn before use.",),
    ),
    _contract(
        resource="captions",
        method="download",
        description="Download captions. Endpoint: captions.download. Quota cost: 200. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=200,
        resource_family="captions",
        input_contract={"required": ["id"], "properties": {"tfmt": {"type": "string"}}},
        response_convention={"resultKind": "download_wrapper", "contentPolicy": "safe_text_or_metadata_wrapper"},
        error_categories=("invalid_request", "authorization_failed", "resource_not_found"),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
    ),
    _contract(
        resource="search",
        method="list",
        description="Search YouTube resources. Endpoint: search.list. Quota cost: 100. Auth: api_key.",
        auth_mode=AuthMode.API_KEY,
        quota_cost=100,
        resource_family="search",
        input_contract={"required": ["part"], "properties": {"q": {"type": "string"}}},
        response_convention={"resultKind": "list", "itemsPath": "items", "pagingFields": ["nextPageToken"]},
        error_categories=("invalid_request", "quota_exhausted", "upstream_failure"),
        usage_notes=("Quota cost: 100. Auth: api_key. High quota cost; inspect quota before use.",),
        caveats=("High quota cost; callers should inspect quota before use.",),
    ),
    _contract(
        resource="videos",
        method="reportAbuse",
        description="Report video abuse. Endpoint: videos.reportAbuse. Quota cost: 50. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="videos",
        input_contract={"required": ["videoId", "reasonId"], "properties": {"videoId": {"type": "string"}}},
        response_convention={"resultKind": "mutation_acknowledgment"},
        error_categories=("invalid_request", "authorization_failed", "resource_not_found"),
        availability_state=AvailabilityState.OWNER_ONLY,
        caveats=("Abuse reporting requires authorized caller context and endpoint-specific validation.",),
    ),
    _contract(
        resource="guideCategories",
        method="list",
        description="List guide categories. Endpoint: guideCategories.list. Quota cost: 1. Auth: api_key.",
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        resource_family="guide_categories",
        input_contract={"required": ["part"], "properties": {"regionCode": {"type": "string"}}},
        response_convention={"resultKind": "lookup", "itemsPath": "items"},
        error_categories=("invalid_request", "deprecated_endpoint", "endpoint_unavailable"),
        availability_state=AvailabilityState.DEPRECATED,
        caveats=("Endpoint is deprecated or availability-constrained in current upstream documentation.",),
    ),
)
