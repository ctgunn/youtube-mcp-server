"""Higher-layer consumer summary methods for playlist images resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class PlaylistImagesConsumerMixin:
    """Provide higher-layer summaries for playlist images resources."""

    def fetch_playlist_images_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch playlist images.
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
            "playlistImageCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_playlist_image_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.insert` result.

        :param arguments: Wrapper arguments needed to create a playlist image.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and create outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet")
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        return {
            "playlistImageId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_playlist_image_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.update` result.

        :param arguments: Wrapper arguments needed to update a playlist image.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet")
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        return {
            "playlistImageId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_playlist_image_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.delete` wrapper result.

        :param arguments: Wrapper arguments needed to delete one playlist image.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted playlist-image identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "playlistImageId": result.get("playlistImageId"),
            "isDeleted": bool(result.get("isDeleted")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
