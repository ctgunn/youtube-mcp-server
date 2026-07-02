"""Concrete Layer 2 tool support for the YouTube ``membershipsLevels`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.memberships_levels import build_memberships_levels_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


MEMBERSHIPS_LEVELS_LIST_TOOL_NAME = "membershipsLevels_list"
MEMBERSHIPS_LEVELS_LIST_QUOTA_COST = 1
MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS = ("snippet",)

MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "enum": list(MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS), "minLength": 1},
    },
    "additionalProperties": False,
}

MEMBERSHIPS_LEVELS_LIST_DESCRIPTION = (
    "List channel membership levels for the authenticated owner. "
    "Endpoint: membershipsLevels.list. Quota cost: 1. Auth: oauth_required."
)

MEMBERSHIPS_LEVELS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: oauth_required. Provide part=snippet for membership-level retrieval.",
    "Quota cost: 1. The caller must be authorized as the owner for the channel-membership surface.",
    "Quota cost: 1. Membership-level retrieval is a direct endpoint-backed list, not a member listing workflow.",
)

MEMBERSHIPS_LEVELS_LIST_CAVEATS = (
    "This tool exposes owner-scoped channel-membership level records only; subscriber lookup is out of scope.",
    "Channel member listing, membership administration, analytics, ranking, summarization, and enrichment are out of scope.",
    "Filters, paging controls, delegation, and cross-channel access modifiers are not supported by this Layer 2 slice.",
)

MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES = (
    {
        "name": "membership_levels_listing",
        "description": "Quota cost: 1. List membership levels for the authenticated owner.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "membershipsLevels.list", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. An empty membership-level collection remains a successful list result.",
        "arguments": {"part": "snippet"},
        "result": {"endpoint": "membershipsLevels.list", "items": []},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required part=snippet value.",
        "arguments": {},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Reject part values outside snippet.",
        "arguments": {"part": "id"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_option",
        "description": "Reject unsupported filters, paging controls, delegation, or member-list options.",
        "arguments": {"part": "snippet", "pageToken": "NEXT_PAGE"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_or_membership_eligibility_failure",
        "description": "Map owner access or channel-membership eligibility failures to authorization errors.",
        "arguments": {"part": "snippet"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "out_of_scope_member_or_analytics_request",
        "description": "Channel member listing, subscriber lookup, and analytics requests belong outside membershipsLevels_list.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
)


class MembershipsLevelsListToolError(ValueError):
    """Represent a safe caller-facing ``membershipsLevels_list`` failure.

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
    """Normalize a comma-delimited membership-level part selection.

    :param parts: Caller-provided part selection.
    :return: Visible part names in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def validate_memberships_levels_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``membershipsLevels_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises MembershipsLevelsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise MembershipsLevelsListToolError("membershipsLevels_list arguments must be an object")

    allowed = {"part"}
    for field in arguments:
        if field not in allowed:
            raise MembershipsLevelsListToolError(
                f"unsupported field for membershipsLevels_list: {field}",
                details={"field": field},
            )

    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise MembershipsLevelsListToolError(
            "membershipsLevels_list requires part=snippet",
            details={"field": "part"},
        )
    parts = _split_parts(part)
    if parts != list(MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS):
        raise MembershipsLevelsListToolError(
            "membershipsLevels_list supports only part=snippet",
            details={"field": "part", "allowed": list(MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS)},
        )

    return {"part": "snippet"}


def map_memberships_levels_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream membership-level payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 membership-level list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_memberships_levels_list_arguments(arguments)
    result = {
        "endpoint": "membershipsLevels.list",
        "quotaCost": MEMBERSHIPS_LEVELS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "auth": {"mode": "oauth_required", "ownerScoped": True},
        "items": payload.get("items", []),
    }
    for field in ("kind", "etag"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_memberships_levels_list_upstream_error(error: NormalizedUpstreamError) -> MembershipsLevelsListToolError:
    """Map a normalized upstream failure to a safe ``membershipsLevels_list`` error.

    :param error: Normalized Layer 1 or upstream failure.
    :return: Safe tool error with shared category and sanitized details.
    """
    category_map = {
        "invalid_request": "invalid_request",
        "authentication": "authentication_failed",
        "auth": "authorization_failed",
        "authorization": "authorization_failed",
        "permission": "authorization_failed",
        "forbidden": "authorization_failed",
        "policy_restricted": "authorization_failed",
        "rate_limit": "quota_exhausted",
        "quota": "quota_exhausted",
        "not_found": "resource_not_found",
        "resource_not_found": "resource_not_found",
        "unavailable": "endpoint_unavailable",
        "deprecated": "endpoint_unavailable",
    }
    category = category_map.get(error.category, "upstream_failure")
    return MembershipsLevelsListToolError(str(error), category=category, details=error.details)


def _memberships_levels_list_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required owner-scoped auth context for ``membershipsLevels_list``.

    :param oauth_token: OAuth token used for owner-scoped membership-level access.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises MembershipsLevelsListToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise MembershipsLevelsListToolError(
            "membershipsLevels_list requires OAuth owner authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_memberships_levels_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``membershipsLevels_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "auth",
            "items",
            "kind",
            "etag",
        ),
        preserved_upstream_fields=("kind", "etag", "items"),
        disallowed_behavior=(
            "member_listing",
            "subscriber_lookup",
            "membership_management",
            "analytics",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=MEMBERSHIPS_LEVELS_LIST_TOOL_NAME,
        upstream_resource="membershipsLevels",
        upstream_method="list",
        operation_key="membershipsLevels.list",
        description=MEMBERSHIPS_LEVELS_LIST_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=MEMBERSHIPS_LEVELS_LIST_QUOTA_COST,
        resource_family="memberships_levels",
        input_contract=MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "requestedParts": list(MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS),
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
        usage_notes=MEMBERSHIPS_LEVELS_LIST_USAGE_NOTES,
        caveats=MEMBERSHIPS_LEVELS_LIST_CAVEATS,
    )


def _default_memberships_levels_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default membership-level calls.

    :return: Integration executor returning representative membership-level data.
    """

    def transport(execution):
        """Return a representative membership-level list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#membershipsLevelListResponse",
            "etag": "etag-membership-levels",
            "items": [
                {
                    "kind": "youtube#membershipsLevel",
                    "id": "level-123",
                    "snippet": {
                        "creatorChannelId": "channel-123",
                        "levelDetails": {"displayName": "Example Level"},
                    },
                }
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_memberships_levels_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``membershipsLevels_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps membership-level requests.
    """
    selected_wrapper = wrapper or build_memberships_levels_list_wrapper()
    selected_executor = executor or _default_memberships_levels_list_executor()
    auth_context = _memberships_levels_list_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``membershipsLevels_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 membership-level list result.
        :raises MembershipsLevelsListToolError: If validation or execution fails.
        """
        normalized = validate_memberships_levels_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_memberships_levels_list_upstream_error(exc) from exc
        return map_memberships_levels_list_result(payload, normalized)

    return handler


def build_memberships_levels_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``membershipsLevels_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_memberships_levels_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES)
    return {
        "name": MEMBERSHIPS_LEVELS_LIST_TOOL_NAME,
        "description": MEMBERSHIPS_LEVELS_LIST_DESCRIPTION,
        "inputSchema": MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA,
        "handler": build_memberships_levels_list_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES",
    "MEMBERSHIPS_LEVELS_LIST_CAVEATS",
    "MEMBERSHIPS_LEVELS_LIST_DESCRIPTION",
    "MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA",
    "MEMBERSHIPS_LEVELS_LIST_QUOTA_COST",
    "MEMBERSHIPS_LEVELS_LIST_SUPPORTED_PARTS",
    "MEMBERSHIPS_LEVELS_LIST_TOOL_NAME",
    "MEMBERSHIPS_LEVELS_LIST_USAGE_NOTES",
    "MembershipsLevelsListToolError",
    "build_memberships_levels_list_contract",
    "build_memberships_levels_list_handler",
    "build_memberships_levels_list_tool_descriptor",
    "map_memberships_levels_list_result",
    "validate_memberships_levels_list_arguments",
]
