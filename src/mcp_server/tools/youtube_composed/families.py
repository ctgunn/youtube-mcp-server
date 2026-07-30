"""Family scaffolding metadata for higher-level YouTube public tools.

This module records where later video, channel, playlist, and transcript slices
should place shared definitions, helpers, examples, caveats, and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mcp_server.tools.youtube_composed.contracts import (
    PLANNED_TOOLS_BY_FAMILY,
    ToolContractError,
    infer_family,
    normalize_family,
)

REPO_ROOT = "/Users/ctgunn/Projects/youtube-mcp-server"
REQUIRED_FAMILIES = ("videos", "channels", "playlists", "transcripts")


@dataclass(frozen=True)
class FamilyScaffolding:
    """Describe where one public YouTube family places shared and future artifacts.

    :param family_name: Owning family name.
    :param public_prefix: Grouped public prefix, such as ``videos_*``.
    :param planned_tools: Planned public tool names owned by the family.
    :param definition_location: Source location for family definitions.
    :param schema_location: Source location for future input schemas.
    :param handler_location: Source location for future composed handlers.
    :param helper_location: Source location for reusable family helpers.
    :param example_location: Source location for representative examples.
    :param test_locations: Test-tier locations for the family.
    :param caveat_location: Location for family-specific caveat notes.
    :param shared_helpers: Shared helper categories owned by the family.
    :param family_caveats: Caveats that apply to the family.
    """

    family_name: str
    public_prefix: str
    planned_tools: tuple[str, ...]
    definition_location: str
    schema_location: str
    handler_location: str
    helper_location: str
    example_location: str
    test_locations: dict[str, str]
    caveat_location: str
    shared_helpers: tuple[str, ...] = field(default_factory=tuple)
    family_caveats: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate family scaffolding metadata.

        :raises ToolContractError: If the family metadata is incomplete
            or disagrees with the planned Layer 3 catalog.
        """
        family = normalize_family(self.family_name)
        if self.family_name not in REQUIRED_FAMILIES:
            raise ToolContractError(f"unsupported public YouTube family: {self.family_name}")
        if self.public_prefix != f"{family.value}_*":
            raise ToolContractError(f"{self.family_name} public prefix must be {family.value}_*")
        expected_tools = PLANNED_TOOLS_BY_FAMILY[family.value]
        if self.planned_tools != expected_tools:
            raise ToolContractError(f"{self.family_name} planned tools do not match the catalog")
        for field_name in (
            "definition_location",
            "schema_location",
            "handler_location",
            "helper_location",
            "example_location",
            "caveat_location",
        ):
            if not getattr(self, field_name):
                raise ToolContractError(f"{field_name} is required")
        if {"unit", "contract", "integration"} - set(self.test_locations):
            raise ToolContractError("unit, contract, and integration test locations are required")

    def to_metadata(self) -> dict[str, object]:
        """Build JSON-compatible family placement metadata.

        :return: Family scaffolding metadata for review and tests.
        """
        return {
            "familyName": self.family_name,
            "publicPrefix": self.public_prefix,
            "plannedTools": list(self.planned_tools),
            "definitionLocation": self.definition_location,
            "schemaLocation": self.schema_location,
            "handlerLocation": self.handler_location,
            "helperLocation": self.helper_location,
            "exampleLocation": self.example_location,
            "testLocations": dict(self.test_locations),
            "caveatLocation": self.caveat_location,
            "sharedHelpers": list(self.shared_helpers),
            "familyCaveats": list(self.family_caveats),
        }


def _family_scaffolding(
    family_name: str,
    *,
    shared_helpers: tuple[str, ...] = (),
    family_caveats: tuple[str, ...] = (),
) -> FamilyScaffolding:
    """Build the standard scaffolding record for one Layer 3 family.

    :param family_name: Owning family name.
    :param shared_helpers: Family-owned helper categories.
    :param family_caveats: Family-level caveat notes.
    :return: Validated family scaffolding record.
    """
    source = f"{REPO_ROOT}/src/mcp_server/tools/youtube_composed/{family_name}.py"
    return FamilyScaffolding(
        family_name=family_name,
        public_prefix=f"{family_name}_*",
        planned_tools=PLANNED_TOOLS_BY_FAMILY[family_name],
        definition_location=source,
        schema_location=source,
        handler_location=source,
        helper_location=source,
        example_location=f"{REPO_ROOT}/src/mcp_server/tools/youtube_composed/examples.py",
        test_locations={
            "unit": f"{REPO_ROOT}/tests/unit/test_youtube_composed_shared_scaffolding.py",
            "contract": f"{REPO_ROOT}/tests/contract/test_youtube_composed_tool_catalog_contract.py",
            "integration": f"{REPO_ROOT}/tests/integration/test_youtube_composed_tool_registration.py",
        },
        caveat_location=source,
        shared_helpers=shared_helpers,
        family_caveats=family_caveats,
    )


FAMILY_SCAFFOLDING: dict[str, FamilyScaffolding] = {
    "videos": _family_scaffolding(
        "videos",
        shared_helpers=("video detail normalization", "video search ranking", "statistics availability"),
        family_caveats=("Hidden or unavailable video counts must be disclosed.",),
    ),
    "channels": _family_scaffolding(
        "channels",
        shared_helpers=("channel normalization", "creator heuristics", "latest-upload enrichment"),
        family_caveats=("Creator classification is inferred and not an upstream fact.",),
    ),
    "playlists": _family_scaffolding(
        "playlists",
        shared_helpers=("playlist item normalization", "playlist search", "transcript fan-out"),
        family_caveats=("Playlist transcript workflows must disclose fan-out bounds.",),
    ),
    "transcripts": _family_scaffolding(
        "transcripts",
        shared_helpers=("language fallback", "caption timing normalization", "transcript text search"),
        family_caveats=("Official caption access may require OAuth authorization.",),
    ),
}


def get_family(family_name: str) -> FamilyScaffolding:
    """Return the scaffolding record for a public YouTube family.

    :param family_name: Family name to look up.
    :return: Matching family scaffolding record.
    :raises ToolContractError: If the family is unknown.
    """
    family = normalize_family(family_name).value
    return FAMILY_SCAFFOLDING[family]


def get_family_for_tool_name(tool_name: str) -> str:
    """Return the owning family name for a planned public tool name.

    :param tool_name: Planned public Layer 3 tool name.
    :return: Owning family name.
    """
    return infer_family(tool_name).value
