"""Contract tests for the Layer 2 ``search_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.search import (
    SEARCH_LIST_CALLER_EXAMPLES,
    SEARCH_LIST_CAVEATS,
    SEARCH_LIST_DESCRIPTION,
    SEARCH_LIST_INPUT_SCHEMA,
    SEARCH_LIST_MAX_RESULTS,
    SEARCH_LIST_QUOTA_COST,
    SEARCH_LIST_RESTRICTED_FILTERS,
    SEARCH_LIST_TOOL_NAME,
    SEARCH_LIST_USAGE_NOTES,
    SEARCH_LIST_VIDEO_ONLY_FILTERS,
    build_search_list_contract,
    build_search_list_tool_descriptor,
)


def test_search_list_public_symbols_are_exported():
    """Expose ``search_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import search

    assert youtube_common.SEARCH_LIST_TOOL_NAME == "search_list"
    assert SEARCH_LIST_TOOL_NAME == "search_list"
    assert SEARCH_LIST_QUOTA_COST == 100
    assert SEARCH_LIST_RESTRICTED_FILTERS == ("forContentOwner", "forDeveloper", "forMine")
    assert "videoDuration" in SEARCH_LIST_VIDEO_ONLY_FILTERS
    assert callable(search.build_search_list_contract)


def test_search_list_schema_preserves_supported_search_inputs():
    """Expose the supported ``search_list`` request shape."""
    properties = SEARCH_LIST_INPUT_SCHEMA["properties"]

    assert SEARCH_LIST_INPUT_SCHEMA["required"] == ["part", "q"]
    assert properties["part"] == {"type": "string", "minLength": 1}
    assert properties["q"] == {"type": "string", "minLength": 1}
    assert properties["pageToken"] == {"type": "string", "minLength": 1}
    assert properties["maxResults"] == {"type": "integer", "minimum": 0, "maximum": SEARCH_LIST_MAX_RESULTS}
    assert properties["forMine"] == {"type": "boolean"}
    assert properties["videoDuration"] == {"type": "string", "minLength": 1}
    assert SEARCH_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_search_list_public_contract_identifies_endpoint_and_result_shape():
    """Expose endpoint identity, quota, conditional auth, and list metadata."""
    contract = build_search_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.DOCUMENTATION_CAVEAT
    assert metadata["name"] == "search_list"
    assert metadata["upstream"]["operationKey"] == "search.list"
    assert metadata["quotaCost"] == 100
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "documentation_caveat"
    assert metadata["resourceFamily"] == "search"
    assert metadata["inputContract"] == SEARCH_LIST_INPUT_SCHEMA
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"
    assert metadata["responseConvention"]["restrictedFields"] == list(SEARCH_LIST_RESTRICTED_FILTERS)
    assert metadata["responseConvention"]["videoOnlyFields"] == list(SEARCH_LIST_VIDEO_ONLY_FILTERS)
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"


def test_search_list_metadata_describes_quota_access_filters_and_boundaries():
    """Keep caller-facing search metadata complete before invocation."""
    descriptor = build_search_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join(
        [
            descriptor["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
            *[example["description"] for example in metadata["examples"]],
        ]
    )

    assert descriptor["name"] == "search_list"
    assert metadata["quotaCost"] == 100
    assert metadata["authMode"] == "mixed/conditional"
    assert "Quota cost: 100" in metadata_text
    assert "part" in metadata_text
    assert "q" in metadata_text
    assert "API-key" in metadata_text
    assert "OAuth" in metadata_text
    assert "pageToken" in metadata_text
    assert "maxResults" in metadata_text
    assert "empty" in metadata_text.lower()
    assert "Video-specific" in metadata_text
    assert "hydrate" in metadata_text or "hydration" in metadata_text
    assert "transcript" in metadata_text
    assert "ranking" in metadata_text
    assert metadata["examples"] == list(SEARCH_LIST_CALLER_EXAMPLES)
    assert SEARCH_LIST_DESCRIPTION in descriptor["description"]
    assert metadata["usageNotes"] == list(SEARCH_LIST_USAGE_NOTES)
    assert metadata["caveats"] == list(SEARCH_LIST_CAVEATS)


def test_search_list_examples_cover_success_and_safe_failure_boundaries():
    """Expose search examples for supported calls and safe failures."""
    descriptor = build_search_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}

    assert examples["public_keyword_search"]["quotaCost"] == 100
    assert examples["type_filtered_video_search"]["arguments"]["type"] == "video"
    assert examples["channel_scoped_search"]["arguments"]["channelId"] == "UC123"
    assert examples["date_and_locale_refinement"]["arguments"]["regionCode"] == "US"
    assert examples["restricted_oauth_search"]["arguments"]["forMine"] is True
    assert examples["paginated_search"]["arguments"]["pageToken"] == "NEXT_PAGE"
    assert examples["empty_success"]["result"]["items"] == []
    assert examples["missing_query"]["error"]["field"] == "q"
    assert examples["missing_part"]["error"]["field"] == "part"
    assert examples["incompatible_video_filter"]["error"]["field"] == "type"
    assert examples["restricted_filter_conflict"]["error"]["field"] == "restricted_filter"
    assert examples["invalid_pagination"]["error"]["field"] == "pageToken"
    assert examples["access_failure"]["error"]["authPath"] == "restricted"
    assert examples["quota_or_upstream_failure"]["error"]["category"] == "quota_exhausted"
    assert examples["out_of_scope_enrichment_request"]["error"]["field"] == "includeTranscript"


def test_search_list_failure_examples_cover_safe_rejection_surface():
    """Expose representative invalid, access, upstream, and out-of-scope failures."""
    descriptor = build_search_list_tool_descriptor()
    examples = {example["name"]: example for example in descriptor["metadata"]["examples"]}
    error_examples = {name: example["error"] for name, example in examples.items() if "error" in example}

    assert {
        "missing_query",
        "missing_part",
        "incompatible_video_filter",
        "restricted_filter_conflict",
        "invalid_pagination",
        "access_failure",
        "quota_or_upstream_failure",
        "out_of_scope_enrichment_request",
    }.issubset(error_examples)
    assert error_examples["missing_query"] == {"category": "invalid_request", "field": "q"}
    assert error_examples["missing_part"] == {"category": "invalid_request", "field": "part"}
    assert error_examples["access_failure"]["category"] == "authentication_failed"
    assert error_examples["quota_or_upstream_failure"]["category"] == "quota_exhausted"
