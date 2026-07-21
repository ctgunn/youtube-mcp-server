"""Concrete Layer 2 tool support for YouTube ``videoAbuseReportReasons``."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext, CredentialBundle
from mcp_server.integrations.auth import AuthMode as Layer1AuthMode
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.video_abuse_report_reasons import (
    build_video_abuse_report_reasons_list_wrapper,
)
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.tools.youtube_common.contracts import AuthMode, AvailabilityState, YouTubeToolContract
from mcp_server.tools.youtube_common.conventions import ResponseBoundary, ResponseBoundaryKind, sanitize_error_details


VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME = "videoAbuseReportReasons_list"
VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST = 1
VIDEO_ABUSE_REPORT_REASONS_LIST_ALLOWED_FIELDS = frozenset({"part", "hl"})
VIDEO_ABUSE_REPORT_REASONS_LIST_UNSAFE_DETAIL_KEYS = frozenset(
    {
        "authorization",
        "authorization_header",
        "headers",
        "request_headers",
        "response_body",
        "upstream_body",
    }
)

VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA = {
    "type": "object",
    "required": ["part", "hl"],
    "properties": {
        "part": {"type": "string", "minLength": 1},
        "hl": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION = (
    "List localized YouTube video abuse report reasons. Endpoint: videoAbuseReportReasons.list. "
    "Quota cost: 1. Auth: api_key. Requires part and hl."
)

VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES = (
    "Quota cost: 1. Auth: api_key. Provide part, usually snippet, and hl for the desired localization.",
    "Quota cost: 1. Empty upstream items are returned as a successful empty reason list.",
    "Quota cost: 1. This lookup is read-only metadata for abuse-report reason labels and descriptions.",
)

VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS = (
    "This tool lists available reason metadata; report submission belongs to videos_reportAbuse.",
    "moderation, policy adjudication, ranking, summarization, enrichment, and translated label generation are out of scope.",
    "The tool preserves upstream reason fields and does not fabricate labels, translations, or policy guidance.",
)

VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES = (
    {
        "name": "localized_reason_lookup",
        "description": "Quota cost: 1. Retrieve localized reason metadata for a caller-selected language.",
        "arguments": {"part": "snippet", "hl": "en"},
        "result": {"endpoint": "videoAbuseReportReasons.list", "itemsPath": "items"},
        "quotaCost": 1,
    },
    {
        "name": "populated_success",
        "description": "Quota cost: 1. Successful lookup with one or more upstream reason items.",
        "arguments": {"part": "snippet", "hl": "en-US"},
        "result": {"items": [{"id": "S"}], "localization": {"hl": "en-US"}},
        "quotaCost": 1,
    },
    {
        "name": "empty_success",
        "description": "Quota cost: 1. Empty upstream items remain a successful empty list result.",
        "arguments": {"part": "snippet", "hl": "fr"},
        "result": {"items": [], "empty": True},
        "quotaCost": 1,
    },
    {
        "name": "missing_part",
        "description": "Quota cost: 1. Missing part is rejected before upstream execution.",
        "arguments": {"hl": "en"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "missing_hl",
        "description": "Quota cost: 1. Missing hl is rejected because localization is required.",
        "arguments": {"part": "snippet"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_part",
        "description": "Quota cost: 1. Empty or malformed part values are rejected.",
        "arguments": {"part": "", "hl": "en"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "invalid_hl",
        "description": "Quota cost: 1. Empty or whitespace-containing hl values are rejected.",
        "arguments": {"part": "snippet", "hl": "bad language"},
        "errorCategory": "invalid_request",
    },
    {
        "name": "access_failure",
        "description": "Quota cost: 1. Missing API-key access is reported as an authentication failure.",
        "arguments": {"part": "snippet", "hl": "en"},
        "errorCategory": "authentication_failed",
    },
    {
        "name": "quota_or_upstream_failure",
        "description": "Quota cost: 1. Quota and upstream failures are mapped to safe public categories.",
        "arguments": {"part": "snippet", "hl": "en"},
        "errorCategory": "quota_exhausted",
    },
    {
        "name": "deprecated_endpoint",
        "description": "Quota cost: 1. Deprecated endpoint failures are surfaced distinctly when upstream reports them.",
        "arguments": {"part": "snippet", "hl": "en"},
        "errorCategory": "deprecated_endpoint",
    },
    {
        "name": "endpoint_unavailable",
        "description": "Quota cost: 1. Endpoint availability failures are surfaced without unsafe upstream details.",
        "arguments": {"part": "snippet", "hl": "en"},
        "errorCategory": "endpoint_unavailable",
    },
    {
        "name": "out_of_scope_report_submission",
        "description": "Quota cost: 1. Report submission and moderation instructions are rejected as unsupported fields.",
        "arguments": {"part": "snippet", "hl": "en", "reportText": "remove this video"},
        "errorCategory": "invalid_request",
    },
)


class VideoAbuseReportReasonsListToolError(ValueError):
    """Represent a safe caller-facing ``videoAbuseReportReasons_list`` failure.

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
        self.details = _sanitize_video_abuse_report_reasons_list_error_details(details or {})


