"""Contract tests for representative YouTube tool catalog examples."""

from mcp_server.tools.youtube_common import AuthMode, REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS


def test_representative_examples_include_required_us1_shapes():
    """Expose representative examples for core naming and metadata shapes."""
    names = {contract.tool_name for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}

    assert {
        "activities_list",
        "captions_insert",
        "captions_update",
        "channelBanners_insert",
        "channelSections_insert",
        "channelSections_list",
        "channelSections_update",
        "channels_update",
        "playlists_insert",
        "comments_insert",
        "comments_update",
        "comments_setModerationStatus",
        "comments_delete",
        "commentThreads_list",
        "commentThreads_insert",
        "guideCategories_list",
        "i18nLanguages_list",
        "members_list",
        "videos_getRating",
        "videos_reportAbuse",
        "watermarks_unset",
    }.issubset(names)


def test_representative_examples_expose_auth_quota_and_caveats():
    """Make auth, quota, and caveat metadata visible in representative examples."""
    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}

    assert by_name["activities_list"].auth_mode is AuthMode.MIXED
    assert by_name["activities_list"].quota_cost == 1
    assert by_name["comments_setModerationStatus"].auth_mode is AuthMode.OAUTH_REQUIRED
    assert by_name["videos_getRating"].upstream_method == "getRating"
    assert by_name["watermarks_unset"].caveats


def test_representative_activities_example_aligns_with_concrete_contract():
    """Keep the representative activities example aligned with YT-203."""
    from mcp_server.tools.youtube_common.activities import build_activities_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "activities_list"
    ]
    concrete = build_activities_list_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode


def test_representative_captions_example_aligns_with_concrete_contract():
    """Keep the representative captions-list example aligned with YT-204."""
    from mcp_server.tools.youtube_common.captions import build_captions_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "captions_list"
    ]
    concrete = build_captions_list_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode


def test_representative_captions_insert_example_aligns_with_concrete_contract():
    """Keep the representative captions-insert example aligned with YT-205."""
    from mcp_server.tools.youtube_common.captions import build_captions_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "captions_insert"
    ]
    concrete = build_captions_insert_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]


def test_representative_captions_update_example_aligns_with_concrete_contract():
    """Keep the representative captions-update example aligned with YT-206."""
    from mcp_server.tools.youtube_common.captions import build_captions_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "captions_update"
    ]
    concrete = build_captions_update_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]


def test_representative_captions_download_example_aligns_with_concrete_contract():
    """Keep the representative captions-download example aligned with YT-207."""
    from mcp_server.tools.youtube_common.captions import build_captions_download_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "captions_download"
    ]
    concrete = build_captions_download_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]


def test_representative_captions_delete_example_aligns_with_concrete_contract():
    """Keep the representative captions-delete example aligned with YT-208."""
    from mcp_server.tools.youtube_common.captions import build_captions_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "captions_delete"
    ]
    concrete = build_captions_delete_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]


def test_representative_comments_insert_example_aligns_with_concrete_contract():
    """Keep the representative comments-insert example aligned with YT-217."""
    from mcp_server.tools.youtube_common.comments import build_comments_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_insert"
    ]
    concrete = build_comments_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.snippet.parentId" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text
    assert "commentThreads.insert" in metadata_text


def test_representative_comments_update_example_aligns_with_concrete_contract():
    """Keep the representative comments-update example aligned with YT-218."""
    from mcp_server.tools.youtube_common.comments import build_comments_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_update"
    ]
    concrete = build_comments_update_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "updated_resource"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.id" in metadata_text
    assert "body.snippet.textOriginal" in metadata_text


def test_representative_comment_threads_list_example_aligns_with_concrete_contract():
    """Keep the representative commentThreads-list example aligned with YT-221."""
    from mcp_server.tools.youtube_common.comment_threads import build_comment_threads_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "commentThreads_list"
    ]
    concrete = build_comment_threads_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "videoId" in metadata_text
    assert "allThreadsRelatedToChannelId" in metadata_text
    assert "moderationStatus" in metadata_text
    assert "read-only" in metadata_text


def test_representative_commentThreads_insert_example_aligns_with_concrete_contract():
    """Keep the representative commentThreads-insert example aligned with YT-222."""
    from mcp_server.tools.youtube_common.comment_threads import (
        COMMENT_THREADS_INSERT_CALLER_EXAMPLES,
        build_comment_threads_insert_contract,
    )

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "commentThreads_insert"
    ]
    concrete = build_comment_threads_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.snippet.channelId" in metadata_text
    assert "body.snippet.videoId" in metadata_text
    assert "body.snippet.topLevelComment.snippet.textOriginal" in metadata_text
    assert "comments_insert" in metadata_text

    example_names = {example["name"] for example in COMMENT_THREADS_INSERT_CALLER_EXAMPLES}
    assert {"invalid_target_context", "unsupported_option"}.issubset(example_names)


