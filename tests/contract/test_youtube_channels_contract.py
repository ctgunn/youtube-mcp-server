"""Contract tests for the concrete Layer 2 ``channels_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.channels import (
    CHANNELS_LIST_CALLER_EXAMPLES,
    CHANNELS_LIST_TOOL_NAME,
    ChannelsListToolError,
    build_channels_list_contract,
    build_channels_list_tool_descriptor,
)


def test_concrete_channels_module_exports_public_tool_contract():
    """Require the concrete channels Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import channels

    assert channels.CHANNELS_LIST_TOOL_NAME == "channels_list"
    assert youtube_common.CHANNELS_LIST_TOOL_NAME == "channels_list"
    assert callable(channels.build_channels_list_tool_descriptor)


def test_channels_list_contract_exposes_identity_quota_and_result_boundary():
    """Expose the public metadata required before invocation."""
    contract = build_channels_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CHANNELS_LIST_TOOL_NAME
    assert contract.upstream_resource == "channels"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "channels.list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_channels_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_channels_list_tool_descriptor()

    assert descriptor["name"] == "channels_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "channels.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {"id", "mine", "forHandle", "forUsername"}.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_channels_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw channel collection fields."""
    result = build_channels_list_tool_descriptor()["handler"]({"part": "snippet", "id": "UC123"})

    assert result["endpoint"] == "channels.list"
    assert result["quotaCost"] == 1
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "id"}


def test_channels_list_metadata_exposes_selectors_auth_pagination_and_boundaries():
    """Expose selector, auth, pagination, and scope details before invocation."""
    metadata = build_channels_list_contract().to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["quotaCost"] == 1
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "mine", "forHandle", "forUsername"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert "nextPageToken" in metadata["responseConvention"]["pagingFields"]
    assert "prevPageToken" in metadata["responseConvention"]["pagingFields"]
    assert "pageInfo" in metadata["responseConvention"]["pagingFields"]
    assert "mine" in metadata_text
    assert "OAuth" in metadata_text
    assert "forHandle" in metadata_text
    assert "forUsername" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "search" in metadata_text.lower()
    assert "update" in metadata_text.lower()


def test_channels_list_caller_examples_cover_required_usage_shapes():
    """Expose safe examples for valid, paginated, empty, and invalid requests."""
    by_name = {example["name"]: example for example in CHANNELS_LIST_CALLER_EXAMPLES}

    assert {
        "id_lookup",
        "handle_lookup",
        "username_lookup",
        "authorized_mine_lookup",
        "paginated_continuation",
        "empty_result",
        "missing_selector",
        "conflicting_selectors",
        "authorization_sensitive_failure",
    }.issubset(by_name)
    assert by_name["id_lookup"]["arguments"]["id"] == "UC123"
    assert by_name["handle_lookup"]["arguments"]["forHandle"] == "@Example"
    assert by_name["username_lookup"]["arguments"]["forUsername"] == "legacy-user"
    assert by_name["authorization_sensitive_failure"]["error"]["category"] == "authentication_failed"


@pytest.mark.parametrize(
    ("arguments", "category"),
    [
        ({"part": "snippet"}, "invalid_request"),
        ({"part": "snippet", "id": "UC123", "mine": True}, "invalid_request"),
        ({"part": "snippet", "mine": True}, "authentication_failed"),
    ],
)
def test_channels_list_contract_returns_safe_error_categories(arguments, category):
    """Expose safe error categories without leaking private execution details."""
    descriptor = build_channels_list_tool_descriptor(api_key="public-key", oauth_token=None)

    with pytest.raises(ChannelsListToolError) as exc_info:
        descriptor["handler"](arguments)

    error = exc_info.value
    error_text = f"{error} {error.details}"
    assert error.category == category
    assert "public-key" not in error_text
    assert "oauth" not in error_text.lower()
    assert "Traceback" not in error_text
    assert "privateChannel" not in error_text


@pytest.mark.parametrize(
    ("upstream_category", "status", "safe_category"),
    [
        ("auth", 403, "authorization_failed"),
        ("not_found", 404, "resource_not_found"),
        ("rate_limit", 429, "quota_exhausted"),
        ("transient", 503, "endpoint_unavailable"),
        ("upstream_service", 500, "upstream_failure"),
    ],
)
def test_channels_list_contract_maps_upstream_errors_safely(upstream_category, status, safe_category):
    """Normalize Layer 1 failures into caller-safe ``channels_list`` categories."""

    class FailingWrapper:
        """Raise one normalized upstream error for contract validation."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured normalized upstream error.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always for this test.
            """
            raise NormalizedUpstreamError(
                "safe upstream failure",
                category=upstream_category,
                retryable=False,
                upstream_status=status,
                details={"privateChannelData": "hidden"},
            )

    descriptor = build_channels_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(ChannelsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "id": "UC123"})

    assert exc_info.value.category == safe_category
    assert exc_info.value.details == {"upstreamStatus": status}
    assert "privateChannelData" not in str(exc_info.value.details)
