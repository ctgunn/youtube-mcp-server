"""Higher-layer consumer summary methods for members resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class MembersConsumerMixin:
    """Provide higher-layer summaries for members resources."""

    def fetch_members_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `members.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch membership records.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing membership mode use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "memberCount": len(items),
            "isEmpty": not items,
            "mode": arguments.get("mode"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
