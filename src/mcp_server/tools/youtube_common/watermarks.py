"""Concrete Layer 2 tool support for the YouTube ``watermarks`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.watermarks import build_watermarks_set_wrapper, build_watermarks_unset_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


WATERMARKS_SET_ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "application/octet-stream")
WATERMARKS_SET_MAX_BYTES = 10 * 1024 * 1024
WATERMARKS_SET_TOOL_NAME = "watermarks_set"
WATERMARKS_SET_QUOTA_COST = 50
WATERMARKS_SET_UNSAFE_DETAIL_KEYS = (
    "authorization",
    "auth_header",
    "content",
    "media.content",
    "raw_content",
    "request_body",
)

WATERMARKS_SET_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId", "body", "media"],
    "properties": {
        "channelId": {"type": "string", "minLength": 1},
        "body": {
            "type": "object",
            "required": ["timing", "position"],
            "properties": {
                "timing": {"type": "object"},
                "position": {"type": "object"},
                "targetChannelId": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "media": {
            "type": "object",
            "required": ["mimeType", "content"],
            "properties": {
                "mimeType": {"type": "string", "enum": list(WATERMARKS_SET_ALLOWED_MIME_TYPES)},
                "content": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

WATERMARKS_UNSET_TOOL_NAME = "watermarks_unset"
WATERMARKS_UNSET_QUOTA_COST = 50
WATERMARKS_UNSET_UNSAFE_DETAIL_KEYS = (
    "authorization",
    "auth_header",
    "body",
    "content",
    "media",
    "media.content",
    "raw_content",
    "raw_media",
    "request_body",
)

WATERMARKS_UNSET_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {
        "channelId": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

WATERMARKS_SET_DESCRIPTION = (
    "Set a channel watermark image for one YouTube channel. Endpoint: watermarks.set. "
    "Quota cost: 50. Auth: OAuth required. Requires channelId, body metadata, and media upload input."
)

WATERMARKS_SET_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required before setting a target channel watermark.",
    "Provide one channelId, body.timing, body.position, and media.mimeType plus media.content.",
    "Accepted media MIME types are image/jpeg, image/png, and application/octet-stream with a 10 MB upload limit.",
    "Successful upstream responses can be sparse; results preserve target channel, metadata, upload, and acknowledgment context.",
)

WATERMARKS_SET_CAVEATS = (
    "Availability is owner_only and depends on eligible OAuth access for the target channel.",
    "onBehalfOfContentOwner partner delegation is rejected in this slice.",
    "watermarks.unset, watermark lookup, channel updates, banner tools, thumbnail tools, video workflows, captions, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, and automated branding are out of scope.",
    "Raw media content, credentials, authorization headers, stack traces, raw upstream bodies, and unsafe diagnostics are never returned to callers.",
)

WATERMARKS_SET_CALLER_EXAMPLES = (
    {
        "name": "oauth_watermark_set",
        "description": "Quota cost: 50. Set one channel watermark with OAuth, metadata, and upload content.",
        "arguments": {
            "channelId": "UC123",
            "body": {
                "timing": {"type": "offsetFromStart", "offsetMs": 0},
                "position": {"type": "corner", "cornerPosition": "topRight"},
            },
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
        },
        "result": {
            "endpoint": "watermarks.set",
            "quotaCost": 50,
            "updated": True,
            "target": {"channelId": "UC123"},
            "metadata": {"hasTiming": True, "hasPosition": True},
            "upload": {"mimeType": "image/png", "contentProvided": True},
            "acknowledgment": {"accepted": True, "status": "watermark_set"},
        },
        "quotaCost": 50,
    },
    {
        "name": "sparse_success",
        "description": "Quota cost: 50. Preserve target, metadata, and upload context for a sparse 204 success.",
        "arguments": {
            "channelId": "UC123",
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/jpeg", "content": "<watermark content omitted>"},
        },
        "result": {
            "endpoint": "watermarks.set",
            "updated": True,
            "target": {"channelId": "UC123"},
            "upload": {"mimeType": "image/jpeg", "contentProvided": True},
            "upstream": {},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_channel_id",
        "description": "Reject requests missing the required target channelId.",
        "arguments": {
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_channel_id",
        "description": "Reject empty, non-string, or ambiguous multi-target channel identifiers.",
        "arguments": {
            "channelId": "UC123,UC456",
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_body",
        "description": "Reject metadata-only gaps where required watermark body timing or position is absent.",
        "arguments": {"channelId": "UC123", "media": {"mimeType": "image/png", "content": "<omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_metadata",
        "description": "Reject malformed metadata or invalid body.targetChannelId values.",
        "arguments": {
            "channelId": "UC123",
            "body": {"timing": {}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
        },
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_media",
        "description": "Reject requests missing required media upload content.",
        "arguments": {"channelId": "UC123", "body": {"timing": {"type": "offsetFromStart"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_upload",
        "description": "Reject unsupported media upload descriptors, MIME types, or oversized content over 10 MB.",
        "arguments": {
            "channelId": "UC123",
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "text/plain", "content": "text"},
        },
        "errorCategory": "unsupported_upload",
    },
    {
        "name": "rejected_partner_delegation",
        "description": "Reject onBehalfOfContentOwner because partner delegation is outside this slice.",
        "arguments": {"channelId": "UC123", "onBehalfOfContentOwner": "owner-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing OAuth access to safe authentication failures.",
        "arguments": {
            "channelId": "UC123",
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
        },
        "errorCategory": "authentication_failed",
    },
    {
        "name": "authorization_or_policy_failure",
        "description": "Map insufficient OAuth, forbidden, or policy failures without private auth details.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "target_channel_or_quota_failure",
        "description": "Map target-channel and quota failures to stable caller-facing categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "target_channel_failed",
    },
    {
        "name": "endpoint_unavailable_or_deprecated",
        "description": "Map unavailable or deprecated endpoint outcomes to safe categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "conflict_or_upstream_refusal",
        "description": "Map conflict or upstream refusal cases to safe categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "conflict",
    },
    {
        "name": "out_of_scope_watermark_workflow_request",
        "description": "Reject removal, lookup, banner, thumbnail, video, analytics, ranking, or enrichment workflows.",
        "arguments": {
            "channelId": "UC123",
            "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
            "media": {"mimeType": "image/png", "content": "<watermark content omitted>"},
            "rankResults": True,
        },
        "errorCategory": "invalid_request",
    },
)

WATERMARKS_UNSET_DESCRIPTION = (
    "Remove a channel watermark for one YouTube channel. Endpoint: watermarks.unset. "
    "Quota cost: 50. Auth: OAuth required. Requires channelId only and accepts no upload body or media."
)

WATERMARKS_UNSET_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required before removing a target channel watermark.",
    "Provide exactly one channelId; body, media, upload content, metadata-only, and media-only requests are rejected.",
    "This is a no upload mutation and successful upstream responses can be sparse 204 acknowledgments.",
    "Successful results preserve target channel, auth, owner-only availability, no-upload, and acknowledgment context.",
)

WATERMARKS_UNSET_CAVEATS = (
    "Availability is owner_only and depends on eligible OAuth access for the target channel.",
    "onBehalfOfContentOwner partner delegation is rejected in this slice.",
    "No-current-watermark, already-removed, or no-removal-possible outcomes are reported as safe failures rather than successful removals.",
    "watermarks.set, watermark lookup, channel updates, banner tools, thumbnail tools, video workflows, captions, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, and automated branding are out of scope.",
    "Raw media content, credentials, authorization headers, stack traces, raw upstream bodies, and unsafe diagnostics are never returned to callers.",
)

WATERMARKS_UNSET_CALLER_EXAMPLES = (
    {
        "name": "oauth_watermark_unset",
        "description": "Quota cost: 50. Remove one channel watermark with OAuth and a target channelId.",
        "arguments": {"channelId": "UC123"},
        "result": {
            "endpoint": "watermarks.unset",
            "quotaCost": 50,
            "removed": True,
            "target": {"channelId": "UC123"},
            "auth": {"mode": "oauth_required"},
            "availability": {"state": "owner_only"},
            "noUpload": {"bodyAccepted": False, "mediaAccepted": False},
            "acknowledgment": {"accepted": True, "status": "watermark_unset"},
        },
        "quotaCost": 50,
    },
    {
        "name": "sparse_success",
        "description": "Quota cost: 50. Preserve target and no-upload context for a sparse 204 success.",
        "arguments": {"channelId": "UC123"},
        "result": {
            "endpoint": "watermarks.unset",
            "removed": True,
            "target": {"channelId": "UC123"},
            "noUpload": {"bodyAccepted": False, "mediaAccepted": False},
            "upstream": {},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_channel_id",
        "description": "Reject requests missing the required target channelId.",
        "arguments": {},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_channel_id",
        "description": "Reject empty, non-string, or ambiguous multi-target channel identifiers.",
        "arguments": {"channelId": "UC123,UC456"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_body",
        "description": "Reject body metadata because watermarks_unset accepts no request body.",
        "arguments": {"channelId": "UC123", "body": {"timing": {"type": "offsetFromStart"}}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_media",
        "description": "Reject media upload descriptors because watermarks_unset accepts no media.",
        "arguments": {"channelId": "UC123", "media": {"mimeType": "image/png", "content": "<omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "rejected_partner_delegation",
        "description": "Reject onBehalfOfContentOwner because partner delegation is outside this slice.",
        "arguments": {"channelId": "UC123", "onBehalfOfContentOwner": "owner-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Map missing OAuth access to safe authentication failures.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "authorization_or_policy_failure",
        "description": "Map insufficient OAuth, forbidden, or policy failures without private auth details.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "target_channel_or_quota_failure",
        "description": "Map target-channel and quota failures to stable caller-facing categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "target_channel_failed",
    },
    {
        "name": "no_removal_possible",
        "description": "Report no-current-watermark or already-removed outcomes without treating them as success.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "no_removal_possible",
    },
    {
        "name": "endpoint_unavailable_or_deprecated",
        "description": "Map unavailable or deprecated endpoint outcomes to safe categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "conflict_or_upstream_refusal",
        "description": "Map conflict or upstream refusal cases to safe categories.",
        "arguments": {"channelId": "UC123"},
        "errorCategory": "conflict",
    },
    {
        "name": "out_of_scope_watermark_workflow_request",
        "description": "Reject upload, lookup, banner, thumbnail, video, analytics, ranking, or enrichment workflows.",
        "arguments": {"channelId": "UC123", "rankResults": True},
        "errorCategory": "invalid_request",
    },
)


class WatermarksSetToolError(ValueError):
    """Represent a safe caller-facing ``watermarks_set`` failure.

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
        self.details = _sanitize_watermarks_set_error_details(details or {})


