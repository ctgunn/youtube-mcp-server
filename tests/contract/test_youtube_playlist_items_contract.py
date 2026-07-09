"""Contract tests for the Layer 2 ``playlistItems_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.playlist_items import (
    PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES,
    PLAYLIST_ITEMS_INSERT_CAVEATS,
    PLAYLIST_ITEMS_INSERT_DESCRIPTION,
    PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA,
    PLAYLIST_ITEMS_INSERT_QUOTA_COST,
    PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS,
    PLAYLIST_ITEMS_INSERT_TOOL_NAME,
    PLAYLIST_ITEMS_INSERT_USAGE_NOTES,
    PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES,
    PLAYLIST_ITEMS_LIST_CAVEATS,
    PLAYLIST_ITEMS_LIST_DESCRIPTION,
    PLAYLIST_ITEMS_LIST_INPUT_SCHEMA,
    PLAYLIST_ITEMS_LIST_QUOTA_COST,
    PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS,
    PLAYLIST_ITEMS_LIST_TOOL_NAME,
    PLAYLIST_ITEMS_LIST_USAGE_NOTES,
    PlaylistItemsInsertToolError,
    PlaylistItemsListToolError,
    build_playlist_items_insert_contract,
    build_playlist_items_insert_handler,
    build_playlist_items_insert_tool_descriptor,
    build_playlist_items_list_contract,
    build_playlist_items_list_handler,
    build_playlist_items_list_tool_descriptor,
    validate_playlist_items_insert_arguments,
    validate_playlist_items_list_arguments,
)


def test_playlist_items_list_public_symbols_are_exported():
    """Expose ``playlistItems_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_items

    assert youtube_common.PLAYLIST_ITEMS_LIST_TOOL_NAME == "playlistItems_list"
    assert PLAYLIST_ITEMS_LIST_TOOL_NAME == "playlistItems_list"
    assert PLAYLIST_ITEMS_LIST_QUOTA_COST == 1
    assert callable(playlist_items.build_playlist_items_list_tool_descriptor)


def test_playlist_items_insert_public_symbols_are_exported():
    """Expose ``playlistItems_insert`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlist_items

    assert youtube_common.PLAYLIST_ITEMS_INSERT_TOOL_NAME == "playlistItems_insert"
    assert PLAYLIST_ITEMS_INSERT_TOOL_NAME == "playlistItems_insert"
    assert PLAYLIST_ITEMS_INSERT_QUOTA_COST == 50
    assert callable(playlist_items.build_playlist_items_insert_tool_descriptor)


def test_playlist_items_insert_schema_preserves_body_inputs():
    """Expose the upstream-like mutation request fields for ``playlistItems_insert``."""
    properties = PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA["properties"]
    snippet = properties["body"]["properties"]["snippet"]
    resource_id = snippet["properties"]["resourceId"]

    assert PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert properties["part"] == {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_INSERT_SUPPORTED_PARTS)}
    assert properties["body"]["required"] == ["snippet"]
    assert snippet["required"] == ["playlistId", "resourceId"]
    assert snippet["properties"]["playlistId"] == {"type": "string", "minLength": 1}
    assert snippet["properties"]["position"] == {"type": "integer", "minimum": 0}
    assert resource_id["required"] == ["videoId"]
    assert resource_id["properties"]["videoId"] == {"type": "string", "minLength": 1}
    assert resource_id["properties"]["kind"] == {"type": "string", "enum": ["youtube#video"]}
    assert PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_items_insert_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, OAuth, availability, and mutation metadata."""
    contract = build_playlist_items_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistItems_insert"
    assert metadata["upstream"]["operationKey"] == "playlistItems.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "body"]
    assert {"part", "body"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "item"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlist_items_insert_metadata_describes_quota_oauth_body_and_boundaries():
    """Keep caller-facing insert metadata complete before invocation."""
    descriptor = build_playlist_items_insert_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlistItems_insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "body.snippet.playlistId" in metadata_text
    assert "body.snippet.resourceId.videoId" in metadata_text
    assert "placement" in metadata_text
    assert "playlist item listing" in metadata_text
    assert "video enrichment" in metadata_text
    assert metadata["examples"] == list(PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES)
    assert PLAYLIST_ITEMS_INSERT_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLIST_ITEMS_INSERT_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLIST_ITEMS_INSERT_CAVEATS)


def test_validate_playlist_items_insert_arguments_accepts_minimal_body():
    """Accept one supported OAuth-backed playlist-item insertion request."""
    selected = validate_playlist_items_insert_arguments(
        {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": " PL123 ",
                    "resourceId": {"kind": "youtube#video", "videoId": " video-123 "},
                }
            },
        }
    )

    assert selected == {
        "part": "snippet",
        "body": {
            "snippet": {
                "playlistId": "PL123",
                "resourceId": {"kind": "youtube#video", "videoId": "video-123"},
            }
        },
    }


