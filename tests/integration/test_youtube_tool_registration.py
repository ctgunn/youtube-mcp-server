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


def test_default_registry_includes_executable_captions_insert_tool():
    """Register ``captions_insert`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "captions_insert" in listed
    assert listed["captions_insert"]["metadata"]["upstream"]["operationKey"] == "captions.insert"
    assert listed["captions_insert"]["metadata"]["quotaCost"] == 400
    assert listed["captions_insert"]["metadata"]["authMode"] == "oauth_required"


def test_default_registry_includes_executable_captions_update_tool():
    """Register ``captions_update`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "captions_update" in listed
    assert listed["captions_update"]["metadata"]["upstream"]["operationKey"] == "captions.update"
    assert listed["captions_update"]["metadata"]["quotaCost"] == 450
    assert listed["captions_update"]["metadata"]["authMode"] == "oauth_required"


def test_default_registry_includes_executable_captions_download_tool():
    """Register ``captions_download`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "captions_download" in listed
    assert listed["captions_download"]["metadata"]["upstream"]["operationKey"] == "captions.download"
    assert listed["captions_download"]["metadata"]["quotaCost"] == 200
    assert listed["captions_download"]["metadata"]["authMode"] == "oauth_required"


def test_default_registry_includes_executable_captions_delete_tool():
    """Register ``captions_delete`` by default with safe metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "captions_delete" in listed
    metadata = listed["captions_delete"]["metadata"]
    assert metadata["upstream"]["operationKey"] == "captions.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert any("destructive" in caveat.lower() for caveat in metadata["caveats"])


def test_default_registry_includes_executable_channel_banners_insert_tool_with_upload_metadata():
    """Register ``channelBanners_insert`` by default with upload metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelBanners_insert" in listed
    metadata = listed["channelBanners_insert"]["metadata"]
    description = listed["channelBanners_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channelBanners.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "media_constrained"
    assert metadata["inputContract"]["required"] == ["media"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["returnedUrlField"] == "url"
    assert metadata["responseConvention"]["activationBoundary"] == "channels.update"
    assert "image/jpeg" in metadata_text
    assert "image/png" in metadata_text
    assert "6 MB" in metadata_text
    assert "channels.update" in metadata_text


def test_default_registry_includes_executable_channels_list_tool_with_selector_metadata():
    """Register ``channels_list`` by default with selector metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channels_list" in listed
    metadata = listed["channels_list"]["metadata"]
    description = listed["channels_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channels.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "mine", "forHandle", "forUsername"}.issubset(metadata["inputContract"]["properties"])
    assert "OAuth" in metadata_text
    assert "forHandle" in metadata_text
    assert "forUsername" in metadata_text
    assert "empty" in metadata_text.lower()


def test_default_registry_includes_executable_channel_sections_list_tool_with_caveat_metadata():
    """Register ``channelSections_list`` by default with selector and caveat metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelSections_list" in listed
    metadata = listed["channelSections_list"]["metadata"]
    description = listed["channelSections_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channelSections.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"channelId", "id", "mine", "hl", "onBehalfOfContentOwner"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["caveatFields"] == [
        "hlDeprecated",
        "contentOwnerPartnerScoped",
        "paginationCompatibilityOnly",
    ]
    assert "OAuth" in metadata_text
    assert "deprecated" in metadata_text
    assert "content partners" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "mutate channel sections" in metadata_text


def test_default_registry_includes_executable_channel_sections_insert_tool_with_create_metadata():
    """Register ``channelSections_insert`` by default with create metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelSections_insert" in listed
    metadata = listed["channelSections_insert"]["metadata"]
    description = listed["channelSections_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channelSections.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["contentDetails", "id", "snippet"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["supportedWritableParts"] == ["contentDetails", "id", "snippet"]
    assert "snippet.type" in metadata_text
    assert "body.snippet.channelId" in metadata_text
    assert "singlePlaylist" in metadata_text
    assert "multiplePlaylists" in metadata_text
    assert "multipleChannels" in metadata_text
    assert "maximum" in metadata_text.lower()
    assert "playlistItems.list" in metadata_text
    assert "channels.update" in metadata_text


def test_default_registry_includes_executable_channels_update_tool_with_update_metadata():
    """Register ``channels_update`` by default with writable update metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channels_update" in listed
    metadata = listed["channels_update"]["metadata"]
    description = listed["channels_update"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channels.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["brandingSettings", "localizations"]
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["supportedWritableParts"] == ["brandingSettings", "localizations"]
    assert "onBehalfOfContentOwner" in metadata_text
    assert "bannerExternalUrl" in metadata_text
    assert "channelBanners_insert" in metadata_text
    assert "analytics" in metadata_text.lower()
