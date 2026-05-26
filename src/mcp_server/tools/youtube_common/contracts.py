"""Shared YouTube contract primitives for endpoint-backed MCP tools.

The concrete endpoint tools are implemented in later feature slices. This
module owns only cross-cutting public contract metadata and validation helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

UNSAFE_METADATA_MARKERS = ("api", "secret", "stack", "raw_media", "signed_url", "signedurl")
SAFE_TOKEN_FIELDS = ("pagetoken", "nextpagetoken", "prevpagetoken")


class YouTubeToolContractError(ValueError):
    """Raised when shared YouTube contract metadata is invalid."""


class AuthMode(Enum):
    """Represent the credential mode declared by a YouTube tool contract."""

    API_KEY = "api_key"
    OAUTH_REQUIRED = "oauth_required"
    MIXED = "mixed/conditional"


class AvailabilityState(Enum):
    """Represent public availability status for a YouTube tool contract."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    UNAVAILABLE = "unavailable"
    REGION_CONSTRAINED = "region_constrained"
    OWNER_ONLY = "owner_only"
    MEDIA_CONSTRAINED = "media_constrained"
    DOCUMENTATION_CAVEAT = "documentation_caveat"


def _require_text(value: str, field_name: str) -> str:
    """Validate and normalize a required text field.

    :param value: Candidate text value.
    :param field_name: Name of the field being validated.
    :return: The stripped text value.
    :raises YouTubeToolContractError: If the value is not non-empty text.
    """
    if not isinstance(value, str) or not value.strip():
        raise YouTubeToolContractError(f"{field_name} is required")
    return value.strip()


def _contains_unsafe_marker(key: str) -> bool:
    """Return whether a metadata key looks unsafe for public exposure.

    :param key: Metadata key to inspect.
    :return: True when the key suggests secret or unsafe diagnostic content.
    """
    normalized = key.lower().replace("-", "_")
    compact = normalized.replace("_", "")
    if "token" in compact and compact not in SAFE_TOKEN_FIELDS:
        return True
    return any(marker in normalized for marker in UNSAFE_METADATA_MARKERS)


