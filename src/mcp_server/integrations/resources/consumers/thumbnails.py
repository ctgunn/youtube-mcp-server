"""Higher-layer consumer summary methods for thumbnails resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class ThumbnailsConsumerMixin:
    """Provide higher-layer summaries for thumbnails resources."""

    def set_thumbnail_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `thumbnails.set` result.

        :param arguments: Wrapper arguments needed to set one video thumbnail.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "videoId": result.get("videoId") or arguments.get("videoId"),
            "thumbnailUrl": result.get("thumbnailUrl") or result.get("url"),
            "isUpdated": bool(result.get("isUpdated") or result.get("videoId") or arguments.get("videoId")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourcePathShape": self.wrapper.metadata.path_shape,
            "sourceNotes": self.wrapper.metadata.notes,
        }
