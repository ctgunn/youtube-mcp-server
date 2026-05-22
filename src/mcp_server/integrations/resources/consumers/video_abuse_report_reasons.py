"""Higher-layer consumer summary methods for video abuse report reasons resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class VideoAbuseReportReasonsConsumerMixin:
    """Provide higher-layer summaries for video abuse report reasons resources."""

    def fetch_video_abuse_report_reasons_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videoAbuseReportReasons.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch abuse-report reasons.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing display-language use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "abuseReasonCount": len(items),
            "isEmpty": not items,
            "hl": arguments.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
