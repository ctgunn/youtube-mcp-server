"""Concrete Layer 2 tool support for the YouTube ``playlists`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlists import (
    build_playlists_delete_wrapper,
    build_playlists_insert_wrapper,
    build_playlists_list_wrapper,
    build_playlists_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLISTS_LIST_TOOL_NAME = "playlists_list"
PLAYLISTS_LIST_QUOTA_COST = 1
PLAYLISTS_LIST_SELECTORS = ("channelId", "id", "mine")
PLAYLISTS_LIST_SUPPORTED_PARTS = ("contentDetails", "id", "localizations", "player", "snippet", "status")
PLAYLISTS_LIST_MAX_RESULTS = 50
PLAYLISTS_LIST_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

PLAYLISTS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLISTS_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLISTS_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLISTS_LIST_DESCRIPTION = (
    "List YouTube playlist resources. Endpoint: playlists.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)

PLAYLISTS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId or id for public playlist lookup with API-key access.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for owner-scoped playlist retrieval.",
    "Quota cost: 1. Use pageToken and maxResults only with collection-style channelId or mine requests.",
    "Quota cost: 1. Valid accessible requests that match no playlists return a successful empty item collection.",
)

PLAYLISTS_LIST_CAVEATS = (
    "Exactly one selector is required: channelId, id, or mine.",
    "This tool only retrieves playlist resources through playlists.list.",
    "Playlist insertion, update, deletion, playlist item traversal, playlist image handling, playlist search, "
    "video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, "
    "and cross-endpoint aggregation are out of scope.",
    "Returned playlist fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLISTS_LIST_CALLER_EXAMPLES = (
    {
        "name": "channel_scoped_playlist_listing",
        "description": "Quota cost: 1. List playlists for one channelId with API-key access.",
        "arguments": {"part": "snippet,contentDetails", "channelId": "UC123"},
        "result": {"endpoint": "playlists.list", "selector": "channelId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_playlist_lookup",
        "description": "Quota cost: 1. Retrieve playlists by playlist id with API-key access.",
        "arguments": {"part": "id,snippet", "id": "PL123"},
        "result": {"endpoint": "playlists.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "owner_scoped_playlist_listing",
        "description": "Quota cost: 1. List the authorized user's playlists with OAuth-backed access.",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "playlists.list", "selector": "mine", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_listing",
        "description": "Quota cost: 1. Continue channel-scoped traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "channelId": "UC123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An accessible empty playlist collection remains a successful list result.",
        "arguments": {"part": "snippet", "channelId": "UC_NO_PLAYLISTS"},
        "result": {"endpoint": "playlists.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing required playlist part selection.",
        "arguments": {"channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside supported playlist resource sections.",
        "arguments": {"part": "statistics", "channelId": "UC123"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_selector",
        "description": "Reject requests missing channelId, id, and mine selectors.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "conflicting_selector",
        "description": "Reject requests that combine channelId, id, or mine selectors.",
        "arguments": {"part": "snippet", "channelId": "UC123", "id": "PL123"},
        "error": {"category": "invalid_request", "field": "selector"},
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "PL123", "pageToken": "NEXT_PAGE"},
        "error": {"category": "invalid_request", "field": "paging"},
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access for mine to safe access errors.",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "selector": "mine"},
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Map quota and upstream playlist list failures to safe categories.",
        "arguments": {"part": "snippet", "channelId": "UC123"},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Playlist mutation, playlist item traversal, enrichment, analytics, and recommendation are out of scope.",
        "arguments": {"part": "snippet", "channelId": "UC123", "includePlaylistItems": True},
        "error": {"category": "invalid_request", "field": "includePlaylistItems"},
    },
)

PLAYLISTS_INSERT_TOOL_NAME = "playlists_insert"
PLAYLISTS_INSERT_QUOTA_COST = 50
PLAYLISTS_INSERT_SUPPORTED_PARTS = ("snippet",)
PLAYLISTS_INSERT_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

PLAYLISTS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLISTS_INSERT_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {"title": {"type": "string", "minLength": 1}},
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLISTS_INSERT_DESCRIPTION = (
    "Create a YouTube playlist. Endpoint: playlists.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires body.snippet.title."
)

PLAYLISTS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and body.snippet.title.",
    "Quota cost: 50. Successful calls create user-visible playlists for the authorized account.",
    "Quota cost: 50. Repeating a creation request can create duplicate playlists; no idempotency is promised.",
    "Quota cost: 50. Returned playlist fields depend on selected parts and upstream availability.",
)

PLAYLISTS_INSERT_CAVEATS = (
    "playlists_insert creates one playlist through playlists.insert and requires OAuth authorization.",
    "Use playlists_list for playlist retrieval; this tool only performs playlists.insert.",
    "body.snippet.title is required for supported playlist creation requests.",
    "Unsupported write fields such as body.snippet.description, body.status, or body.localizations are out of scope.",
    "Playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, "
    "analytics, ranking, summarization, recommendation, duplicate-prevention, and cross-endpoint enrichment are out of scope.",
    "Returned playlist fields depend on selected parts and upstream availability; missing optional fields are not fabricated.",
)

PLAYLISTS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "oauth_playlist_creation",
        "description": "Quota cost: 50. Create a user-visible playlist with OAuth authorization.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Research playlist"}}},
        "result": {"endpoint": "playlists.insert", "quotaCost": 50, "created": True},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject playlist creation requests missing required part selection.",
        "arguments": {"body": {"snippet": {"title": "Research playlist"}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 50. Reject writable parts outside the supported snippet create path.",
        "arguments": {"part": "status", "body": {"snippet": {"title": "Research playlist"}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_body",
        "description": "Quota cost: 50. Reject playlist creation requests missing a writable body.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "body"},
    },
    {
        "name": "missing_title",
        "description": "Quota cost: 50. Reject playlist creation requests missing body.snippet.title.",
        "arguments": {"part": "snippet", "body": {"snippet": {}}},
        "error": {"category": "invalid_request", "field": "body.snippet.title"},
    },
    {
        "name": "unsupported_write_field",
        "description": "Quota cost: 50. Reject optional write fields not supported by this slice.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Research playlist", "description": "Unsupported"}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.description"},
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Research playlist"}}},
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
    },
    {
        "name": "quota_or_upstream_create_failure",
        "description": "Quota cost: 50. Map quota and upstream create failures to safe categories.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Research playlist"}}},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Quota cost: 50. Playlist item insertion, video curation, analytics, and recommendation are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Research playlist"}},
            "insertPlaylistItems": True,
        },
        "error": {"category": "invalid_request", "field": "insertPlaylistItems"},
    },
)

PLAYLISTS_UPDATE_TOOL_NAME = "playlists_update"
PLAYLISTS_UPDATE_QUOTA_COST = 50
PLAYLISTS_UPDATE_SUPPORTED_PARTS = ("snippet",)
PLAYLISTS_UPDATE_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

PLAYLISTS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLISTS_UPDATE_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "snippet": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {"title": {"type": "string", "minLength": 1}},
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLISTS_UPDATE_DESCRIPTION = (
    "Update a YouTube playlist. Endpoint: playlists.update. "
    "Quota cost: 50. Auth: oauth_required. Requires body.id and body.snippet.title."
)

PLAYLISTS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part, body.id, and body.snippet.title.",
    "Quota cost: 50. Successful calls mutate user-visible playlist details for the authorized account.",
    "Quota cost: 50. Repeating an update after an unclear outcome may reapply the requested playlist state.",
    "Quota cost: 50. Returned playlist fields depend on selected parts and upstream availability.",
)

PLAYLISTS_UPDATE_CAVEATS = (
    "playlists_update updates one playlist through playlists.update and requires OAuth authorization.",
    "Use playlists_list for playlist retrieval and playlists_insert for playlist creation; this tool only performs playlists.update.",
    "body.id identifies the existing playlist and body.snippet.title is required for supported update requests.",
    "Unsupported write fields such as body.snippet.description, body.status, or body.localizations are out of scope.",
    "Playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, "
    "transcript retrieval, analytics, ranking, summarization, recommendation, rollback, conflict detection, "
    "playlist-versioning, and cross-endpoint enrichment are out of scope.",
    "Returned playlist fields depend on selected parts and upstream availability; missing optional fields are not fabricated.",
)

PLAYLISTS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "oauth_playlist_update",
        "description": "Quota cost: 50. Update a user-visible playlist title with OAuth authorization.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}},
        },
        "result": {"endpoint": "playlists.update", "quotaCost": 50, "updated": True},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject playlist update requests missing required part selection.",
        "arguments": {"body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 50. Reject update part values outside the supported snippet path.",
        "arguments": {"part": "status", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "missing_body",
        "description": "Quota cost: 50. Reject playlist update requests missing a writable body.",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "body"},
    },
    {
        "name": "missing_target_identity",
        "description": "Quota cost: 50. Reject playlist update requests missing body.id.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Updated research playlist"}}},
        "error": {"category": "invalid_request", "field": "body.id"},
    },
    {
        "name": "missing_title",
        "description": "Quota cost: 50. Reject playlist update requests missing body.snippet.title.",
        "arguments": {"part": "snippet", "body": {"id": "PL123", "snippet": {}}},
        "error": {"category": "invalid_request", "field": "body.snippet.title"},
    },
    {
        "name": "unsupported_write_field",
        "description": "Quota cost: 50. Reject optional write fields not supported by this slice.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "PL123",
                "snippet": {"title": "Updated research playlist", "description": "Unsupported"},
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.description"},
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
        "arguments": {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
    },
    {
        "name": "quota_or_upstream_update_failure",
        "description": "Quota cost: 50. Map quota, missing-resource, and upstream update failures to safe categories.",
        "arguments": {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "repeat_request_caveat",
        "description": "Quota cost: 50. Repeating an update after an unclear outcome may reapply the requested state.",
        "arguments": {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
        "result": {"endpoint": "playlists.update", "caveats": {"repeatRequest": "may_reapply_update"}},
        "quotaCost": 50,
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Quota cost: 50. Playlist item management, video curation, analytics, and recommendation are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}},
            "insertPlaylistItems": True,
        },
        "error": {"category": "invalid_request", "field": "insertPlaylistItems"},
    },
)

PLAYLISTS_DELETE_TOOL_NAME = "playlists_delete"
PLAYLISTS_DELETE_QUOTA_COST = 50
PLAYLISTS_DELETE_UNSAFE_DETAIL_KEYS = frozenset({"authorization", "authorization_header", "headers"})

PLAYLISTS_DELETE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

PLAYLISTS_DELETE_DESCRIPTION = (
    "Delete a YouTube playlist. Endpoint: playlists.delete. "
    "Quota cost: 50. Auth: oauth_required. Requires id."
)

PLAYLISTS_DELETE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide id for the target playlist.",
    "Quota cost: 50. Successful calls delete user-visible playlists for the authorized account.",
    "Quota cost: 50. Successful deletion returns an acknowledgment without a deleted playlist resource body.",
    "Quota cost: 50. Repeating a delete after an unclear outcome may return resource_not_found if the first delete succeeded.",
)

PLAYLISTS_DELETE_CAVEATS = (
    "playlists_delete deletes one playlist through playlists.delete and requires OAuth authorization.",
    "This is a destructive operation for a user-visible playlist represented by the authorized account.",
    "Use playlists_list for retrieval, playlists_insert for creation, and playlists_update for updates; this tool only performs playlists.delete.",
    "Only id is accepted. Request bodies, part selection, list selectors, paging fields, restore, rollback, and idempotency guarantees are out of scope.",
    "Playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, "
    "analytics, ranking, summarization, recommendation, restore, rollback, and cross-endpoint enrichment are out of scope.",
    "No deleted playlist resource is fabricated from request context; successful no-body responses are represented as acknowledgments.",
)

PLAYLISTS_DELETE_CALLER_EXAMPLES = (
    {
        "name": "oauth_playlist_deletion",
        "description": "Quota cost: 50. Delete one user-visible playlist with OAuth authorization.",
        "arguments": {"id": "PL123"},
        "result": {"endpoint": "playlists.delete", "quotaCost": 50, "deleted": True, "acknowledged": True},
        "quotaCost": 50,
    },
    {
        "name": "no_body_deletion_acknowledgment",
        "description": "Quota cost: 50. Successful no-body deletion returns a safe acknowledgment rather than fabricated playlist data.",
        "arguments": {"id": "PL123"},
        "result": {"endpoint": "playlists.delete", "acknowledged": True, "target": {"playlistId": "PL123"}},
        "quotaCost": 50,
    },
    {
        "name": "missing_target_identity",
        "description": "Quota cost: 50. Reject playlist deletion requests missing required id.",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "id"},
    },
    {
        "name": "malformed_target_identity",
        "description": "Quota cost: 50. Reject playlist deletion requests with blank or malformed id.",
        "arguments": {"id": ""},
        "error": {"category": "invalid_request", "field": "id"},
    },
    {
        "name": "unsupported_field",
        "description": "Quota cost: 50. Reject part, body, selectors, paging, and other fields unsupported by playlists.delete.",
        "arguments": {"id": "PL123", "part": "snippet"},
        "error": {"category": "invalid_request", "field": "part"},
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
        "arguments": {"id": "PL123"},
        "error": {"category": "authentication_failed", "authMode": "oauth_required"},
    },
    {
        "name": "insufficient_authorization",
        "description": "Quota cost: 50. Map inaccessible playlist deletion to safe authorization errors.",
        "arguments": {"id": "PL_NOT_OWNED"},
        "error": {"category": "authorization_failed", "field": "id"},
    },
    {
        "name": "missing_resource_or_already_deleted",
        "description": "Quota cost: 50. Map missing or already-deleted playlist targets to resource_not_found.",
        "arguments": {"id": "PL_ALREADY_DELETED"},
        "error": {"category": "resource_not_found", "field": "id"},
    },
    {
        "name": "quota_or_upstream_delete_failure",
        "description": "Quota cost: 50. Map quota and upstream delete failures to safe categories.",
        "arguments": {"id": "PL123"},
        "error": {"category": "quota_exhausted"},
    },
    {
        "name": "repeat_delete_caveat",
        "description": "Quota cost: 50. Repeating a delete after an unclear outcome may return resource_not_found if the first delete succeeded.",
        "arguments": {"id": "PL123"},
        "result": {"endpoint": "playlists.delete", "caveats": {"repeatDelete": "missing_resource_possible_after_success"}},
        "quotaCost": 50,
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Quota cost: 50. Restore, rollback, playlist item management, analytics, and recommendation are out of scope.",
        "arguments": {"id": "PL123", "restore": True},
        "error": {"category": "invalid_request", "field": "restore"},
    },
)


class PlaylistsListToolError(ValueError):
    """Represent a safe caller-facing ``playlists_list`` failure.

    :param message: Human-readable failure summary.
    :param category: Stable safe failure category.
    :param details: Optional structured details with secret-bearing keys removed.
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "invalid_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a sanitized playlists list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_playlists_error_details(details or {})


