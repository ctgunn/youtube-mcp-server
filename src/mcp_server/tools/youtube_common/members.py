"""Concrete Layer 2 tool support for the YouTube ``members`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.members import build_members_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


MEMBERS_LIST_TOOL_NAME = "members_list"
MEMBERS_LIST_QUOTA_COST = 2
MEMBERS_LIST_SUPPORTED_PARTS = ("snippet",)
MEMBERS_LIST_SUPPORTED_MODES = ("all_current", "updates")

MEMBERS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "mode"],
    "properties": {
        "part": {"type": "string", "enum": list(MEMBERS_LIST_SUPPORTED_PARTS), "minLength": 1},
        "mode": {"type": "string", "enum": list(MEMBERS_LIST_SUPPORTED_MODES), "minLength": 1},
        "pageToken": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": 1000},
    },
    "additionalProperties": False,
}

MEMBERS_LIST_DESCRIPTION = (
    "List channel members for the authenticated owner. Endpoint: members.list. "
    "Quota cost: 2. Auth: oauth_required."
)

MEMBERS_LIST_USAGE_NOTES = (
    "Quota cost: 2. Auth: oauth_required. Provide part=snippet and mode=all_current or mode=updates.",
    "Quota cost: 2. The caller must be authorized as the owner for the channel-membership surface.",
    "Quota cost: 2. pageToken and maxResults are optional paging controls for membership-list traversal.",
)

MEMBERS_LIST_CAVEATS = (
    "This tool exposes owner-scoped channel-membership records only; subscriber lookup is out of scope.",
    "membership-level filtering, management actions, analytics, ranking, summarization, and enrichment are out of scope.",
    "Delegation and cross-channel access modifiers are not supported by this Layer 2 slice.",
)

MEMBERS_LIST_CALLER_EXAMPLES = (
    {
        "name": "current_members_listing",
        "description": "Quota cost: 2. List current channel members for the authenticated owner.",
        "arguments": {"part": "snippet", "mode": "all_current"},
        "result": {"endpoint": "members.list", "mode": "all_current", "itemsPath": "items"},
        "quotaCost": 2,
    },
    {
        "name": "membership_updates_listing",
        "description": "Quota cost: 2. List membership updates for the authenticated owner.",
        "arguments": {"part": "snippet", "mode": "updates"},
        "result": {"endpoint": "members.list", "mode": "updates", "itemsPath": "items"},
        "quotaCost": 2,
    },
    {
        "name": "paged_members_listing",
        "description": "Quota cost: 2. Continue a member-list traversal with paging controls.",
        "arguments": {"part": "snippet", "mode": "all_current", "pageToken": "NEXT_PAGE", "maxResults": 25},
        "quotaCost": 2,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 2. An empty member collection remains a successful list result.",
        "arguments": {"part": "snippet", "mode": "updates"},
        "result": {"endpoint": "members.list", "mode": "updates", "items": []},
        "quotaCost": 2,
    },
    {
        "name": "missing_part",
        "description": "Reject requests missing the required part=snippet value.",
        "arguments": {"mode": "all_current"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_mode",
        "description": "Reject requests missing the required membership mode.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_mode",
        "description": "Reject membership modes outside all_current and updates.",
        "arguments": {"part": "snippet", "mode": "expired"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_max_results",
        "description": "Reject maxResults values outside the documented member-list range.",
        "arguments": {"part": "snippet", "mode": "all_current", "maxResults": 1001},
        "errorCategory": "invalid_request",
    },
    {
        "name": "unsupported_option",
        "description": "Reject unsupported delegation, subscriber lookup, or membership-level filters.",
        "arguments": {"part": "snippet", "mode": "all_current", "hasAccessToLevel": "level-123"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_or_membership_eligibility_failure",
        "description": "Map owner access or channel-membership eligibility failures to authorization errors.",
        "arguments": {"part": "snippet", "mode": "all_current"},
        "errorCategory": "authorization_failed",
    },
    {
        "name": "out_of_scope_subscriber_or_analytics_request",
        "description": "Direct subscriber lookup and analytics requests belong outside members_list.",
        "arguments": {"part": "snippet", "mode": "all_current"},
        "errorCategory": "invalid_request",
    },
)


class MembersListToolError(ValueError):
    """Represent a safe caller-facing ``members_list`` failure.

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