class WatermarksUnsetToolError(ValueError):
    """Represent a safe caller-facing ``watermarks_unset`` failure.

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
        self.details = _sanitize_watermarks_unset_error_details(details or {})


def _sanitize_watermarks_set_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove watermark-specific secret and raw upload fields from error details.

    :param details: Candidate diagnostic detail mapping.
    :return: Safe diagnostic details for caller-facing errors.
    """
    filtered = {
        key: value
        for key, value in details.items()
        if str(key).lower() not in set(WATERMARKS_SET_UNSAFE_DETAIL_KEYS)
    }
    return sanitize_error_details(filtered)


def _sanitize_watermarks_unset_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove watermark-unset secret, metadata, and raw upload fields from details.

    :param details: Candidate diagnostic detail mapping.
    :return: Safe diagnostic details for caller-facing errors.
    """
    filtered = {
        key: value
        for key, value in details.items()
        if str(key).lower() not in set(WATERMARKS_UNSET_UNSAFE_DETAIL_KEYS)
    }
    return sanitize_error_details(filtered)


def _validate_watermarks_set_channel_id(channel_id: Any) -> str:
    """Validate and normalize the target channel id.

    :param channel_id: Candidate target channel identifier.
    :return: Stripped target channel id.
    :raises WatermarksSetToolError: If the identifier is missing, invalid, or ambiguous.
    """
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise WatermarksSetToolError("watermarks_set requires channelId", details={"field": "channelId"})
    normalized = channel_id.strip()
    if "," in normalized:
        raise WatermarksSetToolError(
            "watermarks_set accepts exactly one channelId",
            details={"field": "channelId"},
        )
    return normalized


def _validate_watermarks_set_body(body: Any) -> dict[str, Any]:
    """Validate watermark metadata input.

    :param body: Candidate watermark metadata descriptor.
    :return: Metadata descriptor accepted by the Layer 1 wrapper.
    :raises WatermarksSetToolError: If metadata is missing or malformed.
    """
    if not isinstance(body, dict) or not body:
        raise WatermarksSetToolError("watermarks_set requires body", details={"field": "body"})

    unsupported = sorted(set(body) - {"timing", "position", "targetChannelId"})
    if unsupported:
        raise WatermarksSetToolError(
            "watermarks_set body supports only timing, position, and targetChannelId",
            details={"field": f"body.{unsupported[0]}"},
        )

    timing = body.get("timing")
    if not isinstance(timing, dict) or not timing:
        raise WatermarksSetToolError("watermarks_set requires body.timing", details={"field": "body.timing"})

    position = body.get("position")
    if not isinstance(position, dict) or not position:
        raise WatermarksSetToolError("watermarks_set requires body.position", details={"field": "body.position"})

    normalized: dict[str, Any] = {"timing": dict(timing), "position": dict(position)}
    target_channel_id = body.get("targetChannelId")
    if target_channel_id is not None:
        if not isinstance(target_channel_id, str) or not target_channel_id.strip():
            raise WatermarksSetToolError(
                "body.targetChannelId must be a non-empty string when provided",
                details={"field": "body.targetChannelId"},
            )
        normalized["targetChannelId"] = target_channel_id.strip()
    return normalized


def _media_content_size(content: Any) -> int:
    """Return upload content size in bytes for supported in-memory payloads.

    :param content: Candidate media content.
    :return: Byte size of the content.
    """
    if isinstance(content, bytes):
        return len(content)
    return len(str(content).encode("utf-8"))


def _validate_watermarks_set_media(media: Any) -> dict[str, Any]:
    """Validate watermark media upload input.

    :param media: Candidate media upload descriptor.
    :return: Media descriptor accepted by the Layer 1 wrapper.
    :raises WatermarksSetToolError: If media is malformed or unsupported.
    """
    if not isinstance(media, dict) or not media:
        raise WatermarksSetToolError("watermarks_set requires media", details={"field": "media"})

    unsupported = sorted(set(media) - {"mimeType", "content"})
    if unsupported:
        raise WatermarksSetToolError(
            "watermarks_set media supports only mimeType and content",
            category="unsupported_upload",
            details={"field": f"media.{unsupported[0]}"},
        )

    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise WatermarksSetToolError("watermarks_set requires media.mimeType", details={"field": "media.mimeType"})
    mime_type = mime_type.strip()
    if mime_type not in WATERMARKS_SET_ALLOWED_MIME_TYPES:
        raise WatermarksSetToolError(
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream",
            category="unsupported_upload",
            details={"field": "media.mimeType", "mimeType": mime_type},
        )

    content = media.get("content")
    if not isinstance(content, str | bytes) or not content:
        raise WatermarksSetToolError("watermarks_set requires media.content", details={"field": "media.content"})
    if _media_content_size(content) > WATERMARKS_SET_MAX_BYTES:
        raise WatermarksSetToolError(
            "media.content exceeds the 10 MB watermark limit",
            category="unsupported_upload",
            details={"field": "media.content", "limitBytes": WATERMARKS_SET_MAX_BYTES},
        )

    return {"mimeType": mime_type, "content": content}


def validate_watermarks_set_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``watermarks_set`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises WatermarksSetToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise WatermarksSetToolError("watermarks_set arguments must be an object", details={"field": "arguments"})

    allowed = {"channelId", "body", "media"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise WatermarksSetToolError(
            f"unsupported field for watermarks_set: {unsupported[0]}",
            details={"field": unsupported[0]},
        )

    return {
        "channelId": _validate_watermarks_set_channel_id(arguments.get("channelId")),
        "body": _validate_watermarks_set_body(arguments.get("body")),
        "media": _validate_watermarks_set_media(arguments.get("media")),
    }


def _validate_watermarks_unset_channel_id(channel_id: Any) -> str:
    """Validate and normalize the target channel id for watermark removal.

    :param channel_id: Candidate target channel identifier.
    :return: Stripped target channel id.
    :raises WatermarksUnsetToolError: If the identifier is missing, invalid, or ambiguous.
    """
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise WatermarksUnsetToolError("watermarks_unset requires channelId", details={"field": "channelId"})
    normalized = channel_id.strip()
    if "," in normalized:
        raise WatermarksUnsetToolError(
            "watermarks_unset accepts exactly one channelId",
            details={"field": "channelId"},
        )
    return normalized


def validate_watermarks_unset_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``watermarks_unset`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises WatermarksUnsetToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise WatermarksUnsetToolError("watermarks_unset arguments must be an object", details={"field": "arguments"})

    allowed = {"channelId"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise WatermarksUnsetToolError(
            f"unsupported field for watermarks_unset: {unsupported[0]}",
            details={"field": unsupported[0]},
        )

    return {"channelId": _validate_watermarks_unset_channel_id(arguments.get("channelId"))}


def _safe_watermarks_set_upstream_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a safe upstream payload copy for public results.

    :param payload: Upstream or Layer 1 watermark-set payload.
    :return: Sanitized upstream payload that omits unsafe upload or credential fields.
    """
    if not isinstance(payload, dict):
        return {}
    return _sanitize_watermarks_set_error_details(payload)


