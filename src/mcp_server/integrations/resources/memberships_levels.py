"""Memberships level resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import MembershipsLevelsListWrapper, build_memberships_levels_list_wrapper

FAMILY_NAME = "memberships_levels"
RESOURCE_NAMES = ("membershipsLevels",)
BUILDER_FUNCTIONS = {"membershipsLevels.list": build_memberships_levels_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "MembershipsLevelsListWrapper",
    "RESOURCE_NAMES",
    "build_memberships_levels_list_wrapper",
]
