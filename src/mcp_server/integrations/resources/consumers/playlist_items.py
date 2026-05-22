"""Higher-layer consumer summary methods for playlist items resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class PlaylistItemsConsumerMixin:
    """Provide higher-layer summaries for playlist items resources."""

    def fetch_playlist_items_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistItems.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch playlist items.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("playlistId", "id")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "playlistItemCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_playlist_item_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistItems.insert` result.

        :param arguments: Wrapper arguments needed to create a playlist item.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and create outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        body_resource = body_snippet.get("resourceId", {}) if isinstance(body_snippet, dict) else {}
        snippet = result.get("snippet")
        snippet_resource = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
        return {
            "playlistItemId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "videoId": (
                result.get("videoId")
                or (snippet_resource.get("videoId") if isinstance(snippet_resource, dict) else None)
                or body_resource.get("videoId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_playlist_item_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistItems.update` result.

        :param arguments: Wrapper arguments needed to update a playlist item.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        body_resource = body_snippet.get("resourceId", {}) if isinstance(body_snippet, dict) else {}
        snippet = result.get("snippet")
        snippet_resource = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
        return {
            "playlistItemId": result.get("playlistItemId") or result.get("id"),
            "isUpdated": bool(result.get("playlistItemId") or result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "videoId": (
                result.get("videoId")
                or (snippet_resource.get("videoId") if isinstance(snippet_resource, dict) else None)
                or body_resource.get("videoId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_playlist_item_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistItems.delete` result.

        :param arguments: Wrapper arguments needed to delete a playlist item.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted playlist-item identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "playlistItemId": result.get("playlistItemId"),
            "isDeleted": bool(result.get("isDeleted")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
