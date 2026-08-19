"""Shared parameter, response, heuristic, and composition conventions.

The conventions in this module are safe metadata surfaces used by later
higher-level YouTube tools. They do not perform hosted transport, persistence,
or upstream YouTube execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from mcp_server.tools.youtube_composed.contracts import (
    ToolContractError,
    validate_tool_name,
)


class Requiredness(Enum):
    """Represent how a shared public YouTube parameter applies to a tool."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"
    FAMILY_SPECIFIC = "family_specific"


class ResponseFieldCategory(Enum):
    """Represent the provenance category for a higher-level YouTube response field."""

    RAW_UPSTREAM = "raw_upstream"
    NORMALIZED = "normalized"
    HEURISTIC_INFERRED = "heuristic_inferred"


class CompositionKind(Enum):
    """Represent the amount of higher-level behavior in a public YouTube tool."""

    DIRECT_RETRIEVAL = "direct_retrieval"
    NORMALIZED_RETRIEVAL = "normalized_retrieval"
    MULTI_RESOURCE_COMPOSITION = "multi_resource_composition"
    ENRICHMENT = "enrichment"
    SERVER_SIDE_FILTERING = "server_side_filtering"
    RANKING = "ranking"
    RANKED_ENRICHMENT = "ranked_enrichment"
    TRANSCRIPT_RETRIEVAL = "transcript_retrieval"
    FAN_OUT = "fan_out"


class ErrorCategory(Enum):
    """Represent stable safe error categories for public YouTube contracts."""

    INVALID_PARAMETERS = "invalid_parameters"
    UNAVAILABLE_RESOURCE = "unavailable_resource"
    AUTHORIZATION_SENSITIVE_DATA = "authorization_sensitive_data"
    QUOTA_EXHAUSTION = "quota_exhaustion"
    UPSTREAM_FAILURE = "upstream_failure"
    PARTIAL_ENRICHMENT_FAILURE = "partial_enrichment_failure"
    TRANSCRIPT_UNAVAILABLE = "transcript_unavailable"
    FAN_OUT_LIMIT_REACHED = "fan_out_limit_reached"
    UNSUPPORTED_FILTER_OR_SORT = "unsupported_filter_or_sort"
    NO_MATCHING_RESULTS = "no_matching_results"


def _require_text(value: str, field_name: str) -> str:
    """Validate and normalize required convention text.

    :param value: Candidate text value.
    :param field_name: Name of the field being validated.
    :return: The stripped text value.
    :raises ToolContractError: If the value is not non-empty text.
    """
    if not isinstance(value, str) or not value.strip():
        raise ToolContractError(f"{field_name} is required")
    return value.strip()


def _enum_value(value: Enum | str, enum_type: type[Enum], field_name: str) -> str:
    """Normalize enum or text values to their public string form.

    :param value: Candidate enum member or string.
    :param enum_type: Enum type to validate against.
    :param field_name: Name of the field being validated.
    :return: Public string value.
    :raises ToolContractError: If the value does not belong to the enum.
    """
    if not isinstance(value, str):
        if isinstance(value, enum_type):
            return str(value.value)
        raise ToolContractError(f"unsupported {field_name}: {value}")
    text = _require_text(value, field_name)
    if text not in {member.value for member in enum_type}:
        raise ToolContractError(f"unsupported {field_name}: {text}")
    return text


