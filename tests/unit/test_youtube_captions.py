"""Unit tests for the concrete Layer 2 ``captions_list`` tool."""

import pytest

from mcp_server.tools.youtube_common.captions import (
    CAPTIONS_INSERT_INPUT_SCHEMA,
    CAPTIONS_LIST_INPUT_SCHEMA,
    CaptionsInsertToolError,
    CaptionsListToolError,
    build_captions_insert_tool_descriptor,
    build_captions_list_tool_descriptor,
    map_captions_insert_result,
    map_captions_list_result,
    validate_captions_insert_arguments,
    validate_captions_list_arguments,
)


def _valid_captions_insert_arguments() -> dict:
    """Return a representative valid ``captions_insert`` request."""
    return {
        "part": "snippet",
        "body": {
            "snippet": {
                "videoId": "video-123",
                "language": "en",
                "name": "English captions",
                "isDraft": False,
            }
        },
        "media": {"mimeType": "text/xml", "content": "caption text"},
    }


def test_captions_list_schema_preserves_lookup_pagination_and_delegation_inputs():
    """Expose the upstream-like request fields for ``captions_list``."""
    properties = CAPTIONS_LIST_INPUT_SCHEMA["properties"]

    assert CAPTIONS_LIST_INPUT_SCHEMA["required"] == ["part", "videoId"]
    assert {"part", "videoId", "id", "maxResults", "pageToken", "onBehalfOfContentOwner"}.issubset(properties)
    assert CAPTIONS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_captions_insert_schema_preserves_metadata_media_and_delegation_inputs():
    """Expose upstream-like request fields for ``captions_insert``."""
    properties = CAPTIONS_INSERT_INPUT_SCHEMA["properties"]

    assert CAPTIONS_INSERT_INPUT_SCHEMA["required"] == ["part", "body", "media"]
    assert {"part", "body", "media", "onBehalfOfContentOwner", "sync"}.issubset(properties)
    assert CAPTIONS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_captions_list_arguments_accepts_authorized_video_request():
    """Map an authorized video request to the video caption lookup path."""
    selected = validate_captions_list_arguments(
        {"part": "snippet,id", "videoId": "video-123", "maxResults": 5},
        oauth_token="oauth",
    )

    assert selected == {"videoId": "video-123"}


def test_validate_captions_insert_arguments_accepts_authorized_metadata_and_media_request():
    """Map an authorized insert request to safe metadata and media context."""
    selected = validate_captions_insert_arguments(_valid_captions_insert_arguments(), oauth_token="oauth")

    assert selected == {
        "videoId": "video-123",
        "language": "en",
        "name": "English captions",
        "mediaMimeType": "text/xml",
    }


def test_validate_captions_list_arguments_accepts_caption_id_filter():
    """Allow caption track identifiers only as a video-scoped filter."""
    selected = validate_captions_list_arguments(
        {"part": "snippet", "videoId": "video-123", "id": "caption-1"},
        oauth_token="oauth",
    )

    assert selected == {"videoId": "video-123", "id": "caption-1"}


def test_map_captions_list_result_preserves_items_parts_and_pagination():
    """Preserve near-raw caption collection fields in the mapped result."""
    result = map_captions_list_result(
        {
            "items": [{"id": "caption-1"}],
            "nextPageToken": "NEXT",
            "prevPageToken": "PREV",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet,id", "videoId": "video-123", "onBehalfOfContentOwner": "owner"},
    )

    assert result["items"] == [{"id": "caption-1"}]
    assert result["requestedParts"] == ["snippet", "id"]
    assert result["nextPageToken"] == "NEXT"
    assert result["prevPageToken"] == "PREV"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}
    assert result["endpoint"] == "captions.list"
    assert result["quotaCost"] == 50
    assert result["lookup"] == {"videoId": "video-123"}
    assert result["delegation"] == {"onBehalfOfContentOwner": True}


def test_map_captions_insert_result_preserves_resource_metadata_and_safe_media_summary():
    """Preserve near-raw created caption resource fields in the mapped result."""
    result = map_captions_insert_result(
        {"id": "caption-1", "snippet": {"videoId": "video-123", "language": "en"}},
        _valid_captions_insert_arguments(),
    )

    assert result["item"] == {"id": "caption-1", "snippet": {"videoId": "video-123", "language": "en"}}
    assert result["requestedParts"] == ["snippet"]
    assert result["endpoint"] == "captions.insert"
    assert result["quotaCost"] == 400
    assert result["metadata"] == {
        "videoId": "video-123",
        "language": "en",
        "name": "English captions",
        "isDraft": False,
    }
    assert result["media"] == {"mimeType": "text/xml", "contentProvided": True}
    assert "content" not in result["media"]


