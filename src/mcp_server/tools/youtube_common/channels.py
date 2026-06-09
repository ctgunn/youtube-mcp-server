"""Concrete Layer 2 tool support for the YouTube ``channels`` resource."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.channels import build_channels_list_wrapper, build_channels_update_wrapper
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind


CHANNELS_LIST_TOOL_NAME = "channels_list"
CHANNELS_LIST_QUOTA_COST = 1
CHANNELS_LIST_SELECTORS = ("id", "mine", "forHandle", "forUsername")
CHANNELS_UPDATE_TOOL_NAME = "channels_update"
CHANNELS_UPDATE_QUOTA_COST = 50
CHANNELS_UPDATE_SUPPORTED_PARTS = ("brandingSettings", "localizations")

CHANNELS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "id": {"type": "string", "minLength": 1},
        "mine": {"type": "boolean"},
        "forHandle": {"type": "string", "minLength": 1},
        "forUsername": {"type": "string", "minLength": 1},
        "maxResults": {"type": "integer", "minimum": 0, "maximum": 50},
        "pageToken": {"type": "string", "minLength": 1},
        "hl": {"type": "string", "minLength": 1},
    },
    "oneOf": [{"required": [selector]} for selector in CHANNELS_LIST_SELECTORS],
    "additionalProperties": False,
}

CHANNELS_UPDATE_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "body"],
    "properties": {
        "part": {
            "type": "string",
            "enum": list(CHANNELS_UPDATE_SUPPORTED_PARTS),
            "description": "Exactly one writable part: brandingSettings or localizations.",
        },
        "body": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "brandingSettings": {"type": "object"},
                "localizations": {"type": "object"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

CHANNELS_LIST_DESCRIPTION = (
    "List YouTube channels. Endpoint: channels.list. "
    "Quota cost: 1. Auth: mixed/conditional."
)
CHANNELS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Use id, forHandle, or forUsername for public channel lookup.",
    "Quota cost: 1. Use mine with eligible OAuth authorization for the authenticated user's channel.",
    "Quota cost: 1. Pagination preserves nextPageToken, prevPageToken, and pageInfo when returned.",
    "Quota cost: 1. Valid lookups that match no channels return a successful empty item collection.",
)
CHANNELS_LIST_CAVEATS = (
    "Exactly one selector is required: id, mine, forHandle, or forUsername.",
    "forUsername is username-style lookup and may not apply to every modern channel identity.",
    "This low-level tool does not search, rank, enrich, expand videos or playlists, or update channel metadata.",
)
CHANNELS_LIST_CALLER_EXAMPLES = (
    {
        "name": "id_lookup",
        "arguments": {"part": "snippet,contentDetails", "id": "UC123"},
        "result": {
            "endpoint": "channels.list",
            "quotaCost": 1,
            "selector": {"name": "id"},
            "requestedParts": ["snippet", "contentDetails"],
            "items": [{"id": "UC123"}],
        },
        "notes": "Looks up one or more channels by channel ID.",
    },
    {
        "name": "handle_lookup",
        "arguments": {"part": "snippet", "forHandle": "@Example"},
        "result": {"endpoint": "channels.list", "quotaCost": 1, "selector": {"name": "forHandle"}},
        "notes": "Looks up a channel by YouTube handle.",
    },
    {
        "name": "username_lookup",
        "arguments": {"part": "snippet", "forUsername": "legacy-user"},
        "result": {"endpoint": "channels.list", "quotaCost": 1, "selector": {"name": "forUsername"}},
        "notes": "Uses username-style lookup where the upstream endpoint supports it.",
    },
    {
        "name": "authorized_mine_lookup",
        "arguments": {"part": "snippet", "mine": True},
        "result": {"endpoint": "channels.list", "quotaCost": 1, "selector": {"name": "mine"}},
        "notes": "Requires eligible OAuth authorization for the authenticated user's channel.",
    },
    {
        "name": "paginated_continuation",
        "arguments": {"part": "snippet", "id": "UC123", "pageToken": "NEXT"},
        "result": {"endpoint": "channels.list", "nextPageToken": "NEXT_2", "quotaCost": 1},
        "notes": "Preserves pagination tokens returned by the endpoint.",
    },
    {
        "name": "empty_result",
        "arguments": {"part": "snippet", "forHandle": "@missing"},
        "result": {"endpoint": "channels.list", "quotaCost": 1, "items": []},
        "notes": "A valid no-match lookup is a successful empty collection.",
    },
    {
        "name": "missing_selector",
        "arguments": {"part": "snippet"},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Exactly one selector is required.",
    },
    {
        "name": "conflicting_selectors",
        "arguments": {"part": "snippet", "id": "UC123", "mine": True},
        "error": {"category": "invalid_request", "field": "selector"},
        "notes": "Selector combinations are rejected before endpoint execution.",
    },
    {
        "name": "authorization_sensitive_failure",
        "arguments": {"part": "snippet", "mine": True},
        "error": {"category": "authentication_failed", "selector": "mine"},
        "notes": "Owner-scoped lookup requires eligible OAuth authorization.",
    },
)

CHANNELS_UPDATE_DESCRIPTION = (
    "Update supported YouTube channel metadata. Endpoint: channels.update. "
    "Quota cost: 50. Auth: oauth_required."
)
CHANNELS_UPDATE_USAGE_NOTES = (
    "Quota cost: 50. Auth: oauth_required. Provide exactly one part: brandingSettings or localizations.",
    "Quota cost: 50. The request body must include id and the body field matching the selected part.",
    "Quota cost: 50. Update bodies replace writable content for the selected part; include fields that should remain.",
    "Quota cost: 50. brandingSettings.image.bannerExternalUrl can activate a banner URL returned by channelBanners_insert.",
)
CHANNELS_UPDATE_CAVEATS = (
    "This low-level tool only supports brandingSettings and localizations in this slice.",
    "Read-only or unsupported channel fields such as snippet, statistics, status, contentDetails, and topicDetails are rejected.",
    "onBehalfOfContentOwner delegation is not supported by this Layer 2 slice.",
    "The tool does not upload banner media, perform channel lookup, enrich analytics, or orchestrate multi-step workflows.",
)
CHANNELS_UPDATE_CALLER_EXAMPLES = (
    {
        "name": "update_branding_description",
        "arguments": {
            "part": "brandingSettings",
            "body": {
                "id": "UC123",
                "brandingSettings": {"channel": {"description": "Updated channel description"}},
            },
        },
        "result": {
            "endpoint": "channels.update",
            "quotaCost": 50,
            "updatedPart": "brandingSettings",
            "requestedParts": ["brandingSettings"],
            "item": {"id": "UC123", "brandingSettings": {"channel": {"description": "Updated channel description"}}},
        },
        "notes": "Updates supported branding settings for an authorized channel.",
    },
    {
        "name": "activate_banner_url",
        "arguments": {
            "part": "brandingSettings",
            "body": {
                "id": "UC123",
                "brandingSettings": {"image": {"bannerExternalUrl": "https://yt3.example/banner"}},
            },
        },
        "result": {"endpoint": "channels.update", "quotaCost": 50, "updatedPart": "brandingSettings"},
        "notes": "Uses a bannerExternalUrl from channelBanners_insert; media upload itself is out of scope.",
    },
    {
        "name": "update_localizations",
        "arguments": {
            "part": "localizations",
            "body": {"id": "UC123", "localizations": {"es": {"title": "Canal", "description": "Descripcion"}}},
        },
        "result": {"endpoint": "channels.update", "quotaCost": 50, "updatedPart": "localizations"},
        "notes": "Updates localized channel metadata for the selected part.",
    },
    {
        "name": "missing_oauth",
        "arguments": {"part": "brandingSettings", "body": {"id": "UC123", "brandingSettings": {}}},
        "error": {"category": "authentication_failed", "field": "auth"},
        "notes": "channels_update requires eligible OAuth authorization and has no API-key fallback.",
    },
    {
        "name": "missing_body",
        "arguments": {"part": "brandingSettings"},
        "error": {"category": "invalid_request", "field": "body"},
        "notes": "A channel resource body is required.",
    },
    {
        "name": "part_body_mismatch",
        "arguments": {"part": "localizations", "body": {"id": "UC123", "brandingSettings": {}}},
        "error": {"category": "invalid_request", "field": "body.localizations"},
        "notes": "The body must include the field selected by part.",
    },
    {
        "name": "read_only_field",
        "arguments": {"part": "brandingSettings", "body": {"id": "UC123", "snippet": {"title": "Read only"}}},
        "error": {"category": "invalid_request", "field": "body.snippet"},
        "notes": "Read-only and unsupported channel fields are rejected before endpoint execution.",
    },
    {
        "name": "unsupported_part",
        "arguments": {"part": "status", "body": {"id": "UC123", "status": {"privacyStatus": "public"}}},
        "error": {"category": "invalid_request", "field": "part"},
        "notes": "Only brandingSettings and localizations are supported in this slice.",
    },
)


class ChannelsListToolError(ValueError):
    """Represent a safe caller-facing ``channels_list`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channels-list error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


class ChannelsUpdateToolError(ValueError):
    """Represent a safe caller-facing ``channels_update`` failure."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe channels-update error.

        :param message: Caller-facing error message.
        :param category: Shared safe error category.
        :param details: Safe diagnostic details for MCP error payloads.
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}


def _default_channels_transport(_execution) -> dict[str, Any]:
    """Return a safe empty channel collection for local default execution.

    :param _execution: Layer 1 execution request, unused by the default transport.
    :return: Empty upstream-shaped channel collection.
    """
    return {"items": []}


def _default_channels_update_transport(execution) -> dict[str, Any]:
    """Return a safe updated channel resource for local default execution.

    :param execution: Layer 1 execution request containing validated arguments.
    :return: Upstream-shaped updated channel resource without private data.
    """
    body = execution.arguments.get("body", {})
    part = execution.arguments.get("part")
    response: dict[str, Any] = {"id": body.get("id", "UC123")}
    if isinstance(part, str) and isinstance(body.get(part), dict):
        response[part] = body[part]
    return response


def _default_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channels_list``.

    :return: Executor with a safe local transport for endpoint-shaped results.
    """
    return IntegrationExecutor(transport=_default_channels_transport, retry_policy=RetryPolicy(max_attempts=1))


def _default_update_executor() -> IntegrationExecutor:
    """Build the default Layer 1 executor used by ``channels_update``.

    :return: Executor with a safe local transport for updated-resource results.
    """
    return IntegrationExecutor(transport=_default_channels_update_transport, retry_policy=RetryPolicy(max_attempts=1))


def build_channels_list_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channels_list``.

    :return: Validated Layer 2 tool contract for ``channels_list``.
    """
    return YouTubeToolContract(
        tool_name=CHANNELS_LIST_TOOL_NAME,
        upstream_resource="channels",
        upstream_method="list",
        operation_key="channels.list",
        description=CHANNELS_LIST_DESCRIPTION,
        auth_mode=AuthMode.MIXED,
        quota_cost=CHANNELS_LIST_QUOTA_COST,
        resource_family="channels",
        input_contract=CHANNELS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "pagingFields": ["nextPageToken", "prevPageToken", "pageInfo"],
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "selector", "requestedParts"),
            preserved_upstream_fields=("items", "nextPageToken", "prevPageToken", "pageInfo", "requestedParts"),
            disallowed_behavior=(
                "channel_search",
                "ranking",
                "analytics",
                "video_expansion",
                "playlist_expansion",
                "branding_update",
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
        usage_notes=CHANNELS_LIST_USAGE_NOTES,
        caveats=CHANNELS_LIST_CAVEATS,
    )


def build_channels_update_contract() -> YouTubeToolContract:
    """Build the public contract metadata for ``channels_update``.

    :return: Validated Layer 2 tool contract for ``channels_update``.
    """
    return YouTubeToolContract(
        tool_name=CHANNELS_UPDATE_TOOL_NAME,
        upstream_resource="channels",
        upstream_method="update",
        operation_key="channels.update",
        description=CHANNELS_UPDATE_DESCRIPTION,
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=CHANNELS_UPDATE_QUOTA_COST,
        resource_family="channels",
        input_contract=CHANNELS_UPDATE_INPUT_SCHEMA,
        response_convention={
            "resultKind": "updated_resource",
            "resourcePath": "item",
            "updatedPartField": "updatedPart",
            "requestedPartsField": "requestedParts",
            "supportedWritableParts": list(CHANNELS_UPDATE_SUPPORTED_PARTS),
            "bodyPolicy": "selected_part_body_replaces_writable_content",
            "activationBoundary": "channelBanners_insert returns bannerExternalUrl; channels_update activates it",
        },
        response_boundary=ResponseBoundary(
            boundary_kind=ResponseBoundaryKind.NEAR_RAW,
            allowed_wrapper_fields=("endpoint", "quotaCost", "updatedPart", "requestedParts"),
            preserved_upstream_fields=(
                "item",
                "resource",
                "id",
                "kind",
                "etag",
                "brandingSettings",
                "localizations",
                "requestedParts",
            ),
            disallowed_behavior=(
                "channel_lookup",
                "analytics",
                "banner_upload",
                "multi_step_orchestration",
                "read_only_channel_update",
                "content_owner_delegation",
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
        usage_notes=CHANNELS_UPDATE_USAGE_NOTES,
        caveats=CHANNELS_UPDATE_CAVEATS,
    )


def _active_selectors(arguments: dict[str, Any]) -> list[tuple[str, Any]]:
    """Return active channel selectors from one request.

    :param arguments: Caller-supplied ``channels_list`` arguments.
    :return: Active selector name/value pairs.
    """
    active: list[tuple[str, Any]] = []
    for selector in CHANNELS_LIST_SELECTORS:
        value = arguments.get(selector)
        if selector == "mine":
            if value is True:
                active.append((selector, True))
        elif isinstance(value, str) and value.strip():
            active.append((selector, value.strip()))
    return active


def validate_channels_list_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> tuple[str, Any]:
    """Validate ``channels_list`` arguments and return the selected mode.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for owner-scoped lookup.
    :return: Selected selector name and safe value.
    :raises ChannelsListToolError: If arguments are invalid or require missing authorization.
    """
    supported_fields = set(CHANNELS_LIST_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field not in supported_fields:
            raise ChannelsListToolError(
                f"channels_list does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    part = arguments.get("part")
    if not isinstance(part, str) or not part.strip():
        raise ChannelsListToolError(
            "channels_list requires part.",
            category="invalid_request",
            details={"field": "part"},
        )

    for field in ("pageToken", "hl"):
        if field in arguments and (not isinstance(arguments[field], str) or not arguments[field].strip()):
            raise ChannelsListToolError(
                f"channels_list requires a non-empty {field}.",
                category="invalid_request",
                details={"field": field},
            )

    if "maxResults" in arguments:
        max_results = arguments["maxResults"]
        if isinstance(max_results, bool) or not isinstance(max_results, int) or not 0 <= max_results <= 50:
            raise ChannelsListToolError(
                "channels_list maxResults must be an integer from 0 through 50.",
                category="invalid_request",
                details={"field": "maxResults"},
            )

    provided_selectors: list[str] = []
    for selector in CHANNELS_LIST_SELECTORS:
        if selector not in arguments:
            continue

        value = arguments[selector]
        if selector == "mine":
            if value is not True:
                raise ChannelsListToolError(
                    "channels_list mine selector must be true when present.",
                    category="invalid_request",
                    details={"field": "mine"},
                )
        elif not isinstance(value, str) or not value.strip():
            raise ChannelsListToolError(
                f"channels_list requires a non-empty {selector}.",
                category="invalid_request",
                details={"field": selector},
            )
        elif selector == "forHandle" and any(character.isspace() for character in value.strip()):
            raise ChannelsListToolError(
                "channels_list forHandle cannot contain whitespace.",
                category="invalid_request",
                details={"field": "forHandle"},
            )
        provided_selectors.append(selector)

    active = _active_selectors(arguments)
    if len(provided_selectors) != 1 or len(active) != 1:
        raise ChannelsListToolError(
            "channels_list requires exactly one selector: id, mine, forHandle, or forUsername.",
            category="invalid_request",
            details={"field": "selector", "selectors": provided_selectors},
        )

    selector, value = active[0]
    if selector == "mine" and not oauth_token:
        raise ChannelsListToolError(
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
    """Build the Layer 1 auth context for a channel selector.

    :param selector: Selected channel selector.
    :param api_key: API key value available for public selector access.
    :param oauth_token: OAuth token available for owner-scoped lookup.
    :return: Auth context suitable for the Layer 1 wrapper.
    :raises ChannelsListToolError: If required credentials are unavailable.
    """
    if selector in {"id", "forHandle", "forUsername"}:
        if not api_key:
            raise ChannelsListToolError(
                f"{selector} requires public API-key access.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key))

    if selector == "mine":
        if not oauth_token:
            raise ChannelsListToolError(
                "mine requires eligible user authorization.",
                category="authentication_failed",
                details={"selector": selector},
            )
        return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))

    raise ChannelsListToolError(
        "channels_list requires a supported selector.",
        category="invalid_request",
        details={"field": "selector"},
    )


def _requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return normalized requested part names.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Ordered part names with whitespace removed.
    """
    return [part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip()]


def _channels_update_requested_parts(arguments: dict[str, Any]) -> list[str]:
    """Return the normalized writable part selected for ``channels_update``.

    :param arguments: Tool arguments containing a ``part`` value.
    :return: Single selected writable part when present.
    """
    part = arguments.get("part")
    if isinstance(part, str) and part.strip():
        return [part.strip()]
    return []


def map_channels_list_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel response to the public Layer 2 result shape.

    :param response: Upstream-shaped response returned by the Layer 1 wrapper.
    :param arguments: Original validated tool arguments.
    :return: Near-raw channel collection with light MCP clarity fields.
    """
    selector, _value = _active_selectors(arguments)[0]
    result: dict[str, Any] = {
        "endpoint": "channels.list",
        "quotaCost": CHANNELS_LIST_QUOTA_COST,
        "items": response.get("items", []),
        "requestedParts": _requested_parts(arguments),
        "selector": {"name": selector},
    }
    for field in ("nextPageToken", "prevPageToken", "pageInfo"):
        if field in response:
            result[field] = response[field]
    return result


def validate_channels_update_arguments(
    arguments: dict[str, Any],
    *,
    oauth_token: str | None = None,
) -> str:
    """Validate ``channels_update`` arguments and return the selected part.

    :param arguments: Caller-supplied tool arguments.
    :param oauth_token: Optional OAuth token availability for update access.
    :return: The single selected writable part.
    :raises ChannelsUpdateToolError: If arguments are invalid or authorization is missing.
    """
    supported_fields = set(CHANNELS_UPDATE_INPUT_SCHEMA["properties"])
    for field in arguments:
        if field == "onBehalfOfContentOwner":
            raise ChannelsUpdateToolError(
                "channels_update does not support content-owner delegation in this slice.",
                category="invalid_request",
                details={"field": "onBehalfOfContentOwner"},
            )
        if field not in supported_fields:
            raise ChannelsUpdateToolError(
                f"channels_update does not support {field}.",
                category="invalid_request",
                details={"field": field},
            )

    raw_part = arguments.get("part")
    if not isinstance(raw_part, str) or not raw_part.strip():
        raise ChannelsUpdateToolError(
            "channels_update requires part.",
            category="invalid_request",
            details={"field": "part"},
        )
    parts = [part.strip() for part in raw_part.split(",") if part.strip()]
    if len(parts) != 1 or raw_part.count(",") > 0:
        raise ChannelsUpdateToolError(
            "channels_update requires exactly one writable part.",
            category="invalid_request",
            details={"field": "part"},
        )
    part = parts[0]
    if part not in CHANNELS_UPDATE_SUPPORTED_PARTS:
        raise ChannelsUpdateToolError(
            "channels_update supports only brandingSettings or localizations.",
            category="invalid_request",
            details={"field": "part", "supportedParts": list(CHANNELS_UPDATE_SUPPORTED_PARTS)},
        )

    body = arguments.get("body")
    if not isinstance(body, dict) or not body:
        raise ChannelsUpdateToolError(
            "channels_update requires a non-empty body.",
            category="invalid_request",
            details={"field": "body"},
        )
    channel_id = body.get("id")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsUpdateToolError(
            "channels_update body.id is required.",
            category="invalid_request",
            details={"field": "body.id"},
        )
    if part not in body:
        raise ChannelsUpdateToolError(
            f"channels_update body.{part} is required for the selected part.",
            category="invalid_request",
            details={"field": f"body.{part}"},
        )
    if not isinstance(body[part], dict) or not body[part]:
        raise ChannelsUpdateToolError(
            f"channels_update body.{part} must be a non-empty object.",
            category="invalid_request",
            details={"field": f"body.{part}"},
        )

    allowed_body_fields = {"id", part}
    for field in body:
        if field not in allowed_body_fields:
            raise ChannelsUpdateToolError(
                f"channels_update body.{field} is read-only or unsupported.",
                category="invalid_request",
                details={"field": f"body.{field}"},
            )

    if not oauth_token:
        raise ChannelsUpdateToolError(
            "channels_update requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return part


def _auth_context_for_update(*, oauth_token: str | None) -> AuthContext:
    """Build the Layer 1 auth context for ``channels_update``.

    :param oauth_token: OAuth token available for channel update access.
    :return: OAuth-required auth context suitable for the Layer 1 wrapper.
    :raises ChannelsUpdateToolError: If OAuth credentials are unavailable.
    """
    if not oauth_token:
        raise ChannelsUpdateToolError(
            "channels_update requires eligible OAuth authorization.",
            category="authentication_failed",
            details={"field": "auth", "authMode": "oauth_required"},
        )
    return AuthContext(mode=Layer1AuthMode.OAUTH_REQUIRED, credentials=CredentialBundle(oauth_token=oauth_token))


def map_channels_update_result(response: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map a Layer 1 channel update response to the public Layer 2 result shape.

    :param response: Upstream-shaped updated channel resource returned by Layer 1.
    :param arguments: Original validated tool arguments.
    :return: Near-raw updated channel resource with light MCP clarity fields.
    """
    requested_parts = _channels_update_requested_parts(arguments)
    updated_part = requested_parts[0] if requested_parts else ""
    item: Any
    if "item" in response:
        item = response["item"]
    elif "resource" in response:
        item = response["resource"]
    elif isinstance(response.get("items"), list) and response["items"]:
        item = response["items"][0]
    else:
        item = response

    return {
        "endpoint": "channels.update",
        "quotaCost": CHANNELS_UPDATE_QUOTA_COST,
        "updatedPart": updated_part,
        "requestedParts": requested_parts,
        "item": item,
    }


def _map_upstream_error(error: NormalizedUpstreamError) -> ChannelsListToolError:
    """Map a normalized upstream error to the public Layer 2 error model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channels_list`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
    }
    return ChannelsListToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def _map_channels_update_upstream_error(error: NormalizedUpstreamError) -> ChannelsUpdateToolError:
    """Map a normalized upstream error to the public ``channels_update`` model.

    :param error: Normalized upstream failure raised by Layer 1 execution.
    :return: Safe ``channels_update`` error.
    """
    categories = {
        "auth": "authorization_failed",
        "not_found": "resource_not_found",
        "rate_limit": "quota_exhausted",
        "transient": "endpoint_unavailable",
        "upstream_service": "upstream_failure",
        "invalid_request": "invalid_request",
        "validation": "invalid_request",
    }
    return ChannelsUpdateToolError(
        str(error),
        category=categories.get(error.category, "upstream_failure"),
        details={"upstreamStatus": error.upstream_status} if error.upstream_status else {},
    )


