"""Contract tests for ``transcripts_getTranscript``."""


def test_transcript_descriptor_exposes_concrete_safe_contract():
    """Require schema, dependencies, provenance, and safe failures."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_transcript_tool_descriptor,
    )

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
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_list_languages_tool_descriptor,
    )

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


def test_timestamped_caption_descriptor_exposes_concrete_timing_contract():
    """Require the bounded timestamped-caption public contract."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_timestamped_captions_tool_descriptor,
    )

    descriptor = build_transcripts_get_timestamped_captions_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "transcripts_getTimestampedCaptions"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["videoId"],
        "properties": {
            "videoId": {"type": "string", "minLength": 1},
            "language": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["lowerLayerDependencies"] == ["captions.list", "captions.download"]
    assert metadata["compositionBoundary"]["boundedness"] == "one video; one caption discovery; at most one caption download"
    assert metadata["segmentTiming"] == {"unit": "seconds", "granularity": "one source VTT cue per segment"}
    assert metadata["authAndQuotaNotes"] == [
        "Official captions require eligible OAuth-authorized access.",
        "Successful retrieval uses captions.list and captions.download quota.",
    ]
    assert "representativeOnly" not in metadata
    assert metadata["languageSelection"] == ["explicit_language", "source_default", "source_order_fallback"]
    assert metadata["errorGuidance"]["language_unavailable"] == "Request an accessible language or a different video."
    assert {field["fieldName"] for field in metadata["responseFields"]} >= {
        "language",
        "languageSelectionSource",
        "segments.startTimeSeconds",
        "segments.endTimeSeconds",
    }
    assert metadata["emptyResultPolicy"] == "no_accessible_captions"
    assert set(metadata["errorCategories"]) == {
        "invalid_parameters",
        "language_unavailable",
        "authorization_sensitive_data",
        "quota_exhaustion",
        "source_unavailable",
        "upstream_failure",
    }


def test_transcript_search_descriptor_exposes_the_timed_literal_search_contract():
    """Require the concrete transcript-search schema and metadata."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_search_transcript_tool_descriptor,
    )

    descriptor = build_transcripts_search_transcript_tool_descriptor()
    metadata = descriptor["metadata"]

    assert descriptor["name"] == "transcripts_searchTranscript"
    assert descriptor["inputSchema"] == {
        "type": "object",
        "required": ["videoId", "query"],
        "properties": {
            "videoId": {"type": "string", "minLength": 1},
            "query": {"type": "string", "minLength": 1},
            "language": {"type": "string", "minLength": 1},
            "maxMatches": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
        },
        "additionalProperties": False,
    }
    assert metadata["compositionBoundary"]["kind"] == "transcript_text_search"
    assert metadata["lowerLayerDependencies"] == ["transcripts_getTimestampedCaptions", "in_server_literal_search"]
    assert metadata["emptyResultPolicy"] == "no_matches"
    assert metadata["snippetPolicy"]["maximumCharacters"] == 160
    assert metadata["matchLimit"] == {"default": 10, "minimum": 1, "maximum": 50, "appliedAfter": "chronological_ordering"}
    assert metadata["languageSelection"] == ["explicit_language", "source_default", "source_order_fallback"]
    assert metadata["errorGuidance"]["language_unavailable"] == "Request an accessible language or a different video."
    assert "representativeOnly" not in metadata
