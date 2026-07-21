"""Integration tests for ``videos_list`` registration."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.videos import VideosListToolError, build_videos_list_tool_descriptor


class RecordingWrapper:
    """Layer 1 wrapper double for registration-level execution."""

    def __init__(self, payload=None):
        """Initialize call history and fake payload.

        :param payload: Optional payload returned by each wrapper call.
        """
        self.payload = payload or {"items": [{"id": "abc123", "snippet": {"title": "Example"}}]}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the call and return the configured payload.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :return: Configured fake payload.
        """
        self.calls.append({"executor": executor, "arguments": arguments, "auth_context": auth_context})
        return self.payload


class AccessFailingWrapper:
    """Layer 1 wrapper double that raises an access failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a safe-normalized authorization failure with unsafe raw details.

        :param _executor: Ignored fake executor.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :raises NormalizedUpstreamError: Always raised for access mapping.
        """
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={"oauth_token": "secret", "reason": "forbidden"},
        )


def test_descriptor_registers_as_executable_videos_tool():
    """Register and execute the concrete descriptor through the dispatcher."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videos_list", {"part": "snippet", "id": "abc123"})

    assert listed["videos_list"]["metadata"]["upstream"]["operationKey"] == "videos.list"
    assert listed["videos_list"]["metadata"]["quotaCost"] == 1
    assert listed["videos_list"]["metadata"]["authMode"] == "mixed/conditional"
    assert result["endpoint"] == "videos.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"mode": "id", "id": ["abc123"]}
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert result["items"] == [{"id": "abc123", "snippet": {"title": "Example"}}]


def test_descriptor_schema_rejects_missing_part_before_execution():
    """Reject missing required part before the handler reaches Layer 1."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="arguments missing required field: part"):
        dispatcher.call_tool("videos_list", {"id": "abc123"})

    assert wrapper.calls == []


def test_descriptor_schema_rejects_missing_selector_before_execution():
    """Reject missing selector through dispatcher schema validation."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="required combinations"):
        dispatcher.call_tool("videos_list", {"part": "snippet"})

    assert wrapper.calls == []


def test_descriptor_propagates_safe_access_failures():
    """Expose sanitized access failures from the registered handler."""
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=AccessFailingWrapper())])

    with pytest.raises(VideosListToolError) as exc_info:
        dispatcher.call_tool("videos_list", {"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)
