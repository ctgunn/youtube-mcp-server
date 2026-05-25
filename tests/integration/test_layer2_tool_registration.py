"""Integration tests for Layer 2 tool registration scaffolding."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common import REPRESENTATIVE_LAYER2_CONTRACTS, build_representative_tool_descriptor


def test_representative_layer2_descriptor_registers_without_endpoint_execution():
    """Register a representative Layer 2 descriptor with the existing dispatcher."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_LAYER2_CONTRACTS[0])
    dispatcher = InMemoryToolDispatcher(tools=[])

    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
    )

    listed = dispatcher.list_tools()

    assert listed == [
        {
            "name": descriptor["name"],
            "description": descriptor["description"],
            "inputSchema": descriptor["inputSchema"],
        }
    ]
    assert dispatcher.call_tool(descriptor["name"], {"part": "snippet"})["representativeOnly"] is True
