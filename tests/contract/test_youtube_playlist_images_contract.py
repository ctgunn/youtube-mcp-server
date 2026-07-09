"""Contract tests for the Layer 2 ``playlistImages_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.playlist_images import (
    PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES,
    PLAYLIST_IMAGES_DELETE_CAVEATS,
    PLAYLIST_IMAGES_DELETE_DESCRIPTION,
    PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA,
    PLAYLIST_IMAGES_DELETE_TOOL_NAME,
    PLAYLIST_IMAGES_DELETE_USAGE_NOTES,
    PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES,
    PLAYLIST_IMAGES_INSERT_CAVEATS,
    PLAYLIST_IMAGES_INSERT_DESCRIPTION,
    PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA,
    PLAYLIST_IMAGES_INSERT_TOOL_NAME,
    PLAYLIST_IMAGES_INSERT_USAGE_NOTES,
    PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES,
    PLAYLIST_IMAGES_LIST_DESCRIPTION,
    PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
    PLAYLIST_IMAGES_LIST_TOOL_NAME,
    PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES,
    PLAYLIST_IMAGES_UPDATE_CAVEATS,
    PLAYLIST_IMAGES_UPDATE_DESCRIPTION,
    PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA,
    PLAYLIST_IMAGES_UPDATE_TOOL_NAME,
    PLAYLIST_IMAGES_UPDATE_USAGE_NOTES,
    PlaylistImagesDeleteToolError,
    PlaylistImagesInsertToolError,
    PlaylistImagesUpdateToolError,
    build_playlist_images_delete_contract,
    build_playlist_images_delete_handler,
    build_playlist_images_delete_tool_descriptor,
    build_playlist_images_insert_contract,
    build_playlist_images_insert_handler,
    build_playlist_images_insert_tool_descriptor,
    PlaylistImagesListToolError,
    build_playlist_images_list_contract,
    build_playlist_images_list_handler,
    build_playlist_images_list_tool_descriptor,
    build_playlist_images_update_contract,
    build_playlist_images_update_handler,
    build_playlist_images_update_tool_descriptor,
    validate_playlist_images_delete_arguments,
    validate_playlist_images_insert_arguments,
    validate_playlist_images_list_arguments,
    validate_playlist_images_update_arguments,
)


def test_playlist_images_list_public_symbols_are_exported():
    """Expose ``playlistImages_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_images

    assert youtube_common.PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert callable(playlist_images.build_playlist_images_list_tool_descriptor)


def test_playlist_images_insert_public_symbols_are_exported():
    """Expose ``playlistImages_insert`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_images

    assert youtube_common.PLAYLIST_IMAGES_INSERT_TOOL_NAME == "playlistImages_insert"
    assert PLAYLIST_IMAGES_INSERT_TOOL_NAME == "playlistImages_insert"
    assert callable(playlist_images.build_playlist_images_insert_tool_descriptor)


def test_playlist_images_update_public_symbols_are_exported():
    """Expose ``playlistImages_update`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_images

    assert youtube_common.PLAYLIST_IMAGES_UPDATE_TOOL_NAME == "playlistImages_update"
    assert PLAYLIST_IMAGES_UPDATE_TOOL_NAME == "playlistImages_update"
    assert callable(playlist_images.build_playlist_images_update_tool_descriptor)


def test_playlist_images_delete_public_symbols_are_exported():
    """Expose ``playlistImages_delete`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_images

    assert youtube_common.PLAYLIST_IMAGES_DELETE_TOOL_NAME == "playlistImages_delete"
    assert PLAYLIST_IMAGES_DELETE_TOOL_NAME == "playlistImages_delete"
    assert callable(playlist_images.build_playlist_images_delete_tool_descriptor)


