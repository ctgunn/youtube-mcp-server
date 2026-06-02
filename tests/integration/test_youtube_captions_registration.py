"""Integration tests for registering concrete ``captions`` Layer 2 tools."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.captions import (
    build_captions_download_tool_descriptor,
    build_captions_insert_tool_descriptor,
    build_captions_list_tool_descriptor,
    build_captions_update_tool_descriptor,
)


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


def _valid_captions_insert_arguments() -> dict:
    """Return a representative valid ``captions_insert`` request."""
    return {
        "part": "snippet",
        "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English captions"}},
        "media": {"mimeType": "text/xml", "content": "caption text"},
    }


def _register_captions_insert() -> InMemoryToolDispatcher:
    """Register the concrete captions insert tool in a fresh dispatcher."""
    descriptor = build_captions_insert_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _valid_captions_update_arguments() -> dict:
    """Return a representative valid ``captions_update`` request."""
    return {"part": "snippet", "body": {"id": "caption-1", "snippet": {"isDraft": False}}}


def _register_captions_update() -> InMemoryToolDispatcher:
    """Register the concrete captions update tool in a fresh dispatcher."""
    descriptor = build_captions_update_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _valid_captions_download_arguments() -> dict:
    """Return a representative valid ``captions_download`` request."""
    return {"id": "caption-1"}


def _register_captions_download() -> InMemoryToolDispatcher:
    """Register the concrete captions download tool in a fresh dispatcher."""
    descriptor = build_captions_download_tool_descriptor()
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


def test_captions_insert_descriptor_registers_as_executable_tool():
    """Register and execute ``captions_insert`` through the dispatcher."""
    dispatcher = _register_captions_insert()

    result = dispatcher.call_tool("captions_insert", _valid_captions_insert_arguments())

    assert result["endpoint"] == "captions.insert"
    assert result["item"]["id"] == "created-caption"
    assert result["requestedParts"] == ["snippet"]


def test_captions_insert_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, upload, caveats, and usage notes in registration."""
    dispatcher = _register_captions_insert()

    [listed] = dispatcher.list_tools()

    assert listed["metadata"]["name"] == "captions_insert"
    assert listed["metadata"]["upstream"]["operationKey"] == "captions.insert"
    assert listed["metadata"]["quotaCost"] == 400
    assert listed["metadata"]["authMode"] == "oauth_required"
    assert listed["metadata"]["usageNotes"]
    assert listed["metadata"]["caveats"]


def test_captions_insert_dispatcher_rejects_invalid_request():
    """Reject invalid caption insert requests through dispatcher invocation."""
    dispatcher = _register_captions_insert()

    try:
        dispatcher.call_tool(
            "captions_insert",
            {"part": "snippet", "body": {"snippet": {"videoId": "video-123"}}},
        )
    except ValueError as error:
        assert "arguments missing required field: media" in str(error) or "requires body.snippet.language" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid caption insert request to fail")


def test_captions_update_descriptor_registers_as_executable_tool():
    """Register and execute ``captions_update`` through the dispatcher."""
    dispatcher = _register_captions_update()

    result = dispatcher.call_tool("captions_update", _valid_captions_update_arguments())

    assert result["endpoint"] == "captions.update"
    assert result["item"]["id"] == "caption-1"
    assert result["requestedParts"] == ["snippet"]


def test_captions_update_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, update, caveats, and usage notes in registration."""
    dispatcher = _register_captions_update()

    [listed] = dispatcher.list_tools()

    assert listed["metadata"]["name"] == "captions_update"
    assert listed["metadata"]["upstream"]["operationKey"] == "captions.update"
    assert listed["metadata"]["quotaCost"] == 450
    assert listed["metadata"]["authMode"] == "oauth_required"
    assert listed["metadata"]["usageNotes"]
    assert listed["metadata"]["caveats"]


def test_captions_update_dispatcher_rejects_invalid_request():
    """Reject invalid caption update requests through dispatcher invocation."""
    dispatcher = _register_captions_update()

    try:
        dispatcher.call_tool("captions_update", {"part": "snippet", "body": {}})
    except ValueError as error:
        assert "requires body.id" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid caption update request to fail")


def test_captions_download_descriptor_registers_as_executable_tool():
    """Register and execute ``captions_download`` through the dispatcher."""
    dispatcher = _register_captions_download()

    result = dispatcher.call_tool("captions_download", _valid_captions_download_arguments())

    assert result["endpoint"] == "captions.download"
    assert result["content"] == "caption content"
    assert result["download"] == {"id": "caption-1"}


def test_captions_download_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, permission, conversion, caveats, and usage notes in registration."""
    dispatcher = _register_captions_download()

    [listed] = dispatcher.list_tools()

    assert listed["metadata"]["name"] == "captions_download"
    assert listed["metadata"]["upstream"]["operationKey"] == "captions.download"
    assert listed["metadata"]["quotaCost"] == 200
    assert listed["metadata"]["authMode"] == "oauth_required"
    assert listed["metadata"]["usageNotes"]
    assert listed["metadata"]["caveats"]


def test_captions_download_dispatcher_rejects_invalid_request():
    """Reject invalid caption download requests through dispatcher invocation."""
    dispatcher = _register_captions_download()

    try:
        dispatcher.call_tool("captions_download", {"tfmt": "srt"})
    except ValueError as error:
        assert "arguments missing required field: id" in str(error) or "requires id" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid caption download request to fail")