class PlaylistsInsertToolError(ValueError):
    """Represent a safe caller-facing ``playlists_insert`` failure.

    :param message: Human-readable failure summary.
    :param category: Stable safe failure category.
    :param details: Optional structured details with secret-bearing keys removed.
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "invalid_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a sanitized playlists insert tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_playlists_insert_error_details(details or {})


class PlaylistsUpdateToolError(ValueError):
    """Represent a safe caller-facing ``playlists_update`` failure.

    :param message: Human-readable failure summary.
    :param category: Stable safe failure category.
    :param details: Optional structured details with secret-bearing keys removed.
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "invalid_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a sanitized playlists update tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_playlists_update_error_details(details or {})


class PlaylistsDeleteToolError(ValueError):
    """Represent a safe caller-facing ``playlists_delete`` failure.

    :param message: Human-readable failure summary.
    :param category: Stable safe failure category.
    :param details: Optional structured details with secret-bearing keys removed.
    """

    def __init__(
        self,
        message: str,
        *,
        category: str = "invalid_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a sanitized playlists delete tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_playlists_delete_error_details(details or {})


def _sanitize_playlists_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove playlist-list credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in PLAYLISTS_LIST_UNSAFE_DETAIL_KEYS
    }


def _sanitize_playlists_insert_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove playlist-insert credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in PLAYLISTS_INSERT_UNSAFE_DETAIL_KEYS
    }


