"""Contract tests for the Layer 2 ``watermarks`` tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.watermarks import (
    WATERMARKS_SET_CALLER_EXAMPLES,
    WATERMARKS_SET_CAVEATS,
    WATERMARKS_SET_DESCRIPTION,
    WATERMARKS_SET_INPUT_SCHEMA,
    WATERMARKS_SET_QUOTA_COST,
    WATERMARKS_SET_TOOL_NAME,
    WATERMARKS_SET_USAGE_NOTES,
    WatermarksSetToolError,
    build_watermarks_set_contract,
    build_watermarks_set_handler,
    build_watermarks_set_tool_descriptor,
    validate_watermarks_set_arguments,
    WATERMARKS_UNSET_CALLER_EXAMPLES,
    WATERMARKS_UNSET_CAVEATS,
    WATERMARKS_UNSET_DESCRIPTION,
    WATERMARKS_UNSET_INPUT_SCHEMA,
    WATERMARKS_UNSET_QUOTA_COST,
    WATERMARKS_UNSET_TOOL_NAME,
    WATERMARKS_UNSET_USAGE_NOTES,
    WatermarksUnsetToolError,
    build_watermarks_unset_contract,
    build_watermarks_unset_handler,
    build_watermarks_unset_tool_descriptor,
    validate_watermarks_unset_arguments,
)


def test_watermarks_set_public_symbols_are_exported():
    """Expose ``watermarks_set`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import watermarks

    assert youtube_common.WATERMARKS_SET_TOOL_NAME == "watermarks_set"
    assert youtube_common.WATERMARKS_SET_QUOTA_COST == 50
    assert WATERMARKS_SET_TOOL_NAME == "watermarks_set"
    assert WATERMARKS_SET_QUOTA_COST == 50
    assert callable(watermarks.build_watermarks_set_tool_descriptor)


def test_watermarks_set_schema_preserves_required_upload_inputs():
    """Expose the upstream-like request fields for ``watermarks_set``."""
    properties = WATERMARKS_SET_INPUT_SCHEMA["properties"]

    assert WATERMARKS_SET_INPUT_SCHEMA["required"] == ["channelId", "body", "media"]
    assert properties["channelId"] == {"type": "string", "minLength": 1}
    assert properties["body"]["type"] == "object"
    assert properties["body"]["required"] == ["timing", "position"]
    assert properties["media"]["type"] == "object"
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert properties["media"]["additionalProperties"] is False
    assert WATERMARKS_SET_INPUT_SCHEMA["additionalProperties"] is False


def test_watermarks_set_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and upload response metadata."""
    contract = build_watermarks_set_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.OWNER_ONLY
    assert metadata["name"] == "watermarks_set"
    assert metadata["upstream"]["operationKey"] == "watermarks.set"
    assert metadata["resourceFamily"] == "watermarks"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "owner_only"
    assert metadata["inputContract"]["required"] == ["channelId", "body", "media"]
    assert {"channelId", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "upload_mutation_acknowledgment"
    assert metadata["responseConvention"]["mediaResult"] == "safe_media_summary"
    assert "target" in metadata["responseBoundary"]["allowedWrapperFields"]
    assert "upload" in metadata["responseBoundary"]["allowedWrapperFields"]


def test_watermarks_set_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_watermarks_set_tool_descriptor()

    assert descriptor["name"] == "watermarks_set"
    assert descriptor["inputSchema"] == WATERMARKS_SET_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "watermarks.set"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert callable(descriptor["handler"])


def test_watermarks_set_metadata_documents_cost_oauth_upload_and_scope():
    """Expose quota, OAuth, upload, sparse-result, and out-of-scope guidance."""
    contract = build_watermarks_set_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join(
        [
            WATERMARKS_SET_DESCRIPTION,
            *WATERMARKS_SET_USAGE_NOTES,
            *WATERMARKS_SET_CAVEATS,
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "channelId" in metadata_text
    assert "body" in metadata_text
    assert "media" in metadata_text
    assert "image/jpeg" in metadata_text
    assert "image/png" in metadata_text
    assert "10 MB" in metadata_text
    assert "sparse" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "watermarks.unset" in metadata_text
    assert "thumbnail" in metadata_text
    assert "analytics" in metadata_text
    assert metadata["availabilityState"] == "owner_only"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_watermarks_set_examples_cover_success_and_failures():
    """Expose required caller examples for success and safe failure categories."""
    examples = {example["name"]: example for example in WATERMARKS_SET_CALLER_EXAMPLES}

    assert {
        "oauth_watermark_set",
        "sparse_success",
        "missing_channel_id",
        "invalid_channel_id",
        "missing_body",
        "unsupported_metadata",
        "missing_media",
        "unsupported_upload",
        "rejected_partner_delegation",
        "access_failure",
        "authorization_or_policy_failure",
        "target_channel_or_quota_failure",
        "endpoint_unavailable_or_deprecated",
        "conflict_or_upstream_refusal",
        "out_of_scope_watermark_workflow_request",
    }.issubset(examples)
    assert examples["oauth_watermark_set"]["quotaCost"] == 50
    assert examples["oauth_watermark_set"]["result"]["upload"]["contentProvided"] is True
    assert examples["missing_channel_id"]["errorCategory"] == "invalid_request"
    assert examples["missing_media"]["errorCategory"] == "invalid_request"
    assert examples["unsupported_upload"]["errorCategory"] == "unsupported_upload"
    assert examples["rejected_partner_delegation"]["errorCategory"] == "invalid_request"
    assert examples["access_failure"]["errorCategory"] == "authentication_failed"
    assert examples["conflict_or_upstream_refusal"]["errorCategory"] in {"conflict", "upstream_refused"}
    assert "fake-watermark-content" not in str(WATERMARKS_SET_CALLER_EXAMPLES)


def test_watermarks_set_contract_lists_safe_error_categories():
    """Document caller-facing error categories for watermark-setting failures."""
    metadata = build_watermarks_set_contract().to_tool_metadata()

    assert {
        "invalid_request",
        "authentication_failed",
        "authorization_failed",
        "target_channel_failed",
        "unsupported_upload",
        "upload_rejected",
        "quota_exhausted",
        "endpoint_unavailable",
        "deprecated_endpoint",
        "conflict",
        "upstream_refused",
        "upstream_failure",
    }.issubset(set(metadata["errorCategories"]))


def test_watermarks_set_handler_rejects_missing_channel_id():
    """Reject requests missing required target identifiers through public validation."""
    with pytest.raises(WatermarksSetToolError) as exc_info:
        validate_watermarks_set_arguments(
            {
                "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
                "media": {"mimeType": "image/png", "content": "fake-watermark-content"},
            }
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "channelId"}


def test_watermarks_set_handler_maps_upstream_channel_failures():
    """Map normalized target-channel failures to safe public categories."""

    class FailingWrapper:
        """Raise a target-channel failure from a contract-test handler."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized target-channel failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="Target channel cannot accept watermark update",
                category="target_channel",
                retryable=False,
                upstream_status=404,
                details={"channelId": arguments["channelId"], "oauth_token": "secret"},
            )

    handler = build_watermarks_set_handler(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(WatermarksSetToolError) as exc_info:
        handler(
            {
                "channelId": "UC123",
                "body": {"timing": {"type": "offsetFromStart"}, "position": {"type": "corner"}},
                "media": {"mimeType": "image/png", "content": "fake-watermark-content"},
            }
        )

    assert exc_info.value.category == "target_channel_failed"
    assert exc_info.value.details == {"channelId": "UC123"}


def test_configured_watermark_descriptors_preserve_safe_public_metadata():
    """Keep OAuth runtime injection out of watermark discovery metadata.

    :return: ``None`` after validating configured watermark descriptors.
    """
    descriptors = (
        build_watermarks_set_tool_descriptor(executor=object(), oauth_token="configured-oauth-token"),
        build_watermarks_unset_tool_descriptor(executor=object(), oauth_token="configured-oauth-token"),
    )

    assert [descriptor["name"] for descriptor in descriptors] == ["watermarks_set", "watermarks_unset"]
    assert all(descriptor["metadata"]["authMode"] == "oauth_required" for descriptor in descriptors)
    assert "configured-oauth-token" not in str(descriptors)


def test_watermarks_unset_public_symbols_are_exported():
    """Expose ``watermarks_unset`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import watermarks

    assert youtube_common.WATERMARKS_UNSET_TOOL_NAME == "watermarks_unset"
    assert youtube_common.WATERMARKS_UNSET_QUOTA_COST == 50
    assert WATERMARKS_UNSET_TOOL_NAME == "watermarks_unset"
    assert WATERMARKS_UNSET_QUOTA_COST == 50
    assert callable(watermarks.build_watermarks_unset_tool_descriptor)


