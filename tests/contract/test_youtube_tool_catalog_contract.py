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
        "membershipsLevels_list",
        "playlistImages_list",
        "playlistImages_insert",
        "playlistImages_update",
        "playlistImages_delete",
        "playlistItems_delete",
        "playlists_delete",
        "search_list",
        "subscriptions_delete",
        "subscriptions_insert",
        "subscriptions_list",
        "thumbnails_set",
        "videoAbuseReportReasons_list",
        "videoCategories_list",
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


def test_representative_thumbnails_set_example_aligns_with_concrete_contract():
    """Keep the representative thumbnails-set example aligned with YT-244."""
    from mcp_server.tools.youtube_common.thumbnails import build_thumbnails_set_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "thumbnails_set"
    ]
    concrete = build_thumbnails_set_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "upload_result"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "videoId" in metadata_text
    assert "media" in metadata_text
    assert "thumbnail generation" in metadata_text


def test_representative_video_abuse_report_reasons_example_aligns_with_concrete_contract():
    """Keep the representative video-abuse-report-reasons example aligned with YT-245."""
    from mcp_server.tools.youtube_common.video_abuse_report_reasons import (
        build_video_abuse_report_reasons_list_contract,
        build_video_abuse_report_reasons_list_tool_descriptor,
    )

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "videoAbuseReportReasons_list"
    ]
    concrete = build_video_abuse_report_reasons_list_contract()
    descriptor = build_video_abuse_report_reasons_list_tool_descriptor()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == ["part", "hl"]
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "list"
    assert representative.response_convention["localizationFields"] == ["hl"]
    assert "report submission" in metadata_text
    assert "moderation" in metadata_text
    assert {
        "localized_reason_lookup",
        "empty_success",
        "missing_hl",
        "access_failure",
        "quota_or_upstream_failure",
    }.issubset(example_names)


def test_representative_video_categories_example_aligns_with_concrete_contract():
    """Keep the representative video-categories example aligned with YT-246."""
    from mcp_server.tools.youtube_common.video_categories import (
        build_video_categories_list_contract,
        build_video_categories_list_tool_descriptor,
    )

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "videoCategories_list"
    ]
    concrete = build_video_categories_list_contract()
    descriptor = build_video_categories_list_tool_descriptor()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.API_KEY
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == ["part"]
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "list"
    assert representative.response_convention["selectorFields"] == ["regionCode", "id"]
    assert "regionCode" in metadata_text
    assert "category recommendation" in metadata_text
    assert {
        "region_category_lookup",
        "category_id_lookup",
        "empty_success",
        "missing_selector",
        "conflicting_selectors",
        "access_failure",
        "quota_or_upstream_failure",
    }.issubset(example_names)


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


def test_representative_playlist_images_delete_example_aligns_with_concrete_contract():
    """Keep the representative playlistImages-delete example aligned with YT-231."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_delete"
    ]
    concrete = build_playlist_images_delete_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "deletion_acknowledgment"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["successStatus"] == 204
    assert representative.response_convention["bodyPolicy"] == "no_upstream_body"
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text


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


def test_representative_memberships_levels_list_example_aligns_with_concrete_contract():
    """Keep the representative membershipsLevels-list example aligned with YT-227."""
    from mcp_server.tools.youtube_common.memberships_levels import build_memberships_levels_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "membershipsLevels_list"
    ]
    concrete = build_memberships_levels_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text.lower()


def test_representative_memberships_levels_list_metadata_exposes_membership_level_usage():
    """Expose quota, auth, owner access, and membership-level guidance in the catalog."""
    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "membershipsLevels_list"
    ]
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "pageToken" not in metadata["inputContract"]["properties"]
    assert "maxResults" not in metadata["inputContract"]["properties"]
    assert "member listing" in metadata_text
    assert "subscriber lookup" in metadata_text


def test_representative_memberships_levels_list_descriptor_examples_cover_boundaries():
    """Expose representative membershipsLevels-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.memberships_levels import build_memberships_levels_list_tool_descriptor

    descriptor = build_memberships_levels_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert {
        "membership_levels_listing",
        "empty_success",
        "missing_part",
        "invalid_part",
        "unsupported_option",
        "access_or_membership_eligibility_failure",
        "out_of_scope_member_or_analytics_request",
    }.issubset(example_names)


