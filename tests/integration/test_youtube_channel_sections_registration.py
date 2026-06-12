"""Integration tests for registering concrete Layer 2 ``channelSections`` tools."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher


def test_default_registry_includes_executable_channel_sections_list_tool():
    """Register ``channelSections_list`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelSections_list" in listed
    metadata = listed["channelSections_list"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "channelSections.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"


def test_default_registry_executes_channel_sections_list_empty_result():
    """Invoke the default ``channelSections_list`` handler through the dispatcher."""
    dispatcher = InMemoryToolDispatcher()

    result = dispatcher.call_tool("channelSections_list", {"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "channelSections.list"
    assert result["quotaCost"] == 1
    assert result["items"] == []
    assert result["selector"] == {"name": "channelId"}


def test_default_registry_includes_executable_channel_sections_insert_tool():
    """Register ``channelSections_insert`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelSections_insert" in listed
    metadata = listed["channelSections_insert"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "channelSections.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["responseConvention"]["resultKind"] == "created_resource"


def test_default_registry_executes_channel_sections_insert_created_result():
    """Invoke the default ``channelSections_insert`` handler through the dispatcher."""
    dispatcher = InMemoryToolDispatcher()
    body = {
        "snippet": {"type": "singlePlaylist", "channelId": "UC123", "title": "Uploads"},
        "contentDetails": {"playlists": ["PL123"]},
    }

    result = dispatcher.call_tool("channelSections_insert", {"part": "snippet,contentDetails", "body": body})

    assert result["endpoint"] == "channelSections.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["item"]["snippet"] == body["snippet"]
    assert result["item"]["contentDetails"] == body["contentDetails"]
