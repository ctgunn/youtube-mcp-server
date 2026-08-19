"""Unit tests for normalized public playlist-detail behavior."""

import pytest


class RecordingPlaylistLookup:
    """Record direct playlist lookups for composed playlist-detail tests.

    :param result: Result returned by the lookup call.
    """

    def __init__(self, result=None):
        """Initialize the configured result and request history.

        :param result: Optional lower-level playlist-list payload.
        """
        self.result = result if result is not None else {"items": []}
        self.calls = []

    def __call__(self, arguments):
        """Record one lower-level request and return the configured payload.

        :param arguments: Validated lower-level playlist-list request.
        :return: Configured lower-level result.
        """
        self.calls.append(arguments)
        return self.result


class RecordingPlaylistItemsLookup:
    """Record playlist-item listing calls for composed playlist-item tests.

    :param result: Result returned by the controlled lower-layer listing.
    """

    def __init__(self, result=None):
        """Initialize the configured listing result and call history.

        :param result: Optional lower-layer playlist-item payload.
        """
        self.result = result if result is not None else {"items": []}
        self.calls = []

    def __call__(self, arguments):
        """Record one lower-layer listing request and return its configured result.

        :param arguments: Validated playlist-item listing arguments.
        :return: Configured lower-layer listing result.
        """
        self.calls.append(arguments)
        return self.result


class RecordingTimestampedCaptions:
    """Record timestamped-caption requests for playlist fan-out tests.

    :param responses: Mapping from video identifier to result or raised error.
    """

    def __init__(self, responses):
        """Initialize controlled transcript responses and request history.

        :param responses: Mapping from video identifier to result or raised error.
        """
        self.responses = responses
        self.calls = []

    def __call__(self, arguments):
        """Record one transcript request and return its configured response.

        :param arguments: Validated timestamped-caption request.
        :return: Configured result for the requested video.
        :raises ValueError: Re-raises the configured controlled error.
        """
        self.calls.append(arguments)
        response = self.responses[arguments["videoId"]]
        if isinstance(response, BaseException):
            raise response
        return response


class PagingPlaylistItemsLookup:
    """Return controlled playlist-item pages and record their private cursors.

    :param pages: Mapping of a requested page token to its lower-layer payload.
    """

    def __init__(self, pages):
        """Initialize the controlled page mapping and request history.

        :param pages: Mapping keyed by ``None`` for the first page and later tokens.
        """
        self.pages = pages
        self.calls = []

    def __call__(self, arguments):
        """Record one playlist-item request and return its configured page.

        :param arguments: Validated lower-layer playlist-item listing arguments.
        :return: Configured page matching the requested private continuation token.
        """
        self.calls.append(arguments)
        return self.pages[arguments.get("pageToken")]


def _playlist_payload():
    """Return one complete public playlist item payload.

    :return: Lower-level playlist-list result containing one public item.
    """
    return {
        "items": [
            {
                "id": "PL123",
                "snippet": {
                    "title": "Example research playlist",
                    "description": "Public collection",
                    "channelId": "UC123",
                    "channelTitle": "Example Channel",
                    "publishedAt": "2026-01-15T12:00:00Z",
                    "thumbnails": {"default": {"url": "https://example.invalid/thumbnail.jpg"}},
                },
                "contentDetails": {"itemCount": 12},
                "status": {"privacyStatus": "public"},
            }
        ]
    }