def test_watermarks_unset_schema_accepts_only_channel_id():
    """Expose only the owner channel target for ``watermarks_unset``."""
    properties = WATERMARKS_UNSET_INPUT_SCHEMA["properties"]

    assert WATERMARKS_UNSET_INPUT_SCHEMA["required"] == ["channelId"]
    assert properties["channelId"] == {"type": "string", "minLength": 1}
    assert "body" not in properties
    assert "media" not in properties
    assert "onBehalfOfContentOwner" not in properties
    assert WATERMARKS_UNSET_INPUT_SCHEMA["additionalProperties"] is False


def test_watermarks_unset_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and removal metadata."""
    contract = build_watermarks_unset_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.OWNER_ONLY
    assert metadata["name"] == "watermarks_unset"
    assert metadata["upstream"]["operationKey"] == "watermarks.unset"
    assert metadata["resourceFamily"] == "watermarks"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "owner_only"
    assert metadata["inputContract"]["required"] == ["channelId"]
    assert set(metadata["inputContract"]["properties"]) == {"channelId"}
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert "target" in metadata["responseBoundary"]["allowedWrapperFields"]
    assert "acknowledgment" in metadata["responseBoundary"]["allowedWrapperFields"]
    assert "noUpload" in metadata["responseBoundary"]["allowedWrapperFields"]


def test_watermarks_unset_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public unset contract."""
    descriptor = build_watermarks_unset_tool_descriptor()

    assert descriptor["name"] == "watermarks_unset"
    assert descriptor["inputSchema"] == WATERMARKS_UNSET_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "watermarks.unset"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert callable(descriptor["handler"])


