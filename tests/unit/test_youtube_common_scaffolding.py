"""Unit tests for shared YouTube scaffolding helpers."""


def test_youtube_package_imports():
    """Confirm the shared YouTube package can be imported."""
    import mcp_server.tools.youtube_common as youtube_common

    assert youtube_common is not None


def test_derive_tool_name_uses_resource_method_pattern():
    """Derive resource-grouped public names from upstream resource methods."""
    from mcp_server.tools.youtube_common import derive_tool_name

    assert derive_tool_name("videos", "list") == "videos_list"
    assert derive_tool_name("comments", "setModerationStatus") == "comments_setModerationStatus"
    assert derive_tool_name("videos", "getRating") == "videos_getRating"


def test_derive_tool_name_covers_representative_youtube_inventory_names():
    """Derive deterministic names for representative YouTube endpoints."""
    from mcp_server.tools.youtube_common import derive_tool_name

    examples = {
        ("videos", "list"): "videos_list",
        ("playlists", "insert"): "playlists_insert",
        ("captions", "insert"): "captions_insert",
        ("comments", "setModerationStatus"): "comments_setModerationStatus",
        ("videos", "getRating"): "videos_getRating",
        ("videos", "reportAbuse"): "videos_reportAbuse",
        ("playlistItems", "list"): "playlistItems_list",
        ("captions", "download"): "captions_download",
        ("search", "list"): "search_list",
        ("guideCategories", "list"): "guideCategories_list",
        ("i18nLanguages", "list"): "i18nLanguages_list",
        ("watermarks", "unset"): "watermarks_unset",
    }

    assert {pair: derive_tool_name(*pair) for pair in examples} == examples


def test_derive_tool_name_rejects_redundant_youtube_prefix():
    """Reject resource names that would create redundant public prefixes."""
    import pytest

    from mcp_server.tools.youtube_common import YouTubeToolContractError, derive_tool_name

    with pytest.raises(YouTubeToolContractError):
        derive_tool_name("youtube_videos", "list")


def test_derive_tool_name_rejects_casing_drifted_method_names():
    """Reject snake_case rewrites of official upstream method names."""
    import pytest

    from mcp_server.tools.youtube_common import YouTubeToolContractError, derive_tool_name

    with pytest.raises(YouTubeToolContractError):
        derive_tool_name("videos", "get_rating")


def test_input_convention_builds_schema_metadata():
    """Represent near-raw YouTube tool input mapping as schema metadata."""
    from mcp_server.tools.youtube_common import InputConvention

    convention = InputConvention(
        required_fields=("part",),
        optional_fields=("pageToken", "maxResults"),
        selector_groups=(("id", "mine"),),
        part_fields=("snippet", "contentDetails"),
        pagination_fields=("pageToken", "maxResults"),
        request_body_fields=("snippet",),
        media_fields=("media",),
        delegation_fields=("onBehalfOfContentOwner",),
    )

    schema = convention.to_schema()

    assert schema["type"] == "object"
    assert schema["required"] == ["part"]
    assert "oneOf" in schema
    assert schema["properties"]["pageToken"]["type"] == "string"
    assert convention.has_media_inputs is True


def test_response_boundary_builds_metadata():
    """Represent response-boundary metadata for shared YouTube standards."""
    from mcp_server.tools.youtube_common import ResponseBoundary, ResponseBoundaryKind

    metadata = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        preserved_upstream_fields=("items", "nextPageToken"),
    ).to_metadata()

    assert metadata == {
        "boundaryKind": "near_raw",
        "allowedWrapperFields": [],
        "preservedUpstreamFields": ["items", "nextPageToken"],
        "disallowedBehavior": [],
    }


def test_required_youtube_resource_families_have_placement_metadata():
    """Expose resource-family placement rules for later endpoint slices."""
    from mcp_server.tools.youtube_common import REQUIRED_YOUTUBE_RESOURCE_FAMILIES, get_resource_family

    assert {"activities", "captions", "videos", "watermarks"}.issubset(REQUIRED_YOUTUBE_RESOURCE_FAMILIES)

    videos = get_resource_family("videos")

    assert videos.family_name == "videos"
    assert videos.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert "tests/contract" in videos.test_locations["contract"]
    assert videos.layer1_dependency == "mcp_server.integrations.resources.videos"


