"""Channels resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    ChannelsListWrapper,
    ChannelsUpdateWrapper,
    build_channels_list_wrapper,
    build_channels_update_wrapper,
)

FAMILY_NAME = "channels"
RESOURCE_NAMES = ("channels",)
BUILDER_FUNCTIONS = {
    "channels.list": build_channels_list_wrapper,
    "channels.update": build_channels_update_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelsListWrapper",
    "ChannelsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channels_list_wrapper",
    "build_channels_update_wrapper",
]
