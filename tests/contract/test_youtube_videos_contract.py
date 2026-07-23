"""Contract tests for Layer 2 ``videos`` tools."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.videos import (
    VIDEOS_GET_RATING_CALLER_EXAMPLES,
    VIDEOS_GET_RATING_CAVEATS,
    VIDEOS_GET_RATING_DESCRIPTION,
    VIDEOS_GET_RATING_INPUT_SCHEMA,
    VIDEOS_GET_RATING_QUOTA_COST,
    VIDEOS_GET_RATING_TOOL_NAME,
    VIDEOS_GET_RATING_USAGE_NOTES,
    VIDEOS_RATE_CALLER_EXAMPLES,
    VIDEOS_RATE_CAVEATS,
    VIDEOS_RATE_DESCRIPTION,
    VIDEOS_RATE_INPUT_SCHEMA,
    VIDEOS_RATE_QUOTA_COST,
    VIDEOS_RATE_TOOL_NAME,
    VIDEOS_RATE_USAGE_NOTES,
    VideosGetRatingToolError,
    VideosRateToolError,
    build_videos_get_rating_contract,
    build_videos_get_rating_handler,
    build_videos_get_rating_tool_descriptor,
    build_videos_rate_contract,
    build_videos_rate_handler,
    build_videos_rate_tool_descriptor,
    validate_videos_get_rating_arguments,
    validate_videos_rate_arguments,
    VIDEOS_UPDATE_CALLER_EXAMPLES,
    VIDEOS_UPDATE_CAVEATS,
    VIDEOS_UPDATE_DESCRIPTION,
    VIDEOS_UPDATE_INPUT_SCHEMA,
    VIDEOS_UPDATE_QUOTA_COST,
    VIDEOS_UPDATE_TOOL_NAME,
    VIDEOS_UPDATE_USAGE_NOTES,
    VideosUpdateToolError,
    build_videos_update_contract,
    build_videos_update_handler,
    build_videos_update_tool_descriptor,
    validate_videos_update_arguments,
    VIDEOS_LIST_CALLER_EXAMPLES,
    VIDEOS_LIST_CAVEATS,
    VIDEOS_LIST_DESCRIPTION,
    VIDEOS_LIST_INPUT_SCHEMA,
    VIDEOS_LIST_QUOTA_COST,
    VIDEOS_LIST_TOOL_NAME,
    VIDEOS_LIST_USAGE_NOTES,
    VideosListToolError,
    build_videos_list_contract,
    build_videos_list_handler,
    build_videos_list_tool_descriptor,
    validate_videos_list_arguments,
)


class QuotaFailingWrapper:
    """Layer 1 wrapper double that returns a normalized quota failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a failure containing unsafe details that must not leak.

        :param _executor: Ignored fake executor.
        :param arguments: Caller arguments passed through the handler.
        :param auth_context: Auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for quota mapping.
        """
        raise NormalizedUpstreamError(
            message="quota exceeded",
            category="rate_limit",
            retryable=False,
            upstream_status=403,
            details={"api_key": "secret", "oauth_token": "secret", "field": "quota", "stacktrace": "hidden"},
        )


def test_videos_list_exports_package_symbols():
    """Expose concrete package-level symbols for the public tool."""
    assert VIDEOS_LIST_TOOL_NAME == "videos_list"
    assert VIDEOS_LIST_QUOTA_COST == 1
    assert youtube_common.VIDEOS_LIST_TOOL_NAME == "videos_list"
    assert youtube_common.VIDEOS_LIST_QUOTA_COST == 1
    assert callable(youtube_common.build_videos_list_contract)
    assert callable(youtube_common.build_videos_list_tool_descriptor)


def test_videos_list_input_contract_requires_part_and_one_selector():
    """Publish a strict schema for direct, chart, or rating video lookups."""
    schema = VIDEOS_LIST_INPUT_SCHEMA

    assert schema["required"] == ["part"]
    assert schema["properties"]["part"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["id"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["chart"] == {"type": "string", "enum": ["mostPopular"]}
    assert schema["properties"]["myRating"] == {"type": "string", "enum": ["like", "dislike"]}
    assert schema["properties"]["pageToken"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["maxResults"] == {"type": "integer", "minimum": 1, "maximum": 50}
    assert schema["properties"]["regionCode"] == {"type": "string", "minLength": 2, "maxLength": 2}
    assert schema["properties"]["videoCategoryId"] == {"type": "string", "minLength": 1}
    assert schema["oneOf"] == [{"required": ["id"]}, {"required": ["chart"]}, {"required": ["myRating"]}]
    assert schema["additionalProperties"] is False


def test_videos_list_contract_metadata_is_safe_and_complete():
    """Expose auth, quota, selector, pagination, refinement, and boundary metadata."""
    contract = build_videos_list_contract()
    metadata = contract.to_tool_metadata()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "videos_list"
    assert metadata["resourceFamily"] == "videos"
    assert metadata["upstream"]["operationKey"] == "videos.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["selectorFields"] == ["id", "chart", "myRating"]
    assert metadata["responseConvention"]["paginationFields"] == ["pageToken", "maxResults"]
    assert metadata["responseConvention"]["chartRefinementFields"] == ["regionCode", "videoCategoryId"]
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "Quota cost: 1" in metadata_text
    assert "API-key" in metadata_text
    assert "OAuth" in metadata_text
    assert "part" in metadata_text
    assert "id" in metadata_text
    assert "chart" in metadata_text
    assert "myRating" in metadata_text
    assert "pageToken" in metadata_text
    assert "regionCode" in metadata_text
    assert "empty" in metadata_text
    assert "search" in metadata_text
    assert "upload" in metadata_text
    assert "analytics" in metadata_text
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_videos_list_descriptor_carries_examples():
    """Expose representative success, empty, validation, access, and scope examples."""
    descriptor = build_videos_list_tool_descriptor()
    metadata = descriptor["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}

    assert descriptor["name"] == "videos_list"
    assert descriptor["inputSchema"] == VIDEOS_LIST_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert metadata["upstream"]["operationKey"] == "videos.list"
    assert {
        "direct_video_lookup",
        "chart_lookup",
        "rating_lookup",
        "paginated_chart_lookup",
        "populated_success",
        "empty_success",
        "missing_part",
        "missing_selector",
        "conflicting_selectors",
        "invalid_pagination",
        "access_failure",
        "oauth_access_failure",
        "quota_or_upstream_failure",
        "deprecated_endpoint",
        "endpoint_unavailable",
        "out_of_scope_video_workflow",
    }.issubset(example_names)


def test_videos_list_declares_expected_failure_categories():
    """Keep caller-visible failure categories stable and bounded."""
    contract = build_videos_list_contract()

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
        ({"id": "abc123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "", "id": "abc123"}, "part"),
        ({"part": "snippet", "id": ""}, "selector"),
        ({"part": "snippet", "chart": "popular"}, "chart"),
        ({"part": "snippet", "myRating": "none"}, "myRating"),
        ({"part": "snippet", "id": "abc123", "chart": "mostPopular"}, "selector"),
        ({"part": "snippet", "id": "abc123", "pageToken": "next"}, "pageToken"),
        ({"part": "snippet", "myRating": "like", "regionCode": "US"}, "regionCode"),
        ({"part": "snippet", "chart": "mostPopular", "q": "music"}, "q"),
    ],
)
def test_videos_list_validation_failures_are_safe(arguments, field):
    """Reject unsupported request shapes without leaking internal details."""
    with pytest.raises(VideosListToolError) as exc_info:
        validate_videos_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "apiKey" not in str(exc_info.value.details)


def test_videos_list_maps_quota_failures_without_secret_details():
    """Map upstream quota failures to a safe public category."""
    handler = build_videos_list_handler(wrapper=QuotaFailingWrapper(), api_key="visible-key")

    with pytest.raises(VideosListToolError) as exc_info:
        handler({"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "api_key" not in str(exc_info.value.details)


def test_videos_list_metadata_text_constants_are_public_safe():
    """Keep exported text constants useful for clients and safe for discovery."""
    combined = " ".join(
        [
            VIDEOS_LIST_DESCRIPTION,
            *VIDEOS_LIST_USAGE_NOTES,
            *VIDEOS_LIST_CAVEATS,
            *(example["description"] for example in VIDEOS_LIST_CALLER_EXAMPLES),
        ]
    )

    assert "Quota cost: 1" in combined
    assert "videos.list" in combined
    assert "id" in combined
    assert "chart" in combined
    assert "myRating" in combined
    assert "pageToken" in combined
    assert "regionCode" in combined
    assert "search" in combined
    assert "upload" in combined
    assert "analytics" in combined
    assert "apiKey" not in combined


def test_videos_insert_input_contract_and_descriptor_shape():
    """Publish the executable ``videos_insert`` creation contract."""
    from mcp_server.tools.youtube_common.videos import (
        VIDEOS_INSERT_CALLER_EXAMPLES,
        VIDEOS_INSERT_INPUT_SCHEMA,
        VIDEOS_INSERT_QUOTA_COST,
        VIDEOS_INSERT_TOOL_NAME,
        build_videos_insert_contract,
        build_videos_insert_tool_descriptor,
    )

    schema = VIDEOS_INSERT_INPUT_SCHEMA
    contract = build_videos_insert_contract()
    descriptor = build_videos_insert_tool_descriptor()
    metadata = contract.to_tool_metadata()
    example_names = {example["name"] for example in VIDEOS_INSERT_CALLER_EXAMPLES}

    assert VIDEOS_INSERT_TOOL_NAME == "videos_insert"
    assert VIDEOS_INSERT_QUOTA_COST == 1600
    assert schema["required"] == ["part", "body", "media"]
    assert schema["properties"]["part"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["body"]["type"] == "object"
    assert schema["properties"]["media"]["type"] == "object"
    assert schema["properties"]["uploadMode"] == {"type": "string", "enum": ["multipart", "resumable"]}
    assert schema["properties"]["notifySubscribers"] == {"type": "boolean"}
    assert schema["properties"]["onBehalfOfContentOwner"] == {"type": "string", "minLength": 1}
    assert schema["additionalProperties"] is False
    assert metadata["upstream"]["operationKey"] == "videos.insert"
    assert metadata["quotaCost"] == 1600
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "media_constrained"
    assert metadata["responseConvention"]["resultKind"] == "upload_result"
    assert metadata["responseConvention"]["resourcePath"] == "item"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert descriptor["name"] == "videos_insert"
    assert descriptor["inputSchema"] == VIDEOS_INSERT_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert {"authorized_video_creation", "resumable_upload", "delegated_content_owner"}.issubset(example_names)


def test_videos_insert_metadata_text_constants_are_public_safe_and_complete():
    """Expose quota, OAuth, upload, caveat, and scope guidance for callers."""
    from mcp_server.tools.youtube_common.videos import (
        VIDEOS_INSERT_CALLER_EXAMPLES,
        VIDEOS_INSERT_CAVEATS,
        VIDEOS_INSERT_DESCRIPTION,
        VIDEOS_INSERT_USAGE_NOTES,
        build_videos_insert_contract,
    )

    contract = build_videos_insert_contract()
    metadata = contract.to_tool_metadata()
    combined = " ".join(
        [
            VIDEOS_INSERT_DESCRIPTION,
            *VIDEOS_INSERT_USAGE_NOTES,
            *VIDEOS_INSERT_CAVEATS,
            *(example["description"] for example in VIDEOS_INSERT_CALLER_EXAMPLES),
        ]
    )

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.MEDIA_CONSTRAINED
    assert "Quota cost: 1600" in combined
    assert "videos.insert" in combined
    assert "OAuth" in combined
    assert "media" in combined
    assert "uploadMode" in combined
    assert "onBehalfOfContentOwner" in combined
    assert "automatic publishing" in combined
    assert "analytics" in combined
    assert "apiKey" not in combined
    assert "raw media" in combined
    assert "raw_media" not in str(metadata)
    assert "signed_url" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_videos_insert_declares_expected_failure_categories():
    """Keep caller-visible ``videos_insert`` failure categories stable."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_contract

    contract = build_videos_insert_contract()

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
        ({"body": {"snippet": {}}, "media": {"mimeType": "video/mp4", "content": "data"}}, "part"),
        ({"part": "snippet", "media": {"mimeType": "video/mp4", "content": "data"}}, "body"),
        ({"part": "snippet", "body": {"snippet": {}}}, "media"),
        (
            {"part": "snippet", "body": {"snippet": {}}, "media": {"mimeType": "video/mp4", "content": "data"}, "q": "x"},
            "q",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {}},
                "media": {"mimeType": "video/mp4", "content": "data"},
                "uploadMode": "direct",
            },
            "uploadMode",
        ),
    ],
)
def test_videos_insert_validation_failures_are_safe(arguments, field):
    """Reject malformed creation requests with safe field details."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, validate_videos_insert_arguments

    with pytest.raises(VideosInsertToolError) as exc_info:
        validate_videos_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "secret" not in str(exc_info.value.details)


def test_videos_insert_maps_quota_failures_without_secret_or_media_details():
    """Map upload quota failures without leaking credentials or raw media."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_handler

    class InsertQuotaFailingWrapper:
        """Layer 1 wrapper double that raises a quota failure."""

        def call(self, _executor, *, arguments, auth_context):
            """Raise a quota failure with unsafe diagnostic details.

            :param _executor: Ignored fake executor.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context supplied by the handler.
            :raises NormalizedUpstreamError: Always raised for quota mapping.
            """
            raise NormalizedUpstreamError(
                message="quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={
                    "oauth_token": "secret",
                    "raw_media": "video-bytes",
                    "signed_url": "https://example.invalid/upload?token=secret",
                    "field": "quota",
                },
            )

    handler = build_videos_insert_handler(wrapper=InsertQuotaFailingWrapper(), oauth_token="visible-oauth")

    with pytest.raises(VideosInsertToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example"}},
                "media": {"mimeType": "video/mp4", "content": "raw-video-content"},
            }
        )

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "video-bytes" not in str(exc_info.value.details)