def test_playlist_details_validates_one_trimmed_identifier_and_rejects_unknown_fields():
    """Require exactly one nonblank public playlist identifier.

    :return: ``None`` after validating the public input boundary.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetPlaylistToolError,
        validate_playlists_get_playlist_arguments,
    )

    assert validate_playlists_get_playlist_arguments({"playlistId": " PL123 "}) == {"playlistId": "PL123"}
    for arguments, field in (
        ({}, "playlistId"),
        ({"playlistId": " "}, "playlistId"),
        ({"playlistId": 3}, "playlistId"),
        ({"playlistId": "PL123", "part": "snippet"}, "part"),
        ([], "arguments"),
    ):
        with pytest.raises(PlaylistsGetPlaylistToolError) as exc_info:
            validate_playlists_get_playlist_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": field}


def test_playlist_details_uses_one_lookup_and_normalizes_available_public_fields():
    """Map one lower-level playlist item into the documented result shape.

    :return: ``None`` after asserting exact request and result behavior.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_get_playlist_handler,
    )

    lookup = RecordingPlaylistLookup(_playlist_payload())

    result = build_playlists_get_playlist_handler(lookup=lookup)({"playlistId": " PL123 "})

    assert lookup.calls == [{"part": "snippet,contentDetails,status", "id": "PL123"}]
    assert result == {
        "playlistId": "PL123",
        "title": "Example research playlist",
        "description": "Public collection",
        "channelId": "UC123",
        "channelTitle": "Example Channel",
        "publishedAt": "2026-01-15T12:00:00Z",
        "thumbnails": {"default": {"url": "https://example.invalid/thumbnail.jpg"}},
        "privacyStatus": "public",
        "itemCount": 12,
        "fieldProvenance": {
            "playlistId": "raw_upstream",
            "title": "normalized",
            "description": "normalized",
            "channelId": "normalized",
            "channelTitle": "normalized",
            "publishedAt": "normalized",
            "thumbnails": "normalized",
            "privacyStatus": "normalized",
            "itemCount": "normalized",
            "contentScope": "normalized",
        },
        "contentScope": {
            "playlistItemsIncluded": False,
            "playlistItemsTool": "playlists_getPlaylistItems",
            "stateObservedAtRequest": True,
        },
    }


def test_playlist_details_omits_sparse_optional_metadata_without_fabrication():
    """Keep a successful playlist detail sparse when source values are absent.

    :return: ``None`` after asserting absent values are not synthesized.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_get_playlist_handler,
    )

    result = build_playlists_get_playlist_handler(
        lookup=RecordingPlaylistLookup({"items": [{"id": "PL123", "snippet": {}, "contentDetails": {}, "status": {}}]})
    )({"playlistId": "PL123"})

    assert result["playlistId"] == "PL123"
    assert result["fieldProvenance"] == {"playlistId": "raw_upstream", "contentScope": "normalized"}
    assert result["contentScope"]["playlistItemsIncluded"] is False
    for field in ("title", "description", "channelId", "channelTitle", "publishedAt", "thumbnails", "privacyStatus", "itemCount"):
        assert field not in result


def test_playlist_details_maps_empty_or_malformed_results_to_generic_unavailability():
    """Return one safe unavailable outcome for unusable direct lookup results.

    :return: ``None`` after asserting unavailable results do not reveal cause.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetPlaylistToolError,
        build_playlists_get_playlist_handler,
    )

    for payload in ({"items": []}, {"items": [None]}, {"items": "invalid"}, {}):
        with pytest.raises(PlaylistsGetPlaylistToolError) as exc_info:
            build_playlists_get_playlist_handler(lookup=RecordingPlaylistLookup(payload))({"playlistId": "PL123"})

        assert exc_info.value.category == "unavailable_resource"
        assert exc_info.value.details == {"resource": "playlist"}
        assert "private" not in str(exc_info.value).lower()


