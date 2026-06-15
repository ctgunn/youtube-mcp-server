"""Concrete Layer 2 tool support for the YouTube ``channelSections`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.channel_sections import (
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


CHANNEL_SECTIONS_INSERT_TOOL_NAME = "channelSections_insert"
CHANNEL_SECTIONS_INSERT_QUOTA_COST = 50
CHANNEL_SECTIONS_INSERT_SUPPORTED_PARTS = ("contentDetails", "id", "snippet")
CHANNEL_SECTIONS_INSERT_PLAYLIST_TYPES = ("singlePlaylist", "multiplePlaylists")
CHANNEL_SECTIONS_INSERT_CHANNEL_TYPES = ("multipleChannels",)
CHANNEL_SECTIONS_INSERT_TITLE_REQUIRED_TYPES = ("multipleChannels", "multiplePlaylists")
CHANNEL_SECTIONS_INSERT_MAX_REFERENCES = 50
CHANNEL_SECTIONS_UPDATE_TOOL_NAME = "channelSections_update"
CHANNEL_SECTIONS_UPDATE_QUOTA_COST = 50
CHANNEL_SECTIONS_UPDATE_SUPPORTED_PARTS = ("contentDetails", "id", "snippet")
CHANNEL_SECTIONS_UPDATE_PLAYLIST_TYPES = CHANNEL_SECTIONS_INSERT_PLAYLIST_TYPES
CHANNEL_SECTIONS_UPDATE_CHANNEL_TYPES = CHANNEL_SECTIONS_INSERT_CHANNEL_TYPES
CHANNEL_SECTIONS_UPDATE_TITLE_REQUIRED_TYPES = CHANNEL_SECTIONS_INSERT_TITLE_REQUIRED_TYPES
CHANNEL_SECTIONS_UPDATE_MAX_REFERENCES = CHANNEL_SECTIONS_INSERT_MAX_REFERENCES
CHANNEL_SECTIONS_DELETE_TOOL_NAME = "channelSections_delete"
CHANNEL_SECTIONS_DELETE_QUOTA_COST = 50

CHANNEL_SECTIONS_DELETE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CHANNEL_SECTIONS_DELETE_DESCRIPTION = (
    "Delete a YouTube channel section. Endpoint: channelSections.delete. "
    "Quota cost: 50. Auth: oauth_required. Requires id."
)
CHANNEL_SECTIONS_DELETE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide exactly one channel-section id.",
    "Quota cost: 50. This is a destructive delete operation that removes the target channel section.",
    "Quota cost: 50. onBehalfOfContentOwner is partner-only delegated context and requires eligible OAuth authorization.",
    "Quota cost: 50. Do not provide a request body; channelSections.delete accepts query parameters only.",
    "Quota cost: 50. Successful deletion may return an upstream channelSection body or a no request body acknowledgment depending on transport behavior.",
    "Quota cost: 50. This tool does not perform bulk deletion, section lookup, section sorting, layout repair, playlist deletion, playlist cleanup, undo, recovery, enrichment, or recommendation workflows.",
)
CHANNEL_SECTIONS_DELETE_CAVEATS = (
    "Channel-section deletion requires eligible OAuth authorization for channel layout operations.",
    "This destructive operation removes the target section and does not provide undo or recovery behavior.",
    "Partner delegated deletion uses onBehalfOfContentOwner and never exposes owner identifiers in public results or errors.",
    "Missing, already deleted, or inaccessible target sections are surfaced through shared missing-resource or authorization errors.",
    "This low-level tool does not look up, create, update, sort, repair, bulk delete, clean up playlists, enrich, or recommend channel sections.",
)
CHANNEL_SECTIONS_DELETE_CALLER_EXAMPLES = (
    {
        "name": "authorized_delete",
        "arguments": {"id": "section-123"},
        "result": {
            "endpoint": "channelSections.delete",
            "quotaCost": 50,
            "deleted": True,
            "delete": {"id": "section-123"},
            "bodyPolicy": "no_upstream_body",
        },
        "notes": "Quota cost: 50. Deletes one channel section with eligible OAuth authorization.",
    },
    {
        "name": "partner_context_delete",
        "arguments": {"id": "section-123", "onBehalfOfContentOwner": "content-owner-id"},
        "result": {
            "endpoint": "channelSections.delete",
            "quotaCost": 50,
            "deleted": True,
            "partnerContext": {"onBehalfOfContentOwner": True},
        },
        "notes": "Quota cost: 50. Partner deletion requires eligible OAuth authorization.",
    },
    {
        "name": "missing_id",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "id"},
        "notes": "Quota cost: 50. The channel-section id is required before deletion.",
    },
    {
        "name": "invalid_id",
        "arguments": {"id": ""},
        "error": {"category": "invalid_request", "field": "id"},
        "notes": "Quota cost: 50. Empty or malformed channel-section identifiers are rejected.",
    },
    {
        "name": "unsupported_option",
        "arguments": {"id": "section-123", "body": {"snippet": {"title": "No body allowed"}}},
        "error": {"category": "invalid_request", "field": "body"},
        "notes": "Quota cost: 50. Request bodies, bulk deletion, recovery, and layout repair options are unsupported.",
    },
    {
        "name": "missing_target_section",
        "arguments": {"id": "missing-section"},
        "error": {"category": "resource_not_found", "reason": "channelSectionNotFound"},
        "notes": "Quota cost: 50. Repeated deletion or missing target failures preserve the shared missing-resource signal.",
    },
    {
        "name": "missing_oauth",
        "arguments": {"id": "section-123"},
        "error": {"category": "authentication_failed", "field": "auth"},
        "notes": "Quota cost: 50. Channel-section deletion requires eligible OAuth authorization.",
    },
)

CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(CHANNEL_SECTIONS_INSERT_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["snippet"],
            "properties": {
                "snippet": {
                    "type": "object",
                    "required": ["type", "channelId"],
                    "properties": {
                        "type": {"type": "string", "minLength": 1},
                        "channelId": {"type": "string", "minLength": 1},
                        "title": {"type": "string", "minLength": 1},
                        "position": {"type": "integer", "minimum": 0},
                    },
                    "additionalProperties": False,
                },
                "contentDetails": {
                    "type": "object",
                    "properties": {
                        "playlists": {"type": "array", "items": {"type": "string", "minLength": 1}},
                        "channels": {"type": "array", "items": {"type": "string", "minLength": 1}},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
        "onBehalfOfContentOwnerChannel": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CHANNEL_SECTIONS_INSERT_DESCRIPTION = (
    "Create a YouTube channel section. Endpoint: channelSections.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires a channel-section body."
)
CHANNEL_SECTIONS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and a channel-section body.",
    "Quota cost: 50. Supported part values are contentDetails, id, and snippet.",
    "Quota cost: 50. The body requires body.snippet.type and body.snippet.channelId for the target channel.",
    "Quota cost: 50. Supported writable fields are body.snippet.type, body.snippet.channelId, body.snippet.title, body.snippet.position, body.contentDetails.playlists[], and body.contentDetails.channels[].",
    "Quota cost: 50. singlePlaylist requires exactly one playlist reference.",
    "Quota cost: 50. multiplePlaylists requires playlist references and a title.",
    "Quota cost: 50. multipleChannels requires channel references and a title.",
    "Quota cost: 50. onBehalfOfContentOwner and onBehalfOfContentOwnerChannel are partner-only delegated context fields and must be paired.",
    "Quota cost: 50. YouTube may reject creation when the target channel has reached the maximum channel-section capacity.",
    "Quota cost: 50. This tool does not call playlistItems.list, channels.update, playlist creation, video expansion, sorting, enrichment, or layout recommendation workflows.",
)
CHANNEL_SECTIONS_INSERT_CAVEATS = (
    "Channel-section creation requires eligible OAuth authorization for channel layout operations.",
    "Partner delegated creation is authorization-sensitive and requires both onBehalfOfContentOwner and onBehalfOfContentOwnerChannel.",
    "Section content rules depend on body.snippet.type: singlePlaylist, multiplePlaylists, and multipleChannels each accept different contentDetails fields.",
    "The upstream endpoint can reject requests when maximum channel-section behavior or referenced-resource availability prevents creation.",
    "This low-level tool does not sort, replace, reorder, update, delete, expand, enrich, or recommend channel sections.",
)
CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_playlist_section",
        "arguments": {
            "part": "snippet,contentDetails",
            "body": {
                "snippet": {"type": "singlePlaylist", "channelId": "UC123", "title": "Uploads", "position": 3},
                "contentDetails": {"playlists": ["PL123"]},
            },
        },
        "result": {
            "endpoint": "channelSections.insert",
            "quotaCost": 50,
            "created": True,
            "requestedParts": ["snippet", "contentDetails"],
            "item": {"id": "section-123"},
        },
        "notes": "Creates a single-playlist channel section for the authorized target channel.",
    },
    {
        "name": "authorized_channel_section",
        "arguments": {
            "part": "snippet,contentDetails",
            "body": {
                "snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related channels"},
                "contentDetails": {"channels": ["UC456", "UC789"]},
            },
        },
        "result": {"endpoint": "channelSections.insert", "quotaCost": 50, "created": True},
        "notes": "Creates a channel-backed section when channel references match the selected section type.",
    },
    {
        "name": "delegated_channel_section",
        "arguments": {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "onBehalfOfContentOwnerChannel": "UC123",
            "body": {"snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Network channels"}},
        },
        "result": {
            "endpoint": "channelSections.insert",
            "quotaCost": 50,
            "partnerContext": {"onBehalfOfContentOwner": True, "onBehalfOfContentOwnerChannel": True},
        },
        "notes": "Delegated creation requires eligible partner authorization and paired delegated owner/channel context.",
    },
    {
        "name": "missing_oauth",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
        },
        "error": {"category": "authentication_failed", "field": "auth"},
        "notes": "Channel-section creation requires eligible OAuth authorization.",
    },
    {
        "name": "missing_section_type",
        "arguments": {"part": "snippet", "body": {"snippet": {"channelId": "UC123"}}},
        "error": {"category": "invalid_request", "field": "body.snippet.type"},
        "notes": "body.snippet.type is required to determine content structure rules.",
    },
    {
        "name": "invalid_content_structure",
        "arguments": {
            "part": "contentDetails",
            "body": {
                "snippet": {"type": "multipleChannels", "channelId": "UC123", "title": "Related"},
                "contentDetails": {"playlists": ["PL123"]},
            },
        },
        "error": {"category": "invalid_request", "field": "body.contentDetails.playlists"},
        "notes": "Channel-backed sections cannot supply playlist references.",
    },
    {
        "name": "duplicate_references",
        "arguments": {
            "part": "contentDetails",
            "body": {
                "snippet": {"type": "multiplePlaylists", "channelId": "UC123", "title": "Featured"},
                "contentDetails": {"playlists": ["PL123", "PL123"]},
            },
        },
        "error": {"category": "invalid_request", "field": "body.contentDetails.playlists"},
        "notes": "Duplicate playlist or channel references are rejected before creation.",
    },
    {
        "name": "capacity_limit",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
        },
        "error": {"category": "invalid_request", "reason": "maximumChannelSections"},
        "notes": "The upstream endpoint can reject creation when the channel reaches the maximum section capacity.",
    },
    {
        "name": "unsupported_higher_level_workflow",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}},
            "playlistItems": {"list": True},
        },
        "error": {"category": "invalid_request", "field": "playlistItems"},
        "notes": "playlistItems.list expansion is outside this endpoint-backed create tool.",
    },
)

CHANNEL_SECTIONS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "minLength": 1, "enum": list(CHANNEL_SECTIONS_UPDATE_SUPPORTED_PARTS)},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "snippet": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {"type": "string", "minLength": 1},
                        "title": {"type": "string", "minLength": 1},
                        "position": {"type": "integer", "minimum": 0},
                    },
                    "additionalProperties": False,
                },
                "contentDetails": {
                    "type": "object",
                    "properties": {
                        "playlists": {"type": "array", "items": {"type": "string", "minLength": 1}},
                        "channels": {"type": "array", "items": {"type": "string", "minLength": 1}},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CHANNEL_SECTIONS_UPDATE_DESCRIPTION = (
    "Update a YouTube channel section. Endpoint: channelSections.update. "
    "Quota cost: 50. Auth: oauth_required. Requires body.id and snippet.type."
)
CHANNEL_SECTIONS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide part and a channel-section body with body.id.",
    "Quota cost: 50. Supported part values are contentDetails, id, and snippet.",
    "Quota cost: 50. The body requires body.id and body.snippet.type for the target existing section.",
    "Quota cost: 50. Supported writable fields are body.id, body.snippet.type, body.snippet.title, body.snippet.position, body.contentDetails.playlists[], and body.contentDetails.channels[].",
    "Quota cost: 50. singlePlaylist requires exactly one playlist reference.",
    "Quota cost: 50. multiplePlaylists requires playlist references and a title.",
    "Quota cost: 50. multipleChannels requires channel references and a title.",
    "Quota cost: 50. onBehalfOfContentOwner is optional partner-only delegated context.",
    "Quota cost: 50. This update is overwrite-sensitive: omitted writable fields in selected parts may be deleted by the upstream endpoint.",
    "Quota cost: 50. This tool does not call playlistItems.list, perform patch behavior, create sections, delete sections, sort layouts, expand videos, or orchestrate higher-level workflows.",
)
CHANNEL_SECTIONS_UPDATE_CAVEATS = (
    "Channel-section updates require eligible OAuth authorization for channel layout operations.",
    "The request must identify the target section with body.id; missing or non-editable target sections fail safely.",
    "Section content rules depend on body.snippet.type: singlePlaylist, multiplePlaylists, and multipleChannels each accept different contentDetails fields.",
    "Updates replace writable content for the selected parts; omitted fields may be deleted, so include fields that should remain.",
    "Partner delegated updates use onBehalfOfContentOwner only and never expose owner identifiers in public results or errors.",
    "This low-level tool does not patch partial resource fields, call playlistItems.list, expand playlists or videos, or recommend layouts.",
)
CHANNEL_SECTIONS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "authorized_title_position_update",
        "arguments": {
            "part": "snippet,contentDetails",
            "body": {
                "id": "section-123",
                "snippet": {"type": "singlePlaylist", "title": "Uploads", "position": 3},
                "contentDetails": {"playlists": ["PL123"]},
            },
        },
        "result": {
            "endpoint": "channelSections.update",
            "quotaCost": 50,
            "updated": True,
            "requestedParts": ["snippet", "contentDetails"],
            "item": {"id": "section-123"},
        },
        "notes": "Updates title and position for an existing section while preserving the target section identity.",
    },
    {
        "name": "authorized_playlist_section_update",
        "arguments": {
            "part": "snippet,contentDetails",
            "body": {
                "id": "section-123",
                "snippet": {"type": "singlePlaylist", "title": "Uploads"},
                "contentDetails": {"playlists": ["PL123"]},
            },
        },
        "result": {"endpoint": "channelSections.update", "quotaCost": 50, "updated": True},
        "notes": "Updates a single-playlist section with exactly one playlist reference.",
    },
    {
        "name": "authorized_channel_section_update",
        "arguments": {
            "part": "snippet,contentDetails",
            "body": {
                "id": "section-456",
                "snippet": {"type": "multipleChannels", "title": "Related channels"},
                "contentDetails": {"channels": ["UC456", "UC789"]},
            },
        },
        "result": {"endpoint": "channelSections.update", "quotaCost": 50, "updated": True},
        "notes": "Updates a channel-backed section when channel references match the section type.",
    },
    {
        "name": "partner_context_update",
        "arguments": {
            "part": "snippet",
            "onBehalfOfContentOwner": "content-owner-id",
            "body": {
                "id": "section-123",
                "snippet": {"type": "multipleChannels", "title": "Network channels"},
                "contentDetails": {"channels": ["UC456", "UC789"]},
            },
        },
        "result": {
            "endpoint": "channelSections.update",
            "quotaCost": 50,
            "partnerContext": {"onBehalfOfContentOwner": True},
        },
        "notes": "Delegated updates require eligible partner authorization without exposing owner identifiers.",
    },
    {
        "name": "missing_oauth",
        "arguments": {"part": "snippet", "body": {"id": "section-123", "snippet": {"type": "singlePlaylist"}}},
        "error": {"category": "authentication_failed", "field": "auth"},
        "notes": "Channel-section updates require eligible OAuth authorization.",
    },
    {
        "name": "missing_part",
        "arguments": {"body": {"id": "section-123", "snippet": {"type": "singlePlaylist"}}},
        "error": {"category": "invalid_request", "field": "part"},
        "notes": "part is required and must name supported writable resource parts.",
    },
    {
        "name": "missing_section_id",
        "arguments": {"part": "snippet", "body": {"snippet": {"type": "singlePlaylist"}}},
        "error": {"category": "invalid_request", "field": "body.id"},
        "notes": "body.id is required to identify the existing section.",
    },
    {
        "name": "missing_section_type",
        "arguments": {"part": "snippet", "body": {"id": "section-123", "snippet": {}}},
        "error": {"category": "invalid_request", "field": "body.snippet.type"},
        "notes": "body.snippet.type is required to determine content structure rules.",
    },
    {
        "name": "invalid_writable_field",
        "arguments": {
            "part": "snippet",
            "body": {"id": "section-123", "snippet": {"type": "singlePlaylist"}, "status": {}},
        },
        "error": {"category": "invalid_request", "field": "body.status"},
        "notes": "Read-only and unsupported body fields are rejected before update execution.",
    },
    {
        "name": "invalid_content_structure",
        "arguments": {
            "part": "contentDetails",
            "body": {
                "id": "section-123",
                "snippet": {"type": "multipleChannels", "title": "Related"},
                "contentDetails": {"playlists": ["PL123"]},
            },
        },
        "error": {"category": "invalid_request", "field": "body.contentDetails.playlists"},
        "notes": "Channel-backed sections cannot supply playlist references.",
    },
    {
        "name": "duplicate_references",
        "arguments": {
            "part": "contentDetails",
            "body": {
                "id": "section-123",
                "snippet": {"type": "multiplePlaylists", "title": "Featured"},
                "contentDetails": {"playlists": ["PL123", "PL123"]},
            },
        },
        "error": {"category": "invalid_request", "field": "body.contentDetails.playlists"},
        "notes": "Duplicate playlist or channel references are rejected before update execution.",
    },
    {
        "name": "missing_target_section",
        "arguments": {"part": "snippet", "body": {"id": "missing-section", "snippet": {"type": "singlePlaylist"}}},
        "error": {"category": "resource_not_found", "reason": "missingTargetSection"},
        "notes": "The upstream endpoint can reject updates when the target section is missing or not editable.",
    },
    {
        "name": "overwrite_sensitive_caveat",
        "arguments": {"part": "snippet", "body": {"id": "section-123", "snippet": {"type": "singlePlaylist"}}},
        "result": {"endpoint": "channelSections.update", "caveats": {"overwriteSensitive": True}},
        "notes": "Omitted writable fields in selected parts may be deleted; this is not patch behavior.",
    },
    {
        "name": "unsupported_higher_level_workflow",
        "arguments": {
            "part": "snippet",
            "body": {"id": "section-123", "snippet": {"type": "singlePlaylist"}},
            "patch": {"title": "Only update one field"},
        },
        "error": {"category": "invalid_request", "field": "patch"},
        "notes": "Patch orchestration belongs to a higher-level workflow, not this endpoint-backed update tool.",
    },
)

CHANNEL_SECTIONS_LIST_TOOL_NAME = "channelSections_list"
CHANNEL_SECTIONS_LIST_QUOTA_COST = 1
CHANNEL_SECTIONS_LIST_SELECTORS = ("channelId", "id", "mine")

CHANNEL_SECTIONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "hl": {"type": "string", "minLength": 1, "deprecated": True},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in CHANNEL_SECTIONS_LIST_SELECTORS],
    "additionalProperties": False,
}

CHANNEL_SECTIONS_LIST_DESCRIPTION = (
    "List YouTube channel sections. Endpoint: channelSections.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)
CHANNEL_SECTIONS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId or id for public channel-section lookup.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for the authenticated user's channel sections.",
    "Quota cost: 1. Valid lookups that match no channel sections return a successful empty item collection.",
    "Quota cost: 1. hl is deprecated for localized channel-section metadata in current official documentation.",
    "Quota cost: 1. onBehalfOfContentOwner is partner-scoped and requires eligible OAuth authorization when supported.",
    "Quota cost: 1. Continuation fields are preserved when returned, but pagination request controls are compatibility-only for this endpoint.",
)
CHANNEL_SECTIONS_LIST_CAVEATS = (
    "Exactly one selector is required: channelId, id, or mine.",
    "The hl localization parameter is deprecated in current official YouTube documentation.",
    "onBehalfOfContentOwner is intended only for eligible YouTube content partners and is not public API-key behavior.",
    "Pagination request fields are not a first-class official channelSections.list promise in this slice.",
    "This low-level tool does not expand playlist items, expand videos, rank sections, recommend layouts, or mutate channel sections.",
)
CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES = (
    {
        "name": "channel_id_lookup",
        "arguments": {"part": "snippet,contentDetails", "channelId": "UC123"},
        "result": {
            "endpoint": "channelSections.list",
            "quotaCost": 1,
            "selector": {"name": "channelId"},
            "requestedParts": ["snippet", "contentDetails"],
            "items": [{"id": "section-123"}],
        },
        "notes": "Lists channel sections for one public channel ID.",
    },
    {
        "name": "section_id_lookup",
        "arguments": {"part": "snippet", "id": "section-123"},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "selector": {"name": "id"}},
        "notes": "Looks up one or more channel sections by channel-section ID.",
    },
    {
        "name": "authorized_mine_lookup",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "selector": {"name": "mine"}},
        "notes": "Requires eligible OAuth authorization for the authenticated user's channel sections.",
    },
    {
        "name": "empty_result",
        "arguments": {"part": "snippet", "channelId": "UC-missing"},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "items": []},
        "notes": "A valid no-match lookup is a successful empty collection.",
    },
    {
        "name": "deprecated_hl_caveat",
        "arguments": {"part": "snippet", "channelId": "UC123", "hl": "es"},
        "result": {"endpoint": "channelSections.list", "caveats": {"hlDeprecated": True}},
        "notes": "hl is deprecated and remains visible as a compatibility caveat.",
    },
    {
        "name": "content_owner_partner_caveat",
        "arguments": {"part": "snippet", "channelId": "UC123", "onBehalfOfContentOwner": "content-owner-id"},
        "error": {"category": "invalid_request", "field": "onBehalfOfContentOwner"},
        "notes": "Content-owner context is partner-scoped and not public API-key behavior.",
    },
    {
        "name": "missing_selector",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Exactly one selector is required.",
    },
    {
        "name": "conflicting_selectors",
        "arguments": {"part": "snippet", "channelId": "UC123", "mine": True},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Selector combinations are rejected before endpoint execution.",
    },
    {
        "name": "authorization_sensitive_failure",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "selector": "mine"},
        "notes": "Owner-scoped lookup requires eligible OAuth authorization.",
    },
    {
        "name": "unsupported_higher_level_workflow",
        "arguments": {"part": "snippet", "channelId": "UC123", "expandVideos": True},
        "error": {"category": "invalid_request", "field": "expandVideos"},
        "notes": "Video expansion belongs to separate endpoint or Layer 3 workflows.",
    },
)


class ChannelSectionsListToolError(ValueError):
    """Represent a safe caller-facing ``channelSections_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-sections-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class ChannelSectionsInsertToolError(ValueError):
    """Represent a safe caller-facing ``channelSections_insert`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-sections-insert error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class ChannelSectionsUpdateToolError(ValueError):
    """Represent a safe caller-facing ``channelSections_update`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-sections-update error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class ChannelSectionsDeleteToolError(ValueError):
    """Represent a safe caller-facing ``channelSections_delete`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-sections-delete error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_channel_sections_insert_transport(execution) -> dict[str, Any]:
    """Return a safe created channel-section resource for local execution.

    :param execution: Layer 1 execution request containing validated arguments.
    :return: Upstream-shaped created channel-section resource.
    """
    arguments = getattr(execution, "arguments", {}) or {}
    body = arguments.get("body") if isinstance(arguments.get("body"), dict) else {}
    item: dict[str, Any] = {
        "kind": "youtube#channelSection",
        "etag": "local-channel-section",
        "id": body.get("id", "section-123"),
    }
    for field in ("snippet", "contentDetails"):
        if field in body:
            item[field] = body[field]
    return item


