"""Unit tests for normalized public video-detail behavior."""

import pytest


class RecordingLookup:
    """Record lower-level video lookups for focused video-detail tests.

    :param result: Result returned by the lookup call.
    """

    def __init__(self, result=None):
        """Initialize the call history and configured result.

        :param result: Result returned from each invocation.
        """
        self.result = result or {"items": []}
        self.calls = []

    def __call__(self, arguments):
        """Record arguments and return the configured result.

        :param arguments: Lower-level lookup arguments.
        :return: Configured lookup result.
        """
        self.calls.append(arguments)
        return self.result


class RecordingSearchLookup:
    """Record controlled Layer 2 search-list calls for video-search tests.

    :param result: Result returned from each invocation.
    """

    def __init__(self, result=None):
        """Initialize call history and one representative video-search result.

        :param result: Optional result returned from each invocation.
        """
        self.result = result or {
            "items": [
                {
                    "id": {"videoId": "video-1"},
                    "snippet": {
                        "title": "First result",
                        "description": "First description",
                        "publishedAt": "2026-01-15T12:00:00Z",
                        "channelId": "UC1",
                        "channelTitle": "First channel",
                        "thumbnails": {"medium": {"url": "https://example.invalid/first"}},
                    },
                },
                {
                    "id": {"videoId": "video-2"},
                    "snippet": {
                        "title": "Second result",
                        "publishedAt": "2026-01-14T12:00:00Z",
                        "channelId": "UC2",
                        "channelTitle": "Second channel",
                    },
                },
            ],
            "nextPageToken": "NEXT_PAGE",
        }
        self.calls = []

    def __call__(self, arguments):
        """Record arguments and return the configured Layer 2 result.

        :param arguments: Validated lower-layer search arguments.
        :return: Configured public Layer 2 search result.
        """
        self.calls.append(arguments)
        return self.result


def test_video_details_requires_a_nonblank_video_identifier():
    """Reject missing, blank, and non-text video identifiers before lookup."""
    from mcp_server.tools.youtube_composed.videos import VideosGetVideoToolError, validate_videos_get_video_arguments

    for arguments in ({}, {"videoId": " "}, {"videoId": 123}):
        with pytest.raises(VideosGetVideoToolError) as exc_info:
            validate_videos_get_video_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": "videoId"}


def test_video_details_uses_one_core_lookup_and_normalizes_default_fields():
    """Map one lower-level item into the documented default result shape."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_handler

    lookup = RecordingLookup(
        {
            "items": [
                {
                    "id": "abc123",
                    "snippet": {
                        "title": "Example video",
                        "description": "Example description",
                        "publishedAt": "2026-01-15T12:00:00Z",
                        "channelId": "UC123",
                        "channelTitle": "Example Channel",
                        "tags": ["example"],
                        "thumbnails": {"default": {"url": "https://example.invalid/thumb.jpg"}},
                    },
                    "contentDetails": {"duration": "PT12M33S"},
                }
            ]
        }
    )

    result = build_videos_get_video_handler(lookup=lookup)({"videoId": "abc123"})

    assert lookup.calls == [{"id": "abc123", "part": "snippet,contentDetails"}]
    assert result == {
        "videoId": "abc123",
        "title": "Example video",
        "description": "Example description",
        "publishedAt": "2026-01-15T12:00:00Z",
        "channelId": "UC123",
        "channelTitle": "Example Channel",
        "duration": "PT12M33S",
        "tags": ["example"],
        "thumbnails": {"default": {"url": "https://example.invalid/thumb.jpg"}},
    }


def test_video_details_validates_optional_parts_and_unions_them_with_core_parts():
    """Require valid unique groups and include requested groups in one lookup."""
    from mcp_server.tools.youtube_composed.videos import (
        VideosGetVideoToolError,
        build_videos_get_video_handler,
        validate_videos_get_video_arguments,
    )

    for parts in ("statistics", ["statistics", "statistics"], ["unknown"], [123]):
        with pytest.raises(VideosGetVideoToolError) as exc_info:
            validate_videos_get_video_arguments({"videoId": "abc123", "parts": parts})

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": "parts"}

    lookup = RecordingLookup(
        {
            "items": [
                {
                    "id": "abc123",
                    "snippet": {"title": "Example video"},
                    "contentDetails": {},
                    "statistics": {"viewCount": "1000"},
                    "status": {"privacyStatus": "public"},
                }
            ]
        }
    )

    result = build_videos_get_video_handler(lookup=lookup)({"videoId": "abc123", "parts": ["statistics", "status"]})

    assert lookup.calls == [{"id": "abc123", "part": "snippet,contentDetails,statistics,status"}]
    assert result["statistics"] == {"viewCount": "1000"}
    assert result["status"] == {"privacyStatus": "public"}


def test_video_details_treats_an_empty_optional_part_list_as_the_default_shape():
    """Treat an empty part selection the same as an omitted selection."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_handler

    lookup = RecordingLookup({"items": [{"id": "abc123", "snippet": {"title": "Example video"}}]})

    result = build_videos_get_video_handler(lookup=lookup)({"videoId": "abc123", "parts": []})

    assert lookup.calls == [{"id": "abc123", "part": "snippet,contentDetails"}]
    assert result == {"videoId": "abc123", "title": "Example video"}