def test_validate_playlist_items_insert_arguments_accepts_supported_position():
    """Accept supported playlist-item placement context."""
    selected = validate_playlist_items_insert_arguments(
        {
            "part": "snippet",
            "body": {
                "snippet": {
                    "playlistId": "PL123",
                    "position": 0,
                    "resourceId": {"videoId": "video-123"},
                }
            },
        }
    )

    assert selected["body"]["snippet"]["position"] == 0


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}}, "part"),
        (
            {
                "part": "statistics",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            },
            "part",
        ),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": []}, "body"),
        ({"part": "snippet", "body": {}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": {"resourceId": {"videoId": "video-123"}}}}, "body.snippet.playlistId"),
        ({"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}}, "body.snippet.resourceId"),
        (
            {"part": "snippet", "body": {"snippet": {"playlistId": "PL123", "resourceId": {}}}},
            "body.snippet.resourceId.videoId",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"kind": "youtube#playlist", "videoId": "video-123"},
                    }
                },
            },
            "body.snippet.resourceId.kind",
        ),
        (
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"videoId": "video-123"},
                        "position": -1,
                    }
                },
            },
            "body.snippet.position",
        ),
        (
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                "rankPlaylist": True,
            },
            "rankPlaylist",
        ),
    ],
)
def test_validate_playlist_items_insert_arguments_rejects_invalid_shapes(arguments, field):
    """Reject unsupported playlist-item insert request shapes with safe field details."""
    with pytest.raises(PlaylistItemsInsertToolError) as exc_info:
        validate_playlist_items_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlist_items_insert_tool_error_sanitizes_sensitive_details():
    """Avoid leaking credentials or raw request details through safe insert errors."""
    error = PlaylistItemsInsertToolError(
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


def test_playlist_items_insert_handler_maps_upstream_errors_to_safe_categories():
    """Map normalized upstream insert failures to shared Layer 2 error categories."""

    class FailingWrapper:
        """Raise a configured normalized error for insert handler mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an authorization-flavored upstream failure."""
            raise NormalizedUpstreamError(
                "forbidden",
                category="forbidden",
                retryable=False,
                upstream_status=403,
                details={"upstreamStatus": 403, "oauth_token": "secret"},
            )

    handler = build_playlist_items_insert_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsInsertToolError) as exc_info:
        handler(
            {
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            }
        )

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"upstreamStatus": 403}


def test_playlist_items_list_schema_preserves_selector_and_paging_inputs():
    """Expose the upstream-like request fields for ``playlistItems_list``."""
    properties = PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"] == {"type": "string", "minLength": 1, "enum": list(PLAYLIST_ITEMS_LIST_SUPPORTED_PARTS)}
    assert properties["playlistId"] == {"type": "string", "minLength": 1}
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert properties["pageToken"] == {"type": "string", "minLength": 1}
    assert properties["maxResults"]["type"] == "integer"
    assert properties["maxResults"]["minimum"] == 0
    assert {"required": ["playlistId"]} in PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["oneOf"]
    assert {"required": ["id"]} in PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["oneOf"]
    assert PLAYLIST_ITEMS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_playlist_items_list_public_contract_identifies_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list metadata."""
    contract = build_playlist_items_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlistItems_list"
    assert metadata["upstream"]["operationKey"] == "playlistItems.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"playlistId", "id", "pageToken", "maxResults"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert metadata["responseConvention"]["selectorFields"] == ["playlistId", "id"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlist_items_list_metadata_describes_quota_access_empty_and_boundaries():
    """Keep caller-facing metadata complete before invocation."""
    descriptor = build_playlist_items_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlistItems_list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert "Quota cost: 1" in metadata_text
    assert "API-key" in metadata_text or "api_key" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "playlist item mutation" in metadata_text
    assert "video enrichment" in metadata_text
    assert metadata["examples"] == list(PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES)
    assert PLAYLIST_ITEMS_LIST_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLIST_ITEMS_LIST_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLIST_ITEMS_LIST_CAVEATS)


def test_validate_playlist_items_list_arguments_accepts_playlist_scoped_lookup():
    """Accept one supported API-key playlist-scoped request."""
    selected = validate_playlist_items_list_arguments(
        {"part": "snippet,contentDetails", "playlistId": " PL123 ", "pageToken": "NEXT", "maxResults": 25}
    )

    assert selected == {
        "part": "snippet,contentDetails",
        "playlistId": "PL123",
        "pageToken": "NEXT",
        "maxResults": 25,
    }


def test_validate_playlist_items_list_arguments_accepts_direct_id_lookup():
    """Accept one supported direct playlist-item lookup request."""
    selected = validate_playlist_items_list_arguments({"part": "id,snippet", "id": " playlist-item-123 "})

    assert selected == {"part": "id,snippet", "id": "playlist-item-123"}


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"playlistId": "PL123"}, "part"),
        ({"part": "statistics", "playlistId": "PL123"}, "part"),
        ({"part": "snippet,snippet", "playlistId": "PL123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "playlistId": "PL123", "id": "playlist-item-123"}, "selector"),
        ({"part": "snippet", "playlistId": "PL123", "unknown": "x"}, "unknown"),
        ({"part": "snippet", "id": "playlist-item-123", "pageToken": "NEXT"}, "paging"),
        ({"part": "snippet", "playlistId": "PL123", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "playlistId": "PL123", "maxResults": 51}, "maxResults"),
    ],
)
def test_validate_playlist_items_list_arguments_rejects_invalid_shapes(arguments, field):
    """Reject unsupported playlist-item request shapes with safe field details."""
    with pytest.raises(PlaylistItemsListToolError) as exc_info:
        validate_playlist_items_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlist_items_list_tool_error_sanitizes_sensitive_details():
    """Avoid leaking credentials or raw request details through safe errors."""
    error = PlaylistItemsListToolError(
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


def test_playlist_items_list_handler_maps_upstream_errors_to_safe_categories():
    """Map normalized upstream failures to shared Layer 2 error categories."""

    class FailingWrapper:
        """Raise a configured normalized error for handler mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an authorization-flavored upstream failure."""
            raise NormalizedUpstreamError(
                "forbidden",
                category="forbidden",
                retryable=False,
                upstream_status=403,
                details={"upstreamStatus": 403, "api_key": "secret"},
            )

    handler = build_playlist_items_list_handler(wrapper=FailingWrapper())

    with pytest.raises(PlaylistItemsListToolError) as exc_info:
        handler({"part": "snippet", "playlistId": "PL123"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"upstreamStatus": 403}
