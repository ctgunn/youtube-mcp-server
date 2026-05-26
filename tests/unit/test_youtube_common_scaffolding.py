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