@pytest.mark.parametrize(
    ("lower_category", "expected_category"),
    [
        ("resource_not_found", "unavailable_resource"),
        ("authorization_failed", "authorization_sensitive_data"),
        ("quota_exhausted", "quota_exhaustion"),
        ("endpoint_unavailable", "upstream_failure"),
    ],
)
def test_video_details_translates_lower_lookup_failures_safely(lower_category, expected_category):
    """Map lower lookup failures to the public safe error taxonomy."""
    from mcp_server.tools.youtube_common.videos import VideosListToolError
    from mcp_server.tools.youtube_composed.videos import VideosGetVideoToolError, build_videos_get_video_handler

    def failing_lookup(_arguments):
        """Raise an error containing details unsafe for public exposure.

        :param _arguments: Ignored lower-level lookup arguments.
        :raises VideosListToolError: Always raised for public error mapping.
        """
        raise VideosListToolError(
            "source failure",
            category=lower_category,
            details={"reason": "source failure", "oauth_token": "secret", "stack_trace": "hidden"},
        )

    with pytest.raises(VideosGetVideoToolError) as exc_info:
        build_videos_get_video_handler(lookup=failing_lookup)({"videoId": "abc123"})

    assert exc_info.value.category == expected_category
    expected_details = {"resource": "video"} if expected_category == "unavailable_resource" else {"reason": "source failure"}
    assert exc_info.value.details == expected_details


def test_video_details_empty_lookup_hides_the_specific_availability_reason():
    """Return one generic unavailable outcome for an empty item collection."""
    from mcp_server.tools.youtube_composed.videos import VideosGetVideoToolError, build_videos_get_video_handler

    with pytest.raises(VideosGetVideoToolError) as exc_info:
        build_videos_get_video_handler(lookup=RecordingLookup({"items": []}))({"videoId": "abc123"})

    assert exc_info.value.category == "unavailable_resource"
    assert exc_info.value.details == {"resource": "video"}
    assert "private" not in str(exc_info.value).lower()


def test_video_search_validates_public_arguments_and_normalizes_defaults():
    """Reject invalid public search arguments and normalize valid defaults."""
    from mcp_server.tools.youtube_composed.videos import VideosSearchVideosToolError, validate_videos_search_videos_arguments

    for arguments, field in (
        ({}, "query"),
        ({"query": " "}, "query"),
        ({"query": "valid", "maxResults": True}, "maxResults"),
        ({"query": "valid", "maxResults": 51}, "maxResults"),
        ({"query": "valid", "order": "unknown"}, "order"),
        ({"query": "valid", "publishedAfter": "2026-01-01"}, "publishedAfter"),
        ({"query": "valid", "publishedAfter": "2026-02-01T00:00:00Z", "publishedBefore": "2026-01-01T00:00:00Z"}, "publishedAfter"),
        ({"query": "valid", "unexpected": True}, "unexpected"),
    ):
        with pytest.raises(VideosSearchVideosToolError) as exc_info:
            validate_videos_search_videos_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details["field"] == field

    assert validate_videos_search_videos_arguments({"query": "  climate tools  "}) == {
        "query": "climate tools",
        "maxResults": 10,
        "order": "relevance",
        "uniqueChannels": False,
        "creatorOnly": False,
        "sortBy": "relevance",
    }


