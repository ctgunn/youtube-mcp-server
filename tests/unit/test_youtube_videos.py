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


def _valid_videos_insert_arguments(**overrides):
    """Build a valid ``videos_insert`` request for unit tests.

    :param overrides: Field overrides for the default request.
    :return: A valid upload request with any overrides applied.
    """
    arguments = {
        "part": " snippet,status ",
        "body": {"snippet": {"title": "Example upload"}, "status": {"privacyStatus": "private"}},
        "media": {"mimeType": " video/mp4 ", "content": "fake-video-content"},
    }
    arguments.update(overrides)
    return arguments


def _valid_videos_update_arguments(**overrides):
    """Build a valid ``videos_update`` request for unit tests.

    :param overrides: Field overrides for the default request.
    :return: A valid update request with any overrides applied.
    """
    arguments = {
        "part": " snippet ",
        "body": {"id": " abc123 ", "snippet": {"title": " Updated title "}},
    }
    arguments.update(overrides)
    return arguments


def _valid_videos_rate_arguments(**overrides):
    """Build a valid ``videos_rate`` request for unit tests.

    :param overrides: Field overrides for the default request.
    :return: A valid rating request with any overrides applied.
    """
    arguments = {"id": " abc123 ", "rating": "like"}
    arguments.update(overrides)
    return arguments


def test_validate_videos_insert_accepts_authorized_metadata_media_and_options():
    """Normalize valid video creation metadata, media, upload, and delegation fields."""
    from mcp_server.tools.youtube_common.videos import validate_videos_insert_arguments

    normalized = validate_videos_insert_arguments(
        _valid_videos_insert_arguments(
            uploadMode=" resumable ",
            notifySubscribers=False,
            onBehalfOfContentOwner=" owner-123 ",
        )
    )

    assert normalized == {
        "part": "snippet,status",
        "body": {"snippet": {"title": "Example upload"}, "status": {"privacyStatus": "private"}},
        "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
        "uploadMode": "resumable",
        "notifySubscribers": False,
        "onBehalfOfContentOwner": "owner-123",
    }


def test_map_videos_insert_result_preserves_context_without_raw_media():
    """Map a created video result with upload, auth, delegation, and returned fields."""
    from mcp_server.tools.youtube_common.videos import map_videos_insert_result

    payload = {
        "kind": "youtube#video",
        "etag": "etag-video",
        "id": "video-123",
        "snippet": {"title": "Example upload"},
        "status": {"privacyStatus": "private"},
    }
    result = map_videos_insert_result(
        payload,
        _valid_videos_insert_arguments(uploadMode="resumable", onBehalfOfContentOwner="owner-123"),
    )

    assert result["endpoint"] == "videos.insert"
    assert result["quotaCost"] == 1600
    assert result["requestedParts"] == ["snippet", "status"]
    assert result["upload"] == {"mode": "resumable", "mimeType": "video/mp4", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["availability"]["state"] == "media_constrained"
    assert result["delegation"] == {"onBehalfOfContentOwner": "owner-123"}
    assert result["mutation"] == {"type": "created"}
    assert result["item"] == payload
    assert result["kind"] == "youtube#video"
    assert result["id"] == "video-123"
    assert "fake-video-content" not in str(result)


def test_videos_insert_handler_calls_layer1_once_with_oauth():
    """Execute the Layer 1 insert wrapper once with OAuth-required credentials."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_handler

    wrapper = RecordingWrapper(payload={"id": "video-123", "snippet": {"title": "Example upload"}})
    handler = build_videos_insert_handler(wrapper=wrapper, oauth_token="local-oauth")

    result = handler(_valid_videos_insert_arguments())

    assert result["endpoint"] == "videos.insert"
    assert result["item"]["id"] == "video-123"
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"]["part"] == "snippet,status"
    assert wrapper.calls[0]["arguments"]["media"] == {"mimeType": "video/mp4", "content": "fake-video-content"}
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.OAUTH_REQUIRED
    assert wrapper.calls[0]["auth_context"].credentials.oauth_token == "local-oauth"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "part"),
        ({"part": "", "body": {"snippet": {}}, "media": {"mimeType": "video/mp4", "content": "data"}}, "part"),
        ({"part": 123, "body": {"snippet": {}}, "media": {"mimeType": "video/mp4", "content": "data"}}, "part"),
        ({"part": " , ", "body": {"snippet": {}}, "media": {"mimeType": "video/mp4", "content": "data"}}, "part"),
        ({"part": "snippet", "media": {"mimeType": "video/mp4", "content": "data"}}, "body"),
        ({"part": "snippet", "body": {}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": "title"}, "media": {"mimeType": "video/mp4", "content": "data"}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": {}}}, "media"),
        ({"part": "snippet", "body": {"snippet": {}}, "media": {}}, "media.mimeType"),
        ({"part": "snippet", "body": {"snippet": {}}, "media": {"mimeType": "video/mp4"}}, "media.content"),
        (
            {
                "part": "snippet",
                "body": {"snippet": {}},
                "media": {"mimeType": "video/mp4", "content": "data"},
                "uploadMode": "direct",
            },
            "uploadMode",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {}},
                "media": {"mimeType": "video/mp4", "content": "data"},
                "notifySubscribers": "false",
            },
            "notifySubscribers",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {}},
                "media": {"mimeType": "video/mp4", "content": "data"},
                "onBehalfOfContentOwner": "",
            },
            "onBehalfOfContentOwner",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {}},
                "media": {"mimeType": "video/mp4", "content": "data"},
                "publishAt": "now",
            },
            "publishAt",
        ),
    ],
)
def test_videos_insert_validation_rejects_missing_invalid_and_unsupported_inputs(arguments, field):
    """Reject malformed creation, metadata-only, media-only, option, and scope requests."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, validate_videos_insert_arguments

    with pytest.raises(VideosInsertToolError) as exc_info:
        validate_videos_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_videos_insert_handler_rejects_missing_oauth_before_layer1_execution():
    """Surface missing OAuth without invoking the Layer 1 upload wrapper."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_handler

    wrapper = RecordingWrapper()
    handler = build_videos_insert_handler(wrapper=wrapper, oauth_token=None)

    with pytest.raises(VideosInsertToolError) as exc_info:
        handler(_valid_videos_insert_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("policy_restricted", "authorization_failed"),
        ("upload_rejected", "invalid_request"),
        ("rate_limit", "quota_exhausted"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("availability", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "upstream_failure"),
    ],
)
def test_videos_insert_handler_maps_and_sanitizes_upstream_failures(upstream_category, expected_category):
    """Convert Layer 1 upload failures into safe caller-facing categories."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_handler

    wrapper = FailingWrapper(
        NormalizedUpstreamError(
            message="upstream failed",
            category=upstream_category,
            retryable=False,
            upstream_status=503,
            details={
                "authorization": "Bearer secret",
                "oauth_token": "hidden",
                "raw_media": "raw-video-bytes",
                "signed_url": "https://example.invalid/upload?token=secret",
                "reason": "safe",
                "upstream_body": {"secret": "hidden"},
            },
        )
    )
    handler = build_videos_insert_handler(wrapper=wrapper, oauth_token="local-oauth")

    with pytest.raises(VideosInsertToolError) as exc_info:
        handler(_valid_videos_insert_arguments())

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)


