"""Contract tests for the Layer 2 ``videoAbuseReportReasons_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.video_abuse_report_reasons import (
    VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES,
    VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS,
    VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION,
    VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA,
    VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST,
    VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME,
    VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES,
    VideoAbuseReportReasonsListToolError,
    build_video_abuse_report_reasons_list_contract,
    build_video_abuse_report_reasons_list_handler,
    build_video_abuse_report_reasons_list_tool_descriptor,
    validate_video_abuse_report_reasons_list_arguments,
)


class QuotaFailingWrapper:
    """Layer 1 wrapper double that returns a normalized quota failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a failure containing unsafe details that must not leak."""
        raise NormalizedUpstreamError(
            message="quota exceeded",
            category="rate_limit",
            retryable=False,
            upstream_status=403,
            details={"api_key": "secret", "field": "quota", "stacktrace": "hidden"},
        )


def test_video_abuse_report_reasons_list_exports_package_symbols():
    """Expose concrete package-level symbols for the public tool."""
    assert VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME == "videoAbuseReportReasons_list"
    assert VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME == "videoAbuseReportReasons_list"
    assert youtube_common.VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST == 1
    assert callable(youtube_common.build_video_abuse_report_reasons_list_contract)
    assert callable(youtube_common.build_video_abuse_report_reasons_list_tool_descriptor)


def test_video_abuse_report_reasons_list_input_contract_requires_part_and_hl():
    """Publish a strict minimal schema for localized abuse-reason lookup."""
    schema = VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA

    assert schema["required"] == ["part", "hl"]
    assert schema["properties"]["part"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["hl"] == {"type": "string", "minLength": 1}
    assert schema["additionalProperties"] is False


def test_video_abuse_report_reasons_list_contract_metadata_is_safe_and_complete():
    """Expose discoverable auth, quota, localization, and boundary metadata."""
    contract = build_video_abuse_report_reasons_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "videoAbuseReportReasons_list"
    assert metadata["resourceFamily"] == "video_abuse_report_reasons"
    assert metadata["upstream"]["operationKey"] == "videoAbuseReportReasons.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["required"] == ["part", "hl"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["localizationFields"] == ["hl"]
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "Quota cost: 1" in metadata_text
    assert "api_key" in metadata_text
    assert "part" in metadata_text
    assert "hl" in metadata_text
    assert "localization" in metadata_text
    assert "empty" in metadata_text
    assert "report submission" in metadata_text
    assert "moderation" in metadata_text
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_video_abuse_report_reasons_list_descriptor_carries_examples():
    """Expose representative success, empty, validation, access, and scope examples."""
    descriptor = build_video_abuse_report_reasons_list_tool_descriptor()
    metadata = descriptor["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}

    assert descriptor["name"] == "videoAbuseReportReasons_list"
    assert descriptor["inputSchema"] == VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert metadata["upstream"]["operationKey"] == "videoAbuseReportReasons.list"
    assert {
        "localized_reason_lookup",
        "populated_success",
        "empty_success",
        "missing_part",
        "missing_hl",
        "invalid_part",
        "invalid_hl",
        "access_failure",
        "quota_or_upstream_failure",
        "deprecated_endpoint",
        "endpoint_unavailable",
        "out_of_scope_report_submission",
    }.issubset(example_names)


def test_video_abuse_report_reasons_list_declares_expected_failure_categories():
    """Keep caller-visible failure categories stable and bounded."""
    contract = build_video_abuse_report_reasons_list_contract()

    assert set(contract.error_categories) == {
        "invalid_request",
        "authentication_failed",
        "authorization_failed",
        "quota_exhausted",
        "endpoint_unavailable",
        "deprecated_endpoint",
        "upstream_failure",
    }


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"hl": "en"}, "part"),
        ({"part": "snippet"}, "hl"),
        ({"part": "", "hl": "en"}, "part"),
        ({"part": "snippet", "hl": ""}, "hl"),
        ({"part": "snippet", "hl": "bad language"}, "hl"),
        ({"part": "snippet", "hl": "en", "body": {"reasonId": "spam"}}, "body"),
    ],
)
def test_video_abuse_report_reasons_list_validation_failures_are_safe(arguments, field):
    """Reject unsupported request shapes without leaking internal details."""
    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        validate_video_abuse_report_reasons_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "apiKey" not in str(exc_info.value.details)


def test_video_abuse_report_reasons_list_maps_quota_failures_without_secret_details():
    """Map upstream quota failures to a safe public category."""
    handler = build_video_abuse_report_reasons_list_handler(wrapper=QuotaFailingWrapper(), api_key="visible-key")

    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        handler({"part": "snippet", "hl": "en"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "api_key" not in str(exc_info.value.details)


def test_video_abuse_report_reasons_list_metadata_text_constants_are_public_safe():
    """Keep exported text constants useful for clients and safe for discovery."""
    combined = " ".join(
        [
            VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION,
            *VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES,
            *VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS,
            *(example["description"] for example in VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES),
        ]
    )

    assert "Quota cost: 1" in combined
    assert "videoAbuseReportReasons.list" in combined
    assert "report submission" in combined
    assert "moderation" in combined
    assert "apiKey" not in combined
