"""Contract tests for the concrete Layer 2 ``captions_list`` tool."""

import pytest

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.captions import (
    CAPTIONS_DOWNLOAD_TOOL_NAME,
    CAPTIONS_INSERT_TOOL_NAME,
    CAPTIONS_LIST_TOOL_NAME,
    CAPTIONS_UPDATE_TOOL_NAME,
    CaptionsDownloadToolError,
    CaptionsInsertToolError,
    CaptionsListToolError,
    CaptionsUpdateToolError,
    build_captions_download_contract,
    build_captions_download_tool_descriptor,
    build_captions_insert_contract,
    build_captions_insert_tool_descriptor,
    build_captions_list_contract,
    build_captions_list_tool_descriptor,
    build_captions_update_contract,
    build_captions_update_tool_descriptor,
    validate_captions_download_arguments,
    validate_captions_insert_arguments,
    validate_captions_list_arguments,
    validate_captions_update_arguments,
)


def test_concrete_captions_module_exports_public_tool_contract():
    """Require the concrete captions Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import captions

    assert captions.CAPTIONS_LIST_TOOL_NAME == "captions_list"
    assert youtube_common.CAPTIONS_LIST_TOOL_NAME == "captions_list"
    assert callable(captions.build_captions_list_tool_descriptor)
    assert captions.CAPTIONS_INSERT_TOOL_NAME == "captions_insert"
    assert youtube_common.CAPTIONS_INSERT_TOOL_NAME == "captions_insert"
    assert callable(captions.build_captions_insert_tool_descriptor)
    assert captions.CAPTIONS_UPDATE_TOOL_NAME == "captions_update"
    assert youtube_common.CAPTIONS_UPDATE_TOOL_NAME == "captions_update"
    assert callable(captions.build_captions_update_tool_descriptor)
    assert captions.CAPTIONS_DOWNLOAD_TOOL_NAME == "captions_download"
    assert youtube_common.CAPTIONS_DOWNLOAD_TOOL_NAME == "captions_download"
    assert callable(captions.build_captions_download_tool_descriptor)


def test_captions_list_contract_exposes_identity_quota_auth_and_delegation():
    """Expose the public metadata required before invocation."""
    contract = build_captions_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CAPTIONS_LIST_TOOL_NAME
    assert contract.upstream_resource == "captions"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 50
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "captions.list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert metadata["inputContract"]["required"] == ["part", "videoId"]
    assert "id" in metadata["inputContract"]["properties"]
    assert any("onBehalfOfContentOwner" in note for note in metadata["usageNotes"])
    assert any("Quota cost: 50" in note for note in metadata["usageNotes"])


def test_captions_insert_contract_exposes_identity_quota_auth_upload_and_delegation():
    """Expose the public metadata required before caption insertion."""
    contract = build_captions_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CAPTIONS_INSERT_TOOL_NAME
    assert contract.upstream_resource == "captions"
    assert contract.upstream_method == "insert"
    assert contract.quota_cost == 400
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.MEDIA_CONSTRAINED
    assert metadata["upstream"]["operationKey"] == "captions.insert"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert metadata["inputContract"]["required"] == ["part", "body", "media"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "sync" in metadata["inputContract"]["properties"]
    assert any("media" in note for note in metadata["usageNotes"])
    assert any("Quota cost: 400" in note for note in metadata["usageNotes"])
    assert any("deprecated" in caveat.lower() for caveat in metadata["caveats"])


def test_captions_update_contract_exposes_identity_quota_auth_media_and_delegation():
    """Expose the public metadata required before caption update."""
    contract = build_captions_update_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CAPTIONS_UPDATE_TOOL_NAME
    assert contract.upstream_resource == "captions"
    assert contract.upstream_method == "update"
    assert contract.quota_cost == 450
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.MEDIA_CONSTRAINED
    assert metadata["upstream"]["operationKey"] == "captions.update"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert "media" in metadata["inputContract"]["properties"]
    assert "onBehalfOfContentOwner" in metadata["inputContract"]["properties"]
    assert "sync" in metadata["inputContract"]["properties"]
    assert any("media" in note for note in metadata["usageNotes"])
    assert any("body" in note for note in metadata["usageNotes"])
    assert any("Quota cost: 450" in note for note in metadata["usageNotes"])
    assert any("deprecated" in caveat.lower() for caveat in metadata["caveats"])


def test_captions_download_contract_exposes_identity_quota_auth_conversion_and_delegation():
    """Expose the public metadata required before caption download."""
    contract = build_captions_download_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == CAPTIONS_DOWNLOAD_TOOL_NAME
    assert contract.upstream_resource == "captions"
    assert contract.upstream_method == "download"
    assert contract.quota_cost == 200
    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "captions.download"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert metadata["inputContract"]["required"] == ["id"]
    assert {"id", "tfmt", "tlang", "onBehalfOfContentOwner"}.issubset(
        metadata["inputContract"]["properties"]
    )
    assert metadata["inputContract"]["properties"]["tfmt"]["enum"] == ["sbv", "scc", "srt", "ttml", "vtt"]
    assert any("permission" in note.lower() for note in metadata["usageNotes"])
    assert any("tfmt" in note for note in metadata["usageNotes"])
    assert any("tlang" in note for note in metadata["usageNotes"])
    assert any("Quota cost: 200" in note for note in metadata["usageNotes"])


def test_captions_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_captions_list_tool_descriptor()

    assert descriptor["name"] == "captions_list"
    assert "Quota cost: 50" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "captions.list"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"]["required"] == ["part", "videoId"]
    assert {"part", "videoId", "id", "pageToken", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_captions_insert_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the insert public contract."""
    descriptor = build_captions_insert_tool_descriptor()

    assert descriptor["name"] == "captions_insert"
    assert "Quota cost: 400" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "captions.insert"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"]["required"] == ["part", "body", "media"]
    assert {"part", "body", "media", "sync", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_captions_update_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the update public contract."""
    descriptor = build_captions_update_tool_descriptor()

    assert descriptor["name"] == "captions_update"
    assert "Quota cost: 450" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "captions.update"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"]["required"] == ["part", "body"]
    assert {"part", "body", "media", "sync", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_captions_download_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the download public contract."""
    descriptor = build_captions_download_tool_descriptor()

    assert descriptor["name"] == "captions_download"
    assert "Quota cost: 200" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "captions.download"
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["inputSchema"]["required"] == ["id"]
    assert {"id", "tfmt", "tlang", "onBehalfOfContentOwner"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_captions_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw caption collection fields."""
    result = build_captions_list_tool_descriptor()["handler"]({"part": "snippet", "videoId": "video-123"})

    assert result["endpoint"] == "captions.list"
    assert result["quotaCost"] == 50
    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]
    assert result["lookup"] == {"videoId": "video-123"}


def test_captions_insert_contract_documents_successful_result_shape():
    """Require successful insert results to preserve the created resource shape."""
    result = build_captions_insert_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English captions"}},
            "media": {"mimeType": "text/xml", "content": "caption text"},
        }
    )

    assert result["endpoint"] == "captions.insert"
    assert result["quotaCost"] == 400
    assert result["item"]["id"] == "created-caption"
    assert result["requestedParts"] == ["snippet"]
    assert result["metadata"] == {"videoId": "video-123", "language": "en", "name": "English captions"}
    assert result["media"] == {"mimeType": "text/xml", "contentProvided": True}


def test_captions_update_contract_documents_successful_result_shape():
    """Require successful update results to preserve the updated resource shape."""
    result = build_captions_update_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "body": {"id": "caption-1", "snippet": {"isDraft": False}},
        }
    )

    assert result["endpoint"] == "captions.update"
    assert result["quotaCost"] == 450
    assert result["item"]["id"] == "caption-1"
    assert result["requestedParts"] == ["snippet"]
    assert result["update"] == {"id": "caption-1", "isDraft": False}


def test_captions_update_contract_documents_body_plus_media_result_shape():
    """Require successful update results to include safe media summary when supplied."""
    result = build_captions_update_tool_descriptor()["handler"](
        {
            "part": "id",
            "body": {"id": "caption-1", "snippet": {"isDraft": False}},
            "media": {"mimeType": "text/xml", "content": "caption text"},
        }
    )

    assert result["endpoint"] == "captions.update"
    assert result["quotaCost"] == 450
    assert result["item"]["id"] == "caption-1"
    assert result["media"] == {"mimeType": "text/xml", "contentProvided": True}
    assert "content" not in result["media"]


def test_captions_download_contract_documents_successful_result_shape():
    """Require successful download results to preserve caption content context."""
    result = build_captions_download_tool_descriptor()["handler"]({"id": "caption-1"})

    assert result["endpoint"] == "captions.download"
    assert result["quotaCost"] == 200
    assert result["content"] == "caption content"
    assert result["contentType"] == "application/octet-stream"
    assert result["contentForm"] == "text"
    assert result["download"] == {"id": "caption-1"}


def test_captions_download_contract_documents_conversion_result_shape():
    """Require successful download results to include safe conversion context."""
    result = build_captions_download_tool_descriptor()["handler"](
        {"id": "caption-1", "tfmt": "vtt", "tlang": "es"}
    )

    assert result["endpoint"] == "captions.download"
    assert result["requestedFormat"] == "vtt"
    assert result["requestedLanguage"] == "es"
    assert result["download"] == {"id": "caption-1", "tfmt": "vtt", "tlang": "es"}


@pytest.mark.parametrize(
    "arguments",
    [
        {"videoId": "video-123"},
        {"part": "snippet"},
        {"part": "snippet", "id": "caption-1"},
        {"part": "snippet", "videoId": "video-123", "maxResults": 51},
        {"part": "snippet", "videoId": "video-123", "onBehalfOfContentOwner": "owner"},
    ],
)
def test_captions_list_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized requests."""
    with pytest.raises(CaptionsListToolError) as exc_info:
        validate_captions_list_arguments(arguments, oauth_token=None)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details


@pytest.mark.parametrize(
    "arguments",
    [
        {"body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "body": {"snippet": {"language": "en", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "body": {"snippet": {"videoId": "video-123", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "body": {"snippet": {"videoId": "video-123", "language": "en"}}, "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}}},
        {"part": "snippet", "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}}, "media": {"mimeType": "text/xml", "content": "caption text"}, "onBehalfOfContentOwner": "owner"},
    ],
)
def test_captions_insert_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized insert requests."""
    with pytest.raises(CaptionsInsertToolError) as exc_info:
        validate_captions_insert_arguments(arguments, oauth_token=None)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details


@pytest.mark.parametrize(
    "arguments",
    [
        {"body": {"id": "caption-1"}},
        {"part": "snippet"},
        {"part": "snippet", "body": {}},
        {"part": "snippet", "media": {"mimeType": "text/xml", "content": "caption text"}},
        {"part": "snippet", "body": {"id": "caption-1"}, "onBehalfOfContentOwner": "owner"},
        {"part": "snippet", "body": {"id": "caption-1"}, "sync": "yes"},
    ],
)
def test_captions_update_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized update requests."""
    with pytest.raises(CaptionsUpdateToolError) as exc_info:
        validate_captions_update_arguments(arguments, oauth_token=None)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"id": "   "},
        {"id": "caption-1", "tfmt": "unsupported"},
        {"id": "caption-1", "tlang": "spanish"},
        {"id": "caption-1", "onBehalfOfContentOwner": "owner"},
    ],
)
def test_captions_download_validation_surfaces_safe_error_categories(arguments):
    """Surface safe error categories for invalid or unauthorized download requests."""
    with pytest.raises(CaptionsDownloadToolError) as exc_info:
        validate_captions_download_arguments(arguments, oauth_token=None)

    assert exc_info.value.category in {"invalid_request", "authentication_failed"}
    assert "api" not in exc_info.value.details
    assert "token" not in exc_info.value.details


