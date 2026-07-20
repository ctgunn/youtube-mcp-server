"""Unit tests for the concrete Layer 2 ``thumbnails_set`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.thumbnails import (
    THUMBNAILS_SET_INPUT_SCHEMA,
    ThumbnailsSetToolError,
    build_thumbnails_set_handler,
    build_thumbnails_set_tool_descriptor,
    map_thumbnails_set_result,
    validate_thumbnails_set_arguments,
)


class FakeThumbnailsSetWrapper:
    """Capture wrapper calls for ``thumbnails_set`` tests.

    The fake returns a representative thumbnail-set response and exposes call
    arguments for assertions without performing network I/O.
    """

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#thumbnailSetResponse",
            "etag": "etag-thumbnail",
            "thumbnailUrl": "https://yt.example/thumb.jpg",
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingThumbnailsSetWrapper:
    """Raise a configured upstream failure for ``thumbnails_set`` tests."""

    def __init__(self, error: NormalizedUpstreamError):
        """Initialize the fake wrapper with a failure.

        :param error: Normalized error raised for every call.
        """
        self.calls = []
        self.error = error

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and raise the configured failure.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for this fake wrapper.
        """
        self.calls.append((executor, arguments, auth_context))
        raise self.error


def test_thumbnails_set_schema_preserves_required_upload_inputs():
    """Expose required video id and media inputs for thumbnail setting."""
    properties = THUMBNAILS_SET_INPUT_SCHEMA["properties"]

    assert THUMBNAILS_SET_INPUT_SCHEMA["required"] == ["videoId", "media"]
    assert properties["videoId"] == {"type": "string", "minLength": 1}
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert THUMBNAILS_SET_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_thumbnails_set_arguments_accepts_upload_request():
    """Accept one supported OAuth-backed thumbnail-setting request."""
    selected = validate_thumbnails_set_arguments(
        {"videoId": " video-123 ", "media": {"mimeType": "image/png", "content": "fake-image-content"}}
    )

    assert selected == {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}}


