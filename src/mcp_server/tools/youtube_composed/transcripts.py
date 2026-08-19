"""Concrete transcript-family public YouTube tools."""

from __future__ import annotations

import html
import re
from typing import Any

from mcp_server.tools.youtube_common.captions import (
    CaptionsDownloadToolError,
    CaptionsListToolError,
    build_captions_download_handler,
    build_captions_list_handler,
)
from mcp_server.tools.youtube_common.conventions import (
    safe_upstream_error_message,
    sanitize_error_details,
)
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("transcripts")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
TRANSCRIPTS_GET_TRANSCRIPT_TOOL_NAME = "transcripts_getTranscript"
TRANSCRIPTS_GET_TRANSCRIPT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId"],
    "properties": {"videoId": {"type": "string", "minLength": 1}, "language": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
TRANSCRIPTS_LIST_LANGUAGES_TOOL_NAME = "transcripts_listLanguages"
TRANSCRIPTS_LIST_LANGUAGES_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId"],
    "properties": {"videoId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_TOOL_NAME = "transcripts_getTimestampedCaptions"
TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId"],
    "properties": {
        "videoId": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}
TRANSCRIPTS_SEARCH_TRANSCRIPT_TOOL_NAME = "transcripts_searchTranscript"
TRANSCRIPTS_SEARCH_TRANSCRIPT_INPUT_SCHEMA = {
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
_LANGUAGE_PATTERN = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*")
_VTT_TIMESTAMP_PATTERN = re.compile(r"(?:(?P<hours>\d+):)?(?P<minutes>[0-5]\d):(?P<seconds>[0-5]\d\.\d{3})")


class TranscriptsGetTranscriptToolError(ValueError):
    """Represent a safe caller-facing transcript retrieval failure.

    :param message: Caller-safe explanation.
    :param category: Stable public error category.
    :param details: Candidate safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe transcript retrieval error.

        :param message: Caller-safe explanation.
        :param category: Stable public error category.
        :param details: Candidate safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class TranscriptsListLanguagesToolError(ValueError):
    """Represent a safe caller-facing transcript language-discovery failure.

    :param message: Caller-safe explanation.
    :param category: Stable public error category.
    :param details: Candidate safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe transcript language-discovery error.

        :param message: Caller-safe explanation.
        :param category: Stable public error category.
        :param details: Candidate safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class TranscriptsGetTimestampedCaptionsToolError(ValueError):
    """Represent a safe timestamped-caption retrieval failure.

    :param message: Caller-safe explanation.
    :param category: Stable public error category.
    :param details: Candidate safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe timestamped-caption retrieval error.

        :param message: Caller-safe explanation.
        :param category: Stable public error category.
        :param details: Candidate safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class TranscriptsSearchTranscriptToolError(ValueError):
    """Represent a safe caller-facing transcript-search failure.

    :param message: Caller-safe explanation.
    :param category: Stable public error category.
    :param details: Candidate safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe transcript-search error.

        :param message: Caller-safe explanation.
        :param category: Stable public error category.
        :param details: Candidate safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _normalize_language(value: str, *, field: str) -> str:
    """Validate and canonicalize a language tag.

    :param value: Candidate language text.
    :param field: Caller-visible field name for a validation error.
    :return: Canonicalized BCP-47 language tag.
    :raises TranscriptsGetTranscriptToolError: If the value is malformed.
    """
    text = value.strip() if isinstance(value, str) else ""
    if not text or not _LANGUAGE_PATTERN.fullmatch(text):
        raise TranscriptsGetTranscriptToolError("language must be a valid non-empty language tag", category="invalid_parameters", details={"field": field})
    parts = text.split("-")
    return "-".join([parts[0].lower(), *[part.upper() if len(part) == 2 else part.title() if len(part) == 4 else part.lower() for part in parts[1:]]])


def validate_transcripts_get_transcript_arguments(arguments: dict[str, Any]) -> dict[str, str | None]:
    """Validate the public transcript request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized video identifier and optional explicit language.
    :raises TranscriptsGetTranscriptToolError: If public input is invalid.
    """
    if not isinstance(arguments, dict):
        raise TranscriptsGetTranscriptToolError("transcripts_getTranscript arguments must be an object", category="invalid_parameters", details={"field": "arguments"})
    unexpected = set(arguments) - {"videoId", "language"}
    if unexpected:
        raise TranscriptsGetTranscriptToolError("transcripts_getTranscript received an unsupported field", category="invalid_parameters", details={"field": min(unexpected)})
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise TranscriptsGetTranscriptToolError("transcripts_getTranscript requires a non-empty videoId", category="invalid_parameters", details={"field": "videoId"})
    language = arguments.get("language")
    if language is not None and not isinstance(language, str):
        raise TranscriptsGetTranscriptToolError("language must be a valid non-empty language tag", category="invalid_parameters", details={"field": "language"})
    return {"videoId": video_id.strip(), "language": _normalize_language(language, field="language") if language is not None else None}


def validate_transcripts_list_languages_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate the public transcript language-discovery request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized video identifier.
    :raises TranscriptsListLanguagesToolError: If public input is invalid.
    """
    if not isinstance(arguments, dict):
        raise TranscriptsListLanguagesToolError(
            "transcripts_listLanguages arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected = set(arguments) - {"videoId"}
    if unexpected:
        raise TranscriptsListLanguagesToolError(
            "transcripts_listLanguages received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected)},
        )
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise TranscriptsListLanguagesToolError(
            "transcripts_listLanguages requires a non-empty videoId",
            category="invalid_parameters",
            details={"field": "videoId"},
        )
    return {"videoId": video_id.strip()}


def validate_transcripts_get_timestamped_captions_arguments(arguments: dict[str, Any]) -> dict[str, str | None]:
    """Validate one public timestamped-caption request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized video identifier and optional explicit language.
    :raises TranscriptsGetTimestampedCaptionsToolError: If public input is invalid.
    """
    if not isinstance(arguments, dict):
        raise TranscriptsGetTimestampedCaptionsToolError(
            "transcripts_getTimestampedCaptions arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected = set(arguments) - {"videoId", "language"}
    if unexpected:
        raise TranscriptsGetTimestampedCaptionsToolError(
            "transcripts_getTimestampedCaptions received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected)},
        )
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise TranscriptsGetTimestampedCaptionsToolError(
            "transcripts_getTimestampedCaptions requires a non-empty videoId",
            category="invalid_parameters",
            details={"field": "videoId"},
        )
    language = arguments.get("language")
    if language is not None and not isinstance(language, str):
        raise TranscriptsGetTimestampedCaptionsToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": "language"},
        )
    return {
        "videoId": video_id.strip(),
        "language": _normalize_timestamped_caption_language(language) if language is not None else None,
    }


def validate_transcripts_search_transcript_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate one public transcript-search request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized video identifier, query, and optional search inputs.
    :raises TranscriptsSearchTranscriptToolError: If required public text is invalid.
    """
    if not isinstance(arguments, dict):
        raise TranscriptsSearchTranscriptToolError(
            "transcripts_searchTranscript arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected = set(arguments) - {"videoId", "query", "language", "maxMatches"}
    if unexpected:
        raise TranscriptsSearchTranscriptToolError(
            "transcripts_searchTranscript received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected)},
        )
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise TranscriptsSearchTranscriptToolError(
            "transcripts_searchTranscript requires a non-empty videoId",
            category="invalid_parameters",
            details={"field": "videoId"},
        )
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise TranscriptsSearchTranscriptToolError(
            "transcripts_searchTranscript requires a non-empty query",
            category="invalid_parameters",
            details={"field": "query"},
        )
    language = arguments.get("language")
    if language is not None and not isinstance(language, str):
        raise TranscriptsSearchTranscriptToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": "language"},
        )
    max_matches = arguments.get("maxMatches", 10)
    if type(max_matches) is not int or not 1 <= max_matches <= 50:
        raise TranscriptsSearchTranscriptToolError(
            "maxMatches must be an integer from 1 through 50",
            category="invalid_parameters",
            details={"field": "maxMatches"},
        )
    return {
        "videoId": video_id.strip(),
        "query": query.strip(),
        "language": _normalize_transcript_search_language(language) if language is not None else None,
        "maxMatches": max_matches,
    }


def _normalize_transcript_search_language(value: str) -> str:
    """Validate and canonicalize one transcript-search language tag.

    :param value: Candidate caller-requested language text.
    :return: Canonicalized BCP-47 language tag.
    :raises TranscriptsSearchTranscriptToolError: If the language is malformed.
    """
    text = value.strip()
    if not text or not _LANGUAGE_PATTERN.fullmatch(text):
        raise TranscriptsSearchTranscriptToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": "language"},
        )
    parts = text.split("-")
    return "-".join(
        [
            parts[0].lower(),
            *[
                part.upper() if len(part) == 2 else part.title() if len(part) == 4 else part.lower()
                for part in parts[1:]
            ],
        ]
    )


def _normalize_timestamped_caption_language(value: str) -> str:
    """Validate and canonicalize one timestamped-caption language tag.

    :param value: Candidate caller-requested language text.
    :return: Canonicalized BCP-47 language tag.
    :raises TranscriptsGetTimestampedCaptionsToolError: If the language is malformed.
    """
    text = value.strip()
    if not text or not _LANGUAGE_PATTERN.fullmatch(text):
        raise TranscriptsGetTimestampedCaptionsToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": "language"},
        )
    parts = text.split("-")
    return "-".join(
        [
            parts[0].lower(),
            *[
                part.upper() if len(part) == 2 else part.title() if len(part) == 4 else part.lower()
                for part in parts[1:]
            ],
        ]
    )


def _usable_timestamped_caption_tracks(payload: Any) -> list[dict[str, Any]]:
    """Return usable caption tracks in completed source order.

    :param payload: Lower-layer ``captions.list`` result.
    :return: Usable source caption records in source order.
    :raises TranscriptsGetTimestampedCaptionsToolError: If the source result is malformed.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure")
    tracks = []
    for item in items:
        snippet = item.get("snippet") if isinstance(item, dict) and isinstance(item.get("snippet"), dict) else {}
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(snippet.get("language"), str):
            continue
        if snippet.get("status") == "failed":
            continue
        tracks.append(item)
    return tracks


def _select_timestamped_caption_track(payload: Any, language: str | None) -> tuple[dict[str, Any], str] | None:
    """Choose one usable caption track for timestamped retrieval.

    :param payload: Lower-layer ``captions.list`` result.
    :param language: Optional normalized caller-requested language.
    :return: Selected source track and selection-source label, or ``None`` when unavailable.
    :raises TranscriptsGetTimestampedCaptionsToolError: If the source result is malformed.
    """
    tracks = _usable_timestamped_caption_tracks(payload)
    if language is not None:
        for track in tracks:
            source_language = track["snippet"]["language"]
            if source_language.strip().lower() == language.lower():
                return track, "explicit_language"
        return None
    for track in tracks:
        if track["snippet"].get("isDefault") is True:
            return track, "source_default"
    return (tracks[0], "source_order_fallback") if tracks else None


def _parse_vtt_timestamp(value: str) -> float:
    """Convert one VTT timestamp to elapsed seconds.

    :param value: Candidate VTT timestamp.
    :return: Non-negative elapsed seconds.
    :raises TranscriptsGetTimestampedCaptionsToolError: If the timestamp is malformed.
    """
    match = _VTT_TIMESTAMP_PATTERN.fullmatch(value.strip())
    if match is None:
        raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure")
    return float(match.group("hours") or 0) * 3600 + float(match.group("minutes")) * 60 + float(match.group("seconds"))


def _parse_vtt_segments(content: Any) -> list[dict[str, Any]]:
    """Parse downloaded VTT content into ordered timestamped caption segments.

    :param content: Downloaded VTT text or UTF-8 bytes.
    :return: One normalized segment per source VTT cue.
    :raises TranscriptsGetTimestampedCaptionsToolError: If content or cue timing is malformed.
    """
    try:
        text = content.decode("utf-8") if isinstance(content, bytes) else content if isinstance(content, str) else None
    except UnicodeDecodeError as exc:
        raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure") from exc
    if text is None:
        raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure")
    lines = text.lstrip("\ufeff").splitlines()
    index = 0
    if lines and lines[0].strip().startswith("WEBVTT"):
        index = 1
        while index < len(lines) and lines[index].strip():
            index += 1
    segments = []
    while index < len(lines):
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines):
            break
        if lines[index].strip().startswith(("NOTE", "STYLE", "REGION")):
            while index < len(lines) and lines[index].strip():
                index += 1
            continue
        timing = lines[index].strip()
        if "-->" not in timing:
            index += 1
            if index >= len(lines) or "-->" not in lines[index]:
                raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure")
            timing = lines[index].strip()
        index += 1
        start_text, end_text = timing.split("-->", 1)
        start_time = _parse_vtt_timestamp(start_text)
        end_time = _parse_vtt_timestamp(end_text.strip().split(maxsplit=1)[0])
        if end_time < start_time:
            raise TranscriptsGetTimestampedCaptionsToolError(safe_upstream_error_message(), category="upstream_failure")
        cue_lines = []
        while index < len(lines) and lines[index].strip():
            cue_lines.append(re.sub(r"<[^>]+>", "", html.unescape(lines[index].strip())))
            index += 1
        segments.append(
            {
                "text": " ".join(" ".join(cue_lines).split()),
                "startTimeSeconds": start_time,
                "endTimeSeconds": end_time,
            }
        )
    return segments


def _map_timestamped_caption_error(error: ValueError) -> TranscriptsGetTimestampedCaptionsToolError:
    """Translate one lower-layer caption failure to the public timed-caption contract.

    :param error: Lower-layer caption-list or caption-download error.
    :return: Safe public timestamped-caption error.
    """
    category = getattr(error, "category", "upstream_failure")
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "source_unavailable",
    }.get(category, "upstream_failure")
    return TranscriptsGetTimestampedCaptionsToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=getattr(error, "details", {}),
    )


def build_transcripts_get_timestamped_captions_handler(*, caption_list=None, caption_download=None):
    """Build a callable handler for one timestamped-caption retrieval.

    :param caption_list: Optional injected caption-list handler.
    :param caption_download: Optional injected caption-download handler.
    :return: Callable timestamped-caption handler.
    """
    selected_list = caption_list or build_captions_list_handler()
    selected_download = caption_download or build_captions_download_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate, retrieve, and normalize one selected track's VTT cues.

        :param arguments: Caller-provided public arguments.
        :return: Normalized timestamped-caption result.
        :raises TranscriptsGetTimestampedCaptionsToolError: If retrieval cannot complete safely.
        """
        request = validate_transcripts_get_timestamped_captions_arguments(arguments)
        try:
            track_selection = _select_timestamped_caption_track(
                selected_list({"part": "snippet", "videoId": request["videoId"]}),
                request["language"],
            )
        except CaptionsListToolError as exc:
            raise _map_timestamped_caption_error(exc) from exc
        if track_selection is None:
            if request["language"] is not None:
                raise TranscriptsGetTimestampedCaptionsToolError(
                    "The requested caption language is unavailable",
                    category="language_unavailable",
                    details={"language": request["language"]},
                )
            return {
                "videoId": request["videoId"],
                "availability": "no_accessible_captions",
                "segments": [],
                "fieldProvenance": {"videoId": "normalized", "availability": "normalized", "segments": "normalized"},
            }
        track, selection_source = track_selection
        try:
            download = selected_download({"id": track["id"], "tfmt": "vtt"})
        except CaptionsDownloadToolError as exc:
            raise _map_timestamped_caption_error(exc) from exc
        segments = _parse_vtt_segments(download.get("content") if isinstance(download, dict) else None)
        return {
            "videoId": request["videoId"],
            "language": track["snippet"]["language"],
            "languageSelectionSource": selection_source,
            "captionTrackId": track["id"],
            "availability": "available",
            "segments": segments,
            "fieldProvenance": {
                "videoId": "normalized",
                "language": "raw_upstream",
                "languageSelectionSource": "normalized",
                "captionTrackId": "raw_upstream",
                "availability": "normalized",
                "segments.text": "normalized",
                "segments.startTimeSeconds": "normalized",
                "segments.endTimeSeconds": "normalized",
            },
        }

    return handler


def _transcript_search_snippet(text: str, match_start: int, match_end: int) -> str:
    """Build a bounded source-segment snippet around one literal match.

    :param text: Normalized source segment text.
    :param match_start: Inclusive first-match offset in ``text``.
    :param match_end: Exclusive first-match offset in ``text``.
    :return: At most 160 source-text characters with omission ellipses.
    """
    maximum_characters = 160
    if len(text) <= maximum_characters:
        return text
    source_budget = maximum_characters - 6
    match_length = min(match_end - match_start, source_budget)
    remaining = source_budget - match_length
    start = max(0, match_start - remaining // 2)
    end = min(len(text), max(match_end, match_start + match_length) + (remaining - (match_start - start)))
    if end - start < source_budget:
        start = max(0, end - source_budget)
    snippet = text[start:end]
    return ("..." if start else "") + snippet + ("..." if end < len(text) else "")


def _casefolded_source_span(text: str, query: str) -> tuple[int, int] | None:
    """Locate a case-folded query and map it back to source-text offsets.

    :param text: Source segment text.
    :param query: Trimmed caller query.
    :return: Inclusive/exclusive source offsets, or ``None`` when absent.
    """
    folded_parts = []
    source_offsets = []
    for source_index, character in enumerate(text):
        folded_character = character.casefold()
        folded_parts.append(folded_character)
        source_offsets.extend([source_index] * len(folded_character))
    match_start = "".join(folded_parts).find(query.casefold())
    if match_start < 0:
        return None
    match_end = match_start + len(query.casefold())
    return source_offsets[match_start], source_offsets[match_end - 1] + 1


def _transcript_search_matches(segments: Any, query: str) -> list[dict[str, Any]]:
    """Find one chronological literal match per valid timed source segment.

    :param segments: Candidate normalized timestamped segments.
    :param query: Trimmed caller query.
    :return: Chronologically ordered source-segment match records.
    :raises TranscriptsSearchTranscriptToolError: If segment timing is malformed.
    """
    if not isinstance(segments, list):
        raise TranscriptsSearchTranscriptToolError(safe_upstream_error_message(), category="upstream_failure")
    matches = []
    for source_order, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise TranscriptsSearchTranscriptToolError(safe_upstream_error_message(), category="upstream_failure")
        text = segment.get("text")
        start_time = segment.get("startTimeSeconds")
        end_time = segment.get("endTimeSeconds")
        if not isinstance(text, str) or not isinstance(start_time, (int, float)) or not isinstance(end_time, (int, float)):
            raise TranscriptsSearchTranscriptToolError(safe_upstream_error_message(), category="upstream_failure")
        if start_time < 0 or end_time < start_time:
            raise TranscriptsSearchTranscriptToolError(safe_upstream_error_message(), category="upstream_failure")
        source_span = _casefolded_source_span(text, query)
        if source_span is None:
            continue
        match_start, match_end = source_span
        matches.append(
            {
                "matchedText": text[match_start:match_end],
                "snippet": _transcript_search_snippet(text, match_start, match_end),
                "startTimeSeconds": float(start_time),
                "endTimeSeconds": float(end_time),
                "_sourceOrder": source_order,
            }
        )
    matches.sort(key=lambda match: (match["startTimeSeconds"], match["_sourceOrder"]))
    for match in matches:
        match.pop("_sourceOrder")
    return matches


def _map_timestamped_search_error(error: ValueError) -> TranscriptsSearchTranscriptToolError:
    """Translate a timed-retrieval failure to the search tool's safe contract.

    :param error: Error raised by the timed-caption dependency.
    :return: Safe transcript-search error retaining a supported category.
    """
    return TranscriptsSearchTranscriptToolError(
        safe_upstream_error_message(),
        category=getattr(error, "category", "upstream_failure"),
        details=getattr(error, "details", {}),
    )


def build_transcripts_search_transcript_handler(*, timestamped_captions=None):
    """Build a callable handler for one timed transcript text search.

    :param timestamped_captions: Optional injected timed-caption retrieval handler.
    :return: Callable transcript-search handler.
    """
    selected_timestamped_captions = timestamped_captions or build_transcripts_get_timestamped_captions_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Retrieve timed segments and return chronological literal matches.

        :param arguments: Caller-provided public arguments.
        :return: Search result with selected-language context and matches.
        :raises TranscriptsSearchTranscriptToolError: If search cannot complete safely.
        """
        request = validate_transcripts_search_transcript_arguments(arguments)
        try:
            timed_result = selected_timestamped_captions(
                {"videoId": request["videoId"], "language": request["language"]}
            )
        except ValueError as exc:
            raise _map_timestamped_search_error(exc) from exc
        if not isinstance(timed_result, dict) or timed_result.get("availability") != "available":
            raise TranscriptsSearchTranscriptToolError(
                "The requested transcript is unavailable",
                category="transcript_unavailable",
            )
        matches = _transcript_search_matches(timed_result.get("segments"), request["query"])[
            : request["maxMatches"]
        ]
        return {
            "videoId": timed_result.get("videoId", request["videoId"]),
            "language": timed_result.get("language"),
            "languageSelectionSource": timed_result.get("languageSelectionSource"),
            "captionTrackId": timed_result.get("captionTrackId"),
            "availability": "available" if matches else "no_matches",
            "matches": matches,
            "fieldProvenance": {
                "videoId": "normalized",
                "language": "raw_upstream",
                "languageSelectionSource": "normalized",
                "captionTrackId": "raw_upstream",
                "availability": "normalized",
                "matches.matchedText": "normalized_source_segment",
                "matches.snippet": "normalized_source_segment",
                "matches.startTimeSeconds": "normalized_source_segment",
                "matches.endTimeSeconds": "normalized_source_segment",
            },
        }

    return handler


def _language_option(item: Any) -> dict[str, Any]:
    """Normalize one source caption track into a safe language option.

    :param item: Candidate source caption track returned by ``captions.list``.
    :return: One language option retaining only approved source fields.
    """
    source_item = item if isinstance(item, dict) else {}
    snippet = source_item.get("snippet")
    source_snippet = snippet if isinstance(snippet, dict) else {}
    metadata: dict[str, Any] = {}
    for field_name in ("name", "status", "trackKind"):
        value = source_snippet.get(field_name)
        if isinstance(value, str):
            metadata[field_name] = value
    for field_name in ("isDraft", "isAutoSynced"):
        value = source_snippet.get(field_name)
        if isinstance(value, bool):
            metadata[field_name] = value
    identifier = source_item.get("id")
    language = source_snippet.get("language")
    return {
        "language": language if isinstance(language, str) else None,
        "availability": "available",
        "captionTrackId": identifier if isinstance(identifier, str) else None,
        "trackMetadata": metadata,
    }


def _map_caption_list_languages_error(error: ValueError) -> TranscriptsListLanguagesToolError:
    """Translate one lower-layer caption-list failure to the public contract.

    :param error: Lower-layer caption-list error.
    :return: Safe public language-discovery error.
    """
    category = getattr(error, "category", "upstream_failure")
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "source_unavailable",
    }.get(category, "upstream_failure")
    return TranscriptsListLanguagesToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=getattr(error, "details", {}),
    )


def _resolved_language(request: dict[str, str | None], default_language: str | None, default_language_error: str | None) -> tuple[str, str]:
    """Resolve one language from explicit, configured, and English sources.

    :param request: Validated transcript request.
    :param default_language: Injected configured default language.
    :param default_language_error: Safe error state for invalid configuration.
    :return: Resolved language and selection-source label.
    :raises TranscriptsGetTranscriptToolError: If configured language is invalid.
    """
    if request["language"] is not None:
        return request["language"], "explicit"
    if default_language_error:
        raise TranscriptsGetTranscriptToolError("configured transcript language is invalid", category="invalid_parameters", details={"field": "YOUTUBE_TRANSCRIPT_LANG"})
    if default_language:
        return _normalize_language(default_language, field="YOUTUBE_TRANSCRIPT_LANG"), "configured_default"
    return "en", "english_fallback"


def _selected_track(payload: dict[str, Any], language: str) -> dict[str, Any] | None:
    """Choose one deterministic usable exact-language caption track.

    :param payload: Lower-layer caption-list result.
    :param language: Resolved language to match exactly.
    :return: Selected source caption record, or ``None`` when unavailable.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    candidates = []
    for item in items:
        snippet = item.get("snippet") if isinstance(item, dict) and isinstance(item.get("snippet"), dict) else {}
        identifier = item.get("id") if isinstance(item, dict) else None
        source_language = snippet.get("language")
        if not isinstance(identifier, str) or not isinstance(source_language, str) or source_language.strip().lower() != language.lower() or snippet.get("status") == "failed":
            continue
        candidates.append(item)
    def key(item: dict[str, Any]) -> tuple[int, int, int, str]:
        snippet = item["snippet"]
        return ({"serving": 0, "syncing": 1}.get(snippet.get("status"), 2), {"standard": 0, "ASR": 1, "forced": 2}.get(snippet.get("trackKind"), 3), 1 if snippet.get("isDraft") else 0, item["id"])
    return min(candidates, key=key) if candidates else None


def _plain_vtt(content: Any) -> str:
    """Normalize one VTT download into complete plain transcript text.

    :param content: Downloaded VTT text or UTF-8 bytes.
    :return: Whitespace-normalized cue text.
    :raises TranscriptsGetTranscriptToolError: If content is malformed or undecodable.
    """
    try:
        text = content.decode("utf-8") if isinstance(content, bytes) else content if isinstance(content, str) else None
    except UnicodeDecodeError as exc:
        raise TranscriptsGetTranscriptToolError(safe_upstream_error_message(), category="upstream_failure") from exc
    if text is None:
        raise TranscriptsGetTranscriptToolError(safe_upstream_error_message(), category="upstream_failure")
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT" or "-->" in line or re.fullmatch(r"\d+", line):
            continue
        lines.append(re.sub(r"<[^>]+>", "", html.unescape(line)))
    return " ".join(" ".join(lines).split())


def _map_caption_error(error: ValueError, language: str) -> TranscriptsGetTranscriptToolError:
    """Translate one safe lower-layer caption error to the public contract.

    :param error: Lower-layer caption error.
    :param language: Resolved language for safe unavailable context.
    :return: Public transcript error.
    """
    category = getattr(error, "category", "upstream_failure")
    public_category = {"invalid_request": "invalid_parameters", "authentication_failed": "authorization_sensitive_data", "authorization_failed": "authorization_sensitive_data", "quota_exhausted": "quota_exhaustion", "resource_not_found": "transcript_unavailable"}.get(category, "upstream_failure")
    details = {"language": language} if public_category == "transcript_unavailable" else getattr(error, "details", {})
    return TranscriptsGetTranscriptToolError("The requested transcript is unavailable" if public_category == "transcript_unavailable" else safe_upstream_error_message(), category=public_category, details=details)


def build_transcripts_get_transcript_handler(*, caption_list=None, caption_download=None, default_language: str | None = None, default_language_error: str | None = None):
    """Build a callable handler for one normalized transcript retrieval.

    :param caption_list: Optional injected caption-list handler.
    :param caption_download: Optional injected caption-download handler.
    :param default_language: Optional injected configured language.
    :param default_language_error: Optional safe invalid-configuration state.
    :return: Callable transcript handler.
    """
    selected_list = caption_list or build_captions_list_handler()
    selected_download = caption_download or build_captions_download_handler()
    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate, retrieve, and normalize one transcript.

        :param arguments: Caller-provided public arguments.
        :return: Normalized transcript result.
        :raises TranscriptsGetTranscriptToolError: If retrieval cannot complete safely.
        """
        request = validate_transcripts_get_transcript_arguments(arguments)
        language, source = _resolved_language(request, default_language, default_language_error)
        try:
            track = _selected_track(selected_list({"part": "snippet", "videoId": request["videoId"]}), language)
        except CaptionsListToolError as exc:
            raise _map_caption_error(exc, language) from exc
        if track is None:
            raise TranscriptsGetTranscriptToolError("The requested transcript is unavailable", category="transcript_unavailable", details={"language": language})
        try:
            download = selected_download({"id": track["id"], "tfmt": "vtt"})
        except CaptionsDownloadToolError as exc:
            raise _map_caption_error(exc, language) from exc
        text = _plain_vtt(download.get("content") if isinstance(download, dict) else None)
        return {"videoId": request["videoId"], "language": language, "languageSource": source, "availability": "available" if text else "empty", "captionTrackId": track["id"], "text": text, "fieldProvenance": {"videoId": "normalized", "language": "normalized", "languageSource": "normalized", "availability": "normalized", "captionTrackId": "raw_upstream", "text": "normalized"}}
    return handler


def build_transcripts_list_languages_handler(*, caption_list=None):
    """Build a callable handler for one transcript language discovery request.

    :param caption_list: Optional injected caption-list handler.
    :return: Callable language-discovery handler.
    """
    selected_list = caption_list or build_captions_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Validate and list accessible language options for one video.

        :param arguments: Caller-provided public arguments.
        :return: Normalized language-discovery result.
        :raises TranscriptsListLanguagesToolError: If discovery cannot complete safely.
        """
        request = validate_transcripts_list_languages_arguments(arguments)
        try:
            payload = selected_list({"part": "snippet", "videoId": request["videoId"]})
        except CaptionsListToolError as exc:
            raise _map_caption_list_languages_error(exc) from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise TranscriptsListLanguagesToolError(
                safe_upstream_error_message(),
                category="upstream_failure",
            )
        options = [_language_option(item) for item in payload["items"]]
        return {
            "videoId": request["videoId"],
            "languageOptions": options,
            "availability": "available" if options else "no_accessible_languages",
            "fieldProvenance": {
                "videoId": "normalized",
                "languageOptions.language": "raw_upstream",
                "languageOptions.captionTrackId": "raw_upstream",
                "languageOptions.trackMetadata": "raw_upstream",
                "languageOptions.availability": "normalized",
                "availability": "normalized",
            },
        }

    return handler


def build_transcripts_get_transcript_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the transcript retrieval tool.

    :return: JSON-compatible public metadata.
    """
    return {"name": TRANSCRIPTS_GET_TRANSCRIPT_TOOL_NAME, "family": "transcripts", "parameters": ["videoId", "language"], "inputContract": TRANSCRIPTS_GET_TRANSCRIPT_INPUT_SCHEMA, "compositionBoundary": {"kind": "transcript_retrieval", "lowerLayerDependencies": ["captions.list", "captions.download"], "boundedness": "one video; one caption discovery; at most one caption download", "partialResultPolicy": "Return transcript unavailable when no accessible exact-language track exists."}, "lowerLayerDependencies": ["captions.list", "captions.download"], "languageSelection": ["explicit", "configured_default", "english_fallback"], "responseFields": [{"fieldName": "videoId", "category": "normalized", "source": "request"}, {"fieldName": "language", "category": "normalized", "source": "resolved language"}, {"fieldName": "languageSource", "category": "normalized", "source": "selection policy"}, {"fieldName": "captionTrackId", "category": "raw_upstream", "source": "captions.list"}, {"fieldName": "text", "category": "normalized", "source": "captions.download VTT"}], "authAndQuotaNotes": ["Official captions require eligible OAuth-authorized access.", "Successful retrieval uses captions.list and captions.download quota."], "caveats": ["Exact language matching only; no translation or other-language fallback.", "Timestamped segments are not returned by this tool."], "errorCategories": ["invalid_parameters", "transcript_unavailable", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure"], "errorGuidance": {"invalid_parameters": "Correct the named request or configuration field and retry.", "transcript_unavailable": "Request an accessible language or a different video.", "authorization_sensitive_data": "Obtain eligible caption authorization.", "quota_exhaustion": "Retry after capacity is available.", "upstream_failure": "Retry when the source service is available."}}


def build_transcripts_list_languages_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for transcript language discovery.

    :return: JSON-compatible public metadata.
    """
    return {
        "name": TRANSCRIPTS_LIST_LANGUAGES_TOOL_NAME,
        "family": "transcripts",
        "parameters": ["videoId"],
        "inputContract": TRANSCRIPTS_LIST_LANGUAGES_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "transcript_language_discovery",
            "lowerLayerDependencies": ["captions.list"],
            "boundedness": "one video; exactly one caption discovery; zero caption downloads",
            "partialResultPolicy": "Return no_accessible_languages only after a completed empty caption listing.",
        },
        "lowerLayerDependencies": ["captions.list"],
        "emptyResultPolicy": "no_accessible_languages",
        "responseFields": [
            {"fieldName": "videoId", "category": "normalized", "source": "request"},
            {"fieldName": "languageOptions.language", "category": "raw_upstream", "source": "captions.list"},
            {"fieldName": "languageOptions.captionTrackId", "category": "raw_upstream", "source": "captions.list"},
            {"fieldName": "languageOptions.trackMetadata", "category": "raw_upstream", "source": "captions.list"},
            {"fieldName": "languageOptions.availability", "category": "normalized", "source": "discovery result"},
            {"fieldName": "availability", "category": "normalized", "source": "discovery result"},
        ],
        "authAndQuotaNotes": [
            "Official caption discovery requires eligible OAuth-authorized access.",
            "Successful discovery uses captions.list quota.",
        ],
        "caveats": [
            "Each returned caption track remains a separate source-order option; no language selection or fallback occurs.",
            "Caption text and timestamped segments are not returned by this tool.",
        ],
        "errorCategories": [
            "invalid_parameters",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "source_unavailable",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the named request field and retry.",
            "authorization_sensitive_data": "Obtain eligible caption authorization.",
            "quota_exhaustion": "Retry after capacity is available.",
            "source_unavailable": "Retry when caption discovery is available.",
            "upstream_failure": "Retry when the source service is available or use a different video.",
        },
    }


def build_transcripts_get_timestamped_captions_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for timestamped caption retrieval.

    :return: JSON-compatible public metadata.
    """
    return {
        "name": TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_TOOL_NAME,
        "family": "transcripts",
        "parameters": ["videoId", "language"],
        "inputContract": TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "timestamped_caption_retrieval",
            "lowerLayerDependencies": ["captions.list", "captions.download"],
            "boundedness": "one video; one caption discovery; at most one caption download",
            "partialResultPolicy": "Return no partial segments when caption content is malformed or inaccessible.",
        },
        "lowerLayerDependencies": ["captions.list", "captions.download"],
        "emptyResultPolicy": "no_accessible_captions",
        "languageSelection": ["explicit_language", "source_default", "source_order_fallback"],
        "segmentTiming": {"unit": "seconds", "granularity": "one source VTT cue per segment"},
        "responseFields": [
            {"fieldName": "videoId", "category": "normalized", "source": "request"},
            {"fieldName": "language", "category": "raw_upstream", "source": "captions.list"},
            {"fieldName": "languageSelectionSource", "category": "normalized", "source": "selection policy"},
            {"fieldName": "captionTrackId", "category": "raw_upstream", "source": "captions.list"},
            {"fieldName": "segments.text", "category": "normalized", "source": "captions.download VTT cue"},
            {"fieldName": "segments.startTimeSeconds", "category": "normalized", "source": "captions.download VTT cue timing"},
            {"fieldName": "segments.endTimeSeconds", "category": "normalized", "source": "captions.download VTT cue timing"},
        ],
        "authAndQuotaNotes": [
            "Official captions require eligible OAuth-authorized access.",
            "Successful retrieval uses captions.list and captions.download quota.",
        ],
        "caveats": [
            "Explicit language matching is exact; no translation or other-language fallback occurs.",
            "Segments preserve source VTT cue order and timing boundaries without merging or splitting.",
        ],
        "errorCategories": [
            "invalid_parameters",
            "language_unavailable",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "source_unavailable",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the named request field and retry.",
            "language_unavailable": "Request an accessible language or a different video.",
            "authorization_sensitive_data": "Obtain eligible caption authorization.",
            "quota_exhaustion": "Retry after capacity is available.",
            "source_unavailable": "Retry when the caption source is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_transcripts_search_transcript_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for timed transcript text search.

    :return: JSON-compatible public metadata.
    """
    return {
        "name": TRANSCRIPTS_SEARCH_TRANSCRIPT_TOOL_NAME,
        "family": "transcripts",
        "parameters": ["videoId", "query", "language", "maxMatches"],
        "inputContract": TRANSCRIPTS_SEARCH_TRANSCRIPT_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "transcript_text_search",
            "lowerLayerDependencies": ["transcripts_getTimestampedCaptions", "in_server_literal_search"],
            "boundedness": "one video; one timed-caption retrieval; local segment-only literal search",
            "partialResultPolicy": "Return no_matches only after successful selected-transcript retrieval.",
        },
        "lowerLayerDependencies": ["transcripts_getTimestampedCaptions", "in_server_literal_search"],
        "emptyResultPolicy": "no_matches",
        "matchLimit": {
            "default": 10,
            "minimum": 1,
            "maximum": 50,
            "appliedAfter": "chronological_ordering",
        },
        "languageSelection": ["explicit_language", "source_default", "source_order_fallback"],
        "snippetPolicy": {"maximumCharacters": 160, "source": "matching source segment only"},
        "responseFields": [
            {"fieldName": "videoId", "category": "normalized", "source": "request"},
            {"fieldName": "language", "category": "raw_upstream", "source": "timestamped caption retrieval"},
            {"fieldName": "matches.matchedText", "category": "normalized", "source": "matching source segment"},
            {"fieldName": "matches.snippet", "category": "normalized", "source": "matching source segment"},
            {"fieldName": "matches.startTimeSeconds", "category": "normalized", "source": "timestamped caption retrieval"},
            {"fieldName": "matches.endTimeSeconds", "category": "normalized", "source": "timestamped caption retrieval"},
        ],
        "authAndQuotaNotes": [
            "Official captions require eligible OAuth-authorized access.",
            "Successful retrieval uses captions.list and captions.download quota.",
        ],
        "caveats": [
            "Matching is case-insensitive and literal within one source segment; no cross-segment matching occurs.",
            "Matches are chronological by source segment start time; semantic relevance ranking is not provided.",
        ],
        "errorCategories": [
            "invalid_parameters",
            "transcript_unavailable",
            "language_unavailable",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "source_unavailable",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the named request field and retry.",
            "transcript_unavailable": "Use a different video or obtain eligible caption access.",
            "language_unavailable": "Request an accessible language or a different video.",
            "authorization_sensitive_data": "Obtain eligible caption authorization.",
            "quota_exhaustion": "Retry after capacity is available.",
            "source_unavailable": "Retry when the caption source is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_transcripts_get_transcript_tool_descriptor(**dependencies: Any) -> dict[str, Any]:
    """Build the executable MCP descriptor for transcript retrieval.

    :param dependencies: Optional injected handler and configuration dependencies.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {"name": TRANSCRIPTS_GET_TRANSCRIPT_TOOL_NAME, "description": "Retrieve complete transcript text for one video in a requested or default language.", "inputSchema": TRANSCRIPTS_GET_TRANSCRIPT_INPUT_SCHEMA, "handler": build_transcripts_get_transcript_handler(**dependencies), "metadata": build_transcripts_get_transcript_metadata()}


def build_transcripts_list_languages_tool_descriptor(**dependencies: Any) -> dict[str, Any]:
    """Build the executable MCP descriptor for transcript language discovery.

    :param dependencies: Optional injected caption-list dependency.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": TRANSCRIPTS_LIST_LANGUAGES_TOOL_NAME,
        "description": "List accessible transcript and caption language tracks for one video.",
        "inputSchema": TRANSCRIPTS_LIST_LANGUAGES_INPUT_SCHEMA,
        "handler": build_transcripts_list_languages_handler(**dependencies),
        "metadata": build_transcripts_list_languages_metadata(),
    }


def build_transcripts_get_timestamped_captions_tool_descriptor(**dependencies: Any) -> dict[str, Any]:
    """Build the executable MCP descriptor for timestamped caption retrieval.

    :param dependencies: Optional injected caption-list and caption-download dependencies.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_TOOL_NAME,
        "description": "Retrieve timestamped caption segments for one video in a requested or selected language.",
        "inputSchema": TRANSCRIPTS_GET_TIMESTAMPED_CAPTIONS_INPUT_SCHEMA,
        "handler": build_transcripts_get_timestamped_captions_handler(**dependencies),
        "metadata": build_transcripts_get_timestamped_captions_metadata(),
    }


def build_transcripts_search_transcript_tool_descriptor(**dependencies: Any) -> dict[str, Any]:
    """Build the executable MCP descriptor for transcript text search.

    :param dependencies: Optional injected timed-caption dependency.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": TRANSCRIPTS_SEARCH_TRANSCRIPT_TOOL_NAME,
        "description": "Search one video's timestamped transcript for literal matching snippets.",
        "inputSchema": TRANSCRIPTS_SEARCH_TRANSCRIPT_INPUT_SCHEMA,
        "handler": build_transcripts_search_transcript_handler(**dependencies),
        "metadata": build_transcripts_search_transcript_metadata(),
    }