def test_video_search_maps_base_request_and_normalizes_bounded_results():
    """Map public query constraints into one video-only base search."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup()
    result = build_videos_search_videos_handler(search=search)(
        {
            "query": "climate tools",
            "maxResults": 1,
            "order": "date",
            "publishedAfter": "2026-01-01T00:00:00Z",
            "publishedBefore": "2026-01-31T00:00:00Z",
            "channelId": "UC1",
        }
    )

    assert search.calls == [
        {
            "part": "snippet",
            "q": "climate tools",
            "type": "video",
            "maxResults": 1,
            "order": "date",
            "publishedAfter": "2026-01-01T00:00:00Z",
            "publishedBefore": "2026-01-31T00:00:00Z",
            "channelId": "UC1",
        }
    ]
    assert result["items"] == [
        {
            "videoId": "video-1",
            "title": "First result",
            "description": "First description",
            "publishedAt": "2026-01-15T12:00:00Z",
            "channelId": "UC1",
            "channelTitle": "First channel",
            "thumbnails": {"medium": {"url": "https://example.invalid/first"}},
        }
    ]
    assert result["appliedInputs"]["sortBy"] == "relevance"
    assert result["returnedCount"] == 1
    assert result["maxResults"] == 1
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["fieldProvenance"]["videoId"] == "raw_upstream"


def test_video_search_returns_empty_success_and_sanitizes_search_errors():
    """Keep empty search success distinct from safe lower-layer failure."""
    from mcp_server.tools.youtube_common.search import SearchListToolError
    from mcp_server.tools.youtube_composed.videos import VideosSearchVideosToolError, build_videos_search_videos_handler

    assert build_videos_search_videos_handler(search=RecordingSearchLookup({"items": []}))({"query": "none"})["items"] == []

    def failing_search(_arguments):
        """Raise one lower-layer quota error with unsafe diagnostics.

        :param _arguments: Ignored lower-layer arguments.
        :raises SearchListToolError: Always raised for the test.
        """
        raise SearchListToolError(
            "quota failure",
            category="quota_exhausted",
            details={"reason": "quota", "api_key": "hidden", "stack_trace": "hidden"},
        )

    with pytest.raises(VideosSearchVideosToolError) as exc_info:
        build_videos_search_videos_handler(search=failing_search)({"query": "valid"})

    assert exc_info.value.category == "quota_exhaustion"
    assert exc_info.value.details == {"reason": "quota"}


def test_video_search_filters_enriched_channels_and_keeps_one_ranked_video_per_channel():
    """Apply subscriber and creator filters with explicit unique-channel output."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup(
        {
            "items": [
                {"id": {"videoId": "video-1"}, "snippet": {"title": "First", "channelId": "UC1", "channelTitle": "Creator Alex"}},
                {"id": {"videoId": "video-2"}, "snippet": {"title": "Second", "channelId": "UC1", "channelTitle": "Creator Alex"}},
                {"id": {"videoId": "video-3"}, "snippet": {"title": "Third", "channelId": "UC2", "channelTitle": "Large Brand"}},
            ]
        }
    )
    channels = RecordingSearchLookup(
        {
            "items": [
                {"id": "UC1", "snippet": {"title": "Creator Alex", "description": "Independent creator videos"}, "statistics": {"subscriberCount": "25"}},
                {"id": "UC2", "snippet": {"title": "Large Brand"}, "statistics": {"subscriberCount": "5000"}},
            ]
        }
    )

    result = build_videos_search_videos_handler(search=search, channels=channels)(
        {"query": "tools", "channelMinSubscribers": 10, "channelMaxSubscribers": 100, "creatorOnly": True, "uniqueChannels": True}
    )

    assert channels.calls == [{"part": "snippet,statistics,contentDetails", "id": "UC1,UC2"}]
    assert [item["videoId"] for item in result["items"]] == ["video-1"]
    assert result["items"][0]["channel"] == {
        "subscriberCount": "25",
        "creatorClassification": "creator",
        "creatorSignals": ["public_creator_term"],
    }


