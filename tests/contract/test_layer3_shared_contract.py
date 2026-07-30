"""Contract tests for shared Layer 3 YouTube tool contracts."""


def test_layer3_package_exposes_shared_contract_boundaries():
    """Require the Layer 3 package to expose shared contract surfaces only."""
    import mcp_server.tools.youtube_layer3 as youtube_layer3

    assert youtube_layer3.SHARED_LAYER3_HELPER_BOUNDARY == "representative_contracts_only"
    assert youtube_layer3.CONCRETE_LAYER3_TOOL_EXECUTION_ENABLED is False


def test_layer3_contract_module_declares_no_concrete_tool_scope():
    """Require public contract primitives to declare non-executing scope."""
    from mcp_server.tools.youtube_layer3 import contracts

    assert contracts.CONCRETE_LAYER3_TOOL_EXECUTION_ENABLED is False
    assert contracts.SHARED_LAYER3_HELPER_BOUNDARY == "representative_contracts_only"


def test_layer3_tool_contract_requires_public_metadata():
    """Require representative Layer 3 contracts to expose MCP-facing metadata."""
    from mcp_server.tools.youtube_layer3 import Layer3ToolContract, Layer3ToolFamily

    contract = Layer3ToolContract(
        tool_name="videos_getVideo",
        family=Layer3ToolFamily.VIDEOS,
        description="Return normalized details for one YouTube video.",
        parameters=("videoId", "parts"),
        response_fields=(
            {"fieldName": "id", "category": "raw_upstream", "source": "videos.list"},
            {"fieldName": "title", "category": "normalized", "source": "snippet.title"},
        ),
        composition_boundary={"kind": "normalized_retrieval", "boundedness": "single video"},
        lower_layer_dependencies=("videos.list",),
        auth_and_quota_notes=("Uses videos.list quota and public/private video auth caveats.",),
        partial_result_policy="Return unavailable field markers for hidden counts.",
        error_categories=("invalid_parameters", "unavailable_resource", "upstream_failure"),
        review_evidence=("representative_contract",),
    )

    metadata = contract.to_tool_metadata()

    assert metadata["name"] == "videos_getVideo"
    assert metadata["family"] == "videos"
    assert metadata["parameters"] == ["videoId", "parts"]
    assert metadata["compositionBoundary"]["kind"] == "normalized_retrieval"
    assert metadata["lowerLayerDependencies"] == ["videos.list"]
    assert metadata["representativeOnly"] is True


def test_layer3_public_metadata_rejects_unsafe_fields():
    """Reject public Layer 3 metadata that exposes unsafe diagnostic fields."""
    import pytest

    from mcp_server.tools.youtube_layer3 import Layer3ToolContractError, validate_safe_public_metadata

    with pytest.raises(Layer3ToolContractError):
        validate_safe_public_metadata({"safe": "ok", "oauthToken": "secret"})


def test_layer3_public_metadata_rejects_secret_diagnostic_fields():
    """Reject common secret, stack trace, signed URL, and raw media fields."""
    import pytest

    from mcp_server.tools.youtube_layer3 import Layer3ToolContractError, validate_safe_public_metadata

    unsafe_examples = (
        {"apiKey": "hidden"},
        {"secretValue": "hidden"},
        {"stackTrace": "hidden"},
        {"signedUrl": "hidden"},
        {"rawMediaPayload": "hidden"},
        {"nested": {"accessToken": "hidden"}},
    )

    for metadata in unsafe_examples:
        with pytest.raises(Layer3ToolContractError):
            validate_safe_public_metadata(metadata)


def test_response_field_provenance_requires_heuristic_disclosure():
    """Require heuristic fields to include basis and limitation notes."""
    import pytest

    from mcp_server.tools.youtube_layer3 import Layer3ToolContractError
    from mcp_server.tools.youtube_layer3.conventions import ResponseFieldCategory, ResponseFieldProvenance

    provenance = ResponseFieldProvenance(
        field_name="creatorSignals",
        category=ResponseFieldCategory.HEURISTIC_INFERRED,
        source="Public channel metadata and recent upload signals.",
        caller_guidance="Use as an approximate creator-oriented signal.",
        limitations="May produce false positives.",
    )

    assert provenance.to_metadata()["category"] == "heuristic_inferred"

    with pytest.raises(Layer3ToolContractError):
        ResponseFieldProvenance(
            field_name="creatorSignals",
            category=ResponseFieldCategory.HEURISTIC_INFERRED,
            source="Public channel metadata.",
            caller_guidance="Use carefully.",
            limitations="",
        )


def test_heuristic_disclosure_requires_basis_and_limitations():
    """Require heuristic disclosures to tell callers how to treat inferred fields."""
    import pytest

    from mcp_server.tools.youtube_layer3 import Layer3ToolContractError
    from mcp_server.tools.youtube_layer3.conventions import HeuristicDisclosure

    disclosure = HeuristicDisclosure(
        name="rankingScore",
        basis="Search rank, channel metadata, and recency signals.",
        limitations="Approximate ordering only.",
        applicable_tools=("videos_searchVideos", "channels_findCreators"),
        safe_usage_guidance="Use for sorting support, not as a factual upstream field.",
    )

    assert disclosure.to_metadata()["basis"].startswith("Search rank")

    with pytest.raises(Layer3ToolContractError):
        HeuristicDisclosure(
            name="rankingScore",
            basis="",
            limitations="Approximate ordering only.",
            applicable_tools=("videos_searchVideos",),
            safe_usage_guidance="Use carefully.",
        )
