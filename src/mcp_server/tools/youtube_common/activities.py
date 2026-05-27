"""Concrete Layer 2 tool support for the YouTube ``activities`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.activities import build_activities_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


ACTIVITIES_LIST_TOOL_NAME = "activities_list"
ACTIVITIES_LIST_QUOTA_COST = 1
ACTIVITIES_LIST_SELECTORS = ("channelId", "mine", "home")

ACTIVITIES_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "channelId": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "home": {"type": "boolean"},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": 50},
        "pageToken": {"type": "string", "minLength": 1},
        "publishedAfter": {"type": "string", "minLength": 1},
        "publishedBefore": {"type": "string", "minLength": 1},
        "regionCode": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in ACTIVITIES_LIST_SELECTORS],
    "additionalProperties": False,
}

ACTIVITIES_LIST_DESCRIPTION = (
    "List YouTube activities. Endpoint: activities.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)
ACTIVITIES_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use channelId for public channel activity.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for the authenticated user's activity.",
    "Quota cost: 1. home requires eligible OAuth authorization and is deprecated upstream.",
)
ACTIVITIES_LIST_CAVEATS = (
    "The home selector is deprecated upstream and requires eligible user authorization.",
    "Exactly one selector is required: channelId, mine, or home.",
)


class ActivitiesListToolError(ValueError):
    """Represent a safe caller-facing ``activities_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe activities-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_activities_transport(_execution) -> dict[str, Any]:
    """Return a safe empty activity collection for local default execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped activity collection.
    """
    return {"items": []}


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``activities_list``.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_activities_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_activities_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``activities_list``.

    :return: Validated Layer 2 tool contract for ``activities_list``.
    """
    return YouTubeToolContract(
        tool_name=ACTIVITIES_LIST_TOOL_NAME,
        upstream_resource="activities",
        upstream_method="list",
        operation_key="activities.list",
        description=ACTIVITIES_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=ACTIVITIES_LIST_QUOTA_COST,
        resource_family="activities",
        input_contract=ACTIVITIES_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "prevPageToken", "pageInfo"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "selector", "requestedParts"),
            preserved_upstream_fields=("items", "nextPageToken", "prevPageToken", "pageInfo", "requestedParts"),
        ).to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "resource_not_found",
            "deprecated_endpoint",
            "endpoint_unavailable",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=ACTIVITIES_LIST_USAGE_NOTES,
        caveats=ACTIVITIES_LIST_CAVEATS,
    )


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active activity selectors from one request.

    :param arguments: Caller-supplied ``activities_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in ACTIVITIES_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "channelId":
            if isinstance(value, str) and value.strip():
                active.append((selector, value.strip()))
        elif value is True:
            active.append((selector, True))
    return active


def validate_activities_list_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> tuple[str, Any]:
    """Validate ``activities_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for private selectors.
    :return: Selected selector name and safe value.
    :raises ActivitiesListToolError: If arguments are invalid or require missing authorization.
    """
    if not isinstance(arguments.get("part"), str) or not arguments.get("part", "").strip():
        raise ActivitiesListToolError(
            "activities_list requires part.",
            category="invalid_request",
            details={"field": "part"},
        )

    max_results = arguments.get("maxResults")
    if max_results is not None and (not isinstance(max_results, int) or max_results < 0 or max_results > 50):
        raise ActivitiesListToolError(
            "maxResults must be between 0 and 50.",
            category="invalid_request",
            details={"field": "maxResults"},
        )

    active = _active_selectors(arguments)
    if len(active) != 1:
        raise ActivitiesListToolError(
            "activities_list requires exactly one selector: channelId, mine, or home.",
            category="invalid_request",
            details={"selectors": [name for name, _value in active]},
        )

    selector, value = active[0]
    if selector in {"mine", "home"} and not oauth_token:
        raise ActivitiesListToolError(
            f"{selector} requires eligible user authorization.",
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
    """Build the Layer 1 auth context for an activity selector.

    :param selector: Selected activity selector.
    :param api_key: API key value available for public-channel access.
    :param oauth_token: OAuth token available for authorized-user selectors.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises ActivitiesListToolError: If required credentials are unavailable.
    """
    if selector == "channelId":
        if not api_key:
            raise ActivitiesListToolError(
                "channelId requires public API-key access.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))

    if not oauth_token:
        raise ActivitiesListToolError(
            f"{selector} requires eligible user authorization.",
            category="authentication_failed",
            details={"selector": selector},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def map_activities_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 activity response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw activity collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "activities.list",
        "quotaCost": ACTIVITIES_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
    }
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> ActivitiesListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``activities_list`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    return ActivitiesListToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def build_activities_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-access",
    oauth_token: str | None = None,
):
    """Build the concrete ``activities_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public channel requests.
    :param oauth_token: OAuth token availability for authorized selectors.
    :return: Callable dispatcher handler.
    """
    activities_wrapper = wrapper or build_activities_list_wrapper()
    activities_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``activities_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 activity collection result.
        :raises ActivitiesListToolError: If validation, authorization, or upstream execution fails.
        """
        selector, _value = validate_activities_list_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            response = activities_wrapper.call(activities_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_upstream_error(error) from error
        except ValueError as error:
            raise ActivitiesListToolError(
                str(error),
                category="invalid_request",
                details={"selector": selector},
            ) from error
        return map_activities_list_result(response, arguments)

    return handler


def build_activities_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-access",
    oauth_token: str | None = None,
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``activities_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public channel requests.
    :param oauth_token: OAuth token availability for authorized selectors.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_activities_list_contract()
    return {
        "name": ACTIVITIES_LIST_TOOL_NAME,
        "description": ACTIVITIES_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": ACTIVITIES_LIST_INPUT_SCHEMA,
        "handler": build_activities_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "ACTIVITIES_LIST_INPUT_SCHEMA",
    "ACTIVITIES_LIST_QUOTA_COST",
    "ACTIVITIES_LIST_SELECTORS",
    "ACTIVITIES_LIST_TOOL_NAME",
    "ActivitiesListToolError",
    "build_activities_list_contract",
    "build_activities_list_handler",
    "build_activities_list_tool_descriptor",
    "map_activities_list_result",
    "validate_activities_list_arguments",
]
