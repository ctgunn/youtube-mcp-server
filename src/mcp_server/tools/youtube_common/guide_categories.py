"""Concrete Layer 2 tool support for the YouTube ``guideCategories`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.guide_categories import build_guide_categories_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


GUIDE_CATEGORIES_LIST_TOOL_NAME = "guideCategories_list"
GUIDE_CATEGORIES_LIST_QUOTA_COST = 1
GUIDE_CATEGORIES_LIST_SELECTORS = ("regionCode", "id")

GUIDE_CATEGORIES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "regionCode": {"type": "string", "minLength": 2, "maxLength": 2},
        "id": {"type": "string", "minLength": 1},
        "hl": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in GUIDE_CATEGORIES_LIST_SELECTORS],
    "additionalProperties": False,
}

GUIDE_CATEGORIES_LIST_DESCRIPTION = (
    "List legacy YouTube guide categories. Endpoint: guideCategories.list. "
    "Quota cost: 1. Auth: api_key. Availability: deprecated."
)

GUIDE_CATEGORIES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part and exactly one selector: regionCode or id.",
    "Quota cost: 1. Optional hl requests localized guide-category text when legacy behavior supports it.",
    "Quota cost: 1. The guideCategories.list endpoint is deprecated and may be unavailable.",
)

GUIDE_CATEGORIES_LIST_CAVEATS = (
    "This legacy endpoint is deprecated and omitted from current primary reference navigation.",
    "This is a read-only guide-category lookup; it does not list channels or video categories.",
    "Higher-level behavior such as search, recommendation, ranking, summarization, enrichment, and taxonomy migration is out of scope.",
)

GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES = (
    {
        "name": "region_lookup",
        "description": "Quota cost: 1. List legacy guide categories for one region.",
        "arguments": {"part": "snippet", "regionCode": "US"},
        "result": {"endpoint": "guideCategories.list", "selector": "regionCode", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "id_lookup",
        "description": "Quota cost: 1. Retrieve one legacy guide category by id.",
        "arguments": {"part": "snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl"},
        "result": {"endpoint": "guideCategories.list", "selector": "id", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "localized_lookup",
        "description": "Quota cost: 1. Request localized legacy guide-category text.",
        "arguments": {"part": "snippet", "regionCode": "US", "hl": "es"},
        "quotaCost": 1,
    },
)


class GuideCategoriesListToolError(ValueError):
    """Represent a safe caller-facing ``guideCategories_list`` failure.

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


def _split_ids(ids: str) -> list[str]:
    """Normalize a comma-delimited guide category identifier selection.

    :param ids: Caller-provided guide category identifiers.
    :return: Visible guide category identifiers in caller order.
    """
    return [item.strip() for item in ids.split(",") if item.strip()]


def validate_guide_categories_list_arguments(arguments: dict[str, Any]) -> tuple[str, str]:
    """Validate a ``guideCategories_list`` request and return its selector.

    :param arguments: Candidate tool arguments.
    :return: Selected lookup field and value.
    :raises GuideCategoriesListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise GuideCategoriesListToolError("guideCategories_list arguments must be an object")
    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise GuideCategoriesListToolError("guideCategories_list requires part", details={"field": "part"})

    allowed = {"part", "regionCode", "id", "hl"}
    for field in arguments:
        if field not in allowed:
            raise GuideCategoriesListToolError(
                f"unsupported field for guideCategories_list: {field}",
                details={"field": field},
            )

    selected = [
        selector
        for selector in GUIDE_CATEGORIES_LIST_SELECTORS
        if isinstance(arguments.get(selector), str) and arguments[selector].strip()
    ]
    if len(selected) != 1:
        raise GuideCategoriesListToolError(
            "guideCategories_list requires exactly one selector: regionCode or id",
            details={"field": "selector", "allowed": list(GUIDE_CATEGORIES_LIST_SELECTORS)},
        )

    selector = selected[0]
    value = str(arguments[selector]).strip()
    if selector == "regionCode" and (len(value) != 2 or not value.isalpha()):
        raise GuideCategoriesListToolError("regionCode must be a two-letter code", details={"field": "regionCode"})
    if selector == "id" and not _split_ids(value):
        raise GuideCategoriesListToolError("id must include at least one guide category identifier", details={"field": "id"})
    hl = arguments.get("hl")
    if hl is not None and (
        not isinstance(hl, str)
        or not hl.strip()
        or any(character.isspace() for character in hl.strip())
        or not all(character.isalnum() or character in {"-", "_"} for character in hl.strip())
    ):
        raise GuideCategoriesListToolError("hl must be a non-empty language code", details={"field": "hl"})
    return selector, value


def map_guide_categories_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream guide-category payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 guide-category list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    selector, value = validate_guide_categories_list_arguments(arguments)
    result = {
        "endpoint": "guideCategories.list",
        "quotaCost": GUIDE_CATEGORIES_LIST_QUOTA_COST,
        "requestedParts": _split_parts(arguments["part"]),
        "selector": {"mode": selector, selector: _split_ids(value) if selector == "id" else value},
        "availability": {"state": "deprecated"},
        "items": payload.get("items", []),
    }
    if "hl" in arguments:
        result["localization"] = {"hl": arguments["hl"].strip()}
    for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> GuideCategoriesListToolError:
    """Map a normalized upstream failure to a safe ``guideCategories_list`` error.

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
        "removed": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return GuideCategoriesListToolError(str(error), category=category, details=error.details)


