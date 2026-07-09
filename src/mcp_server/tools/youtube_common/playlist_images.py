"""Concrete Layer 2 tool support for the YouTube ``playlistImages`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.playlist_images import (
    build_playlist_images_delete_wrapper,
    build_playlist_images_insert_wrapper,
    build_playlist_images_list_wrapper,
    build_playlist_images_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


PLAYLIST_IMAGES_ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "application/octet-stream")

PLAYLIST_IMAGES_LIST_TOOL_NAME = "playlistImages_list"
PLAYLIST_IMAGES_LIST_QUOTA_COST = 1
PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS = ("id", "snippet")
PLAYLIST_IMAGES_LIST_SELECTORS = ("playlistId", "id")
PLAYLIST_IMAGES_LIST_MAX_RESULTS = 50

PLAYLIST_IMAGES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "playlistId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": PLAYLIST_IMAGES_LIST_MAX_RESULTS},
    },
    "oneOf": [{"required": [selector]} for selector in PLAYLIST_IMAGES_LIST_SELECTORS],
    "additionalProperties": False,
}

PLAYLIST_IMAGES_LIST_DESCRIPTION = (
    "List YouTube playlist image resources. Endpoint: playlistImages.list. "
    "Quota cost: 1. Auth: oauth_required."
)

PLAYLIST_IMAGES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: oauth_required. Provide part and exactly one selector: playlistId or id.",
    "Quota cost: 1. Use playlistId for playlist-scoped image retrieval with optional pageToken and maxResults.",
    "Quota cost: 1. Use id for direct playlist image lookup; pageToken and maxResults are rejected with id.",
)

PLAYLIST_IMAGES_LIST_CAVEATS = (
    "This tool only retrieves playlist image resources through playlistImages.list.",
    "playlist image insertion, update, deletion, media upload, thumbnail replacement, and playlist management are out of scope.",
    "Playlist-item expansion, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint aggregation are out of scope.",
)

PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES = (
    {
        "name": "playlist_scoped_image_listing",
        "description": "Quota cost: 1. List playlist images for one playlistId.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistImages.list", "selector": "playlistId", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "direct_image_lookup",
        "description": "Quota cost: 1. Retrieve one playlist image by id.",
        "arguments": {"part": "id,snippet", "id": "playlist-image-123"},
        "result": {"endpoint": "playlistImages.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paged_playlist_image_listing",
        "description": "Quota cost: 1. Continue a playlist-scoped image traversal with paging controls.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An empty playlist-image collection remains a successful list result.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "result": {"endpoint": "playlistImages.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required playlist-image part selection.",
        "arguments": {"playlistId": "PL123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside id and snippet.",
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
        "arguments": {"part": "snippet", "playlistId": "PL123", "id": "playlist-image-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "paging_with_id",
        "description": "Reject pageToken or maxResults when the id selector is used.",
        "arguments": {"part": "snippet", "id": "playlist-image-123", "pageToken": "NEXT_PAGE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access to safe authentication or authorization errors.",
        "arguments": {"part": "snippet", "playlistId": "PL123"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "out_of_scope_image_management_request",
        "description": "Playlist image mutation, upload, thumbnail replacement, and analytics requests are out of scope.",
        "arguments": {"part": "snippet", "playlistId": "PL123", "media": {"content": "raw"}},
        "errorCategory": "invalid_request",
    },
)

PLAYLIST_IMAGES_INSERT_TOOL_NAME = "playlistImages_insert"
PLAYLIST_IMAGES_INSERT_QUOTA_COST = 50
PLAYLIST_IMAGES_INSERT_SUPPORTED_PARTS = ("id", "snippet")

PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body", "media"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "additionalProperties": False,
        },
        "media": {
            "type": "object",
            "required": ["mimeType", "content"],
            "properties": {
                "mimeType": {"type": "string", "enum": list(PLAYLIST_IMAGES_ALLOWED_MIME_TYPES)},
                "content": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLIST_IMAGES_INSERT_DESCRIPTION = (
    "Insert a YouTube playlist image resource. Endpoint: playlistImages.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires body metadata and media upload input."
)

PLAYLIST_IMAGES_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part, body metadata, and media upload input.",
    "Quota cost: 50. body.snippet supplies the playlist-image creation metadata.",
    "Quota cost: 50. media.mimeType and media.content are required; raw media content is never echoed in results.",
)

PLAYLIST_IMAGES_INSERT_CAVEATS = (
    "Playlist image insertion requires eligible OAuth authorization.",
    "Metadata-only and upload-only requests are unsupported.",
    "This tool only creates playlist image resources through playlistImages.insert.",
    "Playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, ranking, summarization, and enrichment are out of scope.",
)

PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_playlist_image_insert",
        "description": "Quota cost: 50. Insert one playlist image with metadata and media upload content.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "result": {
            "endpoint": "playlistImages.insert",
            "quotaCost": 50,
            "bodyContext": {"hasSnippet": True, "playlistId": "PL123"},
            "mediaContext": {"mimeType": "image/jpeg", "contentProvided": True},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required playlist-image part selection.",
        "arguments": {
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside id and snippet.",
        "arguments": {
            "part": "statistics",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_body",
        "description": "Reject requests missing playlist-image creation metadata.",
        "arguments": {
            "part": "snippet",
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_body",
        "description": "Reject metadata that omits body.snippet.",
        "arguments": {
            "part": "snippet",
            "body": {},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_media",
        "description": "Reject requests missing required media upload content.",
        "arguments": {"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_media",
        "description": "Reject unsupported media upload descriptors.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/gif", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access to safe authentication or authorization errors.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "authorization_failed",
    },
    {
        "name": "quota_or_upstream_insert_failure",
        "description": "Map quota and upstream insertion failures to safe shared categories.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "out_of_scope_image_management_request",
        "description": "Playlist image listing, update, deletion, thumbnail replacement, and analytics are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}, "thumbnailReplacement": True},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
)

PLAYLIST_IMAGES_UPDATE_TOOL_NAME = "playlistImages_update"
PLAYLIST_IMAGES_UPDATE_QUOTA_COST = 50
PLAYLIST_IMAGES_UPDATE_SUPPORTED_PARTS = ("id", "snippet")

PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body", "media"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "snippet": {"type": "object"},
            },
            "additionalProperties": False,
        },
        "media": {
            "type": "object",
            "required": ["mimeType", "content"],
            "properties": {
                "mimeType": {"type": "string", "enum": list(PLAYLIST_IMAGES_ALLOWED_MIME_TYPES)},
                "content": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

PLAYLIST_IMAGES_UPDATE_DESCRIPTION = (
    "Update a YouTube playlist image resource. Endpoint: playlistImages.update. "
    "Quota cost: 50. Auth: oauth_required. Requires body.id, body.snippet.playlistId, and media upload input."
)

PLAYLIST_IMAGES_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part, target body metadata, and media upload input.",
    "Quota cost: 50. body.id identifies the existing playlist image and body.snippet.playlistId identifies its playlist.",
    "Quota cost: 50. media.mimeType and media.content are required; raw media content is never echoed in results.",
)

PLAYLIST_IMAGES_UPDATE_CAVEATS = (
    "Playlist image updates require eligible OAuth authorization.",
    "Metadata-only and upload-only requests are unsupported.",
    "This tool only updates playlist image resources through playlistImages.update.",
    "Playlist image listing, insertion, deletion, thumbnail replacement, playlist management, analytics, ranking, summarization, and enrichment are out of scope.",
)

PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "authorized_playlist_image_update",
        "description": "Quota cost: 50. Update one playlist image with target metadata and media upload content.",
        "arguments": {
            "part": "id,snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "result": {
            "endpoint": "playlistImages.update",
            "quotaCost": 50,
            "bodyContext": {"id": "playlist-image-123", "hasSnippet": True, "playlistId": "PL123"},
            "mediaContext": {"mimeType": "image/jpeg", "contentProvided": True},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required playlist-image part selection.",
        "arguments": {
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside id and snippet.",
        "arguments": {
            "part": "statistics",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_body",
        "description": "Reject requests missing playlist-image target metadata.",
        "arguments": {"part": "snippet", "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_body",
        "description": "Reject metadata that is not an object.",
        "arguments": {
            "part": "snippet",
            "body": [],
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_target_identity",
        "description": "Reject metadata that omits body.id.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_playlist_context",
        "description": "Reject metadata that omits body.snippet.playlistId.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_media",
        "description": "Reject requests missing required media upload content.",
        "arguments": {"part": "snippet", "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_media",
        "description": "Reject unsupported media upload descriptors.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/gif", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access to safe authentication or authorization errors.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "authorization_failed",
    },
    {
        "name": "quota_or_upstream_update_failure",
        "description": "Map quota and upstream update failures to safe shared categories.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "out_of_scope_image_management_request",
        "description": "Playlist image listing, insertion, deletion, thumbnail replacement, and analytics are out of scope.",
        "arguments": {
            "part": "snippet",
            "body": {
                "id": "playlist-image-123",
                "snippet": {"playlistId": "PL123"},
                "thumbnailReplacement": True,
            },
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
)

PLAYLIST_IMAGES_DELETE_TOOL_NAME = "playlistImages_delete"
PLAYLIST_IMAGES_DELETE_QUOTA_COST = 50

PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

PLAYLIST_IMAGES_DELETE_DESCRIPTION = (
    "Delete a YouTube playlist image resource. Endpoint: playlistImages.delete. "
    "Quota cost: 50. Auth: oauth_required. Requires playlist image id; deletion is destructive."
)

PLAYLIST_IMAGES_DELETE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide id for the playlist image to delete.",
    "Quota cost: 50. playlistImages.delete accepts no request body and returns a 204 No Content acknowledgment.",
    "Quota cost: 50. Successful results expose only deletion acknowledgment and safe target context.",
)

PLAYLIST_IMAGES_DELETE_CAVEATS = (
    "Playlist image deletion requires eligible OAuth authorization for the target playlist image.",
    "Playlist image deletion is destructive and does not provide undo or deleted-resource recovery behavior.",
    "This tool accepts no request body, part selection, media upload, paging, or alternate selector inputs.",
    "Playlist image listing, insertion, update, media upload, thumbnail replacement, playlist management, analytics, ranking, summarization, and enrichment are out of scope.",
)

PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES = (
    {
        "name": "authorized_playlist_image_delete",
        "description": "Quota cost: 50. Delete one playlist image by id and receive a 204-style acknowledgment.",
        "arguments": {"id": "playlist-image-123"},
        "result": {
            "endpoint": "playlistImages.delete",
            "quotaCost": 50,
            "target": {"id": "playlist-image-123"},
            "deleted": True,
            "acknowledged": True,
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_id",
        "description": "Reject deletion requests that omit the required playlist image id.",
        "arguments": {},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_id",
        "description": "Reject deletion requests with a blank or non-string playlist image id.",
        "arguments": {"id": ""},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_body",
        "description": "Reject request body metadata because playlistImages.delete accepts no request body.",
        "arguments": {"id": "playlist-image-123", "body": {"snippet": {"playlistId": "PL123"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_media",
        "description": "Reject media inputs because playlistImages.delete performs no media upload.",
        "arguments": {"id": "playlist-image-123", "media": {"content": "<image content omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing or insufficient OAuth access to safe authentication or authorization errors.",
        "arguments": {"id": "playlist-image-123"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "quota_or_upstream_delete_failure",
        "description": "Map quota, missing-resource, and upstream deletion failures to safe shared categories.",
        "arguments": {"id": "playlist-image-123"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "out_of_scope_image_management_request",
        "description": "Thumbnail replacement, upload, playlist management, and analytics requests are out of scope.",
        "arguments": {"id": "playlist-image-123", "thumbnailReplacement": True},
        "errorCategory": "invalid_request",
    },
)


class PlaylistImagesListToolError(ValueError):
    """Represent a safe caller-facing ``playlistImages_list`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistImagesInsertToolError(ValueError):
    """Represent a safe caller-facing ``playlistImages_insert`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe insert tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistImagesUpdateToolError(ValueError):
    """Represent a safe caller-facing ``playlistImages_update`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe update tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class PlaylistImagesDeleteToolError(ValueError):
    """Represent a safe caller-facing ``playlistImages_delete`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe delete tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited playlist-image part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_playlist_images_parts(part: Any) -> str:
    """Validate and normalize the requested playlist-image parts.

    :param part: Candidate part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistImagesListToolError: If part is missing or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistImagesListToolError("playlistImages_list requires part", details={"field": "part"})
    parts = _split_parts(part)
    if not parts or len(set(parts)) != len(parts) or any(item not in PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS for item in parts):
        raise PlaylistImagesListToolError(
            "playlistImages_list part must use id, snippet, or both",
            details={"field": "part", "allowed": list(PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlist_images_insert_parts(part: Any) -> str:
    """Validate and normalize playlist-image insert part selection.

    :param part: Candidate insert part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistImagesInsertToolError: If part is missing or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistImagesInsertToolError("playlistImages_insert requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_IMAGES_INSERT_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert part must use id, snippet, or both",
            details={"field": "part", "allowed": list(PLAYLIST_IMAGES_INSERT_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def _validate_playlist_images_update_parts(part: Any) -> str:
    """Validate and normalize playlist-image update part selection.

    :param part: Candidate update part selection value.
    :return: Normalized comma-delimited part selection.
    :raises PlaylistImagesUpdateToolError: If part is missing or unsupported.
    """
    if not isinstance(part, str) or not part.strip():
        raise PlaylistImagesUpdateToolError("playlistImages_update requires part", details={"field": "part"})
    parts = _split_parts(part)
    if (
        not parts
        or len(set(parts)) != len(parts)
        or any(item not in PLAYLIST_IMAGES_UPDATE_SUPPORTED_PARTS for item in parts)
    ):
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update part must use id, snippet, or both",
            details={"field": "part", "allowed": list(PLAYLIST_IMAGES_UPDATE_SUPPORTED_PARTS)},
        )
    return ",".join(parts)


def validate_playlist_images_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistImages_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistImagesListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistImagesListToolError("playlistImages_list arguments must be an object")

    allowed = {"part", "playlistId", "id", "pageToken", "maxResults"}
    for field in arguments:
        if field not in allowed:
            raise PlaylistImagesListToolError(
                f"unsupported field for playlistImages_list: {field}",
                details={"field": field},
            )

    part = _validate_playlist_images_parts(arguments.get("part"))
    selected = [
        selector
        for selector in PLAYLIST_IMAGES_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise PlaylistImagesListToolError(
            "playlistImages_list requires exactly one selector: playlistId or id",
            details={"field": "selector", "allowed": list(PLAYLIST_IMAGES_LIST_SELECTORS)},
        )

    selector = selected[0]
    normalized: dict[str, Any] = {"part": part, selector: arguments[selector].strip()}

    page_token = arguments.get("pageToken")
    max_results = arguments.get("maxResults")
    if selector == "id" and (page_token is not None or max_results is not None):
        raise PlaylistImagesListToolError(
            "pageToken and maxResults are only supported with playlistId",
            details={"field": "paging"},
        )
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise PlaylistImagesListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise PlaylistImagesListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > PLAYLIST_IMAGES_LIST_MAX_RESULTS:
            raise PlaylistImagesListToolError(
                f"maxResults must be between 0 and {PLAYLIST_IMAGES_LIST_MAX_RESULTS}",
                details={"field": "maxResults", "minimum": 0, "maximum": PLAYLIST_IMAGES_LIST_MAX_RESULTS},
            )
        normalized["maxResults"] = max_results
    return normalized


def _validate_playlist_images_insert_body(body: Any) -> dict[str, Any]:
    """Validate playlist-image insert metadata.

    :param body: Candidate metadata body.
    :return: Metadata body accepted by the Layer 1 wrapper.
    :raises PlaylistImagesInsertToolError: If body is malformed.
    """
    if not isinstance(body, dict):
        raise PlaylistImagesInsertToolError("playlistImages_insert requires body metadata", details={"field": "body"})
    unsupported = sorted(set(body) - {"snippet"})
    if unsupported:
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert body supports only snippet metadata",
            details={"field": f"body.{unsupported[0]}"},
        )
    snippet = body.get("snippet")
    if not isinstance(snippet, dict) or not snippet:
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert requires body.snippet metadata",
            details={"field": "body.snippet"},
        )
    return body


def _validate_playlist_images_insert_media(media: Any) -> dict[str, Any]:
    """Validate playlist-image insert media upload input.

    :param media: Candidate media upload descriptor.
    :return: Media descriptor accepted by the Layer 1 wrapper.
    :raises PlaylistImagesInsertToolError: If media is malformed or unsupported.
    """
    if not isinstance(media, dict) or not media:
        raise PlaylistImagesInsertToolError("playlistImages_insert requires media", details={"field": "media"})
    unsupported = sorted(set(media) - {"mimeType", "content"})
    if unsupported:
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert media supports only mimeType and content",
            details={"field": "media.unsupported"},
        )
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert requires media.mimeType",
            details={"field": "media.mimeType"},
        )
    if mime_type.strip() not in PLAYLIST_IMAGES_ALLOWED_MIME_TYPES:
        raise PlaylistImagesInsertToolError(
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream",
            details={"field": "media.mimeType"},
        )
    content = media.get("content")
    if not isinstance(content, str) or not content:
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert requires media.content",
            details={"field": "media.content"},
        )
    return {"mimeType": mime_type.strip(), "content": content}


def validate_playlist_images_insert_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistImages_insert`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistImagesInsertToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistImagesInsertToolError("playlistImages_insert arguments must be an object")

    allowed = {"part", "body", "media"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise PlaylistImagesInsertToolError(
            f"unsupported field for playlistImages_insert: {unsupported[0]}",
            details={"field": unsupported[0]},
        )
    return {
        "part": _validate_playlist_images_insert_parts(arguments.get("part")),
        "body": _validate_playlist_images_insert_body(arguments.get("body")),
        "media": _validate_playlist_images_insert_media(arguments.get("media")),
    }


def _validate_playlist_images_update_body(body: Any) -> dict[str, Any]:
    """Validate playlist-image update target metadata.

    :param body: Candidate metadata body.
    :return: Metadata body accepted by the Layer 1 update wrapper.
    :raises PlaylistImagesUpdateToolError: If body is malformed.
    """
    if not isinstance(body, dict):
        raise PlaylistImagesUpdateToolError("playlistImages_update requires body metadata", details={"field": "body"})
    unsupported = sorted(set(body) - {"id", "snippet"})
    if unsupported:
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update body supports only id and snippet metadata",
            details={"field": f"body.{unsupported[0]}"},
        )
    image_id = body.get("id")
    if not isinstance(image_id, str) or not image_id.strip():
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires body.id",
            details={"field": "body.id"},
        )
    snippet = body.get("snippet")
    if not isinstance(snippet, dict) or not snippet:
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires body.snippet metadata",
            details={"field": "body.snippet"},
        )
    playlist_id = snippet.get("playlistId")
    if not isinstance(playlist_id, str) or not playlist_id.strip():
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires body.snippet.playlistId",
            details={"field": "body.snippet.playlistId"},
        )
    normalized = dict(body)
    normalized["id"] = image_id.strip()
    normalized["snippet"] = dict(snippet)
    normalized["snippet"]["playlistId"] = playlist_id.strip()
    return normalized


