"""Integration-style tests for Layer 3 shared registration readiness."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_composed import (
    REPRESENTATIVE_TOOL_CONTRACTS,
    build_representative_tool_descriptor,
)


def test_representative_layer3_descriptor_registers_without_tool_execution():
    """Register representative Layer 3 metadata while keeping the handler inert."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_TOOL_CONTRACTS[0])
    dispatcher = InMemoryToolDispatcher(tools=[])

    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )

    listed = dispatcher.list_tools()
    result = dispatcher.call_tool(descriptor["name"], {"videoId": "video-123"})

    assert listed[0]["metadata"]["representativeOnly"] is True
    assert result["representativeOnly"] is True
    assert result["concreteToolExecuted"] is False


def test_representative_layer3_descriptor_exposes_family_and_composition_metadata():
    """Expose Layer 3 family and composition metadata through discovery shape."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_TOOL_CONTRACTS[-1])
    metadata = descriptor["metadata"]

    assert metadata["family"] == "playlists"
    assert metadata["compositionBoundary"]["kind"] == "fan_out"
    assert metadata["lowerLayerDependencies"] == ["playlistItems.list", "captions.list", "captions.download"]
