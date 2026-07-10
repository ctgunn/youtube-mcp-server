"""Concrete Layer 2 tool support for the YouTube ``playlistItems`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlist_items import (
    build_playlist_items_insert_wrapper,
    build_playlist_items_list_wrapper,
    build_playlist_items_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLIST_ITEMS_LIST_TOOL_NAME = "playlistItems_list"
PLAYLIST_ITEMS_LIST_QUOTA_COST = 1
PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS = ("contentDetails", "id", "snippet", "status")
PLAYLIST_ITEMS_LIST_SELECTORS = ("playlistId", "id")
PLAYLIST_ITEMS_LIST_MAX_RESULTS = 50
PLAYLIST_ITEMS_INSERT_TOOL_NAME = "playlistItems_insert"
PLAYLIST_ITEMS_INSERT_QUOTA_COST = 50
PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS = ("snippet",)
PLAYLIST_ITEMS_UPDATE_TOOL_NAME = "playlistItems_update"
PLAYLIST_ITEMS_UPDATE_QUOTA_COST = 50
PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS = ("snippet",)

PLAYLIST_ITEMS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS)},
        "playlistId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLIST_ITEMS_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLIST_ITEMS_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["playlistId", "resourceId"],
                    "properties": {
                        "playlistId": {"type": "string", "minLength": 1},
                        "position": {"type": "integer", "minimum": 0},
                        "resourceId": {
                            "type": "object",
                            "required": ["videoId"],
                            "properties": {
                                "kind": {"type": "string", "enum": ["youtube#video"]},
                                "videoId": {"type": "string", "minLength": 1},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "snippet": {
                    "type": "object",
                    "required": ["playlistId", "resourceId"],
                    "properties": {
                        "playlistId": {"type": "string", "minLength": 1},
                        "resourceId": {
                            "type": "object",
                            "required": ["videoId"],
                            "properties": {
                                "kind": {"type": "string", "enum": ["youtube#video"]},
                                "videoId": {"type": "string", "minLength": 1},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLIST_ITEMS_LIST_DESCRIPTION = (
    "List YouTube playlist item resources. Endpoint: playlistItems.list. "
    "Quota cost: 1. Auth: api_key."
)

PLAYLIST_ITEMS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part and exactly one selector: playlistId or id.",
    "Quota cost: 1. Use playlistId for playlist-scoped traversal with optional pageToken and maxResults.",
    "Quota cost: 1. Use id for direct playlist-item lookup; pageToken and maxResults are rejected with id.",
    "Quota cost: 1. Valid empty item collections remain successful list results.",
)

PLAYLIST_ITEMS_LIST_CAVEATS = (
    "This tool only retrieves playlist item resources through playlistItems.list.",
    "playlist item mutation, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, "
    "recommendation, ranking, summarization, enrichment, and cross-endpoint aggregation are out of scope.",
    "Returned playlist item fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES = (
    {
        "name": "playlist_scoped_item_listing",
        "description": "Quota cost: 1. List playlist items for one playlistId with API-key access.",
        "arguments": {"part": "snippet,contentDetails", "playlistId": "PL123"},
        "result": {"endpoint": "playlistItems.list", "selector": "playlistId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_item_lookup",
        "description": "Quota cost: 1. Retrieve playlist items by item id with API-key access.",
        "arguments": {"part": "id,snippet", "id": "playlist-item-123"},
        "result": {"endpoint": "playlistItems.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_item_listing",
        "description": "Quota cost: 1. Continue playlist-scoped traversal with pageToken and maxResults.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An accessible empty playlist item collection remains a successful list result.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistItems.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing required playlist-item part selection.",
        "arguments": {"playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside contentDetails, id, snippet, and status.",
        "arguments": {"part": "statistics", "playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_selector",
        "description": "Reject requests missing both playlistId and id selectors.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "conflicting_selector",
        "description": "Reject requests that provide both playlistId and id.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "id": "playlist-item-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "playlist-item-123", "pageToken": "NEXT_PAGE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing, invalid, or insufficient API-key access to safe access errors.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "out_of_scope_playlist_item_workflow",
        "description": "playlist item mutation, video enrichment, analytics, and recommendation requests are out of scope.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "insert": {"videoId": "video-123"}},
        "errorCategory": "invalid_request",
    },
)

PLAYLIST_ITEMS_INSERT_DESCRIPTION = (
    "Insert a YouTube playlist item. Endpoint: playlistItems.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires body.snippet.playlistId "
    "and body.snippet.resourceId.videoId."
)

PLAYLIST_ITEMS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and a playlist-item creation body.",
    "Quota cost: 50. body.snippet.playlistId identifies the target playlist to modify.",
    "Quota cost: 50. body.snippet.resourceId.videoId identifies the video to add to the playlist.",
    "Quota cost: 50. body.snippet.position is optional supported placement context when accepted.",
)

PLAYLIST_ITEMS_INSERT_CAVEATS = (
    "playlistItems_insert creates one playlist item through playlistItems.insert and requires OAuth authorization.",
    "Use playlistItems_list for playlist-item retrieval; this tool only performs playlistItems.insert.",
    "body.snippet.playlistId and body.snippet.resourceId.videoId are required for supported insert requests.",
    "Unsupported placement details, read-only fields, playlist item listing, updates, deletion, playlist search, "
    "video enrichment, analytics, ranking, summarization, recommendation, and automated curation are out of scope.",
    "Returned playlist item fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "oauth_playlist_item_insertion",
        "description": "Quota cost: 50. Insert a video into a playlist with OAuth authorization.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                }
            },
        },
        "result": {"endpoint": "playlistItems.insert", "quotaCost": 50, "created": True},
        "quotaCost": 50,
    },
    {
        "name": "positioned_playlist_item_insertion",
        "description": "Quota cost: 50. Insert a video with supported playlist placement context.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                }
            },
        },
        "result": {"endpoint": "playlistItems.insert", "quotaCost": 50, "placement": {"position": 0}},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject insert requests missing required part selection.",
        "arguments": {
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 50. Reject insert part values outside the writable snippet part.",
        "arguments": {
            "part": "statistics",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "missing_playlist_id",
        "description": "Quota cost: 50. Reject body payloads missing body.snippet.playlistId.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"resourceId": {"kind": "youtube#video", "videoId": "video-123"}}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.playlistId"},
        "quotaCost": 50,
    },
    {
        "name": "missing_video_reference",
        "description": "Quota cost: 50. Reject body payloads missing body.snippet.resourceId.videoId.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"kind": "youtube#video"}}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.resourceId.videoId"},
        "quotaCost": 50,
    },
    {
        "name": "invalid_body",
        "description": "Quota cost: 50. Reject malformed, read-only, or unsupported playlist-item body fields.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "read-only", "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
        },
        "error": {"category": "invalid_request", "field": "body.id"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_placement",
        "description": "Quota cost: 50. Reject unsupported or out-of-bound playlist item placement details.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "position": -1, "resourceId": {"videoId": "video-123"}}},
        },
        "error": {"category": "invalid_request", "field": "body.snippet.position"},
        "quotaCost": 50,
    },
    {
        "name": "authorization_failure",
        "description": "Quota cost: 50. Map missing or insufficient OAuth access to safe authorization failures.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
        },
        "error": {"category": "authentication_failed"},
        "quotaCost": 50,
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 50. Map quota, duplicate video, ineligible video, or upstream insert failures safely.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
        },
        "error": {"category": "quota_exhausted"},
        "quotaCost": 50,
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Quota cost: 50. Playlist item listing, playlist search, ranking, and enrichment are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            "generatePlaylist": True,
        },
        "error": {"category": "invalid_request", "field": "generatePlaylist"},
        "quotaCost": 50,
    },
)

PLAYLIST_ITEMS_UPDATE_DESCRIPTION = (
    "Update a YouTube playlist item. Endpoint: playlistItems.update. "
    "Quota cost: 50. Auth: oauth_required. Requires body.id, "
    "body.snippet.playlistId, and body.snippet.resourceId.videoId."
)

PLAYLIST_ITEMS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and a playlist-item update body.",
    "Quota cost: 50. body.id identifies the existing playlist item to update.",
    "Quota cost: 50. body.snippet.playlistId preserves the target playlist context.",
    "Quota cost: 50. body.snippet.resourceId.videoId preserves the referenced video context.",
)

PLAYLIST_ITEMS_UPDATE_CAVEATS = (
    "playlistItems_update updates one playlist item through playlistItems.update and requires OAuth authorization.",
    "Use playlistItems_list for playlist-item retrieval and playlistItems_insert for creation; this tool only performs "
    "playlistItems.update.",
    "body.id, body.snippet.playlistId, and body.snippet.resourceId.videoId are required for supported update requests.",
    "Unsupported placement details, content-detail updates, read-only fields, playlist item listing, insertion, deletion, "
    "playlist search, video enrichment, analytics, ranking, summarization, recommendation, and automated curation are "
    "out of scope.",
    "Returned playlist item fields depend on selected parts and upstream availability; missing optional fields are not "
    "fabricated.",
)

PLAYLIST_ITEMS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "oauth_playlist_item_update",
        "description": "Quota cost: 50. Update an existing playlist item with OAuth authorization.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                },
            },
        },
        "result": {"endpoint": "playlistItems.update", "quotaCost": 50, "updated": True},
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 50. Reject update requests missing required part selection.",
        "arguments": {
            "body": {
                "id": "playlist-item-123",
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                },
            },
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 50. Reject update part values outside the writable snippet part.",
        "arguments": {
            "part": "statistics",
            "body": {
                "id": "playlist-item-123",
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                },
            },
        },
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 50,
    },
    {
        "name": "missing_target_identity",
        "description": "Quota cost: 50. Reject update bodies missing body.id.",
        "arguments": {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                }
            },
        },
        "error": {"category": "invalid_request", "field": "body.id"},
        "quotaCost": 50,
    },
    {
        "name": "missing_playlist_id",
        "description": "Quota cost: 50. Reject update bodies missing body.snippet.playlistId.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"resourceId": {"kind": "youtube#video", "videoId": "video-123"}},
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.playlistId"},
        "quotaCost": 50,
    },
    {
        "name": "missing_video_reference",
        "description": "Quota cost: 50. Reject update bodies missing body.snippet.resourceId.videoId.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"kind": "youtube#video"}},
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.resourceId.videoId"},
        "quotaCost": 50,
    },
    {
        "name": "invalid_body",
        "description": "Quota cost: 50. Reject malformed, read-only, or unsupported playlist-item update fields.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "etag": "read-only",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            },
        },
        "error": {"category": "invalid_request", "field": "body.etag"},
        "quotaCost": 50,
    },
    {
        "name": "unsupported_writable_field",
        "description": "Quota cost: 50. Reject unsupported placement or content-detail update fields.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {
                    "playlistId": "PL123",
                    "position": 0,
                    "resourceId": {"videoId": "video-123"},
                },
            },
        },
        "error": {"category": "invalid_request", "field": "body.snippet.position"},
        "quotaCost": 50,
    },
    {
        "name": "authorization_failure",
        "description": "Quota cost: 50. Map missing or insufficient OAuth access to safe authorization failures.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            },
        },
        "error": {"category": "authentication_failed"},
        "quotaCost": 50,
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 50. Map quota, missing-resource, or upstream update failures safely.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            },
        },
        "error": {"category": "quota_exhausted"},
        "quotaCost": 50,
    },
    {
        "name": "out_of_scope_playlist_management_request",
        "description": "Quota cost: 50. Playlist item listing, playlist search, ranking, and enrichment are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-item-123",
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            },
            "rankPlaylist": True,
        },
        "error": {"category": "invalid_request", "field": "rankPlaylist"},
        "quotaCost": 50,
    },
)


class PlaylistItemsListToolError(ValueError):
    """Represent a safe caller-facing ``playlistItems_list`` failure.

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
        """Initialize a sanitized playlist-items list tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistItemsInsertToolError(ValueError):
    """Represent a safe caller-facing ``playlistItems_insert`` failure.

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
        """Initialize a sanitized playlist-items insert tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistItemsUpdateToolError(ValueError):
    """Represent a safe caller-facing ``playlistItems_update`` failure.

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
        """Initialize a sanitized playlist-items update tool error.

        :param message: Human-readable failure summary.
        :param category: Stable safe failure category.
        :param details: Optional diagnostic details to sanitize before exposure.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist-item part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlist_items_parts(part: Any) -> str:
    """Validate and normalize requested playlist-item parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistItemsListToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistItemsListToolError("playlistItems_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistItemsListToolError(
            "playlistItems_list part must use contentDetails, id, snippet, status, or a comma-delimited subset",
            details={"field": "part", "allowed": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlist_items_insert_parts(part: Any) -> str:
    """Validate and normalize requested playlist-item insert parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistItemsInsertToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistItemsInsertToolError("playlistItems_insert requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistItemsInsertToolError(
            "playlistItems_insert part must use the writable snippet part",
            details={"field": "part", "allowed": list(PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlist_items_update_parts(part: Any) -> str:
    """Validate and normalize requested playlist-item update parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistItemsUpdateToolError: If part is missing, duplicated, or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistItemsUpdateToolError("playlistItems_update requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistItemsUpdateToolError(
            "playlistItems_update part must use the writable snippet part",
            details={"field": "part", "allowed": list(PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _require_object(value: Any, field: str) -> dict[str, Any]:
    """Validate that a playlist-item insert field is an object.

    :param value: Candidate object value.
    :param field: Caller-facing field path.
    :return: The candidate value when it is a dictionary.
    :raises PlaylistItemsInsertToolError: If the value is not an object.
    """
    if not isinstance(value, dict):
        raise PlaylistItemsInsertToolError(f"playlistItems_insert requires {field}", details={"field": field})
    return value


def _require_non_empty_string(value: Any, field: str) -> str:
    """Validate and normalize a required string in an insert request.

    :param value: Candidate string value.
    :param field: Caller-facing field path.
    :return: Trimmed non-empty string.
    :raises PlaylistItemsInsertToolError: If the value is missing or blank.
    """
    if not isinstance(value, str) or not value.strip():
        raise PlaylistItemsInsertToolError(f"playlistItems_insert requires {field}", details={"field": field})
    return value.strip()


def _reject_unknown_fields(fields: set[str], allowed: set[str], prefix: str) -> None:
    """Reject unsupported fields in a playlist-item insert request object.

    :param fields: Field names supplied by the caller.
    :param allowed: Field names supported by the public contract.
    :param prefix: Caller-facing field prefix.
    :raises PlaylistItemsInsertToolError: If an unsupported field is present.
    """
    unsupported = sorted(fields - allowed)
    if unsupported:
        field = f"{prefix}.{unsupported[0]}" if prefix else unsupported[0]
        raise PlaylistItemsInsertToolError(
            f"unsupported field for playlistItems_insert: {field}",
            details={"field": field},
        )


def _require_update_object(value: Any, field: str) -> dict[str, Any]:
    """Validate that a playlist-item update field is an object.

    :param value: Candidate object value.
    :param field: Caller-facing field path.
    :return: The candidate value when it is a dictionary.
    :raises PlaylistItemsUpdateToolError: If the value is not an object.
    """
    if not isinstance(value, dict):
        raise PlaylistItemsUpdateToolError(f"playlistItems_update requires {field}", details={"field": field})
    return value


def _require_update_non_empty_string(value: Any, field: str) -> str:
    """Validate and normalize a required string in an update request.

    :param value: Candidate string value.
    :param field: Caller-facing field path.
    :return: Trimmed non-empty string.
    :raises PlaylistItemsUpdateToolError: If the value is missing or blank.
    """
    if not isinstance(value, str) or not value.strip():
        raise PlaylistItemsUpdateToolError(f"playlistItems_update requires {field}", details={"field": field})
    return value.strip()


def _reject_update_unknown_fields(fields: set[str], allowed: set[str], prefix: str) -> None:
    """Reject unsupported fields in a playlist-item update request object.

    :param fields: Field names supplied by the caller.
    :param allowed: Field names supported by the public update contract.
    :param prefix: Caller-facing field prefix.
    :raises PlaylistItemsUpdateToolError: If an unsupported field is present.
    """
    unsupported = sorted(fields - allowed)
    if unsupported:
        field = f"{prefix}.{unsupported[0]}" if prefix else unsupported[0]
        raise PlaylistItemsUpdateToolError(
            f"unsupported field for playlistItems_update: {field}",
            details={"field": field},
        )


def validate_playlist_items_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistItems_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistItemsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistItemsListToolError("playlistItems_list arguments must be an object")

    allowed = {"part", "playlistId", "id", "pageToken", "maxResults"}
    for field in arguments:
        if field not in allowed:
            raise PlaylistItemsListToolError(
                f"unsupported field for playlistItems_list: {field}",
                details={"field": field},
            )

    part = _validate_playlist_items_parts(arguments.get("part"))
    selected = [
        selector
        for selector in PLAYLIST_ITEMS_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise PlaylistItemsListToolError(
            "playlistItems_list requires exactly one selector: playlistId or id",
            details={"field": "selector", "allowed": list(PLAYLIST_ITEMS_LIST_SELECTORS)},
        )

    selector = selected[0]
    normalized: dict[str, Any] = {"part": part, selector: arguments[selector].strip()}
    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistItemsListToolError(
            "pageToken and maxResults are only supported with playlistId",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistItemsListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistItemsListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLIST_ITEMS_LIST_MAX_RESULTS:
            raise PlaylistItemsListToolError(
                f"maxResults must be between 0 and {PLAYLIST_ITEMS_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLIST_ITEMS_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def validate_playlist_items_insert_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistItems_insert`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistItemsInsertToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistItemsInsertToolError("playlistItems_insert arguments must be an object")

    _reject_unknown_fields(set(arguments), {"part", "body"}, "")
    part = _validate_playlist_items_insert_parts(arguments.get("part"))
    body = _require_object(arguments.get("body"), "body")
    _reject_unknown_fields(set(body), {"snippet"}, "body")
    snippet = _require_object(body.get("snippet"), "body.snippet")
    _reject_unknown_fields(set(snippet), {"playlistId", "resourceId", "position"}, "body.snippet")
    playlist_id = _require_non_empty_string(snippet.get("playlistId"), "body.snippet.playlistId")
    resource_id = _require_object(snippet.get("resourceId"), "body.snippet.resourceId")
    _reject_unknown_fields(set(resource_id), {"kind", "videoId"}, "body.snippet.resourceId")
    video_id = _require_non_empty_string(resource_id.get("videoId"), "body.snippet.resourceId.videoId")
    kind = resource_id.get("kind")
    if kind is not None:
        if not isinstance(kind, str) or kind.strip() != "youtube#video":
            raise PlaylistItemsInsertToolError(
                "playlistItems_insert resource kind must be youtube#video",
                details={"field": "body.snippet.resourceId.kind"},
            )
        kind = kind.strip()
    normalized_snippet: dict[str, Any] = {
        "playlistId": playlist_id,
        "resourceId": {"videoId": video_id},
    }
    if kind:
        normalized_snippet["resourceId"]["kind"] = kind
    if "position" in snippet:
        position = snippet["position"]
        if isinstance(position, bool) or not isinstance(position, int) or position < 0:
            raise PlaylistItemsInsertToolError(
                "playlistItems_insert position must be a non-negative integer",
                details={"field": "body.snippet.position"},
            )
        normalized_snippet["position"] = position
    return {"part": part, "body": {"snippet": normalized_snippet}}


def validate_playlist_items_update_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistItems_update`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistItemsUpdateToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistItemsUpdateToolError("playlistItems_update arguments must be an object")

    _reject_update_unknown_fields(set(arguments), {"part", "body"}, "")
    part = _validate_playlist_items_update_parts(arguments.get("part"))
    body = _require_update_object(arguments.get("body"), "body")
    _reject_update_unknown_fields(set(body), {"id", "snippet"}, "body")
    playlist_item_id = _require_update_non_empty_string(body.get("id"), "body.id")
    snippet = _require_update_object(body.get("snippet"), "body.snippet")
    _reject_update_unknown_fields(set(snippet), {"playlistId", "resourceId"}, "body.snippet")
    playlist_id = _require_update_non_empty_string(snippet.get("playlistId"), "body.snippet.playlistId")
    resource_id = _require_update_object(snippet.get("resourceId"), "body.snippet.resourceId")
    _reject_update_unknown_fields(set(resource_id), {"kind", "videoId"}, "body.snippet.resourceId")
    video_id = _require_update_non_empty_string(resource_id.get("videoId"), "body.snippet.resourceId.videoId")
    kind = resource_id.get("kind")
    if kind is not None:
        if not isinstance(kind, str) or kind.strip() != "youtube#video":
            raise PlaylistItemsUpdateToolError(
                "playlistItems_update resource kind must be youtube#video",
                details={"field": "body.snippet.resourceId.kind"},
            )
        kind = kind.strip()
    normalized_resource: dict[str, Any] = {"videoId": video_id}
    if kind:
        normalized_resource["kind"] = kind
    return {
        "part": part,
        "body": {
            "id": playlist_item_id,
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": normalized_resource,
            },
        },
    }


def map_playlist_items_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist-items payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-items list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlist_items_list_arguments(arguments)
    selector = "playlistId" if "playlistId" in normalized else "id"
    result = {
        "endpoint": "playlistItems.list",
        "quotaCost": PLAYLIST_ITEMS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": "api_key"},
        "items": payload.get("items", []),
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


def _playlist_items_insert_assignment_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Return safe playlist/video assignment context for an insert request.

    :param arguments: Validated ``playlistItems_insert`` arguments.
    :return: Safe assignment context with playlist and video identifiers.
    """
    snippet = arguments["body"]["snippet"]
    resource_id = snippet["resourceId"]
    context = {"playlistId": snippet["playlistId"], "videoId": resource_id["videoId"]}
    if "kind" in resource_id:
        context["resourceKind"] = resource_id["kind"]
    return context


def _playlist_items_insert_placement_context(arguments: dict[str, Any]) -> dict[str, int]:
    """Return safe playlist-item placement context for an insert request.

    :param arguments: Validated ``playlistItems_insert`` arguments.
    :return: Placement context when supplied, otherwise an empty dictionary.
    """
    snippet = arguments["body"]["snippet"]
    if "position" in snippet:
        return {"position": snippet["position"]}
    return {}


def map_playlist_items_insert_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist item creation payload to the public result.

    :param payload: Upstream or Layer 1 playlist item insert payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw created-resource result with safe operation context.
    """
    normalized = validate_playlist_items_insert_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlistItems.insert",
        "quotaCost": PLAYLIST_ITEMS_INSERT_QUOTA_COST,
        "created": True,
        "requestedParts": _split_parts(normalized["part"]),
        "assignment": _playlist_items_insert_assignment_context(normalized),
        "auth": {"mode": "oauth_required"},
        "item": payload,
    }
    placement = _playlist_items_insert_placement_context(normalized)
    if placement:
        result["placement"] = placement
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def _playlist_items_update_target_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Return safe playlist-item target context for an update request.

    :param arguments: Validated ``playlistItems_update`` arguments.
    :return: Safe target context with playlist item, playlist, and video identifiers.
    """
    body = arguments["body"]
    snippet = body["snippet"]
    resource_id = snippet["resourceId"]
    context = {
        "playlistItemId": body["id"],
        "playlistId": snippet["playlistId"],
        "videoId": resource_id["videoId"],
    }
    if "kind" in resource_id:
        context["resourceKind"] = resource_id["kind"]
    return context


def _playlist_items_update_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Return safe writable update context for a playlist-item update request.

    :param arguments: Validated ``playlistItems_update`` arguments.
    :return: Safe update context with playlist and video identifiers.
    """
    snippet = arguments["body"]["snippet"]
    resource_id = snippet["resourceId"]
    context = {"playlistId": snippet["playlistId"], "videoId": resource_id["videoId"]}
    if "kind" in resource_id:
        context["resourceKind"] = resource_id["kind"]
    return context


def map_playlist_items_update_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist item update payload to the public result.

    :param payload: Upstream or Layer 1 playlist item update payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw updated-resource result with safe operation context.
    """
    normalized = validate_playlist_items_update_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlistItems.update",
        "quotaCost": PLAYLIST_ITEMS_UPDATE_QUOTA_COST,
        "updated": True,
        "requestedParts": _split_parts(normalized["part"]),
        "target": _playlist_items_update_target_context(normalized),
        "update": _playlist_items_update_context(normalized),
        "auth": {"mode": "oauth_required"},
        "item": payload,
    }
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_playlist_items_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistItemsListToolError:
    """Map a normalized upstream failure to a safe ``playlistItems_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
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
        "deprecated": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistItemsListToolError(str(error), category=category, details=error.details)


def _map_playlist_items_insert_upstream_error(error: NormalizedUpstreamError) -> PlaylistItemsInsertToolError:
    """Map a normalized upstream failure to a safe ``playlistItems_insert`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "duplicate": "invalid_request",
        "ineligible": "invalid_request",
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
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistItemsInsertToolError(str(error), category=category, details=error.details)


def _map_playlist_items_update_upstream_error(error: NormalizedUpstreamError) -> PlaylistItemsUpdateToolError:
    """Map a normalized upstream failure to a safe ``playlistItems_update`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "invalid_writable_field": "invalid_request",
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
        "deprecated": "deprecated_endpoint",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistItemsUpdateToolError(str(error), category=category, details=error.details)


def _playlist_items_list_access_context(api_key: str | None) -> AuthContext:
    """Build the API-key auth context for ``playlistItems_list``.

    :param api_key: API key used for playlist-item retrieval.
    :return: Layer 1 auth context configured for API-key execution.
    :raises PlaylistItemsListToolError: If no API key is available.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise PlaylistItemsListToolError(
            "playlistItems_list requires API-key access",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.API_KEY,
        credentials=CredentialBundle(api_key=api_key.strip()),
    )


def _playlist_items_insert_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistItems_insert``.

    :param oauth_token: OAuth token used for playlist-item insertion.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistItemsInsertToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistItemsInsertToolError(
            "playlistItems_insert requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def _playlist_items_update_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistItems_update``.

    :param oauth_token: OAuth token used for playlist-item updates.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistItemsUpdateToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistItemsUpdateToolError(
            "playlistItems_update requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_playlist_items_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistItems_list``.

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
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "playlist_item_insertion",
            "playlist_item_update",
            "playlist_item_deletion",
            "playlist_mutation",
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
        tool_name=PLAYLIST_ITEMS_LIST_TOOL_NAME,
        upstream_resource="playlistItems",
        upstream_method="list",
        operation_key="playlistItems.list",
        description=PLAYLIST_ITEMS_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=PLAYLIST_ITEMS_LIST_QUOTA_COST,
        resource_family="playlist_items",
        input_contract=PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLIST_ITEMS_LIST_SELECTORS),
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
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=PLAYLIST_ITEMS_LIST_USAGE_NOTES,
        caveats=PLAYLIST_ITEMS_LIST_CAVEATS,
    )


def build_playlist_items_insert_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistItems_insert``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "created",
            "requestedParts",
            "assignment",
            "placement",
            "auth",
            "item",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "contentDetails", "status"),
        disallowed_behavior=(
            "playlist_item_listing",
            "playlist_item_update",
            "playlist_item_deletion",
            "playlist_search",
            "playlist_generation",
            "video_enrichment",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "automated_curation",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_ITEMS_INSERT_TOOL_NAME,
        upstream_resource="playlistItems",
        upstream_method="insert",
        operation_key="playlistItems.insert",
        description=PLAYLIST_ITEMS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_ITEMS_INSERT_QUOTA_COST,
        resource_family="playlist_items",
        input_contract=PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "item",
            "requestedParts": list(PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS),
            "supportedWritableParts": ["snippet"],
            "assignmentFields": ["body.snippet.playlistId", "body.snippet.resourceId.videoId"],
            "placementFields": ["body.snippet.position"],
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
        usage_notes=PLAYLIST_ITEMS_INSERT_USAGE_NOTES,
        caveats=PLAYLIST_ITEMS_INSERT_CAVEATS,
    )


def build_playlist_items_update_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistItems_update``.

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
            "item",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "contentDetails", "status"),
        disallowed_behavior=(
            "playlist_item_listing",
            "playlist_item_insertion",
            "playlist_item_deletion",
            "playlist_search",
            "playlist_generation",
            "video_enrichment",
            "transcript_retrieval",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "automated_curation",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_ITEMS_UPDATE_TOOL_NAME,
        upstream_resource="playlistItems",
        upstream_method="update",
        operation_key="playlistItems.update",
        description=PLAYLIST_ITEMS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_ITEMS_UPDATE_QUOTA_COST,
        resource_family="playlist_items",
        input_contract=PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "requestedParts": list(PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS),
            "supportedWritableParts": ["snippet"],
            "targetFields": ["body.id"],
            "updateFields": ["body.snippet.playlistId", "body.snippet.resourceId.videoId"],
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
        usage_notes=PLAYLIST_ITEMS_UPDATE_USAGE_NOTES,
        caveats=PLAYLIST_ITEMS_UPDATE_CAVEATS,
    )


def _default_playlist_items_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-item calls.

    :return: Integration executor returning representative playlist-item data.
    """

    def transport(execution):
        """Return a representative playlist-item list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistItemListResponse",
            "etag": "etag-playlist-items",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "etag-playlist-item",
                    "id": execution.arguments.get("id", "playlist-item-123"),
                    "snippet": {
                        "playlistId": execution.arguments.get("playlistId", "PL123"),
                        "title": "Representative playlist item",
                        "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                    },
                    "contentDetails": {"videoId": "video-123"},
                    "status": {"privacyStatus": "public"},
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlist_items_insert_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist item inserts.

    :return: Integration executor returning representative created playlist-item data.
    """

    def transport(execution):
        """Return a representative created playlist item response.

        :param execution: Request execution context.
        :return: Fake upstream created-resource response for local invocation.
        """
        snippet = execution.arguments.get("body", {}).get("snippet", {})
        resource_id = snippet.get("resourceId", {})
        return {
            "kind": "youtube#playlistItem",
            "etag": "etag-playlist-item",
            "id": "playlist-item-123",
            "snippet": {
                "playlistId": snippet.get("playlistId", "PL123"),
                "position": snippet.get("position", 0),
                "resourceId": {
                    "kind": resource_id.get("kind", "youtube#video"),
                    "videoId": resource_id.get("videoId", "video-123"),
                },
                "title": "Representative playlist item",
            },
            "contentDetails": {"videoId": resource_id.get("videoId", "video-123")},
            "status": {"privacyStatus": "public"},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlist_items_update_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist item updates.

    :return: Integration executor returning representative updated playlist-item data.
    """

    def transport(execution):
        """Return a representative updated playlist item response.

        :param execution: Request execution context.
        :return: Fake upstream updated-resource response for local invocation.
        """
        body = execution.arguments.get("body", {})
        snippet = body.get("snippet", {})
        resource_id = snippet.get("resourceId", {})
        return {
            "kind": "youtube#playlistItem",
            "etag": "etag-playlist-item",
            "id": body.get("id", "playlist-item-123"),
            "snippet": {
                "playlistId": snippet.get("playlistId", "PL123"),
                "resourceId": {
                    "kind": resource_id.get("kind", "youtube#video"),
                    "videoId": resource_id.get("videoId", "video-123"),
                },
                "title": "Representative playlist item",
            },
            "contentDetails": {"videoId": resource_id.get("videoId", "video-123")},
            "status": {"privacyStatus": "public"},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlist_items_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``playlistItems_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps playlist-item requests.
    """
    selected_wrapper = wrapper or build_playlist_items_list_wrapper()
    selected_executor = executor or _default_playlist_items_list_executor()
    auth_context = _playlist_items_list_access_context(api_key)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistItems_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-item list result.
        :raises PlaylistItemsListToolError: If validation or execution fails.
        """
        normalized = validate_playlist_items_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_items_list_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistItemsListToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistItems.list"},
            ) from exc
        return map_playlist_items_list_result(payload, normalized)

    return handler


def build_playlist_items_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistItems_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe auth context.
    :return: Callable that validates, executes, and maps playlist-item insert requests.
    """
    selected_wrapper = wrapper or build_playlist_items_insert_wrapper()
    selected_executor = executor or _default_playlist_items_insert_executor()
    auth_context = _playlist_items_insert_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistItems_insert`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-item insert result.
        :raises PlaylistItemsInsertToolError: If validation or execution fails.
        """
        normalized = validate_playlist_items_insert_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_items_insert_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistItemsInsertToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistItems.insert"},
            ) from exc
        return map_playlist_items_insert_result(payload, normalized)

    return handler


def build_playlist_items_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistItems_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe auth context.
    :return: Callable that validates, executes, and maps playlist-item update requests.
    """
    selected_wrapper = wrapper or build_playlist_items_update_wrapper()
    selected_executor = executor or _default_playlist_items_update_executor()
    auth_context = _playlist_items_update_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistItems_update`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-item update result.
        :raises PlaylistItemsUpdateToolError: If validation or execution fails.
        """
        normalized = validate_playlist_items_update_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_items_update_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistItemsUpdateToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistItems.update"},
            ) from exc
        return map_playlist_items_update_result(payload, normalized)

    return handler


def build_playlist_items_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistItems_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_items_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_ITEMS_LIST_TOOL_NAME,
        "description": PLAYLIST_ITEMS_LIST_DESCRIPTION,
        "inputSchema": PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
        "handler": build_playlist_items_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


def build_playlist_items_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistItems_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_items_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_ITEMS_INSERT_TOOL_NAME,
        "description": PLAYLIST_ITEMS_INSERT_DESCRIPTION,
        "inputSchema": PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA,
        "handler": build_playlist_items_insert_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_playlist_items_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistItems_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_items_update_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_ITEMS_UPDATE_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_ITEMS_UPDATE_TOOL_NAME,
        "description": PLAYLIST_ITEMS_UPDATE_DESCRIPTION,
        "inputSchema": PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA,
        "handler": build_playlist_items_update_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES",
    "PLAYLIST_ITEMS_INSERT_CAVEATS",
    "PLAYLIST_ITEMS_INSERT_DESCRIPTION",
    "PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA",
    "PLAYLIST_ITEMS_INSERT_QUOTA_COST",
    "PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS",
    "PLAYLIST_ITEMS_INSERT_TOOL_NAME",
    "PLAYLIST_ITEMS_INSERT_USAGE_NOTES",
    "PLAYLIST_ITEMS_UPDATE_CALLER_EXAMPLES",
    "PLAYLIST_ITEMS_UPDATE_CAVEATS",
    "PLAYLIST_ITEMS_UPDATE_DESCRIPTION",
    "PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA",
    "PLAYLIST_ITEMS_UPDATE_QUOTA_COST",
    "PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS",
    "PLAYLIST_ITEMS_UPDATE_TOOL_NAME",
    "PLAYLIST_ITEMS_UPDATE_USAGE_NOTES",
    "PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES",
    "PLAYLIST_ITEMS_LIST_CAVEATS",
    "PLAYLIST_ITEMS_LIST_DESCRIPTION",
    "PLAYLIST_ITEMS_LIST_INPUT_SCHEMA",
    "PLAYLIST_ITEMS_LIST_MAX_RESULTS",
    "PLAYLIST_ITEMS_LIST_QUOTA_COST",
    "PLAYLIST_ITEMS_LIST_SELECTORS",
    "PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS",
    "PLAYLIST_ITEMS_LIST_TOOL_NAME",
    "PLAYLIST_ITEMS_LIST_USAGE_NOTES",
    "PlaylistItemsInsertToolError",
    "PlaylistItemsListToolError",
    "PlaylistItemsUpdateToolError",
    "build_playlist_items_insert_contract",
    "build_playlist_items_insert_handler",
    "build_playlist_items_insert_tool_descriptor",
    "build_playlist_items_update_contract",
    "build_playlist_items_update_handler",
    "build_playlist_items_update_tool_descriptor",
    "build_playlist_items_list_contract",
    "build_playlist_items_list_handler",
    "build_playlist_items_list_tool_descriptor",
    "map_playlist_items_insert_result",
    "map_playlist_items_update_result",
    "map_playlist_items_list_result",
    "validate_playlist_items_insert_arguments",
    "validate_playlist_items_update_arguments",
    "validate_playlist_items_list_arguments",
]
