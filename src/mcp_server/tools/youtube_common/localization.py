"""Concrete Layer 2 tool support for YouTube localization resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.localization import (
    build_i18n_languages_list_wrapper,
    build_i18n_regions_list_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


I18N_LANGUAGES_LIST_TOOL_NAME = "i18nLanguages_list"
I18N_LANGUAGES_LIST_QUOTA_COST = 1
I18N_LANGUAGES_LIST_SUPPORTED_PARTS = ("snippet",)

I18N_LANGUAGES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {
            "type": "string",
            "enum": list(I18N_LANGUAGES_LIST_SUPPORTED_PARTS),
        },
        "hl": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

I18N_LANGUAGES_LIST_DESCRIPTION = (
    "List YouTube application languages. Endpoint: i18nLanguages.list. "
    "Quota cost: 1. Auth: api_key. Availability: active."
)

I18N_LANGUAGES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part=snippet for localization-language reference data.",
    "Quota cost: 1. Optional hl requests language names in a display-language preference.",
    "Quota cost: 1. When hl is omitted, upstream default display-language behavior applies.",
)

I18N_LANGUAGES_LIST_CAVEATS = (
    "This is a read-only localization-language lookup; it does not perform translation or language detection.",
    "This tool does not list regions, caption-language availability, or content-language filters.",
    "Higher-level behavior such as search, recommendation, ranking, summarization, enrichment, and cross-endpoint aggregation is out of scope.",
)

I18N_LANGUAGES_LIST_CALLER_EXAMPLES = (
    {
        "name": "default_language_listing",
        "description": "Quota cost: 1. List YouTube application languages with the default display language.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "i18nLanguages.list", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "display_language_listing",
        "description": "Quota cost: 1. List YouTube application languages with localized display names.",
        "arguments": {"part": "snippet", "hl": "es"},
        "result": {"endpoint": "i18nLanguages.list", "localization": {"hl": "es"}},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. A valid request may return an empty language collection.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "i18nLanguages.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 1. Requests must include part=snippet.",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 1. Unsupported part selections are rejected.",
        "arguments": {"part": "id"},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_display_language",
        "description": "Quota cost: 1. Malformed display-language preferences are rejected.",
        "arguments": {"part": "snippet", "hl": "bad language"},
        "error": {"category": "invalid_request", "field": "hl"},
        "quotaCost": 1,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 1. Unsupported options such as pageToken are rejected.",
        "arguments": {"part": "snippet", "pageToken": "cursor"},
        "error": {"category": "invalid_request", "field": "pageToken"},
        "quotaCost": 1,
    },
    {
        "name": "out_of_scope_translation_or_region_request",
        "description": "Quota cost: 1. Translation and region lookup requests are outside this tool.",
        "arguments": {"part": "snippet", "regionCode": "US", "translate": "hello"},
        "error": {"category": "invalid_request", "field": "regionCode"},
        "quotaCost": 1,
    },
)

I18N_REGIONS_LIST_TOOL_NAME = "i18nRegions_list"
I18N_REGIONS_LIST_QUOTA_COST = 1
I18N_REGIONS_LIST_SUPPORTED_PARTS = ("snippet",)

I18N_REGIONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {
            "type": "string",
            "enum": list(I18N_REGIONS_LIST_SUPPORTED_PARTS),
        },
        "hl": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

I18N_REGIONS_LIST_DESCRIPTION = (
    "List YouTube content regions. Endpoint: i18nRegions.list. "
    "Quota cost: 1. Auth: api_key. Availability: active."
)

I18N_REGIONS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part=snippet for localization-region reference data.",
    "Quota cost: 1. Optional hl requests region names in a display-language preference.",
    "Quota cost: 1. When hl is omitted, upstream default display-language behavior applies.",
)

I18N_REGIONS_LIST_CAVEATS = (
    "This is a read-only localization-region lookup; it does not perform language lookup or translation.",
    "This tool does not validate countries, convert region codes, geotarget content, or filter search results.",
    "Higher-level behavior such as recommendation, ranking, summarization, enrichment, analytics, and cross-endpoint aggregation is out of scope.",
)

I18N_REGIONS_LIST_CALLER_EXAMPLES = (
    {
        "name": "default_region_listing",
        "description": "Quota cost: 1. List YouTube content regions with the default display language.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "i18nRegions.list", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "display_language_region_listing",
        "description": "Quota cost: 1. List YouTube content regions with localized display names.",
        "arguments": {"part": "snippet", "hl": "es"},
        "result": {"endpoint": "i18nRegions.list", "localization": {"hl": "es"}},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. A valid request may return an empty region collection.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "i18nRegions.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 1. Requests must include part=snippet.",
        "arguments": {},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 1. Unsupported part selections are rejected.",
        "arguments": {"part": "id"},
        "error": {"category": "invalid_request", "field": "part"},
        "quotaCost": 1,
    },
    {
        "name": "invalid_display_language",
        "description": "Quota cost: 1. Malformed display-language preferences are rejected.",
        "arguments": {"part": "snippet", "hl": "bad language"},
        "error": {"category": "invalid_request", "field": "hl"},
        "quotaCost": 1,
    },
    {
        "name": "unsupported_option",
        "description": "Quota cost: 1. Unsupported options such as pageToken are rejected.",
        "arguments": {"part": "snippet", "pageToken": "cursor"},
        "error": {"category": "invalid_request", "field": "pageToken"},
        "quotaCost": 1,
    },
    {
        "name": "out_of_scope_language_or_geotargeting_request",
        "description": "Quota cost: 1. Language lookup and geotargeting requests are outside this tool.",
        "arguments": {"part": "snippet", "regionCode": "US", "geotarget": True},
        "error": {"category": "invalid_request", "field": "regionCode"},
        "quotaCost": 1,
    },
)


class I18nLanguagesListToolError(ValueError):
    """Represent a safe caller-facing ``i18nLanguages_list`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


class I18nRegionsListToolError(ValueError):
    """Represent a safe caller-facing ``i18nRegions_list`` failure.

    :param message: Caller-facing error message.
    :param category: Shared Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Shared Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _validate_language_code(value: str) -> bool:
    """Return whether a display-language value is safe and syntactically valid.

    :param value: Caller-provided display-language preference.
    :return: True when the value is non-empty and contains only language-code characters.
    """
    stripped = value.strip()
    return bool(stripped) and not any(character.isspace() for character in stripped) and all(
        character.isalnum() or character in {"-", "_"} for character in stripped
    )


def validate_i18n_languages_list_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate an ``i18nLanguages_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized arguments safe to forward to Layer 1.
    :raises I18nLanguagesListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise I18nLanguagesListToolError("i18nLanguages_list arguments must be an object")
    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise I18nLanguagesListToolError("i18nLanguages_list requires part", details={"field": "part"})

    allowed = {"part", "hl"}
    for field in arguments:
        if field not in allowed:
            raise I18nLanguagesListToolError(
                f"unsupported field for i18nLanguages_list: {field}",
                details={"field": field},
            )

    normalized_parts = _split_parts(part)
    if normalized_parts != ["snippet"]:
        raise I18nLanguagesListToolError(
            "i18nLanguages_list supports only part=snippet",
            details={"field": "part", "allowed": list(I18N_LANGUAGES_LIST_SUPPORTED_PARTS)},
        )

    normalized = {"part": "snippet"}
    hl = arguments.get("hl")
    if hl is not None:
        if not isinstance(hl, str) or not _validate_language_code(hl):
            raise I18nLanguagesListToolError("hl must be a non-empty language code", details={"field": "hl"})
        normalized["hl"] = hl.strip()
    return normalized


def validate_i18n_regions_list_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate an ``i18nRegions_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized arguments safe to forward to Layer 1.
    :raises I18nRegionsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise I18nRegionsListToolError("i18nRegions_list arguments must be an object")
    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise I18nRegionsListToolError("i18nRegions_list requires part", details={"field": "part"})

    allowed = {"part", "hl"}
    for field in arguments:
        if field not in allowed:
            raise I18nRegionsListToolError(
                f"unsupported field for i18nRegions_list: {field}",
                details={"field": field},
            )

    normalized_parts = _split_parts(part)
    if normalized_parts != ["snippet"]:
        raise I18nRegionsListToolError(
            "i18nRegions_list supports only part=snippet",
            details={"field": "part", "allowed": list(I18N_REGIONS_LIST_SUPPORTED_PARTS)},
        )

    normalized = {"part": "snippet"}
    hl = arguments.get("hl")
    if hl is not None:
        if not isinstance(hl, str) or not _validate_language_code(hl):
            raise I18nRegionsListToolError("hl must be a non-empty language code", details={"field": "hl"})
        normalized["hl"] = hl.strip()
    return normalized


def map_i18n_languages_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream i18n-language payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 i18n-language list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_i18n_languages_list_arguments(arguments)
    result = {
        "endpoint": "i18nLanguages.list",
        "quotaCost": I18N_LANGUAGES_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "availability": {"state": "active"},
        "items": payload.get("items", []),
    }
    if "hl" in normalized:
        result["localization"] = {"hl": normalized["hl"]}
    for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
        if field in payload:
            result[field] = payload[field]
    return result


def map_i18n_regions_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream i18n-region payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 i18n-region list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_i18n_regions_list_arguments(arguments)
    result = {
        "endpoint": "i18nRegions.list",
        "quotaCost": I18N_REGIONS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "availability": {"state": "active"},
        "items": payload.get("items", []),
    }
    if "hl" in normalized:
        result["localization"] = {"hl": normalized["hl"]}
    for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> I18nLanguagesListToolError:
    """Map a normalized upstream failure to a safe ``i18nLanguages_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return I18nLanguagesListToolError(str(error), category=category, details=error.details)


def _map_i18n_regions_upstream_error(error: NormalizedUpstreamError) -> I18nRegionsListToolError:
    """Map a normalized upstream failure to a safe ``i18nRegions_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return I18nRegionsListToolError(str(error), category=category, details=error.details)


def build_i18n_languages_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``i18nLanguages_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "localization",
            "availability",
            "items",
            "kind",
            "etag",
            "id",
            "snippet",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "items"),
        disallowed_behavior=(
            "translation",
            "language_detection",
            "text_localization",
            "region_lookup",
            "caption_language_availability",
            "search",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=I18N_LANGUAGES_LIST_TOOL_NAME,
        upstream_resource="i18nLanguages",
        upstream_method="list",
        operation_key="i18nLanguages.list",
        description=I18N_LANGUAGES_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=I18N_LANGUAGES_LIST_QUOTA_COST,
        resource_family="localization",
        input_contract=I18N_LANGUAGES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "partFields": ["part"],
            "localizationFields": ["hl"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "invalid_request",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=I18N_LANGUAGES_LIST_USAGE_NOTES,
        caveats=I18N_LANGUAGES_LIST_CAVEATS,
    )


def build_i18n_regions_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``i18nRegions_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "localization",
            "availability",
            "items",
            "kind",
            "etag",
            "id",
            "snippet",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "items"),
        disallowed_behavior=(
            "language_lookup",
            "translation",
            "country_validation",
            "region_code_conversion",
            "geotargeting",
            "search_filtering",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "analytics",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=I18N_REGIONS_LIST_TOOL_NAME,
        upstream_resource="i18nRegions",
        upstream_method="list",
        operation_key="i18nRegions.list",
        description=I18N_REGIONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=I18N_REGIONS_LIST_QUOTA_COST,
        resource_family="localization",
        input_contract=I18N_REGIONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "partFields": ["part"],
            "localizationFields": ["hl"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "invalid_request",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=I18N_REGIONS_LIST_USAGE_NOTES,
        caveats=I18N_REGIONS_LIST_CAVEATS,
    )


def _default_i18n_languages_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default i18n-language calls.

    :return: Integration executor returning representative i18n-language data.
    """

    def transport(execution):
        """Return a representative i18n-language list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "items": [
                {
                    "kind": "youtube#i18nLanguage",
                    "id": "en",
                    "snippet": {"hl": "en", "name": "English"},
                }
            ]
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_i18n_regions_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default i18n-region calls.

    :return: Integration executor returning representative i18n-region data.
    """

    def transport(execution):
        """Return a representative i18n-region list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "items": [
                {
                    "kind": "youtube#i18nRegion",
                    "id": "US",
                    "snippet": {"gl": "US", "name": "United States"},
                }
            ]
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_i18n_languages_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``i18nLanguages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps i18n-language lookups.
    """
    selected_wrapper = wrapper or build_i18n_languages_list_wrapper()
    selected_executor = executor or _default_i18n_languages_executor()
    auth_context = AuthContext(
        mode=Layer1AuthMode.API_KEY,
        credentials=CredentialBundle(api_key=api_key),
    )

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``i18nLanguages_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 i18n-language list result.
        :raises I18nLanguagesListToolError: If validation or execution fails.
        """
        normalized = validate_i18n_languages_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_upstream_error(exc) from exc
        return map_i18n_languages_list_result(payload, normalized)

    return handler


def build_i18n_regions_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``i18nRegions_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps i18n-region lookups.
    """
    selected_wrapper = wrapper or build_i18n_regions_list_wrapper()
    selected_executor = executor or _default_i18n_regions_executor()
    auth_context = AuthContext(
        mode=Layer1AuthMode.API_KEY,
        credentials=CredentialBundle(api_key=api_key),
    )

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``i18nRegions_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 i18n-region list result.
        :raises I18nRegionsListToolError: If validation or execution fails.
        """
        normalized = validate_i18n_regions_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_i18n_regions_upstream_error(exc) from exc
        return map_i18n_regions_list_result(payload, normalized)

    return handler


def build_i18n_languages_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``i18nLanguages_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_i18n_languages_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(I18N_LANGUAGES_LIST_CALLER_EXAMPLES)
    return {
        "name": I18N_LANGUAGES_LIST_TOOL_NAME,
        "description": I18N_LANGUAGES_LIST_DESCRIPTION,
        "inputSchema": I18N_LANGUAGES_LIST_INPUT_SCHEMA,
        "handler": build_i18n_languages_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


def build_i18n_regions_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``i18nRegions_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_i18n_regions_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(I18N_REGIONS_LIST_CALLER_EXAMPLES)
    return {
        "name": I18N_REGIONS_LIST_TOOL_NAME,
        "description": I18N_REGIONS_LIST_DESCRIPTION,
        "inputSchema": I18N_REGIONS_LIST_INPUT_SCHEMA,
        "handler": build_i18n_regions_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


__all__ = [
    "I18N_LANGUAGES_LIST_CALLER_EXAMPLES",
    "I18N_LANGUAGES_LIST_CAVEATS",
    "I18N_LANGUAGES_LIST_DESCRIPTION",
    "I18N_LANGUAGES_LIST_INPUT_SCHEMA",
    "I18N_LANGUAGES_LIST_QUOTA_COST",
    "I18N_LANGUAGES_LIST_SUPPORTED_PARTS",
    "I18N_LANGUAGES_LIST_TOOL_NAME",
    "I18N_LANGUAGES_LIST_USAGE_NOTES",
    "I18N_REGIONS_LIST_CALLER_EXAMPLES",
    "I18N_REGIONS_LIST_CAVEATS",
    "I18N_REGIONS_LIST_DESCRIPTION",
    "I18N_REGIONS_LIST_INPUT_SCHEMA",
    "I18N_REGIONS_LIST_QUOTA_COST",
    "I18N_REGIONS_LIST_SUPPORTED_PARTS",
    "I18N_REGIONS_LIST_TOOL_NAME",
    "I18N_REGIONS_LIST_USAGE_NOTES",
    "I18nLanguagesListToolError",
    "I18nRegionsListToolError",
    "build_i18n_languages_list_contract",
    "build_i18n_languages_list_handler",
    "build_i18n_languages_list_tool_descriptor",
    "build_i18n_regions_list_contract",
    "build_i18n_regions_list_handler",
    "build_i18n_regions_list_tool_descriptor",
    "map_i18n_languages_list_result",
    "map_i18n_regions_list_result",
    "validate_i18n_languages_list_arguments",
    "validate_i18n_regions_list_arguments",
]