@dataclass(frozen=True)
class SharedParameterConvention:
    """Describe a reusable caller-facing public YouTube parameter rule.

    :param name: Stable MCP-facing parameter name.
    :param value_kind: Expected user-facing value type or shape.
    :param requiredness: Requiredness classification.
    :param default_behavior: Caller-facing default behavior.
    :param bounds: Accepted bounds or value set metadata.
    :param validation_behavior: User-facing invalid-value behavior.
    :param applicable_families: Families or workflows where this applies.
    :param upstream_mapping_notes: Optional lower-layer mapping notes.
    """

    name: str
    value_kind: str
    requiredness: Requiredness | str
    default_behavior: str
    bounds: dict[str, Any]
    validation_behavior: str
    applicable_families: tuple[str, ...]
    upstream_mapping_notes: str = ""

    def __post_init__(self) -> None:
        """Validate the shared parameter convention.

        :raises ToolContractError: If required convention metadata is missing.
        """
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        object.__setattr__(self, "value_kind", _require_text(self.value_kind, "value_kind"))
        object.__setattr__(self, "requiredness", _enum_value(self.requiredness, Requiredness, "requiredness"))
        object.__setattr__(self, "default_behavior", _require_text(self.default_behavior, "default_behavior"))
        object.__setattr__(self, "validation_behavior", _require_text(self.validation_behavior, "validation_behavior"))
        if not self.applicable_families:
            raise ToolContractError("applicable_families are required")
        if self.name in {"maxResults", "maxMatches", "sampleVideosPerChannel"} and not self.bounds:
            raise ToolContractError(f"{self.name} requires explicit bounds")
        if "date" in self.value_kind.lower() and "iso 8601" not in self.validation_behavior.lower():
            raise ToolContractError(f"{self.name} requires ISO 8601 validation behavior")

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible metadata for this parameter convention.

        :return: Shared parameter convention metadata.
        """
        return {
            "name": self.name,
            "valueKind": self.value_kind,
            "requiredness": self.requiredness,
            "defaultBehavior": self.default_behavior,
            "bounds": self.bounds,
            "validationBehavior": self.validation_behavior,
            "applicableFamilies": list(self.applicable_families),
            "upstreamMappingNotes": self.upstream_mapping_notes,
        }


@dataclass(frozen=True)
class ResponseFieldProvenance:
    """Describe the provenance of a representative public YouTube response field.

    :param field_name: Public result field name.
    :param category: Field provenance category.
    :param source: Upstream, normalization, or inference source.
    :param caller_guidance: Caller-facing interpretation guidance.
    :param limitations: Caveats for missing, hidden, partial, or inferred values.
    """

    field_name: str
    category: ResponseFieldCategory | str
    source: str
    caller_guidance: str
    limitations: str = ""

    def __post_init__(self) -> None:
        """Validate response field provenance metadata.

        :raises ToolContractError: If required provenance metadata is missing.
        """
        object.__setattr__(self, "field_name", _require_text(self.field_name, "field_name"))
        object.__setattr__(self, "category", _enum_value(self.category, ResponseFieldCategory, "category"))
        object.__setattr__(self, "source", _require_text(self.source, "source"))
        object.__setattr__(self, "caller_guidance", _require_text(self.caller_guidance, "caller_guidance"))
        if self.category == ResponseFieldCategory.HEURISTIC_INFERRED.value:
            object.__setattr__(self, "limitations", _require_text(self.limitations, "limitations"))

    def to_metadata(self) -> dict[str, str]:
        """Build JSON-compatible response provenance metadata.

        :return: Response field provenance metadata.
        """
        return {
            "fieldName": self.field_name,
            "category": _enum_value(self.category, ResponseFieldCategory, "category"),
            "source": self.source,
            "callerGuidance": self.caller_guidance,
            "limitations": self.limitations,
        }


@dataclass(frozen=True)
class HeuristicDisclosure:
    """Describe a required disclosure for an inferred public YouTube field.

    :param name: Heuristic field or signal name.
    :param basis: Signals or evidence used to infer the value.
    :param limitations: Uncertainty or false-positive risks.
    :param applicable_tools: Planned tools where the heuristic can appear.
    :param safe_usage_guidance: Caller-facing guidance for safe use.
    """

    name: str
    basis: str
    limitations: str
    applicable_tools: tuple[str, ...]
    safe_usage_guidance: str

    def __post_init__(self) -> None:
        """Validate heuristic disclosure metadata.

        :raises ToolContractError: If required disclosure metadata is missing.
        """
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        object.__setattr__(self, "basis", _require_text(self.basis, "basis"))
        object.__setattr__(self, "limitations", _require_text(self.limitations, "limitations"))
        object.__setattr__(self, "safe_usage_guidance", _require_text(self.safe_usage_guidance, "safe_usage_guidance"))
        if not self.applicable_tools:
            raise ToolContractError("applicable_tools are required")
        for tool_name in self.applicable_tools:
            validate_tool_name(tool_name)

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible heuristic disclosure metadata.

        :return: Heuristic disclosure metadata.
        """
        return {
            "name": self.name,
            "basis": self.basis,
            "limitations": self.limitations,
            "applicableTools": list(self.applicable_tools),
            "safeUsageGuidance": self.safe_usage_guidance,
        }


