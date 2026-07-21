"""Concrete Layer 2 tool support for YouTube ``videoCategories``."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.video_categories import build_video_categories_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


VIDEO_CATEGORIES_LIST_TOOL_NAME = "videoCategories_list"
VIDEO_CATEGORIES_LIST_QUOTA_COST = 1
VIDEO_CATEGORIES_LIST_SELECTORS = ("regionCode", "id")
VIDEO_CATEGORIES_LIST_ALLOWED_FIELDS = frozenset({"part", "regionCode", "id", "hl"})
VIDEO_CATEGORIES_LIST_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "authorization",
        "authorization_header",
        "headers",
        "request_headers",
        "request_context",
        "response_body",
        "upstream_body",
    }
)

VIDEO_CATEGORIES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "regionCode": {"type": "string", "minLength": 2, "maxLength": 2},
        "id": {"type": "string", "minLength": 1},
        "hl": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in VIDEO_CATEGORIES_LIST_SELECTORS],
    "additionalProperties": False,
}

VIDEO_CATEGORIES_LIST_DESCRIPTION = (
    "List YouTube video categories. Endpoint: videoCategories.list. Quota cost: 1. "
    "Auth: api_key API-key access. Requires part and exactly one selector: regionCode or id."
)

VIDEO_CATEGORIES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part, usually snippet, and exactly one selector: regionCode or id.",
    "Quota cost: 1. Optional hl requests localized video category text when upstream provides it.",
    "Quota cost: 1. Empty upstream items are returned as a successful empty video categories list.",
)

VIDEO_CATEGORIES_LIST_CAVEATS = (
    "This tool is a read-only video category lookup; video search is handled by search_list.",
    "category recommendation, analytics, ranking, summarization, enrichment, and automatic video classification are out of scope.",
    "The tool preserves upstream category fields and does not fabricate labels, translations, or recommendations.",
)

VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES = (
    {
        "name": "region_category_lookup",
        "description": "Quota cost: 1. List active video categories for one regionCode.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "result": {"endpoint": "videoCategories.list", "selector": "regionCode", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "category_id_lookup",
        "description": "Quota cost: 1. Retrieve one or more video categories by id.",
        "arguments": {"part": "snippet", "id": "10,20"},
        "result": {"endpoint": "videoCategories.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "localized_category_lookup",
        "description": "Quota cost: 1. Request localized category text with optional hl.",
        "arguments": {"part": "snippet", "regionCode": "US", "hl": "es"},
        "result": {"endpoint": "videoCategories.list", "localization": {"hl": "es"}},
        "quotaCost": 1,
    },
    {
        "name": "populated_success",
        "description": "Quota cost: 1. Successful lookup with one or more upstream video category items.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "result": {"items": [{"id": "10"}], "empty": False},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. Empty upstream items remain a successful empty category list result.",
        "arguments": {"part": "snippet", "id": "999999"},
        "result": {"items": [], "empty": True},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 1. Missing part is rejected before upstream execution.",
        "arguments": {"regionCode": "US"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_selector",
        "description": "Quota cost: 1. Missing regionCode or id selector is rejected before upstream execution.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "conflicting_selectors",
        "description": "Quota cost: 1. Supplying both regionCode and id is rejected as ambiguous.",
        "arguments": {"part": "snippet", "regionCode": "US", "id": "10"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_hl",
        "description": "Quota cost: 1. Empty or whitespace-containing hl values are rejected.",
        "arguments": {"part": "snippet", "regionCode": "US", "hl": "bad language"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 1. Missing API-key access is reported as an authentication failure.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 1. Quota and upstream failures are mapped to safe public categories.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "deprecated_endpoint",
        "description": "Quota cost: 1. Deprecated endpoint failures are surfaced distinctly if upstream reports them.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "errorCategory": "deprecated_endpoint",
    },
    {
        "name": "endpoint_unavailable",
        "description": "Quota cost: 1. Endpoint availability failures are surfaced without unsafe upstream details.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "out_of_scope_category_analysis",
        "description": "Quota cost: 1. Category recommendation and analysis requests are rejected as unsupported fields.",
        "arguments": {"part": "snippet", "regionCode": "US", "recommendation": "pick a category"},
        "errorCategory": "invalid_request",
    },
)


class VideoCategoriesListToolError(ValueError):
    """Represent a safe caller-facing ``videoCategories_list`` failure.

    :param message: Caller-facing error message.
    :param category: Stable Layer 2 error category.
    :param details: Safe diagnostic details.
    """

    def __init__(self, message: str, *, category: str = "invalid_request", details: dict[str, Any] | None = None):
        """Initialize the safe tool error.

        :param message: Caller-facing error message.
        :param category: Stable Layer 2 error category.
        :param details: Safe diagnostic details.
        """
        super().__init__(message)
        self.category = category
        self.details = _sanitize_video_categories_list_error_details(details or {})


def _sanitize_video_categories_list_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove endpoint-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEO_CATEGORIES_LIST_UNSAFE_DETAIL_KEYS
    }


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited ``part`` selection.

    :param parts: Caller-provided ``part`` value.
    :return: Requested parts in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _split_ids(ids: str) -> list[str]:
    """Normalize a comma-delimited video category identifier selection.

    :param ids: Caller-provided category identifiers.
    :return: Visible category identifiers in caller order.
    """
    return [item.strip() for item in ids.split(",") if item.strip()]


def _require_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideoCategoriesListToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideoCategoriesListToolError(
            f"videoCategories_list requires non-empty {field}",
            details={"field": field},
        )
    return value.strip()


def _validate_hl(value: Any) -> str:
    """Validate and normalize an optional ``hl`` localization value.

    :param value: Candidate language or locale code.
    :return: Stripped language or locale code.
    :raises VideoCategoriesListToolError: If ``hl`` is malformed.
    """
    if not isinstance(value, str) or not value.strip():
        raise VideoCategoriesListToolError("hl must be a non-empty language or locale code", details={"field": "hl"})
    normalized = value.strip()
    if any(character.isspace() for character in normalized) or not all(
        character.isalnum() or character in {"-", "_"} for character in normalized
    ):
        raise VideoCategoriesListToolError("hl must be a non-empty language or locale code", details={"field": "hl"})
    return normalized


def _selected_selector(arguments: dict[str, Any]) -> tuple[str, str]:
    """Return the exactly-one non-empty category selector.

    :param arguments: Candidate normalized request arguments.
    :return: Selected selector field and stripped value.
    :raises VideoCategoriesListToolError: If selector input is missing or ambiguous.
    """
    selected = [
        selector
        for selector in VIDEO_CATEGORIES_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise VideoCategoriesListToolError(
            "videoCategories_list requires exactly one selector: regionCode or id",
            details={"field": "selector", "allowed": list(VIDEO_CATEGORIES_LIST_SELECTORS)},
        )
    selector = selected[0]
    return selector, str(arguments[selector]).strip()


def validate_video_categories_list_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate ``videoCategories_list`` arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized ``part``, selector, and optional ``hl`` values.
    :raises VideoCategoriesListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideoCategoriesListToolError("videoCategories_list arguments must be an object")
    for field in arguments:
        if field not in VIDEO_CATEGORIES_LIST_ALLOWED_FIELDS:
            raise VideoCategoriesListToolError(
                f"unsupported field for videoCategories_list: {field}",
                details={"field": field},
            )

    part = _require_text_field(arguments, "part")
    if not _split_parts(part):
        raise VideoCategoriesListToolError(
            "part must include at least one requested resource part",
            details={"field": "part"},
        )

    selector, value = _selected_selector(arguments)
    if selector == "regionCode":
        if len(value) != 2 or not value.isalpha():
            raise VideoCategoriesListToolError("regionCode must be a two-letter code", details={"field": "regionCode"})
        value = value.upper()
    elif not _split_ids(value):
        raise VideoCategoriesListToolError(
            "id must include at least one video category identifier",
            details={"field": "id"},
        )

    normalized = {"part": part, selector: value}
    if "hl" in arguments:
        normalized["hl"] = _validate_hl(arguments["hl"])
    return normalized


def _selector_context(arguments: dict[str, str]) -> dict[str, Any]:
    """Build safe selector context for public result payloads.

    :param arguments: Normalized caller arguments.
    :return: Selector context preserving region or ID lookup intent.
    """
    if "id" in arguments:
        return {"mode": "id", "id": _split_ids(arguments["id"])}
    return {"mode": "regionCode", "regionCode": arguments["regionCode"]}


def map_video_categories_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream category-list payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video category list payload.
    :param arguments: Caller arguments used for the request.
    :return: Near-raw category list result with safe operation context.
    """
    normalized = validate_video_categories_list_arguments(arguments)
    items = payload.get("items", []) if isinstance(payload, dict) else []
    result = {
        "endpoint": "videoCategories.list",
        "quotaCost": VIDEO_CATEGORIES_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "selector": _selector_context(normalized),
        "auth": {"mode": "api_key"},
        "availability": {"state": "active"},
        "items": items,
        "empty": not bool(items),
    }
    if "hl" in normalized:
        result["localization"] = {"hl": normalized["hl"]}
    if isinstance(payload, dict):
        for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
            if field in payload:
                result[field] = payload[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> VideoCategoriesListToolError:
    """Map a normalized upstream failure to a safe ``videoCategories_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe caller-facing tool error.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "not_found": "resource_not_found",
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideoCategoriesListToolError(str(error), category=category, details=error.details or {})


def _api_key_auth_context(api_key: str | None) -> AuthContext:
    """Build the Layer 1 API-key auth context.

    :param api_key: API key credential value.
    :return: Layer 1 auth context for API-key execution.
    :raises VideoCategoriesListToolError: If API-key access is missing.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise VideoCategoriesListToolError(
            "videoCategories_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        )
    try:
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))
    except ValueError as exc:
        raise VideoCategoriesListToolError(
            "videoCategories_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        ) from exc


def build_video_categories_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``videoCategories_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "selector",
            "localization",
            "auth",
            "availability",
            "items",
            "empty",
            "kind",
            "etag",
            "pageInfo",
            "nextPageToken",
            "prevPageToken",
            "id",
            "snippet",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "items", "pageInfo"),
        disallowed_behavior=(
            "video_search",
            "category_recommendation",
            "analytics",
            "ranking",
            "summarization",
            "enrichment",
            "automatic_classification",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=VIDEO_CATEGORIES_LIST_TOOL_NAME,
        upstream_resource="videoCategories",
        upstream_method="list",
        operation_key="videoCategories.list",
        description=VIDEO_CATEGORIES_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=VIDEO_CATEGORIES_LIST_QUOTA_COST,
        resource_family="video_categories",
        input_contract=VIDEO_CATEGORIES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "selectorFields": list(VIDEO_CATEGORIES_LIST_SELECTORS),
            "localizationFields": ["hl"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEO_CATEGORIES_LIST_USAGE_NOTES,
        caveats=VIDEO_CATEGORIES_LIST_CAVEATS,
    )


def _default_video_categories_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default category-list calls.

    :return: Integration executor returning representative category data.
    """

    def transport(_execution):
        """Return a representative video category list response.

        :param _execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#videoCategoryListResponse",
            "items": [
                {
                    "kind": "youtube#videoCategory",
                    "id": "10",
                    "snippet": {"title": "Music", "assignable": True},
                }
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_video_categories_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``videoCategories_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps category-list lookups.
    """
    selected_wrapper = wrapper or build_video_categories_list_wrapper()
    selected_executor = executor or _default_video_categories_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videoCategories_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video category list result.
        :raises VideoCategoriesListToolError: If validation or execution fails.
        """
        normalized = validate_video_categories_list_arguments(arguments)
        auth_context = _api_key_auth_context(api_key)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_upstream_error(exc) from exc
        except ValueError as exc:
            raise VideoCategoriesListToolError(
                str(exc),
                category="authentication_failed",
                details={"authMode": "api_key"},
            ) from exc
        return map_video_categories_list_result(payload, normalized)

    return handler


def build_video_categories_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videoCategories_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_video_categories_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES)
    return {
        "name": VIDEO_CATEGORIES_LIST_TOOL_NAME,
        "description": VIDEO_CATEGORIES_LIST_DESCRIPTION,
        "inputSchema": VIDEO_CATEGORIES_LIST_INPUT_SCHEMA,
        "handler": build_video_categories_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


__all__ = [
    "VIDEO_CATEGORIES_LIST_ALLOWED_FIELDS",
    "VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES",
    "VIDEO_CATEGORIES_LIST_CAVEATS",
    "VIDEO_CATEGORIES_LIST_DESCRIPTION",
    "VIDEO_CATEGORIES_LIST_INPUT_SCHEMA",
    "VIDEO_CATEGORIES_LIST_QUOTA_COST",
    "VIDEO_CATEGORIES_LIST_SELECTORS",
    "VIDEO_CATEGORIES_LIST_TOOL_NAME",
    "VIDEO_CATEGORIES_LIST_UNSAFE_DETAIL_KEYS",
    "VIDEO_CATEGORIES_LIST_USAGE_NOTES",
    "VideoCategoriesListToolError",
    "build_video_categories_list_contract",
    "build_video_categories_list_handler",
    "build_video_categories_list_tool_descriptor",
    "map_video_categories_list_result",
    "validate_video_categories_list_arguments",
]
