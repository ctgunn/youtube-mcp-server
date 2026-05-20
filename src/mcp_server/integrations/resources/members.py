"""Members resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import MembersListWrapper, build_members_list_wrapper

FAMILY_NAME = "members"
RESOURCE_NAMES = ("members",)
BUILDER_FUNCTIONS = {"members.list": build_members_list_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "MembersListWrapper", "RESOURCE_NAMES", "build_members_list_wrapper"]
