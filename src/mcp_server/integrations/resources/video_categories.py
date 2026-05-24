# ruff: noqa: F405
"""Video Categories resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class VideoCategoriesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videoCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    deterministic category lookup using ``part`` plus exactly one selector from
    ``id`` or ``regionCode`` on public API-key requests, with optional ``hl``
    display-language guidance kept visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videoCategories.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("videoCategories.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_video_categories_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videoCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one category
    lookup through ``part`` plus exactly one selector from ``id`` or
    ``regionCode`` on API-key requests and keeps selector and region guidance
    visible.

    :return: Representative wrapper configured for `videoCategories.list`.
    """
    metadata = EndpointMetadata(
        resource_name="videoCategories",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/videoCategories",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("id", "regionCode", "hl"),
            exactly_one_of=("id", "regionCode"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` plus exactly one selector from `id` or "
            "`regionCode`, treats optional `hl` as display-language guidance, "
            "rejects undocumented modifiers, preserves empty result sets as "
            "successful outcomes, and keeps region-specific review notes "
            "visible for reuse decisions."
        ),
    )
    return VideoCategoriesListWrapper(metadata=metadata)

FAMILY_NAME = "video_categories"
RESOURCE_NAMES = ("videoCategories",)
BUILDER_FUNCTIONS = {"videoCategories.list": build_video_categories_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "VideoCategoriesListWrapper",
    "build_video_categories_list_wrapper",
]