def validate_safe_public_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate public YouTube tool metadata before discovery exposure.

    :param metadata: JSON-compatible metadata intended for public surfaces.
    :return: The original metadata mapping when it contains no unsafe keys.
    :raises YouTubeToolContractError: If a key suggests secrets, stack traces,
        signed URLs, or unsafe raw media payloads.
    """
    if not isinstance(metadata, dict):
        raise YouTubeToolContractError("metadata must be a mapping")

    def walk(value: Any, path: str) -> None:
        """Walk nested metadata and reject unsafe public keys.

        :param value: Current metadata value.
        :param path: Dot-separated path to the current value.
        :raises YouTubeToolContractError: If an unsafe key is encountered.
        """
        if isinstance(value, dict):
            for key, nested in value.items():
                if _contains_unsafe_marker(str(key)):
                    raise YouTubeToolContractError(f"unsafe public metadata field: {path}{key}")
                walk(nested, f"{path}{key}.")
        elif isinstance(value, list | tuple):
            for index, nested in enumerate(value):
                walk(nested, f"{path}{index}.")

    walk(metadata, "")
    return metadata


def _quota_phrase(quota_cost: int) -> str:
    """Build the caller-facing quota phrase required in text surfaces.

    :param quota_cost: Official quota-unit cost.
    :return: Text phrase used in descriptions and usage notes.
    """
    return f"Quota cost: {quota_cost}"


def derive_tool_name(resource: str, method: str) -> str:
    """Derive a public YouTube tool name from an upstream resource method.

    :param resource: Upstream YouTube Data API resource name.
    :param method: Upstream YouTube Data API method name.
    :return: Public MCP tool name using the ``resource_method`` pattern.
    :raises YouTubeToolContractError: If either component is empty or would create a
        redundant ``youtube_`` public prefix.
    """
    resource_name = _require_text(resource, "resource")
    method_name = _require_text(method, "method")
    if resource_name.lower().startswith("youtube"):
        raise YouTubeToolContractError("YouTube tool names must not use a youtube_ prefix")
    if "_" in resource_name or "_" in method_name:
        raise YouTubeToolContractError("YouTube tool names must preserve official resource and method casing")
    return f"{resource_name}_{method_name}"


@dataclass(frozen=True)
class YouTubeToolContract:
    """Describe the shared public contract for one YouTube endpoint tool.

    :param tool_name: Public MCP tool name.
    :param upstream_resource: Upstream YouTube Data API resource.
    :param upstream_method: Upstream YouTube Data API method.
    :param operation_key: Stable internal operation identity.
    :param description: Caller-facing description for discovery.
    :param auth_mode: Required credential mode.
    :param quota_cost: Official quota-unit cost.
    :param resource_family: Owning resource-family label.
    :param input_contract: JSON-compatible input contract metadata.
    :param response_convention: JSON-compatible response convention metadata.
    :param response_boundary: JSON-compatible response boundary metadata.
    :param error_categories: Stable safe error categories.
    :param availability_state: Caller-facing endpoint availability state.
    :param usage_notes: Caller-facing notes that include quota and caveats.
    :param caveats: Optional caveat notes visible to callers and reviewers.
    """

    tool_name: str
    upstream_resource: str
    upstream_method: str
    operation_key: str
    description: str
    auth_mode: AuthMode
    quota_cost: int
    resource_family: str
    input_contract: dict[str, Any]
    response_convention: dict[str, Any]
    response_boundary: dict[str, Any]
    error_categories: tuple[str, ...]
    availability_state: AvailabilityState
    usage_notes: tuple[str, ...]
    caveats: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate required contract metadata after dataclass construction.

        :raises YouTubeToolContractError: If any required metadata is missing,
            inconsistent, or unsafe for shared YouTube use.
        """
        for field_name in (
            "tool_name",
            "upstream_resource",
            "upstream_method",
            "operation_key",
            "description",
            "resource_family",
        ):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))

        expected_name = derive_tool_name(self.upstream_resource, self.upstream_method)
        if self.tool_name != expected_name:
            raise YouTubeToolContractError(f"tool_name must be {expected_name}")
        if not isinstance(self.auth_mode, AuthMode):
            raise YouTubeToolContractError("auth_mode must be an AuthMode")
        if not isinstance(self.availability_state, AvailabilityState):
            raise YouTubeToolContractError("availability_state must be an AvailabilityState")
        if not isinstance(self.quota_cost, int) or self.quota_cost < 1:
            raise YouTubeToolContractError("quota_cost must be a positive integer")
        quota_phrase = _quota_phrase(self.quota_cost)
        if quota_phrase not in self.description:
            raise YouTubeToolContractError("description must include official quota cost")
        if not self.usage_notes or not all(isinstance(note, str) and note.strip() for note in self.usage_notes):
            raise YouTubeToolContractError("usage_notes are required")
        if not any(quota_phrase in note for note in self.usage_notes):
            raise YouTubeToolContractError("usage_notes must include official quota cost")
        if not isinstance(self.input_contract, dict) or not self.input_contract:
            raise YouTubeToolContractError("input_contract is required")
        if not isinstance(self.response_convention, dict) or not self.response_convention:
            raise YouTubeToolContractError("response_convention is required")
        if not isinstance(self.response_boundary, dict) or not self.response_boundary:
            raise YouTubeToolContractError("response_boundary is required")
        if not self.error_categories:
            raise YouTubeToolContractError("error_categories are required")
        object.__setattr__(self, "error_categories", tuple(self.error_categories))
        object.__setattr__(self, "usage_notes", tuple(note.strip() for note in self.usage_notes))
        object.__setattr__(self, "caveats", tuple(self.caveats))

    def to_tool_metadata(self) -> dict[str, Any]:
        """Return MCP-facing metadata for discovery and review surfaces.

        :return: JSON-compatible metadata describing the YouTube tool contract.
        """
        return validate_safe_public_metadata(
            {
                "name": self.tool_name,
                "description": self.description,
                "upstream": {
                    "resource": self.upstream_resource,
                    "method": self.upstream_method,
                    "operationKey": self.operation_key,
                },
                "quotaCost": self.quota_cost,
                "authMode": self.auth_mode.value,
                "availabilityState": self.availability_state.value,
                "resourceFamily": self.resource_family,
                "inputContract": self.input_contract,
                "responseConvention": self.response_convention,
                "responseBoundary": self.response_boundary,
                "errorCategories": list(self.error_categories),
                "usageNotes": list(self.usage_notes),
                "caveats": list(self.caveats),
            }
        )
