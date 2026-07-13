"""Unit tests for the Layer 2 ``search_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.search import (
    SearchListToolError,
    build_search_list_handler,
    map_search_list_result,
    validate_search_list_arguments,
)


def test_validate_search_list_accepts_supported_public_requests():
    """Accept supported public search request shapes."""
    cases = [
        {"part": "snippet", "q": "mcp server"},
        {"part": "snippet", "q": "mcp server", "type": "video"},
        {"part": "snippet", "q": "release notes", "channelId": "UC123"},
        {"part": "snippet", "q": "conference", "publishedAfter": "2026-01-01T00:00:00Z"},
        {"part": "snippet", "q": "conference", "regionCode": "US", "relevanceLanguage": "en"},
        {"part": "snippet", "q": "mcp server", "pageToken": "NEXT_PAGE", "maxResults": 25},
        {"part": "snippet", "q": "mcp server", "type": "video", "videoDuration": "short"},
    ]

    for case in cases:
        assert validate_search_list_arguments(case)["q"] == case["q"]


def test_validate_search_list_accepts_restricted_request():
    """Accept one restricted OAuth-backed selector."""
    normalized = validate_search_list_arguments({"part": "snippet", "q": "private uploads", "forMine": True})

    assert normalized["forMine"] is True


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"part": "snippet"}, "q"),
        ({"q": "mcp server"}, "part"),
        ({"part": "", "q": "mcp server"}, "part"),
        ({"part": "snippet", "q": ""}, "q"),
        ({"part": "snippet", "q": "mcp server", "includeTranscript": True}, "includeTranscript"),
        ({"part": "snippet", "q": "mcp server", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "q": "mcp server", "maxResults": 51}, "maxResults"),
        ({"part": "snippet", "q": "mcp server", "maxResults": "25"}, "maxResults"),
    ],
)
def test_validate_search_list_rejects_invalid_request_shapes(arguments, field):
    """Reject malformed or unsupported request shapes with field details."""
    with pytest.raises(SearchListToolError) as exc_info:
        validate_search_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == field


def test_validate_search_list_rejects_restricted_filter_conflicts():
    """Reject mutually exclusive restricted filters."""
    with pytest.raises(SearchListToolError) as exc_info:
        validate_search_list_arguments({"part": "snippet", "q": "mcp server", "forMine": True, "forDeveloper": True})

    assert exc_info.value.details["field"] == "restricted_filter"


def test_validate_search_list_rejects_video_filter_without_video_type():
    """Reject video-only filters unless ``type=video`` is selected."""
    with pytest.raises(SearchListToolError) as exc_info:
        validate_search_list_arguments({"part": "snippet", "q": "mcp server", "videoDuration": "short"})

    assert exc_info.value.details == {"field": "type", "required": "video"}


def test_map_search_list_result_preserves_safe_context_and_paging():
    """Map upstream search payloads to near-raw public results."""
    result = map_search_list_result(
        {
            "kind": "youtube#searchListResponse",
            "etag": "etag-search",
            "nextPageToken": "NEXT_PAGE",
            "items": [{"id": {"videoId": "abc123"}, "snippet": {"title": "Example"}}],
        },
        {"part": "snippet", "q": "mcp server", "type": "video", "pageToken": "PAGE_1", "maxResults": 25},
        auth_mode="api_key",
    )

    assert result["endpoint"] == "search.list"
    assert result["quotaCost"] == 100
    assert result["items"][0]["id"]["videoId"] == "abc123"
    assert result["empty"] is False
    assert result["queryContext"]["q"] == "mcp server"
    assert result["queryContext"]["type"] == "video"
    assert result["pagination"] == {"pageToken": "PAGE_1", "maxResults": 25, "nextPageToken": "NEXT_PAGE"}
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert "transcript" not in result


def test_map_search_list_result_preserves_empty_success():
    """Keep accessible empty search collections successful."""
    result = map_search_list_result({"items": [], "pageInfo": {"totalResults": 0}}, {"part": "snippet", "q": "empty"})

    assert result["items"] == []
    assert result["empty"] is True
    assert result["pageInfo"] == {"totalResults": 0}


def test_search_list_handler_selects_public_and_restricted_auth_paths():
    """Execute public and restricted calls with the correct Layer 1 auth mode."""

    class RecordingWrapper:
        """Record auth modes used for fake wrapper calls."""

        def __init__(self):
            """Initialize the fake wrapper call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Record one call and return a representative payload.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :return: Representative search result payload.
            """
            self.calls.append((arguments, auth_context))
            return {"items": [{"id": {"videoId": "abc123"}}]}

    wrapper = RecordingWrapper()
    handler = build_search_list_handler(wrapper=wrapper, api_key="public-key", oauth_token="oauth-token")

    public_result = handler({"part": "snippet", "q": "mcp server"})
    restricted_result = handler({"part": "snippet", "q": "private uploads", "forMine": True})

    assert public_result["auth"] == {"mode": "api_key", "path": "public"}
    assert restricted_result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert [call[1].mode.value for call in wrapper.calls] == ["api_key", "oauth_required"]
    assert all("token" not in str(result).lower() for result in (public_result, restricted_result))


def test_search_list_handler_rejects_missing_restricted_oauth_safely():
    """Reject restricted searches when OAuth access is unavailable."""
    handler = build_search_list_handler(oauth_token=None)

    with pytest.raises(SearchListToolError) as exc_info:
        handler({"part": "snippet", "q": "private uploads", "forMine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authPath": "restricted", "authMode": "oauth_required"}


def test_search_list_handler_maps_safe_upstream_failures():
    """Map upstream failures without leaking unsafe diagnostic details."""

    class FailingWrapper:
        """Raise one normalized quota failure during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a sanitized quota failure for handler mapping.

            :param executor: Executor supplied by the handler.
            :param arguments: Normalized arguments supplied by the handler.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError("quota", "quota", True, 429, {"api_key": "secret", "quota": "daily"})

    handler = build_search_list_handler(wrapper=FailingWrapper())

    with pytest.raises(SearchListToolError) as exc_info:
        handler({"part": "snippet", "q": "mcp server"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}
