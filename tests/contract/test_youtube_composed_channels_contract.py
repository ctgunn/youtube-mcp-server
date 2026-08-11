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
