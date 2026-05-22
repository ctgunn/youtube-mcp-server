"""Higher-layer consumer summary methods for search resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class SearchConsumerMixin:
    """Provide higher-layer summaries for search resources."""

    def fetch_search_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `search.list` wrapper result.

        :param arguments: Wrapper arguments needed to run search.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing query, result volume, and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "query": arguments.get("q"),
            "resultCount": len(items),
            "isEmpty": not items,
            "searchType": arguments.get("type"),
            "nextPageToken": result.get("nextPageToken"),
            "authPathUsed": result.get("authPath"),
            "queryContext": result.get("queryContext"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceCaveatNote": self.wrapper.metadata.caveat_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }
