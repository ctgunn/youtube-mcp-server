"""Representative higher-layer consumer for Layer 1 wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper


@dataclass(frozen=True)
class RepresentativeHigherLayerConsumer:
    """Compose typed Layer 1 wrapper methods in a higher-layer workflow.

    :param wrapper: Representative typed wrapper used by the consumer.
    :param executor: Shared request executor used for wrapper calls.
    """

    wrapper: RepresentativeEndpointWrapper
    executor: IntegrationExecutor

    def fetch_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a simplified higher-layer summary from a typed wrapper result.

        :param arguments: Wrapper arguments needed to fetch the video.
        :param auth_context: Auth context for the wrapper call.
        :return: Higher-layer summary derived from the typed wrapper response.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        item = result["items"][0]
        return {
            "videoId": item["id"],
            "title": item.get("title"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
        }