def test_videos_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videos_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import videos

    videos_family = youtube_common.get_resource_family("videos")

    assert videos_family.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert videos.VIDEOS_INSERT_TOOL_NAME == "videos_insert"
    assert videos.VIDEOS_INSERT_QUOTA_COST == 1600
    assert youtube_common.VIDEOS_INSERT_TOOL_NAME == "videos_insert"
    assert youtube_common.VIDEOS_INSERT_QUOTA_COST == 1600
    assert youtube_common.VIDEOS_INSERT_UPLOAD_MODES == ("multipart", "resumable")
    assert callable(videos.build_videos_insert_contract)
    assert callable(videos.build_videos_insert_handler)
    assert callable(videos.build_videos_insert_tool_descriptor)
    assert callable(videos.map_videos_insert_result)
    assert callable(videos.validate_videos_insert_arguments)
    assert youtube_common.VideosInsertToolError is videos.VideosInsertToolError


def test_videos_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videos_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import videos

    videos_family = youtube_common.get_resource_family("videos")

    assert videos_family.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert videos.VIDEOS_UPDATE_TOOL_NAME == "videos_update"
    assert videos.VIDEOS_UPDATE_QUOTA_COST == 50
    assert youtube_common.VIDEOS_UPDATE_TOOL_NAME == "videos_update"
    assert youtube_common.VIDEOS_UPDATE_QUOTA_COST == 50
    assert callable(videos.build_videos_update_contract)
    assert callable(videos.build_videos_update_handler)
    assert callable(videos.build_videos_update_tool_descriptor)
    assert callable(videos.map_videos_update_result)
    assert callable(videos.validate_videos_update_arguments)
    assert youtube_common.VideosUpdateToolError is videos.VideosUpdateToolError


def test_videos_rate_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videos_rate`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import videos

    videos_family = youtube_common.get_resource_family("videos")

    assert videos_family.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert videos.VIDEOS_RATE_TOOL_NAME == "videos_rate"
    assert videos.VIDEOS_RATE_QUOTA_COST == 50
    assert youtube_common.VIDEOS_RATE_TOOL_NAME == "videos_rate"
    assert youtube_common.VIDEOS_RATE_QUOTA_COST == 50
    assert youtube_common.VIDEOS_RATE_INPUT_SCHEMA["properties"]["rating"]["enum"] == ["like", "dislike", "none"]
    assert callable(videos.build_videos_rate_contract)
    assert callable(videos.build_videos_rate_handler)
    assert callable(videos.build_videos_rate_tool_descriptor)
    assert callable(videos.map_videos_rate_result)
    assert callable(videos.validate_videos_rate_arguments)
    assert youtube_common.VideosRateToolError is videos.VideosRateToolError


def test_videos_get_rating_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videos_getRating`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import videos

    videos_family = youtube_common.get_resource_family("videos")

    assert videos_family.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert videos.VIDEOS_GET_RATING_TOOL_NAME == "videos_getRating"
    assert videos.VIDEOS_GET_RATING_QUOTA_COST == 1
    assert youtube_common.VIDEOS_GET_RATING_TOOL_NAME == "videos_getRating"
    assert youtube_common.VIDEOS_GET_RATING_QUOTA_COST == 1
    assert youtube_common.VIDEOS_GET_RATING_INPUT_SCHEMA["properties"]["id"]["type"] == "string"
    assert callable(videos.build_videos_get_rating_contract)
    assert callable(videos.build_videos_get_rating_handler)
    assert callable(videos.build_videos_get_rating_tool_descriptor)
    assert callable(videos.map_videos_get_rating_result)
    assert callable(videos.validate_videos_get_rating_arguments)
    assert youtube_common.VideosGetRatingToolError is videos.VideosGetRatingToolError


