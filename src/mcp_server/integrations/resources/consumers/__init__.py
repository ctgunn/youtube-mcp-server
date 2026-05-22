"""Resource-family higher-layer consumer mixins."""

from __future__ import annotations

from mcp_server.integrations.resources.consumers.activities import ActivitiesConsumerMixin
from mcp_server.integrations.resources.consumers.channels import ChannelsConsumerMixin
from mcp_server.integrations.resources.consumers.channel_sections import ChannelSectionsConsumerMixin
from mcp_server.integrations.resources.consumers.playlists import PlaylistsConsumerMixin
from mcp_server.integrations.resources.consumers.search import SearchConsumerMixin
from mcp_server.integrations.resources.consumers.subscriptions import SubscriptionsConsumerMixin
from mcp_server.integrations.resources.consumers.comments import CommentsConsumerMixin
from mcp_server.integrations.resources.consumers.comment_threads import CommentThreadsConsumerMixin
from mcp_server.integrations.resources.consumers.guide_categories import GuideCategoriesConsumerMixin
from mcp_server.integrations.resources.consumers.localization import LocalizationConsumerMixin
from mcp_server.integrations.resources.consumers.video_abuse_report_reasons import VideoAbuseReportReasonsConsumerMixin
from mcp_server.integrations.resources.consumers.video_categories import VideoCategoriesConsumerMixin
from mcp_server.integrations.resources.consumers.videos import VideosConsumerMixin
from mcp_server.integrations.resources.consumers.members import MembersConsumerMixin
from mcp_server.integrations.resources.consumers.memberships_levels import MembershipsLevelsConsumerMixin
from mcp_server.integrations.resources.consumers.playlist_images import PlaylistImagesConsumerMixin
from mcp_server.integrations.resources.consumers.playlist_items import PlaylistItemsConsumerMixin
from mcp_server.integrations.resources.consumers.captions import CaptionsConsumerMixin
from mcp_server.integrations.resources.consumers.channel_banners import ChannelBannersConsumerMixin
from mcp_server.integrations.resources.consumers.thumbnails import ThumbnailsConsumerMixin
from mcp_server.integrations.resources.consumers.watermarks import WatermarksConsumerMixin

__all__ = [
    "ActivitiesConsumerMixin",
    "ChannelsConsumerMixin",
    "ChannelSectionsConsumerMixin",
    "PlaylistsConsumerMixin",
    "SearchConsumerMixin",
    "SubscriptionsConsumerMixin",
    "CommentsConsumerMixin",
    "CommentThreadsConsumerMixin",
    "GuideCategoriesConsumerMixin",
    "LocalizationConsumerMixin",
    "VideoAbuseReportReasonsConsumerMixin",
    "VideoCategoriesConsumerMixin",
    "VideosConsumerMixin",
    "MembersConsumerMixin",
    "MembershipsLevelsConsumerMixin",
    "PlaylistImagesConsumerMixin",
    "PlaylistItemsConsumerMixin",
    "CaptionsConsumerMixin",
    "ChannelBannersConsumerMixin",
    "ThumbnailsConsumerMixin",
    "WatermarksConsumerMixin",
]