def test_representative_comments_set_moderation_status_example_aligns_with_concrete_contract():
    """Keep the representative comments moderation example aligned with YT-219."""
    from mcp_server.tools.youtube_common.comments import build_comments_set_moderation_status_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_setModerationStatus"
    ]
    concrete = build_comments_set_moderation_status_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "mutation_acknowledgment"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["successStatus"] == 204
    assert "heldForReview" in metadata_text
    assert "published" in metadata_text
    assert "rejected" in metadata_text
    assert "banAuthor" in metadata_text


def test_representative_comments_delete_example_aligns_with_concrete_contract():
    """Keep the representative comments-delete example aligned with YT-220."""
    from mcp_server.tools.youtube_common.comments import build_comments_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "comments_delete"
    ]
    concrete = build_comments_delete_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "deletion_acknowledgment"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["successStatus"] == 204
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text


def test_representative_channel_banners_insert_example_aligns_with_concrete_contract():
    """Keep the representative channel-banner upload example aligned with YT-209."""
    from mcp_server.tools.youtube_common.channel_banners import build_channel_banners_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channelBanners_insert"
    ]
    concrete = build_channel_banners_insert_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["activationBoundary"] == "channels.update"


def test_representative_channels_list_example_aligns_with_concrete_contract():
    """Keep the representative channels-list example aligned with YT-210."""
    from mcp_server.tools.youtube_common.channels import build_channels_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channels_list"
    ]
    concrete = build_channels_list_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "forUsername" in representative.input_contract["properties"]


def test_representative_channel_sections_list_example_aligns_with_concrete_contract():
    """Keep the representative channel-sections-list example aligned with YT-212."""
    from mcp_server.tools.youtube_common.channel_sections import build_channel_sections_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channelSections_list"
    ]
    concrete = build_channel_sections_list_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert {"channelId", "id", "mine", "hl", "onBehalfOfContentOwner"}.issubset(
        representative.input_contract["properties"]
    )
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["caveatFields"] == [
        "hlDeprecated",
        "contentOwnerPartnerScoped",
        "paginationCompatibilityOnly",
    ]


def test_representative_channel_sections_insert_example_aligns_with_concrete_contract():
    """Keep the representative channel-section insert example aligned with YT-213."""
    from mcp_server.tools.youtube_common.channel_sections import build_channel_sections_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channelSections_insert"
    ]
    concrete = build_channel_sections_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.input_contract["properties"]["part"]["enum"] == ["contentDetails", "id", "snippet"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["supportedWritableParts"] == ["contentDetails", "id", "snippet"]
    assert "snippet.type" in metadata_text
    assert "maximum" in metadata_text.lower()


def test_representative_channel_sections_update_example_aligns_with_concrete_contract():
    """Keep the representative channel-section update example aligned with YT-214."""
    from mcp_server.tools.youtube_common.channel_sections import build_channel_sections_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channelSections_update"
    ]
    concrete = build_channel_sections_update_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.input_contract["properties"]["part"]["enum"] == ["contentDetails", "id", "snippet"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["supportedWritableParts"] == ["contentDetails", "id", "snippet"]
    assert representative.response_convention["overwriteSensitive"] is True
    assert "body.id" in metadata_text
    assert "omitted" in metadata_text.lower()


def test_representative_channels_update_example_aligns_with_concrete_contract():
    """Keep the representative channels-update example aligned with YT-211."""
    from mcp_server.tools.youtube_common.channels import build_channels_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "channels_update"
    ]
    concrete = build_channels_update_contract()

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == concrete.quota_cost
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.input_contract["properties"]["part"]["enum"] == ["brandingSettings", "localizations"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["supportedWritableParts"] == ["brandingSettings", "localizations"]


def test_representative_guideCategories_list_example_aligns_with_concrete_contract():
    """Keep the representative guideCategories-list example aligned with YT-223."""
    from mcp_server.tools.youtube_common.guide_categories import build_guide_categories_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "guideCategories_list"
    ]
    concrete = build_guide_categories_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "regionCode" in metadata_text
    assert "deprecated" in metadata_text.lower()


def test_representative_i18nLanguages_list_example_aligns_with_concrete_contract():
    """Keep the representative i18nLanguages-list example aligned with YT-224."""
    from mcp_server.tools.youtube_common.localization import build_i18n_languages_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "i18nLanguages_list"
    ]
    concrete = build_i18n_languages_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert "translation" in metadata_text


