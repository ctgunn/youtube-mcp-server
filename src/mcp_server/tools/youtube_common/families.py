"""Resource-family scaffolding for future YouTube tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.tools.youtube_common.contracts import YouTubeToolContract


SHARED_YOUTUBE_HELPER_BOUNDARY = {
    "shared": (
        "naming",
        "auth_quota_metadata",
        "input_conventions",
        "response_conventions",
        "safe_error_categories",
        "representative_descriptors",
    ),
    "endpoint_family": (
        "upstream_execution",
        "media_transfer",
        "endpoint_request_body",
        "endpoint_specific_caveats",
    ),
}

REQUIRED_YOUTUBE_RESOURCE_FAMILIES: tuple[str, ...] = (
    "activities",
    "captions",
    "channel_banners",
    "channels",
    "channel_sections",
    "comments",
    "comment_threads",
    "guide_categories",
    "localization",
    "members",
    "memberships_levels",
    "playlist_images",
    "playlist_items",
    "playlists",
    "search",
    "subscriptions",
    "thumbnails",
    "video_abuse_report_reasons",
    "video_categories",
    "videos",
    "watermarks",
)


@dataclass(frozen=True)
class YouTubeResourceFamily:
    """Describe resource-family placement for future YouTube endpoint tools.

    :param family_name: Stable resource-family label.
    :param definition_location: Expected tool definition module path.
    :param handler_location: Expected endpoint handler module path.
    :param schema_location: Expected schema or input contract module path.
    :param test_locations: Expected test locations by test level.
    :param documentation_location: Expected documentation or caveat location.
    :param layer1_dependency: Layer 1 resource-family module dependency.
    """

    family_name: str
    definition_location: str
    handler_location: str
    schema_location: str
    test_locations: dict[str, str]
    documentation_location: str
    layer1_dependency: str


def _family_module_name(family_name: str) -> str:
    """Return the module-friendly name for a YouTube resource family.

    :param family_name: Resource-family label.
    :return: Python module name for the family.
    """
    return family_name


def _build_family(family_name: str) -> YouTubeResourceFamily:
    """Build placement metadata for one YouTube resource family.

    :param family_name: Resource-family label.
    :return: Resource-family placement metadata.
    """
    module_name = _family_module_name(family_name)
    base = "/Users/ctgunn/Projects/youtube-mcp-server"
    return YouTubeResourceFamily(
        family_name=family_name,
        definition_location=f"{base}/src/mcp_server/tools/youtube_common/{module_name}.py",
        handler_location=f"{base}/src/mcp_server/tools/youtube_common/{module_name}.py",
        schema_location=f"{base}/src/mcp_server/tools/youtube_common/{module_name}.py",
        test_locations={
            "unit": f"{base}/tests/unit/test_youtube_{module_name}.py",
            "contract": f"{base}/tests/contract/test_youtube_{module_name}_contract.py",
            "integration": f"{base}/tests/integration/test_youtube_{module_name}_registration.py",
        },
        documentation_location=f"{base}/specs/{{slice}}/contracts/youtube-{module_name}-contract.md",
        layer1_dependency=f"mcp_server.integrations.resources.{module_name}",
    )


RESOURCE_FAMILY_REGISTRY: dict[str, YouTubeResourceFamily] = {
    family_name: _build_family(family_name) for family_name in REQUIRED_YOUTUBE_RESOURCE_FAMILIES
}


def get_resource_family(family_name: str) -> YouTubeResourceFamily:
    """Look up YouTube tool placement metadata for a resource family.

    :param family_name: Resource-family label.
    :return: Resource-family placement metadata.
    :raises KeyError: If the family is not part of the required shared YouTube set.
    """
    return RESOURCE_FAMILY_REGISTRY[family_name]


def _representative_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a non-executing representative result for registration tests.

    :param arguments: Validated tool call arguments.
    :return: Representative result proving descriptor registration only.
    """
    return {"representativeOnly": True, "arguments": arguments}


def build_representative_tool_descriptor(contract: YouTubeToolContract) -> dict[str, Any]:
    """Build a dispatcher descriptor without adding endpoint execution.

    :param contract: Representative YouTube tool contract.
    :return: Descriptor compatible with the existing in-memory dispatcher.
    """
    return {
        "name": contract.tool_name,
        "description": contract.description,
        "metadata": contract.to_tool_metadata(),
        "inputSchema": {
            "type": "object",
            "required": list(contract.input_contract.get("required", [])),
            "properties": contract.input_contract.get("properties", {}),
            "additionalProperties": False,
        },
        "handler": _representative_handler,
    }