@pytest.mark.parametrize(
    ("lower_category", "expected_category"),
    [
        ("resource_not_found", "unavailable_resource"),
        ("invalid_request", "invalid_parameters"),
        ("authentication_failed", "authorization_sensitive_data"),
        ("authorization_failed", "authorization_sensitive_data"),
        ("quota_exhausted", "quota_exhaustion"),
        ("endpoint_unavailable", "upstream_failure"),
    ],
)
def test_playlist_details_translates_lower_errors_without_sensitive_details(lower_category, expected_category):
    """Map lower-layer failures to the documented safe public taxonomy.

    :param lower_category: Controlled lower-layer category.
    :param expected_category: Required public category.
    :return: ``None`` after asserting sanitized error translation.
    """
    from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetPlaylistToolError,
        build_playlists_get_playlist_handler,
    )

    def failing_lookup(_arguments):
        """Raise the configured safe lower-layer failure.

        :param _arguments: Ignored lower-layer arguments.
        :raises PlaylistsListToolError: Always raised for error-mapping coverage.
        """
        raise PlaylistsListToolError(
            "hidden lower-layer failure",
            category=lower_category,
            details={"reason": "safe reason", "api_key": "secret", "raw_body": "hidden"},
        )

    with pytest.raises(PlaylistsGetPlaylistToolError) as exc_info:
        build_playlists_get_playlist_handler(lookup=failing_lookup)({"playlistId": "PL123"})

    assert exc_info.value.category == expected_category
    assert "secret" not in str(exc_info.value.details)
    assert "hidden" not in str(exc_info.value.details)
    if expected_category == "unavailable_resource":
        assert exc_info.value.details == {"resource": "playlist"}
    else:
        assert exc_info.value.details == {"reason": "safe reason"}


def _playlist_items_payload():
    """Return a complete ordered lower-layer playlist-item response.

    :return: Public playlist-item result with one available and one unavailable entry.
    """
    return {
        "items": [
            {
                "id": "playlist-item-1",
                "snippet": {
                    "position": 0,
                    "resourceId": {"videoId": "video-1"},
                    "title": "First video",
                    "channelId": "UC1",
                    "channelTitle": "First channel",
                    "publishedAt": "2026-01-01T00:00:00Z",
                },
                "contentDetails": {"videoId": "video-1"},
                "status": {"privacyStatus": "public"},
            },
            {
                "id": "playlist-item-2",
                "snippet": {"position": 1},
                "contentDetails": {},
                "status": {"privacyStatus": "private"},
            },
        ],
        "nextPageToken": "next-page",
    }


