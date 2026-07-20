"""Concrete Layer 2 tool support for the YouTube ``thumbnails`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.thumbnails import build_thumbnails_set_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


THUMBNAILS_SET_ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "application/octet-stream")
THUMBNAILS_SET_TOOL_NAME = "thumbnails_set"
THUMBNAILS_SET_QUOTA_COST = 50

THUMBNAILS_SET_INPUT_SCHEMA = {
    "type": "object",
    "required": ["videoId", "media"],
    "properties": {
        "videoId": {"type": "string", "minLength": 1},
        "media": {
            "type": "object",
            "required": ["mimeType", "content"],
            "properties": {
                "mimeType": {"type": "string", "enum": list(THUMBNAILS_SET_ALLOWED_MIME_TYPES)},
                "content": {"type": "string", "minLength": 1},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

THUMBNAILS_SET_DESCRIPTION = (
    "Set a custom thumbnail image for one YouTube video. Endpoint: thumbnails.set. "
    "Quota cost: 50. Auth: OAuth required. Requires videoId and media upload input."
)

THUMBNAILS_SET_USAGE_NOTES = (
    "Quota cost: 50. OAuth authorization is required before replacing a target video thumbnail.",
    "Provide videoId for the target video and media.mimeType plus media.content for the thumbnail upload.",
    "Successful upstream responses can be sparse; results preserve target video and safe media upload context.",
)

THUMBNAILS_SET_CAVEATS = (
    "This tool only replaces an existing video's custom thumbnail through thumbnails.set.",
    "thumbnail generation, image editing, video metadata updates, search, analytics, ranking, summarization, and enrichment are out of scope.",
    "Raw media content, credentials, stack traces, and unsafe upstream diagnostics are never returned to callers.",
)

THUMBNAILS_SET_CALLER_EXAMPLES = (
    {
        "name": "oauth_thumbnail_set",
        "description": "Quota cost: 50. Replace one target video thumbnail with OAuth and media upload content.",
        "arguments": {
            "videoId": "video-123",
            "media": {"mimeType": "image/png", "content": "<image content omitted>"},
        },
        "result": {
            "endpoint": "thumbnails.set",
            "quotaCost": 50,
            "updated": True,
            "target": {"videoId": "video-123"},
            "upload": {"mimeType": "image/png", "contentProvided": True},
        },
        "quotaCost": 50,
    },
    {
        "name": "sparse_success",
        "description": "Quota cost: 50. Preserve target and upload context when upstream returns a sparse success.",
        "arguments": {
            "videoId": "video-123",
            "media": {"mimeType": "image/jpeg", "content": "<image content omitted>"},
        },
        "result": {
            "endpoint": "thumbnails.set",
            "updated": True,
            "target": {"videoId": "video-123"},
            "upload": {"mimeType": "image/jpeg", "contentProvided": True},
            "upstream": {},
        },
        "quotaCost": 50,
    },
    {
        "name": "missing_video_id",
        "description": "Reject requests missing the required target videoId.",
        "arguments": {"media": {"mimeType": "image/png", "content": "<image content omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_media",
        "description": "Reject requests missing required media upload content.",
        "arguments": {"videoId": "video-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_video_id",
        "description": "Reject empty or non-string target video identifiers.",
        "arguments": {"videoId": "", "media": {"mimeType": "image/png", "content": "<image content omitted>"}},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_upload",
        "description": "Reject unsupported media upload descriptors or media types.",
        "arguments": {"videoId": "video-123", "media": {"mimeType": "text/plain", "content": "text"}},
        "errorCategory": "unsupported_upload",
    },
    {
        "name": "access_failure",
        "description": "Map missing OAuth access to safe authentication failures.",
        "arguments": {
            "videoId": "video-123",
            "media": {"mimeType": "image/png", "content": "<image content omitted>"},
        },
        "errorCategory": "authentication_failed",
    },
    {
        "name": "target_video_or_quota_failure",
        "description": "Map target-video and quota failures to stable caller-facing categories.",
        "arguments": {
            "videoId": "video-123",
            "media": {"mimeType": "image/png", "content": "<image content omitted>"},
        },
        "errorCategory": "target_video_failed",
    },
    {
        "name": "out_of_scope_thumbnail_management_request",
        "description": "Reject thumbnail generation, image editing, video metadata, search, and enrichment requests.",
        "arguments": {
            "videoId": "video-123",
            "media": {"mimeType": "image/png", "content": "<image content omitted>"},
            "generateThumbnail": True,
        },
        "errorCategory": "invalid_request",
    },
)


class ThumbnailsSetToolError(ValueError):
    """Represent a safe caller-facing ``thumbnails_set`` failure.

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
        self.details = _sanitize_thumbnails_set_error_details(details or {})


