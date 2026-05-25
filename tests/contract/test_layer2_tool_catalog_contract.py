"""Contract tests for representative Layer 2 tool catalog examples."""

from mcp_server.tools.youtube_common import AuthMode, REPRESENTATIVE_LAYER2_CONTRACTS


def test_representative_examples_include_required_us1_shapes():
    """Expose representative examples for core naming and metadata shapes."""
    names = {contract.tool_name for contract in REPRESENTATIVE_LAYER2_CONTRACTS}

    assert {
        "activities_list",
        "comments_setModerationStatus",
        "videos_getRating",
        "watermarks_unset",
    }.issubset(names)


def test_representative_examples_expose_auth_quota_and_caveats():
    """Make auth, quota, and caveat metadata visible in representative examples."""
    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_LAYER2_CONTRACTS}

    assert by_name["activities_list"].auth_mode is AuthMode.MIXED
    assert by_name["activities_list"].quota_cost == 1
    assert by_name["comments_setModerationStatus"].auth_mode is AuthMode.OAUTH_REQUIRED
    assert by_name["videos_getRating"].upstream_method == "getRating"
    assert by_name["watermarks_unset"].caveats


def test_representative_examples_cover_required_us2_shapes():
    """Cover the shared shape decisions required before endpoint slices."""
    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_LAYER2_CONTRACTS}

    assert by_name["playlistItems_list"].response_convention["resultKind"] == "list"
    assert by_name["videos_update"].response_convention["resultKind"] == "mutation_acknowledgment"
    assert by_name["videos_insert"].response_convention["resultKind"] == "upload_result"
    assert by_name["captions_download"].response_convention["resultKind"] == "download_wrapper"
    assert by_name["search_list"].quota_cost == 100
    assert by_name["guideCategories_list"].caveats