def test_playlist_items_validate_and_apply_default_limit_before_one_listing():
    """Validate public playlist input and make one default-bounded listing.

    :return: ``None`` after validating arguments and one lower-layer request.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetPlaylistItemsToolError,
        build_playlists_get_playlist_items_handler,
        validate_playlists_get_playlist_items_arguments,
    )

    assert validate_playlists_get_playlist_items_arguments({"playlistId": " PL123 "}) == {
        "playlistId": "PL123",
        "maxResults": 25,
    }
    lookup = RecordingPlaylistItemsLookup(_playlist_items_payload())
    result = build_playlists_get_playlist_items_handler(playlist_items=lookup)({"playlistId": " PL123 "})

    assert lookup.calls == [{"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 25}]
    assert result["playlistId"] == "PL123"
    assert result["returnedCount"] == 2
    assert result["appliedLimit"] == 25
    assert result["isLimited"] is True
    for arguments, field in (
        ({}, "playlistId"),
        ({"playlistId": " "}, "playlistId"),
        ({"playlistId": 3}, "playlistId"),
        ({"playlistId": "PL123", "pageToken": "next"}, "pageToken"),
        ({"playlistId": "PL123", "maxResults": 0}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": 51}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": True}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": 1.5}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": "25"}, "maxResults"),
        ([], "arguments"),
    ):
        with pytest.raises(PlaylistsGetPlaylistItemsToolError) as exc_info:
            validate_playlists_get_playlist_items_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": field}


def test_playlist_items_honor_bounds_and_normalize_ordered_available_and_unavailable_entries():
    """Normalize every exposed playlist item without changing source order.

    :return: ``None`` after asserting bounds, item mapping, and availability states.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_get_playlist_items_handler,
    )

    lookup = RecordingPlaylistItemsLookup(_playlist_items_payload())
    result = build_playlists_get_playlist_items_handler(playlist_items=lookup)(
        {"playlistId": "PL123", "maxResults": 50}
    )

    assert lookup.calls == [{"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 50}]
    assert result["items"] == [
        {
            "position": 0,
            "playlistItemId": "playlist-item-1",
            "videoId": "video-1",
            "title": "First video",
            "channelId": "UC1",
            "channelTitle": "First channel",
            "publishedAt": "2026-01-01T00:00:00Z",
            "availabilityState": "available",
        },
        {"position": 1, "playlistItemId": "playlist-item-2", "availabilityState": "unavailable"},
    ]
    assert result["fieldProvenance"] == {
        "items.position": "raw_upstream",
        "items.playlistItemId": "raw_upstream",
        "items.videoId": "raw_upstream",
        "items.title": "raw_upstream",
        "items.channelId": "raw_upstream",
        "items.channelTitle": "raw_upstream",
        "items.publishedAt": "raw_upstream",
        "items.availabilityState": "normalized",
        "playlistId": "normalized",
        "returnedCount": "normalized",
        "appliedLimit": "normalized",
        "isLimited": "normalized",
        "collectionContext": "normalized",
    }
    assert result["collectionContext"] == {
        "source": "playlist_items",
        "ordering": "source_playlist_order_at_request_time",
        "rankingApplied": False,
        "paginationTraversed": False,
        "publicContentOnly": True,
        "requestTimeVariability": "playlist_can_change",
    }


def test_playlist_items_return_successful_empty_collection_and_map_safe_errors():
    """Keep empty success distinct from sanitized whole-request failures.

    :return: ``None`` after validating empty and error outcomes.
    """
    from mcp_server.tools.youtube_common.playlist_items import (
        PlaylistItemsListToolError,
    )
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetPlaylistItemsToolError,
        build_playlists_get_playlist_items_handler,
    )

    empty = build_playlists_get_playlist_items_handler(playlist_items=RecordingPlaylistItemsLookup({"items": []}))(
        {"playlistId": "PL123", "maxResults": 1}
    )
    assert empty["items"] == []
    assert empty["returnedCount"] == 0
    assert empty["isLimited"] is False

    expected_categories = {
        "resource_not_found": "unavailable_resource",
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
        "endpoint_unavailable": "upstream_failure",
    }
    for lower_category, expected_category in expected_categories.items():
        def failing_lookup(_arguments, category=lower_category):
            """Raise one controlled lower-layer error for mapping coverage.

            :param _arguments: Ignored lower-layer request.
            :param category: Configured lower-layer error category.
            :raises PlaylistItemsListToolError: Always raised for public error coverage.
            """
            raise PlaylistItemsListToolError(
                "hidden lower-layer failure",
                category=category,
                details={"reason": "safe reason", "api_key": "secret", "raw_body": "hidden"},
            )

        with pytest.raises(PlaylistsGetPlaylistItemsToolError) as exc_info:
            build_playlists_get_playlist_items_handler(playlist_items=failing_lookup)({"playlistId": "PL123"})

        assert exc_info.value.category == expected_category
        assert "secret" not in str(exc_info.value.details)
        assert "hidden" not in str(exc_info.value.details)


def _playlist_search_item(position, *, title="", description="", channel_title="", video_id="", privacy="public"):
    """Build one controlled source playlist item for search tests.

    :param position: Source playlist position for the item.
    :param title: Exposed item title.
    :param description: Exposed item description.
    :param channel_title: Exposed channel title.
    :param video_id: Exposed video identifier.
    :param privacy: Source availability signal.
    :return: One lower-layer playlist item with only the configured values.
    """
    snippet = {"position": position}
    if title:
        snippet["title"] = title
    if description:
        snippet["description"] = description
    if channel_title:
        snippet["channelTitle"] = channel_title
    if video_id:
        snippet["resourceId"] = {"videoId": video_id}
    return {
        "id": f"playlist-item-{position}",
        "snippet": snippet,
        "contentDetails": {"videoId": video_id} if video_id else {},
        "status": {"privacyStatus": privacy},
    }


def test_playlist_search_validates_and_returns_literal_source_ordered_matches():
    """Search exposed playlist fields with normalized literal matching.

    :return: ``None`` after validating search inputs, matching fields, and source order.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsSearchItemsToolError,
        build_playlists_search_items_handler,
        validate_playlists_search_items_arguments,
    )

    assert validate_playlists_search_items_arguments({"playlistId": " PL123 ", "query": "  Climate   Science "}) == {
        "playlistId": "PL123",
        "query": "Climate Science",
        "maxResults": 25,
    }
    for arguments, field in (
        ({"playlistId": "PL123"}, "query"),
        ({"playlistId": "PL123", "query": " "}, "query"),
        ({"playlistId": "PL123", "query": 5}, "query"),
        ({"playlistId": "PL123", "query": "science", "extra": True}, "extra"),
        ({"playlistId": "PL123", "query": "science", "maxResults": 51}, "maxResults"),
    ):
        with pytest.raises(PlaylistsSearchItemsToolError) as exc_info:
            validate_playlists_search_items_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": field}

    playlist_lookup = RecordingPlaylistLookup(_playlist_payload())
    item_lookup = PagingPlaylistItemsLookup(
        {
            None: {
                "items": [
                    _playlist_search_item(0, description="Climate Science primer", video_id="one"),
                    _playlist_search_item(1, channel_title="SCIENCE Studio", video_id="two"),
                    _playlist_search_item(2, title="Unrelated", video_id="climate-science-3"),
                    _playlist_search_item(3, title="No match", video_id="four"),
                ]
            }
        }
    )

    result = build_playlists_search_items_handler(playlists=playlist_lookup, playlist_items=item_lookup)(
        {"playlistId": " PL123 ", "query": " science "}
    )

    assert playlist_lookup.calls == [{"part": "snippet,contentDetails,status", "id": "PL123"}]
    assert item_lookup.calls == [{"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 50}]
    assert [item["position"] for item in result["items"]] == [0, 1, 2]
    assert [item["matchingFields"] for item in result["items"]] == [["description"], ["channelTitle"], ["videoId"]]
    assert result["query"] == "science"
    assert result["searchCoverage"] == {
        "inspectedEntryCount": 4,
        "isComplete": True,
        "terminationReason": "end_of_playlist",
    }
    assert result["additionalMatchesOmitted"] is False


def test_playlist_search_limits_results_and_reports_private_pagination_coverage():
    """Bound returned matches while preserving honest multi-page coverage state.

    :return: ``None`` after validating limits, omission, and inspection-cap behavior.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_search_items_handler,
    )

    lookup = PagingPlaylistItemsLookup(
        {
            None: {
                "items": [_playlist_search_item(index, title="Needle", video_id=f"video-{index}") for index in range(3)]
            }
        }
    )
    limited = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()), playlist_items=lookup
    )({"playlistId": "PL123", "query": "needle", "maxResults": 2})

    assert limited["returnedCount"] == 2
    assert limited["appliedLimit"] == 2
    assert limited["additionalMatchesOmitted"] is True

    pages = {}
    for page_index in range(10):
        token = None if page_index == 0 else f"page-{page_index}"
        next_token = f"page-{page_index + 1}"
        pages[token] = {
            "items": [
                _playlist_search_item(page_index * 50 + item_index, title="Other", video_id=f"v-{page_index}-{item_index}")
                for item_index in range(50)
            ],
            "nextPageToken": next_token,
        }
    capped_lookup = PagingPlaylistItemsLookup(pages)
    capped = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()), playlist_items=capped_lookup
    )({"playlistId": "PL123", "query": "needle"})

    assert len(capped_lookup.calls) == 10
    assert capped["items"] == []
    assert capped["searchCoverage"] == {
        "inspectedEntryCount": 500,
        "isComplete": False,
        "terminationReason": "inspection_cap",
    }
    assert capped["additionalMatchesOmitted"] is None
    assert "page-10" not in str(capped)


