"""Unit tests for the concrete Layer 2 ``playlistImages_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.tools.youtube_common.playlist_images import (
    PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
    PlaylistImagesListToolError,
    build_playlist_images_list_tool_descriptor,
    map_playlist_images_list_result,
    validate_playlist_images_list_arguments,
)


def test_playlist_images_list_schema_preserves_required_selector_inputs():
    """Expose required part, supported selectors, and playlist-scoped paging controls."""
    properties = PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(properties)
    assert {"required": ["playlistId"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]
    assert {"required": ["id"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]


def test_validate_playlist_images_list_arguments_accepts_playlist_selector():
    """Accept playlist-scoped retrieval arguments."""
    selected = validate_playlist_images_list_arguments(
        {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25}
    )

    assert selected == {
        "part": "snippet",
        "playlistId": "PL123",
        "pageToken": "NEXT_PAGE",
        "maxResults": 25,
    }


def test_validate_playlist_images_list_arguments_accepts_image_id_selector():
    """Accept direct playlist-image lookup arguments."""
    selected = validate_playlist_images_list_arguments({"part": "id,snippet", "id": "img-123"})

    assert selected == {"part": "id,snippet", "id": "img-123"}


def test_map_playlist_images_list_result_preserves_items_paging_and_upstream_fields():
    """Map upstream playlist-image results into a safe near-raw list result."""
    result = map_playlist_images_list_result(
        {
            "items": [{"kind": "youtube#playlistImage", "id": "img-123"}],
            "kind": "youtube#playlistImageListResponse",
            "etag": "etag-123",
            "nextPageToken": "NEXT_PAGE_2",
            "prevPageToken": "PREV_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25},
    )

    assert result["endpoint"] == "playlistImages.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}
    assert result["paging"] == {"pageToken": "NEXT_PAGE", "maxResults": 25}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["items"][0]["id"] == "img-123"
    assert result["kind"] == "youtube#playlistImageListResponse"
    assert result["etag"] == "etag-123"
    assert result["nextPageToken"] == "NEXT_PAGE_2"
    assert result["prevPageToken"] == "PREV_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_map_playlist_images_list_result_preserves_direct_id_context():
    """Map direct image lookup results without fabricating paging context."""
    result = map_playlist_images_list_result({"items": [{"id": "img-123"}]}, {"part": "id", "id": "img-123"})

    assert result["selector"] == {"name": "id", "value": "img-123"}
    assert "paging" not in result
    assert result["requestedParts"] == ["id"]


def test_map_playlist_images_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful empty results."""
    result = map_playlist_images_list_result({"items": []}, {"part": "snippet", "playlistId": "PL123"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_playlist_images_list_handler_invokes_wrapper_once_for_oauth_request():
    """Execute one valid playlist-image lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``playlistImages_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative playlist-image list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "img-123"}]}

    wrapper = FakeWrapper()
    descriptor = build_playlist_images_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet", "playlistId": "PL123"})

    assert result["items"] == [{"id": "img-123"}]
    assert wrapper.calls[0][1] == {"part": "snippet", "playlistId": "PL123"}
    assert wrapper.calls[0][2].mode.value == "oauth_required"


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"part": "", "playlistId": "PL123"},
        {"part": "statistics", "playlistId": "PL123"},
        {"part": "snippet,statistics", "playlistId": "PL123"},
        {"part": "snippet"},
        {"part": "snippet", "playlistId": ""},
        {"part": "snippet", "playlistId": "PL123", "id": "img-123"},
        {"part": "snippet", "id": "img-123", "pageToken": "NEXT_PAGE"},
        {"part": "snippet", "id": "img-123", "maxResults": 25},
        {"part": "snippet", "playlistId": "PL123", "pageToken": ""},
        {"part": "snippet", "playlistId": "PL123", "maxResults": "25"},
        {"part": "snippet", "playlistId": "PL123", "maxResults": True},
        {"part": "snippet", "playlistId": "PL123", "maxResults": -1},
        {"part": "snippet", "playlistId": "PL123", "maxResults": 51},
        {"part": "snippet", "playlistId": "PL123", "body": {"snippet": {}}},
        {"part": "snippet", "playlistId": "PL123", "media": {"content": "raw"}},
        {"part": "snippet", "playlistId": "PL123", "analytics": True},
        {"part": "snippet", "playlistId": "PL123", "rankBy": "views"},
    ],
)
def test_validate_playlist_images_list_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed, mutation, media, analytics, and selector-incompatible requests."""
    with pytest.raises(PlaylistImagesListToolError) as exc_info:
        validate_playlist_images_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