def build_channels_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-access",
    oauth_token: str | None = None,
):
    """Build the concrete ``channels_list`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Callable dispatcher handler.
    """
    channels_wrapper = wrapper or build_channels_list_wrapper()
    channels_executor = executor or _default_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channels_list`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 channel collection result.
        :raises ChannelsListToolError: If validation, authorization, or upstream execution fails.
        """
        selector, _value = validate_channels_list_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context_for_selector(selector, api_key=api_key, oauth_token=oauth_token)
        try:
            response = channels_wrapper.call(channels_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_upstream_error(error) from error
        except ValueError as error:
            raise ChannelsListToolError(
                str(error),
                category="invalid_request",
                details={"selector": selector},
            ) from error
        except Exception as error:
            raise ChannelsListToolError(
                "channels_list upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channels_list_result(response, arguments)

    return handler


def build_channels_update_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-update",
):
    """Build the concrete ``channels_update`` handler.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for channel update requests.
    :return: Callable dispatcher handler.
    """
    channels_wrapper = wrapper or build_channels_update_wrapper()
    channels_executor = executor or _default_update_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one ``channels_update`` request.

        :param arguments: Validated dispatcher arguments.
        :return: Public Layer 2 updated channel resource result.
        :raises ChannelsUpdateToolError: If validation, authorization, or upstream execution fails.
        """
        part = validate_channels_update_arguments(arguments, oauth_token=oauth_token)
        auth_context = _auth_context_for_update(oauth_token=oauth_token)
        try:
            response = channels_wrapper.call(channels_executor, arguments=arguments, auth_context=auth_context)
        except NormalizedUpstreamError as error:
            raise _map_channels_update_upstream_error(error) from error
        except ValueError as error:
            raise ChannelsUpdateToolError(
                str(error),
                category="invalid_request",
                details={"field": "body", "part": part},
            ) from error
        except Exception as error:
            raise ChannelsUpdateToolError(
                "channels_update upstream execution failed.",
                category="upstream_failure",
            ) from error
        return map_channels_update_result(response, arguments)

    return handler


def build_channels_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    api_key: str | None = "public-channel-access",
    oauth_token: str | None = None,
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channels_list`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API-key availability for public selector requests.
    :param oauth_token: OAuth token availability for owner-scoped lookup.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channels_list_contract()
    return {
        "name": CHANNELS_LIST_TOOL_NAME,
        "description": CHANNELS_LIST_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNELS_LIST_INPUT_SCHEMA,
        "handler": build_channels_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
            oauth_token=oauth_token,
        ),
    }


