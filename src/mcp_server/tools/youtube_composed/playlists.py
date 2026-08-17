"""Normalized public playlist-detail tools.

The module owns concrete single-playlist behavior for the playlists family.
"""

from __future__ import annotations

from typing import Any

from mcp_server.tools.youtube_common.conventions import safe_upstream_error_message, sanitize_error_details
from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError, build_playlist_items_list_handler
from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError, build_playlists_list_handler
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("playlists")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools

PLAYLISTS_GET_PLAYLIST_TOOL_NAME = "playlists_getPlaylist"
PLAYLISTS_GET_PLAYLIST_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_PLAYLIST_ITEMS_TOOL_NAME = "playlists_getPlaylistItems"
PLAYLISTS_GET_PLAYLIST_ITEMS_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_PLAYLIST_ITEMS_DEFAULT_MAX_RESULTS = 25
PLAYLISTS_GET_PLAYLIST_ITEMS_MAX_RESULTS = 50
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
            details={"field": sorted(unexpected_fields)[0]},
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
            details={"field": sorted(unexpected_fields)[0]},
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
            details={"field": sorted(unexpected_fields)[0]},
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
