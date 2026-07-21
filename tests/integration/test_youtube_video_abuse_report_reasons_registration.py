"""Integration tests for ``videoAbuseReportReasons_list`` registration."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.video_abuse_report_reasons import (
    VideoAbuseReportReasonsListToolError,
    build_video_abuse_report_reasons_list_tool_descriptor,
)


class RecordingWrapper:
    """Layer 1 wrapper double for registration-level execution."""

    def __init__(self, payload=None):
        """Initialize call history and fake payload."""
        self.payload = payload or {"items": [{"id": "S", "snippet": {"label": "Spam or misleading"}}]}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the call and return the configured payload."""
        self.calls.append({"executor": executor, "arguments": arguments, "auth_context": auth_context})
        return self.payload


class AccessFailingWrapper:
    """Layer 1 wrapper double that raises an access failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a safe-normalized authorization failure with unsafe raw details."""
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={"oauth_token": "secret", "reason": "forbidden"},
        )


def test_descriptor_registers_as_executable_video_abuse_reasons_tool():
    """Register and execute the concrete descriptor through the dispatcher."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_video_abuse_report_reasons_list_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videoAbuseReportReasons_list", {"part": "snippet", "hl": "en"})

    assert listed["videoAbuseReportReasons_list"]["metadata"]["upstream"]["operationKey"] == (
        "videoAbuseReportReasons.list"
    )
    assert listed["videoAbuseReportReasons_list"]["metadata"]["quotaCost"] == 1
    assert listed["videoAbuseReportReasons_list"]["metadata"]["authMode"] == "api_key"
    assert result["endpoint"] == "videoAbuseReportReasons.list"
    assert result["quotaCost"] == 1
    assert result["localization"] == {"hl": "en"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"] == [{"id": "S", "snippet": {"label": "Spam or misleading"}}]


def test_descriptor_schema_rejects_missing_required_fields_before_execution():
    """Reject invalid dispatcher calls before the handler reaches Layer 1."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_video_abuse_report_reasons_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="arguments missing required field: hl"):
        dispatcher.call_tool("videoAbuseReportReasons_list", {"part": "snippet"})

    assert wrapper.calls == []


def test_descriptor_propagates_safe_access_failures():
    """Expose sanitized access failures from the registered handler."""
    dispatcher = InMemoryToolDispatcher(
        tools=[build_video_abuse_report_reasons_list_tool_descriptor(wrapper=AccessFailingWrapper())]
    )

    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        dispatcher.call_tool("videoAbuseReportReasons_list", {"part": "snippet", "hl": "en"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)
