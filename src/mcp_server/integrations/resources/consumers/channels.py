"""Higher-layer consumer summary methods for channels resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class ChannelsConsumerMixin:
    """Provide higher-layer summaries for channels resources."""

    def fetch_channels_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channels.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch channels.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("id", "mine", "forHandle", "forUsername")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "channelCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_channel_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channels.update` wrapper result.

        :param arguments: Wrapper arguments needed to update channel state.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated channel identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        updated_parts = tuple(part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip())
        branding_settings = arguments.get("body", {}).get("brandingSettings", {}) if isinstance(arguments.get("body"), dict) else {}
        image_settings = branding_settings.get("image", {}) if isinstance(branding_settings, dict) else {}
        return {
            "channelId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedParts": updated_parts,
            "bannerUrlUsed": image_settings.get("bannerExternalUrl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