def _default_channel_sections_update_transport(execution) -> dict[str, Any]:
    """Return a safe updated channel-section resource for local execution.

    :param execution: Layer 1 execution request containing validated arguments.
    :return: Upstream-shaped updated channel-section resource.
    """
    return _default_channel_sections_insert_transport(execution)


def _default_channel_sections_delete_transport(_execution) -> dict[str, Any]:
    """Return a safe no-body delete acknowledgment for local execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped delete acknowledgment for ``channelSections_delete``.
    """
    return {}


def _default_insert_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelSections_insert``.

    :return: Executor with a safe local transport for created channel-section resources.
    """
    return IntegrationExecutor(
        transport=_default_channel_sections_insert_transport,
        retry_policy=RetryPolicy(max_attempts=1),
    )


def _default_update_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelSections_update``.

    :return: Executor with a safe local transport for updated channel-section resources.
    """
    return IntegrationExecutor(
        transport=_default_channel_sections_update_transport,
        retry_policy=RetryPolicy(max_attempts=1),
    )


def _default_delete_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelSections_delete``.

    :return: Executor with a safe local transport for deletion acknowledgments.
    """
    return IntegrationExecutor(
        transport=_default_channel_sections_delete_transport,
        retry_policy=RetryPolicy(max_attempts=1),
    )


def _default_channel_sections_transport(_execution) -> dict[str, Any]:
    """Return a safe empty channel-section collection for local execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped channel-section collection.
    """
    return {"items": []}


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelSections_list``.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_channel_sections_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_channel_sections_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelSections_list``.

    :return: Validated Layer 2 tool contract for ``channelSections_list``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_SECTIONS_LIST_TOOL_NAME,
        upstream_resource="channelSections",
        upstream_method="list",
        operation_key="channelSections.list",
        description=CHANNEL_SECTIONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=CHANNEL_SECTIONS_LIST_QUOTA_COST,
        resource_family="channel_sections",
        input_contract=CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "prevPageToken", "pageInfo"],
            "caveatFields": ["hlDeprecated", "contentOwnerPartnerScoped", "paginationCompatibilityOnly"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "selector", "requestedParts", "caveats"),
            preserved_upstream_fields=("items", "nextPageToken", "prevPageToken", "pageInfo", "requestedParts"),
            disallowed_behavior=(
                "channel_search",
                "section_ranking",
                "layout_recommendation",
                "video_expansion",
                "playlist_item_expansion",
                "channel_section_mutation",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=CHANNEL_SECTIONS_LIST_USAGE_NOTES,
        caveats=CHANNEL_SECTIONS_LIST_CAVEATS,
    )


def build_channel_sections_insert_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelSections_insert``.

    :return: Validated Layer 2 tool contract for ``channelSections_insert``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_SECTIONS_INSERT_TOOL_NAME,
        upstream_resource="channelSections",
        upstream_method="insert",
        operation_key="channelSections.insert",
        description=CHANNEL_SECTIONS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CHANNEL_SECTIONS_INSERT_QUOTA_COST,
        resource_family="channel_sections",
        input_contract=CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "created_resource",
            "resourcePath": "item",
            "supportedWritableParts": list(CHANNEL_SECTIONS_INSERT_SUPPORTED_PARTS),
            "writableBodyFields": [
                "body.snippet.type",
                "body.snippet.channelId",
                "body.snippet.title",
                "body.snippet.position",
                "body.contentDetails.playlists[]",
                "body.contentDetails.channels[]",
            ],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "created", "item", "requestedParts", "partnerContext"),
            preserved_upstream_fields=("kind", "etag", "id", "snippet", "contentDetails", "requestedParts"),
            disallowed_behavior=(
                "channel_section_update",
                "channel_section_delete",
                "playlist_item_insertion",
                "video_upload",
                "layout_recommendation",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=CHANNEL_SECTIONS_INSERT_USAGE_NOTES,
        caveats=CHANNEL_SECTIONS_INSERT_CAVEATS,
    )


def build_channel_sections_update_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelSections_update``.

    :return: Validated Layer 2 tool contract for ``channelSections_update``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_SECTIONS_UPDATE_TOOL_NAME,
        upstream_resource="channelSections",
        upstream_method="update",
        operation_key="channelSections.update",
        description=CHANNEL_SECTIONS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CHANNEL_SECTIONS_UPDATE_QUOTA_COST,
        resource_family="channel_sections",
        input_contract=CHANNEL_SECTIONS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "supportedWritableParts": list(CHANNEL_SECTIONS_UPDATE_SUPPORTED_PARTS),
            "writableBodyFields": [
                "body.id",
                "body.snippet.type",
                "body.snippet.title",
                "body.snippet.position",
                "body.contentDetails.playlists[]",
                "body.contentDetails.channels[]",
            ],
            "overwriteSensitive": True,
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "updated", "item", "requestedParts", "partnerContext"),
            preserved_upstream_fields=("kind", "etag", "id", "snippet", "contentDetails", "requestedParts"),
            disallowed_behavior=(
                "patch_update",
                "channel_section_creation",
                "channel_section_delete",
                "playlist_item_expansion",
                "video_expansion",
                "layout_recommendation",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=CHANNEL_SECTIONS_UPDATE_USAGE_NOTES,
        caveats=CHANNEL_SECTIONS_UPDATE_CAVEATS,
    )


def build_channel_sections_delete_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelSections_delete``.

    :return: Validated Layer 2 tool contract for ``channelSections_delete``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_SECTIONS_DELETE_TOOL_NAME,
        upstream_resource="channelSections",
        upstream_method="delete",
        operation_key="channelSections.delete",
        description=CHANNEL_SECTIONS_DELETE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CHANNEL_SECTIONS_DELETE_QUOTA_COST,
        resource_family="channel_sections",
        input_contract=CHANNEL_SECTIONS_DELETE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "deletion_acknowledgment",
            "successStatus": "204_or_upstream_body",
            "bodyPolicy": "preserve_returned_body_or_acknowledge_no_body",
            "targetField": "id",
            "mutation": "destructive_delete",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=(
                "endpoint",
                "quotaCost",
                "deleted",
                "delete",
                "partnerContext",
                "bodyPolicy",
                "upstream",
            ),
            preserved_upstream_fields=("kind", "etag", "id", "snippet", "contentDetails"),
            disallowed_behavior=(
                "channel_section_lookup",
                "channel_section_creation",
                "channel_section_update",
                "bulk_delete",
                "layout_repair",
                "playlist_deletion",
                "playlist_item_cleanup",
                "undo",
                "recovery",
                "enrichment",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
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
        usage_notes=CHANNEL_SECTIONS_DELETE_USAGE_NOTES,
        caveats=CHANNEL_SECTIONS_DELETE_CAVEATS,
    )


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active channel-section selectors from one request.

    :param arguments: Caller-supplied ``channelSections_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in CHANNEL_SECTIONS_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "mine":
            if value is True:
                active.append((selector, True))
        elif isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
    return active


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested channel-section part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _safe_caveat_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe caveat metadata that applies to one request.

    :param arguments: Caller-supplied ``channelSections_list`` arguments.
    :return: Safe caveat flags for public result surfaces.
    """
    caveats: dict[str, Any] = {}
    if "hl" in arguments:
        caveats["hlDeprecated"] = True
    if "onBehalfOfContentOwner" in arguments:
        caveats["contentOwnerPartnerScoped"] = True
    if "pageToken" in arguments or "maxResults" in arguments:
        caveats["paginationCompatibilityOnly"] = True
    return caveats


