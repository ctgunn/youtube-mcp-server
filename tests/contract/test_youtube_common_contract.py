"""Contract tests for shared YouTube tool contracts."""

import pytest

from mcp_server.tools.youtube_common import (
    AuthMode,
    AvailabilityState,
    ErrorCategory,
    YouTubeToolContractError,
    YouTubeToolContract,
    SHARED_YOUTUBE_HELPER_BOUNDARY,
    ResponseBoundary,
    ResponseBoundaryKind,
    ResponseConvention,
    ResponseKind,
    sanitize_error_details,
    validate_safe_public_metadata,
)


def test_youtube_tool_contract_requires_public_metadata():
    """Require every representative contract to expose MCP-facing metadata."""
    contract = YouTubeToolContract(
        tool_name="videos_list",
        upstream_resource="videos",
        upstream_method="list",
        operation_key="videos.list",
        description="List videos. Quota cost: 1. Auth: api_key or mixed/conditional.",
        auth_mode=AuthMode.MIXED,
        quota_cost=1,
        resource_family="videos",
        input_contract={"required": ["part"], "properties": {"part": {"type": "string"}}},
        response_convention={"resultKind": "list", "itemsPath": "items"},
        response_boundary={"boundaryKind": "near_raw"},
        error_categories=("invalid_request", "quota_exhausted"),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=("Quota cost: 1. Auth: mixed/conditional.",),
    )

    metadata = contract.to_tool_metadata()

    assert metadata["name"] == "videos_list"
    assert metadata["upstream"]["resource"] == "videos"
    assert metadata["upstream"]["method"] == "list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["usageNotes"]
    assert metadata["resourceFamily"] == "videos"


def test_playlist_items_list_contract_uses_existing_resource_family():
    """Expose the concrete ``playlistItems_list`` contract in the playlist-items family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_list_contract

    playlist_items = get_resource_family("playlist_items")
    contract = build_playlist_items_list_contract()
    metadata = contract.to_tool_metadata()

    assert playlist_items.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.layer1_dependency == "mcp_server.integrations.resources.playlist_items"
    assert metadata["name"] == "playlistItems_list"
    assert metadata["resourceFamily"] == "playlist_items"
    assert metadata["upstream"]["operationKey"] == "playlistItems.list"


def test_playlist_items_insert_contract_uses_existing_resource_family():
    """Expose the concrete ``playlistItems_insert`` contract in the playlist-items family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_insert_contract

    playlist_items = get_resource_family("playlist_items")
    contract = build_playlist_items_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlist_items.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.layer1_dependency == "mcp_server.integrations.resources.playlist_items"
    assert metadata["name"] == "playlistItems_insert"
    assert metadata["resourceFamily"] == "playlist_items"
    assert metadata["upstream"]["operationKey"] == "playlistItems.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "playlistItems_list" in metadata_text


def test_playlist_items_update_contract_uses_existing_resource_family():
    """Expose the concrete ``playlistItems_update`` contract in the playlist-items family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_update_contract

    playlist_items = get_resource_family("playlist_items")
    contract = build_playlist_items_update_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlist_items.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.layer1_dependency == "mcp_server.integrations.resources.playlist_items"
    assert metadata["name"] == "playlistItems_update"
    assert metadata["resourceFamily"] == "playlist_items"
    assert metadata["upstream"]["operationKey"] == "playlistItems.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text


def test_playlist_items_delete_contract_uses_existing_resource_family():
    """Expose the concrete ``playlistItems_delete`` contract in the playlist-items family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_delete_contract

    playlist_items = get_resource_family("playlist_items")
    contract = build_playlist_items_delete_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlist_items.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.layer1_dependency == "mcp_server.integrations.resources.playlist_items"
    assert metadata["name"] == "playlistItems_delete"
    assert metadata["resourceFamily"] == "playlist_items"
    assert metadata["upstream"]["operationKey"] == "playlistItems.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert "id" in metadata_text
    assert "destructive" in metadata_text


