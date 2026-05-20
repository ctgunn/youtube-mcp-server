"""Channel banner resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import ChannelBannersInsertWrapper, build_channel_banners_insert_wrapper

FAMILY_NAME = "channel_banners"
RESOURCE_NAMES = ("channelBanners",)
BUILDER_FUNCTIONS = {"channelBanners.insert": build_channel_banners_insert_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelBannersInsertWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channel_banners_insert_wrapper",
]
