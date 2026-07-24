"""Concrete Layer 2 tool support for YouTube ``videos``."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.videos import (
    build_videos_get_rating_wrapper,
    build_videos_insert_wrapper,
    build_videos_list_wrapper,
    build_videos_rate_wrapper,
    build_videos_report_abuse_wrapper,
    build_videos_update_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


VIDEOS_LIST_TOOL_NAME = "videos_list"
VIDEOS_LIST_QUOTA_COST = 1
VIDEOS_LIST_SELECTORS = ("id", "chart", "myRating")
VIDEOS_LIST_COLLECTION_SELECTORS = ("chart", "myRating")
VIDEOS_LIST_CHART_REFINEMENTS = ("regionCode", "videoCategoryId")
VIDEOS_LIST_ALLOWED_FIELDS = frozenset(
    {"part", "id", "chart", "myRating", "pageToken", "maxResults", "regionCode", "videoCategoryId"}
)
VIDEOS_LIST_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "authorization",
        "authorization_header",
        "headers",
        "request_headers",
        "request_context",
        "response_body",
        "upstream_body",
    }
)

VIDEOS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "chart": {"type": "string", "enum": ["mostPopular"]},
        "myRating": {"type": "string", "enum": ["like", "dislike"]},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": 50},
        "regionCode": {"type": "string", "minLength": 2, "maxLength": 2},
        "videoCategoryId": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in VIDEOS_LIST_SELECTORS],
    "additionalProperties": False,
}

VIDEOS_LIST_DESCRIPTION = (
    "List YouTube videos. Endpoint: videos.list. Quota cost: 1. Auth: mixed/conditional. "
    "Requires part and exactly one selector: id, chart, or myRating."
)

VIDEOS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: mixed/conditional. Use id and chart with API-key-compatible access; myRating requires OAuth.",
    "Quota cost: 1. Provide non-empty part and exactly one selector from id, chart, or myRating.",
    "Quota cost: 1. pageToken and maxResults are supported only with chart or myRating collection requests.",
    "Quota cost: 1. regionCode and videoCategoryId refine chart=mostPopular only.",
    "Quota cost: 1. Empty upstream items are returned as a successful empty videos list.",
)

VIDEOS_LIST_CAVEATS = (
    "This tool is a read-only videos.list wrapper; search workflows belong to search_list.",
    "upload, update, delete, rating mutation, transcript, analytics, recommendation, ranking, summarization, and enrichment workflows are out of scope.",
    "The tool preserves upstream video fields and does not fabricate video details, rankings, summaries, or recommendations.",
)

VIDEOS_LIST_CALLER_EXAMPLES = (
    {
        "name": "direct_video_lookup",
        "description": "Quota cost: 1. Retrieve one or more videos by id with API-key-compatible access.",
        "arguments": {"part": "snippet,contentDetails", "id": "abc123"},
        "result": {"endpoint": "videos.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "chart_lookup",
        "description": "Quota cost: 1. Retrieve mostPopular chart videos with API-key-compatible access.",
        "arguments": {"part": "snippet,statistics", "chart": "mostPopular", "regionCode": "US"},
        "result": {"endpoint": "videos.list", "selector": "chart", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "rating_lookup",
        "description": "Quota cost: 1. Retrieve videos rated by the authorized caller; myRating requires OAuth.",
        "arguments": {"part": "snippet", "myRating": "like"},
        "result": {"endpoint": "videos.list", "selector": "myRating", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "paginated_chart_lookup",
        "description": "Quota cost: 1. Traverse chart results with pageToken and maxResults.",
        "arguments": {"part": "snippet", "chart": "mostPopular", "pageToken": "next", "maxResults": 25},
        "result": {"endpoint": "videos.list", "pagination": {"pageToken": "next", "maxResults": 25}},
        "quotaCost": 1,
    },
    {
        "name": "populated_success",
        "description": "Quota cost: 1. Successful lookup with one or more upstream video items.",
        "arguments": {"part": "snippet", "id": "abc123"},
        "result": {"items": [{"id": "abc123"}], "empty": False},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. Empty upstream items remain a successful empty videos list result.",
        "arguments": {"part": "snippet", "id": "missing-video"},
        "result": {"items": [], "empty": True},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 1. Missing part is rejected before upstream execution.",
        "arguments": {"id": "abc123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_selector",
        "description": "Quota cost: 1. Missing id, chart, or myRating selector is rejected before upstream execution.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "conflicting_selectors",
        "description": "Quota cost: 1. Supplying multiple selectors is rejected as ambiguous.",
        "arguments": {"part": "snippet", "id": "abc123", "chart": "mostPopular"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_pagination",
        "description": "Quota cost: 1. pageToken and maxResults are rejected with direct id lookups.",
        "arguments": {"part": "snippet", "id": "abc123", "pageToken": "next"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 1. Missing API-key-compatible access is reported as an authentication failure.",
        "arguments": {"part": "snippet", "id": "abc123"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "oauth_access_failure",
        "description": "Quota cost: 1. Missing OAuth access for myRating is reported as an authentication failure.",
        "arguments": {"part": "snippet", "myRating": "like"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 1. Quota and upstream failures are mapped to safe public categories.",
        "arguments": {"part": "snippet", "id": "abc123"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "deprecated_endpoint",
        "description": "Quota cost: 1. Deprecated endpoint failures are surfaced distinctly if upstream reports them.",
        "arguments": {"part": "snippet", "chart": "mostPopular"},
        "errorCategory": "deprecated_endpoint",
    },
    {
        "name": "endpoint_unavailable",
        "description": "Quota cost: 1. Endpoint availability failures are surfaced without unsafe upstream details.",
        "arguments": {"part": "snippet", "chart": "mostPopular"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 1. Search, upload, update, delete, rating mutation, transcript, analytics, ranking, summarization, and enrichment fields are rejected.",
        "arguments": {"part": "snippet", "id": "abc123", "analytics": True},
        "errorCategory": "invalid_request",
    },
)

VIDEOS_INSERT_TOOL_NAME = "videos_insert"
VIDEOS_INSERT_QUOTA_COST = 1600
VIDEOS_INSERT_UPLOAD_MODES = ("multipart", "resumable")
VIDEOS_INSERT_ALLOWED_FIELDS = frozenset(
    {"part", "body", "media", "uploadMode", "notifySubscribers", "onBehalfOfContentOwner"}
)
VIDEOS_INSERT_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "authorization",
        "authorization_header",
        "headers",
        "request_headers",
        "request_context",
        "response_body",
        "upstream_body",
        "media",
        "raw_media",
        "content",
        "signed_url",
    }
)

VIDEOS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body", "media"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "body": {"type": "object"},
        "media": {"type": "object"},
        "uploadMode": {"type": "string", "enum": list(VIDEOS_INSERT_UPLOAD_MODES)},
        "notifySubscribers": {"type": "boolean"},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

VIDEOS_INSERT_DESCRIPTION = (
    "Create a YouTube video through videos.insert. Quota cost: 1600. Auth: OAuth required. "
    "Requires part, metadata body, and media upload input; upload availability is media constrained."
)

VIDEOS_INSERT_USAGE_NOTES = (
    "Quota cost: 1600. OAuth authorization is required for every videos.insert upload request.",
    "Quota cost: 1600. Provide non-empty part, body.snippet metadata, and media.mimeType plus media.content.",
    "Quota cost: 1600. uploadMode may be multipart or resumable; resumable is useful for larger upload flows.",
    "Quota cost: 1600. onBehalfOfContentOwner is accepted only for eligible OAuth delegation contexts.",
    "Quota cost: 1600. The result preserves the created video resource without automatic publishing, editing, analytics, ranking, recommendation, summarization, or enrichment.",
)

VIDEOS_INSERT_CAVEATS = (
    "This tool is a low-level videos.insert wrapper for video creation only.",
    "New uploads may remain private by default or be audit, release, policy, owner, or channel constrained.",
    "Metadata-only, media-only, automatic publishing, update, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint workflows are out of scope.",
    "Credentials, authorization headers, signed upload links, media payload content, and unsafe upstream diagnostics are never returned to callers.",
)

VIDEOS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_video_creation",
        "description": "Quota cost: 1600. Create one video with OAuth, metadata body, and safe media upload content.",
        "arguments": {
            "part": "snippet,status",
            "body": {"snippet": {"title": "Example upload"}, "status": {"privacyStatus": "private"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
        },
        "result": {
            "endpoint": "videos.insert",
            "quotaCost": 1600,
            "mutation": {"type": "created"},
            "resourcePath": "item",
        },
        "quotaCost": 1600,
    },
    {
        "name": "resumable_upload",
        "description": "Quota cost: 1600. Use uploadMode=resumable for a supported resumable videos.insert upload.",
        "arguments": {
            "part": "snippet,status",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
            "uploadMode": "resumable",
        },
        "result": {"endpoint": "videos.insert", "upload": {"mode": "resumable", "contentProvided": True}},
        "quotaCost": 1600,
    },
    {
        "name": "delegated_content_owner",
        "description": "Quota cost: 1600. Provide onBehalfOfContentOwner only with eligible OAuth delegation access.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Partner upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
            "onBehalfOfContentOwner": "CONTENT_OWNER_ID",
        },
        "result": {"endpoint": "videos.insert", "delegation": {"onBehalfOfContentOwner": "CONTENT_OWNER_ID"}},
        "quotaCost": 1600,
    },
    {
        "name": "metadata_only_failure",
        "description": "Quota cost: 1600. Metadata-only creation is rejected because media input is required.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Example upload"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "media_only_failure",
        "description": "Quota cost: 1600. Media-only creation is rejected because part and metadata body are required.",
        "arguments": {"media": {"mimeType": "video/mp4", "content": "<video content omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 1600. Missing OAuth is reported as authentication_failed before upload execution.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
        },
        "errorCategory": "authentication_failed",
    },
    {
        "name": "unsupported_upload_mode",
        "description": "Quota cost: 1600. Unsupported uploadMode values are rejected before endpoint execution.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
            "uploadMode": "direct",
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 1600. Quota, policy, availability, raw media, upload, and upstream failures map to safe public categories.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
        },
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "availability_constrained",
        "description": "Quota cost: 1600. Upload availability may be audit, release, policy, owner, or private-default constrained.",
        "arguments": {
            "part": "snippet,status",
            "body": {"snippet": {"title": "Example upload"}, "status": {"privacyStatus": "private"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
        },
        "result": {"availability": {"state": "media_constrained"}},
        "quotaCost": 1600,
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 1600. Automatic publishing, update, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint fields are rejected.",
        "arguments": {
            "part": "snippet",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "<video content omitted>"},
            "analytics": True,
        },
        "errorCategory": "invalid_request",
    },
)

VIDEOS_UPDATE_TOOL_NAME = "videos_update"
VIDEOS_UPDATE_QUOTA_COST = 50
VIDEOS_UPDATE_WRITABLE_PARTS = ("snippet",)
VIDEOS_UPDATE_ALLOWED_FIELDS = frozenset({"part", "body", "onBehalfOfContentOwner"})
VIDEOS_UPDATE_ALLOWED_BODY_FIELDS = frozenset({"id", "kind", "snippet"})
VIDEOS_UPDATE_ALLOWED_SNIPPET_FIELDS = frozenset({"title"})
VIDEOS_UPDATE_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "authorization_header",
        "headers",
        "oauth_token",
        "request_context",
        "request_headers",
        "response_body",
        "stack",
        "stack_trace",
        "traceback",
        "upstream_body",
    }
)

VIDEOS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {"type": "string", "enum": list(VIDEOS_UPDATE_WRITABLE_PARTS)},
        "body": {
            "type": "object",
            "required": ["id", "snippet"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "kind": {"type": "string", "minLength": 1},
                "snippet": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {"title": {"type": "string", "minLength": 1}},
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

VIDEOS_UPDATE_DESCRIPTION = (
    "Update YouTube video metadata through videos.update. Quota cost: 50. Auth: OAuth required. "
    "Supports replacement-oriented metadata updates for part=snippet with body.id and body.snippet.title."
)

VIDEOS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required for every videos.update request.",
    "Quota cost: 50. Provide part=snippet, body.id, and body.snippet.title for the supported metadata update path.",
    "Quota cost: 50. videos.update uses replacement semantics for included writable parts; include every supported field that should remain on the updated snippet.",
    "Quota cost: 50. onBehalfOfContentOwner is accepted only for eligible OAuth delegation contexts.",
    "Quota cost: 50. The result is a near-raw updated video resource and never includes credentials, raw upstream diagnostics, or secret-bearing request context.",
)

VIDEOS_UPDATE_CAVEATS = (
    "This tool is a low-level videos.update wrapper for metadata update only.",
    "Only the snippet writable part is supported in this slice, and the update body is limited to body.id and body.snippet.title.",
    "media upload, media replacement, transcoding, automatic publishing, create, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint workflows are out of scope.",
    "Credentials, authorization headers, raw upstream diagnostics, raw request context, and secret-bearing fields are never returned to callers.",
)

VIDEOS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "authorized_metadata_update",
        "description": "Quota cost: 50. Update a video title with OAuth using videos.update, part=snippet, body.id, and body.snippet.title.",
        "arguments": {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}},
        "result": {
            "endpoint": "videos.update",
            "quotaCost": 50,
            "mutation": {"type": "updated"},
            "resourcePath": "item",
        },
        "quotaCost": 50,
    },
    {
        "name": "delegated_content_owner_update",
        "description": "Quota cost: 50. Provide onBehalfOfContentOwner only with eligible OAuth delegation access.",
        "arguments": {
            "part": "snippet",
            "body": {"id": "abc123", "snippet": {"title": "Partner updated title"}},
            "onBehalfOfContentOwner": "CONTENT_OWNER_ID",
        },
        "result": {"endpoint": "videos.update", "delegation": {"onBehalfOfContentOwner": "CONTENT_OWNER_ID"}},
        "quotaCost": 50,
    },
    {
        "name": "missing_identity_failure",
        "description": "Quota cost: 50. Missing body.id is rejected before upstream execution.",
        "arguments": {"part": "snippet", "body": {"snippet": {"title": "Updated title"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_part_failure",
        "description": "Quota cost: 50. Missing or empty part is rejected before upstream execution.",
        "arguments": {"body": {"id": "abc123", "snippet": {"title": "Updated title"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_field_failure",
        "description": "Quota cost: 50. Unsupported read-only, status, media upload, or workflow fields are rejected before endpoint execution.",
        "arguments": {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title", "description": "Unsupported"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Missing OAuth is reported as authentication_failed before update execution.",
        "arguments": {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_update_failure",
        "description": "Quota cost: 50. Quota, policy, availability, and upstream failures map to safe public categories without raw upstream diagnostics.",
        "arguments": {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 50. media upload, create, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, and enrichment fields are rejected.",
        "arguments": {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}, "analytics": True},
        "errorCategory": "invalid_request",
    },
)

VIDEOS_RATE_TOOL_NAME = "videos_rate"
VIDEOS_RATE_QUOTA_COST = 50
VIDEOS_RATE_VALUES = ("like", "dislike", "none")
VIDEOS_RATE_ALLOWED_FIELDS = frozenset({"id", "rating"})
VIDEOS_RATE_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "authorization_header",
        "headers",
        "oauth_token",
        "request_context",
        "request_headers",
        "response_body",
        "stack",
        "stack_trace",
        "stacktrace",
        "traceback",
        "upstream_body",
    }
)

VIDEOS_RATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id", "rating"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "rating": {"type": "string", "enum": list(VIDEOS_RATE_VALUES)},
    },
    "additionalProperties": False,
}

VIDEOS_RATE_DESCRIPTION = (
    "Rate a YouTube video through videos.rate. Quota cost: 50. Auth: OAuth required. "
    "Requires id and rating, supports like, dislike, or none, and sends no request body."
)

VIDEOS_RATE_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required for every videos.rate request.",
    "Quota cost: 50. Provide one non-empty id and one rating value: like, dislike, or none.",
    "Quota cost: 50. rating=none is an explicit clear-rating action and is distinct from omitting rating.",
    "Quota cost: 50. The upstream operation sends no request body; body, videoId aliases, and delegation modifiers are rejected.",
    "Quota cost: 50. Success is a mutation acknowledgment for the requested rating action, not a refreshed video resource.",
)

VIDEOS_RATE_CAVEATS = (
    "This tool is a low-level videos.rate wrapper for applying, changing, or clearing the authorized caller's rating only.",
    "current-rating lookup, rating history, aggregate rating counts, upload, update, delete, abuse report, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint workflows are out of scope.",
    "Some videos may be unavailable, removed, purchase-restricted, policy-restricted, or otherwise non-ratable for the authorized caller.",
    "Credentials, authorization headers, raw upstream diagnostics, raw request context, and secret-bearing fields are never returned to callers.",
)

VIDEOS_RATE_CALLER_EXAMPLES = (
    {
        "name": "authorized_like_rating",
        "description": "Quota cost: 50. Apply a like rating with OAuth using videos.rate and no request body.",
        "arguments": {"id": "abc123", "rating": "like"},
        "result": {
            "endpoint": "videos.rate",
            "quotaCost": 50,
            "mutation": {"type": "rated", "acknowledged": True},
            "status": {"code": 204, "body": "none"},
        },
        "quotaCost": 50,
    },
    {
        "name": "authorized_dislike_rating",
        "description": "Quota cost: 50. Apply a dislike rating with OAuth using videos.rate and no request body.",
        "arguments": {"id": "abc123", "rating": "dislike"},
        "result": {"endpoint": "videos.rate", "rating": {"requestedRating": "dislike"}},
        "quotaCost": 50,
    },
    {
        "name": "authorized_clear_rating",
        "description": "Quota cost: 50. Use rating=none to clear the caller's prior rating with OAuth and no request body.",
        "arguments": {"id": "abc123", "rating": "none"},
        "result": {"endpoint": "videos.rate", "rating": {"requestedRating": "none", "clearsRating": True}},
        "quotaCost": 50,
    },
    {
        "name": "missing_identity_failure",
        "description": "Quota cost: 50. Missing id is rejected before videos.rate execution.",
        "arguments": {"rating": "like"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_rating_failure",
        "description": "Quota cost: 50. Missing rating is rejected before videos.rate execution.",
        "arguments": {"id": "abc123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_rating_failure",
        "description": "Quota cost: 50. Unsupported or differently cased rating values are rejected.",
        "arguments": {"id": "abc123", "rating": "LIKE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "request_body_failure",
        "description": "Quota cost: 50. Request body input is rejected because videos.rate sends no request body.",
        "arguments": {"id": "abc123", "rating": "like", "body": {}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Missing OAuth is reported as authentication_failed before rating execution.",
        "arguments": {"id": "abc123", "rating": "like"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_rate_failure",
        "description": "Quota cost: 50. Quota, availability, disabled rating, policy, and upstream failures map to safe public categories.",
        "arguments": {"id": "abc123", "rating": "like"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "not_found_failure",
        "description": "Quota cost: 50. Removed or missing target videos are reported as resource_not_found.",
        "arguments": {"id": "missing-video", "rating": "like"},
        "errorCategory": "resource_not_found",
    },
    {
        "name": "non_ratable_target_failure",
        "description": "Quota cost: 50. Non-ratable, disabled rating, purchase-required, or policy-restricted targets are reported safely.",
        "arguments": {"id": "restricted-video", "rating": "like"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "deprecated_endpoint",
        "description": "Quota cost: 50. Deprecated endpoint failures are surfaced distinctly if upstream reports them.",
        "arguments": {"id": "abc123", "rating": "like"},
        "errorCategory": "deprecated_endpoint",
    },
    {
        "name": "endpoint_unavailable",
        "description": "Quota cost: 50. Endpoint availability failures are surfaced without unsafe upstream details.",
        "arguments": {"id": "abc123", "rating": "like"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 50. Rating lookup, history, counts, upload, update, delete, abuse, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, and enrichment fields are rejected.",
        "arguments": {"id": "abc123", "rating": "like", "analytics": True},
        "errorCategory": "invalid_request",
    },
)

VIDEOS_GET_RATING_TOOL_NAME = "videos_getRating"
VIDEOS_GET_RATING_QUOTA_COST = 1
VIDEOS_GET_RATING_VALUES = ("like", "dislike", "none", "unspecified")
VIDEOS_GET_RATING_ALLOWED_FIELDS = frozenset({"id", "onBehalfOfContentOwner"})
VIDEOS_GET_RATING_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "authorization_header",
        "headers",
        "oauth_token",
        "request_context",
        "request_headers",
        "response_body",
        "stack",
        "stack_trace",
        "stacktrace",
        "traceback",
        "upstream_body",
    }
)

VIDEOS_GET_RATING_INPUT_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

VIDEOS_GET_RATING_DESCRIPTION = (
    "Get the authorized caller's YouTube video rating through videos.getRating. Quota cost: 1. "
    "Auth: OAuth required. Requires id with one to fifty comma-separated video identifiers and sends no request body."
)

VIDEOS_GET_RATING_USAGE_NOTES = (
    "Quota cost: 1. OAuth authorization is required for every videos.getRating request.",
    "Quota cost: 1. Provide id with one to fifty comma-separated unique video identifiers.",
    "Quota cost: 1. Returned per-video rating states are like, dislike, none, or unspecified.",
    "Quota cost: 1. onBehalfOfContentOwner is accepted only for eligible OAuth partner delegation contexts.",
    "Quota cost: 1. videos.getRating sends no request body and returns the caller's rating state only.",
)

VIDEOS_GET_RATING_CAVEATS = (
    "This tool is a read-only videos.getRating wrapper for current authorized-caller rating lookup only.",
    "rating mutation, rating history, aggregate rating counts, video metadata lookup, video update, upload, delete, abuse report, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, and enrichment workflows are out of scope.",
    "Some videos may be unavailable, removed, policy-restricted, or hidden from rating lookup for the authorized caller.",
    "Credentials, authorization headers, raw upstream diagnostics, raw request context, and secret-bearing fields are never returned to callers.",
)

VIDEOS_GET_RATING_CALLER_EXAMPLES = (
    {
        "name": "authorized_single_video_lookup",
        "description": "Quota cost: 1. Look up the authorized caller's rating for one video with OAuth and no request body.",
        "arguments": {"id": "abc123"},
        "result": {"endpoint": "videos.getRating", "items": [{"videoId": "abc123", "rating": "like"}]},
        "quotaCost": 1,
    },
    {
        "name": "authorized_multi_video_lookup",
        "description": "Quota cost: 1. Look up current ratings for one to fifty videos in one OAuth request.",
        "arguments": {"id": "abc123,def456"},
        "result": {"endpoint": "videos.getRating", "lookup": {"requestedIds": ["abc123", "def456"]}},
        "quotaCost": 1,
    },
    {
        "name": "delegated_partner_lookup",
        "description": "Quota cost: 1. Provide onBehalfOfContentOwner only with eligible OAuth partner delegation.",
        "arguments": {"id": "abc123", "onBehalfOfContentOwner": "CONTENT_OWNER_ID"},
        "result": {"endpoint": "videos.getRating", "delegation": {"onBehalfOfContentOwner": "CONTENT_OWNER_ID"}},
        "quotaCost": 1,
    },
    {
        "name": "unrated_none_lookup",
        "description": "Quota cost: 1. A returned rating of none means the caller has no active like or dislike.",
        "arguments": {"id": "unrated-video"},
        "result": {"items": [{"videoId": "unrated-video", "rating": "none", "isUnrated": True}]},
        "quotaCost": 1,
    },
    {
        "name": "unspecified_lookup",
        "description": "Quota cost: 1. A returned rating of unspecified is preserved as an unrated lookup state.",
        "arguments": {"id": "state-unknown"},
        "result": {"items": [{"videoId": "state-unknown", "rating": "unspecified", "isUnrated": True}]},
        "quotaCost": 1,
    },
    {
        "name": "missing_identity_failure",
        "description": "Quota cost: 1. Missing id is rejected before videos.getRating execution.",
        "arguments": {},
        "errorCategory": "invalid_request",
    },
    {
        "name": "duplicate_identifier_failure",
        "description": "Quota cost: 1. Duplicate video identifiers are rejected before lookup execution.",
        "arguments": {"id": "abc123,abc123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "over_limit_identifier_failure",
        "description": "Quota cost: 1. More than one to fifty requested identifiers are rejected before execution.",
        "arguments": {"id": "video-1,...,video-51"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 1. Missing OAuth is reported as authentication_failed before rating lookup execution.",
        "arguments": {"id": "abc123"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_lookup_failure",
        "description": "Quota cost: 1. Quota, policy, availability, and upstream failures map to safe public categories.",
        "arguments": {"id": "abc123"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "unavailable_target_failure",
        "description": "Quota cost: 1. Removed or unavailable target videos are reported without unsafe upstream details.",
        "arguments": {"id": "missing-video"},
        "errorCategory": "resource_not_found",
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 1. Rating mutation, history, counts, metadata, upload, update, delete, transcript, analytics, ranking, summarization, and enrichment fields are rejected.",
        "arguments": {"id": "abc123", "analytics": True},
        "errorCategory": "invalid_request",
    },
)

VIDEOS_REPORT_ABUSE_TOOL_NAME = "videos_reportAbuse"
VIDEOS_REPORT_ABUSE_QUOTA_COST = 50
VIDEOS_REPORT_ABUSE_REQUIRED_BODY_FIELDS = ("videoId", "reasonId")
VIDEOS_REPORT_ABUSE_BODY_FIELDS = ("videoId", "reasonId", "secondaryReasonId", "comments", "language")
VIDEOS_REPORT_ABUSE_ALLOWED_FIELDS = frozenset({"body"})
VIDEOS_REPORT_ABUSE_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "authorization_header",
        "body",
        "comments",
        "headers",
        "oauth_token",
        "raw_body",
        "report_body",
        "request_body",
        "request_context",
        "request_headers",
        "response_body",
        "stack",
        "stack_trace",
        "stacktrace",
        "traceback",
        "upstream_body",
    }
)

VIDEOS_REPORT_ABUSE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["body"],
    "properties": {
        "body": {
            "type": "object",
            "required": list(VIDEOS_REPORT_ABUSE_REQUIRED_BODY_FIELDS),
            "properties": {
                "videoId": {"type": "string", "minLength": 1},
                "reasonId": {"type": "string", "minLength": 1},
                "secondaryReasonId": {"type": "string", "minLength": 1},
                "comments": {"type": "string", "minLength": 1},
                "language": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}

VIDEOS_REPORT_ABUSE_DESCRIPTION = (
    "Submit an authorized YouTube abuse report through videos.reportAbuse. Quota cost: 50. "
    "Auth: OAuth required. Requires body.videoId and body.reasonId, with optional body.secondaryReasonId, "
    "body.comments, and body.language."
)

VIDEOS_REPORT_ABUSE_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required for every videos.reportAbuse request.",
    "Quota cost: 50. Provide body.videoId for the target video and body.reasonId for the selected abuse reason.",
    "Quota cost: 50. Optional body.secondaryReasonId, body.comments, and body.language are passed only as report context.",
    "Quota cost: 50. onBehalfOfContentOwner is not supported for videos_reportAbuse in this slice.",
    "Quota cost: 50. Success is a no-content abuse-report acknowledgment, not video metadata, classification, moderation, evidence, or policy analysis.",
)

VIDEOS_REPORT_ABUSE_CAVEATS = (
    "This tool is a low-level videos.reportAbuse wrapper for direct authorized abuse-report submission only.",
    "Abuse reason discovery belongs to videoAbuseReportReasons_list and is not performed by videos_reportAbuse.",
    "Automated abuse classification, moderation decisions, evidence collection, video lookup, video deletion, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint workflows are out of scope.",
    "Credentials, authorization headers, sensitive report comments, raw upstream diagnostics, raw request context, and secret-bearing fields are never returned to callers.",
)

VIDEOS_REPORT_ABUSE_CALLER_EXAMPLES = (
    {
        "name": "authorized_abuse_report",
        "description": "Quota cost: 50. Submit one abuse report with OAuth using body.videoId and body.reasonId.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}},
        "result": {
            "endpoint": "videos.reportAbuse",
            "quotaCost": 50,
            "acknowledgment": {"accepted": True, "status": "submitted"},
        },
        "quotaCost": 50,
    },
    {
        "name": "authorized_abuse_report_with_optional_details",
        "description": "Quota cost: 50. Include supported optional report details without returning sensitive comments.",
        "arguments": {
            "body": {
                "videoId": "abc123",
                "reasonId": "VIOLENCE",
                "secondaryReasonId": "graphic",
                "comments": "Additional report context omitted from results",
                "language": "en",
            }
        },
        "result": {
            "endpoint": "videos.reportAbuse",
            "report": {"videoId": "abc123", "reasonId": "VIOLENCE", "hasComments": True},
            "status": {"code": 204, "body": "none"},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_body_failure",
        "description": "Quota cost: 50. Missing body is rejected before videos.reportAbuse execution.",
        "arguments": {},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_target_failure",
        "description": "Quota cost: 50. Missing body.videoId is rejected before videos.reportAbuse execution.",
        "arguments": {"body": {"reasonId": "VIOLENCE"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_reason_failure",
        "description": "Quota cost: 50. Missing body.reasonId is rejected before videos.reportAbuse execution.",
        "arguments": {"body": {"videoId": "abc123"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_optional_field_failure",
        "description": "Quota cost: 50. Unsupported body fields are rejected before endpoint execution.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE", "evidence": "unsupported"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "rejected_partner_delegation",
        "description": "Quota cost: 50. onBehalfOfContentOwner is rejected because delegation is outside this slice.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}, "onBehalfOfContentOwner": "owner"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_oauth",
        "description": "Quota cost: 50. Missing OAuth is reported as authentication_failed before report execution.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_report_failure",
        "description": "Quota cost: 50. Quota, policy, refusal, availability, and upstream failures map to safe categories.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "unavailable_target_failure",
        "description": "Quota cost: 50. Removed or unavailable target videos are reported without unsafe upstream details.",
        "arguments": {"body": {"videoId": "missing-video", "reasonId": "VIOLENCE"}},
        "errorCategory": "resource_not_found",
    },
    {
        "name": "upstream_refusal_failure",
        "description": "Quota cost: 50. Upstream refusal or duplicate-report style outcomes are categorized safely.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "out_of_scope_video_workflow",
        "description": "Quota cost: 50. Classification, moderation, evidence, lookup, deletion, analytics, ranking, summarization, and enrichment fields are rejected.",
        "arguments": {"body": {"videoId": "abc123", "reasonId": "VIOLENCE"}, "classify": True},
        "errorCategory": "invalid_request",
    },
)


class VideosListToolError(ValueError):
    """Represent a safe caller-facing ``videos_list`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_list_error_details(details or {})


class VideosInsertToolError(ValueError):
    """Represent a safe caller-facing ``videos_insert`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe insert tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_insert_error_details(details or {})


