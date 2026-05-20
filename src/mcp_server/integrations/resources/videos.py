"""Videos resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    VideosDeleteWrapper,
    VideosGetRatingWrapper,
    VideosInsertWrapper,
    VideosListWrapper,
    VideosRateWrapper,
    VideosReportAbuseWrapper,
    VideosUpdateWrapper,
    build_videos_delete_wrapper,
    build_videos_get_rating_wrapper,
    build_videos_insert_wrapper,
    build_videos_list_wrapper,
    build_videos_rate_wrapper,
    build_videos_report_abuse_wrapper,
    build_videos_update_wrapper,
)

FAMILY_NAME = "videos"
RESOURCE_NAMES = ("videos",)
BUILDER_FUNCTIONS = {
    "videos.list": build_videos_list_wrapper,
    "videos.insert": build_videos_insert_wrapper,
    "videos.update": build_videos_update_wrapper,
    "videos.rate": build_videos_rate_wrapper,
    "videos.getRating": build_videos_get_rating_wrapper,
    "videos.reportAbuse": build_videos_report_abuse_wrapper,
    "videos.delete": build_videos_delete_wrapper,
}
RESPONSE_NORMALIZER_KEYS = (
    "videos.list",
    "videos.insert",
    "videos.update",
    "videos.rate",
    "videos.getRating",
    "videos.reportAbuse",
    "videos.delete",
)

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "VideosDeleteWrapper",
    "VideosGetRatingWrapper",
    "VideosInsertWrapper",
    "VideosListWrapper",
    "VideosRateWrapper",
    "VideosReportAbuseWrapper",
    "VideosUpdateWrapper",
    "build_videos_delete_wrapper",
    "build_videos_get_rating_wrapper",
    "build_videos_insert_wrapper",
    "build_videos_list_wrapper",
    "build_videos_rate_wrapper",
    "build_videos_report_abuse_wrapper",
    "build_videos_update_wrapper",
]