def _sanitize_thumbnails_set_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove thumbnail-specific secret and raw upload fields from error details.

    :param details: Candidate diagnostic detail mapping.
    :return: Safe diagnostic details for caller-facing errors.
    """
    return sanitize_error_details(
        {key: value for key, value in details.items() if str(key).lower() not in {"authorization", "auth_header"}}
    )


def _validate_thumbnails_set_video_id(video_id: Any) -> str:
    """Validate and normalize the target video id.

    :param video_id: Candidate target video identifier.
    :return: Stripped target video id.
    :raises ThumbnailsSetToolError: If the identifier is missing or invalid.
    """
    if not isinstance(video_id, str) or not video_id.strip():
        raise ThumbnailsSetToolError("thumbnails_set requires videoId", details={"field": "videoId"})
    return video_id.strip()


def _validate_thumbnails_set_media(media: Any) -> dict[str, str]:
    """Validate thumbnail media upload input.

    :param media: Candidate media upload descriptor.
    :return: Media descriptor accepted by the Layer 1 wrapper.
    :raises ThumbnailsSetToolError: If media is malformed or unsupported.
    """
    if not isinstance(media, dict) or not media:
        raise ThumbnailsSetToolError("thumbnails_set requires media", details={"field": "media"})

    unsupported = sorted(set(media) - {"mimeType", "content"})
    if unsupported:
        raise ThumbnailsSetToolError(
            "thumbnails_set media supports only mimeType and content",
            category="unsupported_upload",
            details={"field": f"media.{unsupported[0]}"},
        )

    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise ThumbnailsSetToolError("thumbnails_set requires media.mimeType", details={"field": "media.mimeType"})
    mime_type = mime_type.strip()
    if mime_type not in THUMBNAILS_SET_ALLOWED_MIME_TYPES:
        raise ThumbnailsSetToolError(
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream",
            category="unsupported_upload",
            details={"field": "media.mimeType", "mimeType": mime_type},
        )

    content = media.get("content")
    if not isinstance(content, str) or not content:
        raise ThumbnailsSetToolError("thumbnails_set requires media.content", details={"field": "media.content"})

    return {"mimeType": mime_type, "content": content}


def validate_thumbnails_set_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``thumbnails_set`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises ThumbnailsSetToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise ThumbnailsSetToolError("thumbnails_set arguments must be an object")

    allowed = {"videoId", "media"}
    unsupported = sorted(set(arguments) - allowed)
    if unsupported:
        raise ThumbnailsSetToolError(
            f"unsupported field for thumbnails_set: {unsupported[0]}",
            details={"field": unsupported[0]},
        )

    return {
        "videoId": _validate_thumbnails_set_video_id(arguments.get("videoId")),
        "media": _validate_thumbnails_set_media(arguments.get("media")),
    }


def _safe_thumbnails_set_upstream_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a safe upstream payload copy for public results.

    :param payload: Upstream or Layer 1 thumbnail-set payload.
    :return: Sanitized upstream payload that omits unsafe upload or credential fields.
    """
    if not isinstance(payload, dict):
        return {}
    return sanitize_error_details(payload)


def _thumbnails_set_upload_context(media: dict[str, Any]) -> dict[str, Any]:
    """Build safe media upload context for a thumbnail-set result.

    :param media: Validated media upload descriptor.
    :return: Safe media summary that omits raw upload content.
    """
    return {"mimeType": media["mimeType"], "contentProvided": bool(media.get("content"))}