def test_validate_videos_rate_accepts_supported_rating_actions():
    """Normalize valid video rating requests without changing rating semantics."""
    from mcp_server.tools.youtube_common.videos import validate_videos_rate_arguments

    assert validate_videos_rate_arguments(_valid_videos_rate_arguments(rating="like")) == {
        "id": "abc123",
        "rating": "like",
    }
    assert validate_videos_rate_arguments(_valid_videos_rate_arguments(rating="dislike")) == {
        "id": "abc123",
        "rating": "dislike",
    }
    assert validate_videos_rate_arguments(_valid_videos_rate_arguments(rating="none")) == {
        "id": "abc123",
        "rating": "none",
    }


def test_map_videos_rate_result_returns_no_content_acknowledgment():
    """Map successful no-content rate responses without fabricating video details."""
    from mcp_server.tools.youtube_common.videos import map_videos_rate_result

    result = map_videos_rate_result({}, _valid_videos_rate_arguments(rating="none"))

    assert result == {
        "endpoint": "videos.rate",
        "quotaCost": 50,
        "rating": {"videoId": "abc123", "requestedRating": "none", "clearsRating": True},
        "auth": {"mode": "oauth_required", "path": "restricted"},
        "availability": {"state": "active"},
        "mutation": {"type": "rated", "acknowledged": True},
        "status": {"code": 204, "body": "none"},
    }