def _sanitize_playlists_update_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove playlist-update credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in PLAYLISTS_UPDATE_UNSAFE_DETAIL_KEYS
    }


def _sanitize_playlists_delete_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove playlist-delete credential and header fields from error details.

    :param details: Candidate diagnostic details.
    :return: Details safe to expose to MCP callers.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower() not in PLAYLISTS_DELETE_UNSAFE_DETAIL_KEYS
    }


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlists_parts(part: Any) -> str:
    """Validate and normalize requested playlist parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistsListToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistsListToolError("playlists_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLISTS_LIST_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistsListToolError(
            "playlists_list part must use supported playlist resource sections",
            details={"field": "part", "allowed": list(PLAYLISTS_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlists_insert_parts(part: Any) -> str:
    """Validate and normalize requested playlist insert parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistsInsertToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistsInsertToolError("playlists_insert requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLISTS_INSERT_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistsInsertToolError(
            "playlists_insert part must use supported writable playlist sections",
            details={"field": "part", "allowed": list(PLAYLISTS_INSERT_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlists_update_parts(part: Any) -> str:
    """Validate and normalize requested playlist update parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistsUpdateToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistsUpdateToolError("playlists_update requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLISTS_UPDATE_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistsUpdateToolError(
            "playlists_update part must use supported writable playlist sections",
            details={"field": "part", "allowed": list(PLAYLISTS_UPDATE_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def validate_playlists_insert_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlists_insert`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistsInsertToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsInsertToolError("playlists_insert arguments must be an object")

    allowed = set(PLAYLISTS_INSERT_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise PlaylistsInsertToolError(
                f"unsupported field for playlists_insert: {field}",
                details={"field": field},
            )

    part = _validate_playlists_insert_parts(arguments.get("part"))
    body = arguments.get("body")
    if not isinstance(body, dict):
        raise PlaylistsInsertToolError("playlists_insert requires body", details={"field": "body"})
    unsupported_body = [field for field in body if field != "snippet"]
    if unsupported_body:
        raise PlaylistsInsertToolError(
            f"unsupported body field for playlists_insert: {unsupported_body[0]}",
            details={"field": f"body.{unsupported_body[0]}"},
        )
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise PlaylistsInsertToolError(
            "playlists_insert requires body.snippet",
            details={"field": "body.snippet"},
        )
    unsupported_snippet = [field for field in snippet if field != "title"]
    if unsupported_snippet:
        raise PlaylistsInsertToolError(
            f"unsupported snippet field for playlists_insert: {unsupported_snippet[0]}",
            details={"field": f"body.snippet.{unsupported_snippet[0]}"},
        )
    title = snippet.get("title")
    if not isinstance(title, str) or not title.strip():
        raise PlaylistsInsertToolError(
            "playlists_insert requires body.snippet.title",
            details={"field": "body.snippet.title"},
        )
    return {"part": part, "body": {"snippet": {"title": title.strip()}}}


def validate_playlists_update_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlists_update`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistsUpdateToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsUpdateToolError("playlists_update arguments must be an object")

    allowed = set(PLAYLISTS_UPDATE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise PlaylistsUpdateToolError(
                f"unsupported field for playlists_update: {field}",
                details={"field": field},
            )

    part = _validate_playlists_update_parts(arguments.get("part"))
    body = arguments.get("body")
    if not isinstance(body, dict):
        raise PlaylistsUpdateToolError("playlists_update requires body", details={"field": "body"})
    unsupported_body = [field for field in body if field not in {"id", "snippet"}]
    if unsupported_body:
        raise PlaylistsUpdateToolError(
            f"unsupported body field for playlists_update: {unsupported_body[0]}",
            details={"field": f"body.{unsupported_body[0]}"},
        )
    playlist_id = body.get("id")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsUpdateToolError("playlists_update requires body.id", details={"field": "body.id"})
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise PlaylistsUpdateToolError(
            "playlists_update requires body.snippet",
            details={"field": "body.snippet"},
        )
    unsupported_snippet = [field for field in snippet if field != "title"]
    if unsupported_snippet:
        raise PlaylistsUpdateToolError(
            f"unsupported snippet field for playlists_update: {unsupported_snippet[0]}",
            details={"field": f"body.snippet.{unsupported_snippet[0]}"},
        )
    title = snippet.get("title")
    if not isinstance(title, str) or not title.strip():
        raise PlaylistsUpdateToolError(
            "playlists_update requires body.snippet.title",
            details={"field": "body.snippet.title"},
        )
    return {"part": part, "body": {"id": playlist_id.strip(), "snippet": {"title": title.strip()}}}


def validate_playlists_delete_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlists_delete`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistsDeleteToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsDeleteToolError("playlists_delete arguments must be an object")

    allowed = set(PLAYLISTS_DELETE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise PlaylistsDeleteToolError(
                f"unsupported field for playlists_delete: {field}",
                details={"field": field},
            )

    playlist_id = arguments.get("id")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistsDeleteToolError("playlists_delete requires id", details={"field": "id"})
    return {"id": playlist_id.strip()}


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active playlists selectors from one request.

    :param arguments: Caller-supplied ``playlists_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in PLAYLISTS_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "mine":
            if value is True:
                active.append((selector, True))
        elif isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
    return active


def validate_playlists_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlists_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistsListToolError("playlists_list arguments must be an object")

    allowed = set(PLAYLISTS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in allowed:
            raise PlaylistsListToolError(
                f"unsupported field for playlists_list: {field}",
                details={"field": field},
            )

    part = _validate_playlists_parts(arguments.get("part"))
    provided_selectors: list[str] = []
    for selector in PLAYLISTS_LIST_SELECTORS:
        if selector not in arguments:
            continue
        value = arguments[selector]
        if selector == "mine":
            if value is not True:
                raise PlaylistsListToolError(
                    "playlists_list mine selector must be true when present",
                    details={"field": "mine"},
                )
        elif not isinstance(value, str) or not value.strip():
            raise PlaylistsListToolError(
                f"playlists_list requires a non-empty {selector}",
                details={"field": selector},
            )
        provided_selectors.append(selector)

    active = _active_selectors(arguments)
    if len(provided_selectors) != 1 or len(active) != 1:
        raise PlaylistsListToolError(
            "playlists_list requires exactly one selector: channelId, id, or mine",
            details={"field": "selector", "allowed": list(PLAYLISTS_LIST_SELECTORS)},
        )

    selector, value = active[0]
    normalized: dict[str, Any] = {"part": part, selector: value}
    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistsListToolError(
            "pageToken and maxResults are only supported with channelId or mine",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistsListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistsListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLISTS_LIST_MAX_RESULTS:
            raise PlaylistsListToolError(
                f"maxResults must be between 0 and {PLAYLISTS_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLISTS_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def _selector_name(arguments: dict[str, Any]) -> str:
    """Return the active selector name from normalized arguments.

    :param arguments: Normalized ``playlists_list`` arguments.
    :return: Active selector name.
    :raises PlaylistsListToolError: If no supported selector is active.
    """
    for selector in PLAYLISTS_LIST_SELECTORS:
        if selector in arguments:
            return selector
    raise PlaylistsListToolError("playlists_list requires a selector", details={"field": "selector"})


def _auth_context_for_selector(
    selector: str,
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for a playlists selector.

    :param selector: Selected playlists selector.
    :param api_key: API key value available for public selector access.
    :param oauth_token: OAuth token available for owner-scoped lookup.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises PlaylistsListToolError: If required credentials are unavailable.
    """
    if selector in {"channelId", "id"}:
        if not isinstance(api_key, str) or not api_key.strip():
            raise PlaylistsListToolError(
                f"{selector} requires public API-key access",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))

    if selector == "mine":
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise PlaylistsListToolError(
                "mine requires eligible OAuth authorization",
                category="authentication_failed",
                details={"selector": selector, "authMode": "oauth_required"},
            )
        return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token.strip()))

    raise PlaylistsListToolError("playlists_list requires a supported selector", details={"field": "selector"})


