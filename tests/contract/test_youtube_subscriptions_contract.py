"""Contract tests for the Layer 2 ``subscriptions_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.subscriptions import (
    SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES,
    SUBSCRIPTIONS_INSERT_CAVEATS,
    SUBSCRIPTIONS_INSERT_DESCRIPTION,
    SUBSCRIPTIONS_INSERT_INPUT_SCHEMA,
    SUBSCRIPTIONS_INSERT_QUOTA_COST,
    SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS,
    SUBSCRIPTIONS_INSERT_TOOL_NAME,
    SUBSCRIPTIONS_INSERT_USAGE_NOTES,
    SUBSCRIPTIONS_LIST_CALLER_EXAMPLES,
    SUBSCRIPTIONS_LIST_CAVEATS,
    SUBSCRIPTIONS_LIST_DESCRIPTION,
    SUBSCRIPTIONS_LIST_INPUT_SCHEMA,
    SUBSCRIPTIONS_LIST_MAX_RESULTS,
    SUBSCRIPTIONS_LIST_ORDER_VALUES,
    SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS,
    SUBSCRIPTIONS_LIST_QUOTA_COST,
    SUBSCRIPTIONS_LIST_SELECTORS,
    SUBSCRIPTIONS_LIST_SUPPORTED_PARTS,
    SUBSCRIPTIONS_LIST_TOOL_NAME,
    SUBSCRIPTIONS_LIST_USAGE_NOTES,
    SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS,
    build_subscriptions_insert_contract,
    build_subscriptions_insert_tool_descriptor,
    build_subscriptions_list_contract,
    build_subscriptions_list_tool_descriptor,
)


def test_subscriptions_list_public_symbols_are_exported():
    """Expose ``subscriptions_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import subscriptions

    assert youtube_common.SUBSCRIPTIONS_LIST_TOOL_NAME == "subscriptions_list"
    assert SUBSCRIPTIONS_LIST_TOOL_NAME == "subscriptions_list"
    assert SUBSCRIPTIONS_LIST_QUOTA_COST == 1
    assert SUBSCRIPTIONS_LIST_SELECTORS == ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
    assert SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS == ("channelId", "id")
    assert "mySubscribers" in SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS
    assert "subscriberSnippet" in SUBSCRIPTIONS_LIST_SUPPORTED_PARTS
    assert callable(subscriptions.build_subscriptions_list_contract)