@pytest.mark.parametrize("rating", ["like", "dislike", "none"])
def test_videos_rate_handler_calls_layer1_once_with_oauth(rating):
    """Execute the Layer 1 rate wrapper once with OAuth-required credentials."""
    from mcp_server.tools.youtube_common.videos import build_videos_rate_handler

    wrapper = RecordingWrapper(payload={})
    handler = build_videos_rate_handler(wrapper=wrapper, oauth_token="local-oauth")

    result = handler(_valid_videos_rate_arguments(rating=rating))

    assert result["endpoint"] == "videos.rate"
    assert result["rating"]["videoId"] == "abc123"
    assert result["rating"]["requestedRating"] == rating
    assert result["rating"].get("clearsRating", False) is (rating == "none")
    assert result["status"] == {"code": 204, "body": "none"}
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"] == {"id": "abc123", "rating": rating}
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.OAUTH_REQUIRED
    assert wrapper.calls[0]["auth_context"].credentials.oauth_token == "local-oauth"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "id"),
        ({"id": "", "rating": "like"}, "id"),
        ({"id": "   ", "rating": "like"}, "id"),
        ({"id": 123, "rating": "like"}, "id"),
        ({"id": "abc123"}, "rating"),
        ({"id": "abc123", "rating": ""}, "rating"),
        ({"id": "abc123", "rating": 123}, "rating"),
        ({"id": "abc123", "rating": "LIKE"}, "rating"),
        ({"id": "abc123", "rating": "favorite"}, "rating"),
        ({"id": "abc123", "rating": "like", "body": {}}, "body"),
        ({"id": "abc123", "rating": "like", "videoId": "abc123"}, "videoId"),
        ({"id": "abc123", "rating": "like", "onBehalfOfContentOwner": "owner"}, "onBehalfOfContentOwner"),
    ],
)
def test_videos_rate_validation_rejects_missing_invalid_and_unsupported_inputs(arguments, field):
    """Reject malformed rating requests and unsupported aliases or modifiers."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, validate_videos_rate_arguments

    with pytest.raises(VideosRateToolError) as exc_info:
        validate_videos_rate_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "field",
    [
        "part",
        "myRating",
        "ratingHistory",
        "ratingCount",
        "currentRating",
        "media",
        "uploadMode",
        "update",
        "delete",
        "reportAbuse",
        "thumbnail",
        "caption",
        "playlist",
        "comment",
        "includeTranscript",
        "analytics",
        "recommend",
        "rankResults",
        "summarize",
        "enrich",
    ],
)
def test_videos_rate_validation_rejects_out_of_scope_workflow_fields(field):
    """Reject lookup, upload, update, analytics, ranking, and enrichment fields."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, validate_videos_rate_arguments

    with pytest.raises(VideosRateToolError) as exc_info:
        validate_videos_rate_arguments({"id": "abc123", "rating": "like", field: "value"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_videos_rate_handler_rejects_missing_oauth_before_layer1_execution():
    """Surface missing OAuth without invoking the Layer 1 rate wrapper."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, build_videos_rate_handler

    wrapper = RecordingWrapper()
    handler = build_videos_rate_handler(wrapper=wrapper, oauth_token=None)

    with pytest.raises(VideosRateToolError) as exc_info:
        handler(_valid_videos_rate_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("invalid_rating", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("forbidden", "authorization_failed"),
        ("policy_restricted", "authorization_failed"),
        ("disabled_rating", "authorization_failed"),
        ("purchase_required", "authorization_failed"),
        ("unverified_email", "authorization_failed"),
        ("non_ratable", "authorization_failed"),
        ("rate_limit", "quota_exhausted"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("availability", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "upstream_failure"),
    ],
)
def test_videos_rate_handler_maps_and_sanitizes_upstream_failures(upstream_category, expected_category):
    """Convert Layer 1 rating failures into safe caller-facing categories."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, build_videos_rate_handler

    wrapper = FailingWrapper(
        NormalizedUpstreamError(
            message="upstream failed",
            category=upstream_category,
            retryable=False,
            upstream_status=503,
            details={
                "authorization": "Bearer secret",
                "oauth_token": "hidden",
                "upstream_body": {"secret": "hidden"},
                "stacktrace": "hidden",
                "reason": "safe",
            },
        )
    )
    handler = build_videos_rate_handler(wrapper=wrapper, oauth_token="local-oauth")

    with pytest.raises(VideosRateToolError) as exc_info:
        handler(_valid_videos_rate_arguments())

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)
    assert "hidden" not in str(exc_info.value.details)
    assert "raw-video-bytes" not in str(exc_info.value.details)


def test_validate_videos_update_accepts_authorized_snippet_title_and_delegation():
    """Normalize valid video update identity, snippet title, and delegation fields."""
    from mcp_server.tools.youtube_common.videos import validate_videos_update_arguments

    normalized = validate_videos_update_arguments(
        _valid_videos_update_arguments(onBehalfOfContentOwner=" owner-123 ")
    )

    assert normalized == {
        "part": "snippet",
        "body": {"id": "abc123", "snippet": {"title": "Updated title"}},
        "onBehalfOfContentOwner": "owner-123",
    }


def test_map_videos_update_result_preserves_context_and_sparse_fields():
    """Map an updated video result with update, auth, delegation, and returned fields."""
    from mcp_server.tools.youtube_common.videos import map_videos_update_result

    payload = {
        "kind": "youtube#video",
        "etag": "etag-video",
        "id": "abc123",
        "snippet": {"title": "Updated title"},
    }
    result = map_videos_update_result(
        payload,
        _valid_videos_update_arguments(onBehalfOfContentOwner="owner-123"),
    )

    assert result["endpoint"] == "videos.update"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["update"] == {
        "videoId": "abc123",
        "bodyFields": ["id", "snippet"],
        "snippetFields": ["title"],
    }
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["delegation"] == {"onBehalfOfContentOwner": "owner-123"}
    assert result["mutation"] == {"type": "updated"}
    assert result["item"] == payload
    assert result["kind"] == "youtube#video"
    assert result["id"] == "abc123"
    assert "publication" not in result
    assert "analytics" not in result


def test_videos_update_handler_calls_layer1_once_with_oauth():
    """Execute the Layer 1 update wrapper once with OAuth-required credentials."""
    from mcp_server.tools.youtube_common.videos import build_videos_update_handler

    wrapper = RecordingWrapper(payload={"id": "abc123", "snippet": {"title": "Updated title"}})
    handler = build_videos_update_handler(wrapper=wrapper, oauth_token="local-oauth")

    result = handler(_valid_videos_update_arguments())

    assert result["endpoint"] == "videos.update"
    assert result["item"]["id"] == "abc123"
    assert len(wrapper.calls) == 1
    assert wrapper.calls[0]["arguments"] == {
        "part": "snippet",
        "body": {"id": "abc123", "snippet": {"title": "Updated title"}},
    }
    assert wrapper.calls[0]["auth_context"].mode is Layer1AuthMode.OAUTH_REQUIRED
    assert wrapper.calls[0]["auth_context"].credentials.oauth_token == "local-oauth"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "part"),
        ({"part": "", "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": 123, "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": "status", "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": "snippet,status", "body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "part"),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": {"snippet": {"title": "Updated"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": "", "snippet": {"title": "Updated"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": "abc123"}}, "body.snippet"),
        ({"part": "snippet", "body": {"id": "abc123", "snippet": {}}}, "body.snippet.title"),
        ({"part": "snippet", "body": {"id": "abc123", "snippet": {"title": ""}}}, "body.snippet.title"),
        ({"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}, "status": {}}}, "body.status"),
        (
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated", "description": "x"}}},
            "body.snippet.description",
        ),
        (
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}, "onBehalfOfContentOwner": ""},
            "onBehalfOfContentOwner",
        ),
    ],
)
def test_videos_update_validation_rejects_missing_invalid_and_unsupported_inputs(arguments, field):
    """Reject malformed update, read-only field, and delegation requests."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, validate_videos_update_arguments

    with pytest.raises(VideosUpdateToolError) as exc_info:
        validate_videos_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


@pytest.mark.parametrize(
    "field",
    [
        "media",
        "uploadMode",
        "videoCreation",
        "delete",
        "rating",
        "thumbnail",
        "caption",
        "playlist",
        "comment",
        "includeTranscript",
        "analytics",
        "recommend",
        "rankResults",
        "summarize",
        "enrich",
    ],
)
def test_videos_update_validation_rejects_out_of_scope_workflow_fields(field):
    """Reject upload, publishing, analytics, ranking, and enrichment fields."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, validate_videos_update_arguments

    with pytest.raises(VideosUpdateToolError) as exc_info:
        validate_videos_update_arguments(
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}, field: "value"}
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_videos_update_handler_rejects_missing_oauth_before_layer1_execution():
    """Surface missing OAuth without invoking the Layer 1 update wrapper."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, build_videos_update_handler

    wrapper = RecordingWrapper()
    handler = build_videos_update_handler(wrapper=wrapper, oauth_token=None)

    with pytest.raises(VideosUpdateToolError) as exc_info:
        handler(_valid_videos_update_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("forbidden", "authorization_failed"),
        ("policy_restricted", "authorization_failed"),
        ("rate_limit", "quota_exhausted"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("availability", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("transient", "upstream_failure"),
    ],
)
def test_videos_update_handler_maps_and_sanitizes_upstream_failures(upstream_category, expected_category):
    """Convert Layer 1 update failures into safe caller-facing categories."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, build_videos_update_handler

    wrapper = FailingWrapper(
        NormalizedUpstreamError(
            message="upstream failed",
            category=upstream_category,
            retryable=False,
            upstream_status=503,
            details={
                "authorization": "Bearer secret",
                "oauth_token": "hidden",
                "upstream_body": {"secret": "hidden"},
                "reason": "safe",
            },
        )
    )
    handler = build_videos_update_handler(wrapper=wrapper, oauth_token="local-oauth")

    with pytest.raises(VideosUpdateToolError) as exc_info:
        handler(_valid_videos_update_arguments())

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"reason": "safe"}
    assert "Bearer" not in str(exc_info.value.details)
