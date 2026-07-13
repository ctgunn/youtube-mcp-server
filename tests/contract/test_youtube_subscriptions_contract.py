"""Contract tests for the Layer 2 ``subscriptions_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.subscriptions import (
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
