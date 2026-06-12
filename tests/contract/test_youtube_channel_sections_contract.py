"""Contract tests for the concrete Layer 2 ``channelSections_list`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.channel_sections import (
    CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES,
    CHANNEL_SECTIONS_INSERT_TOOL_NAME,
    CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES,
    CHANNEL_SECTIONS_LIST_TOOL_NAME,
    ChannelSectionsInsertToolError,
    ChannelSectionsListToolError,
    build_channel_sections_insert_contract,
    build_channel_sections_insert_tool_descriptor,
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


def test_channel_sections_insert_contract_exposes_identity_oauth_schema_and_boundary():
    """Expose the public metadata required before creating channel sections."""
    contract = build_channel_sections_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CHANNEL_SECTIONS_INSERT_TOOL_NAME
    assert contract.upstream_resource == "channelSections"
    assert contract.upstream_method == "insert"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "channelSections.insert"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body", "onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "requestedParts" in metadata["responseBoundary"]["preservedUpstreamFields"]


def test_channel_sections_insert_descriptor_returns_created_resource_shape():
    """Build an executable insert descriptor that preserves the created resource."""
    descriptor = build_channel_sections_insert_tool_descriptor()
    body = {
        "snippet": {"type": "singlePlaylist", "channelId": "UC123", "title": "Uploads"},
        "contentDetails": {"playlists": ["PL123"]},
    }

    result = descriptor["handler"]({"part": "snippet,contentDetails", "body": body})

    assert descriptor["name"] == "channelSections_insert"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert result["endpoint"] == "channelSections.insert"
    assert result["quotaCost"] == 50
    assert result["created"] is True
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["item"]["kind"] == "youtube#channelSection"
    assert result["item"]["snippet"] == body["snippet"]
    assert result["item"]["contentDetails"] == body["contentDetails"]


def test_channel_sections_insert_descriptor_requires_oauth_for_execution():
    """Keep creation behind OAuth-required authorization."""
    descriptor = build_channel_sections_insert_tool_descriptor(oauth_token=None)

    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        descriptor["handler"](
            {"part": "snippet", "body": {"snippet": {"type": "singlePlaylist", "channelId": "UC123"}}}
        )

    assert exc_info.value.category == "authentication_failed"


def test_channel_sections_insert_metadata_documents_cost_oauth_body_rules_and_boundaries():
    """Expose caller-facing metadata needed before ``channelSections_insert`` calls."""
    descriptor = build_channel_sections_insert_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["contentDetails", "id", "snippet"]
    assert "body" in metadata["inputContract"]["properties"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "onBehalfOfContentOwnerChannel" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["supportedWritableParts"] == ["contentDetails", "id", "snippet"]
    assert metadata["responseConvention"]["writableBodyFields"] == [
        "body.snippet.type",
        "body.snippet.channelId",
        "body.snippet.title",
        "body.snippet.position",
        "body.contentDetails.playlists[]",
        "body.contentDetails.channels[]",
    ]
    assert "snippet.type" in metadata_text
    assert "body.snippet.channelId" in metadata_text
    assert "singlePlaylist" in metadata_text
    assert "multiplePlaylists" in metadata_text
    assert "multipleChannels" in metadata_text
    assert "onBehalfOfContentOwnerChannel" in metadata_text
    assert "maximum" in metadata_text.lower()
    assert "playlistItems.list" in metadata_text
    assert "channels.update" in metadata_text


def test_channel_sections_insert_caller_examples_cover_supported_and_rejected_paths():
    """Document successful creation, partner context, validation, and boundaries."""
    examples = {example["name"]: example for example in CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES}

    assert {
        "authorized_playlist_section",
        "authorized_channel_section",
        "delegated_channel_section",
        "missing_oauth",
        "missing_section_type",
        "invalid_content_structure",
        "duplicate_references",
        "capacity_limit",
        "unsupported_higher_level_workflow",
    }.issubset(examples)
    assert examples["authorized_playlist_section"]["arguments"]["body"]["snippet"]["type"] == "singlePlaylist"
    assert examples["authorized_channel_section"]["arguments"]["body"]["snippet"]["type"] == "multipleChannels"
    assert examples["delegated_channel_section"]["result"]["partnerContext"] == {
        "onBehalfOfContentOwner": True,
        "onBehalfOfContentOwnerChannel": True,
    }
    assert examples["missing_oauth"]["error"]["category"] == "authentication_failed"
    assert examples["missing_section_type"]["error"]["field"] == "body.snippet.type"
    assert examples["unsupported_higher_level_workflow"]["error"]["field"] == "playlistItems"


def test_channel_sections_insert_contract_errors_do_not_leak_sensitive_context():
    """Keep public insert errors free of credentials, stack traces, and private owner data."""

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
                message="private channel oauth-token cms-account UC-secret Traceback (most recent call last)",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"secret": "oauth-token", "cmsAccount": "cms-account", "channel": "UC-secret"},
            )

    descriptor = build_channel_sections_insert_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(ChannelSectionsInsertToolError) as exc_info:
        descriptor["handler"](
            {
                "part": "snippet",
                "body": {
                    "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                    "contentDetails": {"playlists": ["PL123"]},
                },
                "onBehalfOfContentOwner": "cms-account",
                "onBehalfOfContentOwnerChannel": "UC-secret",
            }
        )

    error_text = f"{exc_info.value} {exc_info.value.details}"
    assert exc_info.value.category == "authorization_failed"
    assert "oauth-token" not in error_text
    assert "cms-account" not in error_text
    assert "UC-secret" not in error_text
    assert "Traceback" not in error_text
    assert "private channel" not in error_text
