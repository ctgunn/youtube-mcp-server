"""Integration tests for registering concrete Layer 2 ``comments`` tools."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.comments import (
    build_comments_insert_tool_descriptor,
    build_comments_update_tool_descriptor,
    build_comments_list_tool_descriptor,
)


def _register_comments_list() -> InMemoryToolDispatcher:
    """Register the concrete comments tool in a fresh dispatcher."""
    descriptor = build_comments_list_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_comments_insert(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete comments insert tool in a fresh dispatcher."""
    descriptor = build_comments_insert_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _register_comments_update(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete comments update tool in a fresh dispatcher."""
    descriptor = build_comments_update_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def _valid_insert_arguments() -> dict:
    """Return a representative valid ``comments_insert`` request."""
    return {
        "part": "snippet",
        "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Reply text"}},
    }


def _valid_update_arguments() -> dict:
    """Return a representative valid ``comments_update`` request."""
    return {
        "part": "snippet",
        "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}},
    }


def test_comments_list_descriptor_registers_as_executable_tool_for_id_lookup():
    """Register and execute ``comments_list`` ID lookup through the dispatcher."""
    dispatcher = _register_comments_list()

    result = dispatcher.call_tool("comments_list", {"part": "id,snippet", "id": "comment-123"})

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "comment-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}


def test_comments_list_descriptor_registers_as_executable_tool_for_parent_lookup():
    """Register and execute ``comments_list`` parent lookup through the dispatcher."""
    dispatcher = _register_comments_list()

    result = dispatcher.call_tool(
        "comments_list",
        {"part": "snippet", "parentId": "comment-parent-123", "maxResults": 2, "textFormat": "plainText"},
    )

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "reply-123"}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "parentId"}
    assert result["textFormat"] == "plainText"


def test_comments_list_registration_exposes_metadata_and_usage_notes():
    """Expose quota, auth, selectors, pagination, and caveats in registration."""
    dispatcher = _register_comments_list()

    [listed] = dispatcher.list_tools()
    metadata = listed["metadata"]
    metadata_text = " ".join([listed["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_list"
    assert metadata["upstream"]["operationKey"] == "comments.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert "parentId" in metadata_text
    assert "maxResults" in metadata_text
    assert "plainText" in metadata_text


def test_comments_list_dispatcher_rejects_invalid_selector_request():
    """Reject invalid selector combinations through dispatcher invocation."""
    dispatcher = _register_comments_list()

    try:
        dispatcher.call_tool("comments_list", {"part": "snippet", "id": "comment-123", "parentId": "parent-123"})
    except ValueError as error:
        assert "requires exactly one selector" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid selector request to fail")


def test_default_registry_includes_executable_comments_list_tool():
    """Register ``comments_list`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_list" in listed
    metadata = listed["comments_list"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "comments.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"


def test_comments_insert_descriptor_registers_as_executable_tool_for_reply_creation():
    """Register and execute ``comments_insert`` reply creation."""
    dispatcher = _register_comments_insert()

    result = dispatcher.call_tool("comments_insert", _valid_insert_arguments())

    assert result["endpoint"] == "comments.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["item"]["id"] == "created-comment-123"
    assert result["requestedParts"] == ["snippet"]


def test_comments_insert_registration_exposes_metadata_and_usage_notes():
    """Expose quota, OAuth, reply body, and caveats in registration."""
    dispatcher = _register_comments_insert()

    [listed] = dispatcher.list_tools()
    metadata = listed["metadata"]
    metadata_text = " ".join([listed["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["name"] == "comments_insert"
    assert metadata["upstream"]["operationKey"] == "comments.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "body.snippet.parentId" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "commentThreads.insert" in metadata_text


def test_comments_insert_dispatcher_rejects_invalid_reply_body():
    """Reject invalid reply bodies through dispatcher invocation."""
    dispatcher = _register_comments_insert()

    try:
        dispatcher.call_tool("comments_insert", {"part": "snippet", "body": {"snippet": {"parentId": ""}}})
    except ValueError as error:
        assert "parentId" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid reply body to fail")


def test_comments_insert_dispatcher_rejects_missing_oauth():
    """Reject missing OAuth context through dispatcher invocation."""
    dispatcher = _register_comments_insert(oauth_token=None)

    try:
        dispatcher.call_tool("comments_insert", _valid_insert_arguments())
    except ValueError as error:
        assert "requires OAuth" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected missing OAuth to fail")


def test_comments_update_descriptor_registers_as_executable_tool_for_comment_edit():
    """Register and execute ``comments_update`` comment editing."""
    dispatcher = _register_comments_update()

    result = dispatcher.call_tool("comments_update", _valid_update_arguments())

    assert result["endpoint"] == "comments.update"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["item"]["id"] == "comment-123"
    assert result["item"]["snippet"]["textOriginal"] == "Updated comment text."
    assert result["requestedParts"] == ["snippet"]


def test_comments_update_dispatcher_rejects_missing_oauth():
    """Reject missing OAuth context through dispatcher invocation."""
    dispatcher = _register_comments_update(oauth_token=None)

    try:
        dispatcher.call_tool("comments_update", _valid_update_arguments())
    except ValueError as error:
        assert "requires OAuth" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected missing OAuth to fail")


def test_comments_update_dispatcher_rejects_invalid_update_body():
    """Reject invalid update bodies through dispatcher invocation."""
    dispatcher = _register_comments_update()

    try:
        dispatcher.call_tool("comments_update", {"part": "snippet", "body": {"id": ""}})
    except ValueError as error:
        assert "body.id" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected invalid update body to fail")


def test_comments_update_dispatcher_rejects_unsupported_writable_part():
    """Reject unsupported update parts through dispatcher invocation."""
    dispatcher = _register_comments_update()

    try:
        dispatcher.call_tool(
            "comments_update",
            {
                "part": "statistics",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated text"}},
            },
        )
    except ValueError as error:
        assert "snippet part" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected unsupported writable part to fail")


def test_comments_update_dispatcher_rejects_read_only_field_update():
    """Reject read-only update body fields through dispatcher invocation."""
    dispatcher = _register_comments_update()

    try:
        dispatcher.call_tool(
            "comments_update",
            {
                "part": "snippet",
                "body": {
                    "id": "comment-123",
                    "snippet": {"textOriginal": "Updated text", "parentId": "comment-parent-123"},
                },
            },
        )
    except ValueError as error:
        assert "parentId" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected read-only field update to fail")


def test_comments_update_dispatcher_maps_missing_target_comment_safely():
    """Map missing target comment failures through dispatcher invocation."""
    dispatcher = _register_comments_update()

    try:
        dispatcher.call_tool(
            "comments_update",
            {
                "part": "snippet",
                "body": {"id": "missing-comment", "snippet": {"textOriginal": "Updated text"}},
            },
        )
    except ValueError as error:
        assert "comment not found" in str(error)
    else:  # pragma: no cover - failure path
        raise AssertionError("expected missing target comment to fail")


def test_default_registry_includes_executable_comments_insert_tool():
    """Register ``comments_insert`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_insert" in listed
    metadata = listed["comments_insert"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "comments.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