def map_channel_sections_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel-section response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw channel-section collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "channelSections.list",
        "quotaCost": CHANNEL_SECTIONS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
    }
    caveats = _safe_caveat_context(arguments)
    if caveats:
        result["caveats"] = caveats
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def _safe_insert_partner_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe partner-context flags for one insert request.

    :param arguments: Caller-supplied ``channelSections_insert`` arguments.
    :return: Safe partner-context flags without owner or channel identifiers.
    """
    context: dict[str, Any] = {}
    if "onBehalfOfContentOwner" in arguments:
        context["onBehalfOfContentOwner"] = True
    if "onBehalfOfContentOwnerChannel" in arguments:
        context["onBehalfOfContentOwnerChannel"] = True
    return context


def map_channel_sections_insert_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel-section insert response to the public result shape.

    :param response: Upstream-shaped created channel-section resource.
    :param arguments: Original validated tool arguments.
    :return: Near-raw created-resource result with light MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "channelSections.insert",
        "quotaCost": CHANNEL_SECTIONS_INSERT_QUOTA_COST,
        "created": True,
        "item": response,
        "requestedParts": _requested_parts(arguments),
    }
    partner_context = _safe_insert_partner_context(arguments)
    if partner_context:
        result["partnerContext"] = partner_context
    return result


def _safe_update_partner_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe partner-context flags for one update request.

    :param arguments: Caller-supplied ``channelSections_update`` arguments.
    :return: Safe partner-context flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_channel_sections_update_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel-section update response to the public result shape.

    :param response: Upstream-shaped updated channel-section resource.
    :param arguments: Original validated tool arguments.
    :return: Near-raw updated-resource result with light MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "channelSections.update",
        "quotaCost": CHANNEL_SECTIONS_UPDATE_QUOTA_COST,
        "updated": True,
        "item": response,
        "requestedParts": _requested_parts(arguments),
    }
    partner_context = _safe_update_partner_context(arguments)
    if partner_context:
        result["partnerContext"] = partner_context
    return result


def _safe_delete_partner_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe partner-context flags for one delete request.

    :param arguments: Caller-supplied ``channelSections_delete`` arguments.
    :return: Safe partner-context flags without owner identifiers.
    """
    if "onBehalfOfContentOwner" in arguments:
        return {"onBehalfOfContentOwner": True}
    return {}