def test_playlists_family_module_is_importable():
    """Expose the concrete playlists family module for YT-236."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import playlists

    playlists_family = get_resource_family("playlists")

    assert playlists is not None
    assert playlists_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists_family.layer1_dependency == "mcp_server.integrations.resources.playlists"


def test_search_family_module_is_importable():
    """Expose the concrete search family module for YT-240."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import search

    search_family = get_resource_family("search")

    assert search is not None
    assert search_family.definition_location.endswith("src/mcp_server/tools/youtube_common/search.py")
    assert search_family.layer1_dependency == "mcp_server.integrations.resources.search"


def test_subscriptions_family_module_is_importable():
    """Expose the concrete subscriptions family module for YT-241."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import subscriptions

    subscriptions_family = get_resource_family("subscriptions")

    assert subscriptions is not None
    assert subscriptions_family.definition_location.endswith("src/mcp_server/tools/youtube_common/subscriptions.py")
    assert subscriptions_family.layer1_dependency == "mcp_server.integrations.resources.subscriptions"


def test_subscriptions_list_contract_uses_existing_resource_family():
    """Expose the concrete ``subscriptions_list`` contract in the subscriptions family."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import subscriptions
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_list_contract

    subscriptions_family = get_resource_family("subscriptions")
    contract = build_subscriptions_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert subscriptions_family.definition_location.endswith("src/mcp_server/tools/youtube_common/subscriptions.py")
    assert subscriptions_family.layer1_dependency == "mcp_server.integrations.resources.subscriptions"
    assert subscriptions.SUBSCRIPTIONS_LIST_TOOL_NAME == "subscriptions_list"
    assert youtube_common.SUBSCRIPTIONS_LIST_TOOL_NAME == "subscriptions_list"
    assert callable(youtube_common.build_subscriptions_list_tool_descriptor)
    assert metadata["name"] == "subscriptions_list"
    assert metadata["resourceFamily"] == "subscriptions"
    assert metadata["upstream"]["operationKey"] == "subscriptions.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "channelId" in metadata_text
    assert "myRecentSubscribers" in metadata_text
    assert "OAuth" in metadata_text


def test_subscriptions_insert_contract_uses_existing_resource_family():
    """Expose the concrete ``subscriptions_insert`` contract in the subscriptions family."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import subscriptions
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_insert_contract

    subscriptions_family = get_resource_family("subscriptions")
    contract = build_subscriptions_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert subscriptions_family.definition_location.endswith("src/mcp_server/tools/youtube_common/subscriptions.py")
    assert subscriptions_family.layer1_dependency == "mcp_server.integrations.resources.subscriptions"
    assert subscriptions.SUBSCRIPTIONS_INSERT_TOOL_NAME == "subscriptions_insert"
    assert subscriptions.SUBSCRIPTIONS_INSERT_QUOTA_COST == 50
    assert youtube_common.SUBSCRIPTIONS_INSERT_TOOL_NAME == "subscriptions_insert"
    assert youtube_common.SUBSCRIPTIONS_INSERT_QUOTA_COST == 50
    assert callable(youtube_common.build_subscriptions_insert_tool_descriptor)
    assert metadata["name"] == "subscriptions_insert"
    assert metadata["resourceFamily"] == "subscriptions"
    assert metadata["upstream"]["operationKey"] == "subscriptions.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.resourceId.channelId" in metadata_text
    assert "OAuth" in metadata_text


def test_search_list_contract_uses_existing_resource_family():
    """Expose the concrete ``search_list`` contract in the search family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.search import build_search_list_contract

    search_family = get_resource_family("search")
    contract = build_search_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert search_family.definition_location.endswith("src/mcp_server/tools/youtube_common/search.py")
    assert search_family.layer1_dependency == "mcp_server.integrations.resources.search"
    assert metadata["name"] == "search_list"
    assert metadata["resourceFamily"] == "search"
    assert metadata["upstream"]["operationKey"] == "search.list"
    assert metadata["quotaCost"] == 100
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part", "q"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "OAuth" in metadata_text
    assert "API-key" in metadata_text


