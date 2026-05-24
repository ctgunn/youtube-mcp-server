"""Resource-family response normalizer registry."""

from __future__ import annotations

from collections.abc import Mapping

from mcp_server.integrations.resources.response_normalizers import (
    captions,
    channel_sections,
    channel_banners,
    thumbnails,
    watermarks,
    videos,
    playlist_images,
    playlist_items,
    playlists,
    subscriptions,
    comments,
    comment_threads,
    guide_categories,
    localization,
    video_abuse_report_reasons,
    video_categories,
    members,
    memberships_levels,
    search,
    channels,
)
from mcp_server.integrations.resources.response_normalizers.base import (
    ResponseNormalizer,
    build_response_normalizer_registry,
    normalize_youtube_response,
)

DEFAULT_RESPONSE_NORMALIZERS = (
    *captions.NORMALIZERS,
    *channel_sections.NORMALIZERS,
    *channel_banners.NORMALIZERS,
    *thumbnails.NORMALIZERS,
    *watermarks.NORMALIZERS,
    *videos.NORMALIZERS,
    *playlist_images.NORMALIZERS,
    *playlist_items.NORMALIZERS,
    *playlists.NORMALIZERS,
    *subscriptions.NORMALIZERS,
    *comments.NORMALIZERS,
    *comment_threads.NORMALIZERS,
    *guide_categories.NORMALIZERS,
    *localization.NORMALIZERS,
    *video_abuse_report_reasons.NORMALIZERS,
    *video_categories.NORMALIZERS,
    *members.NORMALIZERS,
    *memberships_levels.NORMALIZERS,
    *search.NORMALIZERS,
    *channels.NORMALIZERS,
)


def default_response_normalizer_registry() -> Mapping[str, ResponseNormalizer]:
    """Return the default operation-key response normalizer registry.

    :return: Mapping used by the shared YouTube transport to normalize endpoint payloads.
    """
    return build_response_normalizer_registry(DEFAULT_RESPONSE_NORMALIZERS)


__all__ = [
    "DEFAULT_RESPONSE_NORMALIZERS",
    "ResponseNormalizer",
    "build_response_normalizer_registry",
    "default_response_normalizer_registry",
    "normalize_youtube_response",
]
