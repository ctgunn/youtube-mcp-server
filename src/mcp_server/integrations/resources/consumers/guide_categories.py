"""Higher-layer consumer summary methods for guide categories resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class GuideCategoriesConsumerMixin:
    """Provide higher-layer summaries for guide categories resources."""

    def fetch_guide_categories_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `guideCategories.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch guide categories.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing region use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "guideCategoryCount": len(items),
            "isEmpty": not items,
            "regionCode": arguments.get("regionCode"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceLifecycleState": self.wrapper.metadata.lifecycle_state,
            "sourceCaveatNote": self.wrapper.metadata.caveat_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }
