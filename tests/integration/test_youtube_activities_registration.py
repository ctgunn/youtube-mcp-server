"""Integration tests for registering the concrete ``activities_list`` tool."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.activities import build_activities_list_tool_descriptor


def _register_activities_list() -> InMemoryToolDispatcher:
    """Register the concrete activities tool in a fresh dispatcher."""
    descriptor = build_activities_list_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_activities_list_descriptor_registers_as_executable_tool():
    """Register and execute ``activities_list`` through the dispatcher."""
    dispatcher = _register_activities_list()

    result = dispatcher.call_tool("activities_list", {"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "activities.list"
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_activities_list_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, availability, caveats, and usage notes in registration."""
    dispatcher = _register_activities_list()

    [listed] = dispatcher.list_tools()

    assert listed["metadata"]["name"] == "activities_list"
    assert listed["metadata"]["upstream"]["operationKey"] == "activities.list"
    assert listed["metadata"]["quotaCost"] == 1
    assert listed["metadata"]["authMode"] == "mixed/conditional"
    assert listed["metadata"]["usageNotes"]


def test_activities_list_dispatcher_rejects_invalid_selector_request():
    """Reject invalid selector combinations through dispatcher invocation."""
    dispatcher = _register_activities_list()

    try:
        dispatcher.call_tool("activities_list", {"part": "snippet", "channelId": "UC123", "mine": True})
    except ValueError as error:
        assert "requires exactly one selector" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid selector request to fail")