def _safe_watermarks_unset_upstream_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a safe upstream payload copy for public watermark-unset results.

    :param payload: Upstream or Layer 1 watermark-unset payload.
    :return: Sanitized upstream payload that omits unsafe metadata, upload, or credential fields.
    """
    if not isinstance(payload, dict):
        return {}
    return _sanitize_watermarks_unset_error_details(payload)


def _watermarks_set_metadata_context(body: dict[str, Any]) -> dict[str, Any]:
    """Build safe watermark metadata context for a result.

    :param body: Validated watermark metadata descriptor.
    :return: Safe metadata summary that omits raw request content.
    """
    metadata = {
        "hasTiming": bool(body.get("timing")),
        "hasPosition": bool(body.get("position")),
    }
    if body.get("targetChannelId"):
        metadata["targetChannelId"] = body["targetChannelId"]
    return metadata


def _watermarks_set_upload_context(media: dict[str, Any]) -> dict[str, Any]:
    """Build safe media upload context for a watermark-set result.

    :param media: Validated media upload descriptor.
    :return: Safe media summary that omits raw upload content.
    """
    return {"mimeType": media["mimeType"], "contentProvided": bool(media.get("content"))}


def _watermarks_unset_target_context(arguments: dict[str, Any]) -> dict[str, str]:
    """Build safe target-channel context for a watermark-unset result.

    :param arguments: Validated watermark-unset arguments.
    :return: Safe target context containing the channel id.
    """
    return {"channelId": arguments["channelId"]}


def _watermarks_unset_no_upload_context() -> dict[str, bool]:
    """Build explicit no-upload context for a watermark-unset result.

    :return: Safe context showing body and media are not accepted.
    """
    return {"bodyAccepted": False, "mediaAccepted": False}


def map_watermarks_set_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream watermark-set payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 watermark-set payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw upload mutation acknowledgment with safe context.
    """
    normalized = validate_watermarks_set_arguments(arguments)
    return {
        "endpoint": "watermarks.set",
        "sourceOperation": "watermarks.set",
        "quotaCost": WATERMARKS_SET_QUOTA_COST,
        "updated": True,
        "target": {"channelId": normalized["channelId"]},
        "metadata": _watermarks_set_metadata_context(normalized["body"]),
        "upload": _watermarks_set_upload_context(normalized["media"]),
        "auth": {"mode": "oauth_required"},
        "availability": {"state": "owner_only"},
        "acknowledgment": {"accepted": True, "status": "watermark_set"},
        "upstream": _safe_watermarks_set_upstream_payload(payload),
    }


