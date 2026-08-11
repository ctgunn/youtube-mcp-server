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
from mcp_server.tools.youtube_common.conventions import safe_upstream_error_message, sanitize_error_details
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
_LANGUAGE_PATTERN = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*")


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
        raise TranscriptsGetTranscriptToolError("transcripts_getTranscript received an unsupported field", category="invalid_parameters", details={"field": sorted(unexpected)[0]})
    video_id = arguments.get("videoId")
    if not isinstance(video_id, str) or not video_id.strip():
        raise TranscriptsGetTranscriptToolError("transcripts_getTranscript requires a non-empty videoId", category="invalid_parameters", details={"field": "videoId"})
    language = arguments.get("language")
    if language is not None and not isinstance(language, str):
        raise TranscriptsGetTranscriptToolError("language must be a valid non-empty language tag", category="invalid_parameters", details={"field": "language"})
    return {"videoId": video_id.strip(), "language": _normalize_language(language, field="language") if language is not None else None}


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


def build_transcripts_get_transcript_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the transcript retrieval tool.

    :return: JSON-compatible public metadata.
    """
    return {"name": TRANSCRIPTS_GET_TRANSCRIPT_TOOL_NAME, "family": "transcripts", "parameters": ["videoId", "language"], "inputContract": TRANSCRIPTS_GET_TRANSCRIPT_INPUT_SCHEMA, "compositionBoundary": {"kind": "transcript_retrieval", "lowerLayerDependencies": ["captions.list", "captions.download"], "boundedness": "one video; one caption discovery; at most one caption download", "partialResultPolicy": "Return transcript unavailable when no accessible exact-language track exists."}, "lowerLayerDependencies": ["captions.list", "captions.download"], "languageSelection": ["explicit", "configured_default", "english_fallback"], "responseFields": [{"fieldName": "videoId", "category": "normalized", "source": "request"}, {"fieldName": "language", "category": "normalized", "source": "resolved language"}, {"fieldName": "languageSource", "category": "normalized", "source": "selection policy"}, {"fieldName": "captionTrackId", "category": "raw_upstream", "source": "captions.list"}, {"fieldName": "text", "category": "normalized", "source": "captions.download VTT"}], "authAndQuotaNotes": ["Official captions require eligible OAuth-authorized access.", "Successful retrieval uses captions.list and captions.download quota."], "caveats": ["Exact language matching only; no translation or other-language fallback.", "Timestamped segments are not returned by this tool."], "errorCategories": ["invalid_parameters", "transcript_unavailable", "authorization_sensitive_data", "quota_exhaustion", "upstream_failure"], "errorGuidance": {"invalid_parameters": "Correct the named request or configuration field and retry.", "transcript_unavailable": "Request an accessible language or a different video.", "authorization_sensitive_data": "Obtain eligible caption authorization.", "quota_exhaustion": "Retry after capacity is available.", "upstream_failure": "Retry when the source service is available."}}


def build_transcripts_get_transcript_tool_descriptor(**dependencies: Any) -> dict[str, Any]:
    """Build the executable MCP descriptor for transcript retrieval.

    :param dependencies: Optional injected handler and configuration dependencies.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {"name": TRANSCRIPTS_GET_TRANSCRIPT_TOOL_NAME, "description": "Retrieve complete transcript text for one video in a requested or default language.", "inputSchema": TRANSCRIPTS_GET_TRANSCRIPT_INPUT_SCHEMA, "handler": build_transcripts_get_transcript_handler(**dependencies), "metadata": build_transcripts_get_transcript_metadata()}