def test_playlists_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete playlists family placement for YT-236."""
    from mcp_server.tools.youtube_common import get_resource_family

    playlists = get_resource_family("playlists")

    assert playlists.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.handler_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.schema_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.layer1_dependency == "mcp_server.integrations.resources.playlists"


def test_playlists_insert_uses_existing_playlists_resource_family():
    """Keep ``playlists_insert`` in the concrete playlists family module."""
    from mcp_server.tools.youtube_common import get_resource_family

    playlists = get_resource_family("playlists")

    assert playlists.family_name == "playlists"
    assert playlists.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.handler_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.schema_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.layer1_dependency == "mcp_server.integrations.resources.playlists"


def test_playlists_update_uses_existing_playlists_resource_family():
    """Keep ``playlists_update`` in the concrete playlists family module."""
    from mcp_server.tools.youtube_common import get_resource_family

    playlists = get_resource_family("playlists")

    assert playlists.family_name == "playlists"
    assert playlists.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.handler_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.schema_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.layer1_dependency == "mcp_server.integrations.resources.playlists"


def test_playlists_delete_uses_existing_playlists_resource_family():
    """Keep ``playlists_delete`` in the concrete playlists family module."""
    from mcp_server.tools.youtube_common import get_resource_family

    playlists = get_resource_family("playlists")

    assert playlists.family_name == "playlists"
    assert playlists.definition_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.handler_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.schema_location.endswith("src/mcp_server/tools/youtube_common/playlists.py")
    assert playlists.layer1_dependency == "mcp_server.integrations.resources.playlists"


def test_search_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete search family placement for YT-240."""
    from mcp_server.tools.youtube_common import get_resource_family

    search = get_resource_family("search")

    assert search.family_name == "search"
    assert search.definition_location.endswith("src/mcp_server/tools/youtube_common/search.py")
    assert search.handler_location.endswith("src/mcp_server/tools/youtube_common/search.py")
    assert search.schema_location.endswith("src/mcp_server/tools/youtube_common/search.py")
    assert search.layer1_dependency == "mcp_server.integrations.resources.search"


def test_search_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``search_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import search

    assert search.SEARCH_LIST_TOOL_NAME == "search_list"
    assert youtube_common.SEARCH_LIST_TOOL_NAME == "search_list"
    assert youtube_common.SEARCH_LIST_QUOTA_COST == 100
    assert callable(search.build_search_list_contract)
    assert callable(youtube_common.build_search_list_tool_descriptor)


def test_activities_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete activities family placement for YT-203."""
    from mcp_server.tools.youtube_common import get_resource_family

    activities = get_resource_family("activities")

    assert activities.definition_location.endswith("src/mcp_server/tools/youtube_common/activities.py")
    assert activities.handler_location.endswith("src/mcp_server/tools/youtube_common/activities.py")
    assert activities.schema_location.endswith("src/mcp_server/tools/youtube_common/activities.py")


def test_captions_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete captions family placement for YT-204."""
    from mcp_server.tools.youtube_common import get_resource_family

    captions = get_resource_family("captions")

    assert captions.definition_location.endswith("src/mcp_server/tools/youtube_common/captions.py")
    assert captions.handler_location.endswith("src/mcp_server/tools/youtube_common/captions.py")
    assert captions.schema_location.endswith("src/mcp_server/tools/youtube_common/captions.py")


def test_channels_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete channels family placement for YT-210."""
    from mcp_server.tools.youtube_common import get_resource_family

    channels = get_resource_family("channels")

    assert channels.definition_location.endswith("src/mcp_server/tools/youtube_common/channels.py")
    assert channels.handler_location.endswith("src/mcp_server/tools/youtube_common/channels.py")
    assert channels.schema_location.endswith("src/mcp_server/tools/youtube_common/channels.py")


def test_channels_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``channels_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import channels

    assert channels.CHANNELS_UPDATE_TOOL_NAME == "channels_update"
    assert youtube_common.CHANNELS_UPDATE_TOOL_NAME == "channels_update"
    assert youtube_common.CHANNELS_UPDATE_QUOTA_COST == 50
    assert callable(channels.build_channels_update_contract)
    assert callable(youtube_common.build_channels_update_tool_descriptor)


def test_channel_sections_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete channel-sections family placement for YT-212."""
    from mcp_server.tools.youtube_common import get_resource_family

    channel_sections = get_resource_family("channel_sections")

    assert channel_sections.definition_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")
    assert channel_sections.handler_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")
    assert channel_sections.schema_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")


