"""Contract tests for the Layer 2 ``videoCategories_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.video_categories import (
    VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES,
    VIDEO_CATEGORIES_LIST_CAVEATS,
    VIDEO_CATEGORIES_LIST_DESCRIPTION,
    VIDEO_CATEGORIES_LIST_INPUT_SCHEMA,
    VIDEO_CATEGORIES_LIST_QUOTA_COST,
    VIDEO_CATEGORIES_LIST_TOOL_NAME,
    VIDEO_CATEGORIES_LIST_USAGE_NOTES,
    VideoCategoriesListToolError,
    build_video_categories_list_contract,
    build_video_categories_list_handler,
    build_video_categories_list_tool_descriptor,
    validate_video_categories_list_arguments,
)


class QuotaFailingWrapper:
    """Layer 1 wrapper double that returns a normalized quota failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a failure containing unsafe details that must not leak.

        :param _executor: Ignored fake executor.
        :param arguments: Caller arguments passed through the handler.
        :param auth_context: API-key auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for quota mapping.
        """
        raise NormalizedUpstreamError(
            message="quota exceeded",
            category="rate_limit",
            retryable=False,
            upstream_status=403,
            details={"api_key": "secret", "field": "quota", "stacktrace": "hidden"},
        )


def test_video_categories_list_exports_package_symbols():
    """Expose concrete package-level symbols for the public tool."""
    assert VIDEO_CATEGORIES_LIST_TOOL_NAME == "videoCategories_list"
    assert VIDEO_CATEGORIES_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEO_CATEGORIES_LIST_TOOL_NAME == "videoCategories_list"
    assert youtube_common.VIDEO_CATEGORIES_LIST_QUOTA_COST == 1
    assert callable(youtube_common.build_video_categories_list_contract)
    assert callable(youtube_common.build_video_categories_list_tool_descriptor)


def test_video_categories_list_input_contract_requires_part_and_one_selector():
    """Publish a strict schema for category lookup by region or category ID."""
    schema = VIDEO_CATEGORIES_LIST_INPUT_SCHEMA

    assert schema["required"] == ["part"]
    assert schema["properties"]["part"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["regionCode"] == {"type": "string", "minLength": 2, "maxLength": 2}
    assert schema["properties"]["id"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["hl"] == {"type": "string", "minLength": 1}
    assert schema["oneOf"] == [{"required": ["regionCode"]}, {"required": ["id"]}]
    assert schema["additionalProperties"] is False


def test_video_categories_list_contract_metadata_is_safe_and_complete():
    """Expose discoverable auth, quota, selector, localization, and boundary metadata."""
    contract = build_video_categories_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "videoCategories_list"
    assert metadata["resourceFamily"] == "video_categories"
    assert metadata["upstream"]["operationKey"] == "videoCategories.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["selectorFields"] == ["regionCode", "id"]
    assert metadata["responseConvention"]["localizationFields"] == ["hl"]
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "Quota cost: 1" in metadata_text
    assert "api_key" in metadata_text
    assert "part" in metadata_text
    assert "regionCode" in metadata_text
    assert "id" in metadata_text
    assert "hl" in metadata_text
    assert "empty" in metadata_text
    assert "video search" in metadata_text
    assert "recommendation" in metadata_text
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_video_categories_list_descriptor_carries_examples():
    """Expose representative success, empty, validation, access, and scope examples."""
    descriptor = build_video_categories_list_tool_descriptor()
    metadata = descriptor["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}

    assert descriptor["name"] == "videoCategories_list"
    assert descriptor["inputSchema"] == VIDEO_CATEGORIES_LIST_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert metadata["upstream"]["operationKey"] == "videoCategories.list"
    assert {
        "region_category_lookup",
        "category_id_lookup",
        "localized_category_lookup",
        "populated_success",
        "empty_success",
        "missing_part",
        "missing_selector",
        "conflicting_selectors",
        "invalid_hl",
        "access_failure",
        "quota_or_upstream_failure",
        "deprecated_endpoint",
        "endpoint_unavailable",
        "out_of_scope_category_analysis",
    }.issubset(example_names)


def test_video_categories_list_declares_expected_failure_categories():
    """Keep caller-visible failure categories stable and bounded."""
    contract = build_video_categories_list_contract()

    assert set(contract.error_categories) == {
        "invalid_request",
        "authentication_failed",
        "authorization_failed",
        "quota_exhausted",
        "resource_not_found",
        "endpoint_unavailable",
        "deprecated_endpoint",
        "upstream_failure",
    }


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"regionCode": "US"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "", "regionCode": "US"}, "part"),
        ({"part": "snippet", "regionCode": "U"}, "regionCode"),
        ({"part": "snippet", "id": ""}, "selector"),
        ({"part": "snippet", "regionCode": "US", "id": "10"}, "selector"),
        ({"part": "snippet", "regionCode": "US", "hl": "bad language"}, "hl"),
        ({"part": "snippet", "regionCode": "US", "q": "music"}, "q"),
    ],
)
def test_video_categories_list_validation_failures_are_safe(arguments, field):
    """Reject unsupported request shapes without leaking internal details."""
    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        validate_video_categories_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "apiKey" not in str(exc_info.value.details)


def test_video_categories_list_maps_quota_failures_without_secret_details():
    """Map upstream quota failures to a safe public category."""
    handler = build_video_categories_list_handler(wrapper=QuotaFailingWrapper(), api_key="visible-key")

    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        handler({"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "api_key" not in str(exc_info.value.details)


def test_video_categories_list_metadata_text_constants_are_public_safe():
    """Keep exported text constants useful for clients and safe for discovery."""
    combined = " ".join(
        [
            VIDEO_CATEGORIES_LIST_DESCRIPTION,
            *VIDEO_CATEGORIES_LIST_USAGE_NOTES,
            *VIDEO_CATEGORIES_LIST_CAVEATS,
            *(example["description"] for example in VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES),
        ]
    )

    assert "Quota cost: 1" in combined
    assert "videoCategories.list" in combined
    assert "regionCode" in combined
    assert "id" in combined
    assert "video search" in combined
    assert "recommendation" in combined
    assert "apiKey" not in combined
