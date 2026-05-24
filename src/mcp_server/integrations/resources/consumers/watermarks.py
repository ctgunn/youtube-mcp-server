"""Higher-layer consumer summary methods for watermarks resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class WatermarksConsumerMixin:
    """Provide higher-layer summaries for watermarks resources."""

    def set_watermark_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `watermarks.set` result.

        :param arguments: Wrapper arguments needed to set one channel watermark.
        :param auth_context: Auth context for the wrapper call.
        :return: Credential-safe summary showing source contract details and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "channelId": result.get("channelId") or arguments.get("channelId"),
            "isSet": bool(result.get("isSet") or result.get("channelId") or arguments.get("channelId")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourcePathShape": self.wrapper.metadata.path_shape,
            "sourceMediaBoundary": "10 MB image/jpeg image/png application/octet-stream",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def unset_watermark_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `watermarks.unset` result.

        :param arguments: Wrapper arguments needed to remove one channel watermark.
        :param auth_context: Auth context for the wrapper call.
        :return: Credential-safe summary showing source contract details and removal outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "channelId": result.get("channelId") or arguments.get("channelId"),
            "isUnset": bool(result.get("isUnset") or result.get("channelId") or arguments.get("channelId")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourcePathShape": self.wrapper.metadata.path_shape,
            "sourcePayloadBoundary": "no body no media upload",
            "sourceNotes": self.wrapper.metadata.notes,
        }
