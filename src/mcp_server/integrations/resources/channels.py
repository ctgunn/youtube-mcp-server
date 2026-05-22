# ruff: noqa: F405
"""Channels resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class ChannelsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channels.list`.

    Official quota cost: ``1`` quota unit. The wrapper uses ``id``,
    ``forHandle``, or ``forUsername`` for public selector paths and uses
    ``mine`` for authorized owner-scoped retrieval.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channels.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector == "mine" and auth_context.mode is not AuthMode.OAUTH_REQUIRED:
            raise ValueError("mine requires oauth_required auth")
        if selector in {"id", "forHandle", "forUsername"} and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one channels request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``id``, ``mine``, ``forHandle``, or ``forUsername``.
        :raises ValueError: If no selector is present.
        """
        for field in ("id", "mine", "forHandle", "forUsername"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if value is True:
                return field
        raise ValueError("channels.list requires a supported selector")

@dataclass(frozen=True)
class ChannelsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channels.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a channel
    resource ``body`` payload aligned to supported writable parts on an
    authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channels.update` with OAuth and write-shape validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channels.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_channels_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channels.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public selector
    paths through ``id``, ``forHandle``, and ``forUsername`` when available,
    and owner-scoped retrieval through ``mine``.

    :return: Representative wrapper configured for `channels.list`.
    """
    metadata = EndpointMetadata(
        resource_name="channels",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/channels",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=(
                "id",
                "mine",
                "forHandle",
                "forUsername",
                "managedByMe",
                "pageToken",
                "maxResults",
            ),
            exactly_one_of=("id", "mine", "forHandle", "forUsername"),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `id`, `forHandle`, or `forUsername` for public selector paths. "
            "Use `mine` for owner-scoped retrieval with oauth_required auth."
        ),
        notes=(
            "Supports selector paths through `id`, `mine`, `forHandle`, and "
            "username-style lookup via `forUsername` when the upstream endpoint "
            "supports it. Treat selector combinations as mutually exclusive and "
            "preserve empty result sets as successful no-match outcomes."
        ),
    )
    return ChannelsListWrapper(metadata=metadata)

def build_channels_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channels.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a channel
    resource `body`, supports writable updates through ``brandingSettings`` and
    ``localizations``, and keeps OAuth-required and banner-URL reuse guidance
    visible for higher-layer reuse.

    :return: Representative wrapper configured for `channels.update`.
    """
    metadata = EndpointMetadata(
        resource_name="channels",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/channels",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_channels_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body` for the channel resource "
            "being updated, support writable updates through `brandingSettings` "
            "and `localizations`, reject read-only channel fields, and preserve "
            "`brandingSettings.image.bannerExternalUrl` for banner-update reuse."
        ),
    )
    return ChannelsUpdateWrapper(metadata=metadata)

FAMILY_NAME = "channels"
RESOURCE_NAMES = ("channels",)
BUILDER_FUNCTIONS = {
    "channels.list": build_channels_list_wrapper,
    "channels.update": build_channels_update_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelsListWrapper",
    "ChannelsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channels_list_wrapper",
    "build_channels_update_wrapper",
]
