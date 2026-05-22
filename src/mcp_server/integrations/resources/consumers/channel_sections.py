"""Higher-layer consumer summary methods for channel sections resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class ChannelSectionsConsumerMixin:
    """Provide higher-layer summaries for channel sections resources."""

    def fetch_channel_sections_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch channel sections.
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
            "channelSectionCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.insert` result.

        :param arguments: Wrapper arguments needed to create one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "channelSectionId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "createdType": snippet.get("type"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.update` result.

        :param arguments: Wrapper arguments needed to update one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "channelSectionId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedType": snippet.get("type"),
            "delegatedOwner": result.get("delegatedOwner"),
            "delegatedOwnerChannel": result.get("delegatedOwnerChannel"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.delete` result.

        :param arguments: Wrapper arguments needed to delete one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "channelSectionId": result.get("channelSectionId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "delegatedOwnerChannel": result.get("delegatedOwnerChannel"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
