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
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_handler

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
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_handler

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
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_items_handler

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
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
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