def map_playlists_list_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    auth_mode: str | None = None,
) -> dict[str, Any]:
    """Map an upstream playlists payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlists list payload.
    :param arguments: Validated caller arguments used for the request.
    :param auth_mode: Safe auth mode selected for execution.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlists_list_arguments(arguments)
    selector = _selector_name(normalized)
    selected_auth_mode = auth_mode or ("oauth_required" if selector == "mine" else "api_key")
    items = payload.get("items", [])
    result: dict[str, Any] = {
        "endpoint": "playlists.list",
        "quotaCost": PLAYLISTS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": selected_auth_mode},
        "items": items,
        "empty": not bool(items),
    }
    paging = {
        field: normalized[field]
        for field in ("pageToken", "maxResults")
        if field in normalized
    }
    if paging:
        result["paging"] = paging
    for field in ("kind", "etag", "nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            result[field] = payload[field]
    return result


def _playlists_insert_creation_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe playlist creation context for an insert request.

    :param arguments: Validated ``playlists_insert`` arguments.
    :return: Safe creation context with writable fields and title.
    """
    return {
        "writableFields": ["body.snippet.title"],
        "title": arguments["body"]["snippet"]["title"],
    }


def _playlists_update_target_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Return safe playlist target context for an update request.

    :param arguments: Validated ``playlists_update`` arguments.
    :return: Safe target context with the playlist identifier.
    """
    return {"playlistId": arguments["body"]["id"]}


def _playlists_update_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe playlist update context for an update request.

    :param arguments: Validated ``playlists_update`` arguments.
    :return: Safe update context with writable fields and title.
    """
    return {
        "writableFields": ["body.snippet.title"],
        "title": arguments["body"]["snippet"]["title"],
    }