def test_representative_playlist_images_list_example_aligns_with_concrete_contract():
    """Keep the representative playlistImages-list example aligned with YT-228."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_list"
    ]
    concrete = build_playlist_images_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(representative.input_contract["properties"])
    assert "playlistId" in metadata_text
    assert "thumbnail replacement" in metadata_text


def test_representative_playlist_items_list_example_aligns_with_concrete_contract():
    """Keep the representative playlistItems-list example aligned with YT-232."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_list"
    ]
    concrete = build_playlist_items_list_contract()
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
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(representative.input_contract["properties"])
    assert "playlistItems.list" in metadata_text
    assert "playlist item mutation" in metadata_text


def test_representative_playlist_items_list_descriptor_examples_cover_boundaries():
    """Expose representative playlistItems-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_list_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_list"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_items_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["properties"]["part"]["enum"] == [
        "contentDetails",
        "id",
        "snippet",
        "status",
    ]
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "playlist_scoped_item_listing",
        "direct_item_lookup",
        "paged_playlist_item_listing",
        "empty_success",
        "missing_selector",
        "conflicting_selector",
        "paging_with_id",
        "access_failure",
        "out_of_scope_playlist_item_workflow",
    }.issubset(example_names)


def test_representative_playlists_list_example_aligns_with_concrete_contract():
    """Keep the representative playlists-list example aligned with YT-236."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_list"
    ]
    concrete = build_playlists_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.MIXED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"channelId", "id", "mine", "pageToken", "maxResults"}.issubset(
        representative.input_contract["properties"]
    )
    assert "playlists.list" in metadata_text
    assert "playlist item traversal" in metadata_text


def test_representative_playlists_list_descriptor_examples_cover_boundaries():
    """Expose representative playlists-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_list_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_list"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlists_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "channel_scoped_playlist_listing",
        "direct_playlist_lookup",
        "owner_scoped_playlist_listing",
        "paged_playlist_listing",
        "empty_success",
        "missing_selector",
        "conflicting_selector",
        "paging_with_id",
        "access_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlists_insert_example_aligns_with_concrete_contract():
    """Keep the representative playlists-insert example aligned with YT-237."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_insert"
    ]
    concrete = build_playlists_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"part", "body"}.issubset(representative.input_contract["properties"])
    assert "playlists.insert" in metadata_text
    assert "body.snippet.title" in metadata_text
    assert "duplicate" in metadata_text.lower()


def test_representative_playlists_insert_descriptor_examples_cover_boundaries():
    """Expose representative playlists-insert examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_insert_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_insert"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlists_insert_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "oauth_playlist_creation",
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_title",
        "unsupported_write_field",
        "access_failure",
        "quota_or_upstream_create_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlists_update_example_aligns_with_concrete_contract():
    """Keep the representative playlists-update example aligned with YT-238."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_update"
    ]
    concrete = build_playlists_update_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"part", "body"}.issubset(representative.input_contract["properties"])
    assert "playlists.update" in metadata_text
    assert "body.id" in metadata_text
    assert "body.snippet.title" in metadata_text
    assert "repeat" in metadata_text.lower()


def test_representative_playlists_update_descriptor_examples_cover_boundaries():
    """Expose representative playlists-update examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_update_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_update"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlists_update_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "oauth_playlist_update",
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_target_identity",
        "missing_title",
        "unsupported_write_field",
        "access_failure",
        "quota_or_upstream_update_failure",
        "repeat_request_caveat",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlists_delete_example_aligns_with_concrete_contract():
    """Keep the representative playlists-delete example aligned with YT-239."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_delete"
    ]
    concrete = build_playlists_delete_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "id" in representative.input_contract["properties"]
    assert "playlists.delete" in metadata_text
    assert "destructive" in metadata_text.lower()
    assert "repeat" in metadata_text.lower()


def test_representative_playlists_delete_descriptor_examples_cover_boundaries():
    """Expose representative playlists-delete examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlists import build_playlists_delete_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlists_delete"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlists_delete_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert "id" in metadata["inputContract"]["properties"]
    assert {
        "oauth_playlist_deletion",
        "no_body_deletion_acknowledgment",
        "missing_target_identity",
        "malformed_target_identity",
        "unsupported_field",
        "access_failure",
        "insufficient_authorization",
        "missing_resource_or_already_deleted",
        "quota_or_upstream_delete_failure",
        "repeat_delete_caveat",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlist_items_insert_example_aligns_with_concrete_contract():
    """Keep the representative playlistItems-insert example aligned with YT-233."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_insert"
    ]
    concrete = build_playlist_items_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "playlist item listing" in metadata_text


