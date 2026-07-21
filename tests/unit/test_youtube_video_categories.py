"""Unit tests for Layer 2 ``videoCategories_list`` behavior."""

from __future__ import annotations

import pytest

from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.video_categories import (
    VideoCategoriesListToolError,
    build_video_categories_list_handler,
    map_video_categories_list_result,
    validate_video_categories_list_arguments,
)


class RecordingWrapper:
    """Layer 1 wrapper double that records each call."""

    def __init__(self, payload=None):
        """Store the fake payload and initialize call history.

        :param payload: Optional payload returned by each wrapper call.
        """
        self.payload = payload or {"items": []}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the Layer 1 call and return the configured payload.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: API-key auth context supplied by the handler.
        :return: Configured fake payload.
        """
        self.calls.append({"executor": executor, "arguments": arguments, "auth_context": auth_context})
        return self.payload


class FailingWrapper:
    """Layer 1 wrapper double that raises a configured upstream error."""

    def __init__(self, error):
        """Store the error raised for every call.

        :param error: Exception to raise during wrapper execution.
        """
        self.error = error

    def call(self, _executor, *, arguments, auth_context):
        """Raise the configured error for execution-boundary tests.

        :param _executor: Ignored fake executor.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: API-key auth context supplied by the handler.
        :raises Exception: The configured fake error.
        """
        raise self.error


def test_validate_video_categories_list_accepts_region_selector():
    """Normalize a region lookup without changing caller semantics."""
    assert validate_video_categories_list_arguments({"part": " snippet ", "regionCode": " us ", "hl": " es "}) == {
        "part": "snippet",
        "regionCode": "US",
        "hl": "es",
    }


def test_validate_video_categories_list_accepts_id_selector():
    """Normalize an ID lookup without requiring a region selector."""
    assert validate_video_categories_list_arguments({"part": "snippet", "id": " 10, 20 "}) == {
        "part": "snippet",
        "id": "10, 20",
    }


def test_map_video_categories_list_result_preserves_near_raw_region_context():
    """Map upstream items with endpoint, quota, selector, localization, and auth context."""
    payload = {
        "kind": "youtube#videoCategoryListResponse",
        "etag": "etag-value",
        "items": [
            {
                "kind": "youtube#videoCategory",
                "id": "10",
                "snippet": {"title": "Music", "assignable": True},
            }
        ],
    }

    result = map_video_categories_list_result(payload, {"part": "snippet, id", "regionCode": "US", "hl": "en"})

    assert result["endpoint"] == "videoCategories.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet", "id"]
    assert result["selector"] == {"mode": "regionCode", "regionCode": "US"}
    assert result["localization"] == {"hl": "en"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["availability"] == {"state": "active"}
    assert result["items"] == payload["items"]
    assert result["kind"] == payload["kind"]
    assert result["etag"] == "etag-value"


def test_map_video_categories_list_result_preserves_id_context():
    """Map ID lookups with normalized category identifier context."""
    result = map_video_categories_list_result({"items": [{"id": "10"}]}, {"part": "snippet", "id": "10,20"})

    assert result["selector"] == {"mode": "id", "id": ["10", "20"]}
    assert result["items"] == [{"id": "10"}]


def test_handler_calls_layer1_once_with_api_key_auth_context():
    """Execute the Layer 1 wrapper once with API-key credentials."""
    wrapper = RecordingWrapper(payload={"items": [{"id": "10", "snippet": {"title": "Music"}}]})
    handler = build_video_categories_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "regionCode": "US"})

    assert result["items"] == [{"id": "10", "snippet": {"title": "Music"}}]
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"] == {"part": "snippet", "regionCode": "US"}
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.API_KEY
    assert wrapper.calls[0]["auth_context"].credentials.api_key == "local-key"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": " ", "regionCode": "US"}, "part"),
        ({"part": 123, "regionCode": "US"}, "part"),
        ({"part": ",,,", "regionCode": "US"}, "part"),
        ({"part": "snippet", "regionCode": ""}, "selector"),
        ({"part": "snippet", "id": ""}, "selector"),
        ({"part": "snippet", "regionCode": "U"}, "regionCode"),
        ({"part": "snippet", "regionCode": "USA"}, "regionCode"),
        ({"part": "snippet", "regionCode": "US", "id": "10"}, "selector"),
        ({"part": "snippet", "regionCode": "US", "hl": " "}, "hl"),
        ({"part": "snippet", "regionCode": "US", "hl": "en us"}, "hl"),
        ({"part": "snippet", "regionCode": "US", "hl": 123}, "hl"),
        ({"part": "snippet", "regionCode": "US", "videoId": "abc"}, "videoId"),
    ],
)
def test_validation_rejects_missing_invalid_and_out_of_scope_inputs(arguments, field):
    """Reject missing, invalid, and out-of-scope inputs before execution."""
    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        validate_video_categories_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "field",
    [
        "pageToken",
        "order",
        "q",
        "videoId",
        "channelId",
        "analytics",
        "classifyVideo",
        "rankResults",
        "summarize",
        "enrich",
        "locale",
        "language",
        "displayLanguage",
    ],
)
def test_validation_rejects_unsupported_category_workflows(field):
    """Reject paging, search, analytics, classification, and enrichment fields."""
    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        validate_video_categories_list_arguments({"part": "snippet", "regionCode": "US", field: "value"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_handler_rejects_missing_api_key_before_layer1_execution():
    """Surface API-key access failures without calling Layer 1."""
    wrapper = RecordingWrapper()
    handler = build_video_categories_list_handler(wrapper=wrapper, api_key=None)

    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        handler({"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}
    assert wrapper.calls == []


def test_handler_maps_layer1_auth_mode_errors_to_safe_access_failure():
    """Map Layer 1 auth-mode failures to sanitized authentication errors."""
    wrapper = FailingWrapper(ValueError("videoCategories.list requires api_key auth"))
    handler = build_video_categories_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        handler({"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}


def test_handler_returns_empty_success_when_upstream_items_are_empty():
    """Treat empty upstream item collections as successful lookups."""
    wrapper = RecordingWrapper(payload={"items": []})
    handler = build_video_categories_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "id": "999999", "hl": "fr"})

    assert result["items"] == []
    assert result["selector"] == {"mode": "id", "id": ["999999"]}
    assert result["localization"] == {"hl": "fr"}
    assert result["empty"] is True


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("rate_limit", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "upstream_failure"),
    ],
)
def test_handler_maps_and_sanitizes_upstream_failures(upstream_category, expected_category):
    """Convert Layer 1 failures into safe caller-facing categories."""
    wrapper = FailingWrapper(
        NormalizedUpstreamError(
            message="upstream failed",
            category=upstream_category,
            retryable=False,
            upstream_status=503,
            details={
                "authorization": "Bearer secret",
                "api_key": "hidden",
                "oauth_token": "hidden",
                "reason": "safe",
                "upstream_body": {"secret": "hidden"},
            },
        )
    )
    handler = build_video_categories_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideoCategoriesListToolError) as exc_info:
        handler({"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)