def _playlists_delete_target_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Return safe playlist target context for a delete request.

    :param arguments: Validated ``playlists_delete`` arguments.
    :return: Safe target context with the playlist identifier.
    """
    return {"playlistId": arguments["id"]}


def map_playlists_insert_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist creation payload to the public result.

    :param payload: Upstream or Layer 1 playlists insert payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw created-resource result with safe operation context.
    """
    normalized = validate_playlists_insert_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlists.insert",
        "quotaCost": PLAYLISTS_INSERT_QUOTA_COST,
        "created": True,
        "requestedParts": _split_parts(normalized["part"]),
        "creation": _playlists_insert_creation_context(normalized),
        "auth": {"mode": "oauth_required"},
        "playlist": payload,
    }
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def map_playlists_update_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist update payload to the public result.

    :param payload: Upstream or Layer 1 playlists update payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw updated-resource result with safe operation context.
    """
    normalized = validate_playlists_update_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlists.update",
        "quotaCost": PLAYLISTS_UPDATE_QUOTA_COST,
        "updated": True,
        "requestedParts": _split_parts(normalized["part"]),
        "target": _playlists_update_target_context(normalized),
        "update": _playlists_update_context(normalized),
        "auth": {"mode": "oauth_required"},
        "playlist": payload,
    }
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def map_playlists_delete_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist deletion payload to the public result.

    :param payload: Upstream or Layer 1 playlists delete payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw deletion acknowledgment result with safe operation context.
    """
    normalized = validate_playlists_delete_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlists.delete",
        "quotaCost": PLAYLISTS_DELETE_QUOTA_COST,
        "deleted": True,
        "acknowledged": True,
        "target": _playlists_delete_target_context(normalized),
        "auth": {"mode": "oauth_required"},
    }
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_playlists_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistsListToolError:
    """Map a normalized upstream failure to a safe ``playlists_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistsListToolError(str(error), category=category, details=error.details)


def _map_playlists_insert_upstream_error(error: NormalizedUpstreamError) -> PlaylistsInsertToolError:
    """Map a normalized upstream failure to a safe ``playlists_insert`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "forbidden_create",
        "policy_restricted": "forbidden_create",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistsInsertToolError(str(error), category=category, details=error.details)


def _map_playlists_update_upstream_error(error: NormalizedUpstreamError) -> PlaylistsUpdateToolError:
    """Map a normalized upstream failure to a safe ``playlists_update`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "forbidden_update",
        "policy_restricted": "forbidden_update",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistsUpdateToolError(str(error), category=category, details=error.details)


