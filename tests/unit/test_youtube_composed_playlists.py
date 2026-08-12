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
