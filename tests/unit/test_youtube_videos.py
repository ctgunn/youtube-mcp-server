"""Unit tests for Layer 2 ``videos_list`` behavior."""

from __future__ import annotations

import pytest

from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.videos import (
    VideosListToolError,
    build_videos_list_handler,
    map_videos_list_result,
    validate_videos_list_arguments,
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
        :param auth_context: Auth context supplied by the handler.
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
        :param auth_context: Auth context supplied by the handler.
        :raises Exception: The configured fake error.
        """
        raise self.error


def test_validate_videos_list_accepts_id_selector():
    """Normalize a direct video lookup without changing caller semantics."""
    assert validate_videos_list_arguments({"part": " snippet, contentDetails ", "id": " abc123, def456 "}) == {
        "part": "snippet, contentDetails",
        "id": "abc123, def456",
    }


def test_validate_videos_list_accepts_chart_selector_with_pagination_and_refinements():
    """Normalize a chart lookup with paging and chart-only refinements."""
    assert validate_videos_list_arguments(
        {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "pageToken": " next-page ",
            "maxResults": 25,
            "regionCode": " us ",
            "videoCategoryId": " 10 ",
        }
    ) == {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "pageToken": "next-page",
        "maxResults": 25,
        "regionCode": "US",
        "videoCategoryId": "10",
    }


def test_validate_videos_list_accepts_rating_selector_with_pagination():
    """Normalize a caller-specific rating lookup with paging."""
    assert validate_videos_list_arguments(
        {"part": "snippet", "myRating": " like ", "pageToken": "next", "maxResults": 50}
    ) == {
        "part": "snippet",
        "myRating": "like",
        "pageToken": "next",
        "maxResults": 50,
    }


def test_map_videos_list_result_preserves_near_raw_context():
    """Map upstream items with endpoint, quota, selector, paging, chart, and auth context."""
    payload = {
        "kind": "youtube#videoListResponse",
        "etag": "etag-value",
        "nextPageToken": "next",
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        "items": [{"kind": "youtube#video", "id": "abc123", "snippet": {"title": "Example"}}],
    }

    result = map_videos_list_result(
        payload,
        {
            "part": "snippet, statistics",
            "chart": "mostPopular",
            "pageToken": "first",
            "maxResults": 1,
            "regionCode": "US",
        },
        auth_mode="api_key",
    )

    assert result["endpoint"] == "videos.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet", "statistics"]
    assert result["selector"] == {"mode": "chart", "chart": "mostPopular"}
    assert result["pagination"] == {
        "pageToken": "first",
        "maxResults": 1,
        "nextPageToken": "next",
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
    }
    assert result["chartRefinement"] == {"regionCode": "US"}
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert result["availability"] == {"state": "active"}
    assert result["items"] == payload["items"]
    assert result["empty"] is False
    assert result["kind"] == payload["kind"]
    assert result["etag"] == "etag-value"


def test_handler_calls_layer1_once_with_api_key_for_id_lookup():
    """Execute the Layer 1 wrapper once with API-key credentials for direct lookup."""
    wrapper = RecordingWrapper(payload={"items": [{"id": "abc123", "snippet": {"title": "Example"}}]})
    handler = build_videos_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "id": "abc123"})

    assert result["items"] == [{"id": "abc123", "snippet": {"title": "Example"}}]
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"] == {"part": "snippet", "id": "abc123"}
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.API_KEY
    assert wrapper.calls[0]["auth_context"].credentials.api_key == "local-key"


def test_handler_calls_layer1_once_with_oauth_for_rating_lookup():
    """Execute the Layer 1 wrapper once with OAuth credentials for rating lookup."""
    wrapper = RecordingWrapper(payload={"items": [{"id": "abc123"}]})
    handler = build_videos_list_handler(wrapper=wrapper, oauth_token="local-oauth")

    result = handler({"part": "snippet", "myRating": "like"})

    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.OAUTH_REQUIRED
    assert wrapper.calls[0]["auth_context"].credentials.oauth_token == "local-oauth"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": " ", "id": "abc123"}, "part"),
        ({"part": 123, "id": "abc123"}, "part"),
        ({"part": ",,,", "id": "abc123"}, "part"),
        ({"part": "snippet", "id": ""}, "selector"),
        ({"part": "snippet", "id": ",,,"}, "id"),
        ({"part": "snippet", "chart": ""}, "selector"),
        ({"part": "snippet", "chart": "popular"}, "chart"),
        ({"part": "snippet", "myRating": ""}, "selector"),
        ({"part": "snippet", "myRating": "none"}, "myRating"),
        ({"part": "snippet", "id": "abc123", "chart": "mostPopular"}, "selector"),
        ({"part": "snippet", "chart": "mostPopular", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "chart": "mostPopular", "pageToken": 123}, "pageToken"),
        ({"part": "snippet", "chart": "mostPopular", "maxResults": 0}, "maxResults"),
        ({"part": "snippet", "chart": "mostPopular", "maxResults": 51}, "maxResults"),
        ({"part": "snippet", "chart": "mostPopular", "maxResults": True}, "maxResults"),
        ({"part": "snippet", "id": "abc123", "pageToken": "next"}, "pageToken"),
        ({"part": "snippet", "id": "abc123", "maxResults": 10}, "maxResults"),
        ({"part": "snippet", "myRating": "like", "regionCode": "US"}, "regionCode"),
        ({"part": "snippet", "myRating": "like", "videoCategoryId": "10"}, "videoCategoryId"),
        ({"part": "snippet", "chart": "mostPopular", "regionCode": "USA"}, "regionCode"),
        ({"part": "snippet", "chart": "mostPopular", "videoCategoryId": ""}, "videoCategoryId"),
    ],
)
def test_validation_rejects_missing_invalid_and_incompatible_inputs(arguments, field):
    """Reject malformed selectors, pagination, and refinements before execution."""
    with pytest.raises(VideosListToolError) as exc_info:
        validate_videos_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "field",
    [
        "q",
        "uploadMode",
        "body",
        "media",
        "rating",
        "includeTranscript",
        "transcript",
        "analytics",
        "recommend",
        "rankResults",
        "summarize",
        "enrich",
        "delete",
        "update",
    ],
)
def test_validation_rejects_unsupported_video_workflows(field):
    """Reject search, upload, mutation, analytics, ranking, and enrichment fields."""
    with pytest.raises(VideosListToolError) as exc_info:
        validate_videos_list_arguments({"part": "snippet", "id": "abc123", field: "value"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_handler_rejects_missing_api_key_before_layer1_execution():
    """Surface API-key access failures without calling Layer 1."""
    wrapper = RecordingWrapper()
    handler = build_videos_list_handler(wrapper=wrapper, api_key=None)

    with pytest.raises(VideosListToolError) as exc_info:
        handler({"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}
    assert wrapper.calls == []


def test_handler_rejects_missing_oauth_before_layer1_execution():
    """Surface OAuth access failures without calling Layer 1."""
    wrapper = RecordingWrapper()
    handler = build_videos_list_handler(wrapper=wrapper, oauth_token=None)

    with pytest.raises(VideosListToolError) as exc_info:
        handler({"part": "snippet", "myRating": "like"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_handler_maps_layer1_auth_mode_errors_to_safe_access_failure():
    """Map Layer 1 auth-mode failures to sanitized authentication errors."""
    wrapper = FailingWrapper(ValueError("videos.list requires api_key auth"))
    handler = build_videos_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideosListToolError) as exc_info:
        handler({"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "api_key"}


def test_handler_returns_empty_success_when_upstream_items_are_empty():
    """Treat empty upstream item collections as successful video list results."""
    wrapper = RecordingWrapper(payload={"items": []})
    handler = build_videos_list_handler(wrapper=wrapper, api_key="local-key")

    result = handler({"part": "snippet", "chart": "mostPopular", "maxResults": 10})

    assert result["items"] == []
    assert result["selector"] == {"mode": "chart", "chart": "mostPopular"}
    assert result["pagination"] == {"maxResults": 10}
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
        ("removed", "resource_not_found"),
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
    handler = build_videos_list_handler(wrapper=wrapper, api_key="local-key")

    with pytest.raises(VideosListToolError) as exc_info:
        handler({"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)
