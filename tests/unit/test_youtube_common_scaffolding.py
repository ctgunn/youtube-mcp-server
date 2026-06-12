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
