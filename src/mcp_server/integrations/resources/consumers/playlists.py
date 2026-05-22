"""Higher-layer consumer summary methods for playlists resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class PlaylistsConsumerMixin:
    """Provide higher-layer summaries for playlists resources."""

    def fetch_playlists_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlists.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch playlists.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("channelId", "id", "mine")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "playlistCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_playlist_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlists.insert` result.

        :param arguments: Wrapper arguments needed to create a playlist.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details, required create
            inputs, and create outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        snippet = result.get("snippet")
        return {
            "playlistId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "title": (
                result.get("title")
                or (snippet.get("title") if isinstance(snippet, dict) else None)
                or body_snippet.get("title")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceWritablePart": arguments.get("part"),
            "sourceRequiredTitleField": "body.snippet.title",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_playlist_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlists.update` result.

        :param arguments: Wrapper arguments needed to update a playlist.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details, required update
            inputs, and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        snippet = result.get("snippet")
        return {
            "playlistId": result.get("id") or (body.get("id") if isinstance(body, dict) else None),
            "isUpdated": bool(result.get("id") or (body.get("id") if isinstance(body, dict) else None)),
            "title": (
                result.get("title")
                or (snippet.get("title") if isinstance(snippet, dict) else None)
                or body_snippet.get("title")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceWritablePart": arguments.get("part"),
            "sourceRequiredIdentifierField": "body.id",
            "sourceRequiredTitleField": "body.snippet.title",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_playlist_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlists.delete` result.

        :param arguments: Wrapper arguments needed to delete a playlist.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted playlist identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "playlistId": result.get("playlistId"),
            "isDeleted": bool(result.get("isDeleted")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
