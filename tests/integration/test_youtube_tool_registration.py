"""Integration tests for YouTube tool registration scaffolding."""

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common import REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS, build_representative_tool_descriptor


def test_representative_youtube_descriptor_registers_without_endpoint_execution():
    """Register a representative YouTube descriptor with the existing dispatcher."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0])
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


def test_representative_youtube_descriptor_exposes_metadata_without_execution():
    """Expose standards metadata while keeping representative descriptors inert."""
    contract = REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0]
    descriptor = build_representative_tool_descriptor(contract)

    assert descriptor["metadata"]["name"] == contract.tool_name
    assert descriptor["metadata"]["upstream"]["operationKey"] == contract.operation_key

    result = descriptor["handler"]({"part": "snippet"})

    assert result["representativeOnly"] is True
    assert "upstreamExecuted" not in result
    assert "sourceOperation" not in result


def test_representative_youtube_descriptor_metadata_includes_cost_access_and_notes():
    """Expose caller-facing metadata needed before representative invocation."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0])
    metadata = descriptor["metadata"]

    assert metadata["quotaCost"] == REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0].quota_cost
    assert metadata["authMode"] == REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0].auth_mode.value
    assert metadata["availabilityState"]
    assert metadata["caveats"] == list(REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS[0].caveats)
    assert metadata["usageNotes"]
