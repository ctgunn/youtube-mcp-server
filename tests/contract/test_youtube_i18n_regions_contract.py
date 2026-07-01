"""Contract tests for the Layer 2 ``i18nRegions_list`` tool."""

from __future__ import annotations

from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.localization import (
    I18N_REGIONS_LIST_INPUT_SCHEMA,
    I18N_REGIONS_LIST_TOOL_NAME,
    build_i18n_regions_list_contract,
    build_i18n_regions_list_tool_descriptor,
)


def test_i18n_regions_list_public_symbols_are_exported():
    """Expose ``i18nRegions_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import localization

    assert youtube_common.I18N_REGIONS_LIST_TOOL_NAME == "i18nRegions_list"
    assert I18N_REGIONS_LIST_TOOL_NAME == "i18nRegions_list"
    assert callable(localization.build_i18n_regions_list_tool_descriptor)


def test_i18n_regions_list_schema_preserves_part_and_optional_display_language():
    """Expose the upstream-like request fields for ``i18nRegions_list``."""
    properties = I18N_REGIONS_LIST_INPUT_SCHEMA["properties"]

    assert I18N_REGIONS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"]["enum"] == ["snippet"]
    assert "hl" in properties
    assert I18N_REGIONS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_i18n_regions_list_public_contract_identifies_active_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list response metadata."""
    contract = build_i18n_regions_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.API_KEY
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "i18nRegions_list"
    assert metadata["upstream"]["operationKey"] == "i18nRegions.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "api_key"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert "hl" in metadata["inputContract"]["properties"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"


def test_i18n_regions_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_i18n_regions_list_tool_descriptor()

    assert descriptor["name"] == "i18nRegions_list"
    assert descriptor["inputSchema"] == I18N_REGIONS_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "i18nRegions.list"
    assert descriptor["metadata"]["quotaCost"] == 1


def test_i18n_regions_list_metadata_exposes_quota_auth_examples_and_boundaries():
    """Expose safe caller-facing metadata before ``i18nRegions_list`` invocation."""
    from mcp_server.tools.youtube_common.localization import I18N_REGIONS_LIST_CALLER_EXAMPLES

    metadata = build_i18n_regions_list_contract().to_tool_metadata()
    descriptor = build_i18n_regions_list_tool_descriptor()
    metadata_text = " ".join([metadata["description"], *metadata["usageNotes"], *metadata["caveats"]])
    example_names = {example["name"] for example in I18N_REGIONS_LIST_CALLER_EXAMPLES}

    assert metadata["quotaCost"] == 1
    assert "Quota cost: 1" in metadata["description"]
    assert any("Auth: api_key" in note for note in metadata["usageNotes"])
    assert "active" in metadata["availabilityState"]
    assert "part=snippet" in metadata_text
    assert "hl" in metadata_text
    assert "language lookup" in metadata_text
    assert "geotarget" in metadata_text
    assert {
        "default_region_listing",
        "display_language_region_listing",
        "empty_success",
        "missing_part",
        "invalid_part",
        "invalid_display_language",
        "unsupported_option",
        "out_of_scope_language_or_geotargeting_request",
    }.issubset(example_names)
    assert descriptor["metadata"]["examples"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert "cross_endpoint_aggregation" in metadata["responseBoundary"]["disallowedBehavior"]
    assert "apiKey" not in str(metadata)
    assert "oauthToken" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_i18n_regions_list_descriptor_metadata_examples_and_errors_are_secret_free():
    """Keep public ``i18nRegions_list`` metadata free of unsafe diagnostics."""
    descriptor = build_i18n_regions_list_tool_descriptor()
    public_payload = {
        "description": descriptor["description"],
        "inputSchema": descriptor["inputSchema"],
        "metadata": descriptor["metadata"],
    }

    public_text = str(public_payload)

    assert "apiKey" not in public_text
    assert "oauthToken" not in public_text
    assert "stackTrace" not in public_text
    assert "signedUrl" not in public_text
    assert "rawBody" not in public_text
