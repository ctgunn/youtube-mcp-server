# ruff: noqa: F405
"""Channel Sections resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class ChannelSectionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelSections.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public selector
    paths through ``channelId`` and ``id`` and owner-scoped retrieval through
    ``mine`` with lifecycle-note guidance kept visible for maintainers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelSections.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector == "mine" and auth_context.mode is not AuthMode.OAUTH_REQUIRED:
            raise ValueError("mine requires oauth_required auth")
        if selector in {"channelId", "id"} and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one channel-sections request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``channelId``, ``id``, or ``mine``.
        :raises ValueError: If no selector is present.
        """
        for field in ("channelId", "id", "mine"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if value is True:
                return field
        raise ValueError("channelSections.list requires a supported selector")

@dataclass(frozen=True)
class ChannelSectionsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelSections.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a channel
    section resource ``body`` aligned to the selected ``snippet.type`` on an
    authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelSections.insert` with OAuth and create-shape validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channelSections.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class ChannelSectionsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelSections.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a channel
    section resource ``body`` that identifies the existing section and stays
    aligned to the selected ``snippet.type`` on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelSections.update` with OAuth and update-shape validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channelSections.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class ChannelSectionsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelSections.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one channel
    section ``id`` and supports optional delegated owner context on an
    authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelSections.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channelSections.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_channel_sections_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelSections.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public selector
    paths through ``channelId`` and ``id`` and owner-scoped retrieval through
    ``mine`` while keeping lifecycle-note readiness visible for later caveats.

    :return: Representative wrapper configured for `channelSections.list`.
    """
    metadata = EndpointMetadata(
        resource_name="channelSections",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/channelSections",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("channelId", "id", "mine", "pageToken", "maxResults"),
            exactly_one_of=("channelId", "id", "mine"),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `channelId` or `id` for public selector paths. Use `mine` for "
            "owner-scoped retrieval with oauth_required auth."
        ),
        notes=(
            "Supports selector paths through `channelId`, `id`, and `mine`. "
            "Treat selector combinations as mutually exclusive, preserve empty "
            "result sets as successful no-match outcomes, and keep lifecycle "
            "notes visible when channel-sections availability caveats matter."
        ),
    )
    return ChannelSectionsListWrapper(metadata=metadata)

def build_channel_sections_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelSections.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    channel-section resource, validates `snippet.type`-specific content rules,
    and keeps OAuth-required, title, and optional delegation guidance visible
    for higher-layer reuse.

    :return: Representative wrapper configured for `channelSections.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="channelSections",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/channelSections",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"),
            validators=(
                _require_channel_sections_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body` for the channel section "
            "resource being created, use `snippet.type` to select playlist, "
            "channel, or other section rules, require `body.snippet.title` for "
            "`multiplePlaylists` and `multipleChannels`, reject duplicated "
            "playlist or channel references, and treat `onBehalfOfContentOwner` "
            "and `onBehalfOfContentOwnerChannel` as optional delegation context."
        ),
    )
    return ChannelSectionsInsertWrapper(metadata=metadata)

def build_channel_sections_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelSections.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    channel-section resource that includes `body.id`, validates
    `snippet.type`-specific content rules, and keeps OAuth-required, title,
    and optional delegation guidance visible for higher-layer reuse.

    :return: Representative wrapper configured for `channelSections.update`.
    """
    metadata = EndpointMetadata(
        resource_name="channelSections",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/channelSections",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"),
            validators=(
                _require_channel_sections_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body` for the existing channel "
            "section resource being updated, require `body.id` to identify the "
            "target section, use `snippet.type` to select playlist, channel, "
            "or other section rules, require `body.snippet.title` for "
            "`multiplePlaylists` and `multipleChannels`, reject duplicated "
            "playlist or channel references, and treat `onBehalfOfContentOwner` "
            "and `onBehalfOfContentOwnerChannel` as optional delegation context."
        ),
    )
    return ChannelSectionsUpdateWrapper(metadata=metadata)

def build_channel_sections_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelSections.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one channel
    section `id`, supports optional `onBehalfOfContentOwner` and
    `onBehalfOfContentOwnerChannel` delegation, and keeps owner-scoped delete
    guidance visible for higher-layer reuse.

    :return: Representative wrapper configured for `channelSections.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="channelSections",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/channelSections",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("onBehalfOfContentOwner", "onBehalfOfContentOwnerChannel"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the channel section "
            "being deleted, keep requests scoped to one target section at a "
            "time, note that deletion remains owner-scoped and target-state "
            "sensitive even with authorized access, and treat "
            "`onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` as "
            "optional delegation context."
        ),
    )
    return ChannelSectionsDeleteWrapper(metadata=metadata)

FAMILY_NAME = "channel_sections"
RESOURCE_NAMES = ("channelSections",)
BUILDER_FUNCTIONS = {
    "channelSections.list": build_channel_sections_list_wrapper,
    "channelSections.insert": build_channel_sections_insert_wrapper,
    "channelSections.update": build_channel_sections_update_wrapper,
    "channelSections.delete": build_channel_sections_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelSectionsDeleteWrapper",
    "ChannelSectionsInsertWrapper",
    "ChannelSectionsListWrapper",
    "ChannelSectionsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channel_sections_delete_wrapper",
    "build_channel_sections_insert_wrapper",
    "build_channel_sections_list_wrapper",
    "build_channel_sections_update_wrapper",
]
