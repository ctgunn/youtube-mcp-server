"""Watermarks resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    WatermarksSetWrapper,
    WatermarksUnsetWrapper,
    build_watermarks_set_wrapper,
    build_watermarks_unset_wrapper,
)

FAMILY_NAME = "watermarks"
RESOURCE_NAMES = ("watermarks",)
BUILDER_FUNCTIONS = {
    "watermarks.set": build_watermarks_set_wrapper,
    "watermarks.unset": build_watermarks_unset_wrapper,
}
RESPONSE_NORMALIZER_KEYS = ("watermarks.set", "watermarks.unset")

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "WatermarksSetWrapper",
    "WatermarksUnsetWrapper",
    "build_watermarks_set_wrapper",
    "build_watermarks_unset_wrapper",
]