def test_map_captions_list_result_preserves_empty_collection_success():
    """Treat a valid empty caption response as a successful collection."""
    result = map_captions_list_result({"items": []}, {"part": "snippet", "videoId": "video-123"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_captions_list_handler_invokes_wrapper_for_authorized_video_request():
    """Call the injected Layer 1 wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the Layer 2 handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a paginated result.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped caption list response.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"items": [{"id": "caption-1"}], "nextPageToken": "NEXT"}

    descriptor = build_captions_list_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"]({"part": "snippet", "videoId": "video-123"})

    assert result["items"] == [{"id": "caption-1"}]
    assert result["nextPageToken"] == "NEXT"
    assert calls[0][1] == {"part": "snippet", "videoId": "video-123"}
    assert calls[0][2] == "oauth_required"


def test_captions_insert_handler_invokes_wrapper_for_authorized_metadata_and_media_request():
    """Call the injected Layer 1 insert wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the insert handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return a created resource.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped created caption resource.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"id": "caption-1", "snippet": {"videoId": "video-123", "language": "en"}}

    descriptor = build_captions_insert_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"](_valid_captions_insert_arguments())

    assert result["item"]["id"] == "caption-1"
    assert result["endpoint"] == "captions.insert"
    assert calls[0][1] == _valid_captions_insert_arguments()
    assert calls[0][2] == "oauth_required"


def test_validate_captions_list_arguments_rejects_missing_part():
    """Reject requests without part selection."""
    with pytest.raises(CaptionsListToolError, match="requires part"):
        validate_captions_list_arguments({"videoId": "video-123"}, oauth_token="oauth")


def test_validate_captions_list_arguments_rejects_missing_video_id():
    """Reject requests without required video context."""
    with pytest.raises(CaptionsListToolError, match="requires videoId"):
        validate_captions_list_arguments({"part": "snippet"}, oauth_token="oauth")


def test_validate_captions_list_arguments_rejects_id_without_video_id():
    """Reject caption identifier filters without video context."""
    with pytest.raises(CaptionsListToolError, match="requires videoId"):
        validate_captions_list_arguments({"part": "snippet", "id": "caption-1"}, oauth_token="oauth")


def test_validate_captions_list_arguments_rejects_missing_oauth():
    """Reject caption listing without eligible OAuth authorization."""
    with pytest.raises(CaptionsListToolError, match="requires eligible OAuth authorization"):
        validate_captions_list_arguments({"part": "snippet", "videoId": "video-123"}, oauth_token=None)


def test_validate_captions_list_arguments_rejects_invalid_max_results():
    """Reject page-size values outside the upstream range."""
    with pytest.raises(CaptionsListToolError, match="maxResults must be between 0 and 50"):
        validate_captions_list_arguments(
            {"part": "snippet", "videoId": "video-123", "maxResults": 51},
            oauth_token="oauth",
        )


def test_validate_captions_list_arguments_rejects_delegation_without_oauth():
    """Reject delegated requests without eligible OAuth authorization."""
    with pytest.raises(CaptionsListToolError, match="Delegated caption listing requires eligible OAuth authorization"):
        validate_captions_list_arguments(
            {"part": "snippet", "videoId": "video-123", "onBehalfOfContentOwner": "owner"},
            oauth_token=None,
        )


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}}, "requires part"),
        ({"part": "snippet", "media": {"mimeType": "text/xml", "content": "caption text"}}, "requires body"),
        ({"part": "snippet", "body": {"snippet": {"language": "en", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}}, "requires body.snippet.videoId"),
        ({"part": "snippet", "body": {"snippet": {"videoId": "video-123", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}}, "requires body.snippet.language"),
        ({"part": "snippet", "body": {"snippet": {"videoId": "video-123", "language": "en"}}, "media": {"mimeType": "text/xml", "content": "caption text"}}, "requires body.snippet.name"),
    ],
)
def test_validate_captions_insert_arguments_rejects_missing_metadata(arguments, message):
    """Reject insert requests with incomplete caption metadata."""
    with pytest.raises(CaptionsInsertToolError, match=message):
        validate_captions_insert_arguments(arguments, oauth_token="oauth")


def test_validate_captions_insert_arguments_rejects_missing_media():
    """Reject metadata-only insert requests."""
    arguments = _valid_captions_insert_arguments()
    arguments.pop("media")

    with pytest.raises(CaptionsInsertToolError, match="requires media"):
        validate_captions_insert_arguments(arguments, oauth_token="oauth")


def test_validate_captions_insert_arguments_rejects_unsupported_media_descriptor():
    """Reject media descriptors that cannot identify caption upload content."""
    arguments = _valid_captions_insert_arguments()
    arguments["media"] = {"mimeType": "text/xml"}

    with pytest.raises(CaptionsInsertToolError, match="requires media.content"):
        validate_captions_insert_arguments(arguments, oauth_token="oauth")


def test_validate_captions_insert_arguments_rejects_missing_oauth():
    """Reject caption insertion without eligible OAuth authorization."""
    with pytest.raises(CaptionsInsertToolError, match="requires eligible OAuth authorization"):
        validate_captions_insert_arguments(_valid_captions_insert_arguments(), oauth_token=None)


def test_validate_captions_insert_arguments_rejects_delegation_without_oauth():
    """Reject delegated insert requests without eligible OAuth authorization."""
    arguments = _valid_captions_insert_arguments()
    arguments["onBehalfOfContentOwner"] = "owner"

    with pytest.raises(CaptionsInsertToolError, match="Delegated caption insertion requires eligible OAuth authorization"):
        validate_captions_insert_arguments(arguments, oauth_token=None)


def test_validate_captions_insert_arguments_accepts_deprecated_sync_with_oauth():
    """Allow deprecated upstream sync only as an explicit caller option."""
    arguments = _valid_captions_insert_arguments()
    arguments["sync"] = True

    selected = validate_captions_insert_arguments(arguments, oauth_token="oauth")

    assert selected["syncDeprecated"] is True
