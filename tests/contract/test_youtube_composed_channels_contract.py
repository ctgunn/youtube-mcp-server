"""Contract tests for the concrete public channel-detail tool."""


def test_channel_details_metadata_is_concrete_and_bounded():
    """Require executable discovery metadata for bounded channel enrichment."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_metadata

    metadata = build_channels_get_channel_metadata()

    assert metadata["name"] == "channels_getChannel"
    assert metadata["compositionBoundary"]["kind"] == "normalized_enrichment"
    assert metadata["lowerLayerDependencies"] == ["channels.list", "playlistItems.list"]
    assert metadata["compositionBoundary"]["boundedness"] == "one channel and at most one playlist item"
    assert "representativeOnly" not in metadata


def test_channel_details_contract_exposes_schema_provenance_and_safe_errors():
    """Require the public schema and caller-safe discovery facts."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_tool_descriptor

    descriptor = build_channels_get_channel_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["channelId"],
        "properties": {"channelId": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}
    assert fields["channelId"]["category"] == "raw_upstream"
    assert fields["latestVideoPublishedAt"]["category"] == "normalized"
    assert fields["normalizedMetadata.country"]["category"] == "normalized"
    assert metadata["errorCategories"] == [
        "invalid_parameters",
        "unavailable_resource",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "upstream_failure",
        "partial_enrichment_failure",
    ]
    assert "token" not in str(metadata).lower()


def test_channel_details_contract_discloses_public_contact_and_classification_limits():
    """Require explicit heuristic provenance, basis, and uncertainty guidance."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_metadata

    metadata = build_channels_get_channel_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}
    heuristics = {item["name"]: item for item in metadata["heuristics"]}

    assert fields["normalizedMetadata.emailsFound"]["category"] == "heuristic_inferred"
    assert fields["normalizedMetadata.contactLinks"]["category"] == "heuristic_inferred"
    assert fields["heuristics.creatorClassification"]["category"] == "heuristic_inferred"
    assert "public" in heuristics["publicContactExtraction"]["basis"].lower()
    assert "not verified" in heuristics["publicContactExtraction"]["limitations"].lower()
    assert "incomplete" in heuristics["creatorClassification"]["limitations"].lower()


def test_channel_details_contract_discloses_safe_partial_enrichment_behavior():
    """Require caller-visible partial and unavailable enrichment rules."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_metadata

    metadata = build_channels_get_channel_metadata()

    assert "unavailable" in metadata["compositionBoundary"]["partialResultPolicy"].lower()
    assert "partial" in metadata["compositionBoundary"]["partialResultPolicy"].lower()
    assert metadata["errorGuidance"]["partial_enrichment_failure"].startswith("Use the returned profile")


def test_batch_channel_details_contract_exposes_bounded_ordered_schema():
    """Require the public batch schema, defaults, and bounded discovery facts."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_tool_descriptor

    descriptor = build_channels_get_channels_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "channels_getChannels"
    assert descriptor["inputSchema"]["required"] == ["channelIds"]
    assert descriptor["inputSchema"]["properties"]["channelIds"]["maxItems"] == 50
    assert descriptor["inputSchema"]["properties"]["parts"]["default"] == ["snippet"]
    assert descriptor["inputSchema"]["properties"]["includeLatestUpload"]["default"] is True
    assert metadata["compositionBoundary"]["kind"] == "normalized_batch_enrichment"
    assert "order" in metadata["responseConvention"]["resultOrdering"].lower()
    assert "representativeOnly" not in metadata


def test_batch_channel_details_contract_discloses_selection_and_enrichment_states():
    """Require explicit detail selection and default-on enrichment guidance."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_metadata

    metadata = build_channels_get_channels_metadata()

    assert metadata["detailSelection"]["supported"] == ["snippet", "contentDetails"]
    assert metadata["detailSelection"]["default"] == ["snippet"]
    assert metadata["latestUploadEnrichment"]["default"] is True
    assert metadata["latestUploadEnrichment"]["states"] == ["complete", "unavailable", "partial", "not_requested"]
    assert "one playlist item per available channel" in metadata["compositionBoundary"]["boundedness"]


