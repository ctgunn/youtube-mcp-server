"""Contract tests for the concrete Layer 2 ``captions_list`` tool."""

import pytest

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.captions import (
    CAPTIONS_LIST_TOOL_NAME,
    CaptionsListToolError,
    build_captions_list_contract,
    build_captions_list_tool_descriptor,
    validate_captions_list_arguments,
)


def test_concrete_captions_module_exports_public_tool_contract():
    """Require the concrete captions Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import captions

    assert captions.CAPTIONS_LIST_TOOL_NAME == "captions_list"
    assert youtube_common.CAPTIONS_LIST_TOOL_NAME == "captions_list"
    assert callable(captions.build_captions_list_tool_descriptor)


def test_captions_list_contract_exposes_identity_quota_auth_and_delegation():
    """Expose the public metadata required before invocation."""
    contract = build_captions_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CAPTIONS_LIST_TOOL_NAME
    assert contract.upstream_resource == "captions"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "captions.list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert metadata["inputContract"]["required"] == ["part", "videoId"]
    assert "id" in metadata["inputContract"]["properties"]
    assert any("onBehalfOfContentOwner" in note for note in metadata["usageNotes"])
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_captions_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_captions_list_tool_descriptor()

    assert descriptor["name"] == "captions_list"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "captions.list"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"]["required"] == ["part", "videoId"]
    assert {"part", "videoId", "id", "pageToken", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_captions_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw caption collection fields."""
    result = build_captions_list_tool_descriptor()["handler"]({"part": "snippet", "videoId": "video-123"})

    assert result["endpoint"] == "captions.list"
    assert result["quotaCost"] == 50
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["lookup"] == {"videoId": "video-123"}


@pytest.mark.parametrize(
    "arguments",
    [
        {"videoId": "video-123"},
        {"part": "snippet"},
        {"part": "snippet", "id": "caption-1"},
        {"part": "snippet", "videoId": "video-123", "maxResults": 51},
        {"part": "snippet", "videoId": "video-123", "onBehalfOfContentOwner": "owner"},
    ],
)
def test_captions_list_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized requests."""
    with pytest.raises(CaptionsListToolError) as exc_info:
        validate_captions_list_arguments(arguments, oauth_token=None)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details