def _sanitize_video_abuse_report_reasons_list_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove endpoint-specific unsafe diagnostic fields.

    :param details: Candidate diagnostic details.
    :return: Safe details suitable for caller-facing errors.
    """
    sanitized = sanitize_error_details(details)
    return {
        key: value
        for key, value in sanitized.items()
        if key.lower().replace("-", "_") not in VIDEO_ABUSE_REPORT_REASONS_LIST_UNSAFE_DETAIL_KEYS
    }


def _split_parts(parts: str) -> list[str]:
    """Normalize a comma-delimited ``part`` selection.

    :param parts: Caller-provided ``part`` value.
    :return: Requested parts in caller order.
    """
    return [part.strip() for part in parts.split(",") if part.strip()]


def _require_text_field(arguments: dict[str, Any], field: str) -> str:
    """Require one non-empty text input field.

    :param arguments: Caller-provided arguments.
    :param field: Field name to validate.
    :return: Stripped field value.
    :raises VideoAbuseReportReasonsListToolError: If the field is missing or invalid.
    """
    value = arguments.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VideoAbuseReportReasonsListToolError(
            f"videoAbuseReportReasons_list requires non-empty {field}",
            details={"field": field},
        )
    return value.strip()


def _validate_hl(value: str) -> str:
    """Validate and normalize the required ``hl`` localization value.

    :param value: Candidate language or locale code.
    :return: Stripped language or locale code.
    :raises VideoAbuseReportReasonsListToolError: If ``hl`` is malformed.
    """
    normalized = value.strip()
    if any(character.isspace() for character in normalized) or not all(
        character.isalnum() or character in {"-", "_"} for character in normalized
    ):
        raise VideoAbuseReportReasonsListToolError(
            "hl must be a non-empty language or locale code",
            details={"field": "hl"},
        )
    return normalized


def validate_video_abuse_report_reasons_list_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate ``videoAbuseReportReasons_list`` arguments.

    :param arguments: Candidate tool arguments.
    :return: Normalized ``part`` and ``hl`` values.
    :raises VideoAbuseReportReasonsListToolError: If the request shape is unsupported.
    """
    if not isinstance(arguments, dict):
        raise VideoAbuseReportReasonsListToolError("videoAbuseReportReasons_list arguments must be an object")
    for field in arguments:
        if field not in VIDEO_ABUSE_REPORT_REASONS_LIST_ALLOWED_FIELDS:
            raise VideoAbuseReportReasonsListToolError(
                f"unsupported field for videoAbuseReportReasons_list: {field}",
                details={"field": field},
            )

    part = _require_text_field(arguments, "part")
    if not _split_parts(part):
        raise VideoAbuseReportReasonsListToolError(
            "part must include at least one requested resource part",
            details={"field": "part"},
        )
    return {"part": part, "hl": _validate_hl(_require_text_field(arguments, "hl"))}


