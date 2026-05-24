"""Resource-family integration access for Layer 1 YouTube wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from mcp_server.integrations.resources import (
    activities,
    captions,
    channel_banners,
    channel_sections,
    channels,
    comment_threads,
    comments,
    guide_categories,
    localization,
    members,
    memberships_levels,
    playlist_images,
    playlist_items,
    playlists,
    search,
    subscriptions,
    thumbnails,
    video_abuse_report_reasons,
    video_categories,
    videos,
    watermarks,
)

WrapperBuilder = Callable[[], Any]
FamilyBuilderRegistry = Mapping[str, Mapping[str, WrapperBuilder]]

REQUIRED_RESOURCE_FAMILIES = (
    "activities",
    "captions",
    "channel_banners",
    "channels",
    "channel_sections",
    "comments",
    "comment_threads",
    "guide_categories",
    "localization",
    "members",
    "memberships_levels",
    "playlist_images",
    "playlist_items",
    "playlists",
    "search",
    "subscriptions",
    "thumbnails",
    "video_abuse_report_reasons",
    "video_categories",
    "videos",
    "watermarks",
)

_RESOURCE_MODULES = (
    activities,
    captions,
    channel_banners,
    channels,
    channel_sections,
    comments,
    comment_threads,
    guide_categories,
    localization,
    members,
    memberships_levels,
    playlist_images,
    playlist_items,
    playlists,
    search,
    subscriptions,
    thumbnails,
    video_abuse_report_reasons,
    video_categories,
    videos,
    watermarks,
)


def build_family_builder_registry(
    family_builders: Mapping[str, Mapping[str, WrapperBuilder]],
) -> FamilyBuilderRegistry:
    """Build an immutable resource-family wrapper builder registry.

    :param family_builders: Mapping of family names to operation-key builder mappings.
    :return: Read-only registry preserving the supplied family and operation mapping.
    """
    return MappingProxyType(
        {
            family_name: MappingProxyType(dict(builders))
            for family_name, builders in family_builders.items()
        }
    )


def get_family_builders(
    registry: FamilyBuilderRegistry,
    family_name: str,
) -> Mapping[str, WrapperBuilder]:
    """Return all wrapper builders for one resource family.

    :param registry: Resource-family builder registry to inspect.
    :param family_name: Resource family name to look up.
    :return: Operation-key to builder mapping for the family.
    :raises KeyError: If the family is not registered.
    """
    if family_name not in registry:
        raise KeyError(f"unknown resource family: {family_name}")
    return registry[family_name]


def get_family_builder(
    registry: FamilyBuilderRegistry,
    family_name: str,
    operation_key: str,
) -> WrapperBuilder:
    """Return one wrapper builder from a resource-family registry.

    :param registry: Resource-family builder registry to inspect.
    :param family_name: Resource family name to look up.
    :param operation_key: Stable operation key to retrieve.
    :return: Wrapper builder callable for the operation.
    :raises KeyError: If the family or operation is not registered.
    """
    family_builders = get_family_builders(registry, family_name)
    if operation_key not in family_builders:
        raise KeyError(f"unknown operation for {family_name}: {operation_key}")
    return family_builders[operation_key]


def list_registered_families(registry: FamilyBuilderRegistry) -> tuple[str, ...]:
    """Return registered resource family names in stable sorted order.

    :param registry: Resource-family builder registry to inspect.
    :return: Sorted family names present in the registry.
    """
    return tuple(sorted(registry))


DEFAULT_FAMILY_BUILDER_REGISTRY = build_family_builder_registry(
    {module.FAMILY_NAME: module.BUILDER_FUNCTIONS for module in _RESOURCE_MODULES}
)
RESPONSE_NORMALIZER_FAMILIES = MappingProxyType(
    {
        module.FAMILY_NAME: getattr(module, "RESPONSE_NORMALIZER_KEYS")
        for module in _RESOURCE_MODULES
        if hasattr(module, "RESPONSE_NORMALIZER_KEYS")
    }
)
