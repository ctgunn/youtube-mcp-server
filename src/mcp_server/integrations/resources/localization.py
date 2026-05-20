"""Localization resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    I18nLanguagesListWrapper,
    I18nRegionsListWrapper,
    build_i18n_languages_list_wrapper,
    build_i18n_regions_list_wrapper,
)

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