def map_video_abuse_report_reasons_list_result(payload: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    """Map an upstream reason-list payload to the public Layer 2 result.

    :param payload: Upstream or Layer 1 video abuse report reason list payload.
    :param arguments: Caller arguments used for the request.
    :return: Near-raw reason list result with safe operation context.
    """
    normalized = validate_video_abuse_report_reasons_list_arguments(arguments)
    items = payload.get("items", []) if isinstance(payload, dict) else []
    result = {
        "endpoint": "videoAbuseReportReasons.list",
        "quotaCost": VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST,
        "requestedParts": _split_parts(normalized["part"]),
        "localization": {"hl": normalized["hl"]},
        "auth": {"mode": "api_key"},
        "items": items,
        "empty": not bool(items),
    }
    if isinstance(payload, dict):
        for field in ("kind", "etag", "pageInfo", "nextPageToken", "prevPageToken"):
            if field in payload:
                result[field] = payload[field]
    return result


def _map_upstream_error(error: NormalizedUpstreamError) -> VideoAbuseReportReasonsListToolError:
    """Map a normalized upstream failure to a safe tool error.

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
        "unavailable": "endpoint_unavailable",
        "deprecated": "deprecated_endpoint",
    }
    category = category_map.get(error.category, "upstream_failure")
    return VideoAbuseReportReasonsListToolError(str(error), category=category, details=error.details or {})


def _api_key_auth_context(api_key: str | None) -> AuthContext:
    """Build the Layer 1 API-key auth context.

    :param api_key: API key credential value.
    :return: Layer 1 auth context for API-key execution.
    :raises VideoAbuseReportReasonsListToolError: If API-key access is missing.
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise VideoAbuseReportReasonsListToolError(
            "videoAbuseReportReasons_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        )
    try:
        return AuthContext(mode=Layer1AuthMode.API_KEY, credentials=CredentialBundle(api_key=api_key.strip()))
    except ValueError as exc:
        raise VideoAbuseReportReasonsListToolError(
            "videoAbuseReportReasons_list requires API-key access",
            category="authentication_failed",
            details={"authMode": "api_key"},
        ) from exc


def build_video_abuse_report_reasons_list_contract() -> YouTubeToolContract:
    """Build the public contract for ``videoAbuseReportReasons_list``.

    :return: Shared YouTube tool contract for discovery metadata.
    """
    boundary = ResponseBoundary(
        boundary_kind=ResponseBoundaryKind.NEAR_RAW,
        allowed_wrapper_fields=(
            "endpoint",
            "quotaCost",
            "requestedParts",
            "localization",
            "auth",
            "items",
            "empty",
            "kind",
            "etag",
            "pageInfo",
            "nextPageToken",
            "prevPageToken",
        ),
        preserved_upstream_fields=("kind", "etag", "id", "snippet", "items", "pageInfo"),
        disallowed_behavior=(
            "report_submission",
            "moderation",
            "policy_adjudication",
            "ranking",
            "summarization",
            "enrichment",
            "translation_generation",
            "cross_endpoint_aggregation",
        ),
    )
    return YouTubeToolContract(
        tool_name=VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME,
        upstream_resource="videoAbuseReportReasons",
        upstream_method="list",
        operation_key="videoAbuseReportReasons.list",
        description=VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION,
        auth_mode=AuthMode.API_KEY,
        quota_cost=VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST,
        resource_family="video_abuse_report_reasons",
        input_contract=VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA,
        response_convention={
            "resultKind": "list",
            "itemsPath": "items",
            "localizationFields": ["hl"],
            "emptyResultPolicy": "empty_success_when_upstream_returns_empty_items",
        },
        response_boundary=boundary.to_metadata(),
        error_categories=(
            "invalid_request",
            "authentication_failed",
            "authorization_failed",
            "quota_exhausted",
            "endpoint_unavailable",
            "deprecated_endpoint",
            "upstream_failure",
        ),
        availability_state=AvailabilityState.ACTIVE,
        usage_notes=VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES,
        caveats=VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS,
    )


def _default_video_abuse_report_reasons_executor() -> IntegrationExecutor:
    """Build a deterministic local executor for default reason-list calls.

    :return: Integration executor returning representative abuse reason data.
    """

    def transport(_execution):
        """Return a representative video abuse report reason list response.

        :param _execution: Request execution context.
        :return: Fake upstream list response for local tool invocation.
        """
        return {
            "kind": "youtube#videoAbuseReportReasonListResponse",
            "items": [
                {
                    "kind": "youtube#videoAbuseReportReason",
                    "id": "S",
                    "snippet": {"label": "Spam or misleading", "secondaryReasons": []},
                }
            ],
        }

    return IntegrationExecutor(transport=transport, retry_policy=RetryPolicy(max_attempts=1))


def build_video_abuse_report_reasons_list_handler(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
):
    """Build the callable handler for ``videoAbuseReportReasons_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used to construct safe API-key auth context.
    :return: Callable that validates, executes, and maps reason-list lookups.
    """
    selected_wrapper = wrapper or build_video_abuse_report_reasons_list_wrapper()
    selected_executor = executor or _default_video_abuse_report_reasons_executor()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated ``videoAbuseReportReasons_list`` request.

        :param arguments: Caller-provided tool arguments.
        :return: Public Layer 2 video abuse report reason list result.
        :raises VideoAbuseReportReasonsListToolError: If validation or execution fails.
        """
        normalized = validate_video_abuse_report_reasons_list_arguments(arguments)
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
            raise VideoAbuseReportReasonsListToolError(
                str(exc),
                category="authentication_failed",
                details={"authMode": "api_key"},
            ) from exc
        return map_video_abuse_report_reasons_list_result(payload, normalized)

    return handler


def build_video_abuse_report_reasons_list_tool_descriptor(
    *,
    wrapper=None,
    executor: IntegrationExecutor | object | None = None,
    api_key: str | None = "local-api-key",
) -> dict[str, Any]:
    """Build the MCP tool descriptor for ``videoAbuseReportReasons_list``.

    :param wrapper: Optional Layer 1 wrapper override for tests.
    :param executor: Optional executor override for tests.
    :param api_key: API key value used by the default handler.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    contract = build_video_abuse_report_reasons_list_contract()
    metadata = contract.to_tool_metadata()
    metadata["examples"] = list(VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES)
    return {
        "name": VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME,
        "description": VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION,
        "inputSchema": VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA,
        "handler": build_video_abuse_report_reasons_list_handler(
            wrapper=wrapper,
            executor=executor,
            api_key=api_key,
        ),
        "metadata": metadata,
    }


__all__ = [
    "VIDEO_ABUSE_REPORT_REASONS_LIST_ALLOWED_FIELDS",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_UNSAFE_DETAIL_KEYS",
    "VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES",
    "VideoAbuseReportReasonsListToolError",
    "build_video_abuse_report_reasons_list_contract",
    "build_video_abuse_report_reasons_list_handler",
    "build_video_abuse_report_reasons_list_tool_descriptor",
    "map_video_abuse_report_reasons_list_result",
    "validate_video_abuse_report_reasons_list_arguments",
]