def map_watermarks_unset_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream watermark-unset payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 watermark-unset payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw mutation acknowledgment with safe target and no-upload context.
    """
    normalized = validate_watermarks_unset_arguments(arguments)
    return {
        "endpoint": "watermarks.unset",
        "sourceOperation": "watermarks.unset",
        "quotaCost": WATERMARKS_UNSET_QUOTA_COST,
        "removed": True,
        "target": _watermarks_unset_target_context(normalized),
        "auth": {"mode": "oauth_required"},
        "availability": {"state": "owner_only"},
        "noUpload": _watermarks_unset_no_upload_context(),
        "acknowledgment": {"accepted": True, "status": "watermark_unset"},
        "upstream": _safe_watermarks_unset_upstream_payload(payload),
    }


def _map_watermarks_set_upstream_error(error: NormalizedUpstreamError) -> WatermarksSetToolError:
    """Map a normalized upstream failure to a safe ``watermarks_set`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe watermarks-set tool error with shared category and sanitized details.
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
        "target_channel": "target_channel_failed",
        "channel": "target_channel_failed",
        "not_found": "target_channel_failed",
        "resource_not_found": "target_channel_failed",
        "unavailable_channel": "target_channel_failed",
        "media_eligibility": "unsupported_upload",
        "unsupported_upload": "unsupported_upload",
        "upload_rejected": "upload_rejected",
        "upload_failure": "upload_rejected",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
        "conflict": "conflict",
        "refused": "upstream_refused",
        "upstream_refusal": "upstream_refused",
    }
    category = category_map.get(error.category, "upstream_failure")
    return WatermarksSetToolError(str(error), category=category, details=error.details)


def _map_watermarks_unset_upstream_error(error: NormalizedUpstreamError) -> WatermarksUnsetToolError:
    """Map a normalized upstream failure to a safe ``watermarks_unset`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe watermarks-unset tool error with shared category and sanitized details.
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
        "target_channel": "target_channel_failed",
        "channel": "target_channel_failed",
        "not_found": "target_channel_failed",
        "resource_not_found": "target_channel_failed",
        "unavailable_channel": "target_channel_failed",
        "no_removal": "no_removal_possible",
        "no_removal_possible": "no_removal_possible",
        "already_removed": "no_removal_possible",
        "no_current_watermark": "no_removal_possible",
        "watermark_not_found": "no_removal_possible",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "availability": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
        "conflict": "conflict",
        "refused": "upstream_refused",
        "upstream_refusal": "upstream_refused",
    }
    category = category_map.get(error.category, "upstream_failure")
    return WatermarksUnsetToolError(str(error), category=category, details=error.details)