def test_representative_playlist_items_insert_descriptor_examples_cover_boundaries():
    """Expose representative playlistItems-insert examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_insert_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_insert"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_items_insert_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {
        "oauth_playlist_item_insertion",
        "positioned_playlist_item_insertion",
        "missing_part",
        "invalid_part",
        "missing_playlist_id",
        "missing_video_reference",
        "invalid_body",
        "unsupported_placement",
        "authorization_failure",
        "quota_or_upstream_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlist_items_update_example_aligns_with_concrete_contract():
    """Keep the representative playlistItems-update example aligned with YT-234."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_update"
    ]
    concrete = build_playlist_items_update_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "updated_resource"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "playlist item listing" in metadata_text


def test_representative_playlist_items_update_descriptor_examples_cover_boundaries():
    """Expose representative playlistItems-update examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_update_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_update"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_items_update_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {
        "oauth_playlist_item_update",
        "missing_part",
        "invalid_part",
        "missing_target_identity",
        "missing_playlist_id",
        "missing_video_reference",
        "invalid_body",
        "unsupported_writable_field",
        "authorization_failure",
        "quota_or_upstream_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_playlist_items_delete_example_aligns_with_concrete_contract():
    """Keep the representative playlistItems-delete example aligned with YT-235."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_delete"
    ]
    concrete = build_playlist_items_delete_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "mutation_acknowledgment"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert representative.response_convention["successStatus"] == 204
    assert "id" in metadata_text
    assert "destructive" in metadata_text
    assert "playlist item listing" in metadata_text or "playlist-item listing" in metadata_text


def test_representative_playlist_items_delete_descriptor_examples_cover_boundaries():
    """Expose representative playlistItems-delete examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_items import build_playlist_items_delete_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistItems_delete"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_items_delete_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert {
        "oauth_playlist_item_deletion",
        "no_body_deletion_acknowledgment",
        "missing_id",
        "invalid_id",
        "unsupported_input",
        "authorization_failure",
        "quota_or_upstream_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(example_names)


def test_representative_search_list_example_aligns_with_concrete_contract():
    """Keep the representative search-list example aligned with YT-240."""
    from mcp_server.tools.youtube_common.search import build_search_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "search_list"
    ]
    concrete = build_search_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 100
    assert representative.auth_mode is AuthMode.MIXED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "list"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "part" in metadata_text
    assert "q" in metadata_text
    assert "OAuth" in metadata_text
    assert "API-key" in metadata_text


def test_representative_search_list_descriptor_examples_cover_boundaries():
    """Expose representative search-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.search import build_search_list_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "search_list"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_search_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 100
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part", "q"]
    assert {
        "public_keyword_search",
        "type_filtered_video_search",
        "channel_scoped_search",
        "date_and_locale_refinement",
        "restricted_oauth_search",
        "paginated_search",
        "empty_success",
        "missing_query",
        "incompatible_video_filter",
        "restricted_filter_conflict",
        "access_failure",
        "quota_or_upstream_failure",
        "out_of_scope_enrichment_request",
    }.issubset(example_names)


def test_representative_subscriptions_list_example_aligns_with_concrete_contract():
    """Keep the representative subscriptions-list example aligned with YT-241."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_list_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_list"
    ]
    concrete = build_subscriptions_list_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 1
    assert representative.auth_mode is AuthMode.MIXED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "list"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "channelId" in metadata_text
    assert "myRecentSubscribers" in metadata_text
    assert "mySubscribers" in metadata_text
    assert "OAuth" in metadata_text


def test_representative_subscriptions_list_descriptor_examples_cover_boundaries():
    """Expose representative subscriptions-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_list_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_list"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_subscriptions_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {
        "channel_subscription_listing",
        "direct_subscription_lookup",
        "current_user_subscriptions",
        "recent_subscribers",
        "subscriber_list",
        "paginated_subscription_listing",
        "empty_success",
        "missing_selector",
        "conflicting_selector",
        "access_failure",
        "quota_or_upstream_failure",
        "out_of_scope_enrichment_request",
    }.issubset(example_names)


