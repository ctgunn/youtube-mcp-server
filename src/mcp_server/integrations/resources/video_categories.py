"""Video category resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import VideoCategoriesListWrapper, build_video_categories_list_wrapper

FAMILY_NAME = "video_categories"
RESOURCE_NAMES = ("videoCategories",)
BUILDER_FUNCTIONS = {"videoCategories.list": build_video_categories_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "VideoCategoriesListWrapper",
    "build_video_categories_list_wrapper",
]