def test_video_search_uses_latest_activity_only_when_requested_and_discloses_partial_data():
    """Filter by conditional latest activity and disclose excluded missing metadata."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup(
        {
            "items": [
                {"id": {"videoId": "video-1"}, "snippet": {"title": "First", "channelId": "UC1"}},
                {"id": {"videoId": "video-2"}, "snippet": {"title": "Second", "channelId": "UC2"}},
            ]
        }
    )
    channels = RecordingSearchLookup({"items": [{"id": "UC1", "statistics": {"subscriberCount": "10"}}, {"id": "UC2", "statistics": {"subscriberCount": "20"}}]})
    activity_calls = []

    def latest_activity(channel_id):
        """Return activity for one channel and omit it for the second channel.

        :param channel_id: Candidate public channel identifier.
        :return: Latest public upload timestamp or ``None``.
        """
        activity_calls.append(channel_id)
        return {"UC1": "2026-01-20T00:00:00Z", "UC2": None}[channel_id]

    result = build_videos_search_videos_handler(search=search, channels=channels, latest_activity=latest_activity)(
        {"query": "tools", "channelLastUploadAfter": "2026-01-01T00:00:00Z"}
    )

    assert activity_calls == ["UC1", "UC2"]
    assert [item["videoId"] for item in result["items"]] == ["video-1"]
    assert result["items"][0]["channel"]["latestVideoPublishedAt"] == "2026-01-20T00:00:00Z"
    assert result["partialEnrichment"] == {
        "status": "partial",
        "excludedCandidateCount": 1,
        "reasons": ["latest_activity_unavailable"],
        "requiredFor": ["channelLastUploadAfter"],
    }


def test_video_search_derives_requested_latest_activity_from_public_uploads_playlists():
    """Use the enriched public uploads playlist only for a latest-activity rule."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup({"items": [{"id": {"videoId": "video-1"}, "snippet": {"title": "First", "channelId": "UC1"}}]})
    channels = RecordingSearchLookup(
        {
            "items": [
                {
                    "id": "UC1",
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU1"}},
                    "statistics": {"subscriberCount": "10"},
                }
            ]
        }
    )
    playlist_items = RecordingSearchLookup(
        {"items": [{"contentDetails": {"videoPublishedAt": "2026-01-20T00:00:00Z"}}]}
    )

    result = build_videos_search_videos_handler(search=search, channels=channels, playlist_items=playlist_items)(
        {"query": "tools", "channelLastUploadAfter": "2026-01-01T00:00:00Z"}
    )

    assert playlist_items.calls == [{"part": "contentDetails", "playlistId": "UU1", "maxResults": 1}]
    assert result["items"][0]["channel"]["latestVideoPublishedAt"] == "2026-01-20T00:00:00Z"


def test_video_search_fails_safely_when_all_required_enrichment_is_unavailable():
    """Return partial-enrichment failure instead of unfiltered candidates."""
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_composed.videos import VideosSearchVideosToolError, build_videos_search_videos_handler

    def unavailable_channels(_arguments):
        """Raise a safe lower-layer failure for all requested channel metadata.

        :param _arguments: Ignored batched channel lookup arguments.
        :raises ChannelsListToolError: Always raised for the test.
        """
        raise ChannelsListToolError("metadata unavailable", category="endpoint_unavailable", details={"api_key": "hidden"})

    with pytest.raises(VideosSearchVideosToolError) as exc_info:
        build_videos_search_videos_handler(search=RecordingSearchLookup(), channels=unavailable_channels)(
            {"query": "tools", "channelMinSubscribers": 1}
        )

    assert exc_info.value.category == "partial_enrichment_failure"
    assert exc_info.value.details == {"requiredFor": ["channelMinSubscribers"]}