def build_guide_categories_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``guideCategories_list``.

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
            "availability",
            "items",
            "kind",
            "etag",
            "id",
            "snippet",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "items"),
        disallowed_behavior=(
            "channel_listing",
            "channel_category_assignment",
            "video_category_lookup",
            "search",
            "recommendation",
            "ranking",
            "summarization",
            "enrichment",
            "taxonomy_migration",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=GUIDE_CATEGORIES_LIST_TOOL_NAME,
        upstream_resource="guideCategories",
        upstream_method="list",
        operation_key="guideCategories.list",
        description=GUIDE_CATEGORIES_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=GUIDE_CATEGORIES_LIST_QUOTA_COST,
        resource_family="guide_categories",
        input_contract=GUIDE_CATEGORIES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "selectorFields": list(GUIDE_CATEGORIES_LIST_SELECTORS),
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
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.DEPRECATED,
        usage_notes=GUIDE_CATEGORIES_LIST_USAGE_NOTES,
        caveats=GUIDE_CATEGORIES_LIST_CAVEATS,
    )


def _default_guide_categories_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default guide-category calls.

    :return: Integration executor returning representative guide-category data.
    """
    def transport(execution):
        """Return a representative guide-category list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "items": [
                {
                    "kind": "youtube#guideCategory",
                    "id": "guide-category-123",
                    "snippet": {"title": "Best of YouTube"},
                }
            ]
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_guide_categories_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``guideCategories_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps guide-category lookups.
    """
    selected_wrapper = wrapper or build_guide_categories_list_wrapper()
    selected_executor = executor or _default_guide_categories_executor()
    auth_context = AuthContext(
        mode=Layer1AuthMode.API_KEY,
        credentials=CredentialBundle(api_key=api_key),
    )

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``guideCategories_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 guide-category list result.
        :raises GuideCategoriesListToolError: If validation or execution fails.
        """
        validate_guide_categories_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_upstream_error(exc) from exc
        return map_guide_categories_list_result(payload, arguments)

    return handler


def build_guide_categories_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``guideCategories_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_guide_categories_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES)
    return {
        "name": GUIDE_CATEGORIES_LIST_TOOL_NAME,
        "description": GUIDE_CATEGORIES_LIST_DESCRIPTION,
        "inputSchema": GUIDE_CATEGORIES_LIST_INPUT_SCHEMA,
        "handler": build_guide_categories_list_handler(wrapper=wrapper, executor=executor, api_key=api_key),
        "metadata": metadata,
    }


__all__ = [
    "GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES",
    "GUIDE_CATEGORIES_LIST_CAVEATS",
    "GUIDE_CATEGORIES_LIST_DESCRIPTION",
    "GUIDE_CATEGORIES_LIST_INPUT_SCHEMA",
    "GUIDE_CATEGORIES_LIST_QUOTA_COST",
    "GUIDE_CATEGORIES_LIST_SELECTORS",
    "GUIDE_CATEGORIES_LIST_TOOL_NAME",
    "GUIDE_CATEGORIES_LIST_USAGE_NOTES",
    "GuideCategoriesListToolError",
    "build_guide_categories_list_contract",
    "build_guide_categories_list_handler",
    "build_guide_categories_list_tool_descriptor",
    "map_guide_categories_list_result",
    "validate_guide_categories_list_arguments",
]