def test_playlist_search_completes_multi_page_results_and_accessible_empty_playlists():
    """Preserve order across terminal pages and distinguish accessible empty success.

    :return: ``None`` after validating complete multi-page and empty-playlist results.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_search_items_handler,
    )

    paged_lookup = PagingPlaylistItemsLookup(
        {
            None: {"items": [_playlist_search_item(0, title="Needle", video_id="first")], "nextPageToken": "second"},
            "second": {"items": [_playlist_search_item(1, title="Needle", video_id="second")]},
        }
    )
    paged = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()), playlist_items=paged_lookup
    )({"playlistId": "PL123", "query": "needle", "maxResults": 2})

    assert [item["position"] for item in paged["items"]] == [0, 1]
    assert paged_lookup.calls == [
        {"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 50},
        {"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 50, "pageToken": "second"},
    ]
    assert paged["searchCoverage"] == {
        "inspectedEntryCount": 2,
        "isComplete": True,
        "terminationReason": "end_of_playlist",
    }

    empty = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()),
        playlist_items=PagingPlaylistItemsLookup({None: {"items": []}}),
    )({"playlistId": "PL123", "query": "needle"})
    assert empty["items"] == []
    assert empty["searchCoverage"]["isComplete"] is True
    assert empty["additionalMatchesOmitted"] is False


def test_playlist_search_distinguishes_unavailable_resources_and_safe_pagination_failures():
    """Keep unavailable and malformed traversal outcomes separate from empty success.

    :return: ``None`` after asserting safe public failure categories and diagnostics.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsSearchItemsToolError,
        build_playlists_search_items_handler,
    )

    unavailable_match = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()),
        playlist_items=PagingPlaylistItemsLookup(
            {None: {"items": [_playlist_search_item(0, title="Needle", video_id="private-video", privacy="private")]}}
        ),
    )({"playlistId": "PL123", "query": "needle"})
    assert unavailable_match["items"][0]["availabilityState"] == "unavailable"
    assert unavailable_match["items"][0]["matchingFields"] == ["title"]

    unavailable = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup({"items": []}),
        playlist_items=PagingPlaylistItemsLookup({None: {"items": []}}),
    )
    with pytest.raises(PlaylistsSearchItemsToolError) as unavailable_error:
        unavailable({"playlistId": "PL123", "query": "needle"})
    assert unavailable_error.value.category == "unavailable_resource"
    assert unavailable_error.value.details == {"resource": "playlist"}

    repeated = build_playlists_search_items_handler(
        playlists=RecordingPlaylistLookup(_playlist_payload()),
        playlist_items=PagingPlaylistItemsLookup(
            {
                None: {"items": [], "nextPageToken": "loop"},
                "loop": {"items": [], "nextPageToken": "loop"},
            }
        ),
    )
    with pytest.raises(PlaylistsSearchItemsToolError) as repeated_error:
        repeated({"playlistId": "PL123", "query": "needle"})
    assert repeated_error.value.category == "upstream_failure"
    assert "loop" not in str(repeated_error.value.details)


