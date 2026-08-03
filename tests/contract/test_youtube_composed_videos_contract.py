"""Contract tests for the public normalized video-detail tool."""


def test_video_details_metadata_is_concrete_not_representative_only():
    """Require executable discovery metadata for the video-detail tool."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_metadata

    metadata = build_videos_get_video_metadata()

    assert metadata["name"] == "videos_getVideo"
    assert "representativeOnly" not in metadata


def test_video_details_contract_exposes_the_core_schema_and_provenance():
    """Require stable discovery metadata for core normalized retrieval."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    descriptor = build_videos_get_video_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "videos_getVideo"
    assert descriptor["inputSchema"]["required"] == ["videoId"]
    assert metadata["compositionBoundary"]["kind"] == "normalized_retrieval"
    assert metadata["lowerLayerDependencies"] == ["videos.list"]
    assert {field["fieldName"] for field in metadata["responseFields"]} >= {
        "videoId",
        "title",
        "duration",
    }
    assert "representativeOnly" not in metadata


def test_video_details_contract_documents_every_optional_part_mapping():
    """Require discovery metadata to expose all additive detail groups."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    descriptor = build_videos_get_video_tool_descriptor()
    schema = descriptor["inputSchema"]
    mappings = descriptor["metadata"]["optionalPartMappings"]

    assert schema["properties"]["parts"]["items"]["enum"] == [
        "snippet",
        "contentDetails",
        "statistics",
        "status",
        "topicDetails",
    ]
    assert set(mappings) == {"snippet", "contentDetails", "statistics", "status", "topicDetails"}
    assert mappings["statistics"] == ["viewCount", "likeCount", "favoriteCount", "commentCount"]


def test_video_details_contract_documents_safe_failure_categories_without_secrets():
    """Require the complete safe error taxonomy in discovery metadata."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_metadata

    metadata = build_videos_get_video_metadata()

    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
    ]
    assert "token" not in str(metadata).lower()
    assert "stack" not in str(metadata).lower()
    assert metadata["errorGuidance"]["quota_exhaustion"] == "Retry after capacity is available."


def test_video_details_contract_retains_videos_list_dependency_without_representative_fallback():
    """Keep the concrete detail contract tied to the lower-layer list tool.

    :return: ``None`` after validating the concrete dependency boundary.
    """
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    metadata = build_videos_get_video_tool_descriptor()["metadata"]

    assert metadata["lowerLayerDependencies"] == ["videos.list"]
    assert "representativeOnly" not in metadata