class VideosUpdateToolError(ValueError):
    """Represent a safe caller-facing ``videos_update`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe update tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_update_error_details(details or {})


class VideosRateToolError(ValueError):
    """Represent a safe caller-facing ``videos_rate`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe rating tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_rate_error_details(details or {})


class VideosGetRatingToolError(ValueError):
    """Represent a safe caller-facing ``videos_getRating`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe rating lookup tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_get_rating_error_details(details or {})


class VideosReportAbuseToolError(ValueError):
    """Represent a safe caller-facing ``videos_reportAbuse`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe report-abuse tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_videos_report_abuse_error_details(details or {})


def _sanitize_videos_list_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove endpoint-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_LIST_UNSAFE_DETAIL_KEYS
    }


def _sanitize_videos_insert_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove upload-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing insert errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_INSERT_UNSAFE_DETAIL_KEYS
    }


def _sanitize_videos_update_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove update-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing update errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_UPDATE_UNSAFE_DETAIL_KEYS
    }


def _sanitize_videos_rate_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove rating-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing rating errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_RATE_UNSAFE_DETAIL_KEYS
    }


def _sanitize_videos_get_rating_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove rating-lookup-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing rating lookup errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_GET_RATING_UNSAFE_DETAIL_KEYS
    }


def _sanitize_videos_report_abuse_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove report-abuse-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing report-abuse errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEOS_REPORT_ABUSE_UNSAFE_DETAIL_KEYS
    }


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited ``part`` selection.

    :param parts: Caller-provided ``part`` value.
    :return: Requested parts in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _split_ids(ids: str) -> list[str]:
    """Normalize a comma-delimited video identifier selection.

    :param ids: Caller-provided video identifiers.
    :return: Visible video identifiers in caller order.
    """
    return [item.strip() for item in ids.split(",") if item.strip()]


def _require_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideosListToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosListToolError(f"videos_list requires non-empty {field}", details={"field": field})
    return value.strip()


def _selected_selector(arguments: dict[str, Any]) -> tuple[str, str]:
    """Return the exactly-one non-empty videos selector.

    :param arguments: Candidate normalized request arguments.
    :return: Selected selector field and stripped value.
    :raises VideosListToolError: If selector input is missing or ambiguous.
    """
    selected = [
        selector for selector in VIDEOS_LIST_SELECTORS if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise VideosListToolError(
            "videos_list requires exactly one selector: id, chart, or myRating",
            details={"field": "selector", "allowed": list(VIDEOS_LIST_SELECTORS)},
        )
    selector = selected[0]
    return selector, str(arguments[selector]).strip()


def _validate_chart(value: str) -> str:
    """Validate and normalize a chart selector value.

    :param value: Candidate chart selector.
    :return: Normalized chart selector.
    :raises VideosListToolError: If the chart is unsupported.
    """
    if value != "mostPopular":
        raise VideosListToolError("chart must be mostPopular", details={"field": "chart"})
    return value


def _validate_my_rating(value: str) -> str:
    """Validate and normalize a caller rating selector value.

    :param value: Candidate ``myRating`` selector.
    :return: Normalized rating selector.
    :raises VideosListToolError: If the rating selector is unsupported.
    """
    if value not in {"like", "dislike"}:
        raise VideosListToolError("myRating must be like or dislike", details={"field": "myRating"})
    return value


def _validate_page_token(value: Any) -> str:
    """Validate and normalize a page token.

    :param value: Candidate page token.
    :return: Stripped page token.
    :raises VideosListToolError: If the page token is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
    return value.strip()