def _watermarks_set_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``watermarks_set``.

    :param oauth_token: OAuth token used for watermark setting.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises WatermarksSetToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise WatermarksSetToolError(
            "watermarks_set requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def _watermarks_unset_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``watermarks_unset``.

    :param oauth_token: OAuth token used for watermark removal.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises WatermarksUnsetToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise WatermarksUnsetToolError(
            "watermarks_unset requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_watermarks_set_contract() -> YouTubeToolContract:
    """Build the public contract for ``watermarks_set``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "sourceOperation",
            "quotaCost",
            "updated",
            "target",
            "metadata",
            "upload",
            "auth",
            "availability",
            "acknowledgment",
            "upstream",
        ),
        preserved_upstream_fields=("sourceOperation", "status", "statusCode", "etag", "kind"),
        disallowed_behavior=(
            "watermark_unset",
            "watermark_lookup",
            "channel_update",
            "banner_upload",
            "thumbnail_upload",
            "video_workflow",
            "caption_workflow",
            "playlist_workflow",
            "comment_workflow",
            "transcript_workflow",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "automated_branding",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=WATERMARKS_SET_TOOL_NAME,
        upstream_resource="watermarks",
        upstream_method="set",
        operation_key="watermarks.set",
        description=WATERMARKS_SET_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=WATERMARKS_SET_QUOTA_COST,
        resource_family="watermarks",
        input_contract=WATERMARKS_SET_INPUT_SCHEMA,
        response_convention={
            "resultKind": "upload_mutation_acknowledgment",
            "mediaResult": "safe_media_summary",
            "targetFields": ["channelId"],
            "metadataFields": ["body.timing", "body.position", "body.targetChannelId"],
            "uploadFields": ["media.mimeType", "media.content"],
            "successStatus": 204,
            "sparseResultPolicy": "preserve_target_metadata_upload_and_acknowledgment_context",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "target_channel_failed",
            "unsupported_upload",
            "upload_rejected",
            "quota_exhausted",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "conflict",
            "upstream_refused",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.OWNER_ONLY,
        usage_notes=WATERMARKS_SET_USAGE_NOTES,
        caveats=WATERMARKS_SET_CAVEATS,
    )


def build_watermarks_unset_contract() -> YouTubeToolContract:
    """Build the public contract for ``watermarks_unset``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "sourceOperation",
            "quotaCost",
            "removed",
            "target",
            "auth",
            "availability",
            "noUpload",
            "acknowledgment",
            "upstream",
        ),
        preserved_upstream_fields=("sourceOperation", "status", "statusCode", "etag", "kind"),
        disallowed_behavior=(
            "watermark_set",
            "watermark_lookup",
            "channel_update",
            "banner_upload",
            "thumbnail_upload",
            "video_workflow",
            "caption_workflow",
            "playlist_workflow",
            "comment_workflow",
            "transcript_workflow",
            "analytics",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "automated_branding",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=WATERMARKS_UNSET_TOOL_NAME,
        upstream_resource="watermarks",
        upstream_method="unset",
        operation_key="watermarks.unset",
        description=WATERMARKS_UNSET_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=WATERMARKS_UNSET_QUOTA_COST,
        resource_family="watermarks",
        input_contract=WATERMARKS_UNSET_INPUT_SCHEMA,
        response_convention={
            "resultKind": "mutation_acknowledgment",
            "targetFields": ["channelId"],
            "noUploadFields": ["body", "media"],
            "successStatus": 204,
            "sparseResultPolicy": "preserve_target_no_upload_and_acknowledgment_context",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "target_channel_failed",
            "no_removal_possible",
            "quota_exhausted",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "conflict",
            "upstream_refused",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.OWNER_ONLY,
        usage_notes=WATERMARKS_UNSET_USAGE_NOTES,
        caveats=WATERMARKS_UNSET_CAVEATS,
    )


def _default_watermarks_set_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default watermark-set calls.

    :return: Integration executor returning representative watermark-set data.
    """

    def transport(execution):
        """Return a representative sparse watermark-set response.

        :param execution: Request execution context.
        :return: Fake upstream watermark-set response for local invocation.
        """
        return {
            "sourceOperation": "watermarks.set",
            "status": 204,
            "target": {"channelId": execution.arguments["channelId"]},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_watermarks_unset_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default watermark-unset calls.

    :return: Integration executor returning representative watermark-unset data.
    """

    def transport(execution):
        """Return a representative sparse watermark-unset response.

        :param execution: Request execution context.
        :return: Fake upstream watermark-unset response for local invocation.
        """
        return {
            "sourceOperation": "watermarks.unset",
            "status": 204,
            "target": {"channelId": execution.arguments["channelId"]},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_watermarks_set_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``watermarks_set``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps watermark-set requests.
    """
    selected_wrapper = wrapper or build_watermarks_set_wrapper()
    selected_executor = executor or _default_watermarks_set_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``watermarks_set`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 watermark-set result.
        :raises WatermarksSetToolError: If validation or execution fails.
        """
        normalized = validate_watermarks_set_arguments(arguments)
        auth_context = _watermarks_set_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_watermarks_set_upstream_error(exc) from exc
        except ValueError as exc:
            raise WatermarksSetToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "watermarks.set"},
            ) from exc
        return map_watermarks_set_result(payload, normalized)

    return handler


def build_watermarks_unset_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``watermarks_unset``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps watermark-unset requests.
    """
    selected_wrapper = wrapper or build_watermarks_unset_wrapper()
    selected_executor = executor or _default_watermarks_unset_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``watermarks_unset`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 watermark-unset result.
        :raises WatermarksUnsetToolError: If validation or execution fails.
        """
        normalized = validate_watermarks_unset_arguments(arguments)
        auth_context = _watermarks_unset_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_watermarks_unset_upstream_error(exc) from exc
        except ValueError as exc:
            raise WatermarksUnsetToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "watermarks.unset"},
            ) from exc
        return map_watermarks_unset_result(payload, normalized)

    return handler


