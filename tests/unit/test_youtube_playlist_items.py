"""Unit tests for the concrete Layer 2 ``playlistItems_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.playlist_items import (
    PLAYLIST_ITEMS_DELETE_CALLER_EXAMPLES,
    PLAYLIST_ITEMS_DELETE_INPUT_SCHEMA,
    PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA,
    PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA,
    PlaylistItemsDeleteToolError,
    PlaylistItemsInsertToolError,
    PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
    PlaylistItemsListToolError,
    PlaylistItemsUpdateToolError,
    build_playlist_items_delete_handler,
    build_playlist_items_delete_tool_descriptor,
    build_playlist_items_insert_handler,
    build_playlist_items_insert_tool_descriptor,
    build_playlist_items_update_handler,
    build_playlist_items_update_tool_descriptor,
    build_playlist_items_list_handler,
    build_playlist_items_list_tool_descriptor,
    map_playlist_items_delete_result,
    map_playlist_items_insert_result,
    map_playlist_items_update_result,
    map_playlist_items_list_result,
    validate_playlist_items_delete_arguments,
    validate_playlist_items_insert_arguments,
    validate_playlist_items_update_arguments,
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


class FakePlaylistItemsInsertWrapper:
    """Capture wrapper calls for ``playlistItems_insert`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response."""
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistItem",
            "etag": "etag-playlist-item",
            "id": "playlist-item-123",
            "snippet": {
                "playlistId": "PL123",
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                "title": "Representative playlist item",
            },
            "contentDetails": {"videoId": "video-123"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response."""
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FakePlaylistItemsUpdateWrapper:
    """Capture wrapper calls for ``playlistItems_update`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response."""
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistItem",
            "etag": "etag-playlist-item",
            "id": "playlist-item-123",
            "snippet": {
                "playlistId": "PL123",
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
                "title": "Representative playlist item",
            },
            "contentDetails": {"videoId": "video-123"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response."""
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FakePlaylistItemsDeleteWrapper:
    """Capture wrapper calls for ``playlistItems_delete`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and no-body delete response."""
        self.calls = []
        self.response = response or {}

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response."""
        self.calls.append((executor, arguments, auth_context))
        return self.response


def _insert_arguments(**overrides):
    """Build a representative ``playlistItems_insert`` request."""
    arguments = {
        "part": "snippet",
        "body": {
            "snippet": {
                "playlistId": "PL123",
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
            }
        },
    }
    arguments.update(overrides)
    return arguments


def _update_arguments(**overrides):
    """Build a representative ``playlistItems_update`` request."""
    arguments = {
        "part": "snippet",
        "body": {
            "id": "playlist-item-123",
            "snippet": {
                "playlistId": "PL123",
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
            },
        },
    }
    arguments.update(overrides)
    return arguments


def _delete_arguments(**overrides):
    """Build a representative ``playlistItems_delete`` request."""
    arguments = {"id": "playlist-item-123"}
    arguments.update(overrides)
    return arguments


def test_playlist_items_update_schema_preserves_required_body_inputs():
    """Expose required part, target identity, and playlist/video update fields."""
    properties = PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA["properties"]
    body = properties["body"]
    snippet = body["properties"]["snippet"]
    resource_id = snippet["properties"]["resourceId"]

    assert PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(properties)
    assert body["required"] == ["id", "snippet"]
    assert snippet["required"] == ["playlistId", "resourceId"]
    assert resource_id["required"] == ["videoId"]
    assert "position" not in snippet["properties"]


def test_validate_playlist_items_update_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist-item update request."""
    selected = validate_playlist_items_update_arguments(
        {
            "part": " snippet ",
            "body": {
                "id": " playlist-item-123 ",
                "snippet": {
                    "playlistId": " PL123 ",
                    "resourceId": {"kind": "youtube#video", "videoId": " video-123 "},
                },
            },
        }
    )

    assert selected == _update_arguments()


