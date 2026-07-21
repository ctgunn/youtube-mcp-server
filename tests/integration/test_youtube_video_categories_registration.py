"""Integration tests for ``videoCategories_list`` registration."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.video_categories import (
    VideoCategoriesListToolError,
    build_video_categories_list_tool_descriptor,
)


class RecordingWrapper:
    """Layer 1 wrapper double for registration-level execution."""

    def __init__(self, payload=None):
        """Initialize call history and fake payload.

        :param payload: Optional payload returned by each wrapper call.
        """
        self.payload = payload or {"items": [{"id": "10", "snippet": {"title": "Music", "assignable": True}}]}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the call and return the configured payload.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: API-key auth context supplied by the handler.
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
        :param auth_context: API-key auth context supplied by the handler.
        :raises NormalizedUpstreamError: Always raised for access mapping.
        """
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={"oauth_token": "secret", "reason": "forbidden"},
        )


def test_descriptor_registers_as_executable_video_categories_tool():
    """Register and execute the concrete descriptor through the dispatcher."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_video_categories_list_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videoCategories_list", {"part": "snippet", "regionCode": "US"})

    assert listed["videoCategories_list"]["metadata"]["upstream"]["operationKey"] == "videoCategories.list"
    assert listed["videoCategories_list"]["metadata"]["quotaCost"] == 1
    assert listed["videoCategories_list"]["metadata"]["authMode"] == "api_key"
    assert result["endpoint"] == "videoCategories.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"mode": "regionCode", "regionCode": "US"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"] == [{"id": "10", "snippet": {"title": "Music", "assignable": True}}]


def test_descriptor_schema_rejects_missing_part_before_execution():
    """Reject missing required part before the handler reaches Layer 1."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_video_categories_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="arguments missing required field: part"):
        dispatcher.call_tool("videoCategories_list", {"regionCode": "US"})

    assert wrapper.calls == []


def test_descriptor_schema_rejects_missing_selector_before_execution():
    """Reject missing selector through dispatcher schema validation."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_video_categories_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="required combinations"):
        dispatcher.call_tool("videoCategories_list", {"part": "snippet"})

    assert wrapper.calls == []


def test_descriptor_propagates_safe_access_failures():
    """Expose sanitized access failures from the registered handler."""
    dispatcher = InMemoryToolDispatcher(tools=[build_video_categories_list_tool_descriptor(wrapper=AccessFailingWrapper())])

    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        dispatcher.call_tool("videoCategories_list", {"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)
