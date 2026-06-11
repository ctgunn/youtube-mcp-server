"""Contract tests for the concrete Layer 2 ``channelSections_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.channel_sections import (
    CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES,
    CHANNEL_SECTIONS_LIST_TOOL_NAME,
    ChannelSectionsListToolError,
    build_channel_sections_list_contract,
    build_channel_sections_list_tool_descriptor,
)


def test_concrete_channel_sections_module_exports_public_tool_contract():
    """Require the concrete channel-sections Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import channel_sections

    assert channel_sections.CHANNEL_SECTIONS_LIST_TOOL_NAME == "channelSections_list"
    assert youtube_common.CHANNEL_SECTIONS_LIST_TOOL_NAME == "channelSections_list"
    assert callable(channel_sections.build_channel_sections_list_tool_descriptor)


def test_channel_sections_list_contract_exposes_identity_quota_and_result_boundary():
    """Expose the public metadata required before invocation."""
    contract = build_channel_sections_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CHANNEL_SECTIONS_LIST_TOOL_NAME
    assert contract.upstream_resource == "channelSections"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "channelSections.list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_channel_sections_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_channel_sections_list_tool_descriptor()

    assert descriptor["name"] == "channelSections_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "channelSections.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {"channelId", "id", "mine"}.issubset(descriptor["inputSchema"]["properties"])
    assert callable(descriptor["handler"])


def test_channel_sections_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw channel-section fields."""
    result = build_channel_sections_list_tool_descriptor()["handler"]({"part": "snippet", "channelId": "UC123"})

    assert result["endpoint"] == "channelSections.list"
    assert result["quotaCost"] == 1
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "channelId"}


def test_channel_sections_list_metadata_documents_access_cost_caveats_and_boundaries():
    """Expose caller-facing metadata needed before ``channelSections_list`` calls."""
    descriptor = build_channel_sections_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert {"channelId", "id", "mine", "hl", "onBehalfOfContentOwner"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["pagingFields"] == ["nextPageToken", "prevPageToken", "pageInfo"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "OAuth" in metadata_text
    assert "deprecated" in metadata_text
    assert "content partners" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "Pagination" in metadata_text
    assert "mutate channel sections" in metadata_text


def test_channel_sections_list_caller_examples_cover_supported_and_rejected_paths():
    """Document supported selectors, caveats, auth failures, and workflow boundaries."""
    examples = {example["name"]: example for example in CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES}

    assert {
        "channel_id_lookup",
        "section_id_lookup",
        "authorized_mine_lookup",
        "empty_result",
        "deprecated_hl_caveat",
        "content_owner_partner_caveat",
        "missing_selector",
        "conflicting_selectors",
        "authorization_sensitive_failure",
        "unsupported_higher_level_workflow",
    }.issubset(examples)
    assert examples["channel_id_lookup"]["arguments"]["channelId"] == "UC123"
    assert examples["section_id_lookup"]["arguments"]["id"] == "section-123"
    assert examples["authorized_mine_lookup"]["arguments"]["mine"] is True
    assert examples["deprecated_hl_caveat"]["result"]["caveats"]["hlDeprecated"] is True
    assert examples["content_owner_partner_caveat"]["error"]["field"] == "onBehalfOfContentOwner"
    assert examples["unsupported_higher_level_workflow"]["error"]["field"] == "expandVideos"


def test_channel_sections_list_contract_errors_do_not_leak_sensitive_context():
    """Keep public errors free of credentials, stack traces, and private owner data."""

    class FailingWrapper:
        """Raise an upstream error with intentionally unsafe details."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the unsafe upstream error.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this contract check.
            """
            raise NormalizedUpstreamError(
                message="private channel oauth-token cms-account Traceback (most recent call last)",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"secret": "oauth-token", "cmsAccount": "cms-account"},
            )

    descriptor = build_channel_sections_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(ChannelSectionsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "channelId": "UC123"})

    error_text = f"{exc_info.value} {exc_info.value.details}"
    assert exc_info.value.category == "authorization_failed"
    assert "oauth-token" not in error_text
    assert "cms-account" not in error_text
    assert "Traceback" not in error_text
    assert "private channel" not in error_text
