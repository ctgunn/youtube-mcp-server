"""Contract tests for the Layer 2 ``playlists_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.playlists import (
    PLAYLISTS_DELETE_CALLER_EXAMPLES,
    PLAYLISTS_DELETE_CAVEATS,
    PLAYLISTS_DELETE_DESCRIPTION,
    PLAYLISTS_DELETE_INPUT_SCHEMA,
    PLAYLISTS_DELETE_QUOTA_COST,
    PLAYLISTS_DELETE_TOOL_NAME,
    PLAYLISTS_DELETE_USAGE_NOTES,
    PLAYLISTS_INSERT_CALLER_EXAMPLES,
    PLAYLISTS_INSERT_CAVEATS,
    PLAYLISTS_INSERT_DESCRIPTION,
    PLAYLISTS_INSERT_INPUT_SCHEMA,
    PLAYLISTS_INSERT_QUOTA_COST,
    PLAYLISTS_INSERT_SUPPORTED_PARTS,
    PLAYLISTS_INSERT_TOOL_NAME,
    PLAYLISTS_INSERT_USAGE_NOTES,
    PLAYLISTS_UPDATE_CALLER_EXAMPLES,
    PLAYLISTS_UPDATE_CAVEATS,
    PLAYLISTS_UPDATE_DESCRIPTION,
    PLAYLISTS_UPDATE_INPUT_SCHEMA,
    PLAYLISTS_UPDATE_QUOTA_COST,
    PLAYLISTS_UPDATE_SUPPORTED_PARTS,
    PLAYLISTS_UPDATE_TOOL_NAME,
    PLAYLISTS_UPDATE_USAGE_NOTES,
    PLAYLISTS_LIST_CALLER_EXAMPLES,
    PLAYLISTS_LIST_CAVEATS,
    PLAYLISTS_LIST_DESCRIPTION,
    PLAYLISTS_LIST_INPUT_SCHEMA,
    PLAYLISTS_LIST_QUOTA_COST,
    PLAYLISTS_LIST_SELECTORS,
    PLAYLISTS_LIST_TOOL_NAME,
    PLAYLISTS_LIST_USAGE_NOTES,
    build_playlists_insert_contract,
    build_playlists_insert_tool_descriptor,
    build_playlists_delete_contract,
    build_playlists_delete_tool_descriptor,
    build_playlists_update_contract,
    build_playlists_update_tool_descriptor,
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


def test_playlists_insert_public_symbols_are_exported():
    """Expose ``playlists_insert`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlists

    assert youtube_common.PLAYLISTS_INSERT_TOOL_NAME == "playlists_insert"
    assert PLAYLISTS_INSERT_TOOL_NAME == "playlists_insert"
    assert PLAYLISTS_INSERT_QUOTA_COST == 50
    assert PLAYLISTS_INSERT_SUPPORTED_PARTS == ("snippet",)
    assert callable(playlists.build_playlists_insert_contract)


def test_playlists_insert_schema_preserves_create_body_inputs():
    """Expose the supported ``playlists_insert`` request shape."""
    properties = PLAYLISTS_INSERT_INPUT_SCHEMA["properties"]
    body = properties["body"]
    snippet = body["properties"]["snippet"]

    assert PLAYLISTS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert properties["part"] == {"type": "string", "minLength": 1, "enum": ["snippet"]}
    assert body["required"] == ["snippet"]
    assert snippet["required"] == ["title"]
    assert snippet["properties"]["title"] == {"type": "string", "minLength": 1}
    assert snippet["additionalProperties"] is False
    assert body["additionalProperties"] is False
    assert PLAYLISTS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_playlists_insert_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, OAuth, and created-resource metadata."""
    contract = build_playlists_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlists_insert"
    assert metadata["upstream"]["operationKey"] == "playlists.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["inputContract"] == PLAYLISTS_INSERT_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "playlist"
    assert metadata["responseConvention"]["writableFields"] == ["body.snippet.title"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlists_insert_metadata_describes_quota_oauth_body_and_boundaries():
    """Keep caller-facing playlists insert metadata complete before invocation."""
    descriptor = build_playlists_insert_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlists_insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "body.snippet.title" in metadata_text
    assert "user-visible" in metadata_text
    assert "duplicate" in metadata_text.lower()
    assert "playlist item insertion" in metadata_text
    assert "video curation" in metadata_text
    assert metadata["examples"] == list(PLAYLISTS_INSERT_CALLER_EXAMPLES)
    assert PLAYLISTS_INSERT_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLISTS_INSERT_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLISTS_INSERT_CAVEATS)


def test_playlists_insert_examples_cover_success_and_safe_failure_boundaries():
    """Expose playlists insert examples for supported calls and safe failures."""
    descriptor = build_playlists_insert_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["oauth_playlist_creation"]["quotaCost"] == 50
    assert examples["oauth_playlist_creation"]["arguments"]["body"]["snippet"]["title"] == "Research playlist"
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["invalid_part"]["error"]["category"] == "invalid_request"
    assert examples["missing_body"]["error"]["field"] == "body"
    assert examples["missing_title"]["error"]["field"] == "body.snippet.title"
    assert examples["unsupported_write_field"]["error"]["field"] == "body.snippet.description"
    assert examples["access_failure"]["error"]["category"] == "authentication_failed"
    assert examples["quota_or_upstream_create_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["out_of_scope_playlist_management_request"]["error"]["field"] == "insertPlaylistItems"


def test_playlists_update_public_symbols_are_exported():
    """Expose ``playlists_update`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlists

    assert youtube_common.PLAYLISTS_UPDATE_TOOL_NAME == "playlists_update"
    assert PLAYLISTS_UPDATE_TOOL_NAME == "playlists_update"
    assert PLAYLISTS_UPDATE_QUOTA_COST == 50
    assert PLAYLISTS_UPDATE_SUPPORTED_PARTS == ("snippet",)
    assert callable(playlists.build_playlists_update_contract)


