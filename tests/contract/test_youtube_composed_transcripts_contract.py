"""Contract tests for ``transcripts_getTranscript``."""


def test_transcript_descriptor_exposes_concrete_safe_contract():
    """Require schema, dependencies, provenance, and safe failures."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_get_transcript_tool_descriptor

    descriptor = build_transcripts_get_transcript_tool_descriptor()
    metadata = descriptor["metadata"]
    assert descriptor["name"] == "transcripts_getTranscript"
    assert descriptor["inputSchema"]["required"] == ["videoId"]
    assert descriptor["inputSchema"]["additionalProperties"] is False
    assert metadata["compositionBoundary"]["kind"] == "transcript_retrieval"
    assert metadata["lowerLayerDependencies"] == ["captions.list", "captions.download"]
    assert metadata["languageSelection"] == ["explicit", "configured_default", "english_fallback"]
    assert "representativeOnly" not in metadata
    assert set(metadata["errorCategories"]) == {"invalid_parameters", "transcript_unavailable", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure"}
