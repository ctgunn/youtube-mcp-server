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


def test_default_registry_includes_executable_comments_insert_tool_with_create_metadata():
    """Register ``comments_insert`` by default with create metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_insert" in listed
    metadata = listed["comments_insert"]["metadata"]
    description = listed["comments_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "comments.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.parentId" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "commentThreads.insert" in metadata_text


def test_default_registry_includes_executable_comments_update_tool_with_update_metadata():
    """Register ``comments_update`` by default with update metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_update" in listed
    metadata = listed["comments_update"]["metadata"]
    description = listed["comments_update"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "comments.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "body.id" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "read-only" in metadata_text


def test_default_registry_includes_executable_comments_set_moderation_status_tool_with_metadata():
    """Register ``comments_setModerationStatus`` by default with moderation metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_setModerationStatus" in listed
    metadata = listed["comments_setModerationStatus"]["metadata"]
    description = listed["comments_setModerationStatus"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "comments.setModerationStatus"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["id", "moderationStatus"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert "heldForReview" in metadata_text
    assert "published" in metadata_text
    assert "rejected" in metadata_text
    assert "banAuthor" in metadata_text


def test_default_registry_includes_executable_comments_delete_tool_with_metadata():
    """Register ``comments_delete`` by default with destructive delete metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "comments_delete" in listed
    metadata = listed["comments_delete"]["metadata"]
    description = listed["comments_delete"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "comments.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "body" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text


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


def test_default_registry_includes_executable_comment_threads_list_tool():
    """Register ``commentThreads_list`` by default with safe selector metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "commentThreads_list" in listed
    metadata = listed["commentThreads_list"]["metadata"]
    description = listed["commentThreads_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "commentThreads.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"videoId", "allThreadsRelatedToChannelId", "id"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert "moderationStatus" in metadata_text


def test_default_registry_includes_executable_commentThreads_insert_tool():
    """Register ``commentThreads_insert`` by default with create metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "commentThreads_insert" in listed
    metadata = listed["commentThreads_insert"]["metadata"]
    description = listed["commentThreads_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "commentThreads.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "body.snippet.channelId" in metadata_text
    assert "body.snippet.videoId" in metadata_text
    assert "body.snippet.topLevelComment.snippet.textOriginal" in metadata_text
    assert "comments_insert" in metadata_text


def test_default_registry_includes_executable_guideCategories_list_tool():
    """Register ``guideCategories_list`` by default with legacy lookup metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "guideCategories_list" in listed
    metadata = listed["guideCategories_list"]["metadata"]
    description = listed["guideCategories_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "guideCategories.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "deprecated"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"regionCode", "id", "hl"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "deprecated" in metadata_text.lower()
    assert "video categories" in metadata_text


def test_default_registry_includes_executable_i18nLanguages_list_tool():
    """Register ``i18nLanguages_list`` by default with localization-language metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "i18nLanguages_list" in listed
    metadata = listed["i18nLanguages_list"]["metadata"]
    description = listed["i18nLanguages_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "i18nLanguages.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "translation" in metadata_text
    assert "region" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "default_language_listing",
        "display_language_listing",
        "empty_success",
    }


def test_default_registry_includes_executable_i18nRegions_list_tool():
    """Register ``i18nRegions_list`` by default with localization-region metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "i18nRegions_list" in listed
    metadata = listed["i18nRegions_list"]["metadata"]
    description = listed["i18nRegions_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "i18nRegions.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "language lookup" in metadata_text
    assert "geotarget" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "default_region_listing",
        "display_language_region_listing",
        "empty_success",
    }


def test_default_registry_includes_executable_members_list_tool():
    """Register ``members_list`` by default with owner-scoped membership metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "members_list" in listed
    metadata = listed["members_list"]["metadata"]
    description = listed["members_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "members.list"
    assert metadata["quotaCost"] == 2
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "mode"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert metadata["inputContract"]["properties"]["mode"]["enum"] == ["all_current", "updates"]
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text.lower()
    assert {example["name"] for example in metadata["examples"]} >= {
        "current_members_listing",
        "membership_updates_listing",
        "empty_success",
    }


def test_default_registry_includes_executable_membershipsLevels_list_tool():
    """Register ``membershipsLevels_list`` by default with membership-level metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "membershipsLevels_list" in listed
    metadata = listed["membershipsLevels_list"]["metadata"]
    description = listed["membershipsLevels_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "membershipsLevels.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "pageToken" not in metadata["inputContract"]["properties"]
    assert "maxResults" not in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text.lower()
    assert {example["name"] for example in metadata["examples"]} >= {
        "membership_levels_listing",
        "empty_success",
        "missing_part",
    }


def test_default_registry_includes_executable_playlistImages_list_tool():
    """Register ``playlistImages_list`` by default with playlist-image metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistImages_list" in listed
    metadata = listed["playlistImages_list"]["metadata"]
    description = listed["playlistImages_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistImages.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["selectorFields"] == ["playlistId", "id"]
    assert "playlistId" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "playlist_scoped_image_listing",
        "direct_image_lookup",
        "empty_success",
    }


def test_default_registry_includes_executable_playlistImages_insert_tool():
    """Register ``playlistImages_insert`` by default with playlist-image upload metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistImages_insert" in listed
    metadata = listed["playlistImages_insert"]["metadata"]
    description = listed["playlistImages_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistImages.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "media" in metadata_text
    assert "body" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_insert",
        "missing_media",
        "unsupported_media",
    }


def test_server_list_tools_preserves_playlistImages_insert_metadata():
    """Expose ``playlistImages_insert`` discovery metadata through the public registry tool."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.call_tool("server_list_tools", {})}
    metadata = listed["playlistImages_insert"]["metadata"]

    assert metadata["upstream"]["operationKey"] == "playlistImages.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert metadata["inputContract"]["properties"]["media"]["required"] == ["mimeType", "content"]
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_insert",
        "invalid_body",
        "quota_or_upstream_insert_failure",
        "out_of_scope_image_management_request",
    }


def test_default_registry_includes_executable_playlistImages_update_tool():
    """Register ``playlistImages_update`` by default with playlist-image update metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistImages_update" in listed
    metadata = listed["playlistImages_update"]["metadata"]
    description = listed["playlistImages_update"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistImages.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "media" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_update",
        "missing_target_identity",
        "missing_playlist_context",
        "unsupported_media",
    }


def test_server_list_tools_preserves_playlistImages_update_metadata():
    """Expose ``playlistImages_update`` discovery metadata through the public registry tool."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.call_tool("server_list_tools", {})}
    metadata = listed["playlistImages_update"]["metadata"]

    assert metadata["upstream"]["operationKey"] == "playlistImages.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert metadata["inputContract"]["properties"]["body"]["required"] == ["id", "snippet"]
    assert metadata["inputContract"]["properties"]["media"]["required"] == ["mimeType", "content"]
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_update",
        "invalid_body",
        "quota_or_upstream_update_failure",
        "out_of_scope_image_management_request",
    }


def test_default_registry_includes_executable_playlistImages_delete_tool():
    """Register ``playlistImages_delete`` by default with destructive deletion metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistImages_delete" in listed
    metadata = listed["playlistImages_delete"]["metadata"]
    description = listed["playlistImages_delete"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistImages.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["id"]
    assert set(metadata["inputContract"]["properties"]) == {"id"}
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text
    assert "media" in metadata_text
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_delete",
        "missing_id",
        "quota_or_upstream_delete_failure",
        "out_of_scope_image_management_request",
    }


def test_server_list_tools_preserves_playlistImages_delete_metadata():
    """Expose ``playlistImages_delete`` discovery metadata through the public registry tool."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.call_tool("server_list_tools", {})}
    metadata = listed["playlistImages_delete"]["metadata"]

    assert metadata["upstream"]["operationKey"] == "playlistImages.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert set(metadata["inputContract"]["properties"]) == {"id"}
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert {example["name"] for example in metadata["examples"]} >= {
        "authorized_playlist_image_delete",
        "invalid_id",
        "quota_or_upstream_delete_failure",
        "out_of_scope_image_management_request",
    }


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


def test_default_registry_includes_executable_channel_sections_update_tool_with_update_metadata():
    """Register ``channelSections_update`` by default with update metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "channelSections_update" in listed
    metadata = listed["channelSections_update"]["metadata"]
    description = listed["channelSections_update"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "channelSections.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["contentDetails", "id", "snippet"]
    assert metadata["inputContract"]["properties"]["body"]["required"] == ["id", "snippet"]
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["supportedWritableParts"] == ["contentDetails", "id", "snippet"]
    assert metadata["responseConvention"]["overwriteSensitive"] is True
    assert "body.id" in metadata_text
    assert "snippet.type" in metadata_text
    assert "singlePlaylist" in metadata_text
    assert "multiplePlaylists" in metadata_text
    assert "multipleChannels" in metadata_text
    assert "omitted" in metadata_text.lower()
    assert "deleted" in metadata_text.lower()
    assert "patch" in metadata_text.lower()


def test_default_registry_includes_executable_playlist_items_list_tool_with_list_metadata():
    """Register ``playlistItems_list`` by default with list metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_list" in listed
    metadata = listed["playlistItems_list"]["metadata"]
    description = listed["playlistItems_list"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistItems.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["selectorFields"] == ["playlistId", "id"]
    assert "API-key" in metadata_text or "api_key" in metadata_text
    assert "playlistItems.list" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "playlist item mutation" in metadata_text


def test_default_registry_includes_executable_playlist_items_insert_tool_with_insert_metadata():
    """Register ``playlistItems_insert`` by default with insert metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_insert" in listed
    metadata = listed["playlistItems_insert"]["metadata"]
    description = listed["playlistItems_insert"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistItems.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "playlist item listing" in metadata_text


def test_default_registry_includes_executable_playlist_items_update_tool_with_update_metadata():
    """Register ``playlistItems_update`` by default with update metadata."""
    dispatcher = InMemoryToolDispatcher()
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}

    assert "playlistItems_update" in listed
    metadata = listed["playlistItems_update"]["metadata"]
    description = listed["playlistItems_update"]["description"]
    metadata_text = " ".join([description, *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["upstream"]["operationKey"] == "playlistItems.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "playlist item listing" in metadata_text


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