def _map_playlists_delete_upstream_error(error: NormalizedUpstreamError) -> PlaylistsDeleteToolError:
    """Map a normalized upstream failure to a safe ``playlists_delete`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistsDeleteToolError(str(error), category=category, details=error.details)


def build_playlists_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlists_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "selector",
            "paging",
            "auth",
            "items",
            "empty",
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "playlist_insertion",
            "playlist_update",
            "playlist_deletion",
            "playlist_item_traversal",
            "playlist_image_handling",
            "playlist_search",
            "video_enrichment",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLISTS_LIST_TOOL_NAME,
        upstream_resource="playlists",
        upstream_method="list",
        operation_key="playlists.list",
        description=PLAYLISTS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=PLAYLISTS_LIST_QUOTA_COST,
        resource_family="playlists",
        input_contract=PLAYLISTS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLISTS_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLISTS_LIST_SELECTORS),
            "pagingFields": ["pageToken", "maxResults", "nextPageToken", "prevPageToken", "pageInfo"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "invalid_request",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLISTS_LIST_USAGE_NOTES,
        caveats=PLAYLISTS_LIST_CAVEATS,
    )


def build_playlists_insert_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlists_insert``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "created",
            "requestedParts",
            "creation",
            "auth",
            "playlist",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "status", "localizations"),
        disallowed_behavior=(
            "playlist_listing",
            "playlist_update",
            "playlist_deletion",
            "playlist_item_insertion",
            "playlist_image_handling",
            "video_curation",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "duplicate_prevention",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLISTS_INSERT_TOOL_NAME,
        upstream_resource="playlists",
        upstream_method="insert",
        operation_key="playlists.insert",
        description=PLAYLISTS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLISTS_INSERT_QUOTA_COST,
        resource_family="playlists",
        input_contract=PLAYLISTS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "playlist",
            "requestedParts": list(PLAYLISTS_INSERT_SUPPORTED_PARTS),
            "supportedWritableParts": ["snippet"],
            "writableFields": ["body.snippet.title"],
            "duplicateCreatePolicy": "not_idempotent",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "forbidden_create",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLISTS_INSERT_USAGE_NOTES,
        caveats=PLAYLISTS_INSERT_CAVEATS,
    )


def build_playlists_update_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlists_update``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "updated",
            "requestedParts",
            "target",
            "update",
            "auth",
            "playlist",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "status", "localizations"),
        disallowed_behavior=(
            "playlist_listing",
            "playlist_creation",
            "playlist_deletion",
            "playlist_item_management",
            "playlist_image_handling",
            "video_curation",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "rollback",
            "conflict_detection",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLISTS_UPDATE_TOOL_NAME,
        upstream_resource="playlists",
        upstream_method="update",
        operation_key="playlists.update",
        description=PLAYLISTS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLISTS_UPDATE_QUOTA_COST,
        resource_family="playlists",
        input_contract=PLAYLISTS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "playlist",
            "requestedParts": list(PLAYLISTS_UPDATE_SUPPORTED_PARTS),
            "supportedWritableParts": ["snippet"],
            "targetFields": ["body.id"],
            "writableFields": ["body.snippet.title"],
            "repeatRequestPolicy": "may_reapply_update",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "forbidden_update",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLISTS_UPDATE_USAGE_NOTES,
        caveats=PLAYLISTS_UPDATE_CAVEATS,
    )


def build_playlists_delete_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlists_delete``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "deleted",
            "acknowledged",
            "target",
            "auth",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag"),
        disallowed_behavior=(
            "playlist_listing",
            "playlist_creation",
            "playlist_update",
            "playlist_item_management",
            "playlist_image_handling",
            "video_curation",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "restore",
            "rollback",
            "idempotency_guarantee",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLISTS_DELETE_TOOL_NAME,
        upstream_resource="playlists",
        upstream_method="delete",
        operation_key="playlists.delete",
        description=PLAYLISTS_DELETE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLISTS_DELETE_QUOTA_COST,
        resource_family="playlists",
        input_contract=PLAYLISTS_DELETE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "deletion_acknowledgment",
            "targetFields": ["id"],
            "noBodySuccess": True,
            "repeatDeletePolicy": "missing_resource_possible_after_success",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLISTS_DELETE_USAGE_NOTES,
        caveats=PLAYLISTS_DELETE_CAVEATS,
    )


def _default_playlists_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist calls.

    :return: Integration executor returning representative playlist data.
    """

    def transport(execution):
        """Return a representative playlist list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistListResponse",
            "etag": "etag-playlists",
            "items": [
                {
                    "kind": "youtube#playlist",
                    "etag": "etag-playlist",
                    "id": execution.arguments.get("id", "PL123"),
                    "snippet": {
                        "channelId": execution.arguments.get("channelId", "UC123"),
                        "title": "Representative playlist",
                    },
                    "contentDetails": {"itemCount": 3},
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlists_insert_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist inserts.

    :return: Integration executor returning representative created playlist data.
    """

    def transport(execution):
        """Return a representative created playlist response.

        :param execution: Request execution context.
        :return: Fake upstream created-resource response for local invocation.
        """
        snippet = execution.arguments.get("body", {}).get("snippet", {})
        return {
            "kind": "youtube#playlist",
            "etag": "etag-created-playlist",
            "id": "PL123",
            "snippet": {
                "title": snippet.get("title", "Research playlist"),
                "channelId": "UC123",
            },
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlists_update_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist updates.

    :return: Integration executor returning representative updated playlist data.
    """

    def transport(execution):
        """Return a representative updated playlist response.

        :param execution: Request execution context.
        :return: Fake upstream updated-resource response for local invocation.
        """
        body = execution.arguments.get("body", {})
        snippet = body.get("snippet", {})
        return {
            "kind": "youtube#playlist",
            "etag": "etag-updated-playlist",
            "id": body.get("id", "PL123"),
            "snippet": {
                "title": snippet.get("title", "Updated research playlist"),
                "channelId": "UC123",
            },
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlists_delete_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist deletes.

    :return: Integration executor returning representative deletion acknowledgment data.
    """

    def transport(execution):
        """Return a representative no-body playlist deletion response.

        :param execution: Request execution context.
        :return: Fake upstream deletion response for local invocation.
        """
        return {}

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlists_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlists_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used for public selector access.
    :param oauth_token: OAuth token value used for owner-scoped lookup.
    :return: Callable that validates, executes, and maps playlist requests.
    """
    selected_wrapper = wrapper or build_playlists_list_wrapper()
    selected_executor = executor or _default_playlists_list_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlists_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlists list result.
        :raises PlaylistsListToolError: If validation or execution fails.
        """
        normalized = validate_playlists_list_arguments(arguments)
        selector = _selector_name(normalized)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlists_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistsListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlists.list", "selector": selector},
            ) from exc
        return map_playlists_list_result(payload, normalized, auth_mode=auth_context.mode.value)

    return handler