def test_representative_subscriptions_insert_example_aligns_with_concrete_contract():
    """Keep the representative subscriptions-insert example aligned with YT-242."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_insert"
    ]
    concrete = build_subscriptions_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == "created_resource"
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert "body.snippet.resourceId.channelId" in metadata_text
    assert "OAuth" in metadata_text


def test_representative_subscriptions_insert_descriptor_examples_cover_boundaries():
    """Expose representative subscriptions-insert examples for success and safe failures."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_insert_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_insert"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_subscriptions_insert_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {
        "oauth_subscription_creation",
        "oauth_subscription_creation_with_kind",
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_target_channel",
        "invalid_resource_kind",
        "unsupported_write_field",
        "access_failure",
        "duplicate_or_ineligible_target",
        "quota_or_upstream_create_failure",
        "out_of_scope_subscription_management_request",
    }.issubset(example_names)


def test_representative_subscriptions_delete_example_aligns_with_concrete_contract():
    """Keep the representative subscriptions-delete example aligned with YT-243."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_delete_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_delete"
    ]
    concrete = build_subscriptions_delete_contract()
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
    assert "id" in metadata_text
    assert "OAuth" in metadata_text


def test_representative_subscriptions_delete_descriptor_examples_cover_boundaries():
    """Expose representative subscriptions-delete examples for success and safe failures."""
    from mcp_server.tools.youtube_common.subscriptions import build_subscriptions_delete_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "subscriptions_delete"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_subscriptions_delete_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["id"]
    assert {
        "oauth_subscription_deletion",
        "missing_id",
        "empty_id",
        "access_failure",
        "already_removed_or_missing_target",
        "non_removable_target",
        "quota_or_upstream_delete_failure",
        "out_of_scope_subscription_management_request",
    }.issubset(example_names)


def test_representative_playlist_images_list_descriptor_examples_cover_boundaries():
    """Expose representative playlistImages-list examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_list_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_list"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_images_list_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["properties"]["part"] == {"type": "string", "minLength": 1}
    assert {"pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "playlist_scoped_image_listing",
        "direct_image_lookup",
        "empty_success",
        "missing_selector",
        "conflicting_selector",
        "paging_with_id",
        "access_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)


def test_representative_playlist_images_insert_example_aligns_with_concrete_contract():
    """Keep the representative playlistImages-insert example aligned with YT-229."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_insert_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_insert"
    ]
    concrete = build_playlist_images_insert_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"part", "body", "media"}.issubset(representative.input_contract["properties"])
    assert "media" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text


def test_representative_playlist_images_insert_descriptor_examples_cover_boundaries():
    """Expose representative playlistImages-insert examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_insert_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_insert"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_images_insert_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "authorized_playlist_image_insert",
        "missing_part",
        "invalid_part",
        "missing_body",
        "invalid_body",
        "missing_media",
        "unsupported_media",
        "access_failure",
        "quota_or_upstream_insert_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)


def test_representative_playlist_images_update_example_aligns_with_concrete_contract():
    """Keep the representative playlistImages-update example aligned with YT-230."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_update_contract

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_update"
    ]
    concrete = build_playlist_images_update_contract()
    metadata = representative.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert representative.tool_name == concrete.tool_name
    assert representative.upstream_resource == concrete.upstream_resource
    assert representative.upstream_method == concrete.upstream_method
    assert representative.quota_cost == 50
    assert representative.auth_mode is AuthMode.OAUTH_REQUIRED
    assert representative.auth_mode == concrete.auth_mode
    assert representative.availability_state == concrete.availability_state
    assert representative.input_contract["required"] == concrete.input_contract["required"]
    assert representative.response_convention["resultKind"] == concrete.response_convention["resultKind"]
    assert {"part", "body", "media"}.issubset(representative.input_contract["properties"])
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "media" in metadata_text


def test_representative_playlist_images_update_descriptor_examples_cover_boundaries():
    """Expose representative playlistImages-update examples for success and safe failures."""
    from mcp_server.tools.youtube_common.playlist_images import build_playlist_images_update_tool_descriptor

    representative = {contract.tool_name: contract for contract in REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS}[
        "playlistImages_update"
    ]
    metadata = representative.to_tool_metadata()
    descriptor = build_playlist_images_update_tool_descriptor()
    example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert {
        "authorized_playlist_image_update",
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_target_identity",
        "missing_playlist_context",
        "missing_media",
        "unsupported_media",
        "access_failure",
        "quota_or_upstream_update_failure",
        "out_of_scope_image_management_request",
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