def _validate_max_results(value: Any) -> int:
    """Validate and normalize a page size.

    :param value: Candidate maximum result count.
    :return: Validated maximum result count.
    :raises VideosListToolError: If the result count is malformed or out of range.
    """
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 50:
        raise VideosListToolError("maxResults must be an integer from 1 through 50", details={"field": "maxResults"})
    return value


def _validate_region_code(value: Any) -> str:
    """Validate and normalize a chart region code.

    :param value: Candidate region code.
    :return: Uppercase two-letter region code.
    :raises VideosListToolError: If the region code is malformed.
    """
    if not isinstance(value, str) or len(value.strip()) != 2 or not value.strip().isalpha():
        raise VideosListToolError("regionCode must be a two-letter code", details={"field": "regionCode"})
    return value.strip().upper()


def _validate_video_category_id(value: Any) -> str:
    """Validate and normalize a chart video category identifier.

    :param value: Candidate video category identifier.
    :return: Stripped video category identifier.
    :raises VideosListToolError: If the identifier is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosListToolError(
            "videoCategoryId must be a non-empty string",
            details={"field": "videoCategoryId"},
        )
    return value.strip()


def validate_videos_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_list`` arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized ``part``, selector, pagination, and refinement values.
    :raises VideosListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosListToolError("videos_list arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_LIST_ALLOWED_FIELDS:
            raise VideosListToolError(f"unsupported field for videos_list: {field}", details={"field": field})

    part = _require_text_field(arguments, "part")
    if not _split_parts(part):
        raise VideosListToolError("part must include at least one requested resource part", details={"field": "part"})

    selector, value = _selected_selector(arguments)
    normalized: dict[str, Any] = {"part": part}
    if selector == "id":
        if not _split_ids(value):
            raise VideosListToolError("id must include at least one video identifier", details={"field": "id"})
        normalized["id"] = value
    elif selector == "chart":
        normalized["chart"] = _validate_chart(value)
    else:
        normalized["myRating"] = _validate_my_rating(value)

    for field in ("pageToken", "maxResults"):
        if field in arguments and selector not in VIDEOS_LIST_COLLECTION_SELECTORS:
            raise VideosListToolError(f"{field} is supported only with chart or myRating", details={"field": field})
    for field in VIDEOS_LIST_CHART_REFINEMENTS:
        if field in arguments and selector != "chart":
            raise VideosListToolError(f"{field} is supported only with chart", details={"field": field})

    if "pageToken" in arguments:
        normalized["pageToken"] = _validate_page_token(arguments["pageToken"])
    if "maxResults" in arguments:
        normalized["maxResults"] = _validate_max_results(arguments["maxResults"])
    if "regionCode" in arguments:
        normalized["regionCode"] = _validate_region_code(arguments["regionCode"])
    if "videoCategoryId" in arguments:
        normalized["videoCategoryId"] = _validate_video_category_id(arguments["videoCategoryId"])
    return normalized


def _require_videos_insert_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty ``videos_insert`` text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideosInsertToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosInsertToolError(f"videos_insert requires non-empty {field}", details={"field": field})
    return value.strip()


def _validate_videos_insert_body(body: Any) -> dict[str, Any]:
    """Validate the required video metadata body.

    :param body: Candidate metadata body.
    :return: Metadata body accepted by the Layer 1 wrapper.
    :raises VideosInsertToolError: If the body is missing or malformed.
    """
    if not isinstance(body, dict):
        raise VideosInsertToolError("videos_insert requires body metadata", details={"field": "body"})
    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise VideosInsertToolError("videos_insert requires body.snippet metadata", details={"field": "body.snippet"})
    return dict(body)


def _validate_videos_insert_media(media: Any) -> dict[str, Any]:
    """Validate the required video upload media descriptor.

    :param media: Candidate media upload descriptor.
    :return: Media descriptor accepted by the Layer 1 wrapper.
    :raises VideosInsertToolError: If the media descriptor is missing or malformed.
    """
    if not isinstance(media, dict):
        raise VideosInsertToolError("videos_insert requires media upload input", details={"field": "media"})
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise VideosInsertToolError("videos_insert requires media.mimeType", details={"field": "media.mimeType"})
    content = media.get("content")
    if not isinstance(content, str) or not content:
        raise VideosInsertToolError("videos_insert requires media.content", details={"field": "media.content"})
    normalized = dict(media)
    normalized["mimeType"] = mime_type.strip()
    return normalized


def _validate_videos_insert_upload_mode(value: Any) -> str:
    """Validate the optional upload mode.

    :param value: Candidate upload-mode value.
    :return: Normalized upload mode.
    :raises VideosInsertToolError: If the upload mode is unsupported.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosInsertToolError("uploadMode must be multipart or resumable", details={"field": "uploadMode"})
    mode = value.strip()
    if mode not in VIDEOS_INSERT_UPLOAD_MODES:
        raise VideosInsertToolError(
            "uploadMode must be multipart or resumable",
            details={"field": "uploadMode", "allowed": list(VIDEOS_INSERT_UPLOAD_MODES)},
        )
    return mode


