"""Higher-layer consumer summary methods for activities resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class ActivitiesConsumerMixin:
    """Provide higher-layer summaries for activities resources."""

    def fetch_activity_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `activities.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch activities.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and result volume.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "activityCount": len(items),
            "isEmpty": not items,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
        }
