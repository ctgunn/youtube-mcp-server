"""Shared public contract primitives for higher-level YouTube tools.

This module owns only shared, representative contract metadata for the Layer 3
public catalog. Concrete public tool execution belongs to later YT-302+ slices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

SHARED_HELPER_BOUNDARY = "representative_contracts_only"
CONCRETE_TOOL_EXECUTION_ENABLED = False

UNSAFE_METADATA_MARKERS = (
    "api_key",
    "apikey",
    "oauth",
    "secret",
    "stack",
    "credential",
    "raw_media",
    "raw_request",
    "raw_body",
    "signed_url",
    "signedurl",
)
SAFE_TOKEN_FIELDS = ("nextpagetoken", "prevpagetoken", "pagetoken", "continuationtoken")


class ToolContractError(ValueError):
    """Raised when shared public YouTube contract metadata is invalid."""


class ToolFamily(Enum):
    """Represent the grouped public YouTube tool families."""

    VIDEOS = "videos"
    CHANNELS = "channels"
    PLAYLISTS = "playlists"
    TRANSCRIPTS = "transcripts"


PLANNED_TOOLS_BY_FAMILY: dict[str, tuple[str, ...]] = {
    ToolFamily.VIDEOS.value: (
        "videos_getVideo",
        "videos_searchVideos",
        "videos_getStatistics",
    ),
    ToolFamily.TRANSCRIPTS.value: (
        "transcripts_getTranscript",
        "transcripts_listLanguages",
        "transcripts_getTimestampedCaptions",
        "transcripts_searchTranscript",
    ),
    ToolFamily.CHANNELS.value: (
        "channels_getChannel",
        "channels_getChannels",
        "channels_searchChannels",
        "channels_findCreators",
        "channels_listVideos",
        "channels_listPlaylists",
        "channels_getStatistics",
        "channels_searchContent",
    ),
    ToolFamily.PLAYLISTS.value: (
        "playlists_getPlaylist",
        "playlists_getPlaylistItems",
        "playlists_searchItems",
        "playlists_getVideoTranscripts",
    ),
}

PLANNED_TOOL_NAMES: tuple[str, ...] = tuple(
    tool_name for tool_names in PLANNED_TOOLS_BY_FAMILY.values() for tool_name in tool_names
)


def _require_text(value: str, field_name: str) -> str:
    """Validate and normalize a required text field.

    :param value: Candidate text value.
    :param field_name: Name of the field being validated.
    :return: The stripped text value.
    :raises ToolContractError: If the value is not non-empty text.
    """
    if not isinstance(value, str) or not value.strip():
        raise ToolContractError(f"{field_name} is required")
    return value.strip()


def normalize_family(family: ToolFamily | str) -> ToolFamily:
    """Normalize a family value to the shared public YouTube family enum.

    :param family: Candidate family enum or string.
    :return: Matching :class:`ToolFamily`.
    :raises ToolContractError: If the family is not supported.
    """
    if isinstance(family, ToolFamily):
        return family
    value = _require_text(family, "family")
    try:
        return ToolFamily(value)
    except ValueError as exc:
        raise ToolContractError(f"unsupported public YouTube family: {value}") from exc


def validate_tool_name(tool_name: str, family: ToolFamily | str | None = None) -> str:
    """Validate a grouped public YouTube tool name.

    :param tool_name: Candidate public tool name.
    :param family: Optional expected family for the tool.
    :return: The validated public tool name.
    :raises ToolContractError: If the name is outside the planned catalog
        or does not match the expected grouped family.
    """
    name = _require_text(tool_name, "tool_name")
    if name.startswith("youtube_"):
        raise ToolContractError("Public YouTube tool names must not use a youtube_ prefix")
    if name not in PLANNED_TOOL_NAMES:
        raise ToolContractError(f"unsupported public YouTube tool name: {name}")
    if family is not None:
        normalized_family = normalize_family(family)
        expected_names = PLANNED_TOOLS_BY_FAMILY[normalized_family.value]
        if name not in expected_names:
            raise ToolContractError(f"{name} does not belong to {normalized_family.value}")
    return name


def infer_family(tool_name: str) -> ToolFamily:
    """Infer a public YouTube family from a planned public tool name.

    :param tool_name: Planned public Layer 3 tool name.
    :return: Owning Layer 3 family.
    :raises ToolContractError: If the name is not in the planned catalog.
    """
    name = validate_tool_name(tool_name)
    for family, names in PLANNED_TOOLS_BY_FAMILY.items():
        if name in names:
            return ToolFamily(family)
    raise ToolContractError(f"unable to infer family for {name}")


def _contains_unsafe_marker(key: str) -> bool:
    """Return whether a metadata key looks unsafe for public exposure.

    :param key: Metadata key to inspect.
    :return: True when the key suggests secret or unsafe diagnostic content.
    """
    normalized = key.lower().replace("-", "_")
    compact = normalized.replace("_", "")
    if "token" in compact and compact not in SAFE_TOKEN_FIELDS:
        return True
    return any(
        marker in normalized or marker.replace("_", "") in compact
        for marker in UNSAFE_METADATA_MARKERS
    )


def validate_safe_public_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate public YouTube metadata before discovery exposure.

    :param metadata: JSON-compatible metadata intended for public surfaces.
    :return: The original metadata mapping when it contains no unsafe keys.
    :raises ToolContractError: If a key suggests secrets, stack traces,
        signed URLs, or unsafe raw media payloads.
    """
    if not isinstance(metadata, dict):
        raise ToolContractError("metadata must be a mapping")

    def walk(value: Any, path: str) -> None:
        """Walk nested metadata and reject unsafe public keys.

        :param value: Current metadata value.
        :param path: Dot-separated path to the current value.
        :raises ToolContractError: If an unsafe key is encountered.
        """
        if isinstance(value, dict):
            for key, nested in value.items():
                if _contains_unsafe_marker(str(key)):
                    raise ToolContractError(f"unsafe public metadata field: {path}{key}")
                walk(nested, f"{path}{key}.")
        elif isinstance(value, list | tuple):
            for index, nested in enumerate(value):
                walk(nested, f"{path}{index}.")

    walk(metadata, "")
    return metadata