def build_channels_update_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | None = None,
    oauth_token: str | None = "authorized-channel-update",
) -> dict[str, Any]:
    """Build the dispatcher descriptor for the ``channels_update`` tool.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param oauth_token: OAuth token availability for channel update requests.
    :return: Dispatcher-compatible descriptor for the concrete Layer 2 tool.
    """
    contract = build_channels_update_contract()
    return {
        "name": CHANNELS_UPDATE_TOOL_NAME,
        "description": CHANNELS_UPDATE_DESCRIPTION,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": CHANNELS_UPDATE_INPUT_SCHEMA,
        "handler": build_channels_update_handler(
            wrapper=wrapper,
            executor=executor,
            oauth_token=oauth_token,
        ),
    }


__all__ = [
    "CHANNELS_LIST_CAVEATS",
    "CHANNELS_LIST_CALLER_EXAMPLES",
    "CHANNELS_LIST_DESCRIPTION",
    "CHANNELS_LIST_INPUT_SCHEMA",
    "CHANNELS_LIST_QUOTA_COST",
    "CHANNELS_LIST_SELECTORS",
    "CHANNELS_LIST_TOOL_NAME",
    "CHANNELS_LIST_USAGE_NOTES",
    "CHANNELS_UPDATE_CAVEATS",
    "CHANNELS_UPDATE_CALLER_EXAMPLES",
    "CHANNELS_UPDATE_DESCRIPTION",
    "CHANNELS_UPDATE_INPUT_SCHEMA",
    "CHANNELS_UPDATE_QUOTA_COST",
    "CHANNELS_UPDATE_SUPPORTED_PARTS",
    "CHANNELS_UPDATE_TOOL_NAME",
    "CHANNELS_UPDATE_USAGE_NOTES",
    "ChannelsListToolError",
    "ChannelsUpdateToolError",
    "build_channels_list_contract",
    "build_channels_list_handler",
    "build_channels_list_tool_descriptor",
    "build_channels_update_contract",
    "build_channels_update_handler",
    "build_channels_update_tool_descriptor",
    "map_channels_list_result",
    "map_channels_update_result",
    "validate_channels_list_arguments",
    "validate_channels_update_arguments",
]