def test_playlist_video_transcripts_validates_bounds_and_returns_ordered_bounded_outcomes():
    """Retrieve ordered timestamped outcomes through one bounded playlist listing.

    :return: ``None`` after validating input, fan-out calls, result order, and summary.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetVideoTranscriptsToolError,
        build_playlists_get_video_transcripts_handler,
        validate_playlists_get_video_transcripts_arguments,
    )

    assert validate_playlists_get_video_transcripts_arguments({"playlistId": " PL123 "}) == {
        "playlistId": "PL123",
        "language": None,
        "maxResults": 10,
    }
    for arguments, field in (
        ({}, "playlistId"),
        ({"playlistId": "PL123", "maxResults": True}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": 0}, "maxResults"),
        ({"playlistId": "PL123", "maxResults": 51}, "maxResults"),
        ({"playlistId": "PL123", "unexpected": "value"}, "unexpected"),
    ):
        with pytest.raises(PlaylistsGetVideoTranscriptsToolError) as exc_info:
            validate_playlists_get_video_transcripts_arguments(arguments)

        assert exc_info.value.category == "invalid_parameters"
        assert exc_info.value.details == {"field": field}

    playlist_items = RecordingPlaylistItemsLookup(
        {
            "items": [
                _playlist_search_item(0, video_id="available"),
                _playlist_search_item(1, video_id="", privacy="private"),
                _playlist_search_item(2, video_id="empty"),
            ],
            "nextPageToken": "later",
        }
    )
    timestamped = RecordingTimestampedCaptions(
        {
            "available": {
                "videoId": "available",
                "language": "en",
                "captionTrackId": "caption-1",
                "availability": "available",
                "segments": [{"text": "Hello", "startTimeSeconds": 0.0, "endTimeSeconds": 1.0}],
            },
            "empty": {"videoId": "empty", "language": "en", "availability": "available", "segments": []},
        }
    )

    result = build_playlists_get_video_transcripts_handler(
        playlist_items=playlist_items,
        timestamped_captions=timestamped,
    )({"playlistId": " PL123 ", "maxResults": 3})

    assert playlist_items.calls == [{"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 3}]
    assert timestamped.calls == [{"videoId": "available", "language": "en"}, {"videoId": "empty", "language": "en"}]
    assert [item["transcriptStatus"] for item in result["items"]] == ["available", "video_unavailable", "empty"]
    assert result["items"][0]["segments"][0]["text"] == "Hello"
    assert result["fanOutSummary"] == {
        "appliedLimit": 3,
        "consideredItemCount": 3,
        "transcriptAttemptCount": 2,
        "outcomeCounts": {"available": 1, "video_unavailable": 1, "empty": 1},
        "additionalPlaylistItemsNotAttempted": True,
    }


def test_playlist_video_transcripts_resolves_explicit_configured_and_english_languages():
    """Resolve and forward one exact language for every eligible playlist video.

    :return: ``None`` after validating explicit, configured, and English language behavior.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetVideoTranscriptsToolError,
        build_playlists_get_video_transcripts_handler,
    )

    payload = {"items": [_playlist_search_item(0, video_id="video-1")]}
    responses = {
        "video-1": {"videoId": "video-1", "language": "fr", "availability": "available", "segments": []},
    }
    configured_captions = RecordingTimestampedCaptions(responses)
    configured = build_playlists_get_video_transcripts_handler(
        playlist_items=RecordingPlaylistItemsLookup(payload),
        timestamped_captions=configured_captions,
        default_language=" FR-ca ",
    )({"playlistId": "PL123"})
    assert configured_captions.calls == [{"videoId": "video-1", "language": "fr-CA"}]
    assert configured["language"] == "fr-CA"
    assert configured["languageSource"] == "configured_default"

    explicit_captions = RecordingTimestampedCaptions(responses)
    explicit = build_playlists_get_video_transcripts_handler(
        playlist_items=RecordingPlaylistItemsLookup(payload),
        timestamped_captions=explicit_captions,
        default_language="fr",
    )({"playlistId": "PL123", "language": " ES "})
    assert explicit_captions.calls == [{"videoId": "video-1", "language": "es"}]
    assert explicit["languageSource"] == "explicit"

    english_captions = RecordingTimestampedCaptions(responses)
    english = build_playlists_get_video_transcripts_handler(
        playlist_items=RecordingPlaylistItemsLookup(payload),
        timestamped_captions=english_captions,
    )({"playlistId": "PL123"})
    assert english_captions.calls == [{"videoId": "video-1", "language": "en"}]
    assert english["languageSource"] == "english_fallback"

    with pytest.raises(PlaylistsGetVideoTranscriptsToolError) as configuration_error:
        build_playlists_get_video_transcripts_handler(
            playlist_items=RecordingPlaylistItemsLookup(payload),
            timestamped_captions=RecordingTimestampedCaptions(responses),
            default_language_error="invalid",
        )({"playlistId": "PL123"})
    assert configuration_error.value.category == "invalid_parameters"
    assert configuration_error.value.details == {"field": "YOUTUBE_TRANSCRIPT_LANG"}


