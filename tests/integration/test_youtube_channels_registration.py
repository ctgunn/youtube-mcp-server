"""Integration tests for registering the concrete ``channels_list`` tool."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher


def test_default_registry_includes_executable_channels_list_tool():
    """Register ``channels_list`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channels_list" in listed
    metadata = listed["channels_list"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "channels.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"


def test_default_registry_executes_channels_list_empty_result():
    """Invoke the default ``channels_list`` handler through the dispatcher."""
    dispatcher = InMemoryToolDispatcher()

    result = dispatcher.call_tool("channels_list", {"part": "snippet", "id": "UC123"})

    assert result["endpoint"] == "channels.list"
    assert result["quotaCost"] == 1
    assert result["items"] == []
    assert result["selector"] == {"name": "id"}
