"""Resource-facing higher-layer consumer for Layer 1 wrappers."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.resources.consumers import (
    ActivitiesConsumerMixin,
    ChannelsConsumerMixin,
    ChannelSectionsConsumerMixin,
    PlaylistsConsumerMixin,
    SearchConsumerMixin,
    SubscriptionsConsumerMixin,
    CommentsConsumerMixin,
    CommentThreadsConsumerMixin,
    GuideCategoriesConsumerMixin,
    LocalizationConsumerMixin,
    VideoAbuseReportReasonsConsumerMixin,
    VideoCategoriesConsumerMixin,
    VideosConsumerMixin,
    MembersConsumerMixin,
    MembershipsLevelsConsumerMixin,
    PlaylistImagesConsumerMixin,
    PlaylistItemsConsumerMixin,
    CaptionsConsumerMixin,
    ChannelBannersConsumerMixin,
    ThumbnailsConsumerMixin,
    WatermarksConsumerMixin,
)
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper


@dataclass(frozen=True)
class RepresentativeHigherLayerConsumer(
    ActivitiesConsumerMixin,
    ChannelsConsumerMixin,
    ChannelSectionsConsumerMixin,
    PlaylistsConsumerMixin,
    SearchConsumerMixin,
    SubscriptionsConsumerMixin,
    CommentsConsumerMixin,
    CommentThreadsConsumerMixin,
    GuideCategoriesConsumerMixin,
    LocalizationConsumerMixin,
    VideoAbuseReportReasonsConsumerMixin,
    VideoCategoriesConsumerMixin,
    VideosConsumerMixin,
    MembersConsumerMixin,
    MembershipsLevelsConsumerMixin,
    PlaylistImagesConsumerMixin,
    PlaylistItemsConsumerMixin,
    CaptionsConsumerMixin,
    ChannelBannersConsumerMixin,
    ThumbnailsConsumerMixin,
    WatermarksConsumerMixin,
):
    """Compose typed Layer 1 wrapper methods in higher-layer workflows.

    :param wrapper: Representative typed wrapper used by the consumer.
    :param executor: Shared request executor used for wrapper calls.
    """

    wrapper: RepresentativeEndpointWrapper
    executor: IntegrationExecutor


__all__ = ["RepresentativeHigherLayerConsumer"]