def test_videos_update_input_contract_and_descriptor_shape():
    """Publish the executable ``videos_update`` mutation contract."""
    schema = VIDEOS_UPDATE_INPUT_SCHEMA
    contract = build_videos_update_contract()
    descriptor = build_videos_update_tool_descriptor()
    metadata = contract.to_tool_metadata()

    assert VIDEOS_UPDATE_TOOL_NAME == "videos_update"
    assert VIDEOS_UPDATE_QUOTA_COST == 50
    assert schema["required"] == ["part", "body"]
    assert schema["properties"]["part"] == {"type": "string", "enum": ["snippet"]}
    assert schema["properties"]["body"]["required"] == ["id", "snippet"]
    assert schema["properties"]["body"]["properties"]["id"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["body"]["properties"]["snippet"]["required"] == ["title"]
    assert schema["properties"]["body"]["properties"]["snippet"]["properties"]["title"] == {
        "type": "string",
        "minLength": 1,
    }
    assert schema["properties"]["onBehalfOfContentOwner"] == {"type": "string", "minLength": 1}
    assert schema["additionalProperties"] is False
    assert metadata["upstream"]["operationKey"] == "videos.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert descriptor["name"] == "videos_update"
    assert descriptor["inputSchema"] == VIDEOS_UPDATE_INPUT_SCHEMA
    assert callable(descriptor["handler"])


def test_videos_update_metadata_text_constants_are_public_safe_and_complete():
    """Expose quota, OAuth, writable-part, update, and scope guidance."""
    contract = build_videos_update_contract()
    metadata = contract.to_tool_metadata()
    combined = " ".join(
        [
            VIDEOS_UPDATE_DESCRIPTION,
            *VIDEOS_UPDATE_USAGE_NOTES,
            *VIDEOS_UPDATE_CAVEATS,
            *(example["description"] for example in VIDEOS_UPDATE_CALLER_EXAMPLES),
        ]
    )
    example_names = {example["name"] for example in VIDEOS_UPDATE_CALLER_EXAMPLES}

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert "Quota cost: 50" in combined
    assert "videos.update" in combined
    assert "OAuth" in combined
    assert "body.id" in combined
    assert "body.snippet.title" in combined
    assert "replacement" in combined
    assert "media upload" in combined
    assert "analytics" in combined
    assert "apiKey" not in combined
    assert "raw upstream" in combined
    assert "oauth_token" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert {
        "authorized_metadata_update",
        "delegated_content_owner_update",
        "missing_identity_failure",
        "unsupported_field_failure",
        "missing_oauth",
        "out_of_scope_video_workflow",
    }.issubset(example_names)


def test_videos_update_declares_expected_failure_categories():
    """Keep caller-visible ``videos_update`` failure categories stable."""
    contract = build_videos_update_contract()

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
        ({}, "part"),
        ({"part": "", "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": "status", "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": {"snippet": {"title": "Updated"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": " ", "snippet": {"title": "Updated"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": "abc123"}}, "body.snippet"),
        ({"part": "snippet", "body": {"id": "abc123", "snippet": {}}}, "body.snippet.title"),
        (
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated", "description": "x"}}},
            "body.snippet.description",
        ),
        ({"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}, "media": {}}, "media"),
    ],
)
def test_videos_update_validation_failures_are_safe(arguments, field):
    """Reject malformed update requests with safe field details."""
    with pytest.raises(VideosUpdateToolError) as exc_info:
        validate_videos_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "secret" not in str(exc_info.value.details)


def test_videos_update_maps_quota_failures_without_secret_details():
    """Map update quota failures without leaking credentials or raw upstream details."""
    class UpdateQuotaFailingWrapper:
        """Layer 1 wrapper double that raises a quota failure."""

        def call(self, _executor, *, arguments, auth_context):
            """Raise a quota failure with unsafe diagnostic details.

            :param _executor: Ignored fake executor.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context supplied by the handler.
            :raises NormalizedUpstreamError: Always raised for quota mapping.
            """
            raise NormalizedUpstreamError(
                message="quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "upstream_body": {"secret": "hidden"},
                    "field": "quota",
                },
            )

    handler = build_videos_update_handler(wrapper=UpdateQuotaFailingWrapper(), oauth_token="visible-oauth")

    with pytest.raises(VideosUpdateToolError) as exc_info:
        handler({"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "Bearer" not in str(exc_info.value.details)


def test_videos_rate_input_contract_and_descriptor_shape():
    """Publish the executable ``videos_rate`` mutation acknowledgment contract."""
    schema = VIDEOS_RATE_INPUT_SCHEMA
    contract = build_videos_rate_contract()
    descriptor = build_videos_rate_tool_descriptor()
    metadata = contract.to_tool_metadata()

    assert VIDEOS_RATE_TOOL_NAME == "videos_rate"
    assert VIDEOS_RATE_QUOTA_COST == 50
    assert schema["required"] == ["id", "rating"]
    assert schema["properties"]["id"] == {"type": "string", "minLength": 1}
    assert schema["properties"]["rating"] == {"type": "string", "enum": ["like", "dislike", "none"]}
    assert schema["additionalProperties"] is False
    assert metadata["upstream"]["operationKey"] == "videos.rate"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "mutation_acknowledgment"
    assert metadata["responseConvention"]["mutation"] == "rated"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["requestBody"] == "none"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert descriptor["name"] == "videos_rate"
    assert descriptor["inputSchema"] == VIDEOS_RATE_INPUT_SCHEMA
    assert callable(descriptor["handler"])


def test_videos_rate_metadata_text_constants_are_public_safe_and_complete():
    """Expose quota, OAuth, rating action, clear-rating, no-body, and scope guidance."""
    contract = build_videos_rate_contract()
    metadata = contract.to_tool_metadata()
    combined = " ".join(
        [
            VIDEOS_RATE_DESCRIPTION,
            *VIDEOS_RATE_USAGE_NOTES,
            *VIDEOS_RATE_CAVEATS,
            *(example["description"] for example in VIDEOS_RATE_CALLER_EXAMPLES),
        ]
    )
    example_names = {example["name"] for example in VIDEOS_RATE_CALLER_EXAMPLES}

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert "Quota cost: 50" in combined
    assert "videos.rate" in combined
    assert "OAuth" in combined
    assert "id" in combined
    assert "rating" in combined
    assert "like" in combined
    assert "dislike" in combined
    assert "none" in combined
    assert "clear" in combined
    assert "no request body" in combined
    assert "acknowledgment" in combined
    assert "history" in combined
    assert "analytics" in combined
    assert "apiKey" not in combined
    assert "oauth_token" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert {
        "authorized_like_rating",
        "authorized_dislike_rating",
        "authorized_clear_rating",
        "missing_identity_failure",
        "missing_rating_failure",
        "unsupported_rating_failure",
        "request_body_failure",
        "missing_oauth",
        "quota_or_upstream_rate_failure",
        "not_found_failure",
        "non_ratable_target_failure",
        "out_of_scope_video_workflow",
    }.issubset(example_names)


def test_videos_rate_declares_expected_failure_categories():
    """Keep caller-visible ``videos_rate`` failure categories stable."""
    contract = build_videos_rate_contract()

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
        ({}, "id"),
        ({"id": "", "rating": "like"}, "id"),
        ({"id": "abc123"}, "rating"),
        ({"id": "abc123", "rating": ""}, "rating"),
        ({"id": "abc123", "rating": "LIKE"}, "rating"),
        ({"id": "abc123", "rating": "favorite"}, "rating"),
        ({"id": "abc123", "rating": "like", "body": {}}, "body"),
        ({"id": "abc123", "rating": "like", "videoId": "abc123"}, "videoId"),
    ],
)
def test_videos_rate_validation_failures_are_safe(arguments, field):
    """Reject malformed rating requests with safe field details."""
    with pytest.raises(VideosRateToolError) as exc_info:
        validate_videos_rate_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "secret" not in str(exc_info.value.details)


def test_videos_rate_maps_quota_failures_without_secret_details():
    """Map rating quota failures without leaking credentials or raw upstream details."""

    class RateQuotaFailingWrapper:
        """Layer 1 wrapper double that raises a quota failure."""

        def call(self, _executor, *, arguments, auth_context):
            """Raise a quota failure with unsafe diagnostic details.

            :param _executor: Ignored fake executor.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context supplied by the handler.
            :raises NormalizedUpstreamError: Always raised for quota mapping.
            """
            raise NormalizedUpstreamError(
                message="quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "upstream_body": {"secret": "hidden"},
                    "field": "quota",
                },
            )

    handler = build_videos_rate_handler(wrapper=RateQuotaFailingWrapper(), oauth_token="visible-oauth")

    with pytest.raises(VideosRateToolError) as exc_info:
        handler({"id": "abc123", "rating": "like"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "Bearer" not in str(exc_info.value.details)


def test_videos_get_rating_input_contract_and_descriptor_shape():
    """Publish the executable ``videos_getRating`` rating lookup contract."""
    schema = VIDEOS_GET_RATING_INPUT_SCHEMA
    contract = build_videos_get_rating_contract()
    descriptor = build_videos_get_rating_tool_descriptor()
    metadata = contract.to_tool_metadata()

    assert VIDEOS_GET_RATING_TOOL_NAME == "videos_getRating"
    assert VIDEOS_GET_RATING_QUOTA_COST == 1
    assert schema["required"] == ["id"]
    assert schema["properties"]["id"]["type"] == "string"
    assert schema["properties"]["id"]["minLength"] == 1
    assert schema["properties"]["onBehalfOfContentOwner"] == {"type": "string", "minLength": 1}
    assert schema["additionalProperties"] is False
    assert metadata["upstream"]["operationKey"] == "videos.getRating"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "rating_lookup"
    assert metadata["responseConvention"]["requiredFields"] == ["id"]
    assert metadata["responseConvention"]["optionalFields"] == ["onBehalfOfContentOwner"]
    assert metadata["responseConvention"]["ratingValues"] == ["like", "dislike", "none", "unspecified"]
    assert metadata["responseConvention"]["requestBody"] == "none"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert descriptor["name"] == "videos_getRating"
    assert descriptor["inputSchema"] == VIDEOS_GET_RATING_INPUT_SCHEMA
    assert callable(descriptor["handler"])


def test_videos_get_rating_metadata_text_constants_are_public_safe_and_complete():
    """Expose quota, OAuth, identifier, returned-state, no-body, and scope guidance."""
    contract = build_videos_get_rating_contract()
    metadata = contract.to_tool_metadata()
    combined = " ".join(
        [
            VIDEOS_GET_RATING_DESCRIPTION,
            *VIDEOS_GET_RATING_USAGE_NOTES,
            *VIDEOS_GET_RATING_CAVEATS,
            *(example["description"] for example in VIDEOS_GET_RATING_CALLER_EXAMPLES),
        ]
    )
    example_names = {example["name"] for example in VIDEOS_GET_RATING_CALLER_EXAMPLES}

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert "Quota cost: 1" in combined
    assert "videos.getRating" in combined
    assert "OAuth" in combined
    assert "id" in combined
    assert "one to fifty" in combined
    assert "onBehalfOfContentOwner" in combined
    assert "like" in combined
    assert "dislike" in combined
    assert "none" in combined
    assert "unspecified" in combined
    assert "no request body" in combined
    assert "rating mutation" in combined
    assert "analytics" in combined
    assert "apiKey" not in combined
    assert "oauth_token" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert {
        "authorized_single_video_lookup",
        "authorized_multi_video_lookup",
        "delegated_partner_lookup",
        "unrated_none_lookup",
        "unspecified_lookup",
        "missing_identity_failure",
        "duplicate_identifier_failure",
        "over_limit_identifier_failure",
        "missing_oauth",
        "quota_or_upstream_lookup_failure",
        "unavailable_target_failure",
        "out_of_scope_video_workflow",
    }.issubset(example_names)


def test_videos_get_rating_declares_expected_failure_categories():
    """Keep caller-visible ``videos_getRating`` failure categories stable."""
    contract = build_videos_get_rating_contract()

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
        ({}, "id"),
        ({"id": ""}, "id"),
        ({"id": "abc123,,def456"}, "id"),
        ({"id": "abc123,abc123"}, "id"),
        ({"id": ",".join(f"video-{index}" for index in range(51))}, "id"),
        ({"id": "abc123", "body": {}}, "body"),
        ({"id": "abc123", "videoId": "abc123"}, "videoId"),
        ({"id": "abc123", "onBehalfOfContentOwner": ""}, "onBehalfOfContentOwner"),
    ],
)
def test_videos_get_rating_validation_failures_are_safe(arguments, field):
    """Reject malformed rating lookup requests with safe field details."""
    with pytest.raises(VideosGetRatingToolError) as exc_info:
        validate_videos_get_rating_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field
    assert "secret" not in str(exc_info.value.details)


def test_videos_get_rating_maps_quota_failures_without_secret_details():
    """Map rating lookup quota failures without leaking credentials or raw upstream details."""

    class GetRatingQuotaFailingWrapper:
        """Layer 1 wrapper double that raises a quota failure."""

        def call(self, _executor, *, arguments, auth_context):
            """Raise a quota failure with unsafe diagnostic details.

            :param _executor: Ignored fake executor.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context supplied by the handler.
            :raises NormalizedUpstreamError: Always raised for quota mapping.
            """
            raise NormalizedUpstreamError(
                message="quota exceeded",
                category="rate_limit",
                retryable=False,
                upstream_status=403,
                details={
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "upstream_body": {"secret": "hidden"},
                    "field": "quota",
                },
            )

    handler = build_videos_get_rating_handler(wrapper=GetRatingQuotaFailingWrapper(), oauth_token="visible-oauth")

    with pytest.raises(VideosGetRatingToolError) as exc_info:
        handler({"id": "abc123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"field": "quota"}
    assert "secret" not in str(exc_info.value)
    assert "Bearer" not in str(exc_info.value.details)