def test_playlists_list_contract_uses_existing_resource_family():
    """Expose the concrete ``playlists_list`` contract in the playlists family."""
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common.playlists import build_playlists_list_contract

    playlists_family = get_resource_family("playlists")
    contract = build_playlists_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlists_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists_family.layer1_dependency == "mcp_server.integrations.resources.playlists"
    assert metadata["name"] == "playlists_list"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["upstream"]["operationKey"] == "playlists.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "channelId" in metadata_text
    assert "mine" in metadata_text


def test_playlists_insert_contract_uses_existing_resource_family():
    """Expose the concrete ``playlists_insert`` contract in the playlists family."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import playlists
    from mcp_server.tools.youtube_common.playlists import build_playlists_insert_contract

    playlists_family = get_resource_family("playlists")
    contract = build_playlists_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlists_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists_family.layer1_dependency == "mcp_server.integrations.resources.playlists"
    assert playlists.PLAYLISTS_INSERT_TOOL_NAME == "playlists_insert"
    assert youtube_common.PLAYLISTS_INSERT_TOOL_NAME == "playlists_insert"
    assert callable(youtube_common.build_playlists_insert_tool_descriptor)
    assert metadata["name"] == "playlists_insert"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["upstream"]["operationKey"] == "playlists.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.title" in metadata_text


def test_playlists_update_contract_uses_existing_resource_family():
    """Expose the concrete ``playlists_update`` contract in the playlists family."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import playlists
    from mcp_server.tools.youtube_common.playlists import build_playlists_update_contract

    playlists_family = get_resource_family("playlists")
    contract = build_playlists_update_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlists_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists_family.layer1_dependency == "mcp_server.integrations.resources.playlists"
    assert playlists.PLAYLISTS_UPDATE_TOOL_NAME == "playlists_update"
    assert youtube_common.PLAYLISTS_UPDATE_TOOL_NAME == "playlists_update"
    assert callable(youtube_common.build_playlists_update_tool_descriptor)
    assert metadata["name"] == "playlists_update"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["upstream"]["operationKey"] == "playlists.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "body.id" in metadata_text
    assert "body.snippet.title" in metadata_text