@pytest.mark.parametrize(
    ("category", "message", "expected"),
    [
        ("auth", "forbidden", "authorization_failed"),
        ("not_found", "captionNotFound", "resource_not_found"),
        ("rate_limit", "quota", "quota_exhausted"),
        ("transient", "temporarily unavailable", "endpoint_unavailable"),
        ("invalid_request", "contentRequired", "invalid_request"),
    ],
)
def test_captions_update_maps_upstream_errors_to_safe_categories(category, message, expected):
    """Map Layer 1 failures into safe public update error categories."""
    from mcp_server.integrations.errors import NormalizedUpstreamError

    class FailingWrapper:
        """Raise one normalized error from the fake Layer 1 wrapper."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured normalized upstream error.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(message, category, retryable=False, upstream_status=400)

    descriptor = build_captions_update_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CaptionsUpdateToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "body": {"id": "caption-1"}})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}


@pytest.mark.parametrize(
    ("category", "message", "expected"),
    [
        ("auth", "forbidden", "authorization_failed"),
        ("not_found", "captionNotFound", "resource_not_found"),
        ("rate_limit", "quota", "quota_exhausted"),
        ("transient", "temporarily unavailable", "endpoint_unavailable"),
        ("invalid_request", "couldNotConvert", "invalid_request"),
    ],
)
def test_captions_download_maps_upstream_errors_to_safe_categories(category, message, expected):
    """Map Layer 1 failures into safe public download error categories."""
    from mcp_server.integrations.errors import NormalizedUpstreamError

    class FailingWrapper:
        """Raise one normalized error from the fake Layer 1 wrapper."""

        def call(self, executor, *, arguments, auth_context):
            """Raise the configured normalized upstream error.

            :param executor: Executor passed by the Layer 2 handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: Auth context selected by the Layer 2 handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(message, category, retryable=False, upstream_status=400)

    descriptor = build_captions_download_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CaptionsDownloadToolError) as exc_info:
        descriptor["handler"]({"id": "caption-1"})

    assert exc_info.value.category == expected
    assert exc_info.value.details == {"upstreamStatus": 400}
