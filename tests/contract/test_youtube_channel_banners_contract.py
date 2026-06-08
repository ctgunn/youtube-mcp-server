"""Contract tests for the concrete Layer 2 ``channelBanners_insert`` tool."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.channel_banners import (
    CHANNEL_BANNERS_INSERT_CALLER_EXAMPLES,
    CHANNEL_BANNERS_INSERT_INPUT_SCHEMA,
    CHANNEL_BANNERS_INSERT_QUOTA_COST,
    CHANNEL_BANNERS_INSERT_TOOL_NAME,
    ChannelBannersInsertToolError,
    build_channel_banners_insert_contract,
    build_channel_banners_insert_handler,
    build_channel_banners_insert_tool_descriptor,
    validate_channel_banners_insert_arguments,
)


def _valid_channel_banners_insert_arguments() -> dict:
    """Return a representative valid ``channelBanners_insert`` request."""
    return {
        "media": {
            "mimeType": "image/png",
            "content": "safe image content",
            "filename": "banner.png",
            "sizeBytes": 2048,
        }
    }


def test_concrete_channel_banners_module_exports_public_tool_contract():
    """Require the concrete channel banners Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import channel_banners

    assert channel_banners.CHANNEL_BANNERS_INSERT_TOOL_NAME == "channelBanners_insert"
    assert youtube_common.CHANNEL_BANNERS_INSERT_TOOL_NAME == "channelBanners_insert"
    assert callable(channel_banners.build_channel_banners_insert_tool_descriptor)