def test_batch_channel_details_contract_discloses_independent_safe_outcomes():
    """Require item-local unavailable and partial-outcome guidance."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_metadata

    metadata = build_channels_get_channels_metadata()

    assert metadata["individualOutcomePolicy"]["unavailable"] == "unavailable_resource"
    assert metadata["individualOutcomePolicy"]["partial"] == "partial_enrichment_failure"
    assert metadata["errorGuidance"]["unavailable_resource"].startswith("Use a different")
    assert metadata["errorGuidance"]["partial_enrichment_failure"].startswith("Use the returned item")


def test_channel_search_contract_exposes_concrete_query_only_schema_and_boundary():
    """Require executable discovery metadata for public channel search."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_tool_descriptor

    descriptor = build_channels_search_channels_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "channels_searchChannels"
    assert descriptor["inputSchema"]["required"] == ["query"]
    assert descriptor["inputSchema"]["properties"]["maxResults"]["default"] == 10
    assert descriptor["inputSchema"]["properties"]["channelType"]["enum"] == ["any", "show"]
    assert metadata["compositionBoundary"]["kind"] == "ranked_enrichment"
    assert metadata["lowerLayerDependencies"] == ["search.list", "channels.list", "playlistItems.list"]
    assert "base-search" in metadata["continuationPolicy"].lower()
    assert "representativeOnly" not in metadata
    assert "token" not in str(metadata).lower()


def test_channel_search_contract_discloses_conditional_public_enrichment_and_heuristics():
    """Require public disclosure of refinement dependencies and limits."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_metadata

    metadata = build_channels_search_channels_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert fields["statistics.subscriberCount"]["category"] == "raw_upstream"
    assert fields["latestVideoPublishedAt"]["category"] == "normalized"
    assert fields["heuristics.creatorClassification"]["category"] == "heuristic_inferred"
    assert "conditional" in metadata["compositionBoundary"]["partialResultPolicy"].lower()
    assert "quota" in " ".join(metadata["authAndQuotaNotes"]).lower()


def test_channel_search_contract_discloses_all_ranking_and_tie_semantics():
    """Require caller-visible deterministic ranking semantics."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_metadata

    metadata = build_channels_search_channels_metadata()

    assert metadata["rankingSemantics"]["sortBy"] == [
        "relevance",
        "subscribers_asc",
        "subscribers_desc",
        "indie_priority",
        "recent_activity",
    ]
    assert "base-search position" in metadata["rankingSemantics"]["ties"]
    assert metadata["rankingSemantics"]["filterOrder"] == "Apply filters before final ranking and result cap."


def test_creator_discovery_contract_exposes_bounded_composite_schema():
    """Require executable public metadata for creator discovery."""
    from mcp_server.tools.youtube_composed.channels import build_channels_find_creators_tool_descriptor

    descriptor = build_channels_find_creators_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "channels_findCreators"
    assert descriptor["inputSchema"]["required"] == ["query"]
    assert descriptor["inputSchema"]["properties"]["maxResults"]["default"] == 10
    assert descriptor["inputSchema"]["properties"]["sampleVideosPerChannel"] == {
        "type": "integer", "minimum": 0, "maximum": 10, "default": 0
    }
    assert metadata["compositionBoundary"]["kind"] == "ranked_enrichment"
    assert metadata["lowerLayerDependencies"] == ["search.list", "channels.list", "playlistItems.list"]
    assert "50" in metadata["compositionBoundary"]["boundedness"]
    assert "base" in metadata["continuationPolicy"].lower()
    assert "representativeOnly" not in metadata
    assert "token" not in str(metadata).lower()


def test_creator_discovery_contract_discloses_provenance_heuristics_and_ranking():
    """Require provenance, heuristic limitations, and deterministic ranking metadata."""
    from mcp_server.tools.youtube_composed.channels import build_channels_find_creators_metadata

    metadata = build_channels_find_creators_metadata()
    fields = {field["fieldName"]: field for field in metadata["responseFields"]}

    assert fields["matchedVideoBasis"]["category"] == "normalized"
    assert fields["sampleVideos"]["category"] == "normalized"
    assert fields["heuristics.creatorClassification"]["category"] == "heuristic_inferred"
    assert metadata["rankingSemantics"]["sortBy"] == [
        "relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"
    ]
    assert "incomplete" in metadata["heuristics"][0]["limitations"].lower()
