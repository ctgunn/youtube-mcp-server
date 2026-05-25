"""Shared Layer 2 contract primitives for endpoint-backed MCP tools.

The concrete endpoint tools are implemented in later feature slices. This
module owns only cross-cutting public contract metadata and validation helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Layer2ContractError(ValueError):
    """Raised when shared Layer 2 contract metadata is invalid."""


class AuthMode(Enum):
    """Represent the credential mode declared by a Layer 2 tool contract."""

    API_KEY = "api_key"
    OAUTH_REQUIRED = "oauth_required"
    MIXED = "mixed/conditional"


def _require_text(value: str, field_name: str) -> str:
    """Validate and normalize a required text field.

    :param value: Candidate text value.
    :param field_name: Name of the field being validated.
    :return: The stripped text value.
    :raises Layer2ContractError: If the value is not non-empty text.
    """
    if not isinstance(value, str) or not value.strip():
        raise Layer2ContractError(f"{field_name} is required")
    return value.strip()


def derive_tool_name(resource: str, method: str) -> str:
    """Derive a public Layer 2 tool name from an upstream resource method.

    :param resource: Upstream YouTube Data API resource name.
    :param method: Upstream YouTube Data API method name.
    :return: Public MCP tool name using the ``resource_method`` pattern.
    :raises Layer2ContractError: If either component is empty or would create a
        redundant ``youtube_`` public prefix.
    """
    resource_name = _require_text(resource, "resource")
    method_name = _require_text(method, "method")
    if resource_name.lower().startswith("youtube"):
        raise Layer2ContractError("Layer 2 tool names must not use a youtube_ prefix")
    return f"{resource_name}_{method_name}"


@dataclass(frozen=True)
class Layer2ToolContract:
    """Describe the shared public contract for one Layer 2 endpoint tool.

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
    :param error_categories: Stable safe error categories.
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
    error_categories: tuple[str, ...]
    caveats: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate required contract metadata after dataclass construction.

        :raises Layer2ContractError: If any required metadata is missing,
            inconsistent, or unsafe for shared Layer 2 use.
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
            raise Layer2ContractError(f"tool_name must be {expected_name}")
        if not isinstance(self.auth_mode, AuthMode):
            raise Layer2ContractError("auth_mode must be an AuthMode")
        if not isinstance(self.quota_cost, int) or self.quota_cost < 1:
            raise Layer2ContractError("quota_cost must be a positive integer")
        if not isinstance(self.input_contract, dict) or not self.input_contract:
            raise Layer2ContractError("input_contract is required")
        if not isinstance(self.response_convention, dict) or not self.response_convention:
            raise Layer2ContractError("response_convention is required")
        if not self.error_categories:
            raise Layer2ContractError("error_categories are required")
        object.__setattr__(self, "error_categories", tuple(self.error_categories))
        object.__setattr__(self, "caveats", tuple(self.caveats))

    def to_tool_metadata(self) -> dict[str, Any]:
        """Return MCP-facing metadata for discovery and review surfaces.

        :return: JSON-compatible metadata describing the Layer 2 tool contract.
        """
        return {
            "name": self.tool_name,
            "description": self.description,
            "upstream": {
                "resource": self.upstream_resource,
                "method": self.upstream_method,
                "operationKey": self.operation_key,
            },
            "quotaCost": self.quota_cost,
            "authMode": self.auth_mode.value,
            "resourceFamily": self.resource_family,
            "inputContract": self.input_contract,
            "responseConvention": self.response_convention,
            "errorCategories": list(self.error_categories),
            "caveats": list(self.caveats),
        }
