"""Representative shared YouTube contract examples for shared validation."""

from __future__ import annotations

from mcp_server.tools.youtube_common.channel_banners import build_channel_banners_insert_contract
from mcp_server.tools.youtube_common.channel_sections import (
    build_channel_sections_delete_contract,
    build_channel_sections_insert_contract,
    build_channel_sections_list_contract,
    build_channel_sections_update_contract,
)
from mcp_server.tools.youtube_common.channels import build_channels_list_contract, build_channels_update_contract
from mcp_server.tools.youtube_common.comments import (
    build_comments_delete_contract,
    build_comments_insert_contract,
    build_comments_list_contract,
    build_comments_set_moderation_status_contract,
    build_comments_update_contract,
)
from mcp_server.tools.youtube_common.comment_threads import (
    build_comment_threads_insert_contract,
    build_comment_threads_list_contract,
)
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract, derive_tool_name
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind
from mcp_server.tools.youtube_common.guide_categories import build_guide_categories_list_contract
from mcp_server.tools.youtube_common.localization import (
    build_i18n_languages_list_contract,
    build_i18n_regions_list_contract,
)
from mcp_server.tools.youtube_common.members import build_members_list_contract
from mcp_server.tools.youtube_common.memberships_levels import build_memberships_levels_list_contract
from mcp_server.tools.youtube_common.playlist_images import (
    build_playlist_images_delete_contract,
    build_playlist_images_insert_contract,
    build_playlist_images_list_contract,
    build_playlist_images_update_contract,
)
from mcp_server.tools.youtube_common.playlist_items import (
    build_playlist_items_delete_contract,
    build_playlist_items_insert_contract,
    build_playlist_items_list_contract,
    build_playlist_items_update_contract,
)
from mcp_server.tools.youtube_common.playlists import (
    build_playlists_delete_contract,
    build_playlists_insert_contract,
    build_playlists_list_contract,
    build_playlists_update_contract,
)


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
        resource="captions",
        method="list",
        description="List caption tracks. Endpoint: captions.list. Quota cost: 50. Auth: oauth_required.",
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="captions",
        input_contract={
            "required": ["part", "videoId"],
            "properties": {
                "part": {"type": "string"},
                "videoId": {"type": "string"},
                "id": {"type": "string"},
                "onBehalfOfContentOwner": {"type": "string"},
            },
        },
        response_convention={"resultKind": "list", "itemsPath": "items", "pagingFields": ["nextPageToken"]},
        error_categories=("invalid_request", "authentication_failed", "authorization_failed", "quota_exhausted"),
        usage_notes=(
            "Quota cost: 50. Auth: oauth_required. Use videoId for caption listing.",
            "Quota cost: 50. onBehalfOfContentOwner is optional delegation context.",
        ),
        caveats=("Caption listing requires eligible OAuth authorization.",),
    ),
    _contract(
        resource="captions",
        method="insert",
        description=(
            "Insert caption track. Endpoint: captions.insert. "
            "Quota cost: 400. Auth: oauth_required. Requires caption media input."
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=400,
        resource_family="captions",
        input_contract={
            "required": ["part", "body", "media"],
            "properties": {
                "part": {"type": "string"},
                "body": {"type": "object"},
                "media": {"type": "object"},
                "onBehalfOfContentOwner": {"type": "string"},
                "sync": {"type": "boolean"},
            },
        },
        response_convention={
            "resultKind": "upload_result",
            "resourcePath": "item",
            "mediaResult": "safe_media_summary",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "metadata", "media", "delegation", "requestedParts"),
            preserved_upstream_fields=("item", "id", "snippet", "requestedParts"),
            disallowed_behavior=("caption_download", "language_ranking", "translation", "cross_endpoint_aggregation"),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
        usage_notes=(
            "Quota cost: 400. Auth: oauth_required. Provide body metadata and media input.",
            "Quota cost: 400. onBehalfOfContentOwner is optional delegation context.",
            "Quota cost: 400. sync is deprecated upstream and is not the recommended path.",
        ),
        caveats=(
            "Caption insertion requires eligible OAuth authorization.",
            "Caption media input is required; metadata-only requests are unsupported.",
            "sync is deprecated and should not be used as the normal path.",
        ),
    ),
    _contract(
        resource="captions",
        method="update",
        description=(
            "Update caption track. Endpoint: captions.update. "
            "Quota cost: 450. Auth: oauth_required. Requires caption update body; media replacement is optional."
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=450,
        resource_family="captions",
        input_contract={
            "required": ["part", "body"],
            "properties": {
                "part": {"type": "string"},
                "body": {"type": "object"},
                "media": {"type": "object"},
                "onBehalfOfContentOwner": {"type": "string"},
                "sync": {"type": "boolean"},
            },
        },
        response_convention={
            "resultKind": "upload_result",
            "resourcePath": "item",
            "mediaResult": "safe_media_summary",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "update", "media", "delegation", "requestedParts"),
            preserved_upstream_fields=("item", "id", "snippet", "requestedParts"),
            disallowed_behavior=("caption_download", "caption_creation", "language_ranking", "translation"),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
        usage_notes=(
            "Quota cost: 450. Auth: oauth_required. Provide body with the caption track id.",
            "Quota cost: 450. media is optional replacement caption content and must be paired with a valid body.",
            "Quota cost: 450. onBehalfOfContentOwner is optional delegation context.",
            "Quota cost: 450. sync is deprecated upstream and requires updated caption media.",
        ),
        caveats=(
            "Caption update requires eligible OAuth authorization.",
            "Caption update body is required; media-only requests are unsupported.",
            "sync is deprecated and should not be used as the normal path.",
        ),
    ),
    build_comments_set_moderation_status_contract(),
    build_comments_delete_contract(),
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
        description=(
            "Download caption track content. Endpoint: captions.download. "
            "Quota cost: 200. Auth: oauth_required. Requires caption track id and eligible edit permission."
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=200,
        resource_family="captions",
        input_contract={
            "required": ["id"],
            "properties": {
                "id": {"type": "string"},
                "tfmt": {"type": "string", "enum": ["sbv", "scc", "srt", "ttml", "vtt"]},
                "tlang": {"type": "string"},
                "onBehalfOfContentOwner": {"type": "string"},
            },
        },
        response_convention={
            "resultKind": "download_wrapper",
            "contentPath": "content",
            "contentPolicy": "safe_text_or_metadata_wrapper",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "download",
                "delegation",
                "requestedFormat",
                "requestedLanguage",
                "contentType",
                "contentForm",
                "sizeBytes",
            ),
            preserved_upstream_fields=("content", "contentType", "contentForm", "sizeBytes"),
            disallowed_behavior=(
                "caption_listing",
                "caption_creation",
                "caption_update",
                "caption_deletion",
                "language_ranking",
                "local_translation",
                "summarization",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        usage_notes=(
            "Quota cost: 200. Auth: oauth_required. Provide id for the caption track to download.",
            "Quota cost: 200. Caption download requires eligible access and permission to edit the associated video.",
            "Quota cost: 200. tfmt is optional and supports sbv, scc, srt, ttml, and vtt.",
            "Quota cost: 200. tlang is optional and should be an ISO 639-1-style two-letter language code.",
            "Quota cost: 200. onBehalfOfContentOwner is optional delegation context.",
        ),
        caveats=(
            "Caption download requires eligible OAuth authorization and permission to edit the associated video.",
            "The upstream response is binary file content; public examples and errors must not expose private caption payloads.",
            "tfmt and tlang conversion can fail upstream when the requested format or language cannot be produced.",
        ),
    ),
    _contract(
        resource="captions",
        method="delete",
        description=(
            "Delete caption track. Endpoint: captions.delete. "
            "Quota cost: 50. Auth: oauth_required. Requires caption track id; deletion is destructive."
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        resource_family="captions",
        input_contract={
            "required": ["id"],
            "properties": {
                "id": {"type": "string"},
                "onBehalfOfContentOwner": {"type": "string"},
            },
        },
        response_convention={
            "resultKind": "mutation_acknowledgment",
            "acknowledgmentPath": "delete",
            "successStatus": 204,
            "bodyPolicy": "no_upstream_body",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "delete",
                "status",
                "responseStatus",
                "hasResponseBody",
                "delegation",
            ),
            preserved_upstream_fields=("responseStatus", "hasResponseBody"),
            disallowed_behavior=(
                "caption_listing",
                "caption_download",
                "caption_creation",
                "caption_update",
                "deleted_resource_echo",
                "request_body",
                "undo",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        usage_notes=(
            "Quota cost: 50. Auth: oauth_required. Provide id for the caption track to delete.",
            "Quota cost: 50. captions.delete accepts no request body and returns a 204 No Content acknowledgment.",
            "Quota cost: 50. onBehalfOfContentOwner is optional delegation context.",
        ),
        caveats=(
            "Caption deletion requires eligible OAuth authorization for the target caption track.",
            "Caption deletion is destructive and does not provide undo or recovery behavior.",
            "The upstream success response is 204 No Content; results must not fabricate deleted caption resource fields.",
        ),
    ),
    build_channel_banners_insert_contract(),
    build_channel_sections_insert_contract(),
    build_channel_sections_list_contract(),
    build_channel_sections_update_contract(),
    build_channel_sections_delete_contract(),
    build_channels_list_contract(),
    build_channels_update_contract(),
    build_comments_list_contract(),
    build_comment_threads_list_contract(),
    build_comment_threads_insert_contract(),
    build_comments_insert_contract(),
    build_comments_update_contract(),
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
    build_members_list_contract(),
    build_memberships_levels_list_contract(),
    build_playlist_items_list_contract(),
    build_playlist_items_insert_contract(),
    build_playlist_items_update_contract(),
    build_playlist_items_delete_contract(),
    build_playlists_list_contract(),
    build_playlists_insert_contract(),
    build_playlists_update_contract(),
    build_playlists_delete_contract(),
    build_playlist_images_list_contract(),
    build_playlist_images_insert_contract(),
    build_playlist_images_update_contract(),
    build_playlist_images_delete_contract(),
    build_guide_categories_list_contract(),
    build_i18n_languages_list_contract(),
    build_i18n_regions_list_contract(),
)
