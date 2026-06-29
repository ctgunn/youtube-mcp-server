# ruff: noqa: F405
"""Guide Categories resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class GuideCategoriesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `guideCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    legacy lookup using ``part`` plus exactly one of ``regionCode`` or ``id``
    on public API-key requests. Optional ``hl`` localization is accepted when
    upstream legacy behavior supports localized guide-category text.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `guideCategories.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("guideCategories.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_guide_categories_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `guideCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one legacy
    lookup through ``part`` plus exactly one of ``regionCode`` or ``id`` on
    API-key requests and accepts optional ``hl`` localization where upstream
    behavior supports it. Deprecated-or-unavailable lifecycle guidance remains
    visible.

    :return: Representative wrapper configured for `guideCategories.list`.
    """
    metadata = EndpointMetadata(
        resource_name="guideCategories",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/guideCategories",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("regionCode", "id", "hl"),
            exactly_one_of=("regionCode", "id"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        lifecycle_state="deprecated",
        caveat_note=(
            "This legacy guide-category endpoint is deprecated and may be "
            "unavailable in current platform behavior even when the request "
            "shape is otherwise valid."
        ),
        notes=(
            "Requires `part` plus exactly one of `regionCode` or `id` for one "
            "deterministic legacy lookup, accepts optional `hl` localization, "
            "rejects undocumented modifiers, preserves empty result sets as "
            "successful outcomes, and keeps lifecycle caveats visible for "
            "reuse decisions."
        ),
    )
    return GuideCategoriesListWrapper(metadata=metadata)

FAMILY_NAME = "guide_categories"
RESOURCE_NAMES = ("guideCategories",)
BUILDER_FUNCTIONS = {"guideCategories.list": build_guide_categories_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "GuideCategoriesListWrapper",
    "RESOURCE_NAMES",
    "build_guide_categories_list_wrapper",
]
