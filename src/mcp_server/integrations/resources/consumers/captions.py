"""Higher-layer consumer summary methods for captions resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class CaptionsConsumerMixin:
    """Provide higher-layer summaries for captions resources."""

    def fetch_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch captions.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and result volume.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "captionCount": len(items),
            "isEmpty": not items,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and created caption identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.update` wrapper result.

        :param arguments: Wrapper arguments needed to update a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and updated caption identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def download_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.download` result.

        :param arguments: Wrapper arguments needed to download caption content.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and download outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        content = result.get("content")
        return {
            "captionId": result.get("captionId"),
            "hasContent": isinstance(content, str) and bool(content),
            "contentFormat": result.get("contentFormat"),
            "contentLanguage": result.get("contentLanguage"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.delete` result.

        :param arguments: Wrapper arguments needed to delete a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and delete outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("captionId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