def _validate_videos_insert_notify_subscribers(value: Any) -> bool:
    """Validate the optional subscriber-notification flag.

    :param value: Candidate notification flag.
    :return: Boolean notification flag.
    :raises VideosInsertToolError: If the value is not boolean.
    """
    if not isinstance(value, bool):
        raise VideosInsertToolError(
            "notifySubscribers must be boolean",
            details={"field": "notifySubscribers"},
        )
    return value


def _validate_videos_insert_delegation(value: Any) -> str:
    """Validate optional content-owner delegation context.

    :param value: Candidate content-owner identifier.
    :return: Stripped content-owner identifier.
    :raises VideosInsertToolError: If the delegation value is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosInsertToolError(
            "onBehalfOfContentOwner must be a non-empty string",
            details={"field": "onBehalfOfContentOwner"},
        )
    return value.strip()


def validate_videos_insert_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_insert`` creation arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized part, body, media, upload mode, notification, and delegation values.
    :raises VideosInsertToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosInsertToolError("videos_insert arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_INSERT_ALLOWED_FIELDS:
            raise VideosInsertToolError(f"unsupported field for videos_insert: {field}", details={"field": field})

    part = _require_videos_insert_text_field(arguments, "part")
    if not _split_parts(part):
        raise VideosInsertToolError("part must include at least one requested resource part", details={"field": "part"})

    normalized: dict[str, Any] = {
        "part": part,
        "body": _validate_videos_insert_body(arguments.get("body")),
        "media": _validate_videos_insert_media(arguments.get("media")),
    }
    if "uploadMode" in arguments:
        normalized["uploadMode"] = _validate_videos_insert_upload_mode(arguments["uploadMode"])
    if "notifySubscribers" in arguments:
        normalized["notifySubscribers"] = _validate_videos_insert_notify_subscribers(arguments["notifySubscribers"])
    if "onBehalfOfContentOwner" in arguments:
        normalized["onBehalfOfContentOwner"] = _validate_videos_insert_delegation(
            arguments["onBehalfOfContentOwner"]
        )
    return normalized


def _require_videos_update_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty ``videos_update`` text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideosUpdateToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosUpdateToolError(f"videos_update requires non-empty {field}", details={"field": field})
    return value.strip()


def _validate_videos_update_part(arguments: dict[str, Any]) -> str:
    """Validate the supported writable update part.

    :param arguments: Caller-provided arguments.
    :return: Normalized ``part`` selection.
    :raises VideosUpdateToolError: If the part is missing or unsupported.
    """
    part = _require_videos_update_text_field(arguments, "part")
    if _split_parts(part) != list(VIDEOS_UPDATE_WRITABLE_PARTS):
        raise VideosUpdateToolError(
            "videos_update supports only part=snippet in this slice",
            details={"field": "part", "allowed": list(VIDEOS_UPDATE_WRITABLE_PARTS)},
        )
    return part


def _validate_videos_update_body(body: Any) -> dict[str, Any]:
    """Validate and normalize the supported video update body.

    :param body: Candidate update body.
    :return: Body accepted by the Layer 1 update wrapper.
    :raises VideosUpdateToolError: If the body is missing, malformed, or out of scope.
    """
    if not isinstance(body, dict):
        raise VideosUpdateToolError("videos_update requires body metadata", details={"field": "body"})
    for field in body:
        if field not in VIDEOS_UPDATE_ALLOWED_BODY_FIELDS:
            raise VideosUpdateToolError(
                f"unsupported body field for videos_update: {field}",
                details={"field": f"body.{field}"},
            )

    video_id = body.get("id")
    if not isinstance(video_id, str) or not video_id.strip():
        raise VideosUpdateToolError("videos_update requires body.id", details={"field": "body.id"})

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise VideosUpdateToolError("videos_update requires body.snippet metadata", details={"field": "body.snippet"})
    for field in snippet:
        if field not in VIDEOS_UPDATE_ALLOWED_SNIPPET_FIELDS:
            raise VideosUpdateToolError(
                f"unsupported body.snippet field for videos_update: {field}",
                details={"field": f"body.snippet.{field}"},
            )

    title = snippet.get("title")
    if not isinstance(title, str) or not title.strip():
        raise VideosUpdateToolError(
            "videos_update requires body.snippet.title",
            details={"field": "body.snippet.title"},
        )

    normalized: dict[str, Any] = {"id": video_id.strip(), "snippet": {"title": title.strip()}}
    if "kind" in body:
        kind = body["kind"]
        if not isinstance(kind, str) or not kind.strip():
            raise VideosUpdateToolError("body.kind must be a non-empty string", details={"field": "body.kind"})
        normalized["kind"] = kind.strip()
    return normalized


def _validate_videos_update_delegation(value: Any) -> str:
    """Validate optional content-owner delegation context.

    :param value: Candidate content-owner identifier.
    :return: Stripped content-owner identifier.
    :raises VideosUpdateToolError: If the delegation value is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosUpdateToolError(
            "onBehalfOfContentOwner must be a non-empty string",
            details={"field": "onBehalfOfContentOwner"},
        )
    return value.strip()


