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
