"""Integration tests for registering concrete ``channelBanners`` Layer 2 tools."""

import pytest

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.channel_banners import (
    ChannelBannersInsertToolError,
    build_channel_banners_insert_tool_descriptor,
)


def _valid_channel_banners_insert_arguments() -> dict:
    """Return a representative valid ``channelBanners_insert`` request."""
    return {
        "media": {
            "mimeType": "image/png",
            "content": "safe image content",
            "filename": "banner.png",
            "sizeBytes": 2048,
        }
    }


def _register_channel_banners_insert() -> InMemoryToolDispatcher:
    """Register the concrete channel banners insert tool in a fresh dispatcher."""
    descriptor = build_channel_banners_insert_tool_descriptor()
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_channel_banners_insert_descriptor_registers_as_executable_tool():
    """Register and execute ``channelBanners_insert`` through the dispatcher."""
    dispatcher = _register_channel_banners_insert()

    result = dispatcher.call_tool("channelBanners_insert", _valid_channel_banners_insert_arguments())

    assert result["endpoint"] == "channelBanners.insert"
    assert result["item"]["url"]
    assert result["media"]["mimeType"] == "image/png"
    assert "content" not in result["media"]


def test_default_registry_includes_executable_channel_banners_insert_tool():
    """Expose ``channelBanners_insert`` through default dispatcher discovery."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelBanners_insert" in listed
    assert listed["channelBanners_insert"]["metadata"]["upstream"]["operationKey"] == "channelBanners.insert"
    assert listed["channelBanners_insert"]["metadata"]["quotaCost"] == 50
    assert listed["channelBanners_insert"]["metadata"]["authMode"] == "oauth_required"


@pytest.mark.parametrize(
    ("arguments", "field", "error_type"),
    [
        ({"media": {"mimeType": "image/gif", "content": "image"}}, "media.mimeType", ChannelBannersInsertToolError),
        ({**_valid_channel_banners_insert_arguments(), "body": {"brandingSettings": {}}}, "body", ValueError),
        (
            {"media": {"mimeType": "image/png", "content": "image", "resize": "2560x1440"}},
            "media.resize",
            ChannelBannersInsertToolError,
        ),
    ],
)
def test_channel_banners_insert_dispatcher_rejects_invalid_requests(arguments, field, error_type):
    """Reject invalid ``channelBanners_insert`` requests through dispatcher execution."""
    dispatcher = _register_channel_banners_insert()

    with pytest.raises(error_type) as context:
        dispatcher.call_tool("channelBanners_insert", arguments)

    if isinstance(context.value, ChannelBannersInsertToolError):
        assert context.value.category == "invalid_request"
        assert context.value.details["field"] == field
    else:
        assert field in str(context.value)
