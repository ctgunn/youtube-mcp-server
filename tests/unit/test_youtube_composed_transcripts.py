"""Unit tests for the concrete Layer 3 transcript tool."""

import pytest


def test_transcript_handler_retrieves_one_vtt_transcript_and_normalizes_text():
    """Compose one caption lookup and download into a normalized result."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_transcript_handler,
    )

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
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_transcript_handler,
    )

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
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTranscriptToolError,
        build_transcripts_get_transcript_handler,
    )

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


def test_timestamped_caption_handler_preserves_vtt_cues_and_timing():
    """Return one normalized segment for every ordered VTT cue."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_timestamped_captions_handler,
    )

    calls = []

    def caption_list(arguments):
        """Return one accessible caption track.

        :param arguments: Lower-layer caption-list arguments.
        :return: One usable caption track.
        """
        calls.append(("list", arguments))
        return {"items": [{"id": "track-1", "snippet": {"language": "en", "status": "serving"}}]}

    def caption_download(arguments):
        """Return ordered VTT cues with timing edge cases.

        :param arguments: Lower-layer caption-download arguments.
        :return: Controlled VTT content.
        """
        calls.append(("download", arguments))
        return {
            "content": "WEBVTT\n\n00:00.000 --> 00:01.250\nHello <b>world</b> &amp; friends\n\ncue-2\n00:01.250 --> 01:00:02.500 align:start\n\n00:01.000 --> 00:02.000\nOverlap"
        }

    result = build_transcripts_get_timestamped_captions_handler(
        caption_list=caption_list,
        caption_download=caption_download,
    )({"videoId": " abc "})

    assert calls == [
        ("list", {"part": "snippet", "videoId": "abc"}),
        ("download", {"id": "track-1", "tfmt": "vtt"}),
    ]
    assert result["language"] == "en"
    assert result["languageSelectionSource"] == "source_order_fallback"
    assert result["segments"] == [
        {"text": "Hello world & friends", "startTimeSeconds": 0.0, "endTimeSeconds": 1.25},
        {"text": "", "startTimeSeconds": 1.25, "endTimeSeconds": 3602.5},
        {"text": "Overlap", "startTimeSeconds": 1.0, "endTimeSeconds": 2.0},
    ]


def test_timestamped_caption_handler_rejects_malformed_vtt_without_partial_segments():
    """Expose malformed downloaded timing as a safe failure."""
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
        build_transcripts_get_timestamped_captions_handler,
    )

    handler = build_transcripts_get_timestamped_captions_handler(
        caption_list=lambda _arguments: {"items": [{"id": "track-1", "snippet": {"language": "en", "status": "serving"}}]},
        caption_download=lambda _arguments: {"content": "WEBVTT\n\n00:bad --> 00:01.000\nBad"},
    )

    with pytest.raises(TranscriptsGetTimestampedCaptionsToolError) as error:
        handler({"videoId": "abc"})

    assert error.value.category == "upstream_failure"
    assert "Bad" not in str(error.value.details)


def test_timestamped_caption_handler_selects_exact_requested_language_or_safe_unavailable_error():
    """Select only an exact requested usable language without fallback."""
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
        build_transcripts_get_timestamped_captions_handler,
    )

    downloads = []
    handler = build_transcripts_get_timestamped_captions_handler(
        caption_list=lambda _arguments: {
            "items": [
                {"id": "en", "snippet": {"language": "en", "status": "serving"}},
                {"id": "fr-failed", "snippet": {"language": "fr", "status": "failed"}},
                {"id": "fr", "snippet": {"language": "fr", "status": "serving"}},
            ]
        },
        caption_download=lambda arguments: downloads.append(arguments) or {"content": "WEBVTT\n\n00:00.000 --> 00:01.000\nBonjour"},
    )

    result = handler({"videoId": "abc", "language": " FR "})

    assert result["language"] == "fr"
    assert result["languageSelectionSource"] == "explicit_language"
    assert downloads == [{"id": "fr", "tfmt": "vtt"}]
    with pytest.raises(TranscriptsGetTimestampedCaptionsToolError) as error:
        handler({"videoId": "abc", "language": "es"})
    assert error.value.category == "language_unavailable"
    assert error.value.details == {"language": "es"}
    assert downloads == [{"id": "fr", "tfmt": "vtt"}]