def test_video_search_ranks_filtered_candidates_stably_before_unique_channel_selection():
    """Rank every documented mode before applying one-result-per-channel output.

    The controlled candidates also prove that a subscriber filter runs before
    ranking and that the final cap is applied only after ranking and de-duplication.
    """
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup(
        {
            "items": [
                {"id": {"videoId": "one-first"}, "snippet": {"title": "First", "channelId": "UC1"}},
                {"id": {"videoId": "two"}, "snippet": {"title": "Second", "channelId": "UC2"}},
                {"id": {"videoId": "one-second"}, "snippet": {"title": "Third", "channelId": "UC1"}},
                {"id": {"videoId": "three"}, "snippet": {"title": "Fourth", "channelId": "UC3"}},
            ]
        }
    )
    channels = RecordingSearchLookup(
        {
            "items": [
                {"id": "UC1", "snippet": {"title": "Creator One"}, "statistics": {"subscriberCount": "100"}},
                {"id": "UC2", "snippet": {"title": "Creator Two"}, "statistics": {"subscriberCount": "10"}},
                {"id": "UC3", "snippet": {"title": "Studio Three"}, "statistics": {"subscriberCount": "50"}},
            ]
        }
    )

    def latest_activity(channel_id):
        """Return deterministic activity timestamps for ranking coverage.

        :param channel_id: Candidate public channel identifier.
        :return: Timezone-aware latest-public-upload timestamp.
        """
        return {"UC1": "2026-01-02T00:00:00Z", "UC2": "2026-01-03T00:00:00Z", "UC3": "2026-01-01T00:00:00Z"}[channel_id]

    handler = build_videos_search_videos_handler(search=search, channels=channels, latest_activity=latest_activity)

    assert [item["videoId"] for item in handler({"query": "tools"})["items"]] == ["one-first", "two", "one-second", "three"]
    assert [item["videoId"] for item in handler({"query": "tools", "sortBy": "subscribers_asc"})["items"]] == ["two", "three", "one-first", "one-second"]
    assert [item["videoId"] for item in handler({"query": "tools", "sortBy": "subscribers_desc"})["items"]] == ["one-first", "one-second", "three", "two"]
    assert [item["videoId"] for item in handler({"query": "tools", "sortBy": "indie_priority"})["items"]] == ["two", "one-first", "one-second", "three"]
    assert [item["videoId"] for item in handler({"query": "tools", "sortBy": "recent_activity"})["items"]] == ["two", "one-first", "one-second", "three"]
    assert [item["videoId"] for item in handler({"query": "tools", "sortBy": "subscribers_asc", "uniqueChannels": True, "maxResults": 1})["items"]] == ["two"]
    assert [item["videoId"] for item in handler({"query": "tools", "channelMaxSubscribers": 50, "sortBy": "subscribers_desc"})["items"]] == ["three", "two"]


def test_video_search_excludes_unavailable_ranking_values_with_partial_disclosure():
    """Never rank a channel when its selected subscriber datum is unavailable."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_handler

    search = RecordingSearchLookup(
        {"items": [{"id": {"videoId": "known"}, "snippet": {"title": "Known", "channelId": "UC1"}}, {"id": {"videoId": "hidden"}, "snippet": {"title": "Hidden", "channelId": "UC2"}}]}
    )
    channels = RecordingSearchLookup(
        {"items": [{"id": "UC1", "statistics": {"subscriberCount": "10"}}, {"id": "UC2", "statistics": {}}]}
    )

    result = build_videos_search_videos_handler(search=search, channels=channels)(
        {"query": "tools", "sortBy": "subscribers_asc"}
    )

    assert [item["videoId"] for item in result["items"]] == ["known"]
    assert result["partialEnrichment"]["reasons"] == ["subscriber_count_unavailable"]
