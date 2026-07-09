"""Unit tests for the concrete Layer 2 ``playlistItems_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.playlist_items import (
    PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
    PlaylistItemsListToolError,
    build_playlist_items_list_handler,
    build_playlist_items_list_tool_descriptor,
    map_playlist_items_list_result,
    validate_playlist_items_list_arguments,
)


class FakePlaylistItemsListWrapper:
    """Capture wrapper calls for ``playlistItems_list`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response."""
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistItemListResponse",
            "etag": "etag-playlist-items",
            "items": [
                {
                    "kind": "youtube#playlistItem",
                    "etag": "etag-item",
                    "id": "playlist-item-123",
                    "snippet": {"playlistId": "PL123", "title": "Video title"},
                    "contentDetails": {"videoId": "video-123"},
                }
            ],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response."""
        self.calls.append((executor, arguments, auth_context))
        return self.response


def test_playlist_items_list_schema_preserves_required_selector_inputs():
    """Expose required part, selectors, and playlist-scoped paging controls."""
    properties = PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(properties)
    assert {"required": ["playlistId"]} in PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["oneOf"]
    assert {"required": ["id"]} in PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["oneOf"]


def test_validate_playlist_items_list_arguments_accepts_playlist_scoped_request():
    """Accept and normalize a supported playlist-scoped list request."""
    selected = validate_playlist_items_list_arguments(
        {"part": " snippet,contentDetails ", "playlistId": " PL123 ", "pageToken": " NEXT ", "maxResults": 10}
    )

    assert selected == {
        "part": "snippet,contentDetails",
        "playlistId": "PL123",
        "pageToken": "NEXT",
        "maxResults": 10,
    }


def test_validate_playlist_items_list_arguments_accepts_direct_id_request():
    """Accept and normalize a supported direct playlist-item lookup."""
    selected = validate_playlist_items_list_arguments({"part": "id,status", "id": " playlist-item-123 "})

    assert selected == {"part": "id,status", "id": "playlist-item-123"}


def test_map_playlist_items_list_result_preserves_items_and_context():
    """Map upstream playlist items into a safe near-raw list result."""
    result = map_playlist_items_list_result(
        {
            "kind": "youtube#playlistItemListResponse",
            "etag": "etag-list",
            "items": [{"id": "playlist-item-123", "snippet": {"playlistId": "PL123"}}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet,contentDetails", "playlistId": "PL123", "pageToken": "PAGE_1", "maxResults": 25},
    )

    assert result["endpoint"] == "playlistItems.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet", "contentDetails"]
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}
    assert result["paging"] == {"pageToken": "PAGE_1", "maxResults": 25}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"] == [{"id": "playlist-item-123", "snippet": {"playlistId": "PL123"}}]
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_map_playlist_items_list_result_preserves_empty_success():
    """Keep empty upstream item collections as successful list results."""
    result = map_playlist_items_list_result({"items": []}, {"part": "snippet", "playlistId": "PL123"})

    assert result["endpoint"] == "playlistItems.list"
    assert result["items"] == []
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}


def test_playlist_items_list_handler_forwards_api_key_context_to_layer1_wrapper():
    """Validate, execute, and map one playlist-scoped request through Layer 1."""
    wrapper = FakePlaylistItemsListWrapper()
    executor = object()
    handler = build_playlist_items_list_handler(wrapper=wrapper, executor=executor, api_key="local-api-key")

    result = handler({"part": "snippet,contentDetails", "playlistId": "PL123"})

    assert result["endpoint"] == "playlistItems.list"
    assert result["items"][0]["id"] == "playlist-item-123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == {"part": "snippet,contentDetails", "playlistId": "PL123"}
    assert wrapper.calls[0][2].mode.value == "api_key"
    assert wrapper.calls[0][2].credentials.api_key == "local-api-key"
    assert "local-api-key" not in str(result)


def test_playlist_items_list_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready descriptor metadata and examples."""
    descriptor = build_playlist_items_list_tool_descriptor(wrapper=FakePlaylistItemsListWrapper())

    assert descriptor["name"] == "playlistItems_list"
    assert descriptor["inputSchema"] == PLAYLIST_ITEMS_LIST_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistItems.list"
    assert descriptor["metadata"]["quotaCost"] == 1
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    "error",
    [
        NormalizedUpstreamError("missing key", "authentication", False, 401, {}),
        NormalizedUpstreamError("not found", "not_found", False, 404, {}),
        NormalizedUpstreamError("quota", "quota", True, 429, {}),
        NormalizedUpstreamError("unavailable", "transient", True, 503, {}),
    ],
)
def test_playlist_items_list_handler_maps_safe_upstream_error_categories(error):
    """Convert upstream failures into MCP-safe playlist-item errors."""

    class FailingWrapper:
        """Raise the provided normalized error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured error for category mapping checks."""
            raise error

    handler = build_playlist_items_list_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsListToolError) as exc_info:
        handler({"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category in {
        "authentication_failed",
        "quota_exhausted",
        "resource_not_found",
        "endpoint_unavailable",
    }


def test_playlist_items_list_handler_maps_layer1_value_errors():
    """Convert Layer 1 auth or validation value errors to safe tool errors."""

    class FailingWrapper:
        """Raise a Layer 1 value error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a value error as a Layer 1 wrapper could."""
            raise ValueError("playlistItems.list requires api_key auth")

    handler = build_playlist_items_list_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsListToolError) as exc_info:
        handler({"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"operation": "playlistItems.list"}