def test_playlists_update_schema_preserves_update_body_inputs():
    """Expose the supported ``playlists_update`` request shape."""
    properties = PLAYLISTS_UPDATE_INPUT_SCHEMA["properties"]
    body = properties["body"]
    snippet = body["properties"]["snippet"]

    assert PLAYLISTS_UPDATE_INPUT_SCHEMA["required"] == ["part", "body"]
    assert properties["part"] == {"type": "string", "minLength": 1, "enum": ["snippet"]}
    assert body["required"] == ["id", "snippet"]
    assert body["properties"]["id"] == {"type": "string", "minLength": 1}
    assert snippet["required"] == ["title"]
    assert snippet["properties"]["title"] == {"type": "string", "minLength": 1}
    assert snippet["additionalProperties"] is False
    assert body["additionalProperties"] is False
    assert PLAYLISTS_UPDATE_INPUT_SCHEMA["additionalProperties"] is False


def test_playlists_update_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, OAuth, and updated-resource metadata."""
    contract = build_playlists_update_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlists_update"
    assert metadata["upstream"]["operationKey"] == "playlists.update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["inputContract"] == PLAYLISTS_UPDATE_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "updated_resource"
    assert metadata["responseConvention"]["resourcePath"] == "playlist"
    assert metadata["responseConvention"]["targetFields"] == ["body.id"]
    assert metadata["responseConvention"]["writableFields"] == ["body.snippet.title"]
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlists_update_metadata_describes_quota_oauth_body_and_boundaries():
    """Keep caller-facing playlists update metadata complete before invocation."""
    descriptor = build_playlists_update_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlists_update"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "body.id" in metadata_text
    assert "body.snippet.title" in metadata_text
    assert "user-visible" in metadata_text
    assert "repeat" in metadata_text.lower()
    assert "playlist item management" in metadata_text
    assert "video curation" in metadata_text
    assert metadata["examples"] == list(PLAYLISTS_UPDATE_CALLER_EXAMPLES)
    assert PLAYLISTS_UPDATE_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLISTS_UPDATE_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLISTS_UPDATE_CAVEATS)


def test_playlists_update_examples_cover_success_and_safe_failure_boundaries():
    """Expose playlists update examples for supported calls and safe failures."""
    descriptor = build_playlists_update_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["oauth_playlist_update"]["quotaCost"] == 50
    assert examples["oauth_playlist_update"]["arguments"]["body"]["id"] == "PL123"
    assert examples["oauth_playlist_update"]["arguments"]["body"]["snippet"]["title"] == "Updated research playlist"
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["invalid_part"]["error"]["category"] == "invalid_request"
    assert examples["missing_body"]["error"]["field"] == "body"
    assert examples["missing_target_identity"]["error"]["field"] == "body.id"
    assert examples["missing_title"]["error"]["field"] == "body.snippet.title"
    assert examples["unsupported_write_field"]["error"]["field"] == "body.snippet.description"
    assert examples["access_failure"]["error"]["category"] == "authentication_failed"
    assert examples["quota_or_upstream_update_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["repeat_request_caveat"]["result"]["caveats"]["repeatRequest"] == "may_reapply_update"
    assert examples["out_of_scope_playlist_management_request"]["error"]["field"] == "insertPlaylistItems"


def test_playlists_update_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope failures."""
    descriptor = build_playlists_update_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_target_identity",
        "missing_title",
        "unsupported_write_field",
        "access_failure",
        "quota_or_upstream_update_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(error_examples)
    assert error_examples["missing_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["invalid_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["missing_body"] == {"category": "invalid_request", "field": "body"}
    assert error_examples["missing_target_identity"] == {"category": "invalid_request", "field": "body.id"}
    assert error_examples["missing_title"] == {"category": "invalid_request", "field": "body.snippet.title"}
    assert error_examples["unsupported_write_field"]["field"] == "body.snippet.description"
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["quota_or_upstream_update_failure"]["category"] == "quota_exhausted"
    assert error_examples["out_of_scope_playlist_management_request"]["field"] == "insertPlaylistItems"


def test_playlists_delete_public_symbols_are_exported():
    """Expose ``playlists_delete`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import playlists

    assert youtube_common.PLAYLISTS_DELETE_TOOL_NAME == "playlists_delete"
    assert PLAYLISTS_DELETE_TOOL_NAME == "playlists_delete"
    assert PLAYLISTS_DELETE_QUOTA_COST == 50
    assert callable(playlists.build_playlists_delete_contract)


def test_playlists_delete_schema_requires_target_identity_only():
    """Expose the supported ``playlists_delete`` request shape."""
    properties = PLAYLISTS_DELETE_INPUT_SCHEMA["properties"]

    assert PLAYLISTS_DELETE_INPUT_SCHEMA["required"] == ["id"]
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert PLAYLISTS_DELETE_INPUT_SCHEMA["additionalProperties"] is False


def test_playlists_delete_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, OAuth, and delete acknowledgment metadata."""
    contract = build_playlists_delete_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "playlists_delete"
    assert metadata["upstream"]["operationKey"] == "playlists.delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["resourceFamily"] == "playlists"
    assert metadata["inputContract"] == PLAYLISTS_DELETE_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "deletion_acknowledgment"
    assert metadata["responseConvention"]["targetFields"] == ["id"]
    assert metadata["responseConvention"]["noBodySuccess"] is True
    assert metadata["responseConvention"]["repeatDeletePolicy"] == "missing_resource_possible_after_success"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_playlists_delete_metadata_describes_quota_oauth_id_and_boundaries():
    """Keep caller-facing playlists delete metadata complete before invocation."""
    descriptor = build_playlists_delete_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "playlists_delete"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text or "oauth_required" in metadata_text
    assert "id" in metadata_text
    assert "user-visible" in metadata_text
    assert "acknowledg" in metadata_text.lower()
    assert "repeat" in metadata_text.lower()
    assert "playlist item management" in metadata_text
    assert "video curation" in metadata_text
    assert metadata["examples"] == list(PLAYLISTS_DELETE_CALLER_EXAMPLES)
    assert PLAYLISTS_DELETE_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(PLAYLISTS_DELETE_USAGE_NOTES)
    assert metadata["caveats"] == list(PLAYLISTS_DELETE_CAVEATS)


def test_playlists_delete_examples_cover_success_and_safe_failure_boundaries():
    """Expose playlists delete examples for supported calls and safe failures."""
    descriptor = build_playlists_delete_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["oauth_playlist_deletion"]["quotaCost"] == 50
    assert examples["oauth_playlist_deletion"]["arguments"]["id"] == "PL123"
    assert examples["oauth_playlist_deletion"]["result"]["deleted"] is True
    assert examples["no_body_deletion_acknowledgment"]["result"]["acknowledged"] is True
    assert examples["missing_target_identity"]["error"]["field"] == "id"
    assert examples["malformed_target_identity"]["error"]["field"] == "id"
    assert examples["unsupported_field"]["error"]["field"] == "part"
    assert examples["access_failure"]["error"]["category"] == "authentication_failed"
    assert examples["insufficient_authorization"]["error"]["category"] == "authorization_failed"
    assert examples["missing_resource_or_already_deleted"]["error"]["category"] == "resource_not_found"
    assert examples["quota_or_upstream_delete_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["repeat_delete_caveat"]["result"]["caveats"]["repeatDelete"] == "missing_resource_possible_after_success"
    assert examples["out_of_scope_playlist_management_request"]["error"]["field"] == "restore"


def test_playlists_delete_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope failures."""
    descriptor = build_playlists_delete_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_target_identity",
        "malformed_target_identity",
        "unsupported_field",
        "access_failure",
        "insufficient_authorization",
        "missing_resource_or_already_deleted",
        "quota_or_upstream_delete_failure",
        "out_of_scope_playlist_management_request",
    }.issubset(error_examples)
    assert error_examples["missing_target_identity"] == {"category": "invalid_request", "field": "id"}
    assert error_examples["malformed_target_identity"] == {"category": "invalid_request", "field": "id"}
    assert error_examples["unsupported_field"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["insufficient_authorization"]["category"] == "authorization_failed"
    assert error_examples["missing_resource_or_already_deleted"]["category"] == "resource_not_found"
    assert error_examples["quota_or_upstream_delete_failure"]["category"] == "quota_exhausted"
    assert error_examples["out_of_scope_playlist_management_request"]["field"] == "restore"
