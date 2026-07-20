"""Contract tests for the Layer 2 ``thumbnails_set`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.thumbnails import (
    THUMBNAILS_SET_CALLER_EXAMPLES,
    THUMBNAILS_SET_CAVEATS,
    THUMBNAILS_SET_DESCRIPTION,
    THUMBNAILS_SET_INPUT_SCHEMA,
    THUMBNAILS_SET_QUOTA_COST,
    THUMBNAILS_SET_TOOL_NAME,
    THUMBNAILS_SET_USAGE_NOTES,
    ThumbnailsSetToolError,
    build_thumbnails_set_contract,
    build_thumbnails_set_handler,
    build_thumbnails_set_tool_descriptor,
    validate_thumbnails_set_arguments,
)


def test_thumbnails_set_public_symbols_are_exported():
    """Expose ``thumbnails_set`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import thumbnails

    assert youtube_common.THUMBNAILS_SET_TOOL_NAME == "thumbnails_set"
    assert youtube_common.THUMBNAILS_SET_QUOTA_COST == 50
    assert THUMBNAILS_SET_TOOL_NAME == "thumbnails_set"
    assert THUMBNAILS_SET_QUOTA_COST == 50
    assert callable(thumbnails.build_thumbnails_set_tool_descriptor)


def test_thumbnails_set_schema_preserves_required_upload_inputs():
    """Expose the upstream-like request fields for ``thumbnails_set``."""
    properties = THUMBNAILS_SET_INPUT_SCHEMA["properties"]

    assert THUMBNAILS_SET_INPUT_SCHEMA["required"] == ["videoId", "media"]
    assert properties["videoId"] == {"type": "string", "minLength": 1}
    assert properties["media"]["type"] == "object"
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert properties["media"]["additionalProperties"] is False
    assert THUMBNAILS_SET_INPUT_SCHEMA["additionalProperties"] is False


def test_thumbnails_set_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and upload response metadata."""
    contract = build_thumbnails_set_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "thumbnails_set"
    assert metadata["upstream"]["operationKey"] == "thumbnails.set"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["videoId", "media"]
    assert {"videoId", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "upload_result"
    assert metadata["responseConvention"]["mediaResult"] == "safe_media_summary"
    assert "target" in metadata["responseBoundary"]["allowedWrapperFields"]
    assert "upload" in metadata["responseBoundary"]["allowedWrapperFields"]


def test_thumbnails_set_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_thumbnails_set_tool_descriptor()

    assert descriptor["name"] == "thumbnails_set"
    assert descriptor["inputSchema"] == THUMBNAILS_SET_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "thumbnails.set"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert callable(descriptor["handler"])


def test_thumbnails_set_metadata_documents_cost_oauth_upload_and_scope():
    """Expose quota, OAuth, upload, sparse-result, and out-of-scope guidance."""
    contract = build_thumbnails_set_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join(
        [
            THUMBNAILS_SET_DESCRIPTION,
            *THUMBNAILS_SET_USAGE_NOTES,
            *THUMBNAILS_SET_CAVEATS,
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "videoId" in metadata_text
    assert "media" in metadata_text
    assert "upload" in metadata_text
    assert "sparse" in metadata_text
    assert "target video" in metadata_text
    assert "thumbnail generation" in metadata_text
    assert "image editing" in metadata_text
    assert "video metadata" in metadata_text
    assert metadata["availabilityState"] == "active"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_thumbnails_set_examples_cover_success_and_failures():
    """Expose required caller examples for success and safe failure categories."""
    examples = {example["name"]: example for example in THUMBNAILS_SET_CALLER_EXAMPLES}

    assert {
        "oauth_thumbnail_set",
        "sparse_success",
        "missing_video_id",
        "missing_media",
        "invalid_video_id",
        "unsupported_upload",
        "access_failure",
        "target_video_or_quota_failure",
        "out_of_scope_thumbnail_management_request",
    }.issubset(examples)
    assert examples["oauth_thumbnail_set"]["quotaCost"] == 50
    assert examples["oauth_thumbnail_set"]["result"]["upload"]["contentProvided"] is True
    assert examples["missing_video_id"]["errorCategory"] == "invalid_request"
    assert examples["missing_media"]["errorCategory"] == "invalid_request"
    assert examples["unsupported_upload"]["errorCategory"] == "unsupported_upload"
    assert examples["access_failure"]["errorCategory"] == "authentication_failed"
    assert examples["target_video_or_quota_failure"]["errorCategory"] in {
        "target_video_failed",
        "quota_exhausted",
    }
    assert "fake-image-content" not in str(THUMBNAILS_SET_CALLER_EXAMPLES)


def test_thumbnails_set_contract_lists_safe_error_categories():
    """Document caller-facing error categories for thumbnail-setting failures."""
    metadata = build_thumbnails_set_contract().to_tool_metadata()

    assert {
        "invalid_request",
        "authentication_failed",
        "authorization_failed",
        "target_video_failed",
        "unsupported_upload",
        "upload_rejected",
        "quota_exhausted",
        "endpoint_unavailable",
        "deprecated_endpoint",
        "upstream_failure",
    }.issubset(set(metadata["errorCategories"]))


def test_thumbnails_set_handler_rejects_missing_video_id():
    """Reject requests missing required target identifiers through public validation."""
    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        validate_thumbnails_set_arguments({"media": {"mimeType": "image/png", "content": "fake-image-content"}})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "videoId"}


def test_thumbnails_set_handler_maps_upstream_target_failures():
    """Map normalized target-video failures to safe public categories."""

    class FailingWrapper:
        """Raise a target-video failure from a contract-test handler."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized target-video failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="Target video cannot accept thumbnail update",
                category="target_video",
                retryable=False,
                upstream_status=404,
                details={"videoId": arguments["videoId"], "oauth_token": "secret"},
            )

    handler = build_thumbnails_set_handler(wrapper=FailingWrapper(), executor=object(), oauth_token="token")

    with pytest.raises(ThumbnailsSetToolError) as exc_info:
        handler({"videoId": "video-123", "media": {"mimeType": "image/png", "content": "fake-image-content"}})

    assert exc_info.value.category == "target_video_failed"
    assert exc_info.value.details == {"videoId": "video-123"}