def test_channel_sections_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``channelSections_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import channel_sections

    assert channel_sections.CHANNEL_SECTIONS_LIST_TOOL_NAME == "channelSections_list"
    assert youtube_common.CHANNEL_SECTIONS_LIST_TOOL_NAME == "channelSections_list"
    assert youtube_common.CHANNEL_SECTIONS_LIST_QUOTA_COST == 1
    assert callable(channel_sections.build_channel_sections_list_contract)
    assert callable(youtube_common.build_channel_sections_list_tool_descriptor)


def test_channel_sections_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``channelSections_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import channel_sections

    channel_sections_family = youtube_common.get_resource_family("channel_sections")

    assert channel_sections_family.definition_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")
    assert channel_sections.CHANNEL_SECTIONS_INSERT_TOOL_NAME == "channelSections_insert"
    assert youtube_common.CHANNEL_SECTIONS_INSERT_TOOL_NAME == "channelSections_insert"
    assert youtube_common.CHANNEL_SECTIONS_INSERT_QUOTA_COST == 50
    assert callable(channel_sections.build_channel_sections_insert_contract)
    assert callable(youtube_common.build_channel_sections_insert_tool_descriptor)


def test_channel_sections_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``channelSections_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import channel_sections

    channel_sections_family = youtube_common.get_resource_family("channel_sections")

    assert channel_sections_family.definition_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")
    assert channel_sections.CHANNEL_SECTIONS_UPDATE_TOOL_NAME == "channelSections_update"
    assert youtube_common.CHANNEL_SECTIONS_UPDATE_TOOL_NAME == "channelSections_update"
    assert youtube_common.CHANNEL_SECTIONS_UPDATE_QUOTA_COST == 50
    assert callable(channel_sections.build_channel_sections_update_contract)
    assert callable(youtube_common.build_channel_sections_update_tool_descriptor)


