"""Integration tests for registering the concrete ``captions_list`` tool."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.captions import build_captions_list_tool_descriptor


def _register_captions_list() -> InMemoryToolDispatcher:
    """Register the concrete captions tool in a fresh dispatcher."""
    descriptor = build_captions_list_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_captions_list_descriptor_registers_as_executable_tool():
    """Register and execute ``captions_list`` through the dispatcher."""
    dispatcher = _register_captions_list()

    result = dispatcher.call_tool("captions_list", {"part": "snippet", "videoId": "video-123"})

    assert result["endpoint"] == "captions.list"
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_captions_list_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, availability, caveats, and usage notes in registration."""
    dispatcher = _register_captions_list()

    [listed] = dispatcher.list_tools()

    assert listed["metadata"]["name"] == "captions_list"
    assert listed["metadata"]["upstream"]["operationKey"] == "captions.list"
    assert listed["metadata"]["quotaCost"] == 50
    assert listed["metadata"]["authMode"] == "oauth_required"
    assert listed["metadata"]["usageNotes"]


def test_captions_list_dispatcher_rejects_invalid_request():
    """Reject invalid caption lookup requests through dispatcher invocation."""
    dispatcher = _register_captions_list()

    try:
        dispatcher.call_tool("captions_list", {"part": "snippet", "videoId": "video-123", "maxResults": 51})
    except ValueError as error:
        assert "maxResults must be between 0 and 50" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid caption lookup request to fail")