def test_playlist_images_list_schema_preserves_selector_and_paging_inputs():
    """Expose the upstream-like request fields for ``playlistImages_list``."""
    properties = PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["playlistId"] == {"type": "string", "minLength": 1}
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert properties["pageToken"] == {"type": "string", "minLength": 1}
    assert properties["maxResults"]["type"] == "integer"
    assert properties["maxResults"]["minimum"] == 0
    assert {"required": ["playlistId"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]
    assert {"required": ["id"]} in PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["oneOf"]
    assert PLAYLIST_IMAGES_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_insert_schema_preserves_required_upload_inputs():
    """Expose the upstream-like request fields for ``playlistImages_insert``."""
    properties = PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["required"] == ["part", "body", "media"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["body"]["type"] == "object"
    assert properties["body"]["required"] == ["snippet"]
    assert properties["body"]["additionalProperties"] is False
    assert properties["media"]["type"] == "object"
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert properties["media"]["additionalProperties"] is False
    assert PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_update_schema_preserves_required_upload_inputs():
    """Expose the upstream-like request fields for ``playlistImages_update``."""
    properties = PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["required"] == ["part", "body", "media"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["body"]["type"] == "object"
    assert properties["body"]["required"] == ["id", "snippet"]
    assert properties["body"]["additionalProperties"] is False
    assert properties["media"]["type"] == "object"
    assert properties["media"]["required"] == ["mimeType", "content"]
    assert properties["media"]["additionalProperties"] is False
    assert PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_delete_schema_preserves_required_target_only_input():
    """Expose only the upstream delete target id for ``playlistImages_delete``."""
    properties = PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["properties"]

    assert PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert "part" not in properties
    assert "body" not in properties
    assert "media" not in properties
    assert PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_images_list_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list response metadata."""
    contract = build_playlist_images_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistImages_list"
    assert metadata["upstream"]["operationKey"] == "playlistImages.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert metadata["responseConvention"]["selectorFields"] == ["playlistId", "id"]


def test_playlist_images_insert_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and mutation response metadata."""
    contract = build_playlist_images_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistImages_insert"
    assert metadata["upstream"]["operationKey"] == "playlistImages.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"


def test_playlist_images_update_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and update response metadata."""
    contract = build_playlist_images_update_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistImages_update"
    assert metadata["upstream"]["operationKey"] == "playlistImages.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"


def test_playlist_images_delete_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and deletion response metadata."""
    contract = build_playlist_images_delete_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistImages_delete"
    assert metadata["upstream"]["operationKey"] == "playlistImages.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["id"]
    assert set(metadata["inputContract"]["properties"]) == {"id"}
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["successStatus"] == 204
    assert metadata["responseConvention"]["bodyPolicy"] == "no_upstream_body"


def test_playlist_images_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_playlist_images_list_tool_descriptor()

    assert descriptor["name"] == "playlistImages_list"
    assert descriptor["inputSchema"] == PLAYLIST_IMAGES_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistImages.list"
    assert descriptor["metadata"]["quotaCost"] == 1


def test_playlist_images_insert_descriptor_uses_public_contract_shape():
    """Build an executable insert descriptor aligned with the public contract."""
    descriptor = build_playlist_images_insert_tool_descriptor()

    assert descriptor["name"] == "playlistImages_insert"
    assert descriptor["inputSchema"] == PLAYLIST_IMAGES_INSERT_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistImages.insert"
    assert descriptor["metadata"]["quotaCost"] == 50


def test_playlist_images_update_descriptor_uses_public_contract_shape():
    """Build an executable update descriptor aligned with the public contract."""
    descriptor = build_playlist_images_update_tool_descriptor()

    assert descriptor["name"] == "playlistImages_update"
    assert descriptor["inputSchema"] == PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistImages.update"
    assert descriptor["metadata"]["quotaCost"] == 50


def test_playlist_images_delete_descriptor_uses_public_contract_shape():
    """Build an executable delete descriptor aligned with the public contract."""
    descriptor = build_playlist_images_delete_tool_descriptor()

    assert descriptor["name"] == "playlistImages_delete"
    assert descriptor["inputSchema"] == PLAYLIST_IMAGES_DELETE_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistImages.delete"
    assert descriptor["metadata"]["quotaCost"] == 50


def test_playlist_images_insert_metadata_documents_upload_access_and_boundaries():
    """Expose quota, OAuth, body, media, examples, mutation, and out-of-scope guidance safely."""
    descriptor = build_playlist_images_insert_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert PLAYLIST_IMAGES_INSERT_DESCRIPTION == descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLIST_IMAGES_INSERT_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLIST_IMAGES_INSERT_CAVEATS)
    assert "Quota cost: 50" in metadata_text
    assert "oauth_required" in metadata_text
    assert "body" in metadata_text
    assert "body.snippet" in metadata_text
    assert "media.mimeType" in metadata_text
    assert "media.content" in metadata_text
    assert "raw media content is never echoed" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert "analytics" in metadata_text
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "raw_media" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_playlist_images_update_metadata_documents_upload_access_and_boundaries():
    """Expose quota, OAuth, target body, media, examples, mutation, and boundaries safely."""
    descriptor = build_playlist_images_update_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert PLAYLIST_IMAGES_UPDATE_DESCRIPTION == descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLIST_IMAGES_UPDATE_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLIST_IMAGES_UPDATE_CAVEATS)
    assert "Quota cost: 50" in metadata_text
    assert "oauth_required" in metadata_text
    assert "body.id" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "media.mimeType" in metadata_text
    assert "media.content" in metadata_text
    assert "raw media content is never echoed" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert "analytics" in metadata_text
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "raw_media" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_playlist_images_delete_metadata_documents_destructive_access_and_boundaries():
    """Expose quota, OAuth, target id, examples, deletion, and boundaries safely."""
    descriptor = build_playlist_images_delete_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert PLAYLIST_IMAGES_DELETE_DESCRIPTION == descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLIST_IMAGES_DELETE_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLIST_IMAGES_DELETE_CAVEATS)
    assert "Quota cost: 50" in metadata_text
    assert "oauth_required" in metadata_text
    assert "id" in metadata_text
    assert "204 No Content" in metadata_text
    assert "destructive" in metadata_text.lower()
    assert "request body" in metadata_text
    assert "media" in metadata_text
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "raw_media" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_playlist_images_insert_examples_cover_success_failures_and_boundaries():
    """Expose insert examples for success, validation, access, quota, and out-of-scope outcomes."""
    descriptor = build_playlist_images_insert_tool_descriptor()
    example_names = {example["name"] for example in PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES}
    descriptor_example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert {
        "authorized_playlist_image_insert",
        "missing_part",
        "invalid_part",
        "missing_body",
        "invalid_body",
        "missing_media",
        "unsupported_media",
        "access_failure",
        "quota_or_upstream_insert_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)
    assert example_names == descriptor_example_names
    assert "image/gif" in str(PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES)
    assert "thumbnailReplacement" in str(PLAYLIST_IMAGES_INSERT_CALLER_EXAMPLES)


def test_playlist_images_update_examples_cover_success_failures_and_boundaries():
    """Expose update examples for success, validation, access, quota, and out-of-scope outcomes."""
    descriptor = build_playlist_images_update_tool_descriptor()
    example_names = {example["name"] for example in PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES}
    descriptor_example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert {
        "authorized_playlist_image_update",
        "missing_part",
        "invalid_part",
        "missing_body",
        "invalid_body",
        "missing_target_identity",
        "missing_playlist_context",
        "missing_media",
        "unsupported_media",
        "access_failure",
        "quota_or_upstream_update_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)
    assert example_names == descriptor_example_names
    assert "image/gif" in str(PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES)
    assert "thumbnailReplacement" in str(PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES)


def test_playlist_images_delete_examples_cover_success_failures_and_boundaries():
    """Expose delete examples for success, validation, access, quota, and out-of-scope outcomes."""
    descriptor = build_playlist_images_delete_tool_descriptor()
    example_names = {example["name"] for example in PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES}
    descriptor_example_names = {example["name"] for example in descriptor["metadata"]["examples"]}

    assert {
        "authorized_playlist_image_delete",
        "missing_id",
        "invalid_id",
        "unsupported_body",
        "unsupported_media",
        "access_failure",
        "quota_or_upstream_delete_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)
    assert example_names == descriptor_example_names
    assert "media" in str(PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES)
    assert "thumbnailReplacement" in str(PLAYLIST_IMAGES_DELETE_CALLER_EXAMPLES)


def test_playlist_images_list_contract_documents_successful_result_shape():
    """Document the playlist-image list result shape."""
    result = build_playlist_images_list_tool_descriptor()["handler"](
        {"part": "snippet", "playlistId": "PL123", "pageToken": "NEXT_PAGE", "maxResults": 25}
    )

    assert result["endpoint"] == "playlistImages.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "playlistId", "value": "PL123"}
    assert result["paging"] == {"pageToken": "NEXT_PAGE", "maxResults": 25}
    assert result["auth"] == {"mode": "oauth_required"}
    assert "items" in result


def test_playlist_images_insert_contract_documents_successful_result_shape():
    """Document the playlist-image insert result shape."""
    result = build_playlist_images_insert_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {"snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        }
    )

    assert result["endpoint"] == "playlistImages.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["bodyContext"] == {"hasSnippet": True, "playlistId": "PL123"}
    assert result["mediaContext"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-image-123"
    assert "fake-image-content" not in str(result)


def test_playlist_images_update_contract_documents_successful_result_shape():
    """Document the playlist-image update result shape."""
    result = build_playlist_images_update_tool_descriptor()["handler"](
        {
            "part": "id,snippet",
            "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "medium"}},
            "media": {"mimeType": "image/jpeg", "content": "fake-image-content"},
        }
    )

    assert result["endpoint"] == "playlistImages.update"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["bodyContext"] == {"id": "playlist-image-123", "hasSnippet": True, "playlistId": "PL123"}
    assert result["mediaContext"] == {"mimeType": "image/jpeg", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["item"]["id"] == "playlist-image-123"
    assert "fake-image-content" not in str(result)


def test_playlist_images_delete_contract_documents_successful_result_shape():
    """Document the playlist-image delete result shape."""
    result = build_playlist_images_delete_tool_descriptor()["handler"]({"id": "playlist-image-123"})

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


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "part"),
        ({"part": "statistics", "body": {"snippet": {"playlistId": "PL123"}}, "media": {"mimeType": "image/jpeg", "content": "raw"}}, "part"),
        ({"part": "snippet", "media": {"mimeType": "image/jpeg", "content": "raw"}}, "body"),
        ({"part": "snippet", "body": {} , "media": {"mimeType": "image/jpeg", "content": "raw"}}, "body.snippet"),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123"}, "thumbnailReplacement": True},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body.thumbnailReplacement",
        ),
        ({"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}}, "media"),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/gif", "content": "raw"},
            },
            "media.mimeType",
        ),
    ],
)
def test_playlist_images_insert_validation_failures_are_safe(arguments, message):
    """Map invalid insert requests to safe validation errors without raw upload details."""
    with pytest.raises(PlaylistImagesInsertToolError) as exc_info:
        validate_playlist_images_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value) or message in str(exc_info.value.details)
    assert "raw" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "part"),
        (
            {
                "part": "statistics",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "part",
        ),
        (
            {
                "part": "snippet",
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body",
        ),
        (
            {
                "part": "snippet",
                "body": {},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body.id",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123"},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body.snippet",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"type": "medium"}},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body.snippet.playlistId",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "playlist-image-123",
                    "snippet": {"playlistId": "PL123"},
                    "thumbnailReplacement": True,
                },
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            },
            "body.thumbnailReplacement",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
            },
            "media",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/gif", "content": "raw"},
            },
            "media.mimeType",
        ),
    ],
)
def test_playlist_images_update_validation_failures_are_safe(arguments, message):
    """Map invalid update requests to safe validation errors without raw upload details."""
    with pytest.raises(PlaylistImagesUpdateToolError) as exc_info:
        validate_playlist_images_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value) or message in str(exc_info.value.details)
    assert "raw" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "id"),
        ({"id": ""}, "id"),
        ({"id": "   "}, "id"),
        ({"id": 123}, "id"),
        ({"id": "playlist-image-123", "part": "snippet"}, "part"),
        ({"id": "playlist-image-123", "body": {"snippet": {}}}, "body"),
        ({"id": "playlist-image-123", "media": {"content": "raw"}}, "media"),
        ({"id": "playlist-image-123", "thumbnailReplacement": True}, "thumbnailReplacement"),
    ],
)
def test_playlist_images_delete_validation_failures_are_safe(arguments, message):
    """Map invalid delete requests to safe validation errors without sensitive diagnostics."""
    with pytest.raises(PlaylistImagesDeleteToolError) as exc_info:
        validate_playlist_images_delete_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value) or message in str(exc_info.value.details)
    assert "raw" not in str(exc_info.value.details)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("media_eligibility", "invalid_request"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_insert_handler_sanitizes_upstream_failures(upstream_category, expected_category):
    """Map normalized insert failures to safe categories and sanitized details."""
    class FailingWrapper:
        """Raise a normalized upstream error for insert handler mapping coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an upstream failure containing unsafe diagnostic fields.

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
                    "oauth_token": "secret",
                    "raw_media": "binary-content",
                    "raw_request": {"body": "unsafe"},
                    "stack": "trace",
                },
            )

    handler = build_playlist_images_insert_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesInsertToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            }
        )

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "media"}


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("media_eligibility", "invalid_request"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_update_handler_sanitizes_upstream_failures(upstream_category, expected_category):
    """Map normalized update failures to safe categories and sanitized details."""
    class FailingWrapper:
        """Raise a normalized upstream error for update handler mapping coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an upstream failure containing unsafe diagnostic fields.

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
                    "oauth_token": "secret",
                    "raw_media": "binary-content",
                    "raw_request": {"body": "unsafe"},
                    "stack": "trace",
                },
            )

    handler = build_playlist_images_update_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesUpdateToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                "media": {"mimeType": "image/jpeg", "content": "raw"},
            }
        )

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "media"}


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("transient", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_delete_handler_sanitizes_upstream_failures(upstream_category, expected_category):
    """Map normalized delete failures to safe categories and sanitized details."""
    class FailingWrapper:
        """Raise a normalized upstream error for delete handler mapping coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an upstream failure containing unsafe diagnostic fields.

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
                    "oauth_token": "secret",
                    "raw_request": {"body": "unsafe"},
                    "stack": "trace",
                },
            )

    handler = build_playlist_images_delete_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesDeleteToolError) as exc_info:
        handler({"id": "playlist-image-123"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "id"}


def test_playlist_images_list_metadata_documents_access_selectors_and_boundaries():
    """Expose quota, OAuth, selectors, paging, examples, and out-of-scope guidance safely."""
    descriptor = build_playlist_images_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert PLAYLIST_IMAGES_LIST_DESCRIPTION == descriptor["description"]
    assert "Quota cost: 1" in metadata_text
    assert "oauth_required" in metadata_text
    assert "playlistId" in metadata_text
    assert "id" in metadata_text
    assert "pageToken" in metadata_text
    assert "maxResults" in metadata_text
    assert "playlist image insertion" in metadata_text
    assert "thumbnail replacement" in metadata_text
    assert "analytics" in metadata_text
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_playlist_images_list_examples_cover_success_and_failure_cases():
    """Expose representative examples for success, empty, validation, auth, and boundary outcomes."""
    example_names = {example["name"] for example in PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES}

    assert {
        "playlist_scoped_image_listing",
        "direct_image_lookup",
        "paged_playlist_image_listing",
        "empty_success",
        "missing_part",
        "invalid_part",
        "missing_selector",
        "conflicting_selector",
        "paging_with_id",
        "access_failure",
        "out_of_scope_image_management_request",
    }.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "part"),
        ({"part": "statistics", "playlistId": "PL123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "playlistId": "PL123", "id": "img-123"}, "selector"),
        ({"part": "snippet", "id": "img-123", "pageToken": "NEXT_PAGE"}, "pageToken"),
        ({"part": "snippet", "playlistId": "PL123", "media": {"content": "raw"}}, "media"),
    ],
)
def test_playlist_images_list_validation_failures_are_safe(arguments, message):
    """Map unsupported requests to safe validation errors without sensitive diagnostics."""
    with pytest.raises(PlaylistImagesListToolError) as exc_info:
        validate_playlist_images_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


@pytest.mark.parametrize(
    ("upstream_category", "expected_category"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("quota", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_playlist_images_list_handler_sanitizes_upstream_failures(upstream_category, expected_category):
    """Map normalized upstream failures to safe caller-facing categories."""
    class FailingWrapper:
        """Raise a normalized upstream error for handler mapping coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an upstream failure containing unsafe diagnostic fields.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="playlist image request failed",
                category=upstream_category,
                retryable=False,
                upstream_status=403,
                details={"field": "playlistId", "oauth_token": "secret", "stack": "trace"},
            )

    handler = build_playlist_images_list_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(PlaylistImagesListToolError) as exc_info:
        handler({"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category == expected_category
    assert exc_info.value.details == {"field": "playlistId"}
