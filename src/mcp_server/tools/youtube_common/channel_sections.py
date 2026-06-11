"""Concrete Layer 2 tool support for the YouTube ``channelSections`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.channel_sections import build_channel_sections_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


CHANNEL_SECTIONS_LIST_TOOL_NAME = "channelSections_list"
CHANNEL_SECTIONS_LIST_QUOTA_COST = 1
CHANNEL_SECTIONS_LIST_SELECTORS = ("channelId", "id", "mine")

CHANNEL_SECTIONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "hl": {"type": "string", "minLength": 1, "deprecated": True},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in CHANNEL_SECTIONS_LIST_SELECTORS],
    "additionalProperties": False,
}

CHANNEL_SECTIONS_LIST_DESCRIPTION = (
    "List YouTube channel sections. Endpoint: channelSections.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)
CHANNEL_SECTIONS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId or id for public channel-section lookup.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for the authenticated user's channel sections.",
    "Quota cost: 1. Valid lookups that match no channel sections return a successful empty item collection.",
    "Quota cost: 1. hl is deprecated for localized channel-section metadata in current official documentation.",
    "Quota cost: 1. onBehalfOfContentOwner is partner-scoped and requires eligible OAuth authorization when supported.",
    "Quota cost: 1. Continuation fields are preserved when returned, but pagination request controls are compatibility-only for this endpoint.",
)
CHANNEL_SECTIONS_LIST_CAVEATS = (
    "Exactly one selector is required: channelId, id, or mine.",
    "The hl localization parameter is deprecated in current official YouTube documentation.",
    "onBehalfOfContentOwner is intended only for eligible YouTube content partners and is not public API-key behavior.",
    "Pagination request fields are not a first-class official channelSections.list promise in this slice.",
    "This low-level tool does not expand playlist items, expand videos, rank sections, recommend layouts, or mutate channel sections.",
)
CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES = (
    {
        "name": "channel_id_lookup",
        "arguments": {"part": "snippet,contentDetails", "channelId": "UC123"},
        "result": {
            "endpoint": "channelSections.list",
            "quotaCost": 1,
            "selector": {"name": "channelId"},
            "requestedParts": ["snippet", "contentDetails"],
            "items": [{"id": "section-123"}],
        },
        "notes": "Lists channel sections for one public channel ID.",
    },
    {
        "name": "section_id_lookup",
        "arguments": {"part": "snippet", "id": "section-123"},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "selector": {"name": "id"}},
        "notes": "Looks up one or more channel sections by channel-section ID.",
    },
    {
        "name": "authorized_mine_lookup",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "selector": {"name": "mine"}},
        "notes": "Requires eligible OAuth authorization for the authenticated user's channel sections.",
    },
    {
        "name": "empty_result",
        "arguments": {"part": "snippet", "channelId": "UC-missing"},
        "result": {"endpoint": "channelSections.list", "quotaCost": 1, "items": []},
        "notes": "A valid no-match lookup is a successful empty collection.",
    },
    {
        "name": "deprecated_hl_caveat",
        "arguments": {"part": "snippet", "channelId": "UC123", "hl": "es"},
        "result": {"endpoint": "channelSections.list", "caveats": {"hlDeprecated": True}},
        "notes": "hl is deprecated and remains visible as a compatibility caveat.",
    },
    {
        "name": "content_owner_partner_caveat",
        "arguments": {"part": "snippet", "channelId": "UC123", "onBehalfOfContentOwner": "content-owner-id"},
        "error": {"category": "invalid_request", "field": "onBehalfOfContentOwner"},
        "notes": "Content-owner context is partner-scoped and not public API-key behavior.",
    },
    {
        "name": "missing_selector",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Exactly one selector is required.",
    },
    {
        "name": "conflicting_selectors",
        "arguments": {"part": "snippet", "channelId": "UC123", "mine": True},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Selector combinations are rejected before endpoint execution.",
    },
    {
        "name": "authorization_sensitive_failure",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "selector": "mine"},
        "notes": "Owner-scoped lookup requires eligible OAuth authorization.",
    },
    {
        "name": "unsupported_higher_level_workflow",
        "arguments": {"part": "snippet", "channelId": "UC123", "expandVideos": True},
        "error": {"category": "invalid_request", "field": "expandVideos"},
        "notes": "Video expansion belongs to separate endpoint or Layer 3 workflows.",
    },
)


class ChannelSectionsListToolError(ValueError):
    """Represent a safe caller-facing ``channelSections_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channel-sections-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_channel_sections_transport(_execution) -> dict[str, Any]:
    """Return a safe empty channel-section collection for local execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped channel-section collection.
    """
    return {"items": []}


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channelSections_list``.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_channel_sections_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_channel_sections_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channelSections_list``.

    :return: Validated Layer 2 tool contract for ``channelSections_list``.
    """
    return YouTubeToolContract(
        tool_name=CHANNEL_SECTIONS_LIST_TOOL_NAME,
        upstream_resource="channelSections",
        upstream_method="list",
        operation_key="channelSections.list",
        description=CHANNEL_SECTIONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=CHANNEL_SECTIONS_LIST_QUOTA_COST,
        resource_family="channel_sections",
        input_contract=CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "prevPageToken", "pageInfo"],
            "caveatFields": ["hlDeprecated", "contentOwnerPartnerScoped", "paginationCompatibilityOnly"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "selector", "requestedParts", "caveats"),
            preserved_upstream_fields=("items", "nextPageToken", "prevPageToken", "pageInfo", "requestedParts"),
            disallowed_behavior=(
                "channel_search",
                "section_ranking",
                "layout_recommendation",
                "video_expansion",
                "playlist_item_expansion",
                "channel_section_mutation",
                "cross_endpoint_aggregation",
            ),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=CHANNEL_SECTIONS_LIST_USAGE_NOTES,
        caveats=CHANNEL_SECTIONS_LIST_CAVEATS,
    )


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active channel-section selectors from one request.

    :param arguments: Caller-supplied ``channelSections_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in CHANNEL_SECTIONS_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "mine":
            if value is True:
                active.append((selector, True))
        elif isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
    return active


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested channel-section part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _safe_caveat_context(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return safe caveat metadata that applies to one request.

    :param arguments: Caller-supplied ``channelSections_list`` arguments.
    :return: Safe caveat flags for public result surfaces.
    """
    caveats: dict[str, Any] = {}
    if "hl" in arguments:
        caveats["hlDeprecated"] = True
    if "onBehalfOfContentOwner" in arguments:
        caveats["contentOwnerPartnerScoped"] = True
    if "pageToken" in arguments or "maxResults" in arguments:
        caveats["paginationCompatibilityOnly"] = True
    return caveats