def validate_videos_update_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_update`` metadata-update arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized part, body, and optional delegation values.
    :raises VideosUpdateToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosUpdateToolError("videos_update arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_UPDATE_ALLOWED_FIELDS:
            raise VideosUpdateToolError(f"unsupported field for videos_update: {field}", details={"field": field})

    normalized: dict[str, Any] = {
        "part": _validate_videos_update_part(arguments),
        "body": _validate_videos_update_body(arguments.get("body")),
    }
    if "onBehalfOfContentOwner" in arguments:
        normalized["onBehalfOfContentOwner"] = _validate_videos_update_delegation(
            arguments["onBehalfOfContentOwner"]
        )
    return normalized


def _require_videos_rate_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty ``videos_rate`` text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideosRateToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosRateToolError(f"videos_rate requires non-empty {field}", details={"field": field})
    return value.strip()


def _validate_videos_rate_id(arguments: dict[str, Any]) -> str:
    """Validate the target video identity for a rating mutation.

    :param arguments: Caller-provided arguments.
    :return: Normalized video identifier.
    :raises VideosRateToolError: If the identity is missing, ambiguous, or malformed.
    """
    video_id = _require_videos_rate_text_field(arguments, "id")
    if "," in video_id or len(_split_ids(video_id)) != 1:
        raise VideosRateToolError("videos_rate requires exactly one id", details={"field": "id"})
    return video_id


def _validate_videos_rate_value(arguments: dict[str, Any]) -> str:
    """Validate the requested rating action.

    :param arguments: Caller-provided arguments.
    :return: Supported rating value.
    :raises VideosRateToolError: If the rating value is missing or unsupported.
    """
    rating = _require_videos_rate_text_field(arguments, "rating")
    if rating not in VIDEOS_RATE_VALUES:
        raise VideosRateToolError(
            "rating must be like, dislike, or none",
            details={"field": "rating", "allowed": list(VIDEOS_RATE_VALUES)},
        )
    return rating


def validate_videos_rate_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_rate`` rating arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized video id and requested rating value.
    :raises VideosRateToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosRateToolError("videos_rate arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_RATE_ALLOWED_FIELDS:
            raise VideosRateToolError(f"unsupported field for videos_rate: {field}", details={"field": field})
    return {"id": _validate_videos_rate_id(arguments), "rating": _validate_videos_rate_value(arguments)}


def _require_videos_get_rating_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty ``videos_getRating`` text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideosGetRatingToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosGetRatingToolError(
            f"videos_getRating requires non-empty {field}",
            details={"field": field},
        )
    return value.strip()


def _validate_videos_get_rating_ids(arguments: dict[str, Any]) -> str:
    """Validate the requested video identifiers for rating lookup.

    :param arguments: Caller-provided arguments.
    :return: Normalized comma-separated video identifiers.
    :raises VideosGetRatingToolError: If identifiers are missing, duplicated, or out of bounds.
    """
    raw_ids = _require_videos_get_rating_text_field(arguments, "id")
    ids = [item.strip() for item in raw_ids.split(",")]
    if not ids or any(not item for item in ids):
        raise VideosGetRatingToolError(
            "id must include one to fifty non-empty video identifiers",
            details={"field": "id"},
        )
    if len(ids) > 50:
        raise VideosGetRatingToolError(
            "id supports at most fifty video identifiers",
            details={"field": "id", "maximum": 50},
        )
    if len(set(ids)) != len(ids):
        raise VideosGetRatingToolError(
            "id must not include duplicate video identifiers",
            details={"field": "id"},
        )
    return ",".join(ids)


def _validate_videos_get_rating_delegation(value: Any) -> str:
    """Validate optional content-owner delegation context.

    :param value: Candidate content-owner identifier.
    :return: Stripped content-owner identifier.
    :raises VideosGetRatingToolError: If the delegation value is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideosGetRatingToolError(
            "onBehalfOfContentOwner must be a non-empty string",
            details={"field": "onBehalfOfContentOwner"},
        )
    return value.strip()


def validate_videos_get_rating_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_getRating`` current-rating lookup arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized id list and optional delegation value.
    :raises VideosGetRatingToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosGetRatingToolError("videos_getRating arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_GET_RATING_ALLOWED_FIELDS:
            raise VideosGetRatingToolError(
                f"unsupported field for videos_getRating: {field}",
                details={"field": field},
            )

    normalized: dict[str, Any] = {"id": _validate_videos_get_rating_ids(arguments)}
    if "onBehalfOfContentOwner" in arguments:
        normalized["onBehalfOfContentOwner"] = _validate_videos_get_rating_delegation(
            arguments["onBehalfOfContentOwner"]
        )
    return normalized


def _require_videos_report_abuse_body(arguments: dict[str, Any]) -> dict[str, Any]:
    """Require the report-abuse request body object.

    :param arguments: Caller-provided arguments.
    :return: Candidate report-abuse request body.
    :raises VideosReportAbuseToolError: If the body is missing or malformed.
    """
    body = arguments.get("body")
    if not isinstance(body, dict):
        raise VideosReportAbuseToolError("videos_reportAbuse requires body", details={"field": "body"})
    return body


def _validate_videos_report_abuse_body_text_field(body: dict[str, Any], field: str) -> str:
    """Validate one non-empty report-abuse body text field.

    :param body: Caller-provided report body.
    :param field: Body field name to validate.
    :return: Stripped field value.
    :raises VideosReportAbuseToolError: If the field is missing or invalid.
    """
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideosReportAbuseToolError(
            f"videos_reportAbuse requires non-empty body.{field}",
            details={"field": f"body.{field}"},
        )
    return value.strip()


def validate_videos_report_abuse_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate ``videos_reportAbuse`` abuse-report arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized report body accepted by the Layer 1 wrapper.
    :raises VideosReportAbuseToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideosReportAbuseToolError("videos_reportAbuse arguments must be an object")
    for field in arguments:
        if field not in VIDEOS_REPORT_ABUSE_ALLOWED_FIELDS:
            raise VideosReportAbuseToolError(
                f"unsupported field for videos_reportAbuse: {field}",
                details={"field": field},
            )

    body = _require_videos_report_abuse_body(arguments)
    for field in body:
        if field not in VIDEOS_REPORT_ABUSE_BODY_FIELDS:
            raise VideosReportAbuseToolError(
                f"unsupported body field for videos_reportAbuse: {field}",
                details={"field": f"body.{field}"},
            )

    normalized_body = {
        "videoId": _validate_videos_report_abuse_body_text_field(body, "videoId"),
        "reasonId": _validate_videos_report_abuse_body_text_field(body, "reasonId"),
    }
    for field in ("secondaryReasonId", "comments", "language"):
        if field in body:
            normalized_body[field] = _validate_videos_report_abuse_body_text_field(body, field)
    return {"body": normalized_body}


def _videos_insert_upload_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe upload context without raw media content.

    :param arguments: Normalized insert arguments.
    :return: Safe media upload context for result payloads.
    """
    media = arguments["media"]
    return {
        "mode": arguments.get("uploadMode") or "multipart",
        "mimeType": media["mimeType"],
        "contentProvided": bool(media.get("content")),
    }


def _videos_insert_availability_context() -> dict[str, Any]:
    """Build public availability context for upload-constrained video creation.

    :return: Safe availability state and caveats for callers.
    """
    return {
        "state": "media_constrained",
        "caveats": [
            "New uploads may be audit-constrained or private by default depending on account and release state."
        ],
    }


def _videos_insert_delegation_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Build safe delegation context when a content-owner identifier is supplied.

    :param arguments: Normalized insert arguments.
    :return: Delegation context or an empty mapping.
    """
    if "onBehalfOfContentOwner" not in arguments:
        return {}
    return {"onBehalfOfContentOwner": arguments["onBehalfOfContentOwner"]}


def _videos_update_body_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe update-body context for public results.

    :param arguments: Normalized update arguments.
    :return: Safe target and writable-field context.
    """
    body = arguments["body"]
    snippet = body["snippet"]
    return {
        "videoId": body["id"],
        "bodyFields": [field for field in body if field != "kind"],
        "snippetFields": list(snippet.keys()),
    }


def _videos_update_delegation_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Build safe delegation context when a content-owner identifier is supplied.

    :param arguments: Normalized update arguments.
    :return: Delegation context or an empty mapping.
    """
    if "onBehalfOfContentOwner" not in arguments:
        return {}
    return {"onBehalfOfContentOwner": arguments["onBehalfOfContentOwner"]}


def _videos_rate_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe target and requested-rating context.

    :param arguments: Normalized rating arguments.
    :return: Public rating context for result payloads.
    """
    context: dict[str, Any] = {"videoId": arguments["id"], "requestedRating": arguments["rating"]}
    if arguments["rating"] == "none":
        context["clearsRating"] = True
    return context


def _videos_get_rating_delegation_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Build safe delegation context when a content-owner identifier is supplied.

    :param arguments: Normalized rating lookup arguments.
    :return: Delegation context or an empty mapping.
    """
    if "onBehalfOfContentOwner" not in arguments:
        return {}
    return {"onBehalfOfContentOwner": arguments["onBehalfOfContentOwner"]}


def _videos_get_rating_item(item: dict[str, Any], fallback_video_id: str | None) -> dict[str, Any]:
    """Map one rating lookup item to the public per-video shape.

    :param item: Sanitized upstream rating item.
    :param fallback_video_id: Requested id to use when the upstream item omits an id.
    :return: Safe per-video rating outcome.
    """
    video_id = item.get("videoId") or item.get("id") or fallback_video_id
    rating = item.get("rating")
    if rating not in VIDEOS_GET_RATING_VALUES:
        rating = "unspecified"
    return {
        "videoId": video_id,
        "rating": rating,
        "isRated": rating in {"like", "dislike"},
        "isUnrated": rating in {"none", "unspecified"},
    }


def _videos_report_abuse_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe report context without exposing sensitive comment text.

    :param arguments: Normalized report-abuse arguments.
    :return: Public report context for acknowledgment results.
    """
    body = arguments["body"]
    context: dict[str, Any] = {
        "videoId": body["videoId"],
        "reasonId": body["reasonId"],
        "hasSecondaryReason": "secondaryReasonId" in body,
        "hasComments": "comments" in body,
    }
    if "language" in body:
        context["language"] = body["language"]
    return context


def map_videos_insert_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream video-create payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video-create payload.
    :param arguments: Caller arguments used for the request.
    :return: Near-raw created video result with safe operation context.
    """
    normalized = validate_videos_insert_arguments(arguments)
    safe_payload = sanitize_error_details(payload if isinstance(payload, dict) else {})
    item = safe_payload.get("item") if isinstance(safe_payload.get("item"), dict) else safe_payload
    result = {
        "endpoint": "videos.insert",
        "quotaCost": VIDEOS_INSERT_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "upload": _videos_insert_upload_context(normalized),
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "availability": _videos_insert_availability_context(),
        "item": item,
        "mutation": {"type": "created"},
    }
    delegation = _videos_insert_delegation_context(normalized)
    if delegation:
        result["delegation"] = delegation
    for field in (
        "kind",
        "etag",
        "id",
        "snippet",
        "status",
        "contentDetails",
        "processingDetails",
        "fileDetails",
        "suggestions",
        "localizations",
    ):
        if field in item:
            result[field] = item[field]
    return result


def map_videos_rate_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream video-rate no-content response to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video-rate payload, if any.
    :param arguments: Caller arguments used for the request.
    :return: Structured mutation acknowledgment with safe operation context.
    """
    normalized = validate_videos_rate_arguments(arguments)
    _safe_payload = sanitize_error_details(payload if isinstance(payload, dict) else {})
    return {
        "endpoint": "videos.rate",
        "quotaCost": VIDEOS_RATE_QUOTA_COST,
        "rating": _videos_rate_context(normalized),
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "availability": {"state": "active"},
        "mutation": {"type": "rated", "acknowledged": True},
        "status": {"code": 204, "body": "none"},
    }


def map_videos_get_rating_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream video-rating lookup payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video-rating lookup payload.
    :param arguments: Caller arguments used for the request.
    :return: Structured per-video rating lookup result with safe operation context.
    """
    normalized = validate_videos_get_rating_arguments(arguments)
    safe_payload = sanitize_error_details(payload if isinstance(payload, dict) else {})
    requested_ids = _split_ids(normalized["id"])
    raw_items = safe_payload.get("videoRatings")
    if not isinstance(raw_items, list):
        raw_items = safe_payload.get("items", [])
    if not isinstance(raw_items, list):
        raw_items = []
    items = [
        _videos_get_rating_item(item, requested_ids[index] if index < len(requested_ids) else None)
        for index, item in enumerate(raw_items)
        if isinstance(item, dict)
    ]
    result: dict[str, Any] = {
        "endpoint": "videos.getRating",
        "quotaCost": VIDEOS_GET_RATING_QUOTA_COST,
        "lookup": {"requestedIds": requested_ids, "resultCount": len(items)},
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "availability": {"state": "active"},
        "items": items,
    }
    delegation = _videos_get_rating_delegation_context(normalized)
    if delegation:
        result["delegation"] = delegation
    for field in ("kind", "etag"):
        if field in safe_payload:
            result[field] = safe_payload[field]
    return result


def map_videos_report_abuse_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream video-abuse-report no-content response to a public acknowledgment.

    :param payload: Upstream or Layer 1 report-abuse payload, if any.
    :param arguments: Caller arguments used for the request.
    :return: Structured report-abuse acknowledgment with safe operation context.
    """
    normalized = validate_videos_report_abuse_arguments(arguments)
    _safe_payload = sanitize_error_details(payload if isinstance(payload, dict) else {})
    return {
        "endpoint": "videos.reportAbuse",
        "quotaCost": VIDEOS_REPORT_ABUSE_QUOTA_COST,
        "report": _videos_report_abuse_context(normalized),
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "availability": {"state": "active"},
        "acknowledgment": {"accepted": True, "status": "submitted"},
        "status": {"code": 204, "body": "none"},
    }


def map_videos_update_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream video-update payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video-update payload.
    :param arguments: Caller arguments used for the request.
    :return: Near-raw updated video result with safe operation context.
    """
    normalized = validate_videos_update_arguments(arguments)
    safe_payload = sanitize_error_details(payload if isinstance(payload, dict) else {})
    item = safe_payload.get("item") if isinstance(safe_payload.get("item"), dict) else safe_payload
    result = {
        "endpoint": "videos.update",
        "quotaCost": VIDEOS_UPDATE_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "update": _videos_update_body_context(normalized),
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "item": item,
        "mutation": {"type": "updated"},
    }
    delegation = _videos_update_delegation_context(normalized)
    if delegation:
        result["delegation"] = delegation
    for field in (
        "kind",
        "etag",
        "id",
        "snippet",
        "status",
        "contentDetails",
        "processingDetails",
        "fileDetails",
        "suggestions",
        "localizations",
    ):
        if field in item:
            result[field] = item[field]
    return result


def _selector_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Build safe selector context for public result payloads.

    :param arguments: Normalized caller arguments.
    :return: Selector context preserving caller lookup intent.
    """
    if "id" in arguments:
        return {"mode": "id", "id": _split_ids(arguments["id"])}
    if "chart" in arguments:
        return {"mode": "chart", "chart": arguments["chart"]}
    return {"mode": "myRating", "myRating": arguments["myRating"]}


def _pagination_context(arguments: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Build safe pagination context from arguments and upstream payload.

    :param arguments: Normalized caller arguments.
    :param payload: Upstream or Layer 1 payload.
    :return: Pagination fields relevant to the request and response.
    """
    pagination = {}
    for field in ("pageToken", "maxResults"):
        if field in arguments:
            pagination[field] = arguments[field]
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            pagination[field] = payload[field]
    return pagination


def _chart_refinement_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Build chart refinement context from normalized arguments.

    :param arguments: Normalized caller arguments.
    :return: Chart refinement fields supplied by the caller.
    """
    return {field: arguments[field] for field in VIDEOS_LIST_CHART_REFINEMENTS if field in arguments}


def _auth_result_context(auth_mode: str) -> dict[str, str]:
    """Build public auth context for a mapped result.

    :param auth_mode: Auth mode used for execution.
    :return: Safe auth context for callers.
    """
    if auth_mode == "oauth_required":
        return {"mode": "oauth_required", "path": "restricted"}
    return {"mode": "api_key", "path": "public"}


def map_videos_list_result(
    payload: dict[str, Any],
    arguments: dict[str, Any],
    *,
    auth_mode: str = "api_key",
) -> dict[str, Any]:
    """Map an upstream video-list payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video list payload.
    :param arguments: Caller arguments used for the request.
    :param auth_mode: Public auth mode used for execution.
    :return: Near-raw video list result with safe operation context.
    """
    normalized = validate_videos_list_arguments(arguments)
    safe_payload = payload if isinstance(payload, dict) else {}
    items = safe_payload.get("items", [])
    result = {
        "endpoint": "videos.list",
        "quotaCost": VIDEOS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": _selector_context(normalized),
        "auth": _auth_result_context(auth_mode),
        "availability": {"state": "active"},
        "items": items,
        "empty": not bool(items),
    }
    pagination = _pagination_context(normalized, safe_payload)
    if pagination:
        result["pagination"] = pagination
    chart_refinement = _chart_refinement_context(normalized)
    if chart_refinement:
        result["chartRefinement"] = chart_refinement
    for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
        if field in safe_payload:
            result[field] = safe_payload[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> VideosListToolError:
    """Map a normalized upstream failure to a safe ``videos_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosListToolError(str(error), category=category, details=error.details or {})


def _api_key_auth_context(api_key: str | None) -> AuthContext:
    """Build the Layer 1 API-key auth context.

    :param api_key: API key credential value.
    :return: Layer 1 auth context for API-key execution.
    :raises VideosListToolError: If API-key access is missing.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise VideosListToolError(
            "videos_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        )
    try:
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))
    except ValueError as exc:
        raise VideosListToolError(
            "videos_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        ) from exc


def _oauth_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth execution.
    :raises VideosListToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosListToolError(
            "videos_list requires OAuth access for myRating",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosListToolError(
            "videos_list requires OAuth access for myRating",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _auth_context_for_selector(
    normalized_arguments: dict[str, Any],
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> tuple[AuthContext, str]:
    """Select Layer 1 auth based on the normalized selector.

    :param normalized_arguments: Validated caller arguments.
    :param api_key: API-key credential value.
    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context and public auth mode label.
    """
    if "myRating" in normalized_arguments:
        return _oauth_auth_context(oauth_token), "oauth_required"
    return _api_key_auth_context(api_key), "api_key"


def build_videos_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "selector",
            "pagination",
            "chartRefinement",
            "auth",
            "availability",
            "items",
            "empty",
            "kind",
            "etag",
            "pageInfo",
            "nextPageToken",
            "prevPageToken",
            "id",
            "snippet",
            "contentDetails",
            "statistics",
            "status",
            "player",
            "recordingDetails",
            "fileDetails",
            "processingDetails",
            "suggestions",
            "liveStreamingDetails",
            "topicDetails",
            "localizations",
        ),
        preserved_upstream_fields=(
            "kind",
            "etag",
            "id",
            "snippet",
            "contentDetails",
            "statistics",
            "status",
            "player",
            "recordingDetails",
            "fileDetails",
            "processingDetails",
            "suggestions",
            "liveStreamingDetails",
            "topicDetails",
            "localizations",
            "items",
            "pageInfo",
            "nextPageToken",
            "prevPageToken",
        ),
        disallowed_behavior=(
            "video_search",
            "video_upload",
            "media_upload",
            "video_update",
            "metadata_update",
            "video_delete",
            "rating_mutation",
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
        tool_name=VIDEOS_LIST_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="list",
        operation_key="videos.list",
        description=VIDEOS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=VIDEOS_LIST_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "selectorFields": list(VIDEOS_LIST_SELECTORS),
            "paginationFields": ["pageToken", "maxResults"],
            "chartRefinementFields": list(VIDEOS_LIST_CHART_REFINEMENTS),
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEOS_LIST_USAGE_NOTES,
        caveats=VIDEOS_LIST_CAVEATS,
    )


def _videos_insert_disallowed_behavior() -> tuple[str, ...]:
    """Return behaviors outside the low-level ``videos_insert`` endpoint boundary.

    :return: Stable disallowed-behavior identifiers for metadata.
    """
    return (
        "automatic_publishing",
        "metadata_update",
        "video_delete",
        "rating_mutation",
        "thumbnail_management",
        "caption_management",
        "playlist_management",
        "comment_management",
        "transcript_retrieval",
        "analytics",
        "recommendation",
        "ranking",
        "summarization",
        "enrichment",
        "cross_endpoint_aggregation",
    )


def build_videos_insert_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_insert``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "upload",
            "auth",
            "availability",
            "delegation",
            "item",
            "mutation",
            "kind",
            "etag",
            "id",
            "snippet",
            "status",
            "contentDetails",
            "processingDetails",
            "fileDetails",
            "suggestions",
            "localizations",
        ),
        preserved_upstream_fields=(
            "kind",
            "etag",
            "id",
            "snippet",
            "status",
            "contentDetails",
            "processingDetails",
            "fileDetails",
            "suggestions",
            "localizations",
        ),
        disallowed_behavior=_videos_insert_disallowed_behavior(),
    )
    return YouTubeToolContract(
        tool_name=VIDEOS_INSERT_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="insert",
        operation_key="videos.insert",
        description=VIDEOS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=VIDEOS_INSERT_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "upload_result",
            "resourcePath": "item",
            "authMode": "oauth_required",
            "requiredFields": ["part", "body", "media"],
            "optionalFields": ["uploadMode", "notifySubscribers", "onBehalfOfContentOwner"],
            "mediaFields": ["media"],
            "delegationFields": ["onBehalfOfContentOwner"],
            "availabilityState": "media_constrained",
            "mutation": "created",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
        usage_notes=VIDEOS_INSERT_USAGE_NOTES,
        caveats=VIDEOS_INSERT_CAVEATS,
    )


def _videos_update_disallowed_behavior() -> tuple[str, ...]:
    """Return behaviors outside the low-level ``videos_update`` endpoint boundary.

    :return: Stable disallowed-behavior identifiers for metadata.
    """
    return (
        "media_upload",
        "media_replacement",
        "transcoding",
        "automatic_publishing",
        "video_creation",
        "video_delete",
        "rating_mutation",
        "thumbnail_management",
        "caption_management",
        "playlist_management",
        "comment_management",
        "transcript_retrieval",
        "analytics",
        "recommendation",
        "ranking",
        "summarization",
        "enrichment",
        "cross_endpoint_aggregation",
    )


def build_videos_update_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_update``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "update",
            "auth",
            "delegation",
            "item",
            "mutation",
            "kind",
            "etag",
            "id",
            "snippet",
            "status",
            "contentDetails",
            "processingDetails",
            "fileDetails",
            "suggestions",
            "localizations",
        ),
        preserved_upstream_fields=(
            "kind",
            "etag",
            "id",
            "snippet",
            "status",
            "contentDetails",
            "processingDetails",
            "fileDetails",
            "suggestions",
            "localizations",
        ),
        disallowed_behavior=_videos_update_disallowed_behavior(),
    )
    return YouTubeToolContract(
        tool_name=VIDEOS_UPDATE_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="update",
        operation_key="videos.update",
        description=VIDEOS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=VIDEOS_UPDATE_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "authMode": "oauth_required",
            "requiredFields": ["part", "body"],
            "optionalFields": ["onBehalfOfContentOwner"],
            "writableParts": list(VIDEOS_UPDATE_WRITABLE_PARTS),
            "bodyFields": ["id", "snippet"],
            "snippetFields": ["title"],
            "delegationFields": ["onBehalfOfContentOwner"],
            "replacementSemantics": True,
            "mutation": "updated",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEOS_UPDATE_USAGE_NOTES,
        caveats=VIDEOS_UPDATE_CAVEATS,
    )


def _videos_rate_disallowed_behavior() -> tuple[str, ...]:
    """Return behaviors outside the low-level ``videos_rate`` endpoint boundary.

    :return: Stable disallowed-behavior identifiers for metadata.
    """
    return (
        "current_rating_lookup",
        "rating_history",
        "rating_counts",
        "video_lookup",
        "media_upload",
        "video_update",
        "metadata_update",
        "video_delete",
        "abuse_reporting",
        "thumbnail_management",
        "caption_management",
        "playlist_management",
        "comment_management",
        "transcript_retrieval",
        "analytics",
        "recommendation",
        "ranking",
        "summarization",
        "enrichment",
        "cross_endpoint_aggregation",
    )


def build_videos_rate_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_rate``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "rating",
            "auth",
            "availability",
            "mutation",
            "status",
        ),
        preserved_upstream_fields=(),
        disallowed_behavior=_videos_rate_disallowed_behavior(),
    )
    return YouTubeToolContract(
        tool_name=VIDEOS_RATE_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="rate",
        operation_key="videos.rate",
        description=VIDEOS_RATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=VIDEOS_RATE_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_RATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "mutation_acknowledgment",
            "mutation": "rated",
            "authMode": "oauth_required",
            "requiredFields": ["id", "rating"],
            "ratingValues": list(VIDEOS_RATE_VALUES),
            "clearRatingValue": "none",
            "requestBody": "none",
            "successStatus": 204,
            "statusBody": "none",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEOS_RATE_USAGE_NOTES,
        caveats=VIDEOS_RATE_CAVEATS,
    )