def map_channel_sections_delete_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel-section delete response to the public result shape.

    :param response: Upstream-shaped deletion response or no-body acknowledgment.
    :param arguments: Original validated ``channelSections_delete`` arguments.
    :return: Near-raw deletion acknowledgment with safe operation context.
    """
    result: dict[str, Any] = {
        "endpoint": "channelSections.delete",
        "quotaCost": CHANNEL_SECTIONS_DELETE_QUOTA_COST,
        "deleted": True,
        "delete": {"id": str(arguments.get("id", "")).strip()},
    }
    partner_context = _safe_delete_partner_context(arguments)
    if partner_context:
        result["partnerContext"] = partner_context
    if response:
        result["upstream"] = response
    else:
        result["bodyPolicy"] = "no_upstream_body"
    return result


def _raise_insert_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``channelSections_insert`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field or content rule that failed validation.
    :param details: Additional safe diagnostic metadata.
    :raises ChannelSectionsInsertToolError: Always raised with a safe category.
    """
    safe_details = {"field": field}
    safe_details.update(details)
    raise ChannelSectionsInsertToolError(message, category="invalid_request", details=safe_details)


def _raise_update_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``channelSections_update`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field or content rule that failed validation.
    :param details: Additional safe diagnostic metadata.
    :raises ChannelSectionsUpdateToolError: Always raised with a safe category.
    """
    safe_details = {"field": field}
    safe_details.update(details)
    raise ChannelSectionsUpdateToolError(message, category="invalid_request", details=safe_details)


def _raise_delete_invalid(message: str, field: str, **details: Any) -> None:
    """Raise a safe invalid-request error for ``channelSections_delete`` validation.

    :param message: Caller-facing validation message.
    :param field: Request field that failed validation.
    :param details: Additional safe diagnostic metadata.
    :raises ChannelSectionsDeleteToolError: Always raised with a safe category.
    """
    safe_details = {"field": field}
    safe_details.update(details)
    raise ChannelSectionsDeleteToolError(message, category="invalid_request", details=safe_details)


def _nonempty_text(value: Any) -> bool:
    """Return whether a value is a non-empty string after trimming.

    :param value: Value to inspect.
    :return: ``True`` when the value is a non-empty string.
    """
    return isinstance(value, str) and bool(value.strip())


def _validate_insert_parts(arguments: dict[str, Any]) -> None:
    """Validate requested insert parts against the supported part set.

    :param arguments: Caller-supplied ``channelSections_insert`` arguments.
    :raises ChannelSectionsInsertToolError: If the part selection is missing or unsupported.
    """
    parts = _requested_parts(arguments)
    if not parts:
        _raise_insert_invalid("channelSections_insert requires part.", "part")
    unsupported = [part for part in parts if part not in CHANNEL_SECTIONS_INSERT_SUPPORTED_PARTS]
    if unsupported:
        _raise_insert_invalid("channelSections_insert received an unsupported part.", "part")


def _insert_body(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section insert body after top-level shape checks.

    :param arguments: Caller-supplied ``channelSections_insert`` arguments.
    :return: Validated body mapping.
    :raises ChannelSectionsInsertToolError: If body is missing or malformed.
    """
    body = arguments.get("body")
    if not isinstance(body, dict):
        _raise_insert_invalid("channelSections_insert requires a body object.", "body")
    unsupported = [field for field in body if field not in {"snippet", "contentDetails"}]
    if unsupported:
        _raise_insert_invalid("channelSections_insert body contains an unsupported field.", f"body.{unsupported[0]}")
    return body


def _insert_snippet(body: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section snippet after writable-field validation.

    :param body: Validated insert body mapping.
    :return: Validated snippet mapping.
    :raises ChannelSectionsInsertToolError: If snippet fields are missing or unsupported.
    """
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        _raise_insert_invalid("channelSections_insert requires body.snippet.", "body.snippet")
    unsupported = [field for field in snippet if field not in {"type", "channelId", "title", "position"}]
    if unsupported:
        _raise_insert_invalid(
            "channelSections_insert body.snippet contains an unsupported field.",
            f"body.snippet.{unsupported[0]}",
        )
    if not _nonempty_text(snippet.get("type")):
        _raise_insert_invalid("channelSections_insert requires body.snippet.type.", "body.snippet.type")
    if not _nonempty_text(snippet.get("channelId")):
        _raise_insert_invalid("channelSections_insert requires body.snippet.channelId.", "body.snippet.channelId")
    position = snippet.get("position")
    if position is not None and (not isinstance(position, int) or position < 0):
        _raise_insert_invalid("channelSections_insert position must be a non-negative integer.", "body.snippet.position")
    return snippet


def _insert_content_details(body: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section contentDetails mapping after shape checks.

    :param body: Validated insert body mapping.
    :return: Content details mapping or an empty mapping.
    :raises ChannelSectionsInsertToolError: If contentDetails is malformed.
    """
    content_details = body.get("contentDetails", {})
    if content_details is None:
        return {}
    if not isinstance(content_details, dict):
        _raise_insert_invalid("channelSections_insert contentDetails must be an object.", "body.contentDetails")
    unsupported = [field for field in content_details if field not in {"playlists", "channels"}]
    if unsupported:
        _raise_insert_invalid(
            "channelSections_insert body.contentDetails contains an unsupported field.",
            f"body.contentDetails.{unsupported[0]}",
        )
    return content_details


def _reference_values(content_details: dict[str, Any], field: str) -> list[str]:
    """Return validated channel-section reference identifiers.

    :param content_details: Request ``contentDetails`` mapping.
    :param field: Reference field, such as ``playlists`` or ``channels``.
    :return: Trimmed reference identifiers.
    :raises ChannelSectionsInsertToolError: If references are missing, malformed, duplicated, or too many.
    """
    raw_values = content_details.get(field)
    details_field = f"body.contentDetails.{field}"
    if not isinstance(raw_values, list) or not raw_values:
        _raise_insert_invalid("channelSections_insert requires content references.", details_field)
    values: list[str] = []
    for value in raw_values:
        if not _nonempty_text(value):
            _raise_insert_invalid("channelSections_insert references must be non-empty strings.", details_field)
        values.append(value.strip())
    if len(values) != len(set(values)):
        _raise_insert_invalid(
            "channelSections_insert does not support duplicate references.",
            details_field,
            reason="duplicateReferences",
        )
    if len(values) > CHANNEL_SECTIONS_INSERT_MAX_REFERENCES:
        _raise_insert_invalid(
            "channelSections_insert received too many references.",
            details_field,
            reason="tooManyReferences",
        )
    return values


def _validate_insert_content_rules(snippet: dict[str, Any], content_details: dict[str, Any]) -> None:
    """Validate section-type-specific channel-section content rules.

    :param snippet: Validated body snippet mapping.
    :param content_details: Validated contentDetails mapping.
    :raises ChannelSectionsInsertToolError: If content rules are not satisfied.
    """
    section_type = str(snippet["type"]).strip()
    if section_type in CHANNEL_SECTIONS_INSERT_TITLE_REQUIRED_TYPES and not _nonempty_text(snippet.get("title")):
        _raise_insert_invalid("channelSections_insert requires title for this section type.", "body.snippet.title")

    if section_type in CHANNEL_SECTIONS_INSERT_PLAYLIST_TYPES:
        if content_details.get("channels") not in (None, [], ()):
            _raise_insert_invalid(
                "channelSections_insert playlist-backed sections cannot include channels.",
                "body.contentDetails.channels",
            )
        playlists = _reference_values(content_details, "playlists")
        if section_type == "singlePlaylist" and len(playlists) != 1:
            _raise_insert_invalid(
                "channelSections_insert singlePlaylist requires exactly one playlist.",
                "body.contentDetails.playlists",
            )
        return

    if section_type in CHANNEL_SECTIONS_INSERT_CHANNEL_TYPES:
        if content_details.get("playlists") not in (None, [], ()):
            _raise_insert_invalid(
                "channelSections_insert channel-backed sections cannot include playlists.",
                "body.contentDetails.playlists",
            )
        _reference_values(content_details, "channels")
        return

    if content_details.get("playlists") not in (None, [], ()):
        _raise_insert_invalid(
            "channelSections_insert section type does not accept playlists.",
            "body.contentDetails.playlists",
        )
    if content_details.get("channels") not in (None, [], ()):
        _raise_insert_invalid(
            "channelSections_insert section type does not accept channels.",
            "body.contentDetails.channels",
        )


def _validate_insert_partner_context(arguments: dict[str, Any]) -> None:
    """Validate delegated owner/channel context without exposing identifiers.

    :param arguments: Caller-supplied ``channelSections_insert`` arguments.
    :raises ChannelSectionsInsertToolError: If partner context is empty or unpaired.
    """
    owner_present = "onBehalfOfContentOwner" in arguments
    channel_present = "onBehalfOfContentOwnerChannel" in arguments
    for field in ("onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"):
        if field in arguments and not _nonempty_text(arguments[field]):
            _raise_insert_invalid(f"channelSections_insert requires a non-empty {field}.", field)
    if owner_present and not channel_present:
        _raise_insert_invalid(
            "channelSections_insert delegated owner context requires delegated channel context.",
            "onBehalfOfContentOwnerChannel",
            partnerScoped=True,
        )
    if channel_present and not owner_present:
        _raise_insert_invalid(
            "channelSections_insert delegated channel context requires delegated owner context.",
            "onBehalfOfContentOwner",
            partnerScoped=True,
        )


def validate_channel_sections_insert_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> None:
    """Validate foundational ``channelSections_insert`` arguments.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: OAuth token availability for channel-section creation.
    :raises ChannelSectionsInsertToolError: If required foundational fields are invalid.
    """
    supported_fields = set(CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelSectionsInsertToolError(
                f"channelSections_insert does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if not oauth_token:
        raise ChannelSectionsInsertToolError(
            "channelSections_insert requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    _validate_insert_partner_context(arguments)
    _validate_insert_parts(arguments)
    body = _insert_body(arguments)
    snippet = _insert_snippet(body)
    content_details = _insert_content_details(body)
    _validate_insert_content_rules(snippet, content_details)


def _insert_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``channelSections_insert``.

    :param oauth_token: OAuth token available for the write request.
    :return: Auth context suitable for the Layer 1 insert wrapper.
    :raises ChannelSectionsInsertToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise ChannelSectionsInsertToolError(
            "channelSections_insert requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _map_insert_upstream_error(error: NormalizedUpstreamError) -> ChannelSectionsInsertToolError:
    """Map a normalized upstream insert error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelSections_insert`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "forbidden": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "rate_limited": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    messages = {
        "invalid_request": "channelSections_insert request was rejected by the upstream endpoint.",
        "authorization_failed": "channelSections_insert was not authorized by the upstream endpoint.",
        "quota_exhausted": "channelSections_insert quota was exhausted by the upstream endpoint.",
        "resource_not_found": "channelSections_insert target was not found by the upstream endpoint.",
        "endpoint_unavailable": "channelSections_insert upstream endpoint is temporarily unavailable.",
        "upstream_failure": "channelSections_insert upstream execution failed.",
    }
    category = categories.get(error.category, "upstream_failure")
    return ChannelSectionsInsertToolError(
        messages[category],
        category=category,
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def _validate_update_parts(arguments: dict[str, Any]) -> None:
    """Validate requested update parts against the supported part set.

    :param arguments: Caller-supplied ``channelSections_update`` arguments.
    :raises ChannelSectionsUpdateToolError: If the part selection is missing or unsupported.
    """
    parts = _requested_parts(arguments)
    if not parts:
        _raise_update_invalid("channelSections_update requires part.", "part")
    unsupported = [part for part in parts if part not in CHANNEL_SECTIONS_UPDATE_SUPPORTED_PARTS]
    if unsupported:
        _raise_update_invalid("channelSections_update received an unsupported part.", "part")


def _update_body(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section update body after top-level shape checks.

    :param arguments: Caller-supplied ``channelSections_update`` arguments.
    :return: Validated body mapping.
    :raises ChannelSectionsUpdateToolError: If body is missing or malformed.
    """
    body = arguments.get("body")
    if not isinstance(body, dict):
        _raise_update_invalid("channelSections_update requires a body object.", "body")
    unsupported = [field for field in body if field not in {"id", "snippet", "contentDetails"}]
    if unsupported:
        _raise_update_invalid("channelSections_update body contains an unsupported field.", f"body.{unsupported[0]}")
    if not _nonempty_text(body.get("id")):
        _raise_update_invalid("channelSections_update requires body.id.", "body.id")
    return body


def _update_snippet(body: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section update snippet after writable-field validation.

    :param body: Validated update body mapping.
    :return: Validated snippet mapping.
    :raises ChannelSectionsUpdateToolError: If snippet fields are missing or unsupported.
    """
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        _raise_update_invalid("channelSections_update requires body.snippet.", "body.snippet")
    unsupported = [field for field in snippet if field not in {"type", "title", "position"}]
    if unsupported:
        _raise_update_invalid(
            "channelSections_update body.snippet contains an unsupported field.",
            f"body.snippet.{unsupported[0]}",
        )
    if not _nonempty_text(snippet.get("type")):
        _raise_update_invalid("channelSections_update requires body.snippet.type.", "body.snippet.type")
    position = snippet.get("position")
    if position is not None and (not isinstance(position, int) or position < 0):
        _raise_update_invalid("channelSections_update position must be a non-negative integer.", "body.snippet.position")
    return snippet


def _update_content_details(body: dict[str, Any]) -> dict[str, Any]:
    """Return the channel-section update contentDetails mapping after shape checks.

    :param body: Validated update body mapping.
    :return: Content details mapping or an empty mapping.
    :raises ChannelSectionsUpdateToolError: If contentDetails is malformed.
    """
    content_details = body.get("contentDetails", {})
    if content_details is None:
        return {}
    if not isinstance(content_details, dict):
        _raise_update_invalid("channelSections_update contentDetails must be an object.", "body.contentDetails")
    unsupported = [field for field in content_details if field not in {"playlists", "channels"}]
    if unsupported:
        _raise_update_invalid(
            "channelSections_update body.contentDetails contains an unsupported field.",
            f"body.contentDetails.{unsupported[0]}",
        )
    return content_details


def _update_reference_values(content_details: dict[str, Any], field: str) -> list[str]:
    """Return validated channel-section update reference identifiers.

    :param content_details: Request ``contentDetails`` mapping.
    :param field: Reference field, such as ``playlists`` or ``channels``.
    :return: Trimmed reference identifiers.
    :raises ChannelSectionsUpdateToolError: If references are missing, malformed, duplicated, or too many.
    """
    raw_values = content_details.get(field)
    details_field = f"body.contentDetails.{field}"
    if not isinstance(raw_values, list) or not raw_values:
        _raise_update_invalid("channelSections_update requires content references.", details_field)
    values: list[str] = []
    for value in raw_values:
        if not _nonempty_text(value):
            _raise_update_invalid("channelSections_update references must be non-empty strings.", details_field)
        values.append(value.strip())
    if len(values) != len(set(values)):
        _raise_update_invalid(
            "channelSections_update does not support duplicate references.",
            details_field,
            reason="duplicateReferences",
        )
    if len(values) > CHANNEL_SECTIONS_UPDATE_MAX_REFERENCES:
        _raise_update_invalid(
            "channelSections_update received too many references.",
            details_field,
            reason="tooManyReferences",
        )
    return values


def _validate_update_content_rules(snippet: dict[str, Any], content_details: dict[str, Any]) -> None:
    """Validate section-type-specific channel-section update content rules.

    :param snippet: Validated body snippet mapping.
    :param content_details: Validated contentDetails mapping.
    :raises ChannelSectionsUpdateToolError: If content rules are not satisfied.
    """
    section_type = str(snippet["type"]).strip()
    if section_type in CHANNEL_SECTIONS_UPDATE_TITLE_REQUIRED_TYPES and not _nonempty_text(snippet.get("title")):
        _raise_update_invalid("channelSections_update requires title for this section type.", "body.snippet.title")

    if section_type in CHANNEL_SECTIONS_UPDATE_PLAYLIST_TYPES:
        if content_details.get("channels") not in (None, [], ()):
            _raise_update_invalid(
                "channelSections_update playlist-backed sections cannot include channels.",
                "body.contentDetails.channels",
            )
        playlists = _update_reference_values(content_details, "playlists")
        if section_type == "singlePlaylist" and len(playlists) != 1:
            _raise_update_invalid(
                "channelSections_update singlePlaylist requires exactly one playlist.",
                "body.contentDetails.playlists",
            )
        return

    if section_type in CHANNEL_SECTIONS_UPDATE_CHANNEL_TYPES:
        if content_details.get("playlists") not in (None, [], ()):
            _raise_update_invalid(
                "channelSections_update channel-backed sections cannot include playlists.",
                "body.contentDetails.playlists",
            )
        _update_reference_values(content_details, "channels")
        return

    if content_details.get("playlists") not in (None, [], ()):
        _raise_update_invalid(
            "channelSections_update section type does not accept playlists.",
            "body.contentDetails.playlists",
        )
    if content_details.get("channels") not in (None, [], ()):
        _raise_update_invalid(
            "channelSections_update section type does not accept channels.",
            "body.contentDetails.channels",
        )


def _validate_update_partner_context(arguments: dict[str, Any]) -> None:
    """Validate delegated owner context without exposing identifiers.

    :param arguments: Caller-supplied ``channelSections_update`` arguments.
    :raises ChannelSectionsUpdateToolError: If partner context is empty.
    """
    if "onBehalfOfContentOwner" in arguments and not _nonempty_text(arguments["onBehalfOfContentOwner"]):
        _raise_update_invalid(
            "channelSections_update requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
            partnerScoped=True,
        )


def validate_channel_sections_update_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> None:
    """Validate foundational ``channelSections_update`` arguments.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: OAuth token availability for channel-section updates.
    :raises ChannelSectionsUpdateToolError: If required foundational fields are invalid.
    """
    supported_fields = set(CHANNEL_SECTIONS_UPDATE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelSectionsUpdateToolError(
                f"channelSections_update does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if not oauth_token:
        raise ChannelSectionsUpdateToolError(
            "channelSections_update requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    _validate_update_partner_context(arguments)
    _validate_update_parts(arguments)
    body = _update_body(arguments)
    snippet = _update_snippet(body)
    content_details = _update_content_details(body)
    _validate_update_content_rules(snippet, content_details)


def _update_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``channelSections_update``.

    :param oauth_token: OAuth token available for the write request.
    :return: Auth context suitable for the Layer 1 update wrapper.
    :raises ChannelSectionsUpdateToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise ChannelSectionsUpdateToolError(
            "channelSections_update requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _map_update_upstream_error(error: NormalizedUpstreamError) -> ChannelSectionsUpdateToolError:
    """Map a normalized upstream update error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelSections_update`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "forbidden": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "rate_limited": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    messages = {
        "invalid_request": "channelSections_update request was rejected by the upstream endpoint.",
        "authorization_failed": "channelSections_update was not authorized by the upstream endpoint.",
        "quota_exhausted": "channelSections_update quota was exhausted by the upstream endpoint.",
        "resource_not_found": "channelSections_update target was not found by the upstream endpoint.",
        "endpoint_unavailable": "channelSections_update upstream endpoint is temporarily unavailable.",
        "upstream_failure": "channelSections_update upstream execution failed.",
    }
    category = categories.get(error.category, "upstream_failure")
    return ChannelSectionsUpdateToolError(
        messages[category],
        category=category,
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def validate_channel_sections_delete_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> None:
    """Validate foundational ``channelSections_delete`` arguments.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: OAuth token availability for channel-section deletion.
    :raises ChannelSectionsDeleteToolError: If required delete fields are invalid.
    """
    supported_fields = set(CHANNEL_SECTIONS_DELETE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelSectionsDeleteToolError(
                f"channelSections_delete does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if not oauth_token:
        raise ChannelSectionsDeleteToolError(
            "channelSections_delete requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    if not _nonempty_text(arguments.get("id")):
        _raise_delete_invalid("channelSections_delete requires id.", "id")
    if "onBehalfOfContentOwner" in arguments and not _nonempty_text(arguments["onBehalfOfContentOwner"]):
        _raise_delete_invalid(
            "channelSections_delete requires a non-empty onBehalfOfContentOwner.",
            "onBehalfOfContentOwner",
            partnerScoped=True,
        )


def _delete_auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``channelSections_delete``.

    :param oauth_token: OAuth token available for the destructive delete request.
    :return: Auth context suitable for the Layer 1 delete wrapper.
    :raises ChannelSectionsDeleteToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise ChannelSectionsDeleteToolError(
            "channelSections_delete requires eligible user authorization.",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _map_delete_upstream_error(error: NormalizedUpstreamError) -> ChannelSectionsDeleteToolError:
    """Map a normalized upstream delete error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelSections_delete`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "forbidden": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "rate_limited": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_unavailable": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
        "deprecated_endpoint": "deprecated_endpoint",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    messages = {
        "invalid_request": "channelSections_delete request was rejected by the upstream endpoint.",
        "authorization_failed": "channelSections_delete was not authorized by the upstream endpoint.",
        "quota_exhausted": "channelSections_delete quota was exhausted by the upstream endpoint.",
        "resource_not_found": "channelSections_delete target was not found by the upstream endpoint.",
        "deprecated_endpoint": "channelSections_delete upstream endpoint is deprecated.",
        "endpoint_unavailable": "channelSections_delete upstream endpoint is temporarily unavailable.",
        "upstream_failure": "channelSections_delete upstream execution failed.",
    }
    category = categories.get(error.category, "upstream_failure")
    return ChannelSectionsDeleteToolError(
        messages[category],
        category=category,
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def validate_channel_sections_list_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> tuple[str, Any]:
    """Validate ``channelSections_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for owner-scoped lookup.
    :return: Selected selector name and safe value.
    :raises ChannelSectionsListToolError: If arguments are invalid or require missing authorization.
    """
    supported_fields = set(CHANNEL_SECTIONS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelSectionsListToolError(
                f"channelSections_list does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise ChannelSectionsListToolError(
            "channelSections_list requires part.",
            category="invalid_request",
            details={"field": "part"},
        )

    for field in ("hl", "onBehalfOfContentOwner"):
        if field in arguments and (not isinstance(arguments[field], str) or not arguments[field].strip()):
            raise ChannelSectionsListToolError(
                f"channelSections_list requires a non-empty {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if "onBehalfOfContentOwner" in arguments:
        raise ChannelSectionsListToolError(
            "channelSections_list does not support content-owner delegation in this slice.",
            category="invalid_request",
            details={"field": "onBehalfOfContentOwner", "partnerScoped": True},
        )

    provided_selectors: list[str] = []
    for selector in CHANNEL_SECTIONS_LIST_SELECTORS:
        if selector not in arguments:
            continue

        value = arguments[selector]
        if selector == "mine":
            if value is not True:
                raise ChannelSectionsListToolError(
                    "channelSections_list mine selector must be true when present.",
                    category="invalid_request",
                    details={"field": "mine"},
                )
        elif not isinstance(value, str) or not value.strip():
            raise ChannelSectionsListToolError(
                f"channelSections_list requires a non-empty {selector}.",
                category="invalid_request",
                details={"field": selector},
            )
        provided_selectors.append(selector)

    active = _active_selectors(arguments)
    if len(provided_selectors) != 1 or len(active) != 1:
        raise ChannelSectionsListToolError(
            "channelSections_list requires exactly one selector: channelId, id, or mine.",
            category="invalid_request",
            details={"field": "selector", "selectors": provided_selectors},
        )

    selector, value = active[0]
    if selector == "mine" and not oauth_token:
        raise ChannelSectionsListToolError(
            "mine requires eligible user authorization.",
            category="authentication_failed",
            details={"selector": selector},
        )
    return selector, value


def _auth_context_for_selector(
    selector: str,
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for a channel-section selector.

    :param selector: Selected channel-section selector.
    :param api_key: API key value available for public selector access.
    :param oauth_token: OAuth token available for owner-scoped lookup.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises ChannelSectionsListToolError: If required credentials are unavailable.
    """
    if selector in {"channelId", "id"}:
        if not api_key:
            raise ChannelSectionsListToolError(
                f"{selector} requires public API-key access.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))

    if selector == "mine":
        if not oauth_token:
            raise ChannelSectionsListToolError(
                "mine requires eligible user authorization.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))

    raise ChannelSectionsListToolError(
        "channelSections_list requires a supported selector.",
        category="invalid_request",
        details={"field": "selector"},
    )


def _map_upstream_error(error: NormalizedUpstreamError) -> ChannelSectionsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelSections_list`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "forbidden": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "rate_limited": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    messages = {
        "invalid_request": "channelSections_list request was rejected by the upstream endpoint.",
        "authorization_failed": "channelSections_list was not authorized by the upstream endpoint.",
        "quota_exhausted": "channelSections_list quota was exhausted by the upstream endpoint.",
        "resource_not_found": "channelSections_list target was not found by the upstream endpoint.",
        "endpoint_unavailable": "channelSections_list upstream endpoint is temporarily unavailable.",
        "upstream_failure": "channelSections_list upstream execution failed.",
    }
    category = categories.get(error.category, "upstream_failure")
    return ChannelSectionsListToolError(
        messages[category],
        category=category,
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def build_channel_sections_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-section-access",
    oauth_token: str | None = None,
):
    """Build the concrete ``channelSections_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Callable dispatcher handler.
    """
    channel_sections_wrapper = wrapper or build_channel_sections_list_wrapper()
    channel_sections_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelSections_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 channel-section collection result.
        :raises ChannelSectionsListToolError: If validation, authorization, or upstream execution fails.
        """
        selector, _value = validate_channel_sections_list_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            response = channel_sections_wrapper.call(
                channel_sections_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_upstream_error(error) from error
        except ValueError as error:
            raise ChannelSectionsListToolError(
                str(error),
                category="invalid_request",
                details={"selector": selector},
            ) from error
        except Exception as error:
            raise ChannelSectionsListToolError(
                "channelSections_list upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channel_sections_list_result(response, arguments)

    return handler


def build_channel_sections_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-section-access",
    oauth_token: str | None = None,
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelSections_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_sections_list_contract()
    return {
        "name": CHANNEL_SECTIONS_LIST_TOOL_NAME,
        "description": CHANNEL_SECTIONS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
        "handler": build_channel_sections_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
    }


def build_channel_sections_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
):
    """Build the concrete ``channelSections_insert`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for write requests.
    :return: Callable dispatcher handler.
    """
    channel_sections_wrapper = wrapper or build_channel_sections_insert_wrapper()
    channel_sections_executor = executor or _default_insert_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelSections_insert`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 created channel-section result.
        :raises ChannelSectionsInsertToolError: If validation, authorization, or upstream execution fails.
        """
        validate_channel_sections_insert_arguments(arguments, oauth_token=oauth_token)
        auth_context = _insert_auth_context(oauth_token=oauth_token)
        try:
            response = channel_sections_wrapper.call(
                channel_sections_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_insert_upstream_error(error) from error
        except ValueError as error:
            raise ChannelSectionsInsertToolError(
                str(error),
                category="invalid_request",
            ) from error
        except Exception as error:
            raise ChannelSectionsInsertToolError(
                "channelSections_insert upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channel_sections_insert_result(response, arguments)

    return handler


def build_channel_sections_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelSections_insert`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for write requests.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_sections_insert_contract()
    return {
        "name": CHANNEL_SECTIONS_INSERT_TOOL_NAME,
        "description": CHANNEL_SECTIONS_INSERT_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA,
        "handler": build_channel_sections_insert_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


def build_channel_sections_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
):
    """Build the concrete ``channelSections_update`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for write requests.
    :return: Callable dispatcher handler.
    """
    channel_sections_wrapper = wrapper or build_channel_sections_update_wrapper()
    channel_sections_executor = executor or _default_update_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelSections_update`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 updated channel-section result.
        :raises ChannelSectionsUpdateToolError: If validation, authorization, or upstream execution fails.
        """
        validate_channel_sections_update_arguments(arguments, oauth_token=oauth_token)
        auth_context = _update_auth_context(oauth_token=oauth_token)
        try:
            response = channel_sections_wrapper.call(
                channel_sections_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_update_upstream_error(error) from error
        except ValueError as error:
            raise ChannelSectionsUpdateToolError(
                str(error),
                category="invalid_request",
            ) from error
        except Exception as error:
            raise ChannelSectionsUpdateToolError(
                "channelSections_update upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channel_sections_update_result(response, arguments)

    return handler


def build_channel_sections_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelSections_update`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for write requests.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_sections_update_contract()
    return {
        "name": CHANNEL_SECTIONS_UPDATE_TOOL_NAME,
        "description": CHANNEL_SECTIONS_UPDATE_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_SECTIONS_UPDATE_INPUT_SCHEMA,
        "handler": build_channel_sections_update_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


def build_channel_sections_delete_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
):
    """Build the concrete ``channelSections_delete`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for destructive delete requests.
    :return: Callable dispatcher handler.
    """
    channel_sections_wrapper = wrapper or build_channel_sections_delete_wrapper()
    channel_sections_executor = executor or _default_delete_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelSections_delete`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 deletion acknowledgment result.
        :raises ChannelSectionsDeleteToolError: If validation, authorization, or upstream execution fails.
        """
        validate_channel_sections_delete_arguments(arguments, oauth_token=oauth_token)
        auth_context = _delete_auth_context(oauth_token=oauth_token)
        try:
            response = channel_sections_wrapper.call(
                channel_sections_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_delete_upstream_error(error) from error
        except ValueError as error:
            raise ChannelSectionsDeleteToolError(
                str(error),
                category="invalid_request",
            ) from error
        except Exception as error:
            raise ChannelSectionsDeleteToolError(
                "channelSections_delete upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channel_sections_delete_result(response, arguments)

    return handler


def build_channel_sections_delete_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-section-write",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelSections_delete`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for destructive delete requests.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_sections_delete_contract()
    return {
        "name": CHANNEL_SECTIONS_DELETE_TOOL_NAME,
        "description": CHANNEL_SECTIONS_DELETE_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_SECTIONS_DELETE_INPUT_SCHEMA,
        "handler": build_channel_sections_delete_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "CHANNEL_SECTIONS_DELETE_CAVEATS",
    "CHANNEL_SECTIONS_DELETE_CALLER_EXAMPLES",
    "CHANNEL_SECTIONS_DELETE_DESCRIPTION",
    "CHANNEL_SECTIONS_DELETE_INPUT_SCHEMA",
    "CHANNEL_SECTIONS_DELETE_QUOTA_COST",
    "CHANNEL_SECTIONS_DELETE_TOOL_NAME",
    "CHANNEL_SECTIONS_DELETE_USAGE_NOTES",
    "CHANNEL_SECTIONS_INSERT_CAVEATS",
    "CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES",
    "CHANNEL_SECTIONS_INSERT_DESCRIPTION",
    "CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA",
    "CHANNEL_SECTIONS_INSERT_QUOTA_COST",
    "CHANNEL_SECTIONS_INSERT_SUPPORTED_PARTS",
    "CHANNEL_SECTIONS_INSERT_TOOL_NAME",
    "CHANNEL_SECTIONS_INSERT_USAGE_NOTES",
    "CHANNEL_SECTIONS_LIST_CAVEATS",
    "CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES",
    "CHANNEL_SECTIONS_LIST_DESCRIPTION",
    "CHANNEL_SECTIONS_LIST_INPUT_SCHEMA",
    "CHANNEL_SECTIONS_LIST_QUOTA_COST",
    "CHANNEL_SECTIONS_LIST_SELECTORS",
    "CHANNEL_SECTIONS_LIST_TOOL_NAME",
    "CHANNEL_SECTIONS_LIST_USAGE_NOTES",
    "CHANNEL_SECTIONS_UPDATE_CAVEATS",
    "CHANNEL_SECTIONS_UPDATE_CALLER_EXAMPLES",
    "CHANNEL_SECTIONS_UPDATE_DESCRIPTION",
    "CHANNEL_SECTIONS_UPDATE_INPUT_SCHEMA",
    "CHANNEL_SECTIONS_UPDATE_QUOTA_COST",
    "CHANNEL_SECTIONS_UPDATE_SUPPORTED_PARTS",
    "CHANNEL_SECTIONS_UPDATE_TOOL_NAME",
    "CHANNEL_SECTIONS_UPDATE_USAGE_NOTES",
    "ChannelSectionsDeleteToolError",
    "ChannelSectionsInsertToolError",
    "ChannelSectionsListToolError",
    "ChannelSectionsUpdateToolError",
    "build_channel_sections_delete_contract",
    "build_channel_sections_delete_handler",
    "build_channel_sections_delete_tool_descriptor",
    "build_channel_sections_insert_contract",
    "build_channel_sections_insert_handler",
    "build_channel_sections_insert_tool_descriptor",
    "build_channel_sections_list_contract",
    "build_channel_sections_list_handler",
    "build_channel_sections_list_tool_descriptor",
    "build_channel_sections_update_contract",
    "build_channel_sections_update_handler",
    "build_channel_sections_update_tool_descriptor",
    "map_channel_sections_delete_result",
    "map_channel_sections_insert_result",
    "map_channel_sections_list_result",
    "map_channel_sections_update_result",
    "validate_channel_sections_delete_arguments",
    "validate_channel_sections_insert_arguments",
    "validate_channel_sections_list_arguments",
    "validate_channel_sections_update_arguments",
]
