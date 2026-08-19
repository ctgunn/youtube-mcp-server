"""Integration tests for registering and invoking ``watermarks`` tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.watermarks import (
    WatermarksSetToolError,
    WatermarksUnsetToolError,
    build_watermarks_set_tool_descriptor,
    build_watermarks_unset_tool_descriptor,
)

VALID_WATERMARKS_SET_ARGS = {
    "channelId": "UC123",
    "body": {
        "timing": {"type": "offsetFromStart", "offsetMs": 0},
        "position": {"type": "corner", "cornerPosition": "topRight"},
    },
    "media": {"mimeType": "image/png", "content": "fake-watermark-content"},
}

VALID_WATERMARKS_UNSET_ARGS = {"channelId": "UC123"}


def _register_watermarks_set(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete watermarks set tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the watermarks set descriptor.
    """
    descriptor = build_watermarks_set_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_watermarks_unset(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete watermarks unset tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the watermarks unset descriptor.
    """
    descriptor = build_watermarks_unset_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_watermarks_set_descriptor_registers_as_executable_tool():
    """Register and execute ``watermarks_set`` for a channel watermark update."""
    dispatcher = _register_watermarks_set()

    result = dispatcher.call_tool("watermarks_set", VALID_WATERMARKS_SET_ARGS)

    assert result["endpoint"] == "watermarks.set"
    assert result["quotaCost"] == 50
    assert result["target"] == {"channelId": "UC123"}
    assert result["upload"] == {"mimeType": "image/png", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["availability"] == {"state": "owner_only"}
    assert result["updated"] is True
    assert "fake-watermark-content" not in str(result)


def test_watermarks_set_descriptor_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for incomplete watermark requests."""
    dispatcher = _register_watermarks_set()

    with pytest.raises(ValueError, match="arguments missing required field: media"):
        dispatcher.call_tool(
            "watermarks_set",
            {"channelId": "UC123", "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}}},
        )

    descriptor = build_watermarks_set_tool_descriptor()
    with pytest.raises(WatermarksSetToolError) as exc_info:
        descriptor["handler"]({"channelId": "UC123"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "body"}


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"body": VALID_WATERMARKS_SET_ARGS["body"], "media": VALID_WATERMARKS_SET_ARGS["media"]}, "channelId"),
        ({"channelId": 123, "body": VALID_WATERMARKS_SET_ARGS["body"], "media": VALID_WATERMARKS_SET_ARGS["media"]}, "channelId"),
        ({"channelId": "UC123", "media": VALID_WATERMARKS_SET_ARGS["media"]}, "body"),
        ({"channelId": "UC123", "body": VALID_WATERMARKS_SET_ARGS["body"]}, "media"),
        ({**VALID_WATERMARKS_SET_ARGS, "onBehalfOfContentOwner": "owner"}, "onBehalfOfContentOwner"),
        ({**VALID_WATERMARKS_SET_ARGS, "rankResults": True}, "rankResults"),
    ],
)
def test_watermarks_set_descriptor_rejects_invalid_or_unsupported_requests(arguments, field):
    """Reject invalid dispatcher requests with safe field-specific details."""
    descriptor = build_watermarks_set_tool_descriptor()

    with pytest.raises(WatermarksSetToolError) as exc_info:
        descriptor["handler"](arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": field}


def test_watermarks_set_descriptor_propagates_safe_access_failures():
    """Propagate safe upstream access failures from the registered handler."""

    class FailingWrapper:
        """Raise an access failure from a registered dispatcher tool."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized access failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="watermark access required",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"field": "channelId", "oauth_token": "secret", "raw_media": "bytes"},
            )

    dispatcher = _register_watermarks_set(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(WatermarksSetToolError) as exc_info:
        dispatcher.call_tool("watermarks_set", VALID_WATERMARKS_SET_ARGS)

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "channelId"}


def test_watermarks_set_descriptor_rejects_missing_oauth_without_wrapper_call():
    """Reject missing OAuth configuration before the wrapper can execute."""
    descriptor = build_watermarks_set_tool_descriptor(wrapper=object(), executor=object(), oauth_token="")

    with pytest.raises(WatermarksSetToolError) as exc_info:
        descriptor["handler"](VALID_WATERMARKS_SET_ARGS)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}


def test_watermarks_unset_descriptor_registers_as_executable_tool():
    """Register and execute ``watermarks_unset`` for a channel watermark removal."""
    dispatcher = _register_watermarks_unset()

    result = dispatcher.call_tool("watermarks_unset", VALID_WATERMARKS_UNSET_ARGS)

    assert result["endpoint"] == "watermarks.unset"
    assert result["quotaCost"] == 50
    assert result["target"] == {"channelId": "UC123"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["availability"] == {"state": "owner_only"}
    assert result["noUpload"] == {"bodyAccepted": False, "mediaAccepted": False}
    assert result["removed"] is True


def test_watermarks_unset_descriptor_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for incomplete removal requests."""
    dispatcher = _register_watermarks_unset()

    with pytest.raises(ValueError, match="arguments missing required field: channelId"):
        dispatcher.call_tool("watermarks_unset", {})

    descriptor = build_watermarks_unset_tool_descriptor()
    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        descriptor["handler"]({"channelId": "UC123", "media": {"content": "fake-watermark-content"}})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "media"}


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "channelId"),
        ({"channelId": 123}, "channelId"),
        ({"channelId": "UC123,UC456"}, "channelId"),
        ({**VALID_WATERMARKS_UNSET_ARGS, "body": {}}, "body"),
        ({**VALID_WATERMARKS_UNSET_ARGS, "media": {"mimeType": "image/png"}}, "media"),
        ({**VALID_WATERMARKS_UNSET_ARGS, "onBehalfOfContentOwner": "owner"}, "onBehalfOfContentOwner"),
        ({**VALID_WATERMARKS_UNSET_ARGS, "rankResults": True}, "rankResults"),
    ],
)
def test_watermarks_unset_descriptor_rejects_invalid_or_unsupported_requests(arguments, field):
    """Reject invalid dispatcher unset requests with safe field-specific details."""
    descriptor = build_watermarks_unset_tool_descriptor()

    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        descriptor["handler"](arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": field}


def test_watermarks_unset_descriptor_propagates_safe_access_failures():
    """Propagate safe upstream access failures from the registered unset handler."""

    class FailingWrapper:
        """Raise an access failure from a registered dispatcher tool."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized access failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="watermark removal access required",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"field": "channelId", "oauth_token": "secret", "raw_media": "bytes"},
            )

    dispatcher = _register_watermarks_unset(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        dispatcher.call_tool("watermarks_unset", VALID_WATERMARKS_UNSET_ARGS)

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "channelId"}


def test_watermarks_unset_descriptor_rejects_missing_oauth_without_wrapper_call():
    """Reject missing OAuth configuration before the unset wrapper can execute."""
    descriptor = build_watermarks_unset_tool_descriptor(wrapper=object(), executor=object(), oauth_token="")

    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        descriptor["handler"](VALID_WATERMARKS_UNSET_ARGS)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth", "authMode": "oauth_required"}
