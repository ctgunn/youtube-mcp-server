"""Representative Layer 2 contract examples for shared validation."""

from __future__ import annotations

from mcp_server.tools.youtube_common.contracts import AuthMode, Layer2ToolContract


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
    caveats: tuple[str, ...] = (),
) -> Layer2ToolContract:
    """Build a representative Layer 2 contract example.

    :param resource: Upstream YouTube resource name.
    :param method: Upstream YouTube method name.
    :param description: Caller-facing example description.
    :param auth_mode: Declared credential mode.
    :param quota_cost: Official quota-unit cost.
    :param resource_family: Owning resource-family label.
    :param input_contract: Representative input contract metadata.
    :param response_convention: Representative response convention metadata.
    :param error_categories: Safe error categories for the example.
    :param caveats: Optional caveat notes for the example.
    :return: A validated representative Layer 2 tool contract.
    """
    return Layer2ToolContract(
        tool_name=f"{resource}_{method}",
        upstream_resource=resource,
        upstream_method=method,
        operation_key=f"{resource}.{method}",
        description=description,
        auth_mode=auth_mode,
        quota_cost=quota_cost,
        resource_family=resource_family,
        input_contract=input_contract,
        response_convention=response_convention,
        error_categories=error_categories,
        caveats=caveats,
    )


REPRESENTATIVE_LAYER2_CONTRACTS: tuple[Layer2ToolContract, ...] = (
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
        resource="videos",
        method="insert",
        description="Upload a video. Endpoint: videos.insert. Quota cost: 1600. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1600,
        resource_family="videos",
        input_contract={"required": ["part", "media"], "properties": {"media": {"type": "string"}}},
        response_convention={"resultKind": "upload_result", "mediaResult": True},
        error_categories=("invalid_request", "authorization_failed", "quota_exhausted"),
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
        caveats=("High quota cost; callers should inspect quota before use.",),
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
        caveats=("Endpoint is deprecated or availability-constrained in current upstream documentation.",),
    ),
)