def test_subscriptions_insert_public_symbols_are_exported():
    """Expose ``subscriptions_insert`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import subscriptions

    assert youtube_common.SUBSCRIPTIONS_INSERT_TOOL_NAME == "subscriptions_insert"
    assert SUBSCRIPTIONS_INSERT_TOOL_NAME == "subscriptions_insert"
    assert SUBSCRIPTIONS_INSERT_QUOTA_COST == 50
    assert callable(subscriptions.build_subscriptions_insert_contract)
    assert callable(subscriptions.build_subscriptions_insert_tool_descriptor)


def test_subscriptions_insert_schema_preserves_supported_create_inputs():
    """Expose the supported ``subscriptions_insert`` request shape."""
    properties = SUBSCRIPTIONS_INSERT_INPUT_SCHEMA["properties"]
    body = properties["body"]
    snippet = body["properties"]["snippet"]
    resource_id = snippet["properties"]["resourceId"]

    assert SUBSCRIPTIONS_INSERT_INPUT_SCHEMA["required"] == ["part", "body"]
    assert properties["part"] == {"type": "string", "minLength": 1, "enum": list(SUBSCRIPTIONS_INSERT_SUPPORTED_PARTS)}
    assert body["required"] == ["snippet"]
    assert body["additionalProperties"] is False
    assert snippet["required"] == ["resourceId"]
    assert snippet["additionalProperties"] is False
    assert resource_id["required"] == ["channelId"]
    assert resource_id["properties"]["kind"] == {"type": "string", "enum": ["youtube#channel"]}
    assert resource_id["properties"]["channelId"] == {"type": "string", "minLength": 1}
    assert resource_id["additionalProperties"] is False
    assert SUBSCRIPTIONS_INSERT_INPUT_SCHEMA["additionalProperties"] is False


def test_subscriptions_list_schema_preserves_supported_inputs():
    """Expose the supported ``subscriptions_list`` request shape."""
    properties = SUBSCRIPTIONS_LIST_INPUT_SCHEMA["properties"]

    assert SUBSCRIPTIONS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["channelId"] == {"type": "string", "minLength": 1}
    assert properties["id"] == {"type": "string", "minLength": 1}
    assert properties["mine"] == {"type": "boolean"}
    assert properties["myRecentSubscribers"] == {"type": "boolean"}
    assert properties["mySubscribers"] == {"type": "boolean"}
    assert properties["pageToken"] == {"type": "string", "minLength": 1}
    assert properties["maxResults"] == {"type": "integer", "minimum": 0, "maximum": SUBSCRIPTIONS_LIST_MAX_RESULTS}
    assert properties["order"] == {"type": "string", "enum": list(SUBSCRIPTIONS_LIST_ORDER_VALUES)}
    assert SUBSCRIPTIONS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_subscriptions_list_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, conditional auth, and list metadata."""
    contract = build_subscriptions_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "subscriptions_list"
    assert metadata["upstream"]["operationKey"] == "subscriptions.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["resourceFamily"] == "subscriptions"
    assert metadata["inputContract"] == SUBSCRIPTIONS_LIST_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert metadata["responseConvention"]["selectorFields"] == list(SUBSCRIPTIONS_LIST_SELECTORS)
    assert metadata["responseConvention"]["publicSelectors"] == list(SUBSCRIPTIONS_LIST_PUBLIC_SELECTORS)
    assert metadata["responseConvention"]["userContextSelectors"] == list(SUBSCRIPTIONS_LIST_USER_CONTEXT_SELECTORS)
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_subscriptions_insert_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, OAuth, and created-resource metadata."""
    contract = build_subscriptions_insert_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "subscriptions_insert"
    assert metadata["upstream"]["operationKey"] == "subscriptions.insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert metadata["resourceFamily"] == "subscriptions"
    assert metadata["inputContract"] == SUBSCRIPTIONS_INSERT_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "created_resource"
    assert metadata["responseConvention"]["resourcePath"] == "subscription"
    assert metadata["responseConvention"]["requestedParts"] == ["snippet"]
    assert metadata["responseConvention"]["targetField"] == "body.snippet.resourceId.channelId"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_subscriptions_insert_descriptor_is_executable_tool_metadata():
    """Expose a callable descriptor for ``subscriptions_insert``."""
    descriptor = build_subscriptions_insert_tool_descriptor()

    assert descriptor["name"] == "subscriptions_insert"
    assert descriptor["inputSchema"] == SUBSCRIPTIONS_INSERT_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"


def test_subscriptions_insert_metadata_describes_create_semantics_and_boundaries():
    """Keep caller-facing subscriptions insert metadata complete before invocation."""
    descriptor = build_subscriptions_insert_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "subscriptions_insert"
    assert metadata["quotaCost"] == 50
    assert metadata["authMode"] == "oauth_required"
    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "part=snippet" in metadata_text
    assert "body.snippet.resourceId.channelId" in metadata_text
    assert "youtube#channel" in metadata_text
    assert "create" in metadata_text.lower()
    assert "subscription relationship" in metadata_text
    assert "Duplicate" in metadata_text or "duplicate" in metadata_text
    assert "ineligible" in metadata_text
    assert "notification" in metadata_text
    assert "analytics" in metadata_text
    assert "enrichment" in metadata_text
    assert metadata["examples"] == list(SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES)
    assert SUBSCRIPTIONS_INSERT_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(SUBSCRIPTIONS_INSERT_USAGE_NOTES)
    assert metadata["caveats"] == list(SUBSCRIPTIONS_INSERT_CAVEATS)


def test_subscriptions_list_metadata_describes_quota_access_selectors_and_boundaries():
    """Keep caller-facing subscriptions metadata complete before invocation."""
    descriptor = build_subscriptions_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "subscriptions_list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert "Quota cost: 1" in metadata_text
    assert "part" in metadata_text
    assert "channelId" in metadata_text
    assert "id" in metadata_text
    assert "mine" in metadata_text
    assert "myRecentSubscribers" in metadata_text
    assert "mySubscribers" in metadata_text
    assert "API-key" in metadata_text
    assert "OAuth" in metadata_text
    assert "pageToken" in metadata_text
    assert "maxResults" in metadata_text
    assert "order" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "Private subscriber" in metadata_text
    assert "enrichment" in metadata_text
    assert "analytics" in metadata_text
    assert metadata["examples"] == list(SUBSCRIPTIONS_LIST_CALLER_EXAMPLES)
    assert SUBSCRIPTIONS_LIST_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(SUBSCRIPTIONS_LIST_USAGE_NOTES)
    assert metadata["caveats"] == list(SUBSCRIPTIONS_LIST_CAVEATS)


def test_subscriptions_list_examples_cover_success_and_safe_failure_boundaries():
    """Expose subscription examples for supported calls and safe failures."""
    descriptor = build_subscriptions_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["channel_subscription_listing"]["quotaCost"] == 1
    assert examples["direct_subscription_lookup"]["arguments"]["id"] == "subscription-123"
    assert examples["current_user_subscriptions"]["arguments"]["mine"] is True
    assert examples["recent_subscribers"]["arguments"]["myRecentSubscribers"] is True
    assert examples["subscriber_list"]["arguments"]["mySubscribers"] is True
    assert examples["paginated_subscription_listing"]["arguments"]["pageToken"] == "NEXT_PAGE"
    assert examples["empty_success"]["result"]["items"] == []
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["invalid_part"]["error"]["field"] == "part"
    assert examples["missing_selector"]["error"]["field"] == "selector"
    assert examples["conflicting_selector"]["error"]["field"] == "selector"
    assert examples["false_boolean_selector"]["error"]["field"] == "selector"
    assert examples["invalid_pagination"]["error"]["field"] == "maxResults"
    assert examples["unsupported_order"]["error"]["field"] == "order"
    assert examples["access_failure"]["error"]["authPath"] == "user_context"
    assert examples["quota_or_upstream_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["not_found_failure"]["error"]["category"] == "not_found"
    assert examples["out_of_scope_enrichment_request"]["error"]["field"] == "includeChannelStatistics"


def test_subscriptions_insert_examples_cover_success_and_safe_failure_boundaries():
    """Expose subscription insert examples for supported calls and safe failures."""
    descriptor = build_subscriptions_insert_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["oauth_subscription_creation"]["quotaCost"] == 50
    assert examples["oauth_subscription_creation"]["arguments"]["body"]["snippet"]["resourceId"]["channelId"] == "UC123"
    assert (
        examples["oauth_subscription_creation_with_kind"]["arguments"]["body"]["snippet"]["resourceId"]["kind"]
        == "youtube#channel"
    )
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["invalid_part"]["error"]["field"] == "part"
    assert examples["missing_body"]["error"]["field"] == "body"
    assert examples["missing_target_channel"]["error"]["field"] == "body.snippet.resourceId.channelId"
    assert examples["invalid_resource_kind"]["error"]["field"] == "body.snippet.resourceId.kind"
    assert examples["unsupported_write_field"]["error"]["field"] == "body.snippet.title"
    assert examples["access_failure"]["error"]["authMode"] == "oauth_required"
    assert examples["duplicate_or_ineligible_target"]["error"]["category"] == "duplicate_target"
    assert examples["quota_or_upstream_create_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["out_of_scope_subscription_management_request"]["error"]["field"] == "deleteExistingSubscription"


def test_subscriptions_list_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope failures."""
    descriptor = build_subscriptions_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_part",
        "invalid_part",
        "missing_selector",
        "conflicting_selector",
        "false_boolean_selector",
        "invalid_pagination",
        "unsupported_order",
        "access_failure",
        "quota_or_upstream_failure",
        "not_found_failure",
        "out_of_scope_enrichment_request",
    }.issubset(error_examples)
    assert error_examples["missing_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["missing_selector"] == {"category": "invalid_request", "field": "selector"}
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["quota_or_upstream_failure"]["category"] == "quota_exhausted"


def test_subscriptions_insert_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope create failures."""
    descriptor = build_subscriptions_insert_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_part",
        "invalid_part",
        "missing_body",
        "missing_target_channel",
        "invalid_resource_kind",
        "unsupported_write_field",
        "access_failure",
        "duplicate_or_ineligible_target",
        "quota_or_upstream_create_failure",
        "out_of_scope_subscription_management_request",
    }.issubset(error_examples)
    assert error_examples["missing_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["missing_target_channel"] == {
        "category": "invalid_request",
        "field": "body.snippet.resourceId.channelId",
    }
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["duplicate_or_ineligible_target"]["category"] == "duplicate_target"
    assert error_examples["quota_or_upstream_create_failure"]["category"] == "quota_exhausted"
