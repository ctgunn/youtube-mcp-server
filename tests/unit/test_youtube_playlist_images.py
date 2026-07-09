"""Unit tests for the concrete Layer 2 ``playlistImages_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.playlist_images import (
    PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA,
    PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA,
    PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
    PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA,
    PlaylistImagesDeleteToolError,
    PlaylistImagesInsertToolError,
    PlaylistImagesListToolError,
    PlaylistImagesUpdateToolError,
    build_playlist_images_delete_handler,
    build_playlist_images_delete_tool_descriptor,
    build_playlist_images_insert_handler,
    build_playlist_images_insert_tool_descriptor,
    build_playlist_images_list_tool_descriptor,
    build_playlist_images_update_handler,
    build_playlist_images_update_tool_descriptor,
    map_playlist_images_delete_result,
    map_playlist_images_insert_result,
    map_playlist_images_list_result,
    map_playlist_images_update_result,
    validate_playlist_images_delete_arguments,
    validate_playlist_images_insert_arguments,
    validate_playlist_images_list_arguments,
    validate_playlist_images_update_arguments,
)


class FakePlaylistImagesInsertWrapper:
    """Capture wrapper calls for ``playlistImages_insert`` tests.

    The fake returns a representative created playlist-image resource and
    exposes call arguments for assertions without performing network I/O.
    """

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistImage",
            "etag": "etag-created",
            "id": "playlist-image-123",
            "snippet": {"playlistId": "PL123", "type": "medium"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FakePlaylistImagesUpdateWrapper:
    """Capture wrapper calls for ``playlistImages_update`` tests.

    The fake returns a representative updated playlist-image resource and
    exposes call arguments for assertions without performing network I/O.
    """

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistImage",
            "etag": "etag-updated",
            "id": "playlist-image-123",
            "snippet": {"playlistId": "PL123", "type": "medium"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FakePlaylistImagesDeleteWrapper:
    """Capture wrapper calls for ``playlistImages_delete`` tests.

    The fake returns a representative no-content deletion summary and exposes
    call arguments for assertions without performing network I/O.
    """

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {
            "playlistImageId": "playlist-image-123",
            "isDeleted": True,
            "upstreamBodyState": "empty",
            "sourceOperation": "playlistImages.delete",
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the Layer 2 handler.
        :param arguments: Validated arguments forwarded to Layer 1.
        :param auth_context: OAuth auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


def test_playlist_images_list_schema_preserves_required_selector_inputs():
    """Expose required part, supported selectors, and playlist-scoped paging controls."""
    properties = PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(properties)
    assert {"required": ["playlistId"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]
    assert {"required": ["id"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]


def test_playlist_images_insert_schema_preserves_required_upload_inputs():
    """Expose required part, body, and media inputs for playlist-image insertion."""
    properties = PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["required"] == ["part", "body", "media"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert {"snippet"}.issubset(properties["body"]["required"])
    assert {"mimeType", "content"}.issubset(properties["media"]["required"])
    assert PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_update_schema_preserves_required_upload_inputs():
    """Expose required part, target body, and media inputs for playlist-image updates."""
    properties = PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["required"] == ["part", "body", "media"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["body"]["required"] == ["id", "snippet"]
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_delete_schema_preserves_target_only_input():
    """Expose required id and no metadata or media inputs for playlist-image deletion."""
    properties = PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert "part" not in properties
    assert "body" not in properties
    assert "media" not in properties
    assert PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_playlist_images_insert_arguments_accepts_upload_request():
    """Accept one supported OAuth-backed playlist-image insertion request."""
    selected = validate_playlist_images_insert_arguments(
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        }
    )

    assert selected == {
        "part": "snippet",
        "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
        "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
    }


def test_validate_playlist_images_update_arguments_accepts_upload_request():
    """Accept one supported OAuth-backed playlist-image update request."""
    selected = validate_playlist_images_update_arguments(
        {
            "part": "id,snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        }
    )

    assert selected == {
        "part": "id,snippet",
        "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
        "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
    }


def test_validate_playlist_images_delete_arguments_accepts_target_id():
    """Accept one supported OAuth-backed playlist-image deletion request."""
    selected = validate_playlist_images_delete_arguments({"id": " playlist-image-123 "})

    assert selected == {"id": "playlist-image-123"}


def test_map_playlist_images_insert_result_preserves_resource_and_safe_context():
    """Map a created playlist-image response into a safe near-raw mutation result."""
    result = map_playlist_images_insert_result(
        {
            "kind": "youtube#playlistImage",
            "etag": "etag-created",
            "id": "playlist-image-123",
            "snippet": {"playlistId": "PL123", "type": "medium"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
    )

    assert result["endpoint"] == "playlistImages.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["bodyContext"] == {"hasSnippet": True, "playlistId": "PL123"}
    assert result["mediaContext"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-image-123"
    assert result["item"]["snippet"] == {"playlistId": "PL123", "type": "medium"}
    assert "fake-image-content" not in str(result)


def test_map_playlist_images_update_result_preserves_resource_and_safe_context():
    """Map an updated playlist-image response into a safe near-raw mutation result."""
    result = map_playlist_images_update_result(
        {
            "kind": "youtube#playlistImage",
            "etag": "etag-updated",
            "id": "playlist-image-123",
            "snippet": {"playlistId": "PL123", "type": "medium"},
        },
        {
            "part": "id,snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
    )

    assert result["endpoint"] == "playlistImages.update"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["bodyContext"] == {"id": "playlist-image-123", "hasSnippet": True, "playlistId": "PL123"}
    assert result["mediaContext"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-image-123"
    assert result["item"]["etag"] == "etag-updated"
    assert "fake-image-content" not in str(result)


def test_map_playlist_images_delete_result_preserves_acknowledgment_and_safe_target():
    """Map a playlist-image deletion response into a safe acknowledgment result."""
    result = map_playlist_images_delete_result(
        {
            "playlistImageId": "playlist-image-123",
            "isDeleted": True,
            "upstreamBodyState": "empty",
            "sourceOperation": "playlistImages.delete",
        },
        {"id": "playlist-image-123"},
    )

    assert result["endpoint"] == "playlistImages.delete"
    assert result["quotaCost"] == 50
    assert result["target"] == {"id": "playlist-image-123"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["deleted"] is True
    assert result["acknowledged"] is True
    assert result["statusCode"] == 204
    assert result["sourceOperation"] == "playlistImages.delete"
    assert "body" not in result
    assert "media" not in result


def test_playlist_images_insert_handler_invokes_wrapper_once_for_oauth_request():
    """Execute one valid playlist-image insertion through the descriptor handler."""
    wrapper = FakePlaylistImagesInsertWrapper()
    descriptor = build_playlist_images_insert_tool_descriptor(wrapper=wrapper, executor=object())
    arguments = {
        "part": "snippet",
        "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
        "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
    }

    result = descriptor["handler"](arguments)

    assert result["endpoint"] == "playlistImages.insert"
    assert result["quotaCost"] == 50
    assert result["item"]["id"] == "playlist-image-123"
    assert wrapper.calls[0][1] == arguments
    assert wrapper.calls[0][2].mode.value == "oauth_required"


def test_playlist_images_update_handler_invokes_wrapper_once_for_oauth_request():
    """Execute one valid playlist-image update through the descriptor handler."""
    wrapper = FakePlaylistImagesUpdateWrapper()
    descriptor = build_playlist_images_update_tool_descriptor(wrapper=wrapper, executor=object())
    arguments = {
        "part": "id,snippet",
        "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
        "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
    }

    result = descriptor["handler"](arguments)

    assert result["endpoint"] == "playlistImages.update"
    assert result["quotaCost"] == 50
    assert result["item"]["id"] == "playlist-image-123"
    assert wrapper.calls[0][1] == arguments
    assert wrapper.calls[0][2].mode.value == "oauth_required"


def test_playlist_images_delete_handler_invokes_wrapper_once_for_oauth_request():
    """Execute one valid playlist-image deletion through the descriptor handler."""
    wrapper = FakePlaylistImagesDeleteWrapper()
    descriptor = build_playlist_images_delete_tool_descriptor(wrapper=wrapper, executor=object())
    arguments = {"id": "playlist-image-123"}

    result = descriptor["handler"](arguments)

    assert result["endpoint"] == "playlistImages.delete"
    assert result["quotaCost"] == 50
    assert result["target"] == {"id": "playlist-image-123"}
    assert result["deleted"] is True
    assert wrapper.calls[0][1] == arguments
    assert wrapper.calls[0][2].mode.value == "oauth_required"


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {
            "part": "",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "statistics",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet,snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": [],
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}, "thumbnailReplacement": True},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": [],
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/gif", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {
                "mimeType": "image/jpeg",
                "content": "fake-image-content",
                "signedUrl": "https://example.test/private",
            },
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": ""},
            "rankBy": "views",
        },
    ],
)
def test_validate_playlist_images_insert_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed insert inputs, unsupported fields, and unsafe upload shapes."""
    with pytest.raises(PlaylistImagesInsertToolError) as exc_info:
        validate_playlist_images_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "fake-image-content" not in str(exc_info.value.details)
    assert "signedUrl" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_playlist_images_insert_handler_requires_oauth_access():
    """Reject insert handler construction when OAuth access is unavailable."""
    with pytest.raises(PlaylistImagesInsertToolError) as exc_info:
        build_playlist_images_insert_handler(wrapper=FakePlaylistImagesInsertWrapper(), executor=object(), oauth_token=None)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth"}


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("authentication", "authentication_failed"),
        ("authorization", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("media_eligibility", "invalid_request"),
        ("not_found", "resource_not_found"),
        ("transient", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_insert_handler_maps_upstream_failures_safely(upstream_category, expected_category):
    """Map upstream insert failures into shared safe categories."""
    class FailingWrapper:
        """Raise one normalized upstream failure for insert handler coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a configured upstream failure.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="playlist image insert failed",
                category=upstream_category,
                retryable=False,
                upstream_status=403,
                details={
                    "field": "media",
                    "raw_media": "fake-image-content",
                    "oauth_token": "secret-token",
                    "stack": "traceback",
                },
            )

    handler = build_playlist_images_insert_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesInsertToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
            }
        )

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "media"}


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {
            "part": "",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "statistics",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet,snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": [],
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123"},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {
                "id": "playlist-image-123",
                "snippet": {"playlistId": "PL123"},
                "thumbnailReplacement": True,
            },
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": [],
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/gif", "content": "fake-image-content"},
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {
                "mimeType": "image/jpeg",
                "content": "fake-image-content",
                "signedUrl": "https://example.test/private",
            },
        },
        {
            "part": "snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
            "rankBy": "views",
        },
    ],
)
def test_validate_playlist_images_update_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed update inputs, unsupported fields, and unsafe upload shapes."""
    with pytest.raises(PlaylistImagesUpdateToolError) as exc_info:
        validate_playlist_images_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "fake-image-content" not in str(exc_info.value.details)
    assert "signedUrl" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_playlist_images_update_handler_requires_oauth_access():
    """Reject update handler construction when OAuth access is unavailable."""
    with pytest.raises(PlaylistImagesUpdateToolError) as exc_info:
        build_playlist_images_update_handler(wrapper=FakePlaylistImagesUpdateWrapper(), executor=object(), oauth_token=None)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth"}


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"id": ""},
        {"id": "   "},
        {"id": []},
        {"id": "playlist-image-123", "part": "snippet"},
        {"id": "playlist-image-123", "body": {"snippet": {}}},
        {"id": "playlist-image-123", "media": {"mimeType": "image/jpeg", "content": "fake-image-content"}},
        {"id": "playlist-image-123", "thumbnailReplacement": True},
        {"id": "playlist-image-123", "rankBy": "views"},
    ],
)
def test_validate_playlist_images_delete_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed delete inputs, unsupported fields, body, media, and analytics shapes."""
    with pytest.raises(PlaylistImagesDeleteToolError) as exc_info:
        validate_playlist_images_delete_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "fake-image-content" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_playlist_images_delete_handler_requires_oauth_access():
    """Reject delete handler construction when OAuth access is unavailable."""
    with pytest.raises(PlaylistImagesDeleteToolError) as exc_info:
        build_playlist_images_delete_handler(wrapper=FakePlaylistImagesDeleteWrapper(), executor=object(), oauth_token=None)

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"field": "auth"}


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("authentication", "authentication_failed"),
        ("authorization", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("media_eligibility", "invalid_request"),
        ("not_found", "resource_not_found"),
        ("transient", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_update_handler_maps_upstream_failures_safely(upstream_category, expected_category):
    """Map upstream update failures into shared safe categories."""
    class FailingWrapper:
        """Raise one normalized upstream failure for update handler coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a configured upstream failure.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="playlist image update failed",
                category=upstream_category,
                retryable=False,
                upstream_status=403,
                details={
                    "field": "media",
                    "raw_media": "fake-image-content",
                    "oauth_token": "secret-token",
                    "stack": "traceback",
                },
            )

    handler = build_playlist_images_update_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesUpdateToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
            }
        )

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "media"}


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("authorization", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("transient", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_delete_handler_maps_upstream_failures_safely(upstream_category, expected_category):
    """Map upstream delete failures into shared safe categories."""
    class FailingWrapper:
        """Raise one normalized upstream failure for delete handler coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a configured upstream failure.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="playlist image delete failed",
                category=upstream_category,
                retryable=False,
                upstream_status=403,
                details={
                    "field": "id",
                    "oauth_token": "secret-token",
                    "raw_request": {"body": "unsafe"},
                    "stack": "traceback",
                },
            )

    handler = build_playlist_images_delete_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesDeleteToolError) as exc_info:
        handler({"id": "playlist-image-123"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "id"}


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
