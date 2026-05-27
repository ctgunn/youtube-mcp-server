"""Contract tests for the concrete Layer 2 ``activities_list`` tool."""

import pytest

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.activities import (
    ACTIVITIES_LIST_TOOL_NAME,
    ActivitiesListToolError,
    build_activities_list_contract,
    build_activities_list_tool_descriptor,
    validate_activities_list_arguments,
)


def test_concrete_activities_module_exports_public_tool_contract():
    """Require the concrete activities Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import activities

    assert activities.ACTIVITIES_LIST_TOOL_NAME == "activities_list"
    assert youtube_common.ACTIVITIES_LIST_TOOL_NAME == "activities_list"
    assert callable(activities.build_activities_list_tool_descriptor)


def test_activities_list_contract_exposes_identity_quota_auth_and_caveat():
    """Expose the public metadata required before invocation."""
    contract = build_activities_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == ACTIVITIES_LIST_TOOL_NAME
    assert contract.upstream_resource == "activities"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "activities.list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("home" in caveat for caveat in metadata["caveats"])
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_activities_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_activities_list_tool_descriptor()

    assert descriptor["name"] == "activities_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "activities.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {"channelId", "mine", "home"}.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_activities_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw activity collection fields."""
    result = build_activities_list_tool_descriptor()["handler"]({"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "activities.list"
    assert result["quotaCost"] == 1
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "channelId"}


@pytest.mark.parametrize(
    "arguments",
    [
        {"part": "snippet"},
        {"part": "snippet", "channelId": "UC123", "mine": True},
        {"part": "snippet", "home": True},
    ],
)
def test_activities_list_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized requests."""
    with pytest.raises(ActivitiesListToolError) as exc_info:
        validate_activities_list_arguments(arguments)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details
