"""Concrete Layer 2 tool support for YouTube ``videos``."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.videos import build_videos_insert_wrapper, build_videos_list_wrapper
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


__all__ = [
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
    "VideosInsertToolError",
    "VideosListToolError",
    "build_videos_insert_contract",
    "build_videos_insert_handler",
    "build_videos_insert_tool_descriptor",
    "build_videos_list_contract",
    "build_videos_list_handler",
    "build_videos_list_tool_descriptor",
    "map_videos_insert_result",
    "map_videos_list_result",
    "validate_videos_insert_arguments",
    "validate_videos_list_arguments",
]