def build_playlists_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlists_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for playlist creation.
    :return: Callable that validates, executes, and maps playlist insert requests.
    """
    selected_wrapper = wrapper or build_playlists_insert_wrapper()
    selected_executor = executor or _default_playlists_insert_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlists_insert`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlists insert result.
        :raises PlaylistsInsertToolError: If validation or execution fails.
        """
        normalized = validate_playlists_insert_arguments(arguments)
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise PlaylistsInsertToolError(
                "playlists_insert requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authMode": "oauth_required"},
            )
        auth_context = AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlists_insert_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistsInsertToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlists.insert"},
            ) from exc
        return map_playlists_insert_result(payload, normalized)

    return handler


def build_playlists_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlists_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for playlist update.
    :return: Callable that validates, executes, and maps playlist update requests.
    """
    selected_wrapper = wrapper or build_playlists_update_wrapper()
    selected_executor = executor or _default_playlists_update_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlists_update`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlists update result.
        :raises PlaylistsUpdateToolError: If validation or execution fails.
        """
        normalized = validate_playlists_update_arguments(arguments)
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise PlaylistsUpdateToolError(
                "playlists_update requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authMode": "oauth_required"},
            )
        auth_context = AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlists_update_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistsUpdateToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlists.update"},
            ) from exc
        return map_playlists_update_result(payload, normalized)

    return handler