def test_map_playlist_items_update_result_preserves_resource_and_context():
    """Map upstream playlist item update into a safe near-raw mutation result."""
    result = map_playlist_items_update_result(
        {
            "kind": "youtube#playlistItem",
            "etag": "etag-item",
            "id": "playlist-item-123",
            "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
            "contentDetails": {"videoId": "video-123"},
        },
        _update_arguments(),
    )

    assert result["endpoint"] == "playlistItems.update"
    assert result["quotaCost"] == 50
    assert result["updated"] is True
    assert result["requestedParts"] == ["snippet"]
    assert result["target"] == {"playlistItemId": "playlist-item-123", "playlistId": "PL123", "videoId": "video-123", "resourceKind": "youtube#video"}
    assert result["update"] == {"playlistId": "PL123", "videoId": "video-123", "resourceKind": "youtube#video"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-item-123"
    assert result["kind"] == "youtube#playlistItem"
    assert result["etag"] == "etag-item"


def test_playlist_items_update_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one update request through Layer 1."""
    wrapper = FakePlaylistItemsUpdateWrapper()
    executor = object()
    handler = build_playlist_items_update_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_update_arguments())

    assert result["endpoint"] == "playlistItems.update"
    assert result["item"]["id"] == "playlist-item-123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _update_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlist_items_update_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready update descriptor metadata and examples."""
    descriptor = build_playlist_items_update_tool_descriptor(wrapper=FakePlaylistItemsUpdateWrapper())

    assert descriptor["name"] == "playlistItems_update"
    assert descriptor["inputSchema"] == PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistItems.update"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        (
            {
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                }
            },
            "part",
        ),
        (
            {
                "part": "statistics",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                },
            },
            "part",
        ),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": []}, "body"),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            },
            "body.id",
        ),
        ({"part": "snippet", "body": {"id": "playlist-item-123"}}, "body.snippet"),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-item-123", "snippet": {"resourceId": {"videoId": "video-123"}}},
            },
            "body.snippet.playlistId",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123"}},
            },
            "body.snippet.resourceId",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123", "resourceId": {}}},
            },
            "body.snippet.resourceId.videoId",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"kind": "youtube#playlist", "videoId": "video-123"},
                    },
                },
            },
            "body.snippet.resourceId.kind",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"videoId": "video-123"},
                        "position": 0,
                    },
                },
            },
            "body.snippet.position",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                    "contentDetails": {"videoId": "video-123"},
                },
            },
            "body.contentDetails",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "etag": "read-only",
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                },
            },
            "body.etag",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                },
                "rankPlaylist": True,
            },
            "rankPlaylist",
        ),
    ],
)
def test_validate_playlist_items_update_arguments_rejects_invalid_shapes(arguments, field):
    """Reject unsupported playlist-item update shapes with safe field details."""
    with pytest.raises(PlaylistItemsUpdateToolError) as exc_info:
        validate_playlist_items_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlist_items_update_tool_error_sanitizes_sensitive_details():
    """Avoid leaking credentials or raw request details through safe update errors."""
    error = PlaylistItemsUpdateToolError(
        "failure",
        details={
            "field": "auth",
            "api_key": "secret",
            "oauth_token": "secret",
            "raw_request": {"part": "snippet"},
            "safe": "visible",
        },
    )

    assert error.details == {"field": "auth", "safe": "visible"}


def test_playlist_items_update_handler_maps_upstream_errors_to_safe_categories():
    """Map normalized upstream update failures to shared Layer 2 error categories."""

    class FailingWrapper:
        """Raise a configured normalized error for update handler mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an authorization-flavored upstream failure."""
            raise NormalizedUpstreamError(
                "forbidden",
                category="forbidden",
                retryable=False,
                upstream_status=403,
                details={"upstreamStatus": 403, "oauth_token": "secret"},
            )

    handler = build_playlist_items_update_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsUpdateToolError) as exc_info:
        handler(_update_arguments())

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"upstreamStatus": 403}