def validate_members_list_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Validate a ``members_list`` request and return normalized arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized caller arguments for execution and result mapping.
    :raises MembersListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise MembersListToolError("members_list arguments must be an object")

    allowed = {"part", "mode", "pageToken", "maxResults"}
    for field in arguments:
        if field not in allowed:
            raise MembersListToolError(
                f"unsupported field for members_list: {field}",
                details={"field": field},
            )

    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise MembersListToolError("members_list requires part=snippet", details={"field": "part"})
    parts = _split_parts(part)
    if parts != list(MEMBERS_LIST_SUPPORTED_PARTS):
        raise MembersListToolError(
            "members_list supports only part=snippet",
            details={"field": "part", "allowed": list(MEMBERS_LIST_SUPPORTED_PARTS)},
        )

    mode = arguments.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        raise MembersListToolError("members_list requires mode", details={"field": "mode"})
    normalized_mode = mode.strip()
    if normalized_mode not in MEMBERS_LIST_SUPPORTED_MODES:
        raise MembersListToolError(
            "members_list mode must be all_current or updates",
            details={"field": "mode", "allowed": list(MEMBERS_LIST_SUPPORTED_MODES)},
        )

    normalized: dict[str, Any] = {"part": "snippet", "mode": normalized_mode}
    page_token = arguments.get("pageToken")
    if page_token is not None:
        if not isinstance(page_token, str) or not page_token.strip():
            raise MembersListToolError("pageToken must be a non-empty string", details={"field": "pageToken"})
        normalized["pageToken"] = page_token.strip()

    max_results = arguments.get("maxResults")
    if max_results is not None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise MembersListToolError("maxResults must be an integer", details={"field": "maxResults"})
        if max_results < 0 or max_results > 1000:
            raise MembersListToolError(
                "maxResults must be between 0 and 1000",
                details={"field": "maxResults", "minimum": 0, "maximum": 1000},
            )
        normalized["maxResults"] = max_results

    return normalized


def map_members_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream member-list payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 member-list payload.
    :param arguments: Validated caller arguments used for the request.
    :return: Near-raw result with safe operation context.
    """
    normalized = validate_members_list_arguments(arguments)
    result = {
        "endpoint": "members.list",
        "quotaCost": MEMBERS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "mode": normalized["mode"],
        "auth": {"mode": "oauth_required", "ownerScoped": True},
        "items": payload.get("items", []),
    }
    page_request = {
        field: normalized[field]
        for field in ("pageToken", "maxResults")
        if field in normalized
    }
    if page_request:
        result["pageRequest"] = page_request
    for field in ("kind", "etag", "nextPageToken", "prevPageToken", "pageInfo"):
        if field in payload:
            result[field] = payload[field]
    return result


def _map_members_list_upstream_error(error: NormalizedUpstreamError) -> MembersListToolError:
    """Map a normalized upstream failure to a safe ``members_list`` error.

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
    return MembersListToolError(str(error), category=category, details=error.details)


def _members_list_auth_context(oauth_token: str | None) -> AuthContext:
    """Build the OAuth-required owner-scoped auth context for ``members_list``.

    :param oauth_token: OAuth token used for owner-scoped member-list access.
    :return: Layer 1 auth context configured for OAuth-required execution.
    :raises MembersListToolError: If no OAuth token is available.
    """
    if not isinstance(oauth_token, str) or not oauth_token.strip():
        raise MembersListToolError(
            "members_list requires OAuth owner authorization",
            category="authentication_failed",
            details={"field": "auth"},
        )
    return AuthContext(
        mode=Layer1AuthMode.OAUTH_REQUIRED,
        credentials=CredentialBundle(oauth_token=oauth_token.strip()),
    )


