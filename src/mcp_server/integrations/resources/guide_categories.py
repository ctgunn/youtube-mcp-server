"""Guide category resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import GuideCategoriesListWrapper, build_guide_categories_list_wrapper

FAMILY_NAME = "guide_categories"
RESOURCE_NAMES = ("guideCategories",)
BUILDER_FUNCTIONS = {"guideCategories.list": build_guide_categories_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "GuideCategoriesListWrapper",
    "RESOURCE_NAMES",
    "build_guide_categories_list_wrapper",
]
