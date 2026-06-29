"""Integration tests for registering concrete Layer 2 ``commentThreads`` tools."""

import pytest

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


def _register_commentThreads_insert(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete comment-thread insert tool in a fresh dispatcher."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_insert_tool_descriptor

    descriptor = build_comment_threads_insert_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _valid_commentThreads_insert_arguments() -> dict:
    """Return a representative valid ``commentThreads_insert`` request."""
    return {
        "part": "snippet",
        "body": {
            "snippet": {
                "channelId": "channel-123",
                "videoId": "video-123",
                "topLevelComment": {"snippet": {"textOriginal": "Great walkthrough."}},
            }
        },
    }


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


def test_commentThreads_insert_registration_exposes_metadata_and_usage_notes():
    """Expose quota, OAuth, target, body, and caveats in registration."""
    dispatcher = _register_commentThreads_insert()

    [listed] = dispatcher.list_tools()
    metadata = listed["metadata"]
    metadata_text = " ".join([listed["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "commentThreads_insert"
    assert metadata["upstream"]["operationKey"] == "commentThreads.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body.snippet.channelId" in metadata_text
    assert "body.snippet.videoId" in metadata_text


def test_commentThreads_insert_descriptor_registers_as_executable_tool_for_top_level_create():
    """Register and execute ``commentThreads_insert`` through the dispatcher."""
    dispatcher = _register_commentThreads_insert()

    result = dispatcher.call_tool("commentThreads_insert", _valid_commentThreads_insert_arguments())

    assert result["endpoint"] == "commentThreads.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["target"] == {"channelId": "channel-123", "videoId": "video-123"}
    assert result["item"]["id"] == "thread-video-123"


@pytest.mark.parametrize(
    ("mutator", "match"),
    [
        (lambda arguments: arguments["body"]["snippet"].pop("channelId"), "body.snippet.channelId"),
        (lambda arguments: arguments["body"]["snippet"].pop("videoId"), "body.snippet.videoId"),
        (
            lambda arguments: arguments["body"]["snippet"]["topLevelComment"]["snippet"].update(
                {"textOriginal": " "}
            ),
            "body.snippet.topLevelComment.snippet.textOriginal",
        ),
        (lambda arguments: arguments["body"]["snippet"].update({"parentId": "comment-parent-123"}), "parentId"),
        (lambda arguments: arguments.update({"moderationStatus": "published"}), "unsupported field"),
        (lambda arguments: arguments.update({"part": "contentDetails"}), "part"),
    ],
)
def test_commentThreads_insert_dispatcher_rejects_invalid_create_shapes(mutator, match):
    """Reject invalid ``commentThreads_insert`` shapes through dispatcher invocation."""
    dispatcher = _register_commentThreads_insert()
    arguments = _valid_commentThreads_insert_arguments()
    mutator(arguments)

    with pytest.raises(ValueError, match=match):
        dispatcher.call_tool("commentThreads_insert", arguments)


def test_commentThreads_insert_dispatcher_rejects_missing_oauth():
    """Reject ``commentThreads_insert`` calls when OAuth access is unavailable."""
    dispatcher = _register_commentThreads_insert(oauth_token=None)

    with pytest.raises(ValueError, match="requires OAuth access"):
        dispatcher.call_tool("commentThreads_insert", _valid_commentThreads_insert_arguments())


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
