"""Contract tests for the public normalized video-detail tool."""


def test_video_details_metadata_is_concrete_not_representative_only():
    """Require executable discovery metadata for the video-detail tool."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_metadata

    metadata = build_videos_get_video_metadata()

    assert metadata["name"] == "videos_getVideo"
    assert "representativeOnly" not in metadata


def test_video_details_contract_exposes_the_core_schema_and_provenance():
    """Require stable discovery metadata for core normalized retrieval."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_get_video_tool_descriptor,
    )

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
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_get_video_tool_descriptor,
    )

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
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_get_video_tool_descriptor,
    )

    metadata = build_videos_get_video_tool_descriptor()["metadata"]

    assert metadata["lowerLayerDependencies"] == ["videos.list"]
    assert "representativeOnly" not in metadata


def test_video_search_contract_exposes_concrete_schema_and_safe_metadata():
    """Require concrete discovery metadata for the public video-search tool."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_search_videos_tool_descriptor,
    )

    descriptor = build_videos_search_videos_tool_descriptor()
    schema = descriptor["inputSchema"]
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "videos_searchVideos"
    assert schema["required"] == ["query"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["maxResults"] == {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}
    assert schema["properties"]["order"]["enum"] == ["date", "rating", "relevance", "title", "viewCount"]
    assert metadata["compositionBoundary"]["kind"] == "ranked_enrichment"
    assert metadata["lowerLayerDependencies"] == ["search.list", "channels.list", "playlistItems.list"]
    assert {field["fieldName"] for field in metadata["responseFields"]} >= {"videoId", "title", "channel.subscriberCount"}
    assert "invalid_parameters" in metadata["errorCategories"]
    assert "representativeOnly" not in metadata
    assert "token" not in str(metadata).lower()


def test_video_search_contract_discloses_enrichment_limits_and_partial_behavior():
    """Require channel-aware metadata to make bounds and uncertainty explicit."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_search_videos_metadata,
    )

    metadata = build_videos_search_videos_metadata()

    assert "uniqueChannels" in metadata["rankingAndFiltering"]
    assert "creatorOnly" in metadata["rankingAndFiltering"]
    assert "partial_enrichment_failure" in metadata["errorCategories"]
    assert "maxResults" in metadata["compositionBoundary"]["boundedness"]
    assert metadata["heuristics"][0]["name"] == "creatorClassification"
    assert "incomplete" in metadata["heuristics"][0]["limitations"]


def test_video_search_contract_discloses_deterministic_ranking_and_exclusion_rules():
    """Require public metadata for ranking provenance and unavailable data behavior."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_search_videos_metadata,
    )

    metadata = build_videos_search_videos_metadata()

    assert metadata["rankingSemantics"]["sortBy"] == ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"]
    assert "base-search position" in metadata["rankingSemantics"]["ties"]
    assert metadata["rankingSemantics"]["deduplication"] == "Apply uniqueChannels after final ranking."
    assert "excluded" in metadata["rankingSemantics"]["unavailableData"]


def test_video_statistics_contract_exposes_a_concrete_single_video_schema_and_boundary():
    """Require concrete discovery metadata for public video statistics."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_get_statistics_tool_descriptor,
    )

    descriptor = build_videos_get_statistics_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "videos_getStatistics"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["videoId"],
        "properties": {"videoId": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["kind"] == "normalized_retrieval"
    assert metadata["lowerLayerDependencies"] == ["videos.list"]
    assert "one-unit" in metadata["authAndQuotaNotes"][0]
    assert "representativeOnly" not in metadata


def test_video_statistics_contract_documents_metric_availability_and_safe_caveats():
    """Require metric provenance, unavailable states, and source caveats."""
    from mcp_server.tools.youtube_composed.videos import (
        build_videos_get_statistics_metadata,
    )

    metadata = build_videos_get_statistics_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert set(metadata["expectedMetrics"]) == {"viewCount", "likeCount", "commentCount", "favoriteCount"}
    assert fields["statistics.*.value"]["category"] == "raw_upstream"
    assert fields["statistics.*.state"]["category"] == "normalized"
    assert metadata["metricAvailability"] == {
        "available": "A source-provided count, including zero.",
        "unavailable": "The expected source metric was not provided; no numeric value is returned.",
    }
    assert "deprecated" in metadata["sourceCaveats"]["favoriteCount"].lower()
    assert "dislikeCount" not in metadata["expectedMetrics"]
    assert "owner-sensitive" in metadata["sourceCaveats"]["dislikeCount"]
    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
    ]