def test_playlists_delete_contract_uses_existing_resource_family():
    """Expose the concrete ``playlists_delete`` contract in the playlists family."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import get_resource_family
    from mcp_server.tools.youtube_common import playlists
    from mcp_server.tools.youtube_common.playlists import build_playlists_delete_contract

    playlists_family = get_resource_family("playlists")
    contract = build_playlists_delete_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert playlists_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists_family.layer1_dependency == "mcp_server.integrations.resources.playlists"
    assert playlists.PLAYLISTS_DELETE_TOOL_NAME == "playlists_delete"
    assert youtube_common.PLAYLISTS_DELETE_TOOL_NAME == "playlists_delete"
    assert callable(youtube_common.build_playlists_delete_tool_descriptor)
    assert metadata["name"] == "playlists_delete"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["upstream"]["operationKey"] == "playlists.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["noBodySuccess"] is True
    assert metadata["responseConvention"]["targetFields"] == ["id"]
    assert "id" in metadata_text
    assert "destructive" in metadata_text.lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tool_name", ""),
        ("upstream_resource", ""),
        ("upstream_method", ""),
        ("operation_key", ""),
        ("description", ""),
        ("quota_cost", 0),
        ("resource_family", ""),
        ("input_contract", {}),
        ("response_convention", {}),
        ("response_boundary", {}),
        ("error_categories", ()),
        ("availability_state", None),
        ("usage_notes", ()),
    ],
)


def test_youtube_tool_contract_rejects_missing_required_metadata(field, value):
    """Reject contracts that omit required shared YouTube metadata."""
    kwargs = {
        "tool_name": "videos_list",
        "upstream_resource": "videos",
        "upstream_method": "list",
        "operation_key": "videos.list",
        "description": "List videos. Quota cost: 1. Auth: api_key.",
        "auth_mode": AuthMode.API_KEY,
        "quota_cost": 1,
        "resource_family": "videos",
        "input_contract": {"required": ["part"], "properties": {"part": {"type": "string"}}},
        "response_convention": {"resultKind": "list", "itemsPath": "items"},
        "response_boundary": {"boundaryKind": "near_raw"},
        "error_categories": ("invalid_request",),
        "availability_state": AvailabilityState.ACTIVE,
        "usage_notes": ("Quota cost: 1. Auth: api_key.",),
    }
    kwargs[field] = value

    with pytest.raises(YouTubeToolContractError):
        YouTubeToolContract(**kwargs)


def test_youtube_tool_contract_requires_quota_visible_description_and_notes():
    """Reject metadata that hides quota cost from caller-facing text."""
    kwargs = {
        "tool_name": "videos_list",
        "upstream_resource": "videos",
        "upstream_method": "list",
        "operation_key": "videos.list",
        "description": "List videos. Auth: api_key.",
        "auth_mode": AuthMode.API_KEY,
        "quota_cost": 1,
        "resource_family": "videos",
        "input_contract": {"required": ["part"], "properties": {"part": {"type": "string"}}},
        "response_convention": {"resultKind": "list", "itemsPath": "items"},
        "response_boundary": {"boundaryKind": "near_raw"},
        "error_categories": ("invalid_request",),
        "availability_state": AvailabilityState.ACTIVE,
        "usage_notes": ("Auth: api_key.",),
    }

    with pytest.raises(YouTubeToolContractError):
        YouTubeToolContract(**kwargs)


def test_youtube_tool_contract_rejects_casing_drifted_tool_names():
    """Reject public names derived from snake_case rewrites of upstream methods."""
    with pytest.raises(YouTubeToolContractError):
        YouTubeToolContract(
            tool_name="videos_get_rating",
            upstream_resource="videos",
            upstream_method="get_rating",
            operation_key="videos.get_rating",
            description="Get video rating. Quota cost: 1. Auth: oauth_required.",
            auth_mode=AuthMode.OAUTH_REQUIRED,
            quota_cost=1,
            resource_family="videos",
            input_contract={"required": ["id"], "properties": {"id": {"type": "string"}}},
            response_convention={"resultKind": "lookup", "itemsPath": "items"},
            response_boundary={"boundaryKind": "near_raw"},
            error_categories=("invalid_request",),
            availability_state=AvailabilityState.ACTIVE,
            usage_notes=("Quota cost: 1. Auth: oauth_required.",),
        )


@pytest.mark.parametrize(
    ("kind", "metadata_key"),
    [
        (ResponseKind.LIST, "itemsPath"),
        (ResponseKind.MUTATION_ACKNOWLEDGMENT, "acknowledgment"),
        (ResponseKind.UPLOAD_RESULT, "mediaResult"),
        (ResponseKind.DOWNLOAD_WRAPPER, "contentPolicy"),
        (ResponseKind.LOOKUP, "itemsPath"),
    ],
)


def test_response_conventions_expose_near_raw_result_shapes(kind, metadata_key):
    """Expose near-raw response conventions for representative result kinds."""
    convention = ResponseConvention(
        result_kind=kind,
        items_path="items",
        paging_fields=("nextPageToken",),
        requested_parts=("snippet",),
        wrapper_fields=("endpoint",),
        content_policy="safe_text_or_metadata_wrapper",
    )

    metadata = convention.to_metadata()

    assert metadata["resultKind"] == kind.value
    assert metadata_key in metadata


def test_response_boundary_metadata_classifies_youtube_result_scope():
    """Classify response behavior as endpoint-backed or out of scope."""
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
        allowed_wrapper_fields=("endpoint", "quotaCost"),
        preserved_upstream_fields=("items", "nextPageToken"),
        disallowed_behavior=("ranking", "cross_endpoint_aggregation"),
    )

    metadata = boundary.to_metadata()

    assert metadata["boundaryKind"] == "lightly_reshaped"
    assert metadata["allowedWrapperFields"] == ["endpoint", "quotaCost"]
    assert metadata["preservedUpstreamFields"] == ["items", "nextPageToken"]
    assert metadata["disallowedBehavior"] == ["ranking", "cross_endpoint_aggregation"]


def test_response_boundary_rejects_empty_out_of_scope_explanation():
    """Require out-of-scope examples to document disallowed behavior."""
    with pytest.raises(YouTubeToolContractError):
        ResponseBoundary(boundary_kind=ResponseBoundaryKind.OUT_OF_SCOPE).to_metadata()


def test_error_categories_cover_shared_youtube_failures():
    """Keep shared error categories stable for endpoint-backed tools."""
    assert {category.value for category in ErrorCategory} == {
        "authentication_failed",
        "authorization_failed",
        "quota_exhausted",
        "resource_not_found",
        "invalid_request",
        "deprecated_endpoint",
        "endpoint_unavailable",
        "upstream_failure",
    }


def test_sanitize_error_details_removes_secret_bearing_fields():
    """Strip unsafe diagnostic fields from caller-facing error details."""
    safe = sanitize_error_details(
        {
            "toolName": "videos_list",
            "api_key": "secret",
            "oauthToken": "secret",
            "stackTrace": "traceback",
            "raw_media_payload": b"secret",
            "parameter": "part",
        }
    )

    assert safe == {"toolName": "videos_list", "parameter": "part"}


def test_validate_safe_public_metadata_rejects_secret_bearing_details():
    """Reject unsafe metadata before exposing it through discovery surfaces."""
    with pytest.raises(YouTubeToolContractError):
        validate_safe_public_metadata(
            {
                "name": "videos_list",
                "quotaCost": 1,
                "apiKey": "secret",
                "nested": {"stackTrace": "traceback"},
                "media": ["safe", {"signedUrl": "https://example.invalid/signed"}],
            }
        )

    safe = validate_safe_public_metadata(
        {
            "name": "videos_list",
            "quotaCost": 1,
            "upstream": {"resource": "videos", "method": "list"},
        }
    )

    assert safe["upstream"]["resource"] == "videos"


def test_playlist_images_delete_public_contract_uses_existing_resource_family():
    """Keep ``playlistImages_delete`` anchored to the shared playlist-images family."""
    from mcp_server.tools.youtube_common import get_resource_family

    playlist_images = get_resource_family("playlist_images")

    assert playlist_images.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.handler_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.schema_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")


def test_captions_update_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, and update metadata for ``captions_update``."""
    from mcp_server.tools.youtube_common.captions import build_captions_update_contract

    metadata = build_captions_update_contract().to_tool_metadata()

    assert metadata["name"] == "captions_update"
    assert metadata["upstream"]["operationKey"] == "captions.update"
    assert metadata["quotaCost"] == 450
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "media" in metadata["inputContract"]["properties"]
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_playlist_images_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, selector, and paging metadata for ``playlistImages_list``."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_list_contract

    metadata = build_playlist_images_list_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "playlistImages_list"
    assert metadata["upstream"]["operationKey"] == "playlistImages.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["selectorFields"] == ["playlistId", "id"]
    assert metadata["responseConvention"]["pagingFields"] == [
        "pageToken",
        "maxResults",
        "nextPageToken",
        "prevPageToken",
        "pageInfo",
    ]
    assert "playlistId" in metadata_text
    assert "id" in metadata_text
    assert "pageToken" in metadata_text
    assert "maxResults" in metadata_text
    assert "token" not in str(metadata).lower().replace("pagetoken", "").replace("nextpagetoken", "")
    assert "apiKey" not in str(metadata)


