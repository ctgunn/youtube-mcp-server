"""Higher-layer consumer summary methods for localization resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class LocalizationConsumerMixin:
    """Provide higher-layer summaries for localization resources."""

    def fetch_i18n_languages_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `i18nLanguages.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch localization languages.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing display-language use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "languageCount": len(items),
            "isEmpty": not items,
            "hl": arguments.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_i18n_regions_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `i18nRegions.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch localization regions.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing display-language use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "regionCount": len(items),
            "isEmpty": not items,
            "hl": arguments.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
