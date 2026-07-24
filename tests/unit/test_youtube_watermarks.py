"""Unit tests for the concrete Layer 2 ``watermarks_set`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.watermarks import (
    WATERMARKS_SET_INPUT_SCHEMA,
    WATERMARKS_SET_MAX_BYTES,
    WATERMARKS_SET_QUOTA_COST,
    WatermarksSetToolError,
    build_watermarks_set_handler,
    build_watermarks_set_tool_descriptor,
    map_watermarks_set_result,
    validate_watermarks_set_arguments,
)


VALID_WATERMARKS_SET_ARGS = {
    "channelId": "UC123",
    "body": {
        "timing": {"type": "offsetFromStart", "offsetMs": 0},
        "position": {"type": "corner", "cornerPosition": "topRight"},
        "targetChannelId": "UC-target",
    },
    "media": {"mimeType": "image/png", "content": "fake-watermark-content"},
}


def _valid_watermarks_set_args(**overrides):
    """Build a valid watermark-set request with optional top-level overrides.

    :param overrides: Top-level request fields to replace or add.
    :return: Valid request mapping for unit tests.
    """
    arguments = {
        "channelId": VALID_WATERMARKS_SET_ARGS["channelId"],
        "body": {
            "timing": dict(VALID_WATERMARKS_SET_ARGS["body"]["timing"]),
            "position": dict(VALID_WATERMARKS_SET_ARGS["body"]["position"]),
            "targetChannelId": VALID_WATERMARKS_SET_ARGS["body"]["targetChannelId"],
        },
        "media": dict(VALID_WATERMARKS_SET_ARGS["media"]),
    }
    arguments.update(overrides)
    return arguments


class FakeWatermarksSetWrapper:
    """Capture wrapper calls for ``watermarks_set`` tests.

    The fake returns a representative sparse watermark-set response and exposes
    call arguments for assertions without performing network I/O.
    """

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {"sourceOperation": "watermarks.set", "status": 204}

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingWatermarksSetWrapper:
    """Raise a configured upstream failure for ``watermarks_set`` tests."""

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


def test_watermarks_set_schema_preserves_required_upload_inputs():
    """Expose required channel, metadata, and upload inputs for watermark setting."""
    properties = WATERMARKS_SET_INPUT_SCHEMA["properties"]

    assert WATERMARKS_SET_INPUT_SCHEMA["required"] == ["channelId", "body", "media"]
    assert properties["channelId"] == {"type": "string", "minLength": 1}
    assert properties["body"]["required"] == ["timing", "position"]
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert properties["media"]["properties"]["mimeType"]["enum"] == [
        "image/jpeg",
        "image/png",
        "application/octet-stream",
    ]
    assert WATERMARKS_SET_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_watermarks_set_arguments_accepts_authorized_upload_request():
    """Accept one supported OAuth-backed watermark-setting request."""
    selected = validate_watermarks_set_arguments(_valid_watermarks_set_args(channelId=" UC123 "))

    assert selected["channelId"] == "UC123"
    assert selected["body"]["timing"] == {"type": "offsetFromStart", "offsetMs": 0}
    assert selected["body"]["position"] == {"type": "corner", "cornerPosition": "topRight"}
    assert selected["body"]["targetChannelId"] == "UC-target"
    assert selected["media"] == {"mimeType": "image/png", "content": "fake-watermark-content"}


def test_map_watermarks_set_result_preserves_safe_acknowledgment_context():
    """Map a watermark-set response into a safe sparse mutation acknowledgment."""
    result = map_watermarks_set_result({"sourceOperation": "watermarks.set", "status": 204}, VALID_WATERMARKS_SET_ARGS)

    assert result["endpoint"] == "watermarks.set"
    assert result["sourceOperation"] == "watermarks.set"
    assert result["quotaCost"] == WATERMARKS_SET_QUOTA_COST == 50
    assert result["updated"] is True
    assert result["target"] == {"channelId": "UC123"}
    assert result["metadata"] == {
        "hasTiming": True,
        "hasPosition": True,
        "targetChannelId": "UC-target",
    }
    assert result["upload"] == {"mimeType": "image/png", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["availability"] == {"state": "owner_only"}
    assert result["acknowledgment"]["accepted"] is True
    assert "fake-watermark-content" not in str(result)


def test_map_watermarks_set_result_handles_sparse_success():
    """Preserve target, metadata, and upload context when upstream success is sparse."""
    result = map_watermarks_set_result({}, _valid_watermarks_set_args(media={"mimeType": "image/jpeg", "content": "x"}))

    assert result["endpoint"] == "watermarks.set"
    assert result["updated"] is True
    assert result["target"] == {"channelId": "UC123"}
    assert result["upload"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["acknowledgment"]["status"] == "watermark_set"
    assert result["upstream"] == {}


def test_build_watermarks_set_handler_invokes_wrapper_once():
    """Invoke the Layer 1 wrapper once for valid watermark-setting requests."""
    wrapper = FakeWatermarksSetWrapper()
    executor = object()
    handler = build_watermarks_set_handler(wrapper=wrapper, executor=executor, oauth_token="token")

    result = handler(VALID_WATERMARKS_SET_ARGS)

    assert len(wrapper.calls) == 1
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == VALID_WATERMARKS_SET_ARGS
    assert wrapper.calls[0][2].requires_oauth_access() is True
    assert result["endpoint"] == "watermarks.set"
    assert result["target"] == {"channelId": "UC123"}


def test_build_watermarks_set_tool_descriptor_is_executable():
    """Build a descriptor whose handler can execute a representative set request."""
    wrapper = FakeWatermarksSetWrapper(response={})
    descriptor = build_watermarks_set_tool_descriptor(wrapper=wrapper, executor=object(), oauth_token="token")

    result = descriptor["handler"](VALID_WATERMARKS_SET_ARGS)

    assert descriptor["name"] == "watermarks_set"
    assert result["updated"] is True


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ("not-object", "arguments"),
        ({"body": VALID_WATERMARKS_SET_ARGS["body"], "media": VALID_WATERMARKS_SET_ARGS["media"]}, "channelId"),
        (_valid_watermarks_set_args(channelId=""), "channelId"),
        (_valid_watermarks_set_args(channelId=123), "channelId"),
        (_valid_watermarks_set_args(channelId="UC123,UC456"), "channelId"),
        (_valid_watermarks_set_args(body=None), "body"),
        (_valid_watermarks_set_args(body="metadata"), "body"),
        (_valid_watermarks_set_args(body={"position": {"type": "corner"}}), "body.timing"),
        (_valid_watermarks_set_args(body={"timing": {}, "position": {"type": "corner"}}), "body.timing"),
        (_valid_watermarks_set_args(body={"timing": {"type": "offsetFromStart"}}), "body.position"),
        (_valid_watermarks_set_args(body={"timing": {"type": "offsetFromStart"}, "position": {}}), "body.position"),
        (
            _valid_watermarks_set_args(
                body={
                    "timing": {"type": "offsetFromStart"},
                    "position": {"type": "corner"},
                    "targetChannelId": 123,
                }
            ),
            "body.targetChannelId",
        ),
        (_valid_watermarks_set_args(media=None), "media"),
        (_valid_watermarks_set_args(media="raw"), "media"),
        (_valid_watermarks_set_args(media={"content": "fake"}), "media.mimeType"),
        (_valid_watermarks_set_args(media={"mimeType": "text/plain", "content": "fake"}), "media.mimeType"),
        (_valid_watermarks_set_args(media={"mimeType": "image/png"}), "media.content"),
        (_valid_watermarks_set_args(media={"mimeType": "image/png", "content": ""}), "media.content"),
        (
            _valid_watermarks_set_args(media={"mimeType": "image/png", "content": "fake", "raw_media": "secret"}),
            "media.raw_media",
        ),
        (_valid_watermarks_set_args(media={"mimeType": "image/png", "content": "x" * (WATERMARKS_SET_MAX_BYTES + 1)}), "media.content"),
        (_valid_watermarks_set_args(onBehalfOfContentOwner="owner-123"), "onBehalfOfContentOwner"),
        (_valid_watermarks_set_args(videoId="video-123"), "videoId"),
    ],
)
def test_validate_watermarks_set_arguments_rejects_invalid_requests(arguments, field):
    """Reject invalid or out-of-scope watermark-setting request shapes."""
    with pytest.raises(WatermarksSetToolError) as exc_info:
        validate_watermarks_set_arguments(arguments)

    assert exc_info.value.category in {"invalid_request", "unsupported_upload"}
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "extra_field",
    [
        "id",
        "ids",
        "channelIds",
        "mine",
        "part",
        "pageToken",
        "unset",
        "removeWatermark",
        "lookupWatermark",
        "brandingSettings",
        "banner",
        "thumbnail",
        "videoId",
        "captionId",
        "playlistId",
        "commentId",
        "transcript",
        "analytics",
        "recommend",
        "rankResults",
        "summarize",
        "enrich",
        "autoBranding",
    ],
)
def test_validate_watermarks_set_arguments_rejects_out_of_scope_fields(extra_field):
    """Reject fields that imply unsupported watermark, lookup, or enrichment behavior."""
    with pytest.raises(WatermarksSetToolError) as exc_info:
        validate_watermarks_set_arguments(_valid_watermarks_set_args(**{extra_field: True}))

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": extra_field}


def test_build_watermarks_set_handler_rejects_missing_oauth_before_wrapper_call():
    """Reject missing OAuth access before invoking Layer 1."""
    wrapper = FakeWatermarksSetWrapper()
    handler = build_watermarks_set_handler(wrapper=wrapper, executor=object(), oauth_token="")

    with pytest.raises(WatermarksSetToolError) as exc_info:
        handler(VALID_WATERMARKS_SET_ARGS)

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
        ("forbidden", "authorization_failed"),
        ("policy_restricted", "authorization_failed"),
        ("target_channel", "target_channel_failed"),
        ("not_found", "target_channel_failed"),
        ("resource_not_found", "target_channel_failed"),
        ("media_eligibility", "unsupported_upload"),
        ("upload_rejected", "upload_rejected"),
        ("quota", "quota_exhausted"),
        ("rate_limit", "quota_exhausted"),
        ("invalid_request", "invalid_request"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("conflict", "conflict"),
        ("refused", "upstream_refused"),
        ("weird", "upstream_failure"),
    ],
)
def test_build_watermarks_set_handler_maps_safe_upstream_failures(upstream_category, expected_category):
    """Map normalized upstream failures to stable safe categories."""
    error = NormalizedUpstreamError(
        message="watermark update failed",
        category=upstream_category,
        retryable=False,
        upstream_status=403,
        details={
            "channelId": "UC123",
            "oauth_token": "secret",
            "authorization": "Bearer secret",
            "raw_media": "fake-watermark-content",
            "content": "fake-watermark-content",
            "stack_trace": "private",
        },
    )
    handler = build_watermarks_set_handler(
        wrapper=FailingWatermarksSetWrapper(error),
        executor=object(),
        oauth_token="token",
    )

    with pytest.raises(WatermarksSetToolError) as exc_info:
        handler(VALID_WATERMARKS_SET_ARGS)

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"channelId": "UC123"}
    assert "secret" not in str(exc_info.value.details)
    assert "fake-watermark-content" not in str(exc_info.value.details)