def test_i18n_languages_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, and active metadata for ``i18nLanguages_list``."""
    from mcp_server.tools.youtube_common.localization import build_i18n_languages_list_contract

    metadata = build_i18n_languages_list_contract().to_tool_metadata()

    assert metadata["name"] == "i18nLanguages_list"
    assert metadata["upstream"]["operationKey"] == "i18nLanguages.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]


def test_i18n_regions_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, and active metadata for ``i18nRegions_list``."""
    from mcp_server.tools.youtube_common.localization import build_i18n_regions_list_contract

    metadata = build_i18n_regions_list_contract().to_tool_metadata()

    assert metadata["name"] == "i18nRegions_list"
    assert metadata["upstream"]["operationKey"] == "i18nRegions.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert "apiKey" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_comments_update_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, and update metadata for ``comments_update``."""
    from mcp_server.tools.youtube_common.comments import build_comments_update_contract

    metadata = build_comments_update_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_update"
    assert metadata["upstream"]["operationKey"] == "comments.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "body.id" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "read-only" in metadata_text
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_comments_update_representative_metadata_aligns_with_shared_safety_rules():
    """Keep public representative metadata aligned with concrete update safety."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
    from mcp_server.tools.youtube_common.comments import build_comments_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_update"
    ].to_tool_metadata()
    concrete = build_comments_update_contract().to_tool_metadata()
    representative_text = " ".join(
        [representative["description"], *representative["usageNotes"], *representative["caveats"]]
    )

    assert representative["quotaCost"] == concrete["quotaCost"] == 50
    assert representative["authMode"] == concrete["authMode"] == "oauth_required"
    assert representative["availabilityState"] == concrete["availabilityState"] == "active"
    assert representative["inputContract"]["required"] == ["part", "body"]
    assert representative["responseConvention"]["resultKind"] == "updated_resource"
    assert representative["responseConvention"]["supportedWritableParts"] == ["snippet"]
    assert "body.id" in representative_text
    assert "body.snippet.textOriginal" in representative_text
    assert "read-only" in representative_text
    assert "oauthToken" not in str(representative)
    assert "apiKey" not in str(representative)


def test_comments_set_moderation_status_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, status, and optional-flag metadata."""
    from mcp_server.tools.youtube_common.comments import build_comments_set_moderation_status_contract

    metadata = build_comments_set_moderation_status_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_setModerationStatus"
    assert metadata["upstream"]["operationKey"] == "comments.setModerationStatus"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id", "moderationStatus"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert "heldForReview" in metadata_text
    assert "published" in metadata_text
    assert "rejected" in metadata_text
    assert "banAuthor" in metadata_text
    assert "request body" in metadata_text
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_comments_set_moderation_status_representative_metadata_aligns_with_shared_safety_rules():
    """Keep public representative metadata aligned with concrete moderation safety."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
    from mcp_server.tools.youtube_common.comments import build_comments_set_moderation_status_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_setModerationStatus"
    ].to_tool_metadata()
    concrete = build_comments_set_moderation_status_contract().to_tool_metadata()
    representative_text = " ".join(
        [representative["description"], *representative["usageNotes"], *representative["caveats"]]
    )

    assert representative["quotaCost"] == concrete["quotaCost"] == 50
    assert representative["authMode"] == concrete["authMode"] == "oauth_required"
    assert representative["availabilityState"] == concrete["availabilityState"] == "active"
    assert representative["inputContract"]["required"] == ["id", "moderationStatus"]
    assert representative["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert representative["responseConvention"]["successStatus"] == 204
    assert "heldForReview" in representative_text
    assert "published" in representative_text
    assert "rejected" in representative_text
    assert "banAuthor" in representative_text
    assert "oauthToken" not in str(representative)
    assert "apiKey" not in str(representative)


def test_comments_delete_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, destructive delete, and no-body metadata."""
    from mcp_server.tools.youtube_common.comments import build_comments_delete_contract

    metadata = build_comments_delete_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_delete"
    assert metadata["upstream"]["operationKey"] == "comments.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_comments_delete_representative_metadata_aligns_with_shared_safety_rules():
    """Keep public representative metadata aligned with concrete delete safety."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
    from mcp_server.tools.youtube_common.comments import build_comments_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_delete"
    ].to_tool_metadata()
    concrete = build_comments_delete_contract().to_tool_metadata()
    representative_text = " ".join(
        [representative["description"], *representative["usageNotes"], *representative["caveats"]]
    )

    assert representative["quotaCost"] == concrete["quotaCost"] == 50
    assert representative["authMode"] == concrete["authMode"] == "oauth_required"
    assert representative["availabilityState"] == concrete["availabilityState"] == "active"
    assert representative["inputContract"]["required"] == ["id"]
    assert representative["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert representative["responseConvention"]["successStatus"] == 204
    assert "destructive" in representative_text.lower()
    assert "request body" in representative_text
    assert "oauthToken" not in str(representative)
    assert "apiKey" not in str(representative)


def test_comments_insert_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, and reply metadata for ``comments_insert``."""
    from mcp_server.tools.youtube_common.comments import build_comments_insert_contract

    metadata = build_comments_insert_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_insert"
    assert metadata["upstream"]["operationKey"] == "comments.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert "body.snippet.parentId" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "commentThreads.insert" in metadata_text
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_captions_download_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, permission, and conversion metadata for ``captions_download``."""
    from mcp_server.tools.youtube_common.captions import build_captions_download_contract

    metadata = build_captions_download_contract().to_tool_metadata()

    assert metadata["name"] == "captions_download"
    assert metadata["upstream"]["operationKey"] == "captions.download"
    assert metadata["quotaCost"] == 200
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "tfmt" in metadata["inputContract"]["properties"]
    assert "tlang" in metadata["inputContract"]["properties"]
    assert any("permission" in note.lower() for note in metadata["usageNotes"])
    assert any("tfmt" in note for note in metadata["usageNotes"])
    assert any("tlang" in note for note in metadata["usageNotes"])
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)


def test_captions_delete_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, destructive delete, and no-body metadata."""
    from mcp_server.tools.youtube_common.captions import build_captions_delete_contract

    metadata = build_captions_delete_contract().to_tool_metadata()

    assert metadata["name"] == "captions_delete"
    assert metadata["upstream"]["operationKey"] == "captions.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert any("destructive" in caveat.lower() for caveat in metadata["caveats"])
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)
    assert "raw_media" not in str(metadata)


