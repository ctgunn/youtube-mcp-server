"""Contract tests for the Layer 2 ``playlistImages_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.playlist_images import (
    PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES,
    PLAYLIST_IMAGES_LIST_DESCRIPTION,
    PLAYLIST_IMAGES_LIST_INPUT_SCHEMA,
    PLAYLIST_IMAGES_LIST_TOOL_NAME,
    PlaylistImagesListToolError,
    build_playlist_images_list_contract,
    build_playlist_images_list_handler,
    build_playlist_images_list_tool_descriptor,
    validate_playlist_images_list_arguments,
)


def test_playlist_images_list_public_symbols_are_exported():
    """Expose ``playlistImages_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_images

    assert youtube_common.PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert PLAYLIST_IMAGES_LIST_TOOL_NAME == "playlistImages_list"
    assert callable(playlist_images.build_playlist_images_list_tool_descriptor)


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


def test_playlist_images_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_playlist_images_list_tool_descriptor()

    assert descriptor["name"] == "playlistImages_list"
    assert descriptor["inputSchema"] == PLAYLIST_IMAGES_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlistImages.list"
    assert descriptor["metadata"]["quotaCost"] == 1


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
