"""Search resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import SearchListWrapper, build_search_list_wrapper

FAMILY_NAME = "search"
RESOURCE_NAMES = ("search",)
BUILDER_FUNCTIONS = {"search.list": build_search_list_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "RESOURCE_NAMES", "SearchListWrapper", "build_search_list_wrapper"]