def map_thumbnails_set_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream thumbnail-set payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 thumbnail-set payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw upload result with safe target and media context.
    """
    normalized = validate_thumbnails_set_arguments(arguments)
    return {
        "endpoint": "thumbnails.set",
        "quotaCost": THUMBNAILS_SET_QUOTA_COST,
        "updated": True,
        "target": {"videoId": normalized["videoId"]},
        "upload": _thumbnails_set_upload_context(normalized["media"]),
        "auth": {"mode": "oauth_required"},
        "upstream": _safe_thumbnails_set_upstream_payload(payload),
    }


def _map_thumbnails_set_upstream_error(error: NormalizedUpstreamError) -> ThumbnailsSetToolError:
    """Map a normalized upstream failure to a safe ``thumbnails_set`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe thumbnails-set tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "target_video": "target_video_failed",
        "not_found": "target_video_failed",
        "resource_not_found": "target_video_failed",
        "media_eligibility": "unsupported_upload",
        "upload_rejected": "upload_rejected",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "unavailable": "endpoint_unavailable",
        "transient": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return ThumbnailsSetToolError(str(error), category=category, details=error.details)


def _thumbnails_set_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required auth context for ``thumbnails_set``.

    :param oauth_token: OAuth token used for thumbnail replacement.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises ThumbnailsSetToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise ThumbnailsSetToolError(
            "thumbnails_set requires OAuth authorization",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_thumbnails_set_contract() -> YouTubeToolContract:
    """Build the public contract for ``thumbnails_set``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "updated",
            "target",
            "upload",
            "auth",
            "upstream",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "thumbnailUrl"),
        disallowed_behavior=(
            "thumbnail_generation",
            "image_editing",
            "video_metadata_update",
            "video_lookup",
            "search",
            "channel_selection",
            "playlist_selection",
            "paging",
            "analytics",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=THUMBNAILS_SET_TOOL_NAME,
        upstream_resource="thumbnails",
        upstream_method="set",
        operation_key="thumbnails.set",
        description=THUMBNAILS_SET_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=THUMBNAILS_SET_QUOTA_COST,
        resource_family="thumbnails",
        input_contract=THUMBNAILS_SET_INPUT_SCHEMA,
        response_convention={
            "resultKind": "upload_result",
            "mediaResult": "safe_media_summary",
            "targetFields": ["videoId"],
            "uploadFields": ["media.mimeType", "media.content"],
            "sparseResultPolicy": "preserve_target_and_upload_context_when_upstream_returns_empty_payload",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "target_video_failed",
            "unsupported_upload",
            "upload_rejected",
            "quota_exhausted",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=THUMBNAILS_SET_USAGE_NOTES,
        caveats=THUMBNAILS_SET_CAVEATS,
    )


def _default_thumbnails_set_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default thumbnail-set calls.

    :return: Integration executor returning representative thumbnail-set data.
    """

    def transport(execution):
        """Return a representative thumbnail-set response.

        :param execution: Request execution context.
        :return: Fake upstream thumbnail-set response for local invocation.
        """
        return {
            "kind": "youtube#thumbnailSetResponse",
            "etag": "etag-thumbnail-set",
            "items": [
                {
                    "default": {
                        "url": f"https://i.ytimg.com/vi/{execution.arguments['videoId']}/default.jpg",
                    }
                }
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_thumbnails_set_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``thumbnails_set``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps thumbnail-set requests.
    """
    selected_wrapper = wrapper or build_thumbnails_set_wrapper()
    selected_executor = executor or _default_thumbnails_set_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``thumbnails_set`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 thumbnail-set result.
        :raises ThumbnailsSetToolError: If validation or execution fails.
        """
        normalized = validate_thumbnails_set_arguments(arguments)
        auth_context = _thumbnails_set_auth_context(oauth_token)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_thumbnails_set_upstream_error(exc) from exc
        except ValueError as exc:
            raise ThumbnailsSetToolError(
                str(exc),
                category="invalid_request",
                details={"operation": "thumbnails.set"},
            ) from exc
        return map_thumbnails_set_result(payload, normalized)

    return handler


def build_thumbnails_set_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``thumbnails_set``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_thumbnails_set_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(THUMBNAILS_SET_CALLER_EXAMPLES)
    return {
        "name": THUMBNAILS_SET_TOOL_NAME,
        "description": THUMBNAILS_SET_DESCRIPTION,
        "inputSchema": THUMBNAILS_SET_INPUT_SCHEMA,
        "handler": build_thumbnails_set_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }
