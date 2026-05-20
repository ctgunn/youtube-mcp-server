"""Video abuse report reason resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    VideoAbuseReportReasonsListWrapper,
    build_video_abuse_report_reasons_list_wrapper,
)

FAMILY_NAME = "video_abuse_report_reasons"
RESOURCE_NAMES = ("videoAbuseReportReasons",)
BUILDER_FUNCTIONS = {"videoAbuseReportReasons.list": build_video_abuse_report_reasons_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "VideoAbuseReportReasonsListWrapper",
    "build_video_abuse_report_reasons_list_wrapper",
]