def map_channel_sections_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel-section response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw channel-section collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "channelSections.list",
        "quotaCost": CHANNEL_SECTIONS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
    }
    caveats = _safe_caveat_context(arguments)
    if caveats:
        result["caveats"] = caveats
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def validate_channel_sections_list_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> tuple[str, Any]:
    """Validate ``channelSections_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for owner-scoped lookup.
    :return: Selected selector name and safe value.
    :raises ChannelSectionsListToolError: If arguments are invalid or require missing authorization.
    """
    supported_fields = set(CHANNEL_SECTIONS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelSectionsListToolError(
                f"channelSections_list does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise ChannelSectionsListToolError(
            "channelSections_list requires part.",
            category="invalid_request",
            details={"field": "part"},
        )

    for field in ("hl", "onBehalfOfContentOwner"):
        if field in arguments and (not isinstance(arguments[field], str) or not arguments[field].strip()):
            raise ChannelSectionsListToolError(
                f"channelSections_list requires a non-empty {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if "onBehalfOfContentOwner" in arguments:
        raise ChannelSectionsListToolError(
            "channelSections_list does not support content-owner delegation in this slice.",
            category="invalid_request",
            details={"field": "onBehalfOfContentOwner", "partnerScoped": True},
        )

    provided_selectors: list[str] = []
    for selector in CHANNEL_SECTIONS_LIST_SELECTORS:
        if selector not in arguments:
            continue

        value = arguments[selector]
        if selector == "mine":
            if value is not True:
                raise ChannelSectionsListToolError(
                    "channelSections_list mine selector must be true when present.",
                    category="invalid_request",
                    details={"field": "mine"},
                )
        elif not isinstance(value, str) or not value.strip():
            raise ChannelSectionsListToolError(
                f"channelSections_list requires a non-empty {selector}.",
                category="invalid_request",
                details={"field": selector},
            )
        provided_selectors.append(selector)

    active = _active_selectors(arguments)
    if len(provided_selectors) != 1 or len(active) != 1:
        raise ChannelSectionsListToolError(
            "channelSections_list requires exactly one selector: channelId, id, or mine.",
            category="invalid_request",
            details={"field": "selector", "selectors": provided_selectors},
        )

    selector, value = active[0]
    if selector == "mine" and not oauth_token:
        raise ChannelSectionsListToolError(
            "mine requires eligible user authorization.",
            category="authentication_failed",
            details={"selector": selector},
        )
    return selector, value


def _auth_context_for_selector(
    selector: str,
    *,
    api_key: str | None,
    oauth_token: str | None,
) -> AuthContext:
    """Build the Layer 1 auth context for a channel-section selector.

    :param selector: Selected channel-section selector.
    :param api_key: API key value available for public selector access.
    :param oauth_token: OAuth token available for owner-scoped lookup.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises ChannelSectionsListToolError: If required credentials are unavailable.
    """
    if selector in {"channelId", "id"}:
        if not api_key:
            raise ChannelSectionsListToolError(
                f"{selector} requires public API-key access.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))

    if selector == "mine":
        if not oauth_token:
            raise ChannelSectionsListToolError(
                "mine requires eligible user authorization.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))

    raise ChannelSectionsListToolError(
        "channelSections_list requires a supported selector.",
        category="invalid_request",
        details={"field": "selector"},
    )


def _map_upstream_error(error: NormalizedUpstreamError) -> ChannelSectionsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channelSections_list`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "forbidden": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "rate_limited": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_unavailable": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    messages = {
        "invalid_request": "channelSections_list request was rejected by the upstream endpoint.",
        "authorization_failed": "channelSections_list was not authorized by the upstream endpoint.",
        "quota_exhausted": "channelSections_list quota was exhausted by the upstream endpoint.",
        "resource_not_found": "channelSections_list target was not found by the upstream endpoint.",
        "endpoint_unavailable": "channelSections_list upstream endpoint is temporarily unavailable.",
        "upstream_failure": "channelSections_list upstream execution failed.",
    }
    category = categories.get(error.category, "upstream_failure")
    return ChannelSectionsListToolError(
        messages[category],
        category=category,
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def build_channel_sections_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-section-access",
    oauth_token: str | None = None,
):
    """Build the concrete ``channelSections_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Callable dispatcher handler.
    """
    channel_sections_wrapper = wrapper or build_channel_sections_list_wrapper()
    channel_sections_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channelSections_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 channel-section collection result.
        :raises ChannelSectionsListToolError: If validation, authorization, or upstream execution fails.
        """
        selector, _value = validate_channel_sections_list_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            response = channel_sections_wrapper.call(
                channel_sections_executor,
                arguments=arguments,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as error:
            raise _map_upstream_error(error) from error
        except ValueError as error:
            raise ChannelSectionsListToolError(
                str(error),
                category="invalid_request",
                details={"selector": selector},
            ) from error
        except Exception as error:
            raise ChannelSectionsListToolError(
                "channelSections_list upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channel_sections_list_result(response, arguments)

    return handler


def build_channel_sections_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-section-access",
    oauth_token: str | None = None,
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channelSections_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channel_sections_list_contract()
    return {
        "name": CHANNEL_SECTIONS_LIST_TOOL_NAME,
        "description": CHANNEL_SECTIONS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNEL_SECTIONS_LIST_INPUT_SCHEMA,
        "handler": build_channel_sections_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "CHANNEL_SECTIONS_LIST_CAVEATS",
    "CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES",
    "CHANNEL_SECTIONS_LIST_DESCRIPTION",
    "CHANNEL_SECTIONS_LIST_INPUT_SCHEMA",
    "CHANNEL_SECTIONS_LIST_QUOTA_COST",
    "CHANNEL_SECTIONS_LIST_SELECTORS",
    "CHANNEL_SECTIONS_LIST_TOOL_NAME",
    "CHANNEL_SECTIONS_LIST_USAGE_NOTES",
    "ChannelSectionsListToolError",
    "build_channel_sections_list_contract",
    "build_channel_sections_list_handler",
    "build_channel_sections_list_tool_descriptor",
    "map_channel_sections_list_result",
    "validate_channel_sections_list_arguments",
]