@dataclass(frozen=True)
class RankingFilteringRule:
    """Describe shared ranking or filtering behavior for public YouTube tools.

    :param name: Public rule or parameter name.
    :param semantics: Caller-facing behavior.
    :param allowed_values: Accepted values where applicable.
    :param default_behavior: Behavior when omitted.
    :param applicable_families: Families or workflows where the rule applies.
    :param dependency_notes: Lower-layer data needed to apply the rule.
    :param partial_data_behavior: Behavior when dependency data is missing.
    """

    name: str
    semantics: str
    allowed_values: tuple[str, ...]
    default_behavior: str
    applicable_families: tuple[str, ...]
    dependency_notes: str
    partial_data_behavior: str

    def __post_init__(self) -> None:
        """Validate ranking and filtering rule metadata.

        :raises ToolContractError: If required rule metadata is missing.
        """
        for field_name in (
            "name",
            "semantics",
            "default_behavior",
            "dependency_notes",
            "partial_data_behavior",
        ):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))
        if not self.applicable_families:
            raise ToolContractError("applicable_families are required")

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible ranking or filtering metadata.

        :return: Ranking or filtering rule metadata.
        """
        return {
            "name": self.name,
            "semantics": self.semantics,
            "allowedValues": list(self.allowed_values),
            "defaultBehavior": self.default_behavior,
            "applicableFamilies": list(self.applicable_families),
            "dependencyNotes": self.dependency_notes,
            "partialDataBehavior": self.partial_data_behavior,
        }


@dataclass(frozen=True)
class CompositionBoundary:
    """Describe how much higher-level behavior a public YouTube tool performs.

    :param kind: Composition boundary kind.
    :param lower_layer_dependencies: Lower-layer resources or contracts involved.
    :param quota_behavior: How quota is exposed to callers.
    :param auth_sensitivity: Whether authorization-sensitive data is involved.
    :param partial_result_policy: Partial-data behavior.
    :param boundedness: Result, fan-out, or sample bounds.
    :param caller_caveats: User-visible caveat notes.
    """

    kind: CompositionKind | str
    lower_layer_dependencies: tuple[str, ...]
    quota_behavior: str
    auth_sensitivity: str
    partial_result_policy: str
    boundedness: str
    caller_caveats: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate composition-boundary metadata.

        :raises ToolContractError: If required boundary metadata is missing.
        """
        object.__setattr__(self, "kind", _enum_value(self.kind, CompositionKind, "kind"))
        for field_name in ("quota_behavior", "auth_sensitivity", "partial_result_policy", "boundedness"):
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name))
        if not self.lower_layer_dependencies:
            raise ToolContractError("lower_layer_dependencies are required")

    def to_metadata(self) -> dict[str, Any]:
        """Build JSON-compatible composition-boundary metadata.

        :return: Composition-boundary metadata for public contracts.
        """
        return {
            "kind": self.kind,
            "lowerLayerDependencies": list(self.lower_layer_dependencies),
            "quotaBehavior": self.quota_behavior,
            "authSensitivity": self.auth_sensitivity,
            "partialResultPolicy": self.partial_result_policy,
            "boundedness": self.boundedness,
            "callerCaveats": list(self.caller_caveats),
        }
