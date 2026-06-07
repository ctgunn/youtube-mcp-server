"""Unit tests for the concrete Layer 2 ``captions_list`` tool."""

import pytest

from mcp_server.tools.youtube_common.captions import (
    CAPTIONS_DELETE_INPUT_SCHEMA,
    CAPTIONS_DOWNLOAD_INPUT_SCHEMA,
    CAPTIONS_INSERT_INPUT_SCHEMA,
    CAPTIONS_LIST_INPUT_SCHEMA,
    CAPTIONS_UPDATE_INPUT_SCHEMA,
    CaptionsDeleteToolError,
    CaptionsDownloadToolError,
    CaptionsInsertToolError,
    CaptionsListToolError,
    CaptionsUpdateToolError,
    build_captions_delete_tool_descriptor,
    build_captions_download_tool_descriptor,
    build_captions_insert_tool_descriptor,
    build_captions_list_tool_descriptor,
    build_captions_update_tool_descriptor,
    map_captions_delete_result,
    map_captions_download_result,
    map_captions_insert_result,
    map_captions_list_result,
    map_captions_update_result,
    validate_captions_delete_arguments,
    validate_captions_download_arguments,
    validate_captions_insert_arguments,
    validate_captions_list_arguments,
    validate_captions_update_arguments,
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


def _valid_captions_update_arguments() -> dict:
    """Return a representative valid ``captions_update`` request."""
    return {
        "part": "snippet",
        "body": {"id": "caption-1", "snippet": {"isDraft": False}},
    }


def _valid_captions_update_with_media_arguments() -> dict:
    """Return a representative valid ``captions_update`` media request."""
    return {
        "part": "id",
        "body": {"id": "caption-1"},
        "media": {"mimeType": "text/xml", "content": "caption text"},
    }


def _valid_captions_download_arguments() -> dict:
    """Return a representative valid ``captions_download`` request."""
    return {"id": "caption-1"}


def _valid_captions_download_with_conversion_arguments() -> dict:
    """Return a representative valid ``captions_download`` conversion request."""
    return {"id": "caption-1", "tfmt": "vtt", "tlang": "es"}


def _valid_captions_delete_arguments() -> dict:
    """Return a representative valid ``captions_delete`` request."""
    return {"id": "caption-1"}


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


def test_captions_update_schema_preserves_body_media_and_delegation_inputs():
    """Expose upstream-like request fields for ``captions_update``."""
    properties = CAPTIONS_UPDATE_INPUT_SCHEMA["properties"]

    assert CAPTIONS_UPDATE_INPUT_SCHEMA["required"] == ["part", "body"]
    assert {"part", "body", "media", "onBehalfOfContentOwner", "sync"}.issubset(properties)
    assert CAPTIONS_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_captions_download_schema_preserves_id_conversion_and_delegation_inputs():
    """Expose upstream-like request fields for ``captions_download``."""
    properties = CAPTIONS_DOWNLOAD_INPUT_SCHEMA["properties"]

    assert CAPTIONS_DOWNLOAD_INPUT_SCHEMA["required"] == ["id"]
    assert {"id", "tfmt", "tlang", "onBehalfOfContentOwner"}.issubset(properties)
    assert properties["tfmt"]["enum"] == ["sbv", "scc", "srt", "ttml", "vtt"]
    assert CAPTIONS_DOWNLOAD_INPUT_SCHEMA["additionalProperties"] is False


def test_captions_delete_schema_preserves_id_and_delegation_inputs():
    """Expose upstream-like request fields for ``captions_delete``."""
    properties = CAPTIONS_DELETE_INPUT_SCHEMA["properties"]

    assert CAPTIONS_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert {"id", "onBehalfOfContentOwner"}.issubset(properties)
    assert "body" not in properties
    assert CAPTIONS_DELETE_INPUT_SCHEMA["additionalProperties"] is False


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


def test_validate_captions_update_arguments_accepts_authorized_body_only_request():
    """Map an authorized body-only update request to safe context."""
    selected = validate_captions_update_arguments(_valid_captions_update_arguments(), oauth_token="oauth")

    assert selected == {"id": "caption-1", "isDraft": False}


def test_validate_captions_update_arguments_accepts_authorized_body_plus_media_request():
    """Map an authorized body-plus-media update request to safe context."""
    selected = validate_captions_update_arguments(_valid_captions_update_with_media_arguments(), oauth_token="oauth")

    assert selected == {"id": "caption-1", "mediaMimeType": "text/xml"}


def test_validate_captions_download_arguments_accepts_authorized_default_request():
    """Map an authorized default download request to safe context."""
    selected = validate_captions_download_arguments(_valid_captions_download_arguments(), oauth_token="oauth")

    assert selected == {"id": "caption-1"}


def test_validate_captions_download_arguments_accepts_authorized_conversion_request():
    """Map an authorized conversion download request to safe context."""
    selected = validate_captions_download_arguments(
        _valid_captions_download_with_conversion_arguments(),
        oauth_token="oauth",
    )

    assert selected == {"id": "caption-1", "tfmt": "vtt", "tlang": "es"}


def test_validate_captions_delete_arguments_accepts_authorized_request():
    """Map an authorized delete request to safe context."""
    selected = validate_captions_delete_arguments(_valid_captions_delete_arguments(), oauth_token="oauth")

    assert selected == {"id": "caption-1"}


def test_validate_captions_delete_arguments_rejects_request_body_shape():
    """Reject body-like delete input with safe body-specific details."""
    with pytest.raises(CaptionsDeleteToolError, match="accepts no request body") as exc_info:
        validate_captions_delete_arguments({"id": "caption-1", "body": {}}, oauth_token="oauth")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "body"}


