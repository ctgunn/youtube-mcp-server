"""Higher-layer consumer summary methods for comments resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class CommentsConsumerMixin:
    """Provide higher-layer summaries for comments resources."""

    def fetch_comments_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch comments.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("id", "parentId")
                if selector in arguments and arguments.get(selector) not in (None, "", [], ())
            ),
            None,
        )
        return {
            "commentCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create one reply comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "commentId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "parentCommentId": snippet.get("parentId"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.update` wrapper result.

        :param arguments: Wrapper arguments needed to update one comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "commentId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedText": snippet.get("textOriginal"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def moderate_comments_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a moderation-status wrapper result.

        :param arguments: Wrapper arguments needed to moderate comments.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing moderation outcome and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "commentIds": tuple(result.get("commentIds", ())),
            "isModerated": bool(result.get("isModerated")),
            "moderationStatus": result.get("moderationStatus"),
            "authorBanApplied": bool(result.get("authorBanApplied")),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.delete` wrapper result.

        :param arguments: Wrapper arguments needed to delete one comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "commentId": result.get("commentId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
