"""Higher-layer consumer summary methods for comment threads resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class CommentThreadsConsumerMixin:
    """Provide higher-layer summaries for comment threads resources."""

    def fetch_comment_threads_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `commentThreads.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch comment threads.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("videoId", "allThreadsRelatedToChannelId", "id")
                if selector in arguments and arguments.get(selector) not in (None, "", [], ())
            ),
            None,
        )
        return {
            "commentThreadCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_comment_thread_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `commentThreads.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create one comment thread.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created thread identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        top_level_comment = (
            snippet.get("topLevelComment", {}) if isinstance(snippet.get("topLevelComment"), dict) else {}
        )
        return {
            "commentThreadId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "videoId": snippet.get("videoId"),
            "topLevelCommentId": top_level_comment.get("id"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