def build_watermarks_set_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``watermarks_set``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_watermarks_set_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(WATERMARKS_SET_CALLER_EXAMPLES)
    return {
        "name": WATERMARKS_SET_TOOL_NAME,
        "description": WATERMARKS_SET_DESCRIPTION,
        "inputSchema": WATERMARKS_SET_INPUT_SCHEMA,
        "handler": build_watermarks_set_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


def build_watermarks_unset_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``watermarks_unset``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_watermarks_unset_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(WATERMARKS_UNSET_CALLER_EXAMPLES)
    return {
        "name": WATERMARKS_UNSET_TOOL_NAME,
        "description": WATERMARKS_UNSET_DESCRIPTION,
        "inputSchema": WATERMARKS_UNSET_INPUT_SCHEMA,
        "handler": build_watermarks_unset_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "WATERMARKS_SET_ALLOWED_MIME_TYPES",
    "WATERMARKS_SET_CALLER_EXAMPLES",
    "WATERMARKS_SET_CAVEATS",
    "WATERMARKS_SET_DESCRIPTION",
    "WATERMARKS_SET_INPUT_SCHEMA",
    "WATERMARKS_SET_MAX_BYTES",
    "WATERMARKS_SET_QUOTA_COST",
    "WATERMARKS_SET_TOOL_NAME",
    "WATERMARKS_SET_UNSAFE_DETAIL_KEYS",
    "WATERMARKS_SET_USAGE_NOTES",
    "WATERMARKS_UNSET_CALLER_EXAMPLES",
    "WATERMARKS_UNSET_CAVEATS",
    "WATERMARKS_UNSET_DESCRIPTION",
    "WATERMARKS_UNSET_INPUT_SCHEMA",
    "WATERMARKS_UNSET_QUOTA_COST",
    "WATERMARKS_UNSET_TOOL_NAME",
    "WATERMARKS_UNSET_UNSAFE_DETAIL_KEYS",
    "WATERMARKS_UNSET_USAGE_NOTES",
    "WatermarksSetToolError",
    "WatermarksUnsetToolError",
    "build_watermarks_set_contract",
    "build_watermarks_set_handler",
    "build_watermarks_set_tool_descriptor",
    "build_watermarks_unset_contract",
    "build_watermarks_unset_handler",
    "build_watermarks_unset_tool_descriptor",
    "map_watermarks_set_result",
    "map_watermarks_unset_result",
    "validate_watermarks_set_arguments",
    "validate_watermarks_unset_arguments",
]