def test_representative_i18nLanguages_list_metadata_exposes_localization_usage():
    """Expose quota, auth, and localization guidance in the representative catalog."""
    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "i18nLanguages_list"
    ]
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert "localization-language" in metadata_text
    assert "translate" in metadata_text or "translation" in metadata_text


def test_representative_i18nRegions_list_example_aligns_with_concrete_contract():
    """Keep the representative i18nRegions-list example aligned with YT-225."""
    from mcp_server.tools.youtube_common.localization import build_i18n_regions_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "i18nRegions_list"
    ]
    concrete = build_i18n_regions_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert "language lookup" in metadata_text
    assert "geotarget" in metadata_text


def test_representative_i18nRegions_list_metadata_exposes_region_usage():
    """Expose quota, auth, and region guidance in the representative catalog."""
    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "i18nRegions_list"
    ]
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert "localization-region" in metadata_text
    assert "geotarget" in metadata_text


def test_representative_members_list_example_aligns_with_concrete_contract():
    """Keep the representative members-list example aligned with YT-226."""
    from mcp_server.tools.youtube_common.members import build_members_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "members_list"
    ]
    concrete = build_members_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 2
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text.lower()


def test_representative_members_list_metadata_exposes_membership_usage():
    """Expose quota, auth, owner access, and membership guidance in the catalog."""
    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "members_list"
    ]
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 2
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert metadata["inputContract"]["properties"]["mode"]["enum"] == ["all_current", "updates"]
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert "subscriber lookup" in metadata_text
    assert "membership-level" in metadata_text


def test_representative_members_list_descriptor_examples_cover_boundaries():
    """Expose representative members-list examples for success and safe failure boundaries."""
    from mcp_server.tools.youtube_common.members import build_members_list_tool_descriptor

    descriptor = build_members_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert {
        "current_members_listing",
        "membership_updates_listing",
        "paged_members_listing",
        "empty_success",
        "missing_part",
        "missing_mode",
        "unsupported_mode",
        "invalid_max_results",
        "unsupported_option",
        "access_or_membership_eligibility_failure",
        "out_of_scope_subscriber_or_analytics_request",
    }.issubset(example_names)


def test_representative_examples_expose_complete_metadata_standard():
    """Require representative examples to expose the YT-202 metadata standard."""
    assert len(REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS) >= 10

    for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS:
        metadata = contract.to_tool_metadata()
        assert metadata["availabilityState"]
        assert metadata["usageNotes"]
        assert f"Quota cost: {metadata['quotaCost']}" in metadata["description"]
        assert any(f"Quota cost: {metadata['quotaCost']}" in note for note in metadata["usageNotes"])
        assert metadata["authMode"] in {"api_key", "oauth_required", "mixed/conditional"}


def test_representative_examples_match_derived_resource_method_names():
    """Keep representative public names derived from upstream identities."""
    from mcp_server.tools.youtube_common import derive_tool_name

    for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS:
        assert contract.tool_name == derive_tool_name(contract.upstream_resource, contract.upstream_method)


def test_representative_examples_include_response_boundary_metadata():
    """Cover response boundaries across representative result shapes."""
    by_kind = {
        contract.response_convention["resultKind"]: contract.to_tool_metadata()["responseBoundary"]["boundaryKind"]
        for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
    }
    upload_boundaries = {
        contract.to_tool_metadata()["responseBoundary"]["boundaryKind"]
        for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS
        if contract.response_convention["resultKind"] == "upload_result"
    }

    assert by_kind["list"] in {"near_raw", "lightly_reshaped"}
    assert by_kind["lookup"] in {"near_raw", "lightly_reshaped"}
    assert by_kind["mutation_acknowledgment"] == "lightly_reshaped"
    assert "lightly_reshaped" in upload_boundaries
    assert "near_raw" in upload_boundaries
    assert by_kind["download_wrapper"] in {"near_raw", "lightly_reshaped"}


def test_representative_examples_cover_required_us2_shapes():
    """Cover the shared shape decisions required before endpoint slices."""
    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}

    assert by_name["playlistItems_list"].response_convention["resultKind"] == "list"
    assert by_name["videos_update"].response_convention["resultKind"] == "mutation_acknowledgment"
    assert by_name["videos_insert"].response_convention["resultKind"] == "upload_result"
    assert by_name["captions_download"].response_convention["resultKind"] == "download_wrapper"
    assert by_name["search_list"].quota_cost == 100
    assert by_name["guideCategories_list"].caveats
    assert by_name["channels_update"].quota_cost == 50
    assert by_name["channels_update"].response_convention["resultKind"] == "updated_resource"
    assert by_name["channelSections_update"].quota_cost == 50
    assert by_name["channelSections_update"].response_convention["resultKind"] == "updated_resource"
