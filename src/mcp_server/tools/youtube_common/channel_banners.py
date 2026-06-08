"""Concrete Layer 2 tool support for the YouTube ``channelBanners`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.channel_banners import build_channel_banners_insert_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


CHANNEL_BANNERS_INSERT_TOOL_NAME = "channelBanners_insert"
CHANNEL_BANNERS_INSERT_QUOTA_COST = 50
CHANNEL_BANNERS_ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "application/octet-stream")
CHANNEL_BANNERS_MAX_BYTES = 6 * 1024 * 1024

CHANNEL_BANNERS_INSERT_INPUT_SCHEMA = {
    "type": "object",
    "required": ["media"],
    "properties": {
        "media": {
            "type": "object",
            "properties": {
                "mimeType": {"type": "string", "enum": list(CHANNEL_BANNERS_ALLOWED_MIME_TYPES)},
                "content": {"type": "string", "minLength": 1},
                "contentRef": {"type": "string", "minLength": 1},
                "filename": {"type": "string", "minLength": 1},
                "sizeBytes": {"type": "integer", "minimum": 0, "maximum": CHANNEL_BANNERS_MAX_BYTES},
            },
            "additionalProperties": False,
        },
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CHANNEL_BANNERS_INSERT_DESCRIPTION = (
    "Upload a YouTube channel banner image. Endpoint: channelBanners.insert. "
    "Quota cost: 50. Auth: oauth_required. Requires banner media input."
)
CHANNEL_BANNERS_INSERT_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide supported banner media input.",
    "Quota cost: 50. Accepted MIME types are image/jpeg, image/png, and application/octet-stream.",
    "Quota cost: 50. Banner images must stay within the documented 6 MB maximum upload size.",
    "Quota cost: 50. YouTube expects a 16:9 image, at least 2048x1152, with 2560x1440 recommended.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegation context and requires eligible OAuth authorization.",
    "Quota cost: 50. channelBanners.insert accepts no JSON metadata request body.",
    "Quota cost: 50. The returned URL is used by a separate channels.update call to activate the banner.",
)
CHANNEL_BANNERS_INSERT_CAVEATS = (
    "Channel banner upload requires eligible OAuth authorization for channel branding operations.",
    "Banner media input is required; metadata-only requests are unsupported.",
    "This tool uploads the banner image and returns the banner URL but does not activate it on a channel.",
    "Image resizing, preview generation, profile image updates, and bulk branding workflows are out of scope.",
)
CHANNEL_BANNERS_INSERT_CALLER_EXAMPLES = (
    {
        "name": "authorized_upload",
        "arguments": {
            "media": {
                "mimeType": "image/png",
                "content": "<binary image content omitted>",
                "filename": "banner.png",
                "sizeBytes": 524288,
            }
        },
        "result": {
            "endpoint": "channelBanners.insert",
            "quotaCost": 50,
            "url": "https://yt3.googleusercontent.com/example-banner",
            "media": {"mimeType": "image/png", "filename": "banner.png", "contentProvided": True},
        },
        "notes": "Uploads supported banner media and returns a URL for later channel activation.",
    },
    {
        "name": "delegated_upload",
        "arguments": {
            "onBehalfOfContentOwner": "content-owner-id",
            "media": {
                "mimeType": "image/jpeg",
                "content": "<binary image content omitted>",
                "filename": "delegated-banner.jpg",
                "sizeBytes": 1048576,
            },
        },
        "result": {
            "endpoint": "channelBanners.insert",
            "quotaCost": 50,
            "delegation": {"onBehalfOfContentOwner": True},
        },
        "notes": "Uses delegated content-owner context when the caller is eligible.",
    },
    {
        "name": "missing_media",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "media"},
        "notes": "A banner image upload requires a media descriptor.",
    },
    {
        "name": "invalid_media",
        "arguments": {"media": {"mimeType": "image/gif", "content": "<binary image content omitted>"}},
        "error": {"category": "invalid_request", "field": "media.mimeType"},
        "notes": "Only image/jpeg, image/png, and application/octet-stream media types are accepted.",
    },
    {
        "name": "unsupported_channel_update",
        "arguments": {
            "media": {"mimeType": "image/png", "content": "<binary image content omitted>"},
            "body": {"brandingSettings": {"image": {"bannerExternalUrl": "https://example.invalid/banner"}}},
        },
        "error": {"category": "invalid_request", "field": "body"},
        "notes": "Activation is a separate channels.update operation.",
    },
    {
        "name": "authorization_sensitive_failure",
        "arguments": {"media": {"mimeType": "image/png", "content": "<binary image content omitted>"}},
        "error": {"category": "authorization_failed"},
        "notes": "Permission-sensitive failures expose only safe category and status details.",
    },
    {
        "name": "returned_url_boundary",
        "arguments": {"media": {"mimeType": "image/png", "content": "<binary image content omitted>"}},
        "result": {
            "endpoint": "channelBanners.insert",
            "url": "https://yt3.googleusercontent.com/example-banner",
        },
        "notes": "Use the returned URL with a separate channels.update request when activating branding.",
    },
)


class ChannelBannersInsertToolError(ValueError):
    """Represent a safe caller-facing ``channelBanners_insert`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-banners-insert error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_channel_banners_insert_transport(_execution) -> dict[str, Any]:
    """Return a safe uploaded channel banner resource for local execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Upstream-shaped channel banner resource without raw media content.
    """
    return {
        "kind": "youtube#channelBannerResource",
        "etag": "local-channel-banner",
        "url": "https://yt3.googleusercontent.com/example-banner",
    }


def _default_insert_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelBanners_insert``.

    :return: Executor with a safe local transport for uploaded banner resources.
    """
    return IntegrationExecutor(
        transport=_default_channel_banners_insert_transport,
        retry_policy=RetryPolicy(max_attempts=1),
    )


def build_channel_banners_insert_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelBanners_insert``.

    :return: Validated Layer 2 tool contract for ``channelBanners_insert``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_BANNERS_INSERT_TOOL_NAME,
        upstream_resource="channelBanners",
        upstream_method="insert",
        operation_key="channelBanners.insert",
        description=CHANNEL_BANNERS_INSERT_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CHANNEL_BANNERS_INSERT_QUOTA_COST,
        resource_family="channelBanners",
        input_contract=CHANNEL_BANNERS_INSERT_INPUT_SCHEMA,
        response_convention={
            "resultKind": "upload_result",
            "resourcePath": "item",
            "mediaResult": "safe_media_summary",
            "returnedUrlField": "url",
            "activationBoundary": "channels.update",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "item", "url", "media", "delegation"),
            preserved_upstream_fields=("kind", "etag", "url"),
            disallowed_behavior=(
                "channels_update",
                "active_banner_publication",
                "image_resizing",
                "preview_generation",
                "profile_image_update",
                "bulk_channel_branding",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.MEDIA_CONSTRAINED,
        usage_notes=CHANNEL_BANNERS_INSERT_USAGE_NOTES,
        caveats=CHANNEL_BANNERS_INSERT_CAVEATS,
    )


def _clean_text(arguments: dict[str, Any], field_name: str) -> str | None:
    """Return stripped text for a field when present.

    :param arguments: Caller-supplied mapping.
    :param field_name: Field to normalize.
    :return: Stripped text or ``None`` when absent.
    """
    value = arguments.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _media_mapping(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return the required media mapping from a banner upload request.

    :param arguments: Caller-supplied tool arguments.
    :return: Media descriptor mapping.
    :raises ChannelBannersInsertToolError: If media is missing or malformed.
    """
    media = arguments.get("media")
    if not isinstance(media, dict):
        raise ChannelBannersInsertToolError(
            "channelBanners_insert requires media.",
            category="invalid_request",
            details={"field": "media"},
        )
    return media


def _media_content_bytes(media: dict[str, Any]) -> bytes:
    """Return media content bytes for safe size validation.

    :param media: Caller-supplied media descriptor.
    :return: Media content as bytes.
    :raises ChannelBannersInsertToolError: If media content is missing.
    """
    content = media.get("content")
    if isinstance(content, bytes):
        content_bytes = content
    elif isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        content_bytes = b""
    if not content_bytes:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert requires media.content for the current upload path.",
            category="invalid_request",
            details={"field": "media.content"},
        )
    return content_bytes


def _media_summary(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a safe media summary for a banner upload request.

    :param arguments: Original tool arguments.
    :return: Safe media fields for public result surfaces.
    """
    media = _media_mapping(arguments)
    summary: dict[str, Any] = {"contentProvided": bool(media.get("content"))}
    for field in ("mimeType", "filename", "sizeBytes"):
        value = media.get(field)
        if value is not None:
            summary[field] = value
    if media.get("contentRef") is not None:
        summary["contentRefProvided"] = True
    return summary


def validate_channel_banners_insert_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> dict[str, Any]:
    """Validate ``channelBanners_insert`` arguments and return safe context.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for banner upload.
    :return: Safe media and delegation context for result mapping.
    :raises ChannelBannersInsertToolError: If arguments are invalid or require missing authorization.
    """
    unsupported = sorted(set(arguments) - set(CHANNEL_BANNERS_INSERT_INPUT_SCHEMA["properties"]))
    if unsupported:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert supports only media and onBehalfOfContentOwner.",
            category="invalid_request",
            details={"field": unsupported[0]},
        )

    media = _media_mapping(arguments)
    media_unsupported = sorted(set(media) - set(CHANNEL_BANNERS_INSERT_INPUT_SCHEMA["properties"]["media"]["properties"]))
    if media_unsupported:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert media supports only mimeType, content, contentRef, filename, and sizeBytes.",
            category="invalid_request",
            details={"field": f"media.{media_unsupported[0]}"},
        )

    mime_type = _clean_text(media, "mimeType")
    if not mime_type:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert requires media.mimeType.",
            category="invalid_request",
            details={"field": "media.mimeType"},
        )
    if mime_type not in CHANNEL_BANNERS_ALLOWED_MIME_TYPES:
        raise ChannelBannersInsertToolError(
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream.",
            category="invalid_request",
            details={"field": "media.mimeType"},
        )

    content_bytes = _media_content_bytes(media)
    declared_size = media.get("sizeBytes")
    if declared_size is not None and (
        not isinstance(declared_size, int) or declared_size < 0 or declared_size > CHANNEL_BANNERS_MAX_BYTES
    ):
        raise ChannelBannersInsertToolError(
            "media.sizeBytes must be between 0 and the 6 MB channel banner limit.",
            category="invalid_request",
            details={"field": "media.sizeBytes"},
        )
    if len(content_bytes) > CHANNEL_BANNERS_MAX_BYTES:
        raise ChannelBannersInsertToolError(
            "media.content exceeds the 6 MB channel banner limit.",
            category="invalid_request",
            details={"field": "media.content"},
        )

    if arguments.get("onBehalfOfContentOwner") is not None and not oauth_token:
        raise ChannelBannersInsertToolError(
            "Delegated channel banner upload requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"field": "onBehalfOfContentOwner"},
        )

    if not oauth_token:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"operation": "channelBanners.insert"},
        )

    context = {
        "mediaMimeType": mime_type,
        "contentProvided": True,
    }
    filename = _clean_text(media, "filename")
    if filename:
        context["filename"] = filename
    if declared_size is not None:
        context["sizeBytes"] = declared_size
    if _clean_text(arguments, "onBehalfOfContentOwner"):
        context["delegated"] = True
    return context


def _auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for channel banner upload.

    :param oauth_token: OAuth token available for channel banner upload.
    :return: OAuth-required auth context suitable for the Layer 1 wrapper.
    :raises ChannelBannersInsertToolError: If required credentials are unavailable.
    """
    if not oauth_token:
        raise ChannelBannersInsertToolError(
            "channelBanners_insert requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"operation": "channelBanners.insert"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def map_channel_banners_insert_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 banner upload response to the public Layer 2 result.

    :param response: Upstream-shaped channel banner resource returned by Layer 1.
    :param arguments: Original validated tool arguments.
    :return: Near-raw channel banner upload result with light MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "channelBanners.insert",
        "quotaCost": CHANNEL_BANNERS_INSERT_QUOTA_COST,
        "item": response,
        "media": _media_summary(arguments),
    }
    url = response.get("url") if isinstance(response, dict) else None
    if url:
        result["url"] = url
    if _clean_text(arguments, "onBehalfOfContentOwner"):
        result["delegation"] = {"onBehalfOfContentOwner": True}
    return result


def _map_insert_upstream_error(error: NormalizedUpstreamError) -> ChannelBannersInsertToolError:
    """Map a normalized upstream error to the public banner upload error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelBanners_insert`` error.
    """
    details: dict[str, Any] = {}
    if error.upstream_status:
        details["upstreamStatus"] = error.upstream_status
    reason = None
    if isinstance(error.details, dict):
        raw_reason = error.details.get("reason") or error.details.get("upstreamReason")
        if isinstance(raw_reason, str) and raw_reason:
            reason = raw_reason
            details["upstreamReason"] = raw_reason
    return ChannelBannersInsertToolError(
        str(error),
        category=_classify_insert_upstream_error(error, reason),
        details=details,
    )


def _classify_insert_upstream_error(error: NormalizedUpstreamError, reason: str | None) -> str:
    """Classify a normalized banner upload failure for public callers.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :param reason: Optional upstream reason code preserved from safe details.
    :return: Public safe error category.
    """
    lowered = f"{reason or ''} {error.message}".lower()
    if error.category == "auth" or error.upstream_status in {401, 403} or "forbidden" in lowered:
        return "authorization_failed"
    if error.category == "rate_limit" or error.upstream_status == 429:
        return "quota_exhausted"
    if error.category == "transient" or error.upstream_status in {502, 503, 504}:
        return "endpoint_unavailable"
    if (
        error.category in {"conflict", "invalid_request"}
        or error.upstream_status == 400
        or "mediabodyrequired" in lowered
        or "banneralbumfull" in lowered
        or "invalid" in lowered
    ):
        return "invalid_request"
    return "upstream_failure"


def build_channel_banners_insert_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "eligible-channel-banner-access",
):
    """Build the concrete ``channelBanners_insert`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for channel banner upload.
    :return: Callable dispatcher handler.
    """
    channel_banners_wrapper = wrapper or build_channel_banners_insert_wrapper()
    channel_banners_executor = executor or _default_insert_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelBanners_insert`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 channel banner upload result.
        :raises ChannelBannersInsertToolError: If validation, authorization, or upstream execution fails.
        """
        validate_channel_banners_insert_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context(oauth_token=oauth_token)
        try:
            response = channel_banners_wrapper.call(
                channel_banners_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_insert_upstream_error(error) from error
        except ValueError as error:
            raise ChannelBannersInsertToolError(
                str(error),
                category="invalid_request",
                details={"operation": "channelBanners.insert"},
            ) from error
        return map_channel_banners_insert_result(response, arguments)

    return handler


def build_channel_banners_insert_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "eligible-channel-banner-access",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelBanners_insert`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for channel banner upload.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_banners_insert_contract()
    return {
        "name": CHANNEL_BANNERS_INSERT_TOOL_NAME,
        "description": CHANNEL_BANNERS_INSERT_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_BANNERS_INSERT_INPUT_SCHEMA,
        "handler": build_channel_banners_insert_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "CHANNEL_BANNERS_ALLOWED_MIME_TYPES",
    "CHANNEL_BANNERS_INSERT_CALLER_EXAMPLES",
    "CHANNEL_BANNERS_INSERT_INPUT_SCHEMA",
    "CHANNEL_BANNERS_INSERT_QUOTA_COST",
    "CHANNEL_BANNERS_INSERT_TOOL_NAME",
    "CHANNEL_BANNERS_MAX_BYTES",
    "ChannelBannersInsertToolError",
    "build_channel_banners_insert_contract",
    "build_channel_banners_insert_handler",
    "build_channel_banners_insert_tool_descriptor",
    "map_channel_banners_insert_result",
    "validate_channel_banners_insert_arguments",
]
