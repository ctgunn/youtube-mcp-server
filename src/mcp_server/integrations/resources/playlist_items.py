# ruff: noqa: F405
"""Playlist Items resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class PlaylistItemsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistItems.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    playlist-item lookup using required ``part`` plus exactly one selector
    from ``playlistId`` or ``id`` on API-key requests, and only allows
    paging arguments for playlist-scoped lookups.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistItems.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("playlistItems.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistItemsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistItems.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet` payload carrying playlist and referenced video details on an
    authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistItems.insert` with OAuth and write validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistItems.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistItemsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistItems.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a target
    `body.id` plus a writable `body.snippet` payload carrying playlist and
    referenced video details on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistItems.update` with OAuth and write validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistItems.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistItemsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistItems.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist-item ``id`` on an authorized request with target-state-sensitive
    behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistItems.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistItems.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_playlist_items_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistItems.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    API-key playlist-item lookup through required ``part`` plus exactly one
    selector from ``playlistId`` or ``id`` and limits paging inputs to
    playlist-scoped retrieval.

    :return: Representative wrapper configured for `playlistItems.list`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistItems",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/playlistItems",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("playlistId", "id", "pageToken", "maxResults"),
            exactly_one_of=("playlistId", "id"),
            validators=(_require_playlist_items_list_arguments,),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires required `part` plus exactly one selector from "
            "`playlistId` or `id` for one deterministic API-key "
            "playlist-item lookup, allows `pageToken` and `maxResults` only "
            "for `playlistId` requests, rejects undocumented modifiers, and "
            "preserves empty result sets as successful outcomes."
        ),
    )
    return PlaylistItemsListWrapper(metadata=metadata)

def build_playlist_items_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistItems.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet` payload with playlist and referenced video details on
    authorized requests and keeps unsupported optional write fields visible for
    higher-layer reuse.

    :return: Representative wrapper configured for `playlistItems.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistItems",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/playlistItems",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_playlist_items_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.snippet.playlistId` for "
            "the target playlist, use `body.snippet.resourceId.videoId` for "
            "the referenced video, accept optional non-negative "
            "`body.snippet.position` placement, keep the minimum writable "
            "`snippet` boundary visible for review, and reject unsupported "
            "optional content-details fields unless explicitly added to the "
            "contract."
        ),
    )
    return PlaylistItemsInsertWrapper(metadata=metadata)

def build_playlist_items_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistItems.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a target
    `body.id` plus a writable `body.snippet` payload with playlist and
    referenced video details on authorized requests and keeps unsupported
    optional write fields visible for higher-layer reuse.

    :return: Representative wrapper configured for `playlistItems.update`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistItems",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/playlistItems",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_playlist_items_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.id` to identify the "
            "existing playlist item being updated, use `body.snippet.playlistId` "
            "for the target playlist, use `body.snippet.resourceId.videoId` for "
            "the referenced video, keep the minimum writable `snippet` boundary "
            "visible for review, and reject unsupported optional placement or "
            "content-details fields unless explicitly added to the contract."
        ),
    )
    return PlaylistItemsUpdateWrapper(metadata=metadata)

def build_playlist_items_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistItems.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist-item ``id`` on authorized requests, keeps the destructive delete
    boundary visible for review, and preserves target-state-sensitive guidance
    for downstream reuse.

    :return: Representative wrapper configured for `playlistItems.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistItems",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/playlistItems",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_playlist_items_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the playlist item "
            "being deleted, keep requests scoped to one target playlist item "
            "at a time, and note that deletion remains target-state sensitive "
            "even with authorized access."
        ),
    )
    return PlaylistItemsDeleteWrapper(metadata=metadata)

FAMILY_NAME = "playlist_items"
RESOURCE_NAMES = ("playlistItems",)
BUILDER_FUNCTIONS = {
    "playlistItems.list": build_playlist_items_list_wrapper,
    "playlistItems.insert": build_playlist_items_insert_wrapper,
    "playlistItems.update": build_playlist_items_update_wrapper,
    "playlistItems.delete": build_playlist_items_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistItemsDeleteWrapper",
    "PlaylistItemsInsertWrapper",
    "PlaylistItemsListWrapper",
    "PlaylistItemsUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlist_items_delete_wrapper",
    "build_playlist_items_insert_wrapper",
    "build_playlist_items_list_wrapper",
    "build_playlist_items_update_wrapper",
]
