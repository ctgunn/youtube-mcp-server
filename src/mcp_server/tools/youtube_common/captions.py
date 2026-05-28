"""Concrete Layer 2 tool support for the YouTube ``captions`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.captions import build_captions_list_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


CAPTIONS_LIST_TOOL_NAME = "captions_list"
CAPTIONS_LIST_QUOTA_COST = 50

CAPTIONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "videoId"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "videoId": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": 50},
        "pageToken": {"type": "string", "minLength": 1},
        "onBehalfOfContentOwner": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

CAPTIONS_LIST_DESCRIPTION = (
    "List YouTube caption tracks. Endpoint: captions.list. "
    "Quota cost: 50. Auth: oauth_required."
)
CAPTIONS_LIST_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Use videoId to list caption tracks for an accessible video.",
    "Quota cost: 50. id may narrow the lookup but does not replace the required videoId.",
    "Quota cost: 50. onBehalfOfContentOwner is optional delegation context and still requires eligible OAuth authorization.",
)
CAPTIONS_LIST_CAVEATS = (
    "Caption listing requires eligible OAuth authorization for the target video's captions.",
    "Delegated content-owner context is optional and permission-sensitive.",
)


class CaptionsListToolError(ValueError):
    """Represent a safe caller-facing ``captions_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe captions-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_captions_transport(_execution) -> dict[str, Any]:
    """Return a safe empty caption collection for local default execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped caption collection.
    """
    return {"items": []}


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``captions_list``.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_captions_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_captions_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``captions_list``.

    :return: Validated Layer 2 tool contract for ``captions_list``.
    """
    return YouTubeToolContract(
        tool_name=CAPTIONS_LIST_TOOL_NAME,
        upstream_resource="captions",
        upstream_method="list",
        operation_key="captions.list",
        description=CAPTIONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CAPTIONS_LIST_QUOTA_COST,
        resource_family="captions",
        input_contract=CAPTIONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "prevPageToken", "pageInfo"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "lookup", "delegation", "requestedParts"),
            preserved_upstream_fields=("items", "nextPageToken", "prevPageToken", "pageInfo", "requestedParts"),
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
        usage_notes=CAPTIONS_LIST_USAGE_NOTES,
        caveats=CAPTIONS_LIST_CAVEATS,
    )


def _clean_text(arguments: dict[str, Any], field_name: str) -> str | None:
    """Return stripped text for a field when present.

    :param arguments: Caller-supplied tool arguments.
    :param field_name: Field to normalize.
    :return: Stripped text or ``None`` when absent.
    """
    value = arguments.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def validate_captions_list_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> dict[str, str]:
    """Validate ``captions_list`` arguments and return the lookup context.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for caption access.
    :return: Safe lookup context for result mapping.
    :raises CaptionsListToolError: If arguments are invalid or require missing authorization.
    """
    if not isinstance(arguments.get("part"), str) or not arguments.get("part", "").strip():
        raise CaptionsListToolError(
            "captions_list requires part.",
            category="invalid_request",
            details={"field": "part"},
        )

    video_id = _clean_text(arguments, "videoId")
    if not video_id:
        raise CaptionsListToolError(
            "captions_list requires videoId.",
            category="invalid_request",
            details={"field": "videoId"},
        )

    max_results = arguments.get("maxResults")
    if max_results is not None and (not isinstance(max_results, int) or max_results < 0 or max_results > 50):
        raise CaptionsListToolError(
            "maxResults must be between 0 and 50.",
            category="invalid_request",
            details={"field": "maxResults"},
        )

    if arguments.get("onBehalfOfContentOwner") is not None and not oauth_token:
        raise CaptionsListToolError(
            "Delegated caption listing requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"field": "onBehalfOfContentOwner"},
        )

    if not oauth_token:
        raise CaptionsListToolError(
            "captions_list requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"operation": "captions.list"},
        )

    lookup = {"videoId": video_id}
    caption_id = _clean_text(arguments, "id")
    if caption_id:
        lookup["id"] = caption_id
    return lookup


def _auth_context(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for caption listing.

    :param oauth_token: OAuth token available for caption listing.
    :return: OAuth-required auth context suitable for the Layer 1 wrapper.
    :raises CaptionsListToolError: If required credentials are unavailable.
    """
    if not oauth_token:
        raise CaptionsListToolError(
            "captions_list requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"operation": "captions.list"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _lookup_summary(arguments: dict[str, Any]) -> dict[str, str]:
    """Return a safe lookup summary for one caption-list request.

    :param arguments: Original tool arguments.
    :return: Safe lookup fields for the public result.
    """
    lookup = {"videoId": _clean_text(arguments, "videoId") or ""}
    caption_id = _clean_text(arguments, "id")
    if caption_id:
        lookup["id"] = caption_id
    return lookup


def map_captions_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 caption response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw caption collection with light MCP clarity fields.
    """
    result: dict[str, Any] = {
        "endpoint": "captions.list",
        "quotaCost": CAPTIONS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "lookup": _lookup_summary(arguments),
    }
    if _clean_text(arguments, "onBehalfOfContentOwner"):
        result["delegation"] = {"onBehalfOfContentOwner": True}
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> CaptionsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``captions_list`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    return CaptionsListToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def build_captions_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "eligible-caption-access",
):
    """Build the concrete ``captions_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for caption listing.
    :return: Callable dispatcher handler.
    """
    captions_wrapper = wrapper or build_captions_list_wrapper()
    captions_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``captions_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 caption collection result.
        :raises CaptionsListToolError: If validation, authorization, or upstream execution fails.
        """
        validate_captions_list_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context(oauth_token=oauth_token)
        try:
            response = captions_wrapper.call(captions_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_upstream_error(error) from error
        except ValueError as error:
            raise CaptionsListToolError(
                str(error),
                category="invalid_request",
                details={"operation": "captions.list"},
            ) from error
        return map_captions_list_result(response, arguments)

    return handler


def build_captions_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "eligible-caption-access",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``captions_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for caption listing.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_captions_list_contract()
    return {
        "name": CAPTIONS_LIST_TOOL_NAME,
        "description": CAPTIONS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CAPTIONS_LIST_INPUT_SCHEMA,
        "handler": build_captions_list_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "CAPTIONS_LIST_INPUT_SCHEMA",
    "CAPTIONS_LIST_QUOTA_COST",
    "CAPTIONS_LIST_TOOL_NAME",
    "CaptionsListToolError",
    "build_captions_list_contract",
    "build_captions_list_handler",
    "build_captions_list_tool_descriptor",
    "map_captions_list_result",
    "validate_captions_list_arguments",
]
