"""Integration tests for registering and invoking ``thumbnails_set``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.thumbnails import (
    ThumbnailsSetToolError,
    build_thumbnails_set_tool_descriptor,
)


def _register_thumbnails_set(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete thumbnails set tool in a fresh dispatcher.

    :param descriptor_kwargs: Overrides passed to the descriptor builder.
    :return: Dispatcher containing only the thumbnails set descriptor.
    """
    descriptor = build_thumbnails_set_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_thumbnails_set_descriptor_registers_as_executable_tool():
    """Register and execute ``thumbnails_set`` for custom thumbnail replacement."""
    dispatcher = _register_thumbnails_set()

    result = dispatcher.call_tool(
        "thumbnails_set",
        {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}},
    )

    assert result["endpoint"] == "thumbnails.set"
    assert result["quotaCost"] == 50
    assert result["target"] == {"videoId": "video-123"}
    assert result["upload"] == {"mimeType": "image/png", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["updated"] is True
    assert "fake-image-content" not in str(result)


def test_thumbnails_set_descriptor_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for incomplete thumbnail requests."""
    dispatcher = _register_thumbnails_set()

    with pytest.raises(ValueError, match="arguments missing required field: media"):
        dispatcher.call_tool("thumbnails_set", {"videoId": "video-123"})

    descriptor = build_thumbnails_set_tool_descriptor()
    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        descriptor["handler"]({"videoId": "video-123"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "media"}


def test_thumbnails_set_descriptor_propagates_safe_access_failures():
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
                message="thumbnail access required",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"field": "videoId", "oauth_token": "secret", "raw_media": "bytes"},
            )

    dispatcher = _register_thumbnails_set(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        dispatcher.call_tool(
            "thumbnails_set",
            {"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}},
        )

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "videoId"}
