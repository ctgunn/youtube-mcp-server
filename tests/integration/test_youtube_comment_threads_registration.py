"""Integration tests for registering concrete Layer 2 ``commentThreads`` tools."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_list_tool_descriptor


def _register_comment_threads_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete comment-thread list tool in a fresh dispatcher."""
    descriptor = build_comment_threads_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_comment_threads_list_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, selectors, pagination, and caveats in registration."""
    dispatcher = _register_comment_threads_list()

    [listed] = dispatcher.list_tools()
    metadata = listed["metadata"]
    metadata_text = " ".join([listed["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "commentThreads_list"
    assert metadata["upstream"]["operationKey"] == "commentThreads.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"videoId", "allThreadsRelatedToChannelId", "id", "maxResults", "pageToken", "textFormat"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert "allThreadsRelatedToChannelId" in metadata_text
    assert "moderationStatus" in metadata_text


def test_comment_threads_list_descriptor_registers_as_executable_tool_for_video_lookup():
    """Register and execute ``commentThreads_list`` video lookup through the dispatcher."""
    dispatcher = _register_comment_threads_list()

    result = dispatcher.call_tool("commentThreads_list", {"part": "snippet", "videoId": "video-123"})

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-video-123", "snippet": {"videoId": "video-123"}}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "videoId"}


def test_comment_threads_list_descriptor_registers_as_executable_tool_for_channel_lookup():
    """Register and execute ``commentThreads_list`` channel lookup through the dispatcher."""
    dispatcher = _register_comment_threads_list()

    result = dispatcher.call_tool(
        "commentThreads_list",
        {
            "part": "snippet",
            "allThreadsRelatedToChannelId": "channel-123",
            "maxResults": 2,
            "textFormat": "plainText",
        },
    )

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-channel-123", "snippet": {"channelId": "channel-123"}}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "allThreadsRelatedToChannelId"}
    assert result["textFormat"] == "plainText"


def test_comment_threads_list_descriptor_registers_as_executable_tool_for_id_lookup():
    """Register and execute ``commentThreads_list`` ID lookup through the dispatcher."""
    dispatcher = _register_comment_threads_list()

    result = dispatcher.call_tool("commentThreads_list", {"part": "id,snippet", "id": "thread-123"})

    assert result["endpoint"] == "commentThreads.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "thread-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}


def test_comment_threads_list_dispatcher_rejects_invalid_selector_request():
    """Reject invalid selector combinations through dispatcher invocation."""
    dispatcher = _register_comment_threads_list()

    try:
        dispatcher.call_tool("commentThreads_list", {"part": "snippet", "videoId": "video-123", "id": "thread-123"})
    except ValueError as error:
        assert "requires exactly one selector" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid selector request to fail")


def test_comment_threads_list_dispatcher_rejects_unsupported_id_modifier():
    """Reject modifiers that upstream disallows with ID lookup."""
    dispatcher = _register_comment_threads_list()

    try:
        dispatcher.call_tool("commentThreads_list", {"part": "snippet", "id": "thread-123", "maxResults": 25})
    except ValueError as error:
        assert "does not support maxResults with id" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected unsupported id modifier to fail")


def test_default_registry_includes_executable_comment_threads_list_tool():
    """Register ``commentThreads_list`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "commentThreads_list" in listed
    metadata = listed["commentThreads_list"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "commentThreads.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
