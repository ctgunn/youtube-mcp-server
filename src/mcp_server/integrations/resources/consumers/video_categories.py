"""Higher-layer consumer summary methods for video categories resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class VideoCategoriesConsumerMixin:
    """Provide higher-layer summaries for video categories resources."""

    def fetch_video_categories_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videoCategories.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch video categories.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "categoryCount": len(items),
            "isEmpty": not items,
            "selectedSelector": result.get("selectedSelector"),
            "id": result.get("id"),
            "regionCode": result.get("regionCode"),
            "hl": result.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
