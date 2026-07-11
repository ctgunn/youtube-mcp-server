"""Contract tests for the Layer 2 ``playlists_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.playlists import (
    PLAYLISTS_LIST_CALLER_EXAMPLES,
    PLAYLISTS_LIST_CAVEATS,
    PLAYLISTS_LIST_DESCRIPTION,
    PLAYLISTS_LIST_INPUT_SCHEMA,
    PLAYLISTS_LIST_QUOTA_COST,
    PLAYLISTS_LIST_SELECTORS,
    PLAYLISTS_LIST_TOOL_NAME,
    PLAYLISTS_LIST_USAGE_NOTES,
    build_playlists_list_contract,
    build_playlists_list_tool_descriptor,
)


def test_playlists_list_public_symbols_are_exported():
    """Expose ``playlists_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlists

    assert youtube_common.PLAYLISTS_LIST_TOOL_NAME == "playlists_list"
    assert PLAYLISTS_LIST_TOOL_NAME == "playlists_list"
    assert PLAYLISTS_LIST_QUOTA_COST == 1
    assert PLAYLISTS_LIST_SELECTORS == ("channelId", "id", "mine")
    assert callable(playlists.build_playlists_list_contract)


def test_playlists_list_schema_requires_part_and_one_selector():
    """Expose the supported ``playlists_list`` request shape."""
    properties = PLAYLISTS_LIST_INPUT_SCHEMA["properties"]

    assert PLAYLISTS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["channelId"] == {"type": "string", "minLength": 1}
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert properties["mine"] == {"type": "boolean"}
    assert properties["pageToken"] == {"type": "string", "minLength": 1}
    assert properties["maxResults"] == {"type": "integer", "minimum": 0, "maximum": 50}
    assert PLAYLISTS_LIST_INPUT_SCHEMA["oneOf"] == [
        {"required": ["channelId"]},
        {"required": ["id"]},
        {"required": ["mine"]},
    ]
    assert PLAYLISTS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_playlists_list_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, conditional auth, and list metadata."""
    contract = build_playlists_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlists_list"
    assert metadata["upstream"]["operationKey"] == "playlists.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["inputContract"] == PLAYLISTS_LIST_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert metadata["responseConvention"]["selectorFields"] == ["channelId", "id", "mine"]
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlists_list_metadata_describes_quota_access_selectors_and_boundaries():
    """Keep caller-facing playlists list metadata complete before invocation."""
    descriptor = build_playlists_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlists_list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert "Quota cost: 1" in metadata_text
    assert "channelId" in metadata_text
    assert "id" in metadata_text
    assert "mine" in metadata_text
    assert "API-key" in metadata_text or "api_key" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "pageToken" in metadata_text
    assert "maxResults" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "playlist item traversal" in metadata_text
    assert "video enrichment" in metadata_text
    assert metadata["examples"] == list(PLAYLISTS_LIST_CALLER_EXAMPLES)
    assert PLAYLISTS_LIST_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLISTS_LIST_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLISTS_LIST_CAVEATS)


def test_playlists_list_examples_cover_success_and_safe_failure_boundaries():
    """Expose playlists list examples for supported calls and safe failures."""
    descriptor = build_playlists_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["channel_scoped_playlist_listing"]["quotaCost"] == 1
    assert examples["direct_playlist_lookup"]["arguments"]["id"] == "PL123"
    assert examples["owner_scoped_playlist_listing"]["arguments"]["mine"] is True
    assert examples["paged_playlist_listing"]["arguments"]["pageToken"] == "NEXT_PAGE"
    assert examples["empty_success"]["result"]["items"] == []
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["invalid_part"]["error"]["category"] == "invalid_request"
    assert examples["missing_selector"]["error"]["field"] == "selector"
    assert examples["conflicting_selector"]["error"]["field"] == "selector"
    assert examples["paging_with_id"]["error"]["field"] == "paging"
    assert examples["access_failure"]["error"]["selector"] == "mine"
    assert examples["quota_or_upstream_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["out_of_scope_playlist_management_request"]["error"]["field"] == "includePlaylistItems"


def test_playlists_list_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope failures."""
    descriptor = build_playlists_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_part",
        "invalid_part",
        "missing_selector",
        "conflicting_selector",
        "paging_with_id",
        "access_failure",
        "quota_or_upstream_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(error_examples)
    assert error_examples["missing_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["invalid_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["missing_selector"] == {"category": "invalid_request", "field": "selector"}
    assert error_examples["conflicting_selector"] == {"category": "invalid_request", "field": "selector"}
    assert error_examples["paging_with_id"] == {"category": "invalid_request", "field": "paging"}
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["quota_or_upstream_failure"]["category"] == "quota_exhausted"
    assert error_examples["out_of_scope_playlist_management_request"]["field"] == "includePlaylistItems"