def test_map_thumbnails_set_result_preserves_safe_context():
    """Map a thumbnail-set response into a safe near-raw upload result."""
    result = map_thumbnails_set_result(
        {"kind": "youtube#thumbnailSetResponse", "thumbnailUrl": "https://yt.example/thumb.jpg"},
        {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}},
    )

    assert result["endpoint"] == "thumbnails.set"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["target"] == {"videoId": "video-123"}
    assert result["upload"] == {"mimeType": "image/png", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["upstream"]["thumbnailUrl"] == "https://yt.example/thumb.jpg"
    assert "fake-image-content" not in str(result)


def test_map_thumbnails_set_result_handles_sparse_success():
    """Preserve target and upload context when upstream success is sparse."""
    result = map_thumbnails_set_result(
        {},
        {"videoId": "video-123", "media": {"mimeType": "image/jpeg", "content": "fake-image-content"}},
    )

    assert result["endpoint"] == "thumbnails.set"
    assert result["updated"] is True
    assert result["target"] == {"videoId": "video-123"}
    assert result["upload"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["upstream"] == {}
    assert "thumbnailUrl" not in result


def test_build_thumbnails_set_handler_invokes_wrapper_once():
    """Invoke the Layer 1 wrapper once for valid thumbnail-setting requests."""
    wrapper = FakeThumbnailsSetWrapper()
    executor = object()
    handler = build_thumbnails_set_handler(wrapper=wrapper, executor=executor, oauth_token="token")

    result = handler({"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}})

    assert len(wrapper.calls) == 1
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == {
        "videoId": "video-123",
        "media": {"mimeType": "image/png", "content": "fake-image-content"},
    }
    assert wrapper.calls[0][2].requires_oauth_access() is True
    assert result["endpoint"] == "thumbnails.set"
    assert result["target"] == {"videoId": "video-123"}


def test_build_thumbnails_set_tool_descriptor_is_executable():
    """Build a descriptor whose handler can execute a representative set request."""
    wrapper = FakeThumbnailsSetWrapper(response={})
    descriptor = build_thumbnails_set_tool_descriptor(wrapper=wrapper, executor=object(), oauth_token="token")

    result = descriptor["handler"](
        {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}}
    )

    assert descriptor["name"] == "thumbnails_set"
    assert result["updated"] is True


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"media": {"mimeType": "image/png", "content": "fake-image-content"}}, "videoId"),
        ({"videoId": "", "media": {"mimeType": "image/png", "content": "fake-image-content"}}, "videoId"),
        ({"videoId": 123, "media": {"mimeType": "image/png", "content": "fake-image-content"}}, "videoId"),
        ({"videoId": "video-123"}, "media"),
        ({"videoId": "video-123", "media": "raw"}, "media"),
        ({"videoId": "video-123", "media": {"content": "fake-image-content"}}, "media.mimeType"),
        ({"videoId": "video-123", "media": {"mimeType": "image/png"}}, "media.content"),
        ({"videoId": "video-123", "media": {"mimeType": "image/png", "content": ""}}, "media.content"),
        (
            {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake", "raw_media": "secret"}},
            "media.raw_media",
        ),
        (
            {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake"}, "generateThumbnail": True},
            "generateThumbnail",
        ),
    ],
)
def test_validate_thumbnails_set_arguments_rejects_invalid_requests(arguments, field):
    """Reject invalid or out-of-scope thumbnail-setting request shapes."""
    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        validate_thumbnails_set_arguments(arguments)

    assert exc_info.value.category in {"invalid_request", "unsupported_upload"}
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "extra_field",
    [
        "videoUrl",
        "q",
        "channelId",
        "playlistId",
        "body",
        "generateThumbnail",
        "transformImage",
        "pageToken",
        "includeAnalytics",
        "rankResults",
        "summarize",
        "enrich",
    ],
)
def test_validate_thumbnails_set_arguments_rejects_out_of_scope_fields(extra_field):
    """Reject fields that imply lookup, generation, analytics, or enrichment behavior."""
    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        validate_thumbnails_set_arguments(
            {
                "videoId": "video-123",
                "media": {"mimeType": "image/png", "content": "fake-image-content"},
                extra_field: True,
            }
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": extra_field}


def test_validate_thumbnails_set_arguments_rejects_unsupported_media_type():
    """Reject upload content whose media type is outside the supported boundary."""
    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        validate_thumbnails_set_arguments(
            {"videoId": "video-123", "media": {"mimeType": "text/plain", "content": "fake-image-content"}}
        )

    assert exc_info.value.category == "unsupported_upload"
    assert exc_info.value.details == {"field": "media.mimeType", "mimeType": "text/plain"}


def test_build_thumbnails_set_handler_rejects_missing_oauth_before_wrapper_call():
    """Reject missing OAuth access before invoking Layer 1."""
    wrapper = FakeThumbnailsSetWrapper()
    handler = build_thumbnails_set_handler(wrapper=wrapper, executor=object(), oauth_token="")

    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        handler({"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}
    assert wrapper.calls == []


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("authorization", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("target_video", "target_video_failed"),
        ("not_found", "target_video_failed"),
        ("resource_not_found", "target_video_failed"),
        ("media_eligibility", "unsupported_upload"),
        ("upload_rejected", "upload_rejected"),
        ("quota", "quota_exhausted"),
        ("rate_limit", "quota_exhausted"),
        ("invalid_request", "invalid_request"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "endpoint_unavailable"),
        ("weird", "upstream_failure"),
    ],
)
def test_build_thumbnails_set_handler_maps_upstream_errors(upstream_category, expected_category):
    """Map upstream failure categories into safe thumbnail-setting errors."""
    error = NormalizedUpstreamError(
        message="upstream failed",
        category=upstream_category,
        retryable=False,
        upstream_status=400,
        details={
            "videoId": "video-123",
            "mimeType": "image/png",
            "oauth_token": "secret",
            "raw_media": "secret-bytes",
            "stack": "traceback",
        },
    )
    wrapper = FailingThumbnailsSetWrapper(error)
    handler = build_thumbnails_set_handler(wrapper=wrapper, executor=object(), oauth_token="token")

    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        handler({"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"videoId": "video-123", "mimeType": "image/png"}


def test_thumbnails_set_error_sanitizes_raw_upload_details():
    """Remove credentials and raw media details from caller-facing failures."""
    error = ThumbnailsSetToolError(
        "bad upload",
        category="unsupported_upload",
        details={
            "field": "media",
            "oauth_token": "secret",
            "authorization": "Bearer secret",
            "raw_media": "secret-bytes",
            "raw_body": {"content": "secret"},
            "stack": "traceback",
        },
    )

    assert error.details == {"field": "media"}
    assert "secret" not in str(error.details)