def test_validate_captions_delete_arguments_rejects_unsupported_options():
    """Reject unsupported delete options without leaking unsafe diagnostics."""
    with pytest.raises(CaptionsDeleteToolError, match="supports only") as exc_info:
        validate_captions_delete_arguments({"id": "caption-1", "part": "snippet"}, oauth_token="oauth")

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details == {"field": "part"}


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


def test_map_captions_update_result_preserves_resource_update_and_safe_media_summary():
    """Preserve near-raw updated caption resource fields in the mapped result."""
    result = map_captions_update_result(
        {"id": "caption-1", "snippet": {"isDraft": False}},
        _valid_captions_update_with_media_arguments(),
    )

    assert result["item"] == {"id": "caption-1", "snippet": {"isDraft": False}}
    assert result["requestedParts"] == ["id"]
    assert result["endpoint"] == "captions.update"
    assert result["quotaCost"] == 450
    assert result["update"] == {"id": "caption-1"}
    assert result["media"] == {"mimeType": "text/xml", "contentProvided": True}
    assert "content" not in result["media"]


def test_map_captions_download_result_preserves_content_and_conversion_context():
    """Preserve near-raw downloaded content fields in the mapped result."""
    result = map_captions_download_result(
        {"content": "WEBVTT", "contentType": "text/vtt", "sizeBytes": 6},
        _valid_captions_download_with_conversion_arguments(),
    )

    assert result["content"] == "WEBVTT"
    assert result["contentType"] == "text/vtt"
    assert result["contentForm"] == "text"
    assert result["sizeBytes"] == 6
    assert result["endpoint"] == "captions.download"
    assert result["quotaCost"] == 200
    assert result["requestedFormat"] == "vtt"
    assert result["requestedLanguage"] == "es"
    assert result["download"] == {"id": "caption-1", "tfmt": "vtt", "tlang": "es"}


def test_map_captions_delete_result_preserves_acknowledgment_context():
    """Preserve near-raw deletion acknowledgment fields in the mapped result."""
    result = map_captions_delete_result({}, _valid_captions_delete_arguments())

    assert result["endpoint"] == "captions.delete"
    assert result["quotaCost"] == 50
    assert result["delete"] == {"id": "caption-1"}
    assert result["status"] == "deleted"
    assert result["responseStatus"] == 204
    assert result["hasResponseBody"] is False
    assert "item" not in result


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


def test_captions_update_handler_invokes_wrapper_for_authorized_body_request():
    """Call the injected Layer 1 update wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the update handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return an updated resource.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped updated caption resource.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"id": "caption-1", "snippet": {"isDraft": False}}

    descriptor = build_captions_update_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"](_valid_captions_update_arguments())

    assert result["item"]["id"] == "caption-1"
    assert result["endpoint"] == "captions.update"
    assert calls[0][1] == _valid_captions_update_arguments()
    assert calls[0][2] == "oauth_required"


def test_captions_download_handler_invokes_wrapper_for_authorized_default_request():
    """Call the injected Layer 1 download wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the download handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return downloaded content.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped downloaded caption content.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"content": "caption content", "contentType": "application/octet-stream"}

    descriptor = build_captions_download_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"](_valid_captions_download_arguments())

    assert result["content"] == "caption content"
    assert result["endpoint"] == "captions.download"
    assert calls[0][1] == _valid_captions_download_arguments()
    assert calls[0][2] == "oauth_required"


