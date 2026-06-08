"""Unit tests for the concrete Layer 2 ``channelBanners_insert`` tool."""

import pytest

from mcp_server.tools.youtube_common.channel_banners import (
    CHANNEL_BANNERS_MAX_BYTES,
    CHANNEL_BANNERS_INSERT_INPUT_SCHEMA,
    ChannelBannersInsertToolError,
    build_channel_banners_insert_tool_descriptor,
    map_channel_banners_insert_result,
    validate_channel_banners_insert_arguments,
)


def _valid_channel_banners_insert_arguments() -> dict:
    """Return a representative valid ``channelBanners_insert`` request."""
    return {
        "media": {
            "mimeType": "image/png",
            "content": "safe image content",
            "filename": "banner.png",
            "sizeBytes": 2048,
        }
    }


def test_channel_banners_insert_schema_requires_media_and_delegation_input():
    """Expose the upstream-like request fields for ``channelBanners_insert``."""
    properties = CHANNEL_BANNERS_INSERT_INPUT_SCHEMA["properties"]

    assert CHANNEL_BANNERS_INSERT_INPUT_SCHEMA["required"] == ["media"]
    assert {"media", "onBehalfOfContentOwner"}.issubset(properties)
    assert {"mimeType", "content", "contentRef", "filename", "sizeBytes"}.issubset(
        properties["media"]["properties"]
    )
    assert CHANNEL_BANNERS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_channel_banners_insert_arguments_accepts_authorized_media_request():
    """Map an authorized upload request to safe media context."""
    selected = validate_channel_banners_insert_arguments(
        _valid_channel_banners_insert_arguments(),
        oauth_token="oauth",
    )

    assert selected == {
        "mediaMimeType": "image/png",
        "filename": "banner.png",
        "sizeBytes": 2048,
        "contentProvided": True,
    }


def test_map_channel_banners_insert_result_preserves_resource_and_safe_media_summary():
    """Preserve near-raw channel banner fields in the mapped result."""
    response = {
        "kind": "youtube#channelBannerResource",
        "etag": "etag-value",
        "url": "https://yt3.googleusercontent.com/example-banner",
    }

    result = map_channel_banners_insert_result(response, _valid_channel_banners_insert_arguments())

    assert result["endpoint"] == "channelBanners.insert"
    assert result["quotaCost"] == 50
    assert result["item"] == response
    assert result["url"] == response["url"]
    assert result["media"] == {
        "mimeType": "image/png",
        "filename": "banner.png",
        "sizeBytes": 2048,
        "contentProvided": True,
    }
    assert "content" not in result["media"]
    assert "active" not in result


def test_channel_banners_insert_descriptor_exposes_executable_handler():
    """Build an executable descriptor for ``channelBanners_insert``."""
    descriptor = build_channel_banners_insert_tool_descriptor()

    assert descriptor["name"] == "channelBanners_insert"
    assert descriptor["inputSchema"]["required"] == ["media"]
    assert callable(descriptor["handler"])


def test_validate_channel_banners_insert_arguments_accepts_delegation_with_authorization():
    """Accept delegated upload context when authorization is available."""
    arguments = {
        **_valid_channel_banners_insert_arguments(),
        "onBehalfOfContentOwner": "content-owner-id",
    }

    selected = validate_channel_banners_insert_arguments(arguments, oauth_token="eligible")

    assert selected["delegated"] is True
    assert selected["mediaMimeType"] == "image/png"


def test_validate_channel_banners_insert_arguments_rejects_delegation_without_authorization():
    """Reject delegated upload context when authorization is unavailable."""
    arguments = {
        **_valid_channel_banners_insert_arguments(),
        "onBehalfOfContentOwner": "content-owner-id",
    }

    with pytest.raises(ChannelBannersInsertToolError) as context:
        validate_channel_banners_insert_arguments(arguments, oauth_token=None)

    assert context.value.category == "authentication_failed"
    assert context.value.details == {"field": "onBehalfOfContentOwner"}


def test_validate_channel_banners_insert_arguments_rejects_oversized_actual_content():
    """Reject actual upload content over the documented channel-banner limit."""
    arguments = {
        "media": {
            "mimeType": "image/png",
            "content": "x" * (CHANNEL_BANNERS_MAX_BYTES + 1),
            "filename": "too-large.png",
        }
    }

    with pytest.raises(ChannelBannersInsertToolError) as context:
        validate_channel_banners_insert_arguments(arguments, oauth_token="eligible")

    assert context.value.category == "invalid_request"
    assert context.value.details == {"field": "media.content"}


def test_validate_channel_banners_insert_arguments_reports_unsupported_body_field():
    """Reject request bodies because banner activation is out of scope."""
    arguments = {**_valid_channel_banners_insert_arguments(), "body": {"brandingSettings": {}}}

    with pytest.raises(ChannelBannersInsertToolError) as context:
        validate_channel_banners_insert_arguments(arguments, oauth_token="eligible")

    assert context.value.category == "invalid_request"
    assert context.value.details == {"field": "body"}