def test_channel_sections_delete_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``channelSections_delete`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import channel_sections

    channel_sections_family = youtube_common.get_resource_family("channel_sections")

    assert channel_sections_family.definition_location.endswith("src/mcp_server/tools/youtube_common/channel_sections.py")
    assert channel_sections.CHANNEL_SECTIONS_DELETE_TOOL_NAME == "channelSections_delete"
    assert youtube_common.CHANNEL_SECTIONS_DELETE_TOOL_NAME == "channelSections_delete"
    assert youtube_common.CHANNEL_SECTIONS_DELETE_QUOTA_COST == 50
    assert callable(channel_sections.build_channel_sections_delete_contract)
    assert callable(youtube_common.build_channel_sections_delete_tool_descriptor)


def test_comments_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``comments_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comments

    comments_family = youtube_common.get_resource_family("comments")

    assert comments_family.definition_location.endswith("src/mcp_server/tools/youtube_common/comments.py")
    assert comments.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert youtube_common.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert youtube_common.COMMENTS_LIST_QUOTA_COST == 1
    assert callable(comments.build_comments_list_contract)
    assert callable(youtube_common.build_comments_list_tool_descriptor)


def test_members_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``members_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import members

    members_family = youtube_common.get_resource_family("members")

    assert members_family.definition_location.endswith("src/mcp_server/tools/youtube_common/members.py")
    assert members.MEMBERS_LIST_TOOL_NAME == "members_list"
    assert youtube_common.MEMBERS_LIST_TOOL_NAME == "members_list"
    assert youtube_common.MEMBERS_LIST_QUOTA_COST == 2
    assert callable(members.build_members_list_contract)
    assert callable(youtube_common.build_members_list_tool_descriptor)


def test_memberships_levels_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``membershipsLevels_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import memberships_levels

    memberships_levels_family = youtube_common.get_resource_family("memberships_levels")

    assert memberships_levels_family.definition_location.endswith(
        "src/mcp_server/tools/youtube_common/memberships_levels.py"
    )
    assert memberships_levels.MEMBERSHIPS_LEVELS_LIST_TOOL_NAME == "membershipsLevels_list"
    assert youtube_common.MEMBERSHIPS_LEVELS_LIST_TOOL_NAME == "membershipsLevels_list"
    assert youtube_common.MEMBERSHIPS_LEVELS_LIST_QUOTA_COST == 1
    assert callable(memberships_levels.build_memberships_levels_list_contract)
    assert callable(youtube_common.build_memberships_levels_list_tool_descriptor)


def test_playlist_images_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistImages_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_images

    playlist_images_family = youtube_common.get_resource_family("playlist_images")

    assert playlist_images_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert youtube_common.PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert youtube_common.PLAYLIST_IMAGES_LIST_QUOTA_COST == 1
    assert callable(playlist_images.build_playlist_images_list_contract)
    assert callable(youtube_common.build_playlist_images_list_tool_descriptor)


def test_playlist_items_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistItems_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_items

    playlist_items_family = youtube_common.get_resource_family("playlist_items")

    assert playlist_items_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.PLAYLIST_ITEMS_LIST_TOOL_NAME == "playlistItems_list"
    assert youtube_common.PLAYLIST_ITEMS_LIST_TOOL_NAME == "playlistItems_list"
    assert youtube_common.PLAYLIST_ITEMS_LIST_QUOTA_COST == 1
    assert callable(playlist_items.build_playlist_items_list_contract)
    assert callable(youtube_common.build_playlist_items_list_tool_descriptor)


def test_playlist_items_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistItems_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_items

    playlist_items_family = youtube_common.get_resource_family("playlist_items")

    assert playlist_items_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.PLAYLIST_ITEMS_INSERT_TOOL_NAME == "playlistItems_insert"
    assert youtube_common.PLAYLIST_ITEMS_INSERT_TOOL_NAME == "playlistItems_insert"
    assert youtube_common.PLAYLIST_ITEMS_INSERT_QUOTA_COST == 50
    assert callable(playlist_items.build_playlist_items_insert_contract)
    assert callable(youtube_common.build_playlist_items_insert_tool_descriptor)


def test_playlist_items_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistItems_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_items

    playlist_items_family = youtube_common.get_resource_family("playlist_items")

    assert playlist_items_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.PLAYLIST_ITEMS_UPDATE_TOOL_NAME == "playlistItems_update"
    assert youtube_common.PLAYLIST_ITEMS_UPDATE_TOOL_NAME == "playlistItems_update"
    assert youtube_common.PLAYLIST_ITEMS_UPDATE_QUOTA_COST == 50
    assert callable(playlist_items.build_playlist_items_update_contract)
    assert callable(youtube_common.build_playlist_items_update_tool_descriptor)


def test_playlist_items_delete_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistItems_delete`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_items

    playlist_items_family = youtube_common.get_resource_family("playlist_items")

    assert playlist_items_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_items.py")
    assert playlist_items.PLAYLIST_ITEMS_DELETE_TOOL_NAME == "playlistItems_delete"
    assert youtube_common.PLAYLIST_ITEMS_DELETE_TOOL_NAME == "playlistItems_delete"
    assert youtube_common.PLAYLIST_ITEMS_DELETE_QUOTA_COST == 50
    assert callable(playlist_items.build_playlist_items_delete_contract)
    assert callable(youtube_common.build_playlist_items_delete_tool_descriptor)


def test_playlist_images_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistImages_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_images

    playlist_images_family = youtube_common.get_resource_family("playlist_images")

    assert playlist_images_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.PLAYLIST_IMAGES_INSERT_TOOL_NAME == "playlistImages_insert"
    assert youtube_common.PLAYLIST_IMAGES_INSERT_TOOL_NAME == "playlistImages_insert"
    assert youtube_common.PLAYLIST_IMAGES_INSERT_QUOTA_COST == 50
    assert callable(playlist_images.build_playlist_images_insert_contract)
    assert callable(youtube_common.build_playlist_images_insert_tool_descriptor)


def test_playlist_images_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistImages_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_images

    playlist_images_family = youtube_common.get_resource_family("playlist_images")

    assert playlist_images_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.PLAYLIST_IMAGES_UPDATE_TOOL_NAME == "playlistImages_update"
    assert youtube_common.PLAYLIST_IMAGES_UPDATE_TOOL_NAME == "playlistImages_update"
    assert youtube_common.PLAYLIST_IMAGES_UPDATE_QUOTA_COST == 50
    assert callable(playlist_images.build_playlist_images_update_contract)
    assert callable(youtube_common.build_playlist_images_update_tool_descriptor)