def test_timestamped_caption_handler_uses_source_default_before_source_order_fallback():
    """Prefer an explicitly designated source default when language is omitted."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_get_timestamped_captions_handler,
    )

    handler = build_transcripts_get_timestamped_captions_handler(
        caption_list=lambda _arguments: {
            "items": [
                {"id": "en", "snippet": {"language": "en", "status": "serving"}},
                {"id": "es", "snippet": {"language": "es", "status": "serving", "isDefault": True}},
            ]
        },
        caption_download=lambda arguments: {"content": "WEBVTT\n\n00:00.000 --> 00:01.000\n" + arguments["id"]},
    )

    result = handler({"videoId": "abc"})

    assert result["language"] == "es"
    assert result["languageSelectionSource"] == "source_default"


def test_timestamped_caption_handler_distinguishes_empty_access_and_source_failures_safely():
    """Keep completed absence and each unsafe source outcome distinct."""
    from mcp_server.tools.youtube_common.captions import (
        CaptionsDownloadToolError,
        CaptionsListToolError,
    )
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
        build_transcripts_get_timestamped_captions_handler,
    )

    no_download = []
    empty = build_transcripts_get_timestamped_captions_handler(
        caption_list=lambda _arguments: {"items": []},
        caption_download=lambda arguments: no_download.append(arguments),
    )
    assert empty({"videoId": "abc"}) == {
        "videoId": "abc",
        "availability": "no_accessible_captions",
        "segments": [],
        "fieldProvenance": {"videoId": "normalized", "availability": "normalized", "segments": "normalized"},
    }
    assert no_download == []

    expected_categories = {
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "source_unavailable",
        "resource_not_found": "upstream_failure",
    }
    for lower_category, public_category in expected_categories.items():
        failing = build_transcripts_get_timestamped_captions_handler(
            caption_list=lambda _, category=lower_category: (_ for _ in ()).throw(
                CaptionsListToolError("source secret", category=category, details={"token": "secret", "raw_body": "hidden"})
            )
        )
        with pytest.raises(TranscriptsGetTimestampedCaptionsToolError) as error:
            failing({"videoId": "abc"})
        assert error.value.category == public_category
        assert "secret" not in str(error.value.details)
        assert "hidden" not in str(error.value.details)

    malformed_download = build_transcripts_get_timestamped_captions_handler(
        caption_list=lambda _arguments: {"items": [{"id": "track", "snippet": {"language": "en", "status": "serving"}}]},
        caption_download=lambda _arguments: (_ for _ in ()).throw(
            CaptionsDownloadToolError("source secret", category="endpoint_unavailable", details={"token": "secret"})
        ),
    )
    with pytest.raises(TranscriptsGetTimestampedCaptionsToolError) as download_error:
        malformed_download({"videoId": "abc"})
    assert download_error.value.category == "source_unavailable"
    assert "secret" not in str(download_error.value.details)


def test_language_discovery_lists_every_track_once_in_source_order_without_caption_content():
    """Return one safe option for each source caption track."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_list_languages_handler,
    )

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
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_list_languages_handler,
    )

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


def test_transcript_search_matches_case_insensitively_with_chronological_timestamps_and_one_dependency_call():
    """Return source-preserving, chronologically ordered timed matches."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_search_transcript_handler,
    )

    calls = []

    def timestamped_captions(arguments):
        """Record one timed retrieval request and return unordered matches.

        :param arguments: Timed-caption retrieval arguments.
        :return: Controlled selected transcript segments.
        """
        calls.append(arguments)
        return {
            "videoId": "abc",
            "language": "en",
            "languageSelectionSource": "source_default",
            "captionTrackId": "track-1",
            "availability": "available",
            "segments": [
                {"text": "A later LAUNCH PLAN point", "startTimeSeconds": 9.0, "endTimeSeconds": 10.0},
                {"text": "An earlier launch plan point", "startTimeSeconds": 2.0, "endTimeSeconds": 3.0},
                {"text": "Nothing to see here", "startTimeSeconds": 1.0, "endTimeSeconds": 2.0},
            ],
        }

    result = build_transcripts_search_transcript_handler(timestamped_captions=timestamped_captions)(
        {"videoId": " abc ", "query": "Launch Plan"}
    )

    assert calls == [{"videoId": "abc", "language": None}]
    assert result["availability"] == "available"
    assert [match["matchedText"] for match in result["matches"]] == ["launch plan", "LAUNCH PLAN"]
    assert [match["startTimeSeconds"] for match in result["matches"]] == [2.0, 9.0]
    assert [match["endTimeSeconds"] for match in result["matches"]] == [3.0, 10.0]
    assert all("snippet" in match for match in result["matches"])


def test_transcript_search_rejects_blank_public_text_before_timed_retrieval():
    """Reject invalid search input without requesting caption segments."""
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsSearchTranscriptToolError,
        build_transcripts_search_transcript_handler,
    )

    calls = []
    handler = build_transcripts_search_transcript_handler(timestamped_captions=lambda arguments: calls.append(arguments))

    with pytest.raises(TranscriptsSearchTranscriptToolError) as error:
        handler({"videoId": "abc", "query": "   "})

    assert error.value.category == "invalid_parameters"
    assert error.value.details == {"field": "query"}
    assert calls == []


def test_transcript_search_normalizes_and_forwards_an_explicit_language_without_fallback():
    """Forward one canonical explicit language to timed retrieval."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_search_transcript_handler,
    )

    calls = []

    def timestamped_captions(arguments):
        """Record explicit language and return only that selected transcript.

        :param arguments: Timed-caption retrieval arguments.
        :return: Selected French transcript segment.
        """
        calls.append(arguments)
        return {
            "videoId": "abc",
            "language": "fr",
            "languageSelectionSource": "explicit_language",
            "captionTrackId": "track-fr",
            "availability": "available",
            "segments": [{"text": "Plan de lancement", "startTimeSeconds": 1.0, "endTimeSeconds": 2.0}],
        }

    result = build_transcripts_search_transcript_handler(timestamped_captions=timestamped_captions)(
        {"videoId": "abc", "query": "plan", "language": " FR "}
    )

    assert calls == [{"videoId": "abc", "language": "fr"}]
    assert result["language"] == "fr"
    assert result["languageSelectionSource"] == "explicit_language"


