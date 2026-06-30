# ruff: noqa: F405
"""Localization resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class I18nLanguagesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `i18nLanguages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-language lookup using required ``part`` and optional ``hl``
    on public API-key requests and keeps localization guidance visible for
    reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `i18nLanguages.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("i18nLanguages.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class I18nRegionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `i18nRegions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-region lookup using ``part`` plus ``hl`` on public API-key
    requests and keeps region guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `i18nRegions.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("i18nRegions.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_i18n_languages_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `i18nLanguages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-language lookup through required ``part`` and optional
    ``hl`` on API-key requests and keeps localization guidance visible.

    :return: Representative wrapper configured for `i18nLanguages.list`.
    """
    metadata = EndpointMetadata(
        resource_name="i18nLanguages",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/i18nLanguages",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("hl",),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` and accepts optional `hl` for one deterministic "
            "localization lookup, rejects undocumented modifiers, preserves "
            "empty result sets as successful outcomes, and keeps localization "
            "guidance visible for reuse decisions."
        ),
    )
    return I18nLanguagesListWrapper(metadata=metadata)

def build_i18n_regions_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `i18nRegions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-region lookup through ``part`` plus ``hl`` on API-key
    requests and keeps region guidance visible.

    :return: Representative wrapper configured for `i18nRegions.list`.
    """
    metadata = EndpointMetadata(
        resource_name="i18nRegions",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/i18nRegions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "hl"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` plus `hl` for one deterministic region "
            "lookup, rejects undocumented modifiers, preserves empty result "
            "sets as successful outcomes, and keeps region guidance "
            "visible for reuse decisions."
        ),
    )
    return I18nRegionsListWrapper(metadata=metadata)

FAMILY_NAME = "localization"
RESOURCE_NAMES = ("i18nLanguages", "i18nRegions")
BUILDER_FUNCTIONS = {
    "i18nLanguages.list": build_i18n_languages_list_wrapper,
    "i18nRegions.list": build_i18n_regions_list_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "I18nLanguagesListWrapper",
    "I18nRegionsListWrapper",
    "RESOURCE_NAMES",
    "build_i18n_languages_list_wrapper",
    "build_i18n_regions_list_wrapper",
]
