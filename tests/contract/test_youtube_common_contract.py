"""Contract tests for shared YouTube tool contracts."""

import pytest

from mcp_server.tools.youtube_common import (
    AuthMode,
    ErrorCategory,
    YouTubeToolContractError,
    YouTubeToolContract,
    SHARED_YOUTUBE_HELPER_BOUNDARY,
    ResponseConvention,
    ResponseKind,
    sanitize_error_details,
)


def test_youtube_tool_contract_requires_public_metadata():
    """Require every representative contract to expose MCP-facing metadata."""
    contract = YouTubeToolContract(
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
        error_categories=("invalid_request", "quota_exhausted"),
    )

    metadata = contract.to_tool_metadata()

    assert metadata["name"] == "videos_list"
    assert metadata["upstream"]["resource"] == "videos"
    assert metadata["upstream"]["method"] == "list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
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
        ("error_categories", ()),
    ],
)
def test_youtube_tool_contract_rejects_missing_required_metadata(field, value):
    """Reject contracts that omit required shared YouTube metadata."""
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
        "error_categories": ("invalid_request",),
    }
    kwargs[field] = value

    with pytest.raises(YouTubeToolContractError):
        YouTubeToolContract(**kwargs)


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


def test_error_categories_cover_shared_youtube_failures():
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


def test_shared_helper_boundary_keeps_endpoint_facts_in_resource_families():
    """Document which concerns are shared and which stay endpoint-specific."""
    assert "naming" in SHARED_YOUTUBE_HELPER_BOUNDARY["shared"]
    assert "auth_quota_metadata" in SHARED_YOUTUBE_HELPER_BOUNDARY["shared"]
    assert "upstream_execution" in SHARED_YOUTUBE_HELPER_BOUNDARY["endpoint_family"]
    assert "media_transfer" in SHARED_YOUTUBE_HELPER_BOUNDARY["endpoint_family"]