def test_playlist_items_delete_schema_requires_identifier_only():
    """Expose only the playlist item ``id`` for destructive deletion."""
    assert PLAYLIST_ITEMS_DELETE_INPUT_SCHEMA == {
        "type": "object",
        "required": ["id"],
        "properties": {"id": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }


def test_validate_playlist_items_delete_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist-item deletion request."""
    selected = validate_playlist_items_delete_arguments({"id": " playlist-item-123 "})

    assert selected == _delete_arguments()


def test_map_playlist_items_delete_result_preserves_acknowledgment_and_context():
    """Map no-body upstream deletion into a safe acknowledgment result."""
    result = map_playlist_items_delete_result({}, _delete_arguments())

    assert result == {
        "endpoint": "playlistItems.delete",
        "quotaCost": 50,
        "target": {"id": "playlist-item-123"},
        "auth": {"mode": "oauth_required"},
        "deleted": True,
        "acknowledged": True,
    }


def test_playlist_items_delete_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one delete request through Layer 1."""
    wrapper = FakePlaylistItemsDeleteWrapper()
    executor = object()
    handler = build_playlist_items_delete_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_delete_arguments())

    assert result["endpoint"] == "playlistItems.delete"
    assert result["target"] == {"id": "playlist-item-123"}
    assert result["deleted"] is True
    assert result["acknowledged"] is True
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _delete_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlist_items_delete_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready delete descriptor metadata and examples."""
    descriptor = build_playlist_items_delete_tool_descriptor(wrapper=FakePlaylistItemsDeleteWrapper())

    assert descriptor["name"] == "playlistItems_delete"
    assert descriptor["inputSchema"] == PLAYLIST_ITEMS_DELETE_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistItems.delete"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"] == list(PLAYLIST_ITEMS_DELETE_CALLER_EXAMPLES)


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "id"),
        ({"id": ""}, "id"),
        ({"id": "   "}, "id"),
        ({"id": 123}, "id"),
        ({"id": "playlist-item-123", "part": "snippet"}, "part"),
        ({"id": "playlist-item-123", "body": {}}, "body"),
        ({"id": "playlist-item-123", "playlistId": "PL123"}, "playlistId"),
        ({"id": "playlist-item-123", "pageToken": "NEXT"}, "pageToken"),
        ({"id": "playlist-item-123", "maxResults": 5}, "maxResults"),
    ],
)
def test_validate_playlist_items_delete_arguments_rejects_invalid_shapes(arguments, field):
    """Reject unsupported playlist-item delete shapes with safe field details."""
    with pytest.raises(PlaylistItemsDeleteToolError) as exc_info:
        validate_playlist_items_delete_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlist_items_delete_tool_error_sanitizes_sensitive_details():
    """Avoid leaking credentials or raw request details through safe delete errors."""
    error = PlaylistItemsDeleteToolError(
        "failure",
        details={
            "field": "auth",
            "api_key": "secret",
            "oauth_token": "secret",
            "raw_request": {"id": "playlist-item-123"},
            "safe": "visible",
        },
    )

    assert error.details == {"field": "auth", "safe": "visible"}


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (NormalizedUpstreamError("missing oauth", "authentication", False, 401, {}), "authentication_failed"),
        (NormalizedUpstreamError("forbidden", "forbidden", False, 403, {}), "authorization_failed"),
        (NormalizedUpstreamError("not found", "not_found", False, 404, {}), "resource_not_found"),
        (NormalizedUpstreamError("quota", "quota", True, 429, {}), "quota_exhausted"),
        (NormalizedUpstreamError("unavailable", "transient", True, 503, {}), "endpoint_unavailable"),
        (NormalizedUpstreamError("deprecated", "deprecated", False, 410, {}), "deprecated_endpoint"),
        (NormalizedUpstreamError("invalid", "invalid_request", False, 400, {"reason": "bad"}), "invalid_request"),
    ],
)
def test_playlist_items_delete_handler_maps_safe_upstream_error_categories(error, category):
    """Convert upstream deletion failures into MCP-safe playlist-item errors."""

    class FailingWrapper:
        """Raise the provided normalized error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured error for category mapping checks."""
            raise error

    handler = build_playlist_items_delete_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsDeleteToolError) as exc_info:
        handler(_delete_arguments())

    assert exc_info.value.category == category


def test_playlist_items_delete_handler_maps_layer1_value_errors():
    """Convert Layer 1 auth or validation value errors to safe delete errors."""

    class FailingWrapper:
        """Raise a Layer 1 value error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a value error as a Layer 1 wrapper could."""
            raise ValueError("playlistItems.delete requires oauth_required auth")

    handler = build_playlist_items_delete_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsDeleteToolError) as exc_info:
        handler(_delete_arguments())

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"operation": "playlistItems.delete"}


def test_playlist_items_insert_schema_preserves_required_body_inputs():
    """Expose required part, body, and playlist/video assignment fields."""
    properties = PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA["properties"]
    snippet = properties["body"]["properties"]["snippet"]
    resource_id = snippet["properties"]["resourceId"]

    assert PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(properties)
    assert snippet["required"] == ["playlistId", "resourceId"]
    assert resource_id["required"] == ["videoId"]
    assert "position" in snippet["properties"]


def test_validate_playlist_items_insert_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist-item insertion request."""
    selected = validate_playlist_items_insert_arguments(
        {
            "part": " snippet ",
            "body": {
                "snippet": {
                    "playlistId": " PL123 ",
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": " video-123 "},
                }
            },
        }
    )

    assert selected == _insert_arguments()


