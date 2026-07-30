"""Unit tests for shared Layer 3 YouTube scaffolding helpers."""


def test_package_imports():
    """Confirm the shared Layer 3 package can be imported."""
    import mcp_server.tools.youtube_composed as youtube_composed

    assert youtube_composed is not None


def test_package_boundary_avoids_execution_dependencies():
    """Keep Layer 3 shared scaffolding free of concrete execution dependencies."""
    import mcp_server.tools.youtube_composed as youtube_composed

    forbidden_modules = ("fastapi", "uvicorn", "redis", "subprocess", "urllib")

    assert youtube_composed.CONCRETE_TOOL_EXECUTION_ENABLED is False
    assert not any(name in youtube_composed.__dict__ for name in forbidden_modules)


def test_contract_module_keeps_shared_scope():
    """Expose shared Layer 3 scope without hosted transport or persistence state."""
    from mcp_server.tools.youtube_composed import contracts

    assert contracts.SHARED_HELPER_BOUNDARY == "representative_contracts_only"
    assert contracts.CONCRETE_TOOL_EXECUTION_ENABLED is False


def test_validate_tool_name_accepts_grouped_catalog_names():
    """Validate grouped Layer 3 public names by family."""
    from mcp_server.tools.youtube_composed import ToolFamily, validate_tool_name

    assert validate_tool_name("videos_getVideo", ToolFamily.VIDEOS) == "videos_getVideo"
    assert validate_tool_name("channels_findCreators", "channels") == "channels_findCreators"
    assert validate_tool_name("playlists_searchItems") == "playlists_searchItems"


def test_validate_tool_name_rejects_invalid_or_redundant_prefixes():
    """Reject public names outside the grouped Layer 3 catalog."""
    import pytest

    from mcp_server.tools.youtube_composed import ToolContractError, ToolFamily, validate_tool_name

    with pytest.raises(ToolContractError):
        validate_tool_name("youtube_videos_getVideo")

    with pytest.raises(ToolContractError):
        validate_tool_name("videos_getVideo", ToolFamily.CHANNELS)

    with pytest.raises(ToolContractError):
        validate_tool_name("videos_unplannedTool")


def test_shared_parameter_convention_requires_bounds_for_result_limits():
    """Require bounded behavior for repeated Layer 3 limit parameters."""
    import pytest

    from mcp_server.tools.youtube_composed import ToolContractError
    from mcp_server.tools.youtube_composed.conventions import Requiredness, SharedParameterConvention

    convention = SharedParameterConvention(
        name="maxResults",
        value_kind="integer",
        requiredness=Requiredness.OPTIONAL,
        default_behavior="Return up to 25 results when omitted.",
        bounds={"minimum": 1, "maximum": 50},
        validation_behavior="Reject values outside 1..50.",
        applicable_families=("videos", "channels", "playlists", "transcripts"),
        upstream_mapping_notes="Maps to lower-layer maxResults where available.",
    )

    metadata = convention.to_metadata()

    assert metadata["name"] == "maxResults"
    assert metadata["bounds"]["maximum"] == 50

    with pytest.raises(ToolContractError):
        SharedParameterConvention(
            name="maxResults",
            value_kind="integer",
            requiredness=Requiredness.OPTIONAL,
            default_behavior="Return a bounded count.",
            bounds={},
            validation_behavior="Reject invalid values.",
            applicable_families=("videos",),
        )


def test_date_parameter_convention_declares_iso8601_validation():
    """Require date-filter conventions to declare ISO 8601 validation behavior."""
    from mcp_server.tools.youtube_composed.conventions import Requiredness, SharedParameterConvention

    convention = SharedParameterConvention(
        name="publishedAfter",
        value_kind="iso8601_datetime",
        requiredness=Requiredness.OPTIONAL,
        default_behavior="No lower date bound when omitted.",
        bounds={"format": "ISO 8601"},
        validation_behavior="Reject invalid ISO 8601 values and reversed date windows.",
        applicable_families=("videos",),
        upstream_mapping_notes="Maps to publishedAfter in search-like workflows.",
    )

    assert convention.to_metadata()["validationBehavior"].startswith("Reject invalid ISO 8601")


def test_family_registry_exposes_placement_metadata():
    """Expose family placement rules for videos, channels, playlists, and transcripts."""
    from mcp_server.tools.youtube_composed import REQUIRED_FAMILIES, get_family

    assert REQUIRED_FAMILIES == ("videos", "channels", "playlists", "transcripts")

    videos = get_family("videos")

    assert videos.family_name == "videos"
    assert videos.public_prefix == "videos_*"
    assert "videos_getVideo" in videos.planned_tools
    assert videos.definition_location.endswith("src/mcp_server/tools/youtube_composed/videos.py")
    assert videos.handler_location.endswith("src/mcp_server/tools/youtube_composed/videos.py")
    assert "tests/contract" in videos.test_locations["contract"]


def test_family_modules_remain_scaffolding_only():
    """Keep family modules cohesive without concrete public tool handlers."""
    from mcp_server.tools.youtube_composed import channels, playlists, transcripts, videos

    for module in (videos, channels, playlists, transcripts):
        assert module.FAMILY_SCAFFOLDING.family_name in {"videos", "channels", "playlists", "transcripts"}
        assert not any(name.startswith("build_") and name.endswith("_handler") for name in dir(module))