def _videos_get_rating_disallowed_behavior() -> tuple[str, ...]:
    """Return behaviors outside the low-level ``videos_getRating`` endpoint boundary.

    :return: Stable disallowed-behavior identifiers for metadata.
    """
    return (
        "rating_mutation",
        "rating_history",
        "aggregate_rating_counts",
        "metadata_lookup",
        "metadata_update",
        "media_upload",
        "media_replacement",
        "transcoding",
        "automatic_publishing",
        "video_creation",
        "video_update",
        "video_delete",
        "abuse_reporting",
        "thumbnail_management",
        "caption_management",
        "playlist_management",
        "comment_management",
        "transcript_retrieval",
        "analytics",
        "recommendation",
        "ranking",
        "summarization",
        "enrichment",
        "cross_endpoint_aggregation",
    )


def build_videos_get_rating_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_getRating``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "lookup",
            "auth",
            "availability",
            "delegation",
            "items",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "items[].videoId", "items[].rating"),
        disallowed_behavior=_videos_get_rating_disallowed_behavior(),
    )
    return YouTubeToolContract(
        tool_name=VIDEOS_GET_RATING_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="getRating",
        operation_key="videos.getRating",
        description=VIDEOS_GET_RATING_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=VIDEOS_GET_RATING_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_GET_RATING_INPUT_SCHEMA,
        response_convention={
            "resultKind": "rating_lookup",
            "resourcePath": "items",
            "authMode": "oauth_required",
            "requiredFields": ["id"],
            "optionalFields": ["onBehalfOfContentOwner"],
            "ratingValues": list(VIDEOS_GET_RATING_VALUES),
            "identifierLimit": 50,
            "requestBody": "none",
            "successBody": "videoGetRatingResponse",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEOS_GET_RATING_USAGE_NOTES,
        caveats=VIDEOS_GET_RATING_CAVEATS,
    )


def _videos_report_abuse_disallowed_behavior() -> tuple[str, ...]:
    """Return behaviors outside the low-level ``videos_reportAbuse`` endpoint boundary.

    :return: Stable disallowed-behavior identifiers for metadata.
    """
    return (
        "abuse_reason_discovery",
        "abuse_classification",
        "evidence_collection",
        "moderation_decision",
        "metadata_lookup",
        "metadata_update",
        "rating_lookup",
        "rating_mutation",
        "media_upload",
        "media_replacement",
        "transcoding",
        "automatic_publishing",
        "video_creation",
        "video_update",
        "video_delete",
        "thumbnail_management",
        "caption_management",
        "playlist_management",
        "comment_management",
        "transcript_retrieval",
        "analytics",
        "recommendation",
        "ranking",
        "summarization",
        "enrichment",
        "cross_endpoint_aggregation",
    )


def build_videos_report_abuse_contract() -> YouTubeToolContract:
    """Build the public contract for ``videos_reportAbuse``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "report",
            "auth",
            "availability",
            "acknowledgment",
            "status",
        ),
        preserved_upstream_fields=(),
        disallowed_behavior=_videos_report_abuse_disallowed_behavior(),
    )
    return YouTubeToolContract(
        tool_name=VIDEOS_REPORT_ABUSE_TOOL_NAME,
        upstream_resource="videos",
        upstream_method="reportAbuse",
        operation_key="videos.reportAbuse",
        description=VIDEOS_REPORT_ABUSE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=VIDEOS_REPORT_ABUSE_QUOTA_COST,
        resource_family="videos",
        input_contract=VIDEOS_REPORT_ABUSE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "mutation_acknowledgment",
            "mutation": "reported_abuse",
            "authMode": "oauth_required",
            "requiredFields": ["body.videoId", "body.reasonId"],
            "optionalFields": ["body.secondaryReasonId", "body.comments", "body.language"],
            "requestBody": "required",
            "successStatus": 204,
            "statusBody": "none",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEOS_REPORT_ABUSE_USAGE_NOTES,
        caveats=VIDEOS_REPORT_ABUSE_CAVEATS,
    )


def _default_videos_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video-list calls.

    :return: Integration executor returning representative video data.
    """

    def transport(_execution):
        """Return a representative video list response.

        :param _execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#videoListResponse",
            "items": [
                {
                    "kind": "youtube#video",
                    "id": "abc123",
                    "snippet": {"title": "Example video"},
                }
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_videos_insert_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video-insert calls.

    :return: Integration executor returning representative created-video data.
    """

    def transport(execution):
        """Return a representative video-create response.

        :param execution: Request execution context.
        :return: Fake upstream created-video response for local invocation.
        """
        body = execution.arguments.get("body")
        body = body if isinstance(body, dict) else {}
        snippet = body.get("snippet") if isinstance(body.get("snippet"), dict) else {}
        status = body.get("status") if isinstance(body.get("status"), dict) else {}
        return {
            "kind": "youtube#video",
            "etag": "etag-video-insert",
            "id": "local-video-upload",
            "snippet": {
                "title": snippet.get("title") or "Example upload",
            },
            "status": {
                "privacyStatus": status.get("privacyStatus") or "private",
            },
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_videos_update_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video-update calls.

    :return: Integration executor returning representative updated-video data.
    """

    def transport(execution):
        """Return a representative video-update response.

        :param execution: Request execution context.
        :return: Fake upstream updated-video response for local invocation.
        """
        body = execution.arguments.get("body")
        body = body if isinstance(body, dict) else {}
        snippet = body.get("snippet") if isinstance(body.get("snippet"), dict) else {}
        return {
            "kind": "youtube#video",
            "etag": "etag-video-update",
            "id": body.get("id") or "local-video-update",
            "snippet": {"title": snippet.get("title") or "Updated title"},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_videos_rate_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video-rate calls.

    :return: Integration executor returning a representative no-content acknowledgment payload.
    """

    def transport(_execution):
        """Return a representative empty video-rate response.

        :param _execution: Request execution context.
        :return: Empty fake upstream rating response for local invocation.
        """
        return {}

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_videos_get_rating_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video-rating lookup calls.

    :return: Integration executor returning representative per-video rating data.
    """

    def transport(execution):
        """Return a representative video-rating lookup response.

        :param execution: Request execution context.
        :return: Fake upstream getRating response for local invocation.
        """
        requested_ids = _split_ids(str(execution.arguments.get("id", "")))
        ratings = ("like", "none")
        return {
            "kind": "youtube#videoGetRatingResponse",
            "etag": "etag-video-get-rating",
            "items": [
                {"videoId": video_id, "rating": ratings[index] if index < len(ratings) else "none"}
                for index, video_id in enumerate(requested_ids)
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_videos_report_abuse_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default video abuse-report calls.

    :return: Integration executor returning a representative no-content acknowledgment payload.
    """

    def transport(_execution):
        """Return a representative empty report-abuse response.

        :param _execution: Request execution context.
        :return: Empty fake upstream report-abuse response for local invocation.
        """
        return {}

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _videos_insert_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context for ``videos_insert``.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth-required upload execution.
    :raises VideosInsertToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosInsertToolError(
            "videos_insert requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosInsertToolError(
            "videos_insert requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _videos_update_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context for ``videos_update``.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth-required update execution.
    :raises VideosUpdateToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosUpdateToolError(
            "videos_update requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosUpdateToolError(
            "videos_update requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _videos_rate_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context for ``videos_rate``.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth-required rating execution.
    :raises VideosRateToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosRateToolError(
            "videos_rate requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosRateToolError(
            "videos_rate requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _videos_get_rating_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context for ``videos_getRating``.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth-required rating lookup execution.
    :raises VideosGetRatingToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosGetRatingToolError(
            "videos_getRating requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosGetRatingToolError(
            "videos_getRating requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _videos_report_abuse_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 OAuth auth context for ``videos_reportAbuse``.

    :param oauth_token: OAuth token credential value.
    :return: Layer 1 auth context for OAuth-required abuse-report execution.
    :raises VideosReportAbuseToolError: If OAuth access is missing.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise VideosReportAbuseToolError(
            "videos_reportAbuse requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        )
    try:
        return AuthContext(
            mode=Layer1AuthMode.OAUTH_REQUIRED,
            credentials=CredentialBundle(oauth_token=oauth_token.strip()),
        )
    except ValueError as exc:
        raise VideosReportAbuseToolError(
            "videos_reportAbuse requires OAuth authorization",
            category="authentication_failed",
            details={"authMode": "oauth_required"},
        ) from exc


def _map_videos_insert_upstream_error(error: NormalizedUpstreamError) -> VideosInsertToolError:
    """Map a normalized upstream failure to a safe ``videos_insert`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "upload_rejected": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosInsertToolError(str(error), category=category, details=error.details or {})


def _map_videos_update_upstream_error(error: NormalizedUpstreamError) -> VideosUpdateToolError:
    """Map a normalized upstream failure to a safe ``videos_update`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosUpdateToolError(str(error), category=category, details=error.details or {})


def _map_videos_rate_upstream_error(error: NormalizedUpstreamError) -> VideosRateToolError:
    """Map a normalized upstream failure to a safe ``videos_rate`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "invalid_rating": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "disabled_rating": "authorization_failed",
        "purchase_required": "authorization_failed",
        "unverified_email": "authorization_failed",
        "non_ratable": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosRateToolError(str(error), category=category, details=error.details or {})


def _map_videos_get_rating_upstream_error(error: NormalizedUpstreamError) -> VideosGetRatingToolError:
    """Map a normalized upstream failure to a safe ``videos_getRating`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosGetRatingToolError(str(error), category=category, details=error.details or {})


def _map_videos_report_abuse_upstream_error(error: NormalizedUpstreamError) -> VideosReportAbuseToolError:
    """Map a normalized upstream failure to a safe ``videos_reportAbuse`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "invalid_reason": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "refused": "authorization_failed",
        "duplicate_report": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideosReportAbuseToolError(str(error), category=category, details=error.details or {})


def build_videos_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for video creation.
    :return: Callable that validates, executes, and maps video-create requests.
    """
    selected_wrapper = wrapper or build_videos_insert_wrapper()
    selected_executor = executor or _default_videos_insert_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_insert`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video-create result.
        :raises VideosInsertToolError: If validation, access, or execution fails.
        """
        normalized = validate_videos_insert_arguments(arguments)
        auth_context = _videos_insert_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_videos_insert_upstream_error(exc) from exc
        except ValueError as exc:
            message = str(exc)
            category = "authentication_failed" if "oauth" in message.lower() else "invalid_request"
            raise VideosInsertToolError(
                message,
                category=category,
                details={"authMode": "oauth_required"} if category == "authentication_failed" else {"field": "request"},
            ) from exc
        return map_videos_insert_result(payload, normalized)

    return handler


def build_videos_rate_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_rate``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for video rating mutations.
    :return: Callable that validates, executes, and maps video-rating requests.
    """
    selected_wrapper = wrapper or build_videos_rate_wrapper()
    selected_executor = executor or _default_videos_rate_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_rate`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video-rate acknowledgment result.
        :raises VideosRateToolError: If validation, access, or execution fails.
        """
        normalized = validate_videos_rate_arguments(arguments)
        auth_context = _videos_rate_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_videos_rate_upstream_error(exc) from exc
        except ValueError as exc:
            message = str(exc)
            category = "authentication_failed" if "oauth" in message.lower() else "invalid_request"
            raise VideosRateToolError(
                message,
                category=category,
                details={"authMode": "oauth_required"} if category == "authentication_failed" else {"field": "request"},
            ) from exc
        return map_videos_rate_result(payload, normalized)

    return handler


def build_videos_get_rating_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_getRating``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for current-rating lookups.
    :return: Callable that validates, executes, and maps video-rating lookup requests.
    """
    selected_wrapper = wrapper or build_videos_get_rating_wrapper()
    selected_executor = executor or _default_videos_get_rating_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_getRating`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video-rating lookup result.
        :raises VideosGetRatingToolError: If validation, access, or execution fails.
        """
        normalized = validate_videos_get_rating_arguments(arguments)
        auth_context = _videos_get_rating_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_videos_get_rating_upstream_error(exc) from exc
        except ValueError as exc:
            message = str(exc)
            category = "authentication_failed" if "oauth" in message.lower() else "invalid_request"
            raise VideosGetRatingToolError(
                message,
                category=category,
                details={"authMode": "oauth_required"} if category == "authentication_failed" else {"field": "request"},
            ) from exc
        return map_videos_get_rating_result(payload, normalized)

    return handler


def build_videos_report_abuse_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_reportAbuse``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for abuse-report submission.
    :return: Callable that validates, executes, and maps abuse-report requests.
    """
    selected_wrapper = wrapper or build_videos_report_abuse_wrapper()
    selected_executor = executor or _default_videos_report_abuse_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_reportAbuse`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 abuse-report acknowledgment result.
        :raises VideosReportAbuseToolError: If validation, access, or execution fails.
        """
        normalized = validate_videos_report_abuse_arguments(arguments)
        auth_context = _videos_report_abuse_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_videos_report_abuse_upstream_error(exc) from exc
        except ValueError as exc:
            message = str(exc)
            category = "authentication_failed" if "oauth" in message.lower() else "invalid_request"
            raise VideosReportAbuseToolError(
                message,
                category=category,
                details={"authMode": "oauth_required"} if category == "authentication_failed" else {"field": "request"},
            ) from exc
        return map_videos_report_abuse_result(payload, normalized)

    return handler


def build_videos_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used for video metadata updates.
    :return: Callable that validates, executes, and maps video-update requests.
    """
    selected_wrapper = wrapper or build_videos_update_wrapper()
    selected_executor = executor or _default_videos_update_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_update`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video-update result.
        :raises VideosUpdateToolError: If validation, access, or execution fails.
        """
        normalized = validate_videos_update_arguments(arguments)
        auth_context = _videos_update_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_videos_update_upstream_error(exc) from exc
        except ValueError as exc:
            message = str(exc)
            category = "authentication_failed" if "oauth" in message.lower() else "invalid_request"
            raise VideosUpdateToolError(
                message,
                category=category,
                details={"authMode": "oauth_required"} if category == "authentication_failed" else {"field": "request"},
            ) from exc
        return map_videos_update_result(payload, normalized)

    return handler


def build_videos_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``videos_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used for direct and chart lookups.
    :param oauth_token: OAuth token value used for ``myRating`` lookups.
    :return: Callable that validates, executes, and maps video-list lookups.
    """
    selected_wrapper = wrapper or build_videos_list_wrapper()
    selected_executor = executor or _default_videos_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videos_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video list result.
        :raises VideosListToolError: If validation or execution fails.
        """
        normalized = validate_videos_list_arguments(arguments)
        auth_context, public_auth_mode = _auth_context_for_selector(
            normalized,
            api_key=api_key,
            oauth_token=oauth_token,
        )
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_upstream_error(exc) from exc
        except ValueError as exc:
            raise VideosListToolError(
                str(exc),
                category="authentication_failed",
                details={"authMode": public_auth_mode},
            ) from exc
        return map_videos_list_result(payload, normalized, auth_mode=public_auth_mode)

    return handler


def build_videos_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_LIST_CALLER_EXAMPLES)
    return {
        "name": VIDEOS_LIST_TOOL_NAME,
        "description": VIDEOS_LIST_DESCRIPTION,
        "inputSchema": VIDEOS_LIST_INPUT_SCHEMA,
        "handler": build_videos_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
        "metadata": metadata,
    }


def build_videos_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_insert``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_insert_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_INSERT_CALLER_EXAMPLES)
    return {
        "name": VIDEOS_INSERT_TOOL_NAME,
        "description": VIDEOS_INSERT_DESCRIPTION,
        "inputSchema": VIDEOS_INSERT_INPUT_SCHEMA,
        "handler": build_videos_insert_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_videos_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_update``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_update_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_UPDATE_CALLER_EXAMPLES)
    return {
        "name": VIDEOS_UPDATE_TOOL_NAME,
        "description": VIDEOS_UPDATE_DESCRIPTION,
        "inputSchema": VIDEOS_UPDATE_INPUT_SCHEMA,
        "handler": build_videos_update_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_videos_rate_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_rate``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_rate_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_RATE_CALLER_EXAMPLES)
    return {
        "name": VIDEOS_RATE_TOOL_NAME,
        "description": VIDEOS_RATE_DESCRIPTION,
        "inputSchema": VIDEOS_RATE_INPUT_SCHEMA,
        "handler": build_videos_rate_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_videos_get_rating_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_getRating``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_get_rating_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_GET_RATING_CALLER_EXAMPLES)
    return {
        "name": VIDEOS_GET_RATING_TOOL_NAME,
        "description": VIDEOS_GET_RATING_DESCRIPTION,
        "inputSchema": VIDEOS_GET_RATING_INPUT_SCHEMA,
        "handler": build_videos_get_rating_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_videos_report_abuse_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videos_reportAbuse``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_videos_report_abuse_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEOS_REPORT_ABUSE_CALLER_EXAMPLES)
    validation_input_schema = {
        **VIDEOS_REPORT_ABUSE_INPUT_SCHEMA,
        "properties": {
            **VIDEOS_REPORT_ABUSE_INPUT_SCHEMA["properties"],
            "body": {
                **VIDEOS_REPORT_ABUSE_INPUT_SCHEMA["properties"]["body"],
                "x-validateNestedSchema": True,
            },
        },
    }
    return {
        "name": VIDEOS_REPORT_ABUSE_TOOL_NAME,
        "description": VIDEOS_REPORT_ABUSE_DESCRIPTION,
        "inputSchema": VIDEOS_REPORT_ABUSE_INPUT_SCHEMA,
        "validationInputSchema": validation_input_schema,
        "handler": build_videos_report_abuse_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "VIDEOS_GET_RATING_ALLOWED_FIELDS",
    "VIDEOS_GET_RATING_CALLER_EXAMPLES",
    "VIDEOS_GET_RATING_CAVEATS",
    "VIDEOS_GET_RATING_DESCRIPTION",
    "VIDEOS_GET_RATING_INPUT_SCHEMA",
    "VIDEOS_GET_RATING_QUOTA_COST",
    "VIDEOS_GET_RATING_TOOL_NAME",
    "VIDEOS_GET_RATING_UNSAFE_DETAIL_KEYS",
    "VIDEOS_GET_RATING_USAGE_NOTES",
    "VIDEOS_GET_RATING_VALUES",
    "VIDEOS_INSERT_ALLOWED_FIELDS",
    "VIDEOS_INSERT_CALLER_EXAMPLES",
    "VIDEOS_INSERT_CAVEATS",
    "VIDEOS_INSERT_DESCRIPTION",
    "VIDEOS_INSERT_INPUT_SCHEMA",
    "VIDEOS_INSERT_QUOTA_COST",
    "VIDEOS_INSERT_TOOL_NAME",
    "VIDEOS_INSERT_UNSAFE_DETAIL_KEYS",
    "VIDEOS_INSERT_UPLOAD_MODES",
    "VIDEOS_INSERT_USAGE_NOTES",
    "VIDEOS_LIST_ALLOWED_FIELDS",
    "VIDEOS_LIST_CALLER_EXAMPLES",
    "VIDEOS_LIST_CAVEATS",
    "VIDEOS_LIST_CHART_REFINEMENTS",
    "VIDEOS_LIST_COLLECTION_SELECTORS",
    "VIDEOS_LIST_DESCRIPTION",
    "VIDEOS_LIST_INPUT_SCHEMA",
    "VIDEOS_LIST_QUOTA_COST",
    "VIDEOS_LIST_SELECTORS",
    "VIDEOS_LIST_TOOL_NAME",
    "VIDEOS_LIST_UNSAFE_DETAIL_KEYS",
    "VIDEOS_LIST_USAGE_NOTES",
    "VIDEOS_RATE_ALLOWED_FIELDS",
    "VIDEOS_RATE_CALLER_EXAMPLES",
    "VIDEOS_RATE_CAVEATS",
    "VIDEOS_RATE_DESCRIPTION",
    "VIDEOS_RATE_INPUT_SCHEMA",
    "VIDEOS_RATE_QUOTA_COST",
    "VIDEOS_RATE_TOOL_NAME",
    "VIDEOS_RATE_UNSAFE_DETAIL_KEYS",
    "VIDEOS_RATE_USAGE_NOTES",
    "VIDEOS_RATE_VALUES",
    "VIDEOS_REPORT_ABUSE_ALLOWED_FIELDS",
    "VIDEOS_REPORT_ABUSE_BODY_FIELDS",
    "VIDEOS_REPORT_ABUSE_CALLER_EXAMPLES",
    "VIDEOS_REPORT_ABUSE_CAVEATS",
    "VIDEOS_REPORT_ABUSE_DESCRIPTION",
    "VIDEOS_REPORT_ABUSE_INPUT_SCHEMA",
    "VIDEOS_REPORT_ABUSE_QUOTA_COST",
    "VIDEOS_REPORT_ABUSE_REQUIRED_BODY_FIELDS",
    "VIDEOS_REPORT_ABUSE_TOOL_NAME",
    "VIDEOS_REPORT_ABUSE_UNSAFE_DETAIL_KEYS",
    "VIDEOS_REPORT_ABUSE_USAGE_NOTES",
    "VIDEOS_UPDATE_ALLOWED_BODY_FIELDS",
    "VIDEOS_UPDATE_ALLOWED_FIELDS",
    "VIDEOS_UPDATE_ALLOWED_SNIPPET_FIELDS",
    "VIDEOS_UPDATE_CALLER_EXAMPLES",
    "VIDEOS_UPDATE_CAVEATS",
    "VIDEOS_UPDATE_DESCRIPTION",
    "VIDEOS_UPDATE_INPUT_SCHEMA",
    "VIDEOS_UPDATE_QUOTA_COST",
    "VIDEOS_UPDATE_TOOL_NAME",
    "VIDEOS_UPDATE_UNSAFE_DETAIL_KEYS",
    "VIDEOS_UPDATE_USAGE_NOTES",
    "VIDEOS_UPDATE_WRITABLE_PARTS",
    "VideosGetRatingToolError",
    "VideosInsertToolError",
    "VideosListToolError",
    "VideosRateToolError",
    "VideosReportAbuseToolError",
    "VideosUpdateToolError",
    "build_videos_insert_contract",
    "build_videos_insert_handler",
    "build_videos_insert_tool_descriptor",
    "build_videos_get_rating_contract",
    "build_videos_get_rating_handler",
    "build_videos_get_rating_tool_descriptor",
    "build_videos_list_contract",
    "build_videos_list_handler",
    "build_videos_list_tool_descriptor",
    "build_videos_rate_contract",
    "build_videos_rate_handler",
    "build_videos_rate_tool_descriptor",
    "build_videos_report_abuse_contract",
    "build_videos_report_abuse_handler",
    "build_videos_report_abuse_tool_descriptor",
    "build_videos_update_contract",
    "build_videos_update_handler",
    "build_videos_update_tool_descriptor",
    "map_videos_insert_result",
    "map_videos_get_rating_result",
    "map_videos_list_result",
    "map_videos_rate_result",
    "map_videos_report_abuse_result",
    "map_videos_update_result",
    "validate_videos_insert_arguments",
    "validate_videos_get_rating_arguments",
    "validate_videos_list_arguments",
    "validate_videos_rate_arguments",
    "validate_videos_report_abuse_arguments",
    "validate_videos_update_arguments",
]
