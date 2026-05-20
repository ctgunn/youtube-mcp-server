"""Thumbnails resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import ThumbnailsSetWrapper, build_thumbnails_set_wrapper

FAMILY_NAME = "thumbnails"
RESOURCE_NAMES = ("thumbnails",)
BUILDER_FUNCTIONS = {"thumbnails.set": build_thumbnails_set_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "RESOURCE_NAMES", "ThumbnailsSetWrapper", "build_thumbnails_set_wrapper"]
