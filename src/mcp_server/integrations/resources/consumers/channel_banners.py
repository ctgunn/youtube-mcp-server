"""Higher-layer consumer summary methods for channel banners resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class ChannelBannersConsumerMixin:
    """Provide higher-layer summaries for channel banners resources."""

    def upload_channel_banner_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelBanners.insert` result.

        :param arguments: Wrapper arguments needed to upload banner artwork.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and upload outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "bannerUrl": result.get("bannerUrl") or result.get("url"),
            "isUploaded": bool(result.get("isUploaded") or result.get("url")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