def test_captions_download_handler_invokes_wrapper_for_authorized_conversion_request():
    """Call the injected Layer 1 download wrapper with format and language options."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the conversion handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return converted content.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped converted caption content.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {"content": "WEBVTT", "contentType": "text/vtt"}

    descriptor = build_captions_download_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"](_valid_captions_download_with_conversion_arguments())

    assert result["requestedFormat"] == "vtt"
    assert result["requestedLanguage"] == "es"
    assert calls[0][1] == _valid_captions_download_with_conversion_arguments()


def test_captions_delete_handler_invokes_wrapper_for_authorized_request():
    """Call the injected Layer 1 delete wrapper through the concrete handler."""
    calls = []

    class FakeWrapper:
        """Capture Layer 1 wrapper calls made by the delete handler."""

        def call(self, executor, *, arguments, auth_context):
            """Record one fake Layer 1 call and return no-content acknowledgment.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :return: Upstream-shaped delete acknowledgment.
            """
            calls.append((executor, arguments, auth_context.mode.value))
            return {}

    descriptor = build_captions_delete_tool_descriptor(wrapper=FakeWrapper(), executor=object())

    result = descriptor["handler"](_valid_captions_delete_arguments())

    assert result["endpoint"] == "captions.delete"
    assert result["delete"] == {"id": "caption-1"}
    assert calls[0][1] == _valid_captions_delete_arguments()
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


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"body": {"id": "caption-1"}}, "requires part"),
        ({"part": "snippet"}, "requires body"),
        ({"part": "snippet", "body": {}}, "requires body.id"),
        ({"part": "snippet", "body": {"id": "   "}}, "requires body.id"),
    ],
)
def test_validate_captions_update_arguments_rejects_missing_body_fields(arguments, message):
    """Reject update requests with incomplete caption body."""
    with pytest.raises(CaptionsUpdateToolError, match=message):
        validate_captions_update_arguments(arguments, oauth_token="oauth")


def test_validate_captions_update_arguments_rejects_media_without_body():
    """Reject media-only update requests."""
    with pytest.raises(CaptionsUpdateToolError, match="requires body"):
        validate_captions_update_arguments(
            {"part": "id", "media": {"mimeType": "text/xml", "content": "caption text"}},
            oauth_token="oauth",
        )


def test_validate_captions_update_arguments_rejects_unsupported_media_descriptor():
    """Reject media descriptors that cannot identify replacement caption content."""
    arguments = _valid_captions_update_arguments()
    arguments["media"] = {"mimeType": "text/xml"}

    with pytest.raises(CaptionsUpdateToolError, match="requires media.content"):
        validate_captions_update_arguments(arguments, oauth_token="oauth")


def test_validate_captions_update_arguments_rejects_missing_oauth():
    """Reject caption update without eligible OAuth authorization."""
    with pytest.raises(CaptionsUpdateToolError, match="requires eligible OAuth authorization"):
        validate_captions_update_arguments(_valid_captions_update_arguments(), oauth_token=None)


def test_validate_captions_update_arguments_rejects_delegation_without_oauth():
    """Reject delegated update requests without eligible OAuth authorization."""
    arguments = _valid_captions_update_arguments()
    arguments["onBehalfOfContentOwner"] = "owner"

    with pytest.raises(CaptionsUpdateToolError, match="Delegated caption update requires eligible OAuth authorization"):
        validate_captions_update_arguments(arguments, oauth_token=None)


def test_validate_captions_update_arguments_rejects_invalid_sync():
    """Reject non-boolean deprecated sync values."""
    arguments = _valid_captions_update_with_media_arguments()
    arguments["sync"] = "yes"

    with pytest.raises(CaptionsUpdateToolError, match="sync must be a boolean"):
        validate_captions_update_arguments(arguments, oauth_token="oauth")


def test_validate_captions_update_arguments_accepts_deprecated_sync_with_media():
    """Allow deprecated upstream sync only with replacement media."""
    arguments = _valid_captions_update_with_media_arguments()
    arguments["sync"] = True

    selected = validate_captions_update_arguments(arguments, oauth_token="oauth")

    assert selected["syncDeprecated"] is True


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "requires id"),
        ({"id": "   "}, "requires id"),
        ({"id": "caption-1", "tfmt": "unsupported"}, "unsupported tfmt"),
        ({"id": "caption-1", "tlang": "spanish"}, "tlang must be a two-letter language code"),
    ],
)
def test_validate_captions_download_arguments_rejects_invalid_inputs(arguments, message):
    """Reject download requests with incomplete or unsupported input."""
    with pytest.raises(CaptionsDownloadToolError, match=message):
        validate_captions_download_arguments(arguments, oauth_token="oauth")


def test_validate_captions_download_arguments_rejects_missing_oauth():
    """Reject caption download without eligible OAuth authorization."""
    with pytest.raises(CaptionsDownloadToolError, match="requires eligible OAuth authorization"):
        validate_captions_download_arguments(_valid_captions_download_arguments(), oauth_token=None)


def test_validate_captions_download_arguments_rejects_delegation_without_oauth():
    """Reject delegated download requests without eligible OAuth authorization."""
    arguments = _valid_captions_download_arguments()
    arguments["onBehalfOfContentOwner"] = "owner"

    with pytest.raises(CaptionsDownloadToolError, match="Delegated caption download requires eligible OAuth authorization"):
        validate_captions_download_arguments(arguments, oauth_token=None)


def test_existing_captions_list_and_insert_validation_remains_unchanged():
    """Preserve existing captions list and insert validation behavior."""
    assert validate_captions_list_arguments(
        {"part": "snippet", "videoId": "video-123"},
        oauth_token="oauth",
    ) == {"videoId": "video-123"}
    assert validate_captions_insert_arguments(
        _valid_captions_insert_arguments(),
        oauth_token="oauth",
    )["videoId"] == "video-123"
    assert validate_captions_update_arguments(
        _valid_captions_update_arguments(),
        oauth_token="oauth",
    )["id"] == "caption-1"
