"""Unit tests for the concrete Layer 3 transcript tool."""

import pytest


def test_transcript_handler_retrieves_one_vtt_transcript_and_normalizes_text():
    """Compose one caption lookup and download into a normalized result."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_get_transcript_handler

    list_calls, download_calls = [], []

    def caption_list(arguments):
        """Record a caption-list request and return one serving English track."""
        list_calls.append(arguments)
        return {"items": [{"id": "track-1", "snippet": {"language": "en", "status": "serving", "trackKind": "standard"}}]}

    def caption_download(arguments):
        """Record a caption-download request and return VTT content."""
        download_calls.append(arguments)
        return {"content": "WEBVTT\n\n00:00.000 --> 00:01.000\nHello <b>world</b>"}

    result = build_transcripts_get_transcript_handler(caption_list=caption_list, caption_download=caption_download)({"videoId": " abc "})
    assert list_calls == [{"part": "snippet", "videoId": "abc"}]
    assert download_calls == [{"id": "track-1", "tfmt": "vtt"}]
    assert result["text"] == "Hello world"
    assert result["languageSource"] == "english_fallback"


def test_language_selection_is_explicit_then_configured_then_english_and_exact():
    """Select exact matching language tracks with deterministic identifiers."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_get_transcript_handler

    calls = []
    handler = build_transcripts_get_transcript_handler(
        default_language="fr",
        caption_list=lambda _: {"items": [
            {"id": "z", "snippet": {"language": "fr", "status": "syncing", "trackKind": "ASR", "isDraft": True}},
            {"id": "a", "snippet": {"language": "fr", "status": "serving", "trackKind": "standard", "isDraft": False}},
            {"id": "other", "snippet": {"language": "fr-CA", "status": "serving"}},
        ]},
        caption_download=lambda arguments: calls.append(arguments) or {"content": "WEBVTT\n\n00:00.000 --> 00:01.000\nBonjour"},
    )
    assert handler({"videoId": "abc", "language": " FR "})["languageSource"] == "explicit"
    assert handler({"videoId": "abc"})["languageSource"] == "configured_default"
    assert calls == [{"id": "a", "tfmt": "vtt"}, {"id": "a", "tfmt": "vtt"}]


def test_transcript_handler_maps_unavailable_and_safe_errors():
    """Expose stable safe transcript failure categories."""
    from mcp_server.tools.youtube_common.captions import CaptionsListToolError
    from mcp_server.tools.youtube_composed.transcripts import TranscriptsGetTranscriptToolError, build_transcripts_get_transcript_handler

    unavailable = build_transcripts_get_transcript_handler(caption_list=lambda _: {"items": []})
    with pytest.raises(TranscriptsGetTranscriptToolError) as unavailable_error:
        unavailable({"videoId": "abc"})
    assert unavailable_error.value.category == "transcript_unavailable"
    assert unavailable_error.value.details == {"language": "en"}

    denied = build_transcripts_get_transcript_handler(caption_list=lambda _: (_ for _ in ()).throw(CaptionsListToolError("secret", category="authorization_failed", details={"token": "secret"})))
    with pytest.raises(TranscriptsGetTranscriptToolError) as denied_error:
        denied({"videoId": "abc"})
    assert denied_error.value.category == "authorization_sensitive_data"
    assert "secret" not in str(denied_error.value.details)


def test_language_discovery_lists_every_track_once_in_source_order_without_caption_content():
    """Return one safe option for each source caption track."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_list_languages_handler

    calls = []

    def caption_list(arguments):
        """Record the discovery request and return ordered caption records.

        :param arguments: Lower-layer caption-list arguments.
        :return: Controlled ordered caption-list payload.
        """
        calls.append(arguments)
        return {
            "items": [
                {"id": "track-en-standard", "snippet": {"language": "en", "status": "serving", "trackKind": "standard"}},
                {"id": "track-es", "snippet": {"language": "es", "status": "syncing", "trackKind": "ASR"}},
                {"id": "track-en-asr", "snippet": {"language": "en", "status": "serving", "trackKind": "ASR"}},
            ]
        }

    result = build_transcripts_list_languages_handler(caption_list=caption_list)({"videoId": " abc "})

    assert calls == [{"part": "snippet", "videoId": "abc"}]
    assert result["videoId"] == "abc"
    assert result["availability"] == "available"
    assert [option["language"] for option in result["languageOptions"]] == ["en", "es", "en"]
    assert [option["captionTrackId"] for option in result["languageOptions"]] == ["track-en-standard", "track-es", "track-en-asr"]
    assert "text" not in result
    assert "content" not in str(result)


def test_language_discovery_preserves_only_approved_source_metadata_and_missing_values():
    """Expose allowed source metadata without inventing unavailable values."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_list_languages_handler

    result = build_transcripts_list_languages_handler(
        caption_list=lambda _: {
            "items": [
                {
                    "id": "track-1",
                    "snippet": {
                        "language": "en",
                        "name": "English",
                        "status": "serving",
                        "trackKind": "standard",
                        "isDraft": False,
                        "isAutoSynced": False,
                        "privateOwner": "must-not-leak",
                    },
                },
                {"snippet": {"language": "en", "unknown": "must-not-leak"}},
            ]
        }
    )({"videoId": "abc"})

    first, second = result["languageOptions"]
    assert first["captionTrackId"] == "track-1"
    assert first["trackMetadata"] == {
        "name": "English",
        "status": "serving",
        "trackKind": "standard",
        "isDraft": False,
        "isAutoSynced": False,
    }
    assert second["captionTrackId"] is None
    assert second["trackMetadata"] == {}
    assert "privateOwner" not in str(result)
    assert "unknown" not in str(result)
    assert result["fieldProvenance"] == {
        "videoId": "normalized",
        "languageOptions.language": "raw_upstream",
        "languageOptions.captionTrackId": "raw_upstream",
        "languageOptions.trackMetadata": "raw_upstream",
        "languageOptions.availability": "normalized",
        "availability": "normalized",
    }


def test_language_discovery_validates_input_and_maps_empty_and_safe_errors():
    """Keep validation, empty discovery, and source failures distinct and safe."""
    from mcp_server.tools.youtube_common.captions import CaptionsListToolError
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsListLanguagesToolError,
        build_transcripts_list_languages_handler,
    )

    calls = []
    handler = build_transcripts_list_languages_handler(caption_list=lambda arguments: calls.append(arguments) or {"items": []})
    with pytest.raises(TranscriptsListLanguagesToolError) as invalid_error:
        handler({"videoId": " "})
    assert invalid_error.value.category == "invalid_parameters"
    assert calls == []
    assert handler({"videoId": "abc"})["availability"] == "no_accessible_languages"

    expected_categories = {
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "source_unavailable",
        "resource_not_found": "upstream_failure",
        "upstream_failure": "upstream_failure",
    }
    for lower_category, public_category in expected_categories.items():
        failing = build_transcripts_list_languages_handler(
            caption_list=lambda _, category=lower_category: (_ for _ in ()).throw(
                CaptionsListToolError("source secret", category=category, details={"token": "secret", "raw_body": "hidden"})
            )
        )
        with pytest.raises(TranscriptsListLanguagesToolError) as mapped_error:
            failing({"videoId": "abc"})
        assert mapped_error.value.category == public_category
        assert "secret" not in str(mapped_error.value.details)
        assert "hidden" not in str(mapped_error.value.details)