def test_channel_sections_delete_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, destructive delete, and acknowledgment metadata."""
    from mcp_server.tools.youtube_common.channel_sections import build_channel_sections_delete_contract

    metadata = build_channel_sections_delete_contract().to_tool_metadata()

    assert metadata["name"] == "channelSections_delete"
    assert metadata["upstream"]["operationKey"] == "channelSections.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["bodyPolicy"] == "preserve_returned_body_or_acknowledge_no_body"
    assert any("destructive" in caveat.lower() for caveat in metadata["caveats"])
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)
    assert "raw_media" not in str(metadata)


def test_comments_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, selector, pagination, and list metadata."""
    from mcp_server.tools.youtube_common.comments import build_comments_list_contract

    metadata = build_comments_list_contract().to_tool_metadata()

    assert metadata["name"] == "comments_list"
    assert metadata["upstream"]["operationKey"] == "comments.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert any("parentId" in note for note in metadata["usageNotes"])
    assert any("maxResults" in caveat for caveat in metadata["caveats"])
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_members_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, owner access, and list metadata."""
    from mcp_server.tools.youtube_common.members import build_members_list_contract

    metadata = build_members_list_contract().to_tool_metadata()

    assert metadata["name"] == "members_list"
    assert metadata["upstream"]["operationKey"] == "members.list"
    assert metadata["quotaCost"] == 2
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "mode"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert metadata["inputContract"]["properties"]["mode"]["enum"] == ["all_current", "updates"]
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert any("owner" in note.lower() for note in metadata["usageNotes"])
    assert any("channel-membership" in caveat.lower() for caveat in metadata["caveats"])
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_memberships_levels_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, owner access, and membership-level metadata."""
    from mcp_server.tools.youtube_common.memberships_levels import build_memberships_levels_list_contract

    metadata = build_memberships_levels_list_contract().to_tool_metadata()

    assert metadata["name"] == "membershipsLevels_list"
    assert metadata["upstream"]["operationKey"] == "membershipsLevels.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "pageToken" not in metadata["inputContract"]["properties"]
    assert "maxResults" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert any("owner" in note.lower() for note in metadata["usageNotes"])
    assert any("channel-membership" in caveat.lower() for caveat in metadata["caveats"])
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_comment_threads_list_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, selector, pagination, and list metadata."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_list_contract

    metadata = build_comment_threads_list_contract().to_tool_metadata()

    assert metadata["name"] == "commentThreads_list"
    assert metadata["upstream"]["operationKey"] == "commentThreads.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"videoId", "allThreadsRelatedToChannelId", "id", "maxResults", "pageToken", "textFormat"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert any("videoId" in note for note in metadata["usageNotes"])
    assert any("allThreadsRelatedToChannelId" in note for note in metadata["usageNotes"])
    assert any("maxResults" in caveat for caveat in metadata["caveats"])
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_commentThreads_insert_public_metadata_is_safe_and_complete():
    """Expose safe quota, OAuth, target, and top-level body metadata."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_insert_contract

    metadata = build_comment_threads_insert_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "commentThreads_insert"
    assert metadata["upstream"]["operationKey"] == "commentThreads.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.channelId" in metadata_text
    assert "body.snippet.videoId" in metadata_text
    assert "body.snippet.topLevelComment.snippet.textOriginal" in metadata_text
    assert "comments_insert" in metadata_text
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_commentThreads_insert_shared_metadata_exposes_examples_and_safe_boundaries():
    """Keep shared metadata complete enough for clients to choose this write tool safely."""
    from mcp_server.tools.youtube_common.comment_threads import (
        COMMENT_THREADS_INSERT_CALLER_EXAMPLES,
        build_comment_threads_insert_contract,
    )

    metadata = build_comment_threads_insert_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])
    example_names = {example["name"] for example in COMMENT_THREADS_INSERT_CALLER_EXAMPLES}

    assert {"invalid_target_context", "unsupported_option"}.issubset(example_names)
    assert "Quota cost: 50" in metadata["description"]
    assert any("Auth: oauth_required" in note for note in metadata["usageNotes"])
    assert "onBehalfOfContentOwner" in metadata_text
    assert "near_raw" in str(metadata["responseBoundary"])
    assert "generated responses" in metadata_text
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_channel_banners_insert_public_metadata_is_safe_and_complete():
    """Expose safe quota, auth, media, URL, and activation-boundary metadata."""
    from mcp_server.tools.youtube_common.channel_banners import build_channel_banners_insert_contract

    metadata = build_channel_banners_insert_contract().to_tool_metadata()

    assert metadata["name"] == "channelBanners_insert"
    assert metadata["upstream"]["operationKey"] == "channelBanners.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "media_constrained"
    assert metadata["inputContract"]["required"] == ["media"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["returnedUrlField"] == "url"
    assert metadata["responseConvention"]["activationBoundary"] == "channels.update"
    assert any("6 MB" in note for note in metadata["usageNotes"])
    assert any("16:9" in note for note in metadata["usageNotes"])
    assert any("channels.update" in note for note in metadata["usageNotes"])
    assert "token" not in str(metadata).lower()
    assert "apiKey" not in str(metadata)
    assert "raw_media" not in str(metadata)
    assert "content" not in str(metadata["responseBoundary"]).lower()


def test_shared_helper_boundary_keeps_endpoint_facts_in_resource_families():
    """Document which concerns are shared and which stay endpoint-specific."""
    assert "naming" in SHARED_YOUTUBE_HELPER_BOUNDARY["shared"]
    assert "auth_quota_metadata" in SHARED_YOUTUBE_HELPER_BOUNDARY["shared"]
    assert "upstream_execution" in SHARED_YOUTUBE_HELPER_BOUNDARY["endpoint_family"]
    assert "media_transfer" in SHARED_YOUTUBE_HELPER_BOUNDARY["endpoint_family"]
