"""Unit tests for Layer 2 ``videoAbuseReportReasons_list`` behavior."""

from __future__ import annotations

import pytest

from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.video_abuse_report_reasons import (
    VideoAbuseReportReasonsListToolError,
    build_video_abuse_report_reasons_list_handler,
    map_video_abuse_report_reasons_list_result,
    validate_video_abuse_report_reasons_list_arguments,
)


class RecordingWrapper:
    """Layer 1 wrapper double that records each call."""

    def __init__(self, payload=None):
        """Store the fake payload and initialize call history."""
        self.payload = payload or {"items": []}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the Layer 1 call and return the configured payload."""
        self.calls.append({"executor": executor, "arguments": arguments, "auth_context": auth_context})
        return self.payload


class FailingWrapper:
    """Layer 1 wrapper double that raises a configured upstream error."""

    def __init__(self, error):
        """Store the error raised for every call."""
        self.error = error

    def call(self, _executor, *, arguments, auth_context):
        """Raise the configured error for execution-boundary tests."""
        raise self.error


def test_validate_video_abuse_report_reasons_list_accepts_required_fields():
    """Normalize the required lookup fields without changing caller semantics."""
    assert validate_video_abuse_report_reasons_list_arguments({"part": " snippet ", "hl": " en-US "}) == {
        "part": "snippet",
        "hl": "en-US",
    }


def test_map_video_abuse_report_reasons_list_result_preserves_near_raw_context():
    """Map upstream items with endpoint, quota, localization, and auth context."""
    payload = {
        "kind": "youtube#videoAbuseReportReasonListResponse",
        "etag": "etag-value",
        "items": [
            {
                "kind": "youtube#videoAbuseReportReason",
                "id": "V",
                "snippet": {"label": "Violent or repulsive content"},
            }
        ],
    }

    result = map_video_abuse_report_reasons_list_result(payload, {"part": "snippet, id", "hl": "en"})

    assert result["endpoint"] == "videoAbuseReportReasons.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet", "id"]
    assert result["localization"] == {"hl": "en"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"] == payload["items"]
    assert result["kind"] == payload["kind"]
    assert result["etag"] == "etag-value"


def test_handler_calls_layer1_once_with_api_key_auth_context():
    """Execute the Layer 1 wrapper once with API-key credentials."""
    wrapper = RecordingWrapper(payload={"items": [{"id": "S", "snippet": {"label": "Spam"}}]})
    handler = build_video_abuse_report_reasons_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "hl": "en"})

    assert result["items"] == [{"id": "S", "snippet": {"label": "Spam"}}]
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"] == {"part": "snippet", "hl": "en"}
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.API_KEY
    assert wrapper.calls[0]["auth_context"].credentials.api_key == "local-key"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "part"),
        ({"part": "snippet"}, "hl"),
        ({"part": " ", "hl": "en"}, "part"),
        ({"part": 123, "hl": "en"}, "part"),
        ({"part": ",,,", "hl": "en"}, "part"),
        ({"part": "snippet", "hl": " "}, "hl"),
        ({"part": "snippet", "hl": "en us"}, "hl"),
        ({"part": "snippet", "hl": 123}, "hl"),
        ({"part": "snippet", "hl": "en", "reasonId": "spam"}, "reasonId"),
    ],
)
def test_validation_rejects_missing_invalid_and_out_of_scope_inputs(arguments, field):
    """Reject missing, invalid, and mutation-oriented inputs before execution."""
    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        validate_video_abuse_report_reasons_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "field",
    [
        "videoId",
        "reasonId",
        "reportText",
        "pageToken",
        "id",
        "regionCode",
        "moderationStatus",
        "evaluatePolicy",
        "rankResults",
        "summarize",
        "enrich",
        "locale",
        "language",
        "displayLanguage",
    ],
)
def test_validation_rejects_unsupported_lookup_workflows(field):
    """Reject selector, paging, mutation, moderation, and enrichment fields."""
    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        validate_video_abuse_report_reasons_list_arguments({"part": "snippet", "hl": "en", field: "value"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_handler_rejects_missing_api_key_before_layer1_execution():
    """Surface API-key access failures without calling Layer 1."""
    wrapper = RecordingWrapper()
    handler = build_video_abuse_report_reasons_list_handler(wrapper=wrapper, api_key=None)

    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        handler({"part": "snippet", "hl": "en"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}
    assert wrapper.calls == []


def test_handler_maps_layer1_auth_mode_errors_to_safe_access_failure():
    """Map Layer 1 auth-mode failures to sanitized authentication errors."""
    wrapper = FailingWrapper(ValueError("videoAbuseReportReasons.list requires api_key auth"))
    handler = build_video_abuse_report_reasons_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        handler({"part": "snippet", "hl": "en"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}


def test_handler_returns_empty_success_when_upstream_items_are_empty():
    """Treat empty upstream item collections as successful lookups."""
    wrapper = RecordingWrapper(payload={"items": []})
    handler = build_video_abuse_report_reasons_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "hl": "fr"})

    assert result["items"] == []
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
    handler = build_video_abuse_report_reasons_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideoAbuseReportReasonsListToolError) as exc_info:
        handler({"part": "snippet", "hl": "en"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)