@dataclass(frozen=True)
class ToolContract:
    """Describe the shared public contract for one higher-level YouTube tool.

    :param tool_name: Grouped public YouTube tool name.
    :param family: Owning public YouTube tool family.
    :param description: Caller-facing summary.
    :param parameters: Shared parameter convention names used by the tool.
    :param response_fields: Field provenance metadata.
    :param composition_boundary: Composition and boundedness metadata.
    :param lower_layer_dependencies: Lower-layer operations or contracts used.
    :param auth_and_quota_notes: User-visible auth and quota notes.
    :param partial_result_policy: User-visible partial-result behavior.
    :param error_categories: Safe caller-facing error categories.
    :param review_evidence: Review evidence identifiers for this contract.
    :param ranking_and_filtering: Optional ranking or filtering rule names.
    :param heuristics: Optional heuristic disclosure metadata.
    :param caveats: Optional caller-facing caveats.
    """

    tool_name: str
    family: ToolFamily | str
    description: str
    parameters: tuple[str, ...]
    response_fields: tuple[dict[str, Any], ...]
    composition_boundary: dict[str, Any]
    lower_layer_dependencies: tuple[str, ...]
    auth_and_quota_notes: tuple[str, ...]
    partial_result_policy: str
    error_categories: tuple[str, ...]
    review_evidence: tuple[str, ...]
    ranking_and_filtering: tuple[str, ...] = field(default_factory=tuple)
    heuristics: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    caveats: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate contract metadata after dataclass construction.

        :raises ToolContractError: If required metadata is missing,
            inconsistent, or unsafe for public Layer 3 use.
        """
        normalized_family = normalize_family(self.family)
        object.__setattr__(self, "family", normalized_family)
        object.__setattr__(self, "tool_name", validate_tool_name(self.tool_name, normalized_family))
        object.__setattr__(self, "description", _require_text(self.description, "description"))
        object.__setattr__(
            self,
            "partial_result_policy",
            _require_text(self.partial_result_policy, "partial_result_policy"),
        )

        for field_name in (
            "parameters",
            "response_fields",
            "composition_boundary",
            "lower_layer_dependencies",
            "auth_and_quota_notes",
            "error_categories",
            "review_evidence",
        ):
            if not getattr(self, field_name):
                raise ToolContractError(f"{field_name} is required")
        validate_safe_public_metadata(self.to_tool_metadata(validate=False))

    def to_tool_metadata(self, *, validate: bool = True) -> dict[str, Any]:
        """Return MCP-facing metadata for discovery and review surfaces.

        :param validate: Whether to validate unsafe metadata keys before return.
        :return: JSON-compatible metadata for the representative contract.
        """
        metadata = {
            "name": self.tool_name,
            "family": self.family.value,
            "description": self.description,
            "parameters": list(self.parameters),
            "responseFields": list(self.response_fields),
            "compositionBoundary": self.composition_boundary,
            "lowerLayerDependencies": list(self.lower_layer_dependencies),
            "authAndQuotaNotes": list(self.auth_and_quota_notes),
            "partialResultPolicy": self.partial_result_policy,
            "errorCategories": list(self.error_categories),
            "reviewEvidence": list(self.review_evidence),
            "rankingAndFiltering": list(self.ranking_and_filtering),
            "heuristics": list(self.heuristics),
            "caveats": list(self.caveats),
            "representativeOnly": True,
        }
        if validate:
            return validate_safe_public_metadata(metadata)
        return metadata
