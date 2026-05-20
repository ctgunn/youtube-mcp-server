"""Channel section resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    ChannelSectionsDeleteWrapper,
    ChannelSectionsInsertWrapper,
    ChannelSectionsListWrapper,
    ChannelSectionsUpdateWrapper,
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
)

FAMILY_NAME = "channel_sections"
RESOURCE_NAMES = ("channelSections",)
BUILDER_FUNCTIONS = {
    "channelSections.list": build_channel_sections_list_wrapper,
    "channelSections.insert": build_channel_sections_insert_wrapper,
    "channelSections.update": build_channel_sections_update_wrapper,
    "channelSections.delete": build_channel_sections_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelSectionsDeleteWrapper",
    "ChannelSectionsInsertWrapper",
    "ChannelSectionsListWrapper",
    "ChannelSectionsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channel_sections_delete_wrapper",
    "build_channel_sections_insert_wrapper",
    "build_channel_sections_list_wrapper",
    "build_channel_sections_update_wrapper",
]
