"""Contract tests for the concrete Layer 2 ``guideCategories`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.guide_categories import (
    GUIDE_CATEGORIES_LIST_INPUT_SCHEMA,
    GUIDE_CATEGORIES_LIST_TOOL_NAME,
    build_guide_categories_list_contract,
    build_guide_categories_list_tool_descriptor,
)


def test_guide_categories_list_public_symbols_are_exported():
    """Expose ``guideCategories_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import guide_categories

    assert youtube_common.GUIDE_CATEGORIES_LIST_TOOL_NAME == "guideCategories_list"
    assert GUIDE_CATEGORIES_LIST_TOOL_NAME == "guideCategories_list"
    assert callable(guide_categories.build_guide_categories_list_tool_descriptor)


def test_guide_categories_list_schema_preserves_selector_and_localization_inputs():
    """Expose the upstream-like request fields for ``guideCategories_list``."""
    properties = GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["properties"]

    assert GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "regionCode", "id", "hl"}.issubset(properties)
    assert GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["oneOf"] == [
        {"required": ["regionCode"]},
        {"required": ["id"]},
    ]
    assert GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_guide_categories_list_public_contract_identifies_legacy_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list response metadata."""
    contract = build_guide_categories_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.DEPRECATED
    assert metadata["name"] == "guideCategories_list"
    assert metadata["upstream"]["operationKey"] == "guideCategories.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "deprecated"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"regionCode", "id", "hl"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"


def test_guide_categories_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_guide_categories_list_tool_descriptor()

    assert descriptor["name"] == "guideCategories_list"
    assert descriptor["inputSchema"] == GUIDE_CATEGORIES_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "guideCategories.list"
    assert descriptor["metadata"]["quotaCost"] == 1


def test_guide_categories_list_metadata_exposes_quota_auth_examples_and_caveats():
    """Expose safe caller-facing metadata before ``guideCategories_list`` invocation."""
    from mcp_server.tools.youtube_common.guide_categories import GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES

    metadata = build_guide_categories_list_contract().to_tool_metadata()
    descriptor = build_guide_categories_list_tool_descriptor()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])
    example_names = {example["name"] for example in GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES}

    assert metadata["quotaCost"] == 1
    assert "Quota cost: 1" in metadata["description"]
    assert any("Auth: api_key" in note for note in metadata["usageNotes"])
    assert "deprecated" in metadata_text.lower()
    assert "regionCode" in metadata_text
    assert "id" in metadata_text
    assert "hl" in metadata_text
    assert {"region_lookup", "id_lookup", "localized_lookup"}.issubset(example_names)
    assert descriptor["metadata"]["examples"]
    assert "apiKey" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "stack" not in str(metadata).lower()
