"""Shared YouTube input, response, and error conventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from mcp_server.tools.youtube_common.contracts import YouTubeToolContractError


class ResponseKind(Enum):
    """Represent successful result kinds used by YouTube tools."""

    LIST = "list"
    MUTATION_ACKNOWLEDGMENT = "mutation_acknowledgment"
    UPLOAD_RESULT = "upload_result"
    DOWNLOAD_WRAPPER = "download_wrapper"
    LOOKUP = "lookup"


class ResponseBoundaryKind(Enum):
    """Classify whether response behavior belongs in endpoint-backed YouTube tools."""

    NEAR_RAW = "near_raw"
    LIGHTLY_RESHAPED = "lightly_reshaped"
    OUT_OF_SCOPE = "out_of_scope"


class ErrorCategory(Enum):
    """Represent stable MCP-safe YouTube tool failure categories."""

    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    QUOTA_EXHAUSTED = "quota_exhausted"
    RESOURCE_NOT_FOUND = "resource_not_found"
    INVALID_REQUEST = "invalid_request"
    DEPRECATED_ENDPOINT = "deprecated_endpoint"
    ENDPOINT_UNAVAILABLE = "endpoint_unavailable"
    UPSTREAM_FAILURE = "upstream_failure"


@dataclass(frozen=True)
class InputConvention:
    """Describe how MCP-facing inputs map to upstream request concepts.

    :param required_fields: Required caller-facing field names.
    :param optional_fields: Optional caller-facing field names.
    :param selector_groups: Mutually exclusive or conditional selector groups.
    :param part_fields: Upstream ``part`` values when relevant.
    :param pagination_fields: Pagination-related field names.
    :param request_body_fields: Request body field names.
    :param media_fields: Media or upload field names.
    :param delegation_fields: Delegation or content-owner field names.
    """

    required_fields: tuple[str, ...] = field(default_factory=tuple)
    optional_fields: tuple[str, ...] = field(default_factory=tuple)
    selector_groups: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    part_fields: tuple[str, ...] = field(default_factory=tuple)
    pagination_fields: tuple[str, ...] = field(default_factory=tuple)
    request_body_fields: tuple[str, ...] = field(default_factory=tuple)
    media_fields: tuple[str, ...] = field(default_factory=tuple)
    delegation_fields: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_media_inputs(self) -> bool:
        """Return whether this convention includes media-related inputs.

        :return: True when media fields are present.
        """
        return bool(self.media_fields)

    def to_schema(self) -> dict[str, Any]:
        """Build JSON-compatible schema metadata for the input convention.

        :return: Schema-like metadata suitable for shared YouTube tests and
            future MCP tool definitions.
        """
        all_fields = tuple(
            dict.fromkeys(
                self.required_fields
                + self.optional_fields
                + self.part_fields
                + self.pagination_fields
                + self.request_body_fields
                + self.media_fields
                + self.delegation_fields
                + tuple(field for group in self.selector_groups for field in group)
            )
        )
        schema: dict[str, Any] = {
            "type": "object",
            "required": list(self.required_fields),
            "properties": {field: {"type": "string"} for field in all_fields},
            "additionalProperties": False,
        }
        if self.selector_groups:
            schema["oneOf"] = [{"required": list(group)} for group in self.selector_groups]
        return schema


@dataclass(frozen=True)
class ResponseConvention:
    """Describe a near-raw successful YouTube tool response shape.

    :param result_kind: Shared result kind.
    :param items_path: Path to returned items for list or lookup results.
    :param paging_fields: Paging fields preserved from upstream responses.
    :param requested_parts: Requested resource parts preserved for review.
    :param wrapper_fields: Light MCP clarity wrapper fields.
    :param content_policy: Safe content policy for downloads or media payloads.
    """

    result_kind: ResponseKind
    items_path: str = ""
    paging_fields: tuple[str, ...] = field(default_factory=tuple)
    requested_parts: tuple[str, ...] = field(default_factory=tuple)
    wrapper_fields: tuple[str, ...] = field(default_factory=tuple)
    content_policy: str = ""

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible metadata for this response convention.

        :return: Metadata that preserves the near-raw response shape.
        """
        metadata: dict[str, Any] = {
            "resultKind": self.result_kind.value,
            "pagingFields": list(self.paging_fields),
            "requestedParts": list(self.requested_parts),
            "wrapperFields": list(self.wrapper_fields),
        }
        if self.result_kind in {ResponseKind.LIST, ResponseKind.LOOKUP}:
            metadata["itemsPath"] = self.items_path or "items"
        if self.result_kind is ResponseKind.MUTATION_ACKNOWLEDGMENT:
            metadata["acknowledgment"] = True
        if self.result_kind is ResponseKind.UPLOAD_RESULT:
            metadata["mediaResult"] = True
        if self.result_kind is ResponseKind.DOWNLOAD_WRAPPER:
            metadata["contentPolicy"] = self.content_policy or "safe_text_or_metadata_wrapper"
        return metadata


@dataclass(frozen=True)
class ResponseBoundary:
    """Describe the boundary between endpoint-backed and higher-level responses.

    :param boundary_kind: Classification of the response behavior.
    :param allowed_wrapper_fields: Safe wrapper fields allowed for MCP clarity.
    :param preserved_upstream_fields: Upstream-visible fields preserved.
    :param disallowed_behavior: Behaviors that belong outside endpoint-backed tools.
    """

    boundary_kind: ResponseBoundaryKind
    allowed_wrapper_fields: tuple[str, ...] = field(default_factory=tuple)
    preserved_upstream_fields: tuple[str, ...] = field(default_factory=tuple)
    disallowed_behavior: tuple[str, ...] = field(default_factory=tuple)

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible response-boundary metadata.

        :return: Metadata describing the response boundary.
        :raises YouTubeToolContractError: If out-of-scope behavior is not explained.
        """
        if not isinstance(self.boundary_kind, ResponseBoundaryKind):
            raise YouTubeToolContractError("boundary_kind must be a ResponseBoundaryKind")
        if self.boundary_kind is ResponseBoundaryKind.OUT_OF_SCOPE and not self.disallowed_behavior:
            raise YouTubeToolContractError("out-of-scope response boundaries require disallowed behavior")
        return {
            "boundaryKind": self.boundary_kind.value,
            "allowedWrapperFields": list(self.allowed_wrapper_fields),
            "preservedUpstreamFields": list(self.preserved_upstream_fields),
            "disallowedBehavior": list(self.disallowed_behavior),
        }


UNSAFE_DETAIL_MARKERS = (
    "api_key",
    "apikey",
    "token",
    "secret",
    "stack",
    "credential",
    "raw_media",
    "raw_request",
    "rawrequest",
    "raw_body",
    "rawbody",
    "signed_url",
    "signedurl",
)


def sanitize_error_details(details: dict[str, Any]) -> dict[str, Any]:
    """Remove secret-bearing fields from caller-facing error details.

    :param details: Candidate diagnostic detail mapping.
    :return: A copy containing only safe diagnostic fields.
    """
    safe: dict[str, Any] = {}
    for key, value in details.items():
        normalized = key.lower()
        if any(marker in normalized for marker in UNSAFE_DETAIL_MARKERS):
            continue
        if isinstance(value, dict):
            safe[key] = sanitize_error_details(value)
        elif isinstance(value, list):
            safe[key] = [sanitize_error_details(item) if isinstance(item, dict) else item for item in value]
        else:
            safe[key] = value
    return safe