def test_transcript_search_keeps_requested_language_unavailable_error_safe():
    """Preserve a safe exact-language unavailability outcome."""
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
        TranscriptsSearchTranscriptToolError,
        build_transcripts_search_transcript_handler,
    )

    handler = build_transcripts_search_transcript_handler(
        timestamped_captions=lambda _arguments: (_ for _ in ()).throw(
            TranscriptsGetTimestampedCaptionsToolError(
                "The requested caption language is unavailable",
                category="language_unavailable",
                details={"language": "fr", "token": "secret"},
            )
        )
    )

    with pytest.raises(TranscriptsSearchTranscriptToolError) as error:
        handler({"videoId": "abc", "query": "plan", "language": "fr"})

    assert error.value.category == "language_unavailable"
    assert "secret" not in str(error.value.details)


def test_transcript_search_defaults_and_applies_match_limit_after_chronological_ordering():
    """Bound common-term matches after sorting their source timing."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_search_transcript_handler,
    )

    segments = [
        {"text": f"needle {index}", "startTimeSeconds": float(index), "endTimeSeconds": float(index) + 0.5}
        for index in range(12, 0, -1)
    ]
    timed_result = {
        "videoId": "abc",
        "language": "en",
        "languageSelectionSource": "source_default",
        "captionTrackId": "track-1",
        "availability": "available",
        "segments": segments,
    }
    handler = build_transcripts_search_transcript_handler(timestamped_captions=lambda _arguments: timed_result)

    default_result = handler({"videoId": "abc", "query": "needle"})
    bounded_result = handler({"videoId": "abc", "query": "needle", "maxMatches": 2})

    assert len(default_result["matches"]) == 10
    assert [match["startTimeSeconds"] for match in default_result["matches"]] == list(range(1, 11))
    assert [match["startTimeSeconds"] for match in bounded_result["matches"]] == [1.0, 2.0]


def test_transcript_search_rejects_invalid_match_limits_before_retrieval_and_distinguishes_empty_states():
    """Validate match limits and preserve no-match versus unavailable outcomes."""
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsSearchTranscriptToolError,
        build_transcripts_search_transcript_handler,
    )

    calls = []
    handler = build_transcripts_search_transcript_handler(timestamped_captions=lambda arguments: calls.append(arguments))

    for invalid_limit in (0, 51, "2", True):
        with pytest.raises(TranscriptsSearchTranscriptToolError) as error:
            handler({"videoId": "abc", "query": "needle", "maxMatches": invalid_limit})
        assert error.value.category == "invalid_parameters"
        assert error.value.details == {"field": "maxMatches"}
    assert calls == []

    no_match = build_transcripts_search_transcript_handler(
        timestamped_captions=lambda _arguments: {
            "videoId": "abc",
            "language": "en",
            "languageSelectionSource": "source_default",
            "captionTrackId": "track-1",
            "availability": "available",
            "segments": [],
        }
    )({"videoId": "abc", "query": "needle"})
    assert no_match["availability"] == "no_matches"
    assert no_match["matches"] == []

    unavailable = build_transcripts_search_transcript_handler(
        timestamped_captions=lambda _arguments: {"videoId": "abc", "availability": "no_accessible_captions", "segments": []}
    )
    with pytest.raises(TranscriptsSearchTranscriptToolError) as unavailable_error:
        unavailable({"videoId": "abc", "query": "needle"})
    assert unavailable_error.value.category == "transcript_unavailable"


def test_transcript_search_keeps_snippets_bounded_and_preserves_expanding_casefold_source_text():
    """Keep contract-sized context while mapping Unicode case folds to source text."""
    from mcp_server.tools.youtube_composed.transcripts import (
        build_transcripts_search_transcript_handler,
    )

    result = build_transcripts_search_transcript_handler(
        timestamped_captions=lambda _arguments: {
            "videoId": "abc",
            "language": "de",
            "languageSelectionSource": "explicit_language",
            "captionTrackId": "track-de",
            "availability": "available",
            "segments": [
                {
                    "text": "Straße " + ("context " * 40),
                    "startTimeSeconds": 1.0,
                    "endTimeSeconds": 2.0,
                }
            ],
        }
    )({"videoId": "abc", "query": "STRASSE"})

    match = result["matches"][0]
    assert match["matchedText"] == "Straße"
    assert len(match["snippet"]) <= 160
    assert match["snippet"].endswith("...")