def build_playlists_delete_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlists_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for playlist deletion.
    :return: Callable that validates, executes, and maps playlist delete requests.
    """
    selected_wrapper = wrapper or build_playlists_delete_wrapper()
    selected_executor = executor or _default_playlists_delete_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlists_delete`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlists delete result.
        :raises PlaylistsDeleteToolError: If validation or execution fails.
        """
        normalized = validate_playlists_delete_arguments(arguments)
        if not isinstance(oauth_token, str) or not oauth_token.strip():
            raise PlaylistsDeleteToolError(
                "playlists_delete requires eligible OAuth authorization",
                category="authentication_failed",
                details={"authMode": "oauth_required"},
            )
        auth_context = AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlists_delete_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistsDeleteToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlists.delete"},
            ) from exc
        return map_playlists_delete_result(payload, normalized)

    return handler


def build_playlists_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlists_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlists_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLISTS_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLISTS_LIST_TOOL_NAME,
        "description": PLAYLISTS_LIST_DESCRIPTION,
        "inputSchema": PLAYLISTS_LIST_INPUT_SCHEMA,
        "handler": build_playlists_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


def build_playlists_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlists_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlists_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLISTS_INSERT_CALLER_EXAMPLES)
    return {
        "name": PLAYLISTS_INSERT_TOOL_NAME,
        "description": PLAYLISTS_INSERT_DESCRIPTION,
        "inputSchema": PLAYLISTS_INSERT_INPUT_SCHEMA,
        "handler": build_playlists_insert_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


def build_playlists_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlists_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlists_update_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLISTS_UPDATE_CALLER_EXAMPLES)
    return {
        "name": PLAYLISTS_UPDATE_TOOL_NAME,
        "description": PLAYLISTS_UPDATE_DESCRIPTION,
        "inputSchema": PLAYLISTS_UPDATE_INPUT_SCHEMA,
        "handler": build_playlists_update_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


def build_playlists_delete_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlists_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlists_delete_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLISTS_DELETE_CALLER_EXAMPLES)
    return {
        "name": PLAYLISTS_DELETE_TOOL_NAME,
        "description": PLAYLISTS_DELETE_DESCRIPTION,
        "inputSchema": PLAYLISTS_DELETE_INPUT_SCHEMA,
        "handler": build_playlists_delete_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLISTS_DELETE_CALLER_EXAMPLES",
    "PLAYLISTS_DELETE_CAVEATS",
    "PLAYLISTS_DELETE_DESCRIPTION",
    "PLAYLISTS_DELETE_INPUT_SCHEMA",
    "PLAYLISTS_DELETE_QUOTA_COST",
    "PLAYLISTS_DELETE_TOOL_NAME",
    "PLAYLISTS_DELETE_USAGE_NOTES",
    "PLAYLISTS_INSERT_CALLER_EXAMPLES",
    "PLAYLISTS_INSERT_CAVEATS",
    "PLAYLISTS_INSERT_DESCRIPTION",
    "PLAYLISTS_INSERT_INPUT_SCHEMA",
    "PLAYLISTS_INSERT_QUOTA_COST",
    "PLAYLISTS_INSERT_SUPPORTED_PARTS",
    "PLAYLISTS_INSERT_TOOL_NAME",
    "PLAYLISTS_INSERT_USAGE_NOTES",
    "PLAYLISTS_UPDATE_CALLER_EXAMPLES",
    "PLAYLISTS_UPDATE_CAVEATS",
    "PLAYLISTS_UPDATE_DESCRIPTION",
    "PLAYLISTS_UPDATE_INPUT_SCHEMA",
    "PLAYLISTS_UPDATE_QUOTA_COST",
    "PLAYLISTS_UPDATE_SUPPORTED_PARTS",
    "PLAYLISTS_UPDATE_TOOL_NAME",
    "PLAYLISTS_UPDATE_USAGE_NOTES",
    "PLAYLISTS_LIST_CALLER_EXAMPLES",
    "PLAYLISTS_LIST_CAVEATS",
    "PLAYLISTS_LIST_DESCRIPTION",
    "PLAYLISTS_LIST_INPUT_SCHEMA",
    "PLAYLISTS_LIST_MAX_RESULTS",
    "PLAYLISTS_LIST_QUOTA_COST",
    "PLAYLISTS_LIST_SELECTORS",
    "PLAYLISTS_LIST_SUPPORTED_PARTS",
    "PLAYLISTS_LIST_TOOL_NAME",
    "PLAYLISTS_LIST_USAGE_NOTES",
    "PlaylistsInsertToolError",
    "PlaylistsDeleteToolError",
    "PlaylistsUpdateToolError",
    "PlaylistsListToolError",
    "build_playlists_insert_contract",
    "build_playlists_delete_contract",
    "build_playlists_insert_handler",
    "build_playlists_delete_handler",
    "build_playlists_insert_tool_descriptor",
    "build_playlists_delete_tool_descriptor",
    "build_playlists_update_contract",
    "build_playlists_update_handler",
    "build_playlists_update_tool_descriptor",
    "build_playlists_list_contract",
    "build_playlists_list_handler",
    "build_playlists_list_tool_descriptor",
    "map_playlists_insert_result",
    "map_playlists_delete_result",
    "map_playlists_update_result",
    "map_playlists_list_result",
    "validate_playlists_insert_arguments",
    "validate_playlists_delete_arguments",
    "validate_playlists_update_arguments",
    "validate_playlists_list_arguments",
]