def test_channel_banners_insert_contract_exposes_identity_quota_auth_and_upload():
    """Expose the public metadata required before channel banner upload."""
    contract = build_channel_banners_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CHANNEL_BANNERS_INSERT_TOOL_NAME
    assert contract.upstream_resource == "channelBanners"
    assert contract.upstream_method == "insert"
    assert contract.quota_cost == CHANNEL_BANNERS_INSERT_QUOTA_COST == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.MEDIA_CONSTRAINED
    assert metadata["upstream"]["operationKey"] == "channelBanners.insert"
    assert metadata["inputContract"]["required"] == ["media"]
    assert "media" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "upload_result"
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_channel_banners_insert_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public upload contract."""
    descriptor = build_channel_banners_insert_tool_descriptor()

    assert descriptor["name"] == "channelBanners_insert"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "channelBanners.insert"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"] == CHANNEL_BANNERS_INSERT_INPUT_SCHEMA
    assert descriptor["inputSchema"]["required"] == ["media"]
    assert callable(descriptor["handler"])


def test_channel_banners_insert_handler_returns_upload_result_shape():
    """Execute the default handler and preserve the returned banner resource."""
    descriptor = build_channel_banners_insert_tool_descriptor()

    result = descriptor["handler"](_valid_channel_banners_insert_arguments())

    assert result["endpoint"] == "channelBanners.insert"
    assert result["quotaCost"] == 50
    assert result["item"]["url"]
    assert result["media"] == {
        "mimeType": "image/png",
        "filename": "banner.png",
        "sizeBytes": 2048,
        "contentProvided": True,
    }
    assert "content" not in result["media"]
    assert "active" not in result


def test_channel_banners_insert_metadata_documents_upload_rules_and_boundaries():
    """Expose upload constraints and activation boundaries in caller metadata."""
    metadata = build_channel_banners_insert_contract().to_tool_metadata()
    metadata_text = " ".join(
        [
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            str(metadata["responseConvention"]),
            str(metadata["responseBoundary"]),
        ]
    )

    assert metadata["responseConvention"]["returnedUrlField"] == "url"
    assert metadata["responseConvention"]["activationBoundary"] == "channels.update"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "channelBanners.insert" in metadata_text
    assert "Quota cost: 50" in metadata_text
    assert "oauth_required" in metadata_text
    assert "media" in metadata_text
    assert "image/jpeg" in metadata_text
    assert "image/png" in metadata_text
    assert "application/octet-stream" in metadata_text
    assert "6 MB" in metadata_text
    assert "16:9" in metadata_text
    assert "2048x1152" in metadata_text
    assert "2560x1440" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "no JSON" in metadata_text
    assert "returned URL" in metadata_text
    assert "channels.update" in metadata_text
    assert "active_banner_publication" in metadata["responseBoundary"]["disallowedBehavior"]


def test_channel_banners_insert_exposes_safe_caller_examples():
    """Expose representative caller examples without raw media or secrets."""
    examples = {example["name"]: example for example in CHANNEL_BANNERS_INSERT_CALLER_EXAMPLES}

    assert {
        "authorized_upload",
        "delegated_upload",
        "missing_media",
        "invalid_media",
        "unsupported_channel_update",
        "authorization_sensitive_failure",
        "returned_url_boundary",
    }.issubset(examples)
    assert examples["authorized_upload"]["arguments"]["media"]["content"] == "<binary image content omitted>"
    assert examples["returned_url_boundary"]["result"]["url"]
    assert "channels.update" in examples["returned_url_boundary"]["notes"]
    assert "oauth" not in str(examples).lower()
    assert "token" not in str(examples).lower()


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "media"),
        ({"media": {"content": "image"}}, "media.mimeType"),
        ({"media": {"mimeType": "image/png"}}, "media.content"),
        ({"media": {"mimeType": "image/gif", "content": "image"}}, "media.mimeType"),
        ({"media": {"mimeType": "image/png", "content": "image", "sizeBytes": 6 * 1024 * 1024 + 1}}, "media.sizeBytes"),
        ({**_valid_channel_banners_insert_arguments(), "body": {}}, "body"),
        ({**_valid_channel_banners_insert_arguments(), "crop": "center"}, "crop"),
        ({"media": {"mimeType": "image/png", "content": "image", "resize": "2560x1440"}}, "media.resize"),
    ],
)
def test_channel_banners_insert_rejects_invalid_upload_requests(arguments, field):
    """Reject unsupported channel banner upload requests with safe details."""
    with pytest.raises(ChannelBannersInsertToolError) as context:
        validate_channel_banners_insert_arguments(arguments, oauth_token="eligible")

    assert context.value.category == "invalid_request"
    assert context.value.details["field"] == field
    assert "content" not in context.value.details


@pytest.mark.parametrize(
    ("error", "expected_category"),
    [
        (
            NormalizedUpstreamError(
                "Upstream rejected the upload",
                category="upstream_service",
                retryable=False,
                upstream_status=400,
                details={"reason": "mediaBodyRequired"},
            ),
            "invalid_request",
        ),
        (
            NormalizedUpstreamError(
                "Banner album is full",
                category="upstream_service",
                retryable=False,
                upstream_status=400,
                details={"reason": "bannerAlbumFull"},
            ),
            "invalid_request",
        ),
        (
            NormalizedUpstreamError(
                "Forbidden channel branding operation",
                category="upstream_service",
                retryable=False,
                upstream_status=403,
                details={"reason": "forbidden"},
            ),
            "authorization_failed",
        ),
        (
            NormalizedUpstreamError(
                "Quota exceeded",
                category="rate_limit",
                retryable=True,
                upstream_status=429,
                details={"reason": "quotaExceeded"},
            ),
            "quota_exhausted",
        ),
        (
            NormalizedUpstreamError(
                "Temporary service unavailable",
                category="transient",
                retryable=True,
                upstream_status=503,
                details={"reason": "backendError"},
            ),
            "endpoint_unavailable",
        ),
        (
            NormalizedUpstreamError(
                "Invalid channel banner request",
                category="invalid_request",
                retryable=False,
                upstream_status=400,
                details={"reason": "invalidRequest"},
            ),
            "invalid_request",
        ),
        (
            NormalizedUpstreamError(
                "Unexpected upstream failure",
                category="upstream_service",
                retryable=False,
                upstream_status=500,
                details={"reason": "unknown"},
            ),
            "upstream_failure",
        ),
    ],
)
def test_channel_banners_insert_maps_upstream_failures_to_safe_categories(error, expected_category):
    """Map upstream channel banner failures to safe public error categories."""

    class FailingWrapper:
        """Raise a supplied upstream error for handler mapping tests."""

        def __init__(self, failure: NormalizedUpstreamError) -> None:
            """Store the failure raised by the fake wrapper.

            :param failure: Normalized upstream failure to raise.
            """
            self.failure = failure

        def call(self, _executor, *, arguments, auth_context):
            """Raise the configured failure during wrapper execution.

            :param _executor: Executor argument supplied by the handler.
            :param arguments: Tool arguments supplied by the handler.
            :param auth_context: Auth context supplied by the handler.
            :raises NormalizedUpstreamError: Always raises the configured failure.
            """
            raise self.failure

    handler = build_channel_banners_insert_handler(wrapper=FailingWrapper(error))

    with pytest.raises(ChannelBannersInsertToolError) as context:
        handler(_valid_channel_banners_insert_arguments())

    assert context.value.category == expected_category
    assert context.value.details.get("upstreamStatus") == error.upstream_status
    assert "token" not in str(context.value.details).lower()
    assert "raw" not in str(context.value.details).lower()
