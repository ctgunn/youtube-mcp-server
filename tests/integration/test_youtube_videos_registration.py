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


class UnsafeInsertFailingWrapper:
    """Layer 1 wrapper double that raises an unsafe insert failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a normalized failure with details that must be sanitized.

        :param _executor: Ignored fake executor.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :raises NormalizedUpstreamError: Always raised for safety checks.
        """
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={
                "oauth_token": "secret",
                "raw_media": "raw-video",
                "signed_url": "https://example.invalid/upload?token=secret",
                "reason": "forbidden",
            },
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


def test_videos_insert_descriptor_registers_as_executable_upload_tool():
    """Register and execute the ``videos_insert`` descriptor through the dispatcher."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper(payload={"id": "video-123", "snippet": {"title": "Example upload"}})
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool(
        "videos_insert",
        {
            "part": "snippet,status",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            "uploadMode": "resumable",
        },
    )

    assert listed["videos_insert"]["metadata"]["upstream"]["operationKey"] == "videos.insert"
    assert listed["videos_insert"]["metadata"]["quotaCost"] == 1600
    assert listed["videos_insert"]["metadata"]["authMode"] == "oauth_required"
    assert listed["videos_insert"]["metadata"]["availabilityState"] == "media_constrained"
    assert result["endpoint"] == "videos.insert"
    assert result["quotaCost"] == 1600
    assert result["requestedParts"] == ["snippet", "status"]
    assert result["upload"] == {"mode": "resumable", "mimeType": "video/mp4", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["mutation"] == {"type": "created"}
    assert result["item"]["id"] == "video-123"
    assert "fake-video-content" not in str(result)


def test_videos_insert_descriptor_exposes_caller_metadata_and_examples():
    """Expose usage notes and examples needed before high-cost upload calls."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor()])
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    metadata = listed["videos_insert"]["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}
    metadata_text = " ".join([listed["videos_insert"]["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert "Quota cost: 1600" in metadata_text
    assert "OAuth" in metadata_text
    assert "media" in metadata_text
    assert "uploadMode" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "automatic publishing" in metadata_text
    assert {"authorized_video_creation", "missing_oauth", "out_of_scope_video_workflow"}.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (
            {"part": "snippet", "body": {"snippet": {"title": "Example"}}},
            "arguments missing required field: media",
        ),
        (
            {"part": "snippet", "media": {"mimeType": "video/mp4", "content": "data"}},
            "arguments missing required field: body",
        ),
    ],
)
def test_videos_insert_descriptor_schema_rejects_missing_required_inputs(arguments, message):
    """Reject missing required upload fields before handler execution."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match=message):
        dispatcher.call_tool("videos_insert", arguments)

    assert wrapper.calls == []


def test_videos_insert_descriptor_rejects_missing_oauth_safely():
    """Reject valid upload requests with missing OAuth before Layer 1 execution."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper, oauth_token=None)])

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            },
        )

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_videos_insert_descriptor_rejects_unsupported_upload_mode():
    """Reject unsupported upload modes through the executable descriptor."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor()])

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
                "uploadMode": "direct",
            },
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == "uploadMode"


def test_videos_insert_descriptor_propagates_sanitized_access_failures():
    """Expose sanitized insert access failures from the registered handler."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(
        tools=[build_videos_insert_tool_descriptor(wrapper=UnsafeInsertFailingWrapper())]
    )

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            },
        )

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)
    assert "raw-video" not in str(exc_info.value.details)