def test_playlist_images_delete_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``playlistImages_delete`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import playlist_images

    playlist_images_family = youtube_common.get_resource_family("playlist_images")

    assert playlist_images_family.definition_location.endswith("src/mcp_server/tools/youtube_common/playlist_images.py")
    assert playlist_images.PLAYLIST_IMAGES_DELETE_TOOL_NAME == "playlistImages_delete"
    assert youtube_common.PLAYLIST_IMAGES_DELETE_TOOL_NAME == "playlistImages_delete"
    assert youtube_common.PLAYLIST_IMAGES_DELETE_QUOTA_COST == 50
    assert callable(playlist_images.build_playlist_images_delete_contract)
    assert callable(youtube_common.build_playlist_images_delete_tool_descriptor)


def test_comment_threads_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``commentThreads_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comment_threads

    comment_threads_family = youtube_common.get_resource_family("comment_threads")

    assert comment_threads_family.definition_location.endswith(
        "src/mcp_server/tools/youtube_common/comment_threads.py"
    )
    assert comment_threads.COMMENT_THREADS_LIST_TOOL_NAME == "commentThreads_list"
    assert youtube_common.COMMENT_THREADS_LIST_TOOL_NAME == "commentThreads_list"
    assert youtube_common.COMMENT_THREADS_LIST_QUOTA_COST == 1
    assert callable(comment_threads.build_comment_threads_list_contract)
    assert callable(youtube_common.build_comment_threads_list_tool_descriptor)


def test_commentThreads_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``commentThreads_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comment_threads

    comment_threads_family = youtube_common.get_resource_family("comment_threads")

    assert comment_threads_family.definition_location.endswith(
        "src/mcp_server/tools/youtube_common/comment_threads.py"
    )
    assert comment_threads.COMMENT_THREADS_INSERT_TOOL_NAME == "commentThreads_insert"
    assert youtube_common.COMMENT_THREADS_INSERT_TOOL_NAME == "commentThreads_insert"
    assert youtube_common.COMMENT_THREADS_INSERT_QUOTA_COST == 50
    assert callable(comment_threads.build_comment_threads_insert_contract)
    assert callable(youtube_common.build_comment_threads_insert_tool_descriptor)


def test_comments_insert_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``comments_insert`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comments

    comments_family = youtube_common.get_resource_family("comments")

    assert comments_family.definition_location.endswith("src/mcp_server/tools/youtube_common/comments.py")
    assert comments.COMMENTS_INSERT_TOOL_NAME == "comments_insert"
    assert youtube_common.COMMENTS_INSERT_TOOL_NAME == "comments_insert"
    assert youtube_common.COMMENTS_INSERT_QUOTA_COST == 50
    assert callable(comments.build_comments_insert_contract)
    assert callable(youtube_common.build_comments_insert_tool_descriptor)


def test_comments_update_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``comments_update`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comments

    comments_family = youtube_common.get_resource_family("comments")

    assert comments_family.definition_location.endswith("src/mcp_server/tools/youtube_common/comments.py")
    assert comments.COMMENTS_UPDATE_TOOL_NAME == "comments_update"
    assert youtube_common.COMMENTS_UPDATE_TOOL_NAME == "comments_update"
    assert youtube_common.COMMENTS_UPDATE_QUOTA_COST == 50
    assert callable(comments.build_comments_update_contract)
    assert callable(youtube_common.build_comments_update_tool_descriptor)


def test_comments_set_moderation_status_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``comments_setModerationStatus`` symbols."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comments

    comments_family = youtube_common.get_resource_family("comments")

    assert comments_family.definition_location.endswith("src/mcp_server/tools/youtube_common/comments.py")
    assert comments.COMMENTS_SET_MODERATION_STATUS_TOOL_NAME == "comments_setModerationStatus"
    assert youtube_common.COMMENTS_SET_MODERATION_STATUS_TOOL_NAME == "comments_setModerationStatus"
    assert youtube_common.COMMENTS_SET_MODERATION_STATUS_QUOTA_COST == 50
    assert callable(comments.build_comments_set_moderation_status_contract)
    assert callable(youtube_common.build_comments_set_moderation_status_tool_descriptor)


def test_comments_delete_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``comments_delete`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import comments

    comments_family = youtube_common.get_resource_family("comments")

    assert comments_family.definition_location.endswith("src/mcp_server/tools/youtube_common/comments.py")
    assert comments.COMMENTS_DELETE_TOOL_NAME == "comments_delete"
    assert youtube_common.COMMENTS_DELETE_TOOL_NAME == "comments_delete"
    assert youtube_common.COMMENTS_DELETE_QUOTA_COST == 50
    assert callable(comments.build_comments_delete_contract)
    assert callable(youtube_common.build_comments_delete_tool_descriptor)


