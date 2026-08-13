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


def test_transcript_language_discovery_descriptor_exposes_the_executable_contract():
    """Require the bounded public language-discovery contract."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_list_languages_tool_descriptor

    descriptor = build_transcripts_list_languages_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "transcripts_listLanguages"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["videoId"],
        "properties": {"videoId": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }
    assert metadata["family"] == "transcripts"
    assert metadata["compositionBoundary"] == {
        "kind": "transcript_language_discovery",
        "lowerLayerDependencies": ["captions.list"],
        "boundedness": "one video; exactly one caption discovery; zero caption downloads",
        "partialResultPolicy": "Return no_accessible_languages only after a completed empty caption listing.",
    }
    assert metadata["lowerLayerDependencies"] == ["captions.list"]
    assert metadata["authAndQuotaNotes"] == [
        "Official caption discovery requires eligible OAuth-authorized access.",
        "Successful discovery uses captions.list quota.",
    ]
    assert set(metadata["errorCategories"]) == {
        "invalid_parameters",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "source_unavailable",
        "upstream_failure",
    }
    assert metadata["emptyResultPolicy"] == "no_accessible_languages"
    assert "representativeOnly" not in metadata
