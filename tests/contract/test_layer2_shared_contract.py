"""Contract tests for shared Layer 2 tool contracts."""

import pytest

from mcp_server.tools.youtube_common import (
    AuthMode,
    AvailabilityState,
    ErrorCategory,
    Layer2ContractError,
    Layer2ToolContract,
    SHARED_LAYER2_HELPER_BOUNDARY,
    ResponseBoundary,
    ResponseBoundaryKind,
    ResponseConvention,
    ResponseKind,
    sanitize_error_details,
    validate_safe_public_metadata,
)


def test_layer2_tool_contract_requires_public_metadata():
    """Require every representative contract to expose MCP-facing metadata."""
    contract = Layer2ToolContract(
        tool_name="videos_list",
        upstream_resource="videos",
        upstream_method="list",
        operation_key="videos.list",
        description="List videos. Quota cost: 1. Auth: api_key or mixed/conditional.",
        auth_mode=AuthMode.MIXED,
        quota_cost=1,
        resource_family="videos",
        input_contract={"required": ["part"], "properties": {"part": {"type": "string"}}},
        response_convention={"resultKind": "list", "itemsPath": "items"},
        response_boundary={"boundaryKind": "near_raw"},
        error_categories=("invalid_request", "quota_exhausted"),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=("Quota cost: 1. Auth: mixed/conditional.",),
    )

    metadata = contract.to_tool_metadata()

    assert metadata["name"] == "videos_list"
    assert metadata["upstream"]["resource"] == "videos"
    assert metadata["upstream"]["method"] == "list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["usageNotes"]
    assert metadata["resourceFamily"] == "videos"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tool_name", ""),
        ("upstream_resource", ""),
        ("upstream_method", ""),
        ("operation_key", ""),
        ("description", ""),
        ("quota_cost", 0),
        ("resource_family", ""),
        ("input_contract", {}),
        ("response_convention", {}),
        ("response_boundary", {}),
        ("error_categories", ()),
        ("availability_state", None),
        ("usage_notes", ()),
    ],
)
def test_layer2_tool_contract_rejects_missing_required_metadata(field, value):
    """Reject contracts that omit required shared Layer 2 metadata."""
    kwargs = {
        "tool_name": "videos_list",
        "upstream_resource": "videos",
        "upstream_method": "list",
        "operation_key": "videos.list",
        "description": "List videos. Quota cost: 1. Auth: api_key.",
        "auth_mode": AuthMode.API_KEY,
        "quota_cost": 1,
        "resource_family": "videos",
        "input_contract": {"required": ["part"], "properties": {"part": {"type": "string"}}},
        "response_convention": {"resultKind": "list", "itemsPath": "items"},
        "response_boundary": {"boundaryKind": "near_raw"},
        "error_categories": ("invalid_request",),
        "availability_state": AvailabilityState.ACTIVE,
        "usage_notes": ("Quota cost: 1. Auth: api_key.",),
    }
    kwargs[field] = value

    with pytest.raises(Layer2ContractError):
        Layer2ToolContract(**kwargs)


def test_layer2_tool_contract_requires_quota_visible_description_and_notes():
    """Reject metadata that hides quota cost from caller-facing text."""
    kwargs = {
        "tool_name": "videos_list",
        "upstream_resource": "videos",
        "upstream_method": "list",
        "operation_key": "videos.list",
        "description": "List videos. Auth: api_key.",
        "auth_mode": AuthMode.API_KEY,
        "quota_cost": 1,
        "resource_family": "videos",
        "input_contract": {"required": ["part"], "properties": {"part": {"type": "string"}}},
        "response_convention": {"resultKind": "list", "itemsPath": "items"},
        "response_boundary": {"boundaryKind": "near_raw"},
        "error_categories": ("invalid_request",),
        "availability_state": AvailabilityState.ACTIVE,
        "usage_notes": ("Auth: api_key.",),
    }

    with pytest.raises(Layer2ContractError):
        Layer2ToolContract(**kwargs)


def test_layer2_tool_contract_rejects_casing_drifted_tool_names():
    """Reject public names derived from snake_case rewrites of upstream methods."""
    with pytest.raises(Layer2ContractError):
        Layer2ToolContract(
            tool_name="videos_get_rating",
            upstream_resource="videos",
            upstream_method="get_rating",
            operation_key="videos.get_rating",
            description="Get video rating. Quota cost: 1. Auth: oauth_required.",
            auth_mode=AuthMode.OAUTH_REQUIRED,
            quota_cost=1,
            resource_family="videos",
            input_contract={"required": ["id"], "properties": {"id": {"type": "string"}}},
            response_convention={"resultKind": "lookup", "itemsPath": "items"},
            response_boundary={"boundaryKind": "near_raw"},
            error_categories=("invalid_request",),
            availability_state=AvailabilityState.ACTIVE,
            usage_notes=("Quota cost: 1. Auth: oauth_required.",),
        )


