"""Normalized public playlist-detail tools.

The module owns concrete single-playlist behavior for the playlists family.
"""

from __future__ import annotations

import re
from typing import Any

from mcp_server.tools.youtube_common.conventions import (
    safe_upstream_error_message,
    sanitize_error_details,
)
from mcp_server.tools.youtube_common.playlist_items import (
    PlaylistItemsListToolError,
    build_playlist_items_list_handler,
)
from mcp_server.tools.youtube_common.playlists import (
    PlaylistsListToolError,
    build_playlists_list_handler,
)
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("playlists")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools

PLAYLISTS_GET_PLAYLIST_TOOL_NAME = "playlists_getPlaylist"
PLAYLISTS_GET_PLAYLIST_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_PLAYLIST_ITEMS_TOOL_NAME = "playlists_getPlaylistItems"
PLAYLISTS_GET_PLAYLIST_ITEMS_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_PLAYLIST_ITEMS_DEFAULT_MAX_RESULTS = 25
PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS = 50
PLAYLISTS_GET_VIDEO_TRANSCRIPTS_TOOL_NAME = "playlists_getVideoTranscripts"
PLAYLISTS_GET_VIDEO_TRANSCRIPTS_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_VIDEO_TRANSCRIPTS_DEFAULT_MAX_RESULTS = 10
PLAYLISTS_GET_VIDEO_TRANSCRIPTS_MAX_RESULTS = 50
PLAYLISTS_SEARCH_ITEMS_TOOL_NAME = "playlists_searchItems"
PLAYLISTS_SEARCH_ITEMS_PARTS = "snippet,contentDetails,status"
PLAYLISTS_SEARCH_ITEMS_DEFAULT_MAX_RESULTS = 25
PLAYLISTS_SEARCH_ITEMS_MAX_RESULTS = 50
PLAYLISTS_SEARCH_ITEMS_PAGE_SIZE = 50
PLAYLISTS_SEARCH_ITEMS_MAX_INSPECTED_ENTRIES = 500
PLAYLISTS_SEARCH_ITEMS_MAX_PAGES = PLAYLISTS_SEARCH_ITEMS_MAX_INSPECTED_ENTRIES // PLAYLISTS_SEARCH_ITEMS_PAGE_SIZE
PLAYLISTS_GET_PLAYLIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["playlistId"],
    "properties": {"playlistId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
PLAYLISTS_GET_PLAYLIST_ITEMS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["playlistId"],
    "properties": {
        "playlistId": {"type": "string", "minLength": 1},
        "maxResults": {
            "type": "integer",
            "minimum": 1,
            "maximum": PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS,
            "default": PLAYLISTS_GET_PLAYLIST_ITEMS_DEFAULT_MAX_RESULTS,
        },
    },
    "additionalProperties": False,
}
PLAYLISTS_GET_VIDEO_TRANSCRIPTS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["playlistId"],
    "properties": {
        "playlistId": {"type": "string", "minLength": 1},
        "language": {"type": "string", "minLength": 1},
        "maxResults": {
            "type": "integer",
            "minimum": 1,
            "maximum": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_MAX_RESULTS,
            "default": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_DEFAULT_MAX_RESULTS,
        },
    },
    "additionalProperties": False,
}
_PLAYLIST_TRANSCRIPT_LANGUAGE_PATTERN = re.compile(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*")
PLAYLISTS_SEARCH_ITEMS_INPUT_SCHEMA = {
    "type": "object",
    "required": ["playlistId", "query"],
    "properties": {
        "playlistId": {"type": "string", "minLength": 1},
        "query": {"type": "string", "minLength": 1},
        "maxResults": {
            "type": "integer",
            "minimum": 1,
            "maximum": PLAYLISTS_SEARCH_ITEMS_MAX_RESULTS,
            "default": PLAYLISTS_SEARCH_ITEMS_DEFAULT_MAX_RESULTS,
        },
    },
    "additionalProperties": False,
}


class PlaylistsGetPlaylistToolError(ValueError):
    """Represent a safe caller-facing ``playlists_getPlaylist`` failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public playlist-detail error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistsGetPlaylistItemsToolError(ValueError):
    """Represent a safe caller-facing playlist-item retrieval failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public playlist-item error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistsGetVideoTranscriptsToolError(ValueError):
    """Represent a safe caller-facing playlist transcript fan-out failure.

    :param message: Caller-safe explanation of the failure.
    :param category: Stable public failure category.
    :param details: Candidate caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public playlist transcript error.

        :param message: Caller-safe explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistsSearchItemsToolError(ValueError):
    """Represent a safe caller-facing playlist-item search failure.

    :param message: Caller-facing explanation of the failure.
    :param category: Stable public failure category.
    :param details: Optional caller-safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the normalized public playlist-search error.

        :param message: Caller-facing explanation of the failure.
        :param category: Stable public failure category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def build_playlists_get_playlist_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the concrete playlist-detail tool.

    :return: JSON-compatible public metadata without a representative-only marker.
    """
    return {
        "name": PLAYLISTS_GET_PLAYLIST_TOOL_NAME,
        "family": "playlists",
        "parameters": ["playlistId"],
        "inputContract": PLAYLISTS_GET_PLAYLIST_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_retrieval",
            "lowerLayerDependencies": ["playlists.list"],
            "boundedness": "one playlist; one lookup",
            "partialResultPolicy": "Preserve unavailable public fields without inventing values.",
        },
        "lowerLayerDependencies": ["playlists.list"],
        "authAndQuotaNotes": ["Uses the playlists.list direct identifier path and its one-unit quota behavior."],
        "responseFields": [
            {"fieldName": "playlistId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "title", "category": "normalized", "source": "snippet.title"},
            {"fieldName": "description", "category": "normalized", "source": "snippet.description"},
            {"fieldName": "channelId", "category": "normalized", "source": "snippet.channelId"},
            {"fieldName": "channelTitle", "category": "normalized", "source": "snippet.channelTitle"},
            {"fieldName": "publishedAt", "category": "normalized", "source": "snippet.publishedAt"},
            {"fieldName": "thumbnails", "category": "normalized", "source": "snippet.thumbnails"},
            {"fieldName": "privacyStatus", "category": "normalized", "source": "status.privacyStatus"},
            {"fieldName": "itemCount", "category": "normalized", "source": "contentDetails.itemCount"},
            {"fieldName": "fieldProvenance", "category": "normalized", "source": "public contract"},
            {"fieldName": "contentScope", "category": "normalized", "source": "public contract"},
        ],
        "contentScope": {
            "playlistItemsIncluded": False,
            "playlistItemsTool": "playlists_getPlaylistItems",
            "stateObservedAtRequest": True,
        },
        "stateVariability": "Public metadata is observed at request time and may change later.",
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible playlist identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_playlists_get_playlist_items_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for playlist-item retrieval.

    :return: JSON-compatible executable metadata without a representative marker.
    """
    return {
        "name": PLAYLISTS_GET_PLAYLIST_ITEMS_TOOL_NAME,
        "family": "playlists",
        "parameters": ["playlistId", "maxResults"],
        "inputContract": PLAYLISTS_GET_PLAYLIST_ITEMS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "source_ordered_collection",
            "lowerLayerDependencies": ["playlistItems.list"],
            "boundedness": "one playlist; one listing; 1-50 items",
            "partialResultPolicy": "Retain exposed unavailable entries in source order without fabricating details.",
        },
        "lowerLayerDependencies": ["playlistItems.list"],
        "authAndQuotaNotes": ["Uses one public playlistItems.list request and its one-unit quota behavior."],
        "limitPolicy": {
            "default": PLAYLISTS_GET_PLAYLIST_ITEMS_DEFAULT_MAX_RESULTS,
            "minimum": 1,
            "maximum": PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS,
            "continuationInputAccepted": False,
        },
        "collectionPolicy": {
            "ordering": "source_playlist_order_at_request_time",
            "rankingApplied": False,
            "paginationTraversed": False,
            "emptyResult": "successful_empty_collection",
            "unavailableEntry": "retain_and_mark_unavailable",
        },
        "responseFields": [
            {"fieldName": "items.position", "category": "raw_upstream", "source": "snippet.position"},
            {"fieldName": "items.playlistItemId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "items.videoId", "category": "raw_upstream", "source": "contentDetails.videoId"},
            {"fieldName": "items.title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "items.channelId", "category": "raw_upstream", "source": "snippet.channelId"},
            {"fieldName": "items.channelTitle", "category": "raw_upstream", "source": "snippet.channelTitle"},
            {"fieldName": "items.publishedAt", "category": "raw_upstream", "source": "snippet.publishedAt"},
            {"fieldName": "items.availabilityState", "category": "normalized", "source": "public contract"},
            {"fieldName": "playlistId", "category": "normalized", "source": "validated request"},
            {"fieldName": "returnedCount", "category": "normalized", "source": "public contract"},
            {"fieldName": "appliedLimit", "category": "normalized", "source": "validated request"},
            {"fieldName": "isLimited", "category": "normalized", "source": "source continuation signal"},
            {"fieldName": "collectionContext", "category": "normalized", "source": "public contract"},
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible playlist identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def build_playlists_get_video_transcripts_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for bounded playlist transcript fan-out.

    :return: JSON-compatible executable metadata without a representative marker.
    """
    return {
        "name": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_TOOL_NAME,
        "family": "playlists",
        "parameters": ["playlistId", "language", "maxResults"],
        "inputContract": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "bounded_playlist_transcript_fan_out",
            "lowerLayerDependencies": ["playlistItems.list", "captions.list", "captions.download"],
            "boundedness": "one playlist listing; 1-50 items; at most one caption retrieval per eligible item",
            "partialResultPolicy": "Return source-ordered per-video outcomes without discarding successful transcripts.",
        },
        "lowerLayerDependencies": ["playlistItems.list", "captions.list", "captions.download"],
        "limitPolicy": {
            "default": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_DEFAULT_MAX_RESULTS,
            "minimum": 1,
            "maximum": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_MAX_RESULTS,
            "continuationInputAccepted": False,
        },
        "languageSelection": ["explicit", "configured_default", "english_fallback"],
        "languagePolicy": "Exact normalized language matching only; no translation or other-language fallback.",
        "fanOutPolicy": {
            "playlistListingCount": 1,
            "maximumTranscriptAttempts": "appliedLimit",
            "sourceOrderPreserved": True,
            "paginationTraversed": False,
            "additionalItemsSignal": "nextPageToken",
        },
        "authAndQuotaNotes": [
            "Playlist enumeration uses configured public-read capability.",
            "Caption retrieval requires eligible authorized access and multiplies capacity use across the bounded fan-out.",
        ],
        "responseFields": [
            {"fieldName": "items.position", "category": "raw_upstream", "source": "snippet.position"},
            {"fieldName": "items.playlistItemId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "items.videoId", "category": "raw_upstream", "source": "contentDetails.videoId"},
            {"fieldName": "items.transcriptStatus", "category": "normalized", "source": "public contract"},
            {"fieldName": "items.language", "category": "raw_upstream", "source": "caption retrieval"},
            {"fieldName": "items.languageSource", "category": "normalized", "source": "request language resolution"},
            {"fieldName": "items.captionTrackId", "category": "raw_upstream", "source": "caption retrieval"},
            {"fieldName": "items.segments.text", "category": "normalized", "source": "timestamped caption VTT"},
            {"fieldName": "items.segments.startTimeSeconds", "category": "normalized", "source": "timestamped caption VTT"},
            {"fieldName": "items.segments.endTimeSeconds", "category": "normalized", "source": "timestamped caption VTT"},
            {"fieldName": "playlistId", "category": "normalized", "source": "validated request"},
            {"fieldName": "language", "category": "normalized", "source": "request language resolution"},
            {"fieldName": "languageSource", "category": "normalized", "source": "request language resolution"},
            {"fieldName": "fanOutSummary", "category": "normalized", "source": "public contract"},
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "source_unavailable",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible playlist identifier.",
            "authorization_sensitive_data": "Obtain eligible caption authorization.",
            "quota_exhaustion": "Retry after capacity is available.",
            "source_unavailable": "Retry when the source is available.",
            "upstream_failure": "Retry when the source is available.",
        },
    }


def build_playlists_search_items_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for bounded playlist-item search.

    :return: JSON-compatible executable metadata for the composite search tool.
    """
    return {
        "name": PLAYLISTS_SEARCH_ITEMS_TOOL_NAME,
        "family": "playlists",
        "parameters": ["playlistId", "query", "maxResults"],
        "inputContract": PLAYLISTS_SEARCH_ITEMS_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "bounded_playlist_item_literal_search",
            "lowerLayerDependencies": ["playlists.list", "playlistItems.list", "in_server_literal_search"],
            "boundedness": "one playlist lookup; up to 10 item pages; at most 500 inspected entries; 1-50 returned matches",
            "partialResultPolicy": "Report incomplete coverage without exposing private continuation state.",
        },
        "lowerLayerDependencies": ["playlists.list", "playlistItems.list", "in_server_literal_search"],
        "authAndQuotaNotes": [
            "Uses one playlist availability lookup and up to ten playlist-item listing requests.",
        ],
        "limitPolicy": {
            "default": PLAYLISTS_SEARCH_ITEMS_DEFAULT_MAX_RESULTS,
            "minimum": 1,
            "maximum": PLAYLISTS_SEARCH_ITEMS_MAX_RESULTS,
            "continuationInputAccepted": False,
        },
        "searchPolicy": {
            "matching": "case_insensitive_literal_phrase",
            "searchableFields": ["title", "description", "channelTitle", "videoId"],
            "matchingFieldOrder": ["title", "description", "channelTitle", "videoId"],
            "ordering": "source_playlist_order_at_request_time",
            "rankingApplied": False,
            "paginationTraversed": True,
            "maximumInspectedEntries": PLAYLISTS_SEARCH_ITEMS_MAX_INSPECTED_ENTRIES,
            "excludedSearchTypes": ["semantic", "synonym", "fuzzy", "transcript"],
        },
        "responseFields": [
            {"fieldName": "items.position", "category": "raw_upstream", "source": "snippet.position"},
            {"fieldName": "items.playlistItemId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "items.videoId", "category": "raw_upstream", "source": "contentDetails.videoId"},
            {"fieldName": "items.title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "items.description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "items.channelId", "category": "raw_upstream", "source": "snippet.channelId"},
            {"fieldName": "items.channelTitle", "category": "raw_upstream", "source": "snippet.channelTitle"},
            {"fieldName": "items.publishedAt", "category": "raw_upstream", "source": "snippet.publishedAt"},
            {"fieldName": "items.availabilityState", "category": "normalized", "source": "public contract"},
            {"fieldName": "items.matchingFields", "category": "normalized", "source": "literal comparison"},
            {"fieldName": "playlistId", "category": "normalized", "source": "validated request"},
            {"fieldName": "query", "category": "normalized", "source": "normalized request"},
            {"fieldName": "returnedCount", "category": "normalized", "source": "public contract"},
            {"fieldName": "appliedLimit", "category": "normalized", "source": "validated request"},
            {"fieldName": "searchCoverage", "category": "normalized", "source": "public contract"},
            {"fieldName": "additionalMatchesOmitted", "category": "normalized", "source": "public contract"},
            {"fieldName": "searchContext", "category": "normalized", "source": "public contract"},
            {"fieldName": "fieldProvenance", "category": "normalized", "source": "public contract"},
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible playlist identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
        },
    }


def validate_playlists_get_playlist_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate and normalize one public playlist-detail request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one stripped playlist identifier.
    :raises PlaylistsGetPlaylistToolError: If the request is missing, invalid, or unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsGetPlaylistToolError(
            "playlists_getPlaylist arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"playlistId"}
    if unexpected_fields:
        raise PlaylistsGetPlaylistToolError(
            "playlists_getPlaylist received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    playlist_id = arguments.get("playlistId")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsGetPlaylistToolError(
            "playlists_getPlaylist requires a non-empty playlistId",
            category="invalid_parameters",
            details={"field": "playlistId"},
        )
    return {"playlistId": playlist_id.strip()}


def validate_playlists_get_playlist_items_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public playlist-item retrieval request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request with a stripped identifier and applied limit.
    :raises PlaylistsGetPlaylistItemsToolError: If the request is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsGetPlaylistItemsToolError(
            "playlists_getPlaylistItems arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"playlistId", "maxResults"}
    if unexpected_fields:
        raise PlaylistsGetPlaylistItemsToolError(
            "playlists_getPlaylistItems received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    playlist_id = arguments.get("playlistId")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsGetPlaylistItemsToolError(
            "playlists_getPlaylistItems requires a non-empty playlistId",
            category="invalid_parameters",
            details={"field": "playlistId"},
        )
    max_results = arguments.get("maxResults", PLAYLISTS_GET_PLAYLIST_ITEMS_DEFAULT_MAX_RESULTS)
    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise PlaylistsGetPlaylistItemsToolError(
            "maxResults must be an integer",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if not 1 <= max_results <= PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS:
        raise PlaylistsGetPlaylistItemsToolError(
            f"maxResults must be between 1 and {PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS}",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    return {"playlistId": playlist_id.strip(), "maxResults": max_results}


def _normalize_playlist_transcript_language(value: str, *, field: str) -> str:
    """Validate and canonicalize one playlist transcript language tag.

    :param value: Candidate language text.
    :param field: Caller-visible field name for a validation error.
    :return: Canonicalized language tag.
    :raises PlaylistsGetVideoTranscriptsToolError: If the language tag is malformed.
    """
    text = value.strip() if isinstance(value, str) else ""
    if not text or not _PLAYLIST_TRANSCRIPT_LANGUAGE_PATTERN.fullmatch(text):
        raise PlaylistsGetVideoTranscriptsToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": field},
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


def validate_playlists_get_video_transcripts_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public playlist transcript request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized playlist identifier, optional language, and applied limit.
    :raises PlaylistsGetVideoTranscriptsToolError: If public input is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsGetVideoTranscriptsToolError(
            "playlists_getVideoTranscripts arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"playlistId", "language", "maxResults"}
    if unexpected_fields:
        raise PlaylistsGetVideoTranscriptsToolError(
            "playlists_getVideoTranscripts received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    playlist_id = arguments.get("playlistId")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsGetVideoTranscriptsToolError(
            "playlists_getVideoTranscripts requires a non-empty playlistId",
            category="invalid_parameters",
            details={"field": "playlistId"},
        )
    language = arguments.get("language")
    if language is not None and not isinstance(language, str):
        raise PlaylistsGetVideoTranscriptsToolError(
            "language must be a valid non-empty language tag",
            category="invalid_parameters",
            details={"field": "language"},
        )
    max_results = arguments.get("maxResults", PLAYLISTS_GET_VIDEO_TRANSCRIPTS_DEFAULT_MAX_RESULTS)
    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise PlaylistsGetVideoTranscriptsToolError(
            "maxResults must be an integer",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if not 1 <= max_results <= PLAYLISTS_GET_VIDEO_TRANSCRIPTS_MAX_RESULTS:
        raise PlaylistsGetVideoTranscriptsToolError(
            f"maxResults must be between 1 and {PLAYLISTS_GET_VIDEO_TRANSCRIPTS_MAX_RESULTS}",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    return {
        "playlistId": playlist_id.strip(),
        "language": _normalize_playlist_transcript_language(language, field="language") if language is not None else None,
        "maxResults": max_results,
    }


def validate_playlists_search_items_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one public playlist-item search request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized identifier, literal query, and applied result limit.
    :raises PlaylistsSearchItemsToolError: If the request is invalid or unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsSearchItemsToolError(
            "playlists_searchItems arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"playlistId", "query", "maxResults"}
    if unexpected_fields:
        raise PlaylistsSearchItemsToolError(
            "playlists_searchItems received an unsupported field",
            category="invalid_parameters",
            details={"field": min(unexpected_fields)},
        )
    playlist_id = arguments.get("playlistId")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsSearchItemsToolError(
            "playlists_searchItems requires a non-empty playlistId",
            category="invalid_parameters",
            details={"field": "playlistId"},
        )
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise PlaylistsSearchItemsToolError(
            "playlists_searchItems requires a non-empty query",
            category="invalid_parameters",
            details={"field": "query"},
        )
    max_results = arguments.get("maxResults", PLAYLISTS_SEARCH_ITEMS_DEFAULT_MAX_RESULTS)
    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise PlaylistsSearchItemsToolError(
            "maxResults must be an integer",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    if not 1 <= max_results <= PLAYLISTS_SEARCH_ITEMS_MAX_RESULTS:
        raise PlaylistsSearchItemsToolError(
            f"maxResults must be between 1 and {PLAYLISTS_SEARCH_ITEMS_MAX_RESULTS}",
            category="invalid_parameters",
            details={"field": "maxResults"},
        )
    return {"playlistId": playlist_id.strip(), "query": " ".join(query.split()), "maxResults": max_results}


def _playlist_lookup_arguments(playlist_id: str) -> dict[str, str]:
    """Build the one direct lower-layer request for playlist details.

    :param playlist_id: Validated public playlist identifier.
    :return: Direct playlists-list arguments for required public detail groups.
    """
    return {"part": PLAYLISTS_GET_PLAYLIST_PARTS, "id": playlist_id}


def _playlist_items_lookup_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the one playlist-scoped lower-layer item listing request.

    :param arguments: Validated public playlist-item request.
    :return: Direct playlist-item listing arguments with the applied limit.
    """
    return {
        "part": PLAYLISTS_GET_PLAYLIST_ITEMS_PARTS,
        "playlistId": arguments["playlistId"],
        "maxResults": arguments["maxResults"],
    }


def _playlist_video_transcript_lookup_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build the one bounded playlist-item lookup for transcript fan-out.

    :param arguments: Validated public playlist transcript request.
    :return: Lower-layer playlist-item listing arguments with the applied limit.
    """
    return {
        "part": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_PARTS,
        "playlistId": arguments["playlistId"],
        "maxResults": arguments["maxResults"],
    }


def _playlist_search_page_arguments(playlist_id: str, page_cursor: str | None = None) -> dict[str, Any]:
    """Build one private bounded lower-layer playlist-item search page request.

    :param playlist_id: Validated public playlist identifier.
    :param page_cursor: Private cursor from the preceding lower-layer result.
    :return: Lower-layer item-list arguments for one 50-entry page.
    """
    arguments: dict[str, Any] = {
        "part": PLAYLISTS_SEARCH_ITEMS_PARTS,
        "playlistId": playlist_id,
        "maxResults": PLAYLISTS_SEARCH_ITEMS_PAGE_SIZE,
    }
    if page_cursor:
        arguments["pageToken"] = page_cursor
    return arguments


def _source_text(source: dict[str, Any], field: str) -> str | None:
    """Return one usable source text value when present.

    :param source: Candidate source mapping.
    :param field: Source field name.
    :return: Nonblank text value or ``None`` when unavailable.
    """
    value = source.get(field)
    return value if isinstance(value, str) and value else None


def _playlist_item_availability(item: dict[str, Any], video_id: str | None) -> str:
    """Classify an exposed playlist entry using safe source availability signals.

    :param item: Source playlist-item mapping.
    :param video_id: Usable public video identity when available.
    :return: ``available`` or ``unavailable`` public availability state.
    """
    status = item.get("status") if isinstance(item.get("status"), dict) else {}
    privacy_status = _source_text(status, "privacyStatus")
    if not video_id or privacy_status in {"private", "deleted"}:
        return "unavailable"
    return "available"


def _normalize_playlist_item(item: Any) -> dict[str, Any]:
    """Normalize one exposed source playlist item without changing its order.

    :param item: Candidate source playlist-item value.
    :return: Stable public item with available source fields and availability state.
    """
    source = item if isinstance(item, dict) else {}
    snippet = source.get("snippet") if isinstance(source.get("snippet"), dict) else {}
    content_details = source.get("contentDetails") if isinstance(source.get("contentDetails"), dict) else {}
    resource_id = snippet.get("resourceId") if isinstance(snippet.get("resourceId"), dict) else {}
    video_id = _source_text(content_details, "videoId") or _source_text(resource_id, "videoId")
    availability_state = _playlist_item_availability(source, video_id)
    result: dict[str, Any] = {}
    position = snippet.get("position")
    if isinstance(position, int) and not isinstance(position, bool):
        result["position"] = position
    playlist_item_id = _source_text(source, "id")
    if playlist_item_id:
        result["playlistItemId"] = playlist_item_id
    if availability_state == "available":
        result["videoId"] = video_id
        for field in ("title", "channelId", "channelTitle", "publishedAt"):
            value = _source_text(snippet, field)
            if value:
                result[field] = value
    result["availabilityState"] = availability_state
    return result


def _playlist_search_match(item: Any, normalized_query: str) -> dict[str, Any] | None:
    """Return one normalized matching item when exposed fields contain the query.

    :param item: Candidate lower-layer playlist item.
    :param normalized_query: Case-folded literal phrase to search.
    :return: Normalized matching item or ``None`` when no exposed field matches.
    """
    source = item if isinstance(item, dict) else {}
    snippet = source.get("snippet") if isinstance(source.get("snippet"), dict) else {}
    content_details = source.get("contentDetails") if isinstance(source.get("contentDetails"), dict) else {}
    resource_id = snippet.get("resourceId") if isinstance(snippet.get("resourceId"), dict) else {}
    video_id = _source_text(content_details, "videoId") or _source_text(resource_id, "videoId")
    searchable_values = {
        "title": _source_text(snippet, "title"),
        "description": _source_text(snippet, "description"),
        "channelTitle": _source_text(snippet, "channelTitle"),
        "videoId": video_id,
    }
    matching_fields = [
        field_name
        for field_name in ("title", "description", "channelTitle", "videoId")
        if searchable_values[field_name] and normalized_query in searchable_values[field_name].casefold()
    ]
    if not matching_fields:
        return None

    result: dict[str, Any] = {}
    position = snippet.get("position")
    if isinstance(position, int) and not isinstance(position, bool):
        result["position"] = position
    playlist_item_id = _source_text(source, "id")
    if playlist_item_id:
        result["playlistItemId"] = playlist_item_id
    source_values = {
        "videoId": video_id,
        "title": _source_text(snippet, "title"),
        "description": _source_text(snippet, "description"),
        "channelId": _source_text(snippet, "channelId"),
        "channelTitle": _source_text(snippet, "channelTitle"),
        "publishedAt": _source_text(snippet, "publishedAt"),
    }
    for field_name, value in source_values.items():
        if value:
            result[field_name] = value
    result["availabilityState"] = _playlist_item_availability(source, video_id)
    result["matchingFields"] = matching_fields
    return result


def _playlist_search_availability(payload: Any) -> None:
    """Require one usable public playlist before searching its entries.

    :param payload: Lower-layer playlist-list response.
    :raises PlaylistsSearchItemsToolError: If the playlist cannot be safely retrieved.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise PlaylistsSearchItemsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    playlist_id = items[0].get("id")
    if not isinstance(playlist_id, str) or not playlist_id:
        raise PlaylistsSearchItemsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )


def _playlist_search_result(
    *,
    arguments: dict[str, Any],
    matches: list[dict[str, Any]],
    inspected_entry_count: int,
    is_complete: bool,
    termination_reason: str,
    additional_matches_omitted: bool | None,
) -> dict[str, Any]:
    """Build the normalized public result for one completed playlist search.

    :param arguments: Validated public search request.
    :param matches: Source-ordered matching items up to the applied limit.
    :param inspected_entry_count: Number of source entries inspected.
    :param is_complete: Whether all accessible entries were inspected.
    :param termination_reason: Documented reason traversal stopped.
    :param additional_matches_omitted: Known or unknown post-limit match state.
    :return: Stable search result with provenance and coverage context.
    """
    return {
        "playlistId": arguments["playlistId"],
        "query": arguments["query"].casefold(),
        "items": matches,
        "returnedCount": len(matches),
        "appliedLimit": arguments["maxResults"],
        "searchCoverage": {
            "inspectedEntryCount": inspected_entry_count,
            "isComplete": is_complete,
            "terminationReason": termination_reason,
        },
        "additionalMatchesOmitted": additional_matches_omitted,
        "searchContext": {
            "matching": "case_insensitive_literal_phrase",
            "searchableFields": ["title", "description", "channelTitle", "videoId"],
            "ordering": "source_playlist_order_at_request_time",
            "rankingApplied": False,
            "excludedSearchTypes": ["semantic", "synonym", "fuzzy", "transcript"],
        },
        "fieldProvenance": {
            "items.position": "raw_upstream",
            "items.playlistItemId": "raw_upstream",
            "items.videoId": "raw_upstream",
            "items.title": "raw_upstream",
            "items.description": "raw_upstream",
            "items.channelId": "raw_upstream",
            "items.channelTitle": "raw_upstream",
            "items.publishedAt": "raw_upstream",
            "items.availabilityState": "normalized",
            "items.matchingFields": "normalized",
            "playlistId": "normalized",
            "query": "normalized",
            "returnedCount": "normalized",
            "appliedLimit": "normalized",
            "searchCoverage": "normalized",
            "additionalMatchesOmitted": "normalized",
            "searchContext": "normalized",
        },
    }


def normalize_playlists_get_playlist_items_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize one successful bounded lower-layer playlist-item response.

    :param payload: Lower-layer result containing source playlist items.
    :param arguments: Validated public request used for the listing.
    :return: Source-ordered public collection with counts and provenance.
    """
    source_items = payload.get("items") if isinstance(payload, dict) else []
    items = [_normalize_playlist_item(item) for item in source_items] if isinstance(source_items, list) else []
    is_limited = isinstance(payload, dict) and isinstance(payload.get("nextPageToken"), str) and bool(payload["nextPageToken"])
    return {
        "playlistId": arguments["playlistId"],
        "items": items,
        "returnedCount": len(items),
        "appliedLimit": arguments["maxResults"],
        "isLimited": is_limited,
        "collectionContext": {
            "source": "playlist_items",
            "ordering": "source_playlist_order_at_request_time",
            "rankingApplied": False,
            "paginationTraversed": False,
            "publicContentOnly": True,
            "requestTimeVariability": "playlist_can_change",
        },
        "fieldProvenance": {
            "items.position": "raw_upstream",
            "items.playlistItemId": "raw_upstream",
            "items.videoId": "raw_upstream",
            "items.title": "raw_upstream",
            "items.channelId": "raw_upstream",
            "items.channelTitle": "raw_upstream",
            "items.publishedAt": "raw_upstream",
            "items.availabilityState": "normalized",
            "playlistId": "normalized",
            "returnedCount": "normalized",
            "appliedLimit": "normalized",
            "isLimited": "normalized",
            "collectionContext": "normalized",
        },
    }


def _copy_if_present(
    result: dict[str, Any],
    provenance: dict[str, str],
    source: dict[str, Any],
    source_name: str,
    result_name: str,
) -> None:
    """Copy one available source value and record its normalized provenance.

    :param result: Result mapping being assembled.
    :param provenance: Field-provenance mapping being assembled.
    :param source: Source mapping containing the candidate value.
    :param source_name: Source field name.
    :param result_name: Public result field name.
    """
    if source_name in source:
        result[result_name] = source[source_name]
        provenance[result_name] = "normalized"


def normalize_playlists_get_playlist_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize the first available lower-layer playlist item.

    :param payload: Lower-layer result containing an ``items`` collection.
    :return: Stable public detail fields, provenance, and playlist-item scope guidance.
    :raises PlaylistsGetPlaylistToolError: If no usable public playlist is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise PlaylistsGetPlaylistToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    item = items[0]
    playlist_id = item.get("id")
    if not isinstance(playlist_id, str) or not playlist_id:
        raise PlaylistsGetPlaylistToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
    content_details = item.get("contentDetails") if isinstance(item.get("contentDetails"), dict) else {}
    status = item.get("status") if isinstance(item.get("status"), dict) else {}
    result: dict[str, Any] = {"playlistId": playlist_id}
    provenance = {"playlistId": "raw_upstream"}
    for field in ("title", "description", "channelId", "channelTitle", "publishedAt", "thumbnails"):
        _copy_if_present(result, provenance, snippet, field, field)
    _copy_if_present(result, provenance, status, "privacyStatus", "privacyStatus")
    _copy_if_present(result, provenance, content_details, "itemCount", "itemCount")
    provenance["contentScope"] = "normalized"
    result["fieldProvenance"] = provenance
    result["contentScope"] = {
        "playlistItemsIncluded": False,
        "playlistItemsTool": "playlists_getPlaylistItems",
        "stateObservedAtRequest": True,
    }
    return result


def _map_playlists_list_error(error: PlaylistsListToolError) -> PlaylistsGetPlaylistToolError:
    """Translate one lower-layer error to a safe public playlist-detail error.

    :param error: Safe lower-layer playlist lookup error.
    :return: Public error with documented category and sanitized details.
    """
    if error.category in {"resource_not_found", "removed"}:
        return PlaylistsGetPlaylistToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return PlaylistsGetPlaylistToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=error.details,
    )


def _map_playlist_items_list_error(error: PlaylistItemsListToolError) -> PlaylistsGetPlaylistItemsToolError:
    """Translate one lower-layer item-list error to a safe public error.

    :param error: Safe lower-layer playlist-item listing error.
    :return: Public error with documented category and sanitized details.
    """
    if error.category in {"resource_not_found", "removed"}:
        return PlaylistsGetPlaylistItemsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return PlaylistsGetPlaylistItemsToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=error.details,
    )


def _map_playlist_items_list_error_to_video_transcripts(
    error: PlaylistItemsListToolError,
) -> PlaylistsGetVideoTranscriptsToolError:
    """Translate one playlist-item listing error to the fan-out public taxonomy.

    :param error: Safe lower-layer playlist-item listing error.
    :return: Safe whole-request playlist transcript error.
    """
    if error.category in {"resource_not_found", "removed"}:
        return PlaylistsGetVideoTranscriptsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "source_unavailable",
    }.get(error.category, "upstream_failure")
    return PlaylistsGetVideoTranscriptsToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=error.details,
    )


def _map_playlists_list_error_to_search(error: PlaylistsListToolError) -> PlaylistsSearchItemsToolError:
    """Translate a playlist availability failure to the public search taxonomy.

    :param error: Safe lower-layer playlist lookup error.
    :return: Public playlist-search error with sanitized details.
    """
    if error.category in {"resource_not_found", "removed"}:
        return PlaylistsSearchItemsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return PlaylistsSearchItemsToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=error.details,
    )


def _map_playlist_items_list_error_to_search(error: PlaylistItemsListToolError) -> PlaylistsSearchItemsToolError:
    """Translate a playlist-item listing failure to the public search taxonomy.

    :param error: Safe lower-layer playlist-item listing error.
    :return: Public playlist-search error with sanitized details.
    """
    if error.category in {"resource_not_found", "removed"}:
        return PlaylistsSearchItemsToolError(
            "The requested playlist is unavailable",
            category="unavailable_resource",
            details={"resource": "playlist"},
        )
    public_category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return PlaylistsSearchItemsToolError(
        safe_upstream_error_message(),
        category=public_category,
        details=error.details,
    )


def build_playlists_get_playlist_handler(*, lookup=None):
    """Build a callable handler for one normalized public playlist lookup.

    :param lookup: Optional lower-layer lookup override for tests.
    :return: Callable that validates, retrieves, and normalizes one playlist.
    """
    selected_lookup = lookup or build_playlists_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated playlist-detail request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized public detail result for one available playlist.
        :raises PlaylistsGetPlaylistToolError: If validation, lookup, or normalization fails.
        """
        normalized = validate_playlists_get_playlist_arguments(arguments)
        try:
            payload = selected_lookup(_playlist_lookup_arguments(normalized["playlistId"]))
        except PlaylistsListToolError as exc:
            raise _map_playlists_list_error(exc) from exc
        return normalize_playlists_get_playlist_result(payload)

    return handler


def build_playlists_get_playlist_tool_descriptor(*, lookup=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``playlists_getPlaylist``.

    :param lookup: Optional lower-layer lookup override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": PLAYLISTS_GET_PLAYLIST_TOOL_NAME,
        "description": "Return normalized public details for one YouTube playlist.",
        "inputSchema": PLAYLISTS_GET_PLAYLIST_INPUT_SCHEMA,
        "handler": build_playlists_get_playlist_handler(lookup=lookup),
        "metadata": build_playlists_get_playlist_metadata(),
    }


def build_playlists_get_playlist_items_handler(*, playlist_items=None):
    """Build a callable handler for one normalized playlist-item retrieval.

    :param playlist_items: Optional lower-layer playlist-item listing override for tests.
    :return: Callable that validates, lists, and normalizes playlist entries.
    """
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated bounded playlist-item retrieval request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized source-ordered playlist-item collection.
        :raises PlaylistsGetPlaylistItemsToolError: If validation or listing fails.
        """
        normalized = validate_playlists_get_playlist_items_arguments(arguments)
        try:
            payload = selected_playlist_items(_playlist_items_lookup_arguments(normalized))
        except PlaylistItemsListToolError as exc:
            raise _map_playlist_items_list_error(exc) from exc
        return normalize_playlists_get_playlist_items_result(payload, normalized)

    return handler


def build_playlists_get_playlist_items_tool_descriptor(*, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for playlist-item retrieval.

    :param playlist_items: Optional lower-layer playlist-item listing override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": PLAYLISTS_GET_PLAYLIST_ITEMS_TOOL_NAME,
        "description": "Return normalized source-ordered videos contained in one YouTube playlist.",
        "inputSchema": PLAYLISTS_GET_PLAYLIST_ITEMS_INPUT_SCHEMA,
        "handler": build_playlists_get_playlist_items_handler(playlist_items=playlist_items),
        "metadata": build_playlists_get_playlist_items_metadata(),
    }


def _resolved_playlist_transcript_language(
    request: dict[str, Any],
    default_language: str | None,
    default_language_error: str | None,
) -> tuple[str, str]:
    """Resolve playlist transcript language from explicit, configured, and English sources.

    :param request: Validated public playlist transcript request.
    :param default_language: Optional injected configured transcript language.
    :param default_language_error: Safe invalid-configuration state supplied by runtime settings.
    :return: Resolved language and its public selection-source label.
    :raises PlaylistsGetVideoTranscriptsToolError: If configured language is invalid.
    """
    if request["language"] is not None:
        return request["language"], "explicit"
    if default_language_error:
        raise PlaylistsGetVideoTranscriptsToolError(
            "configured transcript language is invalid",
            category="invalid_parameters",
            details={"field": "YOUTUBE_TRANSCRIPT_LANG"},
        )
    if default_language:
        return _normalize_playlist_transcript_language(default_language, field="YOUTUBE_TRANSCRIPT_LANG"), "configured_default"
    return "en", "english_fallback"


def _playlist_video_transcript_error_outcome(item: dict[str, Any], error: ValueError) -> dict[str, Any]:
    """Build one safe per-video outcome from a timestamped-caption failure.

    :param item: Existing normalized playlist item identity.
    :param error: Safe child caption retrieval error.
    :return: Source-ordered public outcome without unsafe child details.
    """
    child_category = getattr(error, "category", "upstream_failure")
    status = {
        "language_unavailable": "transcript_unavailable",
        "transcript_unavailable": "transcript_unavailable",
        "authorization_sensitive_data": "authorization_sensitive_data",
        "quota_exhaustion": "quota_exhaustion",
        "source_unavailable": "source_unavailable",
    }.get(child_category, "upstream_failure")
    reason = {
        "transcript_unavailable": "No accessible transcript is available in the requested language.",
        "authorization_sensitive_data": "Caption access is restricted for this video.",
        "quota_exhaustion": "Caption retrieval capacity is currently unavailable.",
        "source_unavailable": "The caption source is temporarily unavailable.",
        "upstream_failure": "The transcript could not be retrieved safely.",
    }[status]
    return {**item, "transcriptStatus": status, "safeReason": reason}


def _playlist_video_transcript_outcome(
    source_item: Any,
    *,
    timestamped_captions,
    language: str,
    language_source: str,
) -> tuple[dict[str, Any], bool]:
    """Build one source-ordered playlist transcript outcome.

    :param source_item: Candidate lower-layer playlist item.
    :param timestamped_captions: Injected timestamped-caption handler.
    :param language: Exact resolved language forwarded to the child handler.
    :param language_source: Public request language-selection source.
    :return: Outcome and whether a caption attempt occurred.
    """
    normalized_item = _normalize_playlist_item(source_item)
    if normalized_item.get("availabilityState") != "available" or not normalized_item.get("videoId"):
        normalized_item.pop("availabilityState", None)
        return {
            **normalized_item,
            "transcriptStatus": "video_unavailable",
            "safeReason": "This playlist entry has no accessible video for transcript retrieval.",
        }, False
    try:
        payload = timestamped_captions({"videoId": normalized_item["videoId"], "language": language})
    except ValueError as exc:
        normalized_item.pop("availabilityState", None)
        return _playlist_video_transcript_error_outcome(normalized_item, exc), True
    normalized_item.pop("availabilityState", None)
    if not isinstance(payload, dict):
        return _playlist_video_transcript_error_outcome(
            normalized_item,
            ValueError("invalid transcript result"),
        ), True
    availability = payload.get("availability")
    if availability == "no_accessible_captions":
        return {
            **normalized_item,
            "transcriptStatus": "transcript_unavailable",
            "safeReason": "No accessible transcript is available in the requested language.",
        }, True
    segments = payload.get("segments")
    if availability != "available" or not isinstance(segments, list):
        return _playlist_video_transcript_error_outcome(
            normalized_item,
            ValueError("invalid transcript result"),
        ), True
    result: dict[str, Any] = {
        **normalized_item,
        "transcriptStatus": "available" if segments else "empty",
        "languageSource": language_source,
        "segments": segments,
    }
    for field in ("language", "captionTrackId"):
        value = payload.get(field)
        if isinstance(value, str) and value:
            result[field] = value
    return result, True


def _playlist_video_transcript_result(
    *,
    request: dict[str, Any],
    language: str,
    language_source: str,
    payload: Any,
    timestamped_captions,
) -> dict[str, Any]:
    """Build one completed bounded playlist transcript fan-out result.

    :param request: Validated public request with the applied limit.
    :param language: Resolved request language.
    :param language_source: Public language-selection source label.
    :param payload: Lower-layer playlist-item listing result.
    :param timestamped_captions: Injected timestamped-caption handler.
    :return: Normalized source-ordered result and fan-out summary.
    :raises PlaylistsGetVideoTranscriptsToolError: If the listing payload is malformed.
    """
    source_items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(source_items, list):
        raise PlaylistsGetVideoTranscriptsToolError(
            safe_upstream_error_message(),
            category="upstream_failure",
        )
    outcomes: list[dict[str, Any]] = []
    attempt_count = 0
    for source_item in source_items[: request["maxResults"]]:
        outcome, attempted = _playlist_video_transcript_outcome(
            source_item,
            timestamped_captions=timestamped_captions,
            language=language,
            language_source=language_source,
        )
        outcomes.append(outcome)
        attempt_count += int(attempted)
    outcome_counts: dict[str, int] = {}
    for outcome in outcomes:
        status = outcome["transcriptStatus"]
        outcome_counts[status] = outcome_counts.get(status, 0) + 1
    return {
        "playlistId": request["playlistId"],
        "language": language,
        "languageSource": language_source,
        "items": outcomes,
        "fanOutSummary": {
            "appliedLimit": request["maxResults"],
            "consideredItemCount": len(outcomes),
            "transcriptAttemptCount": attempt_count,
            "outcomeCounts": outcome_counts,
            "additionalPlaylistItemsNotAttempted": bool(payload.get("nextPageToken")) if isinstance(payload, dict) else False,
        },
        "fieldProvenance": {
            "items.position": "raw_upstream",
            "items.playlistItemId": "raw_upstream",
            "items.videoId": "raw_upstream",
            "items.transcriptStatus": "normalized",
            "items.language": "raw_upstream",
            "items.languageSource": "normalized",
            "items.captionTrackId": "raw_upstream",
            "items.segments.text": "normalized",
            "items.segments.startTimeSeconds": "normalized",
            "items.segments.endTimeSeconds": "normalized",
            "playlistId": "normalized",
            "language": "normalized",
            "languageSource": "normalized",
            "fanOutSummary": "normalized",
        },
    }


def build_playlists_get_video_transcripts_handler(
    *,
    playlist_items=None,
    timestamped_captions=None,
    default_language: str | None = None,
    default_language_error: str | None = None,
):
    """Build a callable handler for bounded playlist transcript aggregation.

    :param playlist_items: Optional injected lower-layer playlist-item handler.
    :param timestamped_captions: Optional injected timestamped-caption handler.
    :param default_language: Optional injected configured transcript language.
    :param default_language_error: Optional safe invalid-configuration state.
    :return: Callable that validates, lists, and aggregates playlist transcripts.
    """
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()
    if timestamped_captions is None:
        from mcp_server.tools.youtube_composed.transcripts import (
            build_transcripts_get_timestamped_captions_handler,
        )

        timestamped_captions = build_transcripts_get_timestamped_captions_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated bounded playlist transcript aggregation request.

        :param arguments: Caller-provided public arguments.
        :return: Source-ordered transcript outcomes and fan-out summary.
        :raises PlaylistsGetVideoTranscriptsToolError: If validation or playlist listing fails safely.
        """
        request = validate_playlists_get_video_transcripts_arguments(arguments)
        language, language_source = _resolved_playlist_transcript_language(
            request,
            default_language,
            default_language_error,
        )
        try:
            payload = selected_playlist_items(_playlist_video_transcript_lookup_arguments(request))
        except PlaylistItemsListToolError as exc:
            raise _map_playlist_items_list_error_to_video_transcripts(exc) from exc
        return _playlist_video_transcript_result(
            request=request,
            language=language,
            language_source=language_source,
            payload=payload,
            timestamped_captions=timestamped_captions,
        )

    return handler


def build_playlists_get_video_transcripts_tool_descriptor(
    *,
    playlist_items=None,
    timestamped_captions=None,
    default_language: str | None = None,
    default_language_error: str | None = None,
) -> dict[str, Any]:
    """Build the executable MCP descriptor for playlist transcript aggregation.

    :param playlist_items: Optional injected lower-layer playlist-item handler.
    :param timestamped_captions: Optional injected timestamped-caption handler.
    :param default_language: Optional injected configured transcript language.
    :param default_language_error: Optional safe invalid-configuration state.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_TOOL_NAME,
        "description": "Retrieve timestamped transcripts for videos in one playlist with bounded fan-out.",
        "inputSchema": PLAYLISTS_GET_VIDEO_TRANSCRIPTS_INPUT_SCHEMA,
        "handler": build_playlists_get_video_transcripts_handler(
            playlist_items=playlist_items,
            timestamped_captions=timestamped_captions,
            default_language=default_language,
            default_language_error=default_language_error,
        ),
        "metadata": build_playlists_get_video_transcripts_metadata(),
    }


def build_playlists_search_items_handler(*, playlists=None, playlist_items=None):
    """Build a callable handler for bounded literal playlist-item search.

    :param playlists: Optional lower-layer playlist lookup override for tests.
    :param playlist_items: Optional lower-layer paged playlist-item listing override for tests.
    :return: Callable that validates, checks availability, searches, and normalizes one playlist.
    """
    selected_playlists = playlists or build_playlists_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated bounded literal playlist-item search.

        :param arguments: Caller-provided public search arguments.
        :return: Normalized source-ordered matching item collection and coverage state.
        :raises PlaylistsSearchItemsToolError: If validation, availability, traversal, or matching fails safely.
        """
        normalized = validate_playlists_search_items_arguments(arguments)
        try:
            availability_payload = selected_playlists(_playlist_lookup_arguments(normalized["playlistId"]))
        except PlaylistsListToolError as exc:
            raise _map_playlists_list_error_to_search(exc) from exc
        _playlist_search_availability(availability_payload)

        matches: list[dict[str, Any]] = []
        inspected_entry_count = 0
        additional_matches_omitted = False
        page_cursor: str | None = None
        seen_cursors: set[str] = set()

        for page_index in range(PLAYLISTS_SEARCH_ITEMS_MAX_PAGES):
            try:
                payload = selected_playlist_items(_playlist_search_page_arguments(normalized["playlistId"], page_cursor))
            except PlaylistItemsListToolError as exc:
                raise _map_playlist_items_list_error_to_search(exc) from exc
            source_items = payload.get("items") if isinstance(payload, dict) else None
            if not isinstance(source_items, list):
                raise PlaylistsSearchItemsToolError(
                    safe_upstream_error_message(),
                    category="upstream_failure",
                    details={"reason": "invalid_playlist_item_result"},
                )
            remaining_capacity = PLAYLISTS_SEARCH_ITEMS_MAX_INSPECTED_ENTRIES - inspected_entry_count
            for source_item in source_items[:remaining_capacity]:
                inspected_entry_count += 1
                match = _playlist_search_match(source_item, normalized["query"].casefold())
                if match is None:
                    continue
                if len(matches) < normalized["maxResults"]:
                    matches.append(match)
                else:
                    additional_matches_omitted = True

            if len(source_items) > remaining_capacity:
                return _playlist_search_result(
                    arguments=normalized,
                    matches=matches,
                    inspected_entry_count=inspected_entry_count,
                    is_complete=False,
                    termination_reason="inspection_cap",
                    additional_matches_omitted=True if additional_matches_omitted else None,
                )

            next_cursor = payload.get("nextPageToken") if isinstance(payload, dict) else None
            if not isinstance(next_cursor, str) or not next_cursor:
                return _playlist_search_result(
                    arguments=normalized,
                    matches=matches,
                    inspected_entry_count=inspected_entry_count,
                    is_complete=True,
                    termination_reason="end_of_playlist",
                    additional_matches_omitted=additional_matches_omitted,
                )
            if next_cursor in seen_cursors:
                raise PlaylistsSearchItemsToolError(
                    safe_upstream_error_message(),
                    category="upstream_failure",
                    details={"reason": "repeated_page_cursor"},
                )
            seen_cursors.add(next_cursor)
            if page_index == PLAYLISTS_SEARCH_ITEMS_MAX_PAGES - 1:
                return _playlist_search_result(
                    arguments=normalized,
                    matches=matches,
                    inspected_entry_count=inspected_entry_count,
                    is_complete=False,
                    termination_reason="inspection_cap",
                    additional_matches_omitted=True if additional_matches_omitted else None,
                )
            page_cursor = next_cursor

        raise PlaylistsSearchItemsToolError(
            safe_upstream_error_message(),
            category="upstream_failure",
            details={"reason": "unexpected_search_termination"},
        )

    return handler


def build_playlists_search_items_tool_descriptor(*, playlists=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``playlists_searchItems``.

    :param playlists: Optional lower-layer playlist lookup override for tests.
    :param playlist_items: Optional lower-layer playlist-item listing override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": PLAYLISTS_SEARCH_ITEMS_TOOL_NAME,
        "description": "Search accessible playlist items with a bounded case-insensitive literal phrase match.",
        "inputSchema": PLAYLISTS_SEARCH_ITEMS_INPUT_SCHEMA,
        "handler": build_playlists_search_items_handler(playlists=playlists, playlist_items=playlist_items),
        "metadata": build_playlists_search_items_metadata(),
    }
