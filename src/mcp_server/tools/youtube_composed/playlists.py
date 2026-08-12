"""Normalized public playlist-detail tools.

The module owns concrete single-playlist behavior for the playlists family.
"""

from __future__ import annotations

from typing import Any

from mcp_server.tools.youtube_common.conventions import safe_upstream_error_message, sanitize_error_details
from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError, build_playlists_list_handler
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("playlists")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools

PLAYLISTS_GET_PLAYLIST_TOOL_NAME = "playlists_getPlaylist"
PLAYLISTS_GET_PLAYLIST_PARTS = "snippet,contentDetails,status"
PLAYLISTS_GET_PLAYLIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["playlistId"],
    "properties": {"playlistId": {"type": "string", "minLength": 1}},
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


def _playlist_lookup_arguments(playlist_id: str) -> dict[str, str]:
    """Build the one direct lower-layer request for playlist details.

    :param playlist_id: Validated public playlist identifier.
    :return: Direct playlists-list arguments for required public detail groups.
    """
    return {"part": PLAYLISTS_GET_PLAYLIST_PARTS, "id": playlist_id}


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