@pytest.mark.parametrize(
    ("kind", "metadata_key"),
    [
        (ResponseKind.LIST, "itemsPath"),
        (ResponseKind.MUTATION_ACKNOWLEDGMENT, "acknowledgment"),
        (ResponseKind.UPLOAD_RESULT, "mediaResult"),
        (ResponseKind.DOWNLOAD_WRAPPER, "contentPolicy"),
        (ResponseKind.LOOKUP, "itemsPath"),
    ],
)
def test_response_conventions_expose_near_raw_result_shapes(kind, metadata_key):
    """Expose near-raw response conventions for representative result kinds."""
    convention = ResponseConvention(
        result_kind=kind,
        items_path="items",
        paging_fields=("nextPageToken",),
        requested_parts=("snippet",),
        wrapper_fields=("endpoint",),
        content_policy="safe_text_or_metadata_wrapper",
    )

    metadata = convention.to_metadata()

    assert metadata["resultKind"] == kind.value
    assert metadata_key in metadata


def test_response_boundary_metadata_classifies_layer2_result_scope():
    """Classify response behavior as Layer 2 or out of scope."""
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.LIGHTLY_RESHAPED,
        allowed_wrapper_fields=("endpoint", "quotaCost"),
        preserved_upstream_fields=("items", "nextPageToken"),
        disallowed_behavior=("ranking", "cross_endpoint_aggregation"),
    )

    metadata = boundary.to_metadata()

    assert metadata["boundaryKind"] == "lightly_reshaped"
    assert metadata["allowedWrapperFields"] == ["endpoint", "quotaCost"]
    assert metadata["preservedUpstreamFields"] == ["items", "nextPageToken"]
    assert metadata["disallowedBehavior"] == ["ranking", "cross_endpoint_aggregation"]


def test_response_boundary_rejects_empty_out_of_scope_explanation():
    """Require out-of-scope examples to document disallowed behavior."""
    with pytest.raises(Layer2ContractError):
        ResponseBoundary(boundary_kind=ResponseBoundaryKind.OUT_OF_SCOPE).to_metadata()


def test_error_categories_cover_shared_layer2_failures():
    """Keep shared error categories stable for endpoint-backed tools."""
    assert {category.value for category in ErrorCategory} == {
        "authentication_failed",
        "authorization_failed",
        "quota_exhausted",
        "resource_not_found",
        "invalid_request",
        "deprecated_endpoint",
        "endpoint_unavailable",
        "upstream_failure",
    }


def test_sanitize_error_details_removes_secret_bearing_fields():
    """Strip unsafe diagnostic fields from caller-facing error details."""
    safe = sanitize_error_details(
        {
            "toolName": "videos_list",
            "api_key": "secret",
            "oauthToken": "secret",
            "stackTrace": "traceback",
            "raw_media_payload": b"secret",
            "parameter": "part",
        }
    )

    assert safe == {"toolName": "videos_list", "parameter": "part"}


def test_validate_safe_public_metadata_rejects_secret_bearing_details():
    """Reject unsafe metadata before exposing it through discovery surfaces."""
    with pytest.raises(Layer2ContractError):
        validate_safe_public_metadata(
            {
                "name": "videos_list",
                "quotaCost": 1,
                "apiKey": "secret",
                "nested": {"stackTrace": "traceback"},
                "media": ["safe", {"signedUrl": "https://example.invalid/signed"}],
            }
        )

    safe = validate_safe_public_metadata(
        {
            "name": "videos_list",
            "quotaCost": 1,
            "upstream": {"resource": "videos", "method": "list"},
        }
    )

    assert safe["upstream"]["resource"] == "videos"


def test_shared_helper_boundary_keeps_endpoint_facts_in_resource_families():
    """Document which concerns are shared and which stay endpoint-specific."""
    assert "naming" in SHARED_LAYER2_HELPER_BOUNDARY["shared"]
    assert "auth_quota_metadata" in SHARED_LAYER2_HELPER_BOUNDARY["shared"]
    assert "upstream_execution" in SHARED_LAYER2_HELPER_BOUNDARY["endpoint_family"]
    assert "media_transfer" in SHARED_LAYER2_HELPER_BOUNDARY["endpoint_family"]