def test_playlist_video_transcripts_preserves_safe_mixed_access_outcomes():
    """Preserve successful transcripts while mapping child failures per video.

    :return: ``None`` after validating mixed outcomes, safe errors, and no sensitive detail.
    """
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_get_video_transcripts_handler,
    )
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
    )

    playlist_items = RecordingPlaylistItemsLookup(
        {
            "items": [
                _playlist_search_item(0, video_id="available"),
                _playlist_search_item(1, video_id="missing"),
                _playlist_search_item(2, video_id="restricted"),
                _playlist_search_item(3, video_id="quota"),
            ]
        }
    )
    timestamped = RecordingTimestampedCaptions(
        {
            "available": {
                "videoId": "available",
                "language": "en",
                "availability": "available",
                "segments": [{"text": "Safe", "startTimeSeconds": 0.0, "endTimeSeconds": 1.0}],
            },
            "missing": TranscriptsGetTimestampedCaptionsToolError(
                "secret", category="language_unavailable", details={"token": "secret"}
            ),
            "restricted": TranscriptsGetTimestampedCaptionsToolError(
                "secret", category="authorization_sensitive_data", details={"api_key": "secret"}
            ),
            "quota": TranscriptsGetTimestampedCaptionsToolError(
                "secret", category="quota_exhaustion", details={"raw_body": "secret"}
            ),
        }
    )

    result = build_playlists_get_video_transcripts_handler(
        playlist_items=playlist_items,
        timestamped_captions=timestamped,
    )({"playlistId": "PL123"})

    assert [item["transcriptStatus"] for item in result["items"]] == [
        "available",
        "transcript_unavailable",
        "authorization_sensitive_data",
        "quota_exhaustion",
    ]
    assert result["fanOutSummary"]["transcriptAttemptCount"] == 4
    assert "secret" not in str(result)
    assert "token" not in str(result).lower()


