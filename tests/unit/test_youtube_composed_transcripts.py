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