def _validate_playlist_images_update_media(media: Any) -> dict[str, Any]:
    """Validate playlist-image update media upload input.

    :param media: Candidate media upload descriptor.
    :return: Media descriptor accepted by the Layer 1 wrapper.
    :raises PlaylistImagesUpdateToolError: If media is malformed or unsupported.
    """
    if not isinstance(media, dict) or not media:
        raise PlaylistImagesUpdateToolError("playlistImages_update requires media", details={"field": "media"})
    unsupported = sorted(set(media) - {"mimeType", "content"})
    if unsupported:
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update media supports only mimeType and content",
            details={"field": "media.unsupported"},
        )
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires media.mimeType",
            details={"field": "media.mimeType"},
        )
    if mime_type.strip() not in PLAYLIST_IMAGES_ALLOWED_MIME_TYPES:
        raise PlaylistImagesUpdateToolError(
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream",
            details={"field": "media.mimeType"},
        )
    content = media.get("content")
    if not isinstance(content, str) or not content:
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires media.content",
            details={"field": "media.content"},
        )
    return {"mimeType": mime_type.strip(), "content": content}


def validate_playlist_images_update_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistImages_update`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistImagesUpdateToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistImagesUpdateToolError("playlistImages_update arguments must be an object")

    allowed = {"part", "body", "media"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise PlaylistImagesUpdateToolError(
            f"unsupported field for playlistImages_update: {unsupported[0]}",
            details={"field": unsupported[0]},
        )
    return {
        "part": _validate_playlist_images_update_parts(arguments.get("part")),
        "body": _validate_playlist_images_update_body(arguments.get("body")),
        "media": _validate_playlist_images_update_media(arguments.get("media")),
    }


def validate_playlist_images_delete_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``playlistImages_delete`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises PlaylistImagesDeleteToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise PlaylistImagesDeleteToolError("playlistImages_delete arguments must be an object")

    allowed = {"id"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise PlaylistImagesDeleteToolError(
            f"unsupported field for playlistImages_delete: {unsupported[0]}",
            details={"field": unsupported[0]},
        )

    image_id = arguments.get("id")
    if not isinstance(image_id, str) or not image_id.strip():
        raise PlaylistImagesDeleteToolError(
            "playlistImages_delete requires id",
            details={"field": "id"},
        )
    return {"id": image_id.strip()}


def map_playlist_images_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream playlist-image payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-image list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_playlist_images_list_arguments(arguments)
    selector = "playlistId" if "playlistId" in normalized else "id"
    result = {
        "endpoint": "playlistImages.list",
        "quotaCost": PLAYLIST_IMAGES_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": {"name": selector, "value": normalized[selector]},
        "auth": {"mode": "oauth_required"},
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


def _playlist_images_insert_body_context(body: dict[str, Any]) -> dict[str, Any]:
    """Build safe body context for a playlist-image insert result.

    :param body: Validated playlist-image metadata body.
    :return: Safe metadata summary for public result surfaces.
    """
    snippet = body.get("snippet") if isinstance(body.get("snippet"), dict) else {}
    context: dict[str, Any] = {"hasSnippet": bool(snippet)}
    playlist_id = snippet.get("playlistId") if isinstance(snippet, dict) else None
    if isinstance(playlist_id, str) and playlist_id:
        context["playlistId"] = playlist_id
    return context


def _playlist_images_insert_media_context(media: dict[str, Any]) -> dict[str, Any]:
    """Build safe media context for a playlist-image insert result.

    :param media: Validated media upload descriptor.
    :return: Safe media summary that omits raw upload content.
    """
    return {
        "mimeType": media["mimeType"],
        "contentProvided": bool(media.get("content")),
    }


def map_playlist_images_insert_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream insert payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-image insert payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw mutation result with safe operation context.
    """
    normalized = validate_playlist_images_insert_arguments(arguments)
    return {
        "endpoint": "playlistImages.insert",
        "quotaCost": PLAYLIST_IMAGES_INSERT_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "bodyContext": _playlist_images_insert_body_context(normalized["body"]),
        "mediaContext": _playlist_images_insert_media_context(normalized["media"]),
        "auth": {"mode": "oauth_required"},
        "item": payload,
    }


def _playlist_images_update_body_context(body: dict[str, Any]) -> dict[str, Any]:
    """Build safe body context for a playlist-image update result.

    :param body: Validated playlist-image update metadata body.
    :return: Safe target metadata summary for public result surfaces.
    """
    snippet = body.get("snippet") if isinstance(body.get("snippet"), dict) else {}
    context: dict[str, Any] = {
        "id": body["id"],
        "hasSnippet": bool(snippet),
    }
    playlist_id = snippet.get("playlistId") if isinstance(snippet, dict) else None
    if isinstance(playlist_id, str) and playlist_id:
        context["playlistId"] = playlist_id
    return context


def _playlist_images_update_media_context(media: dict[str, Any]) -> dict[str, Any]:
    """Build safe media context for a playlist-image update result.

    :param media: Validated media upload descriptor.
    :return: Safe media summary that omits raw upload content.
    """
    return {
        "mimeType": media["mimeType"],
        "contentProvided": bool(media.get("content")),
    }


def map_playlist_images_update_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream update payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-image update payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw mutation result with safe operation context.
    """
    normalized = validate_playlist_images_update_arguments(arguments)
    return {
        "endpoint": "playlistImages.update",
        "quotaCost": PLAYLIST_IMAGES_UPDATE_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "bodyContext": _playlist_images_update_body_context(normalized["body"]),
        "mediaContext": _playlist_images_update_media_context(normalized["media"]),
        "auth": {"mode": "oauth_required"},
        "item": payload,
    }


def _playlist_images_delete_target_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe target context for a playlist-image delete result.

    :param arguments: Validated playlist-image delete arguments.
    :return: Safe target summary for public result surfaces.
    """
    return {"id": arguments["id"]}


def map_playlist_images_delete_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream delete payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 playlist-image delete payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw deletion acknowledgment with safe target context.
    """
    normalized = validate_playlist_images_delete_arguments(arguments)
    result: dict[str, Any] = {
        "endpoint": "playlistImages.delete",
        "quotaCost": PLAYLIST_IMAGES_DELETE_QUOTA_COST,
        "target": _playlist_images_delete_target_context(normalized),
        "auth": {"mode": "oauth_required"},
        "deleted": bool(payload.get("isDeleted", True)),
        "acknowledged": True,
        "statusCode": 204,
        "sourceOperation": payload.get("sourceOperation", "playlistImages.delete"),
    }
    return result


def _map_playlist_images_list_upstream_error(error: NormalizedUpstreamError) -> PlaylistImagesListToolError:
    """Map a normalized upstream failure to a safe ``playlistImages_list`` error.

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
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistImagesListToolError(str(error), category=category, details=error.details)


def _map_playlist_images_insert_upstream_error(error: NormalizedUpstreamError) -> PlaylistImagesInsertToolError:
    """Map a normalized upstream failure to a safe ``playlistImages_insert`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe insert tool error with shared category and sanitized details.
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
        "media_eligibility": "invalid_request",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistImagesInsertToolError(str(error), category=category, details=error.details)


def _map_playlist_images_update_upstream_error(error: NormalizedUpstreamError) -> PlaylistImagesUpdateToolError:
    """Map a normalized upstream failure to a safe ``playlistImages_update`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe update tool error with shared category and sanitized details.
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
        "media_eligibility": "invalid_request",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return PlaylistImagesUpdateToolError(str(error), category=category, details=error.details)


def _map_playlist_images_delete_upstream_error(error: NormalizedUpstreamError) -> PlaylistImagesDeleteToolError:
    """Map a normalized upstream failure to a safe ``playlistImages_delete`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe delete tool error with shared category and sanitized details.
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
    return PlaylistImagesDeleteToolError(str(error), category=category, details=error.details)


def _playlist_images_list_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistImages_list``.

    :param oauth_token: OAuth token used for playlist-image retrieval.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistImagesListToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistImagesListToolError(
            "playlistImages_list requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def _playlist_images_insert_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistImages_insert``.

    :param oauth_token: OAuth token used for playlist-image insertion.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistImagesInsertToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistImagesInsertToolError(
            "playlistImages_insert requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def _playlist_images_update_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistImages_update``.

    :param oauth_token: OAuth token used for playlist-image updates.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistImagesUpdateToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistImagesUpdateToolError(
            "playlistImages_update requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def _playlist_images_delete_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``playlistImages_delete``.

    :param oauth_token: OAuth token used for playlist-image deletion.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises PlaylistImagesDeleteToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise PlaylistImagesDeleteToolError(
            "playlistImages_delete requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_playlist_images_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistImages_list``.

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
            "playlist_image_insertion",
            "playlist_image_update",
            "playlist_image_deletion",
            "media_upload",
            "thumbnail_replacement",
            "playlist_management",
            "playlist_item_expansion",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_IMAGES_LIST_TOOL_NAME,
        upstream_resource="playlistImages",
        upstream_method="list",
        operation_key="playlistImages.list",
        description=PLAYLIST_IMAGES_LIST_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_IMAGES_LIST_QUOTA_COST,
        resource_family="playlist_images",
        input_contract=PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS),
            "selectorFields": list(PLAYLIST_IMAGES_LIST_SELECTORS),
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
        usage_notes=PLAYLIST_IMAGES_LIST_USAGE_NOTES,
        caveats=PLAYLIST_IMAGES_LIST_CAVEATS,
    )


def build_playlist_images_insert_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistImages_insert``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "bodyContext",
            "mediaContext",
            "auth",
            "item",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet"),
        disallowed_behavior=(
            "playlist_image_listing",
            "playlist_image_update",
            "playlist_image_deletion",
            "thumbnail_replacement",
            "playlist_management",
            "playlist_item_expansion",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_IMAGES_INSERT_TOOL_NAME,
        upstream_resource="playlistImages",
        upstream_method="insert",
        operation_key="playlistImages.insert",
        description=PLAYLIST_IMAGES_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_IMAGES_INSERT_QUOTA_COST,
        resource_family="playlist_images",
        input_contract=PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "item",
            "requestedParts": list(PLAYLIST_IMAGES_INSERT_SUPPORTED_PARTS),
            "metadataContext": "bodyContext",
            "mediaResult": "safe_media_summary",
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
        usage_notes=PLAYLIST_IMAGES_INSERT_USAGE_NOTES,
        caveats=PLAYLIST_IMAGES_INSERT_CAVEATS,
    )


def build_playlist_images_update_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistImages_update``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "bodyContext",
            "mediaContext",
            "auth",
            "item",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet"),
        disallowed_behavior=(
            "playlist_image_listing",
            "playlist_image_insertion",
            "playlist_image_deletion",
            "thumbnail_replacement",
            "playlist_management",
            "playlist_item_expansion",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_IMAGES_UPDATE_TOOL_NAME,
        upstream_resource="playlistImages",
        upstream_method="update",
        operation_key="playlistImages.update",
        description=PLAYLIST_IMAGES_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_IMAGES_UPDATE_QUOTA_COST,
        resource_family="playlist_images",
        input_contract=PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "requestedParts": list(PLAYLIST_IMAGES_UPDATE_SUPPORTED_PARTS),
            "metadataContext": "bodyContext",
            "mediaResult": "safe_media_summary",
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
        usage_notes=PLAYLIST_IMAGES_UPDATE_USAGE_NOTES,
        caveats=PLAYLIST_IMAGES_UPDATE_CAVEATS,
    )


def build_playlist_images_delete_contract() -> YouTubeToolContract:
    """Build the public contract for ``playlistImages_delete``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "target",
            "auth",
            "deleted",
            "acknowledged",
            "statusCode",
            "sourceOperation",
        ),
        preserved_upstream_fields=("sourceOperation",),
        disallowed_behavior=(
            "playlist_image_listing",
            "playlist_image_insertion",
            "playlist_image_update",
            "media_upload",
            "thumbnail_replacement",
            "playlist_management",
            "playlist_item_expansion",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=PLAYLIST_IMAGES_DELETE_TOOL_NAME,
        upstream_resource="playlistImages",
        upstream_method="delete",
        operation_key="playlistImages.delete",
        description=PLAYLIST_IMAGES_DELETE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=PLAYLIST_IMAGES_DELETE_QUOTA_COST,
        resource_family="playlist_images",
        input_contract=PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "deletion_acknowledgment",
            "successStatus": 204,
            "bodyPolicy": "no_upstream_body",
            "targetFields": ["id"],
            "requiredFields": ["id"],
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
        usage_notes=PLAYLIST_IMAGES_DELETE_USAGE_NOTES,
        caveats=PLAYLIST_IMAGES_DELETE_CAVEATS,
    )


def _default_playlist_images_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-image calls.

    :return: Integration executor returning representative playlist-image data.
    """

    def transport(execution):
        """Return a representative playlist-image list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#playlistImageListResponse",
            "etag": "etag-playlist-images",
            "items": [
                {
                    "kind": "youtube#playlistImage",
                    "id": "playlist-image-123",
                    "snippet": {
                        "playlistId": execution.arguments.get("playlistId", "PL123"),
                        "type": "medium",
                    },
                }
            ],
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlist_images_insert_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-image insert calls.

    :return: Integration executor returning representative created playlist-image data.
    """

    def transport(execution):
        """Return a representative playlist-image insert response.

        :param execution: Request execution context.
        :return: Fake upstream created playlist-image response for local invocation.
        """
        snippet = execution.arguments.get("body", {}).get("snippet", {})
        return {
            "kind": "youtube#playlistImage",
            "etag": "etag-created-playlist-image",
            "id": "playlist-image-123",
            "snippet": {
                "playlistId": snippet.get("playlistId", "PL123"),
                "type": snippet.get("type", "medium"),
            },
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlist_images_update_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-image update calls.

    :return: Integration executor returning representative updated playlist-image data.
    """

    def transport(execution):
        """Return a representative playlist-image update response.

        :param execution: Request execution context.
        :return: Fake upstream updated playlist-image response for local invocation.
        """
        body = execution.arguments.get("body", {})
        snippet = body.get("snippet", {})
        return {
            "kind": "youtube#playlistImage",
            "etag": "etag-updated-playlist-image",
            "id": body.get("id", "playlist-image-123"),
            "snippet": {
                "playlistId": snippet.get("playlistId", "PL123"),
                "type": snippet.get("type", "medium"),
            },
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_playlist_images_delete_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default playlist-image delete calls.

    :return: Integration executor returning representative delete acknowledgment data.
    """

    def transport(execution):
        """Return a representative playlist-image delete response.

        :param execution: Request execution context.
        :return: Fake upstream deletion acknowledgment for local invocation.
        """
        return {
            "playlistImageId": execution.arguments.get("id", "playlist-image-123"),
            "isDeleted": True,
            "upstreamBodyState": "empty",
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_playlist_images_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistImages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps playlist-image requests.
    """
    selected_wrapper = wrapper or build_playlist_images_list_wrapper()
    selected_executor = executor or _default_playlist_images_list_executor()
    auth_context = _playlist_images_list_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistImages_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-image list result.
        :raises PlaylistImagesListToolError: If validation or execution fails.
        """
        normalized = validate_playlist_images_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_images_list_upstream_error(exc) from exc
        return map_playlist_images_list_result(payload, normalized)

    return handler


def build_playlist_images_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistImages_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps playlist-image insert requests.
    """
    selected_wrapper = wrapper or build_playlist_images_insert_wrapper()
    selected_executor = executor or _default_playlist_images_insert_executor()
    auth_context = _playlist_images_insert_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistImages_insert`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-image insert result.
        :raises PlaylistImagesInsertToolError: If validation or execution fails.
        """
        normalized = validate_playlist_images_insert_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_images_insert_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistImagesInsertToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistImages.insert"},
            ) from exc
        return map_playlist_images_insert_result(payload, normalized)

    return handler


def build_playlist_images_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistImages_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps playlist-image update requests.
    """
    selected_wrapper = wrapper or build_playlist_images_update_wrapper()
    selected_executor = executor or _default_playlist_images_update_executor()
    auth_context = _playlist_images_update_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistImages_update`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-image update result.
        :raises PlaylistImagesUpdateToolError: If validation or execution fails.
        """
        normalized = validate_playlist_images_update_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_images_update_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistImagesUpdateToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "playlistImages.update"},
            ) from exc
        return map_playlist_images_update_result(payload, normalized)

    return handler


def build_playlist_images_delete_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``playlistImages_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps playlist-image delete requests.
    """
    selected_wrapper = wrapper or build_playlist_images_delete_wrapper()
    selected_executor = executor or _default_playlist_images_delete_executor()
    auth_context = _playlist_images_delete_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``playlistImages_delete`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 playlist-image delete result.
        :raises PlaylistImagesDeleteToolError: If validation or execution fails.
        """
        normalized = validate_playlist_images_delete_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_playlist_images_delete_upstream_error(exc) from exc
        except ValueError as exc:
            raise PlaylistImagesDeleteToolError(
                str(exc),
                category="invalid_request",
                details={"field": "id"},
            ) from exc
        return map_playlist_images_delete_result(payload, normalized)

    return handler


def build_playlist_images_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistImages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_images_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_IMAGES_LIST_TOOL_NAME,
        "description": PLAYLIST_IMAGES_LIST_DESCRIPTION,
        "inputSchema": PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
        "handler": build_playlist_images_list_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_playlist_images_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistImages_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_images_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_IMAGES_INSERT_TOOL_NAME,
        "description": PLAYLIST_IMAGES_INSERT_DESCRIPTION,
        "inputSchema": PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA,
        "handler": build_playlist_images_insert_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_playlist_images_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistImages_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_images_update_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_IMAGES_UPDATE_TOOL_NAME,
        "description": PLAYLIST_IMAGES_UPDATE_DESCRIPTION,
        "inputSchema": PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA,
        "handler": build_playlist_images_update_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_playlist_images_delete_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``playlistImages_delete``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_playlist_images_delete_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES)
    return {
        "name": PLAYLIST_IMAGES_DELETE_TOOL_NAME,
        "description": PLAYLIST_IMAGES_DELETE_DESCRIPTION,
        "inputSchema": PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA,
        "handler": build_playlist_images_delete_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "PLAYLIST_IMAGES_ALLOWED_MIME_TYPES",
    "PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES",
    "PLAYLIST_IMAGES_DELETE_CAVEATS",
    "PLAYLIST_IMAGES_DELETE_DESCRIPTION",
    "PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA",
    "PLAYLIST_IMAGES_DELETE_QUOTA_COST",
    "PLAYLIST_IMAGES_DELETE_TOOL_NAME",
    "PLAYLIST_IMAGES_DELETE_USAGE_NOTES",
    "PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES",
    "PLAYLIST_IMAGES_INSERT_CAVEATS",
    "PLAYLIST_IMAGES_INSERT_DESCRIPTION",
    "PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA",
    "PLAYLIST_IMAGES_INSERT_QUOTA_COST",
    "PLAYLIST_IMAGES_INSERT_SUPPORTED_PARTS",
    "PLAYLIST_IMAGES_INSERT_TOOL_NAME",
    "PLAYLIST_IMAGES_INSERT_USAGE_NOTES",
    "PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES",
    "PLAYLIST_IMAGES_LIST_CAVEATS",
    "PLAYLIST_IMAGES_LIST_DESCRIPTION",
    "PLAYLIST_IMAGES_LIST_INPUT_SCHEMA",
    "PLAYLIST_IMAGES_LIST_MAX_RESULTS",
    "PLAYLIST_IMAGES_LIST_QUOTA_COST",
    "PLAYLIST_IMAGES_LIST_SELECTORS",
    "PLAYLIST_IMAGES_LIST_SUPPORTED_PARTS",
    "PLAYLIST_IMAGES_LIST_TOOL_NAME",
    "PLAYLIST_IMAGES_LIST_USAGE_NOTES",
    "PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES",
    "PLAYLIST_IMAGES_UPDATE_CAVEATS",
    "PLAYLIST_IMAGES_UPDATE_DESCRIPTION",
    "PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA",
    "PLAYLIST_IMAGES_UPDATE_QUOTA_COST",
    "PLAYLIST_IMAGES_UPDATE_SUPPORTED_PARTS",
    "PLAYLIST_IMAGES_UPDATE_TOOL_NAME",
    "PLAYLIST_IMAGES_UPDATE_USAGE_NOTES",
    "PlaylistImagesDeleteToolError",
    "PlaylistImagesInsertToolError",
    "PlaylistImagesListToolError",
    "PlaylistImagesUpdateToolError",
    "build_playlist_images_delete_contract",
    "build_playlist_images_delete_handler",
    "build_playlist_images_delete_tool_descriptor",
    "build_playlist_images_insert_contract",
    "build_playlist_images_insert_handler",
    "build_playlist_images_insert_tool_descriptor",
    "build_playlist_images_list_contract",
    "build_playlist_images_list_handler",
    "build_playlist_images_list_tool_descriptor",
    "build_playlist_images_update_contract",
    "build_playlist_images_update_handler",
    "build_playlist_images_update_tool_descriptor",
    "map_playlist_images_delete_result",
    "map_playlist_images_insert_result",
    "map_playlist_images_list_result",
    "map_playlist_images_update_result",
    "validate_playlist_images_delete_arguments",
    "validate_playlist_images_insert_arguments",
    "validate_playlist_images_list_arguments",
    "validate_playlist_images_update_arguments",
]
