"""Shared constants for resource-family wrapper validators."""

from __future__ import annotations

_CHANNEL_BANNER_ALLOWED_MIME_TYPES = frozenset({"image/jpeg", "image/png", "application/octet-stream"})
_CHANNEL_BANNER_MAX_BYTES = 6 * 1024 * 1024
_WATERMARK_ALLOWED_MIME_TYPES = frozenset({"image/jpeg", "image/png", "application/octet-stream"})
_WATERMARK_MAX_BYTES = 10 * 1024 * 1024
_CHANNELS_UPDATE_SUPPORTED_PARTS = frozenset({"brandingSettings", "localizations"})
_CHANNEL_SECTIONS_PLAYLIST_TYPES = frozenset({"singlePlaylist", "multiplePlaylists"})
_CHANNEL_SECTIONS_CHANNEL_TYPES = frozenset({"multipleChannels"})
_CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES = frozenset({"multiplePlaylists", "multipleChannels"})
_SEARCH_RESTRICTED_FIELDS = frozenset({"forContentOwner", "forDeveloper", "forMine"})
_SEARCH_VIDEO_ONLY_FIELDS = frozenset(
    {
        "videoCaption",
        "videoDefinition",
        "videoDuration",
        "videoEmbeddable",
        "videoLicense",
        "videoPaidProductPlacement",
        "videoSyndicated",
        "videoType",
    }
)
_VIDEOS_INSERT_UPLOAD_MODES = frozenset({"multipart", "resumable"})
_VIDEOS_REPORT_ABUSE_BODY_FIELDS = frozenset(
    {"videoId", "reasonId", "secondaryReasonId", "comments", "language"}
)

__all__ = [
    "_CHANNEL_BANNER_ALLOWED_MIME_TYPES",
    "_CHANNEL_BANNER_MAX_BYTES",
    "_WATERMARK_ALLOWED_MIME_TYPES",
    "_WATERMARK_MAX_BYTES",
    "_CHANNELS_UPDATE_SUPPORTED_PARTS",
    "_CHANNEL_SECTIONS_PLAYLIST_TYPES",
    "_CHANNEL_SECTIONS_CHANNEL_TYPES",
    "_CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES",
    "_SEARCH_RESTRICTED_FIELDS",
    "_SEARCH_VIDEO_ONLY_FIELDS",
    "_VIDEOS_INSERT_UPLOAD_MODES",
    "_VIDEOS_REPORT_ABUSE_BODY_FIELDS",
]
