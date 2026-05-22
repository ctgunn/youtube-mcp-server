"""Higher-layer consumer summary methods for memberships levels resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class MembershipsLevelsConsumerMixin:
    """Provide higher-layer summaries for memberships levels resources."""

    def fetch_memberships_levels_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `membershipsLevels.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch membership levels.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing required request input use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "membershipLevelCount": len(items),
            "isEmpty": not items,
            "part": arguments.get("part"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