def test_localization_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete localization family placement for YT-224."""
    from mcp_server.tools.youtube_common import get_resource_family

    localization = get_resource_family("localization")

    assert localization.definition_location.endswith("src/mcp_server/tools/youtube_common/localization.py")
    assert localization.handler_location.endswith("src/mcp_server/tools/youtube_common/localization.py")
    assert localization.schema_location.endswith("src/mcp_server/tools/youtube_common/localization.py")


def test_i18n_languages_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``i18nLanguages_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import localization

    localization_family = youtube_common.get_resource_family("localization")

    assert localization_family.definition_location.endswith("src/mcp_server/tools/youtube_common/localization.py")
    assert localization.I18N_LANGUAGES_LIST_TOOL_NAME == "i18nLanguages_list"
    assert youtube_common.I18N_LANGUAGES_LIST_TOOL_NAME == "i18nLanguages_list"
    assert youtube_common.I18N_LANGUAGES_LIST_QUOTA_COST == 1
    assert callable(localization.build_i18n_languages_list_contract)
    assert callable(youtube_common.build_i18n_languages_list_tool_descriptor)


def test_i18n_regions_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``i18nRegions_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import localization

    localization_family = youtube_common.get_resource_family("localization")

    assert localization_family.definition_location.endswith("src/mcp_server/tools/youtube_common/localization.py")
    assert localization.I18N_REGIONS_LIST_TOOL_NAME == "i18nRegions_list"
    assert youtube_common.I18N_REGIONS_LIST_TOOL_NAME == "i18nRegions_list"
    assert youtube_common.I18N_REGIONS_LIST_QUOTA_COST == 1
    assert callable(localization.build_i18n_regions_list_contract)
    assert callable(youtube_common.build_i18n_regions_list_tool_descriptor)


def test_representative_captions_insert_metadata_exposes_upload_and_sync_caveats():
    """Expose safe caller-facing metadata for the captions insert endpoint."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS

    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}
    metadata = by_name["captions_insert"].to_tool_metadata()

    assert metadata["quotaCost"] == 400
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert "media" in metadata["inputContract"]["properties"]
    assert any("media" in note for note in metadata["usageNotes"])
    assert any("sync" in caveat for caveat in metadata["caveats"])


def test_representative_captions_update_metadata_exposes_update_media_and_sync_caveats():
    """Expose safe caller-facing metadata for the captions update endpoint."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS

    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}
    metadata = by_name["captions_update"].to_tool_metadata()

    assert metadata["quotaCost"] == 450
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body" in metadata["inputContract"]["properties"]
    assert "media" in metadata["inputContract"]["properties"]
    assert any("body" in note for note in metadata["usageNotes"])
    assert any("media" in note for note in metadata["usageNotes"])
    assert any("sync" in caveat for caveat in metadata["caveats"])


def test_representative_captions_download_metadata_exposes_permission_and_conversion_caveats():
    """Expose safe caller-facing metadata for the captions download endpoint."""
    from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS

    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}
    metadata = by_name["captions_download"].to_tool_metadata()

    assert metadata["quotaCost"] == 200
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert metadata["inputContract"]["properties"]["tfmt"]["enum"] == ["sbv", "scc", "srt", "ttml", "vtt"]
    assert "tlang" in metadata["inputContract"]["properties"]
    assert any("permission" in note.lower() for note in metadata["usageNotes"])
    assert any("tfmt" in note for note in metadata["usageNotes"])
    assert any("tlang" in note for note in metadata["usageNotes"])
    assert any("binary" in caveat.lower() for caveat in metadata["caveats"])


def test_thumbnails_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete thumbnails family placement for YT-244."""
    from mcp_server.tools.youtube_common import get_resource_family

    thumbnails = get_resource_family("thumbnails")

    assert thumbnails.family_name == "thumbnails"
    assert thumbnails.definition_location.endswith("src/mcp_server/tools/youtube_common/thumbnails.py")
    assert thumbnails.handler_location.endswith("src/mcp_server/tools/youtube_common/thumbnails.py")
    assert thumbnails.schema_location.endswith("src/mcp_server/tools/youtube_common/thumbnails.py")
    assert thumbnails.layer1_dependency == "mcp_server.integrations.resources.thumbnails"


