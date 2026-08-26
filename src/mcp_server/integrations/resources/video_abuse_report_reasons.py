"""Video Abuse Report Reasons resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *


@dataclass(frozen=True)
class VideoAbuseReportReasonsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videoAbuseReportReasons.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one localized
    abuse-reason lookup using ``part`` plus ``hl`` on OAuth-authorized requests
    and keeps localization guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videoAbuseReportReasons.list` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videoAbuseReportReasons.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_video_abuse_report_reasons_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videoAbuseReportReasons.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one localized
    abuse-reason lookup through ``part`` plus ``hl`` on OAuth-authorized requests and
    keeps localization guidance visible.

    :return: Representative wrapper configured for `videoAbuseReportReasons.list`.
    """
    metadata = EndpointMetadata(
        resource_name="videoAbuseReportReasons",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/videoAbuseReportReasons",
        request_shape=EndpointRequestShape(
            required_fields=("part", "hl"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        notes=(
            "Requires OAuth authorization plus `part` and optional `hl` for one "
            "deterministic localization lookup, rejects undocumented modifiers, preserves empty result "
            "sets as successful outcomes, and keeps localization guidance "
            "visible for reuse decisions."
        ),
    )
    return VideoAbuseReportReasonsListWrapper(metadata=metadata)

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
