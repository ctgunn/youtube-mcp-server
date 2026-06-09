"""Integration tests for registering concrete Layer 2 ``channels`` tools."""

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


def test_default_registry_includes_executable_channels_update_tool():
    """Register ``channels_update`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channels_update" in listed
    metadata = listed["channels_update"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "channels.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["brandingSettings", "localizations"]


def test_default_registry_executes_channels_update_result():
    """Invoke the default ``channels_update`` handler through the dispatcher."""
    dispatcher = InMemoryToolDispatcher()

    result = dispatcher.call_tool(
        "channels_update",
        {
            "part": "localizations",
            "body": {"id": "UC123", "localizations": {"es": {"title": "Canal"}}},
        },
    )

    assert result["endpoint"] == "channels.update"
    assert result["quotaCost"] == 50
    assert result["updatedPart"] == "localizations"
    assert result["requestedParts"] == ["localizations"]
    assert result["item"]["id"] == "UC123"
    assert result["item"]["localizations"] == {"es": {"title": "Canal"}}