def test_map_playlist_items_insert_result_preserves_resource_and_context():
    """Map upstream playlist item creation into a safe near-raw mutation result."""
    result = map_playlist_items_insert_result(
        {
            "kind": "youtube#playlistItem",
            "etag": "etag-item",
            "id": "playlist-item-123",
            "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}, "position": 0},
            "contentDetails": {"videoId": "video-123"},
        },
        _insert_arguments(),
    )

    assert result["endpoint"] == "playlistItems.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["assignment"] == {"playlistId": "PL123", "videoId": "video-123", "resourceKind": "youtube#video"}
    assert result["placement"] == {"position": 0}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-item-123"
    assert result["kind"] == "youtube#playlistItem"
    assert result["etag"] == "etag-item"


def test_playlist_items_insert_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one insert request through Layer 1."""
    wrapper = FakePlaylistItemsInsertWrapper()
    executor = object()
    handler = build_playlist_items_insert_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_insert_arguments())

    assert result["endpoint"] == "playlistItems.insert"
    assert result["item"]["id"] == "playlist-item-123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _insert_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlist_items_insert_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready insert descriptor metadata and examples."""
    descriptor = build_playlist_items_insert_tool_descriptor(wrapper=FakePlaylistItemsInsertWrapper())

    assert descriptor["name"] == "playlistItems_insert"
    assert descriptor["inputSchema"] == PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistItems.insert"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    "arguments",
    [
        {"body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}},
        {"part": "statistics", "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet"},
        {"part": "snippet", "body": []},
        {"part": "snippet", "body": {}},
        {"part": "snippet", "body": {"snippet": {"resourceId": {"videoId": "video-123"}}}},
        {"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}},
        {"part": "snippet", "body": {"snippet": {"playlistId": "PL123", "resourceId": {}}}},
        {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "resourceId": {"kind": "youtube#playlist", "videoId": "video-123"},
                }
            },
        },
        {
            "part": "snippet",
            "body": {
                "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}, "position": -1}
            },
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            "videoEnrichment": True,
        },
    ],
)
def test_validate_playlist_items_insert_arguments_rejects_invalid_shapes(arguments):
    """Reject unsupported playlist-item insertion shapes with safe errors."""
    with pytest.raises(PlaylistItemsInsertToolError):
        validate_playlist_items_insert_arguments(arguments)


@pytest.mark.parametrize(
    "error",
    [
        NormalizedUpstreamError("missing oauth", "authentication", False, 401, {}),
        NormalizedUpstreamError("forbidden", "forbidden", False, 403, {}),
        NormalizedUpstreamError("not found", "not_found", False, 404, {}),
        NormalizedUpstreamError("quota", "quota", True, 429, {}),
        NormalizedUpstreamError("duplicate", "invalid_request", False, 400, {"reason": "duplicate"}),
        NormalizedUpstreamError("unavailable", "transient", True, 503, {}),
    ],
)
def test_playlist_items_insert_handler_maps_safe_upstream_error_categories(error):
    """Convert upstream insertion failures into MCP-safe playlist-item errors."""

    class FailingWrapper:
        """Raise the provided normalized error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured error for category mapping checks."""
            raise error

    handler = build_playlist_items_insert_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsInsertToolError) as exc_info:
        handler(_insert_arguments())

    assert exc_info.value.category in {
        "authentication_failed",
        "authorization_failed",
        "quota_exhausted",
        "resource_not_found",
        "endpoint_unavailable",
        "invalid_request",
    }


def test_playlist_items_insert_handler_maps_layer1_value_errors():
    """Convert Layer 1 auth or validation value errors to safe insert errors."""

    class FailingWrapper:
        """Raise a Layer 1 value error during wrapper execution."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a value error as a Layer 1 wrapper could."""
            raise ValueError("playlistItems.insert requires oauth_required auth")

    handler = build_playlist_items_insert_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsInsertToolError) as exc_info:
        handler(_insert_arguments())

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"operation": "playlistItems.insert"}


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
