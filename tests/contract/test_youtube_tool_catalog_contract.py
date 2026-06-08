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
        "playlists_insert",
        "comments_setModerationStatus",
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
