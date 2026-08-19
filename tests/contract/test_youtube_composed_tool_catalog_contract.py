"""Contract tests for the Layer 3 public YouTube catalog."""


EXPECTED_TOOL_NAMES = {
    "videos_getVideo",
    "videos_searchVideos",
    "videos_getStatistics",
    "transcripts_getTranscript",
    "transcripts_listLanguages",
    "transcripts_getTimestampedCaptions",
    "transcripts_searchTranscript",
    "channels_getChannel",
    "channels_getChannels",
    "channels_searchChannels",
    "channels_findCreators",
    "channels_listVideos",
    "channels_listPlaylists",
    "channels_getStatistics",
    "channels_searchContent",
    "playlists_getPlaylist",
    "playlists_getPlaylistItems",
    "playlists_searchItems",
    "playlists_getVideoTranscripts",
}


def test_planned_catalog_names_match_initial_prd_catalog():
    """Validate all planned Layer 3 public names from the shared catalog."""
    from mcp_server.tools.youtube_composed import PLANNED_TOOL_NAMES

    assert set(PLANNED_TOOL_NAMES) == EXPECTED_TOOL_NAMES
    assert len(PLANNED_TOOL_NAMES) == 19


def test_planned_catalog_names_use_grouped_family_prefixes():
    """Require each planned public name to use its owning family prefix."""
    from mcp_server.tools.youtube_composed import PLANNED_TOOLS_BY_FAMILY

    assert set(PLANNED_TOOLS_BY_FAMILY) == {"videos", "channels", "playlists", "transcripts"}
    for family, tool_names in PLANNED_TOOLS_BY_FAMILY.items():
        assert tool_names
        assert all(name.startswith(f"{family}_") for name in tool_names)


def test_representative_contract_examples_cover_catalog_shapes():
    """Expose representative non-executing examples for initial Layer 3 shapes."""
    from mcp_server.tools.youtube_composed import REPRESENTATIVE_TOOL_CONTRACTS

    names = {contract.tool_name for contract in REPRESENTATIVE_TOOL_CONTRACTS}

    assert len(REPRESENTATIVE_TOOL_CONTRACTS) >= 8
    assert {
        "videos_getVideo",
        "videos_searchVideos",
        "channels_findCreators",
        "transcripts_getTranscript",
        "transcripts_searchTranscript",
        "playlists_getPlaylistItems",
        "playlists_searchItems",
        "playlists_getVideoTranscripts",
    }.issubset(names)


def test_representative_examples_disclose_provenance_and_heuristics():
    """Require representative examples to separate raw, normalized, and heuristic fields."""
    from mcp_server.tools.youtube_composed import REPRESENTATIVE_TOOL_CONTRACTS

    categories = {
        field["category"]
        for contract in REPRESENTATIVE_TOOL_CONTRACTS
        for field in contract.to_tool_metadata()["responseFields"]
    }
    heuristic_contracts = [contract for contract in REPRESENTATIVE_TOOL_CONTRACTS if contract.heuristics]

    assert {"raw_upstream", "normalized", "heuristic_inferred"}.issubset(categories)
    assert heuristic_contracts
    assert all(disclosure.get("basis") and disclosure.get("limitations") for contract in heuristic_contracts for disclosure in contract.heuristics)


def test_ranking_filtering_and_composition_rules_are_metadata_ready():
    """Expose ranking/filtering, composition, partial-result, and error metadata."""
    from mcp_server.tools.youtube_composed.conventions import (
        CompositionBoundary,
        CompositionKind,
        ErrorCategory,
        RankingFilteringRule,
    )

    boundary = CompositionBoundary(
        kind=CompositionKind.FAN_OUT,
        lower_layer_dependencies=("playlistItems.list", "captions.list", "captions.download"),
        quota_behavior="Quota multiplies across bounded playlist videos.",
        auth_sensitivity="Caption access may require OAuth authorization.",
        partial_result_policy="Return per-video status for inaccessible captions.",
        boundedness="Bounded by maxResults.",
        caller_caveats=("High-quota fan-out.",),
    )
    rule = RankingFilteringRule(
        name="creatorOnly",
        semantics="Filter to channels that satisfy shared creator heuristics.",
        allowed_values=("true", "false"),
        default_behavior="Do not filter by creator heuristic when omitted.",
        applicable_families=("videos", "channels"),
        dependency_notes="Requires channel metadata enrichment.",
        partial_data_behavior="Exclude candidates only when creatorOnly is true and data is insufficient.",
    )

    assert boundary.to_metadata()["kind"] == "fan_out"
    assert rule.to_metadata()["name"] == "creatorOnly"
    assert ErrorCategory.PARTIAL_ENRICHMENT_FAILURE.value == "partial_enrichment_failure"


def test_each_planned_name_maps_to_one_family_and_source_area():
    """Map every planned public name to exactly one family and source module."""
    from mcp_server.tools.youtube_composed import (
        PLANNED_TOOL_NAMES,
        get_family,
        get_family_for_tool_name,
    )

    seen = {}
    for tool_name in PLANNED_TOOL_NAMES:
        family_name = get_family_for_tool_name(tool_name)
        family = get_family(family_name)
        seen[tool_name] = family_name

        assert tool_name in family.planned_tools
        assert family.definition_location.endswith(f"src/mcp_server/tools/youtube_composed/{family_name}.py")
        assert family.example_location.endswith("src/mcp_server/tools/youtube_composed/examples.py")

    assert len(seen) == len(PLANNED_TOOL_NAMES)
    assert set(seen.values()) == {"videos", "channels", "playlists", "transcripts"}
