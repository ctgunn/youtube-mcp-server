"""Contract tests for representative Layer 2 tool catalog examples."""

from mcp_server.tools.youtube_common import AuthMode, REPRESENTATIVE_LAYER2_CONTRACTS


def test_representative_examples_include_required_us1_shapes():
    """Expose representative examples for core naming and metadata shapes."""
    names = {contract.tool_name for contract in REPRESENTATIVE_LAYER2_CONTRACTS}

    assert {
        "activities_list",
        "playlists_insert",
        "comments_setModerationStatus",
        "videos_getRating",
        "videos_reportAbuse",
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


def test_representative_examples_expose_complete_metadata_standard():
    """Require representative examples to expose the YT-202 metadata standard."""
    assert len(REPRESENTATIVE_LAYER2_CONTRACTS) >= 10

    for contract in REPRESENTATIVE_LAYER2_CONTRACTS:
        metadata = contract.to_tool_metadata()
        assert metadata["availabilityState"]
        assert metadata["usageNotes"]
        assert f"Quota cost: {metadata['quotaCost']}" in metadata["description"]
        assert any(f"Quota cost: {metadata['quotaCost']}" in note for note in metadata["usageNotes"])
        assert metadata["authMode"] in {"api_key", "oauth_required", "mixed/conditional"}


def test_representative_examples_match_derived_resource_method_names():
    """Keep representative public names derived from upstream identities."""
    from mcp_server.tools.youtube_common import derive_tool_name

    for contract in REPRESENTATIVE_LAYER2_CONTRACTS:
        assert contract.tool_name == derive_tool_name(contract.upstream_resource, contract.upstream_method)


def test_representative_examples_include_response_boundary_metadata():
    """Cover response boundaries across representative result shapes."""
    by_kind = {
        contract.response_convention["resultKind"]: contract.to_tool_metadata()["responseBoundary"]["boundaryKind"]
        for contract in REPRESENTATIVE_LAYER2_CONTRACTS
    }

    assert by_kind["list"] in {"near_raw", "lightly_reshaped"}
    assert by_kind["lookup"] in {"near_raw", "lightly_reshaped"}
    assert by_kind["mutation_acknowledgment"] == "lightly_reshaped"
    assert by_kind["upload_result"] == "lightly_reshaped"
    assert by_kind["download_wrapper"] == "lightly_reshaped"


def test_representative_examples_cover_required_us2_shapes():
    """Cover the shared shape decisions required before endpoint slices."""
    by_name = {contract.tool_name: contract for contract in REPRESENTATIVE_LAYER2_CONTRACTS}

    assert by_name["playlistItems_list"].response_convention["resultKind"] == "list"
    assert by_name["videos_update"].response_convention["resultKind"] == "mutation_acknowledgment"
    assert by_name["videos_insert"].response_convention["resultKind"] == "upload_result"
    assert by_name["captions_download"].response_convention["resultKind"] == "download_wrapper"
    assert by_name["search_list"].quota_cost == 100
    assert by_name["guideCategories_list"].caveats