def test_thumbnails_set_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``thumbnails_set`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import thumbnails

    assert thumbnails.THUMBNAILS_SET_TOOL_NAME == "thumbnails_set"
    assert thumbnails.THUMBNAILS_SET_QUOTA_COST == 50
    assert youtube_common.THUMBNAILS_SET_TOOL_NAME == "thumbnails_set"
    assert youtube_common.THUMBNAILS_SET_QUOTA_COST == 50
    assert callable(thumbnails.build_thumbnails_set_contract)
    assert callable(youtube_common.build_thumbnails_set_tool_descriptor)


def test_video_abuse_report_reasons_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete video-abuse-report-reasons placement for YT-245."""
    from mcp_server.tools.youtube_common import get_resource_family

    family = get_resource_family("video_abuse_report_reasons")

    assert family.family_name == "video_abuse_report_reasons"
    assert family.definition_location.endswith("src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py")
    assert family.handler_location.endswith("src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py")
    assert family.schema_location.endswith("src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py")
    assert family.layer1_dependency == "mcp_server.integrations.resources.video_abuse_report_reasons"


def test_video_abuse_report_reasons_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videoAbuseReportReasons_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import video_abuse_report_reasons

    assert video_abuse_report_reasons.VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME == "videoAbuseReportReasons_list"
    assert video_abuse_report_reasons.VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME == "videoAbuseReportReasons_list"
    assert youtube_common.VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST == 1
    assert callable(video_abuse_report_reasons.build_video_abuse_report_reasons_list_contract)
    assert callable(youtube_common.build_video_abuse_report_reasons_list_tool_descriptor)


def test_video_categories_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete video-categories family placement for YT-246."""
    from mcp_server.tools.youtube_common import get_resource_family

    family = get_resource_family("video_categories")

    assert family.family_name == "video_categories"
    assert family.definition_location.endswith("src/mcp_server/tools/youtube_common/video_categories.py")
    assert family.handler_location.endswith("src/mcp_server/tools/youtube_common/video_categories.py")
    assert family.schema_location.endswith("src/mcp_server/tools/youtube_common/video_categories.py")
    assert family.layer1_dependency == "mcp_server.integrations.resources.video_categories"


def test_video_categories_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videoCategories_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import video_categories

    assert video_categories.VIDEO_CATEGORIES_LIST_TOOL_NAME == "videoCategories_list"
    assert video_categories.VIDEO_CATEGORIES_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEO_CATEGORIES_LIST_TOOL_NAME == "videoCategories_list"
    assert youtube_common.VIDEO_CATEGORIES_LIST_QUOTA_COST == 1
    assert callable(video_categories.build_video_categories_list_contract)
    assert callable(youtube_common.build_video_categories_list_tool_descriptor)


def test_videos_resource_family_points_to_concrete_layer2_module():
    """Expose the concrete videos family placement for YT-247."""
    from mcp_server.tools.youtube_common import get_resource_family

    family = get_resource_family("videos")

    assert family.family_name == "videos"
    assert family.definition_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert family.handler_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert family.schema_location.endswith("src/mcp_server/tools/youtube_common/videos.py")
    assert family.layer1_dependency == "mcp_server.integrations.resources.videos"


def test_videos_list_scaffolding_exports_concrete_layer2_symbols():
    """Expose foundational ``videos_list`` symbols from the shared package."""
    from mcp_server.tools import youtube_common
    from mcp_server.tools.youtube_common import videos

    assert videos.VIDEOS_LIST_TOOL_NAME == "videos_list"
    assert videos.VIDEOS_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEOS_LIST_TOOL_NAME == "videos_list"
    assert youtube_common.VIDEOS_LIST_QUOTA_COST == 1
    assert callable(videos.build_videos_list_contract)
    assert callable(youtube_common.build_videos_list_tool_descriptor)
