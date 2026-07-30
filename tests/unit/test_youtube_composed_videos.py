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