def test_playlist_video_transcripts_maps_listing_and_remaining_child_failures_safely():
    """Separate whole-request listing failures from safe source-ordered child outcomes.

    :return: ``None`` after validating unavailable, source, and unexpected failure handling.
    """
    from mcp_server.tools.youtube_common.playlist_items import (
        PlaylistItemsListToolError,
    )
    from mcp_server.tools.youtube_composed.playlists import (
        PlaylistsGetVideoTranscriptsToolError,
        build_playlists_get_video_transcripts_handler,
    )
    from mcp_server.tools.youtube_composed.transcripts import (
        TranscriptsGetTimestampedCaptionsToolError,
    )

    def unavailable_listing(_arguments):
        """Raise an unavailable listing error with unsafe lower-layer details.

        :param _arguments: Ignored lower-layer listing arguments.
        :raises PlaylistItemsListToolError: Always raised for whole-request mapping coverage.
        """
        raise PlaylistItemsListToolError(
            "secret",
            category="resource_not_found",
            details={"api_key": "secret", "raw_body": "secret"},
        )

    with pytest.raises(PlaylistsGetVideoTranscriptsToolError) as listing_error:
        build_playlists_get_video_transcripts_handler(
            playlist_items=unavailable_listing,
            timestamped_captions=RecordingTimestampedCaptions({}),
        )({"playlistId": "PL123"})
    assert listing_error.value.category == "unavailable_resource"
    assert listing_error.value.details == {"resource": "playlist"}

    results = build_playlists_get_video_transcripts_handler(
        playlist_items=RecordingPlaylistItemsLookup(
            {"items": [_playlist_search_item(0, video_id="source"), _playlist_search_item(1, video_id="unexpected")]}
        ),
        timestamped_captions=RecordingTimestampedCaptions(
            {
                "source": TranscriptsGetTimestampedCaptionsToolError(
                    "secret", category="source_unavailable", details={"token": "secret"}
                ),
                "unexpected": ValueError("secret"),
            }
        ),
    )({"playlistId": "PL123"})
    assert [item["transcriptStatus"] for item in results["items"]] == ["source_unavailable", "upstream_failure"]
    assert "secret" not in str(results)