def test_watermarks_unset_metadata_documents_cost_oauth_removal_and_scope():
    """Expose quota, OAuth, no-upload, sparse-result, and out-of-scope guidance."""
    contract = build_watermarks_unset_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join(
        [
            WATERMARKS_UNSET_DESCRIPTION,
            *WATERMARKS_UNSET_USAGE_NOTES,
            *WATERMARKS_UNSET_CAVEATS,
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "channelId" in metadata_text
    assert "body" in metadata_text
    assert "media" in metadata_text
    assert "no upload" in metadata_text
    assert "sparse" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "watermarks.set" in metadata_text
    assert "thumbnail" in metadata_text
    assert "analytics" in metadata_text
    assert metadata["availabilityState"] == "owner_only"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_watermarks_unset_examples_cover_success_and_failures():
    """Expose required caller examples for removal success and safe failure categories."""
    examples = {example["name"]: example for example in WATERMARKS_UNSET_CALLER_EXAMPLES}

    assert {
        "oauth_watermark_unset",
        "sparse_success",
        "missing_channel_id",
        "invalid_channel_id",
        "unsupported_body",
        "unsupported_media",
        "rejected_partner_delegation",
        "access_failure",
        "authorization_or_policy_failure",
        "target_channel_or_quota_failure",
        "no_removal_possible",
        "endpoint_unavailable_or_deprecated",
        "conflict_or_upstream_refusal",
        "out_of_scope_watermark_workflow_request",
    }.issubset(examples)
    assert examples["oauth_watermark_unset"]["quotaCost"] == 50
    assert examples["oauth_watermark_unset"]["result"]["removed"] is True
    assert examples["oauth_watermark_unset"]["result"]["noUpload"]["mediaAccepted"] is False
    assert examples["missing_channel_id"]["errorCategory"] == "invalid_request"
    assert examples["unsupported_body"]["errorCategory"] == "invalid_request"
    assert examples["unsupported_media"]["errorCategory"] == "invalid_request"
    assert examples["no_removal_possible"]["errorCategory"] == "no_removal_possible"
    assert examples["rejected_partner_delegation"]["errorCategory"] == "invalid_request"
    assert examples["access_failure"]["errorCategory"] == "authentication_failed"
    assert examples["conflict_or_upstream_refusal"]["errorCategory"] in {"conflict", "upstream_refused"}
    assert "fake-watermark-content" not in str(WATERMARKS_UNSET_CALLER_EXAMPLES)


def test_watermarks_unset_contract_lists_safe_error_categories():
    """Document caller-facing error categories for watermark removal failures."""
    metadata = build_watermarks_unset_contract().to_tool_metadata()

    assert {
        "invalid_request",
        "authentication_failed",
        "authorization_failed",
        "target_channel_failed",
        "no_removal_possible",
        "quota_exhausted",
        "endpoint_unavailable",
        "deprecated_endpoint",
        "conflict",
        "upstream_refused",
        "upstream_failure",
    }.issubset(set(metadata["errorCategories"]))


def test_watermarks_unset_handler_rejects_missing_channel_id():
    """Reject requests missing required target identifiers through public validation."""
    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        validate_watermarks_unset_arguments({})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "channelId"}


def test_watermarks_unset_handler_maps_upstream_no_removal_failures():
    """Map normalized no-removal failures to a safe public category."""

    class FailingWrapper:
        """Raise a no-removal failure from a contract-test handler."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized no-removal failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="No watermark exists for removal",
                category="no_removal",
                retryable=False,
                upstream_status=404,
                details={"channelId": arguments["channelId"], "oauth_token": "secret"},
            )

    handler = build_watermarks_unset_handler(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(WatermarksUnsetToolError) as exc_info:
        handler({"channelId": "UC123"})

    assert exc_info.value.category == "no_removal_possible"
    assert exc_info.value.details == {"channelId": "UC123"}