def build_members_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``members_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "mode",
            "auth",
            "pageRequest",
            "items",
            "kind",
            "etag",
            "nextPageToken",
            "prevPageToken",
            "pageInfo",
        ),
        preserved_upstream_fields=("kind", "etag", "items", "nextPageToken", "prevPageToken", "pageInfo"),
        disallowed_behavior=(
            "subscriber_lookup",
            "membership_level_filtering",
            "membership_management",
            "analytics",
            "ranking",
            "summarization",
            "enrichment",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=MEMBERS_LIST_TOOL_NAME,
        upstream_resource="members",
        upstream_method="list",
        operation_key="members.list",
        description=MEMBERS_LIST_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=MEMBERS_LIST_QUOTA_COST,
        resource_family="members",
        input_contract=MEMBERS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["pageToken", "maxResults", "nextPageToken", "pageInfo"],
            "requestedParts": list(MEMBERS_LIST_SUPPORTED_PARTS),
            "modeFields": ["mode"],
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
        usage_notes=MEMBERS_LIST_USAGE_NOTES,
        caveats=MEMBERS_LIST_CAVEATS,
    )


def _default_members_list_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default member-list calls.

    :return: Integration executor returning representative membership data.
    """
    def transport(execution):
        """Return a representative member-list response.

        :param execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#memberListResponse",
            "etag": "etag-members",
            "items": [
                {
                    "kind": "youtube#member",
                    "id": "member-123",
                    "snippet": {
                        "memberDetails": {"displayName": "Example Member"},
                        "membershipsDetails": {"highestAccessibleLevel": "level-123"},
                    },
                }
            ],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_members_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
):
    """Build the callable handler for ``members_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used to construct safe OAuth auth context.
    :return: Callable that validates, executes, and maps member-list requests.
    """
    selected_wrapper = wrapper or build_members_list_wrapper()
    selected_executor = executor or _default_members_list_executor()
    auth_context = _members_list_auth_context(oauth_token)

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``members_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 member-list result.
        :raises MembersListToolError: If validation or execution fails.
        """
        normalized = validate_members_list_arguments(arguments)
        try:
            payload = selected_wrapper.call(
                selected_executor,
                arguments=normalized,
                auth_context=auth_context,
            )
        except NormalizedUpstreamError as exc:
            raise _map_members_list_upstream_error(exc) from exc
        return map_members_list_result(payload, normalized)

    return handler


def build_members_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    oauth_token: str | None = "local-oauth-token",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``members_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_members_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(MEMBERS_LIST_CALLER_EXAMPLES)
    return {
        "name": MEMBERS_LIST_TOOL_NAME,
        "description": MEMBERS_LIST_DESCRIPTION,
        "inputSchema": MEMBERS_LIST_INPUT_SCHEMA,
        "handler": build_members_list_handler(wrapper=wrapper, executor=executor, oauth_token=oauth_token),
        "metadata": metadata,
    }


__all__ = [
    "MEMBERS_LIST_CALLER_EXAMPLES",
    "MEMBERS_LIST_CAVEATS",
    "MEMBERS_LIST_DESCRIPTION",
    "MEMBERS_LIST_INPUT_SCHEMA",
    "MEMBERS_LIST_QUOTA_COST",
    "MEMBERS_LIST_SUPPORTED_MODES",
    "MEMBERS_LIST_SUPPORTED_PARTS",
    "MEMBERS_LIST_TOOL_NAME",
    "MEMBERS_LIST_USAGE_NOTES",
    "MembersListToolError",
    "build_members_list_contract",
    "build_members_list_handler",
    "build_members_list_tool_descriptor",
    "map_members_list_result",
    "validate_members_list_arguments",
]
