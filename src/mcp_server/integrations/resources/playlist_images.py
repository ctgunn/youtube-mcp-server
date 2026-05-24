# ruff: noqa: F405
"""Playlist Images resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class PlaylistImagesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistImages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    playlist-image lookup using required ``part`` plus exactly one selector
    from ``playlistId`` or ``id`` on OAuth-backed requests, and only allows
    paging arguments for playlist-scoped lookups.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistImages.list` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistImages.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistImagesInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistImages.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    metadata payload plus a `media` upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistImages.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistImages.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistImagesUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistImages.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    payload that identifies the existing playlist image plus a `media` update
    payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistImages.update` with OAuth and update validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistImages.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistImagesDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlistImages.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist-image ``id`` on an authorized request and keeps target-state-
    sensitive delete guidance visible for higher-layer reuse.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlistImages.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlistImages.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_playlist_images_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistImages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    OAuth-required playlist-image lookup through required ``part`` plus
    exactly one selector from ``playlistId`` or ``id`` and limits paging
    inputs to playlist-scoped retrieval.

    :return: Representative wrapper configured for `playlistImages.list`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistImages",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/playlistImages",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("playlistId", "id", "pageToken", "maxResults"),
            exactly_one_of=("playlistId", "id"),
            validators=(_require_playlist_images_list_arguments,),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        notes=(
            "Requires required `part` plus exactly one selector from "
            "`playlistId` or `id` for one deterministic OAuth-required "
            "playlist-image lookup, allows `pageToken` and `maxResults` only "
            "for `playlistId` requests, rejects undocumented modifiers, and "
            "preserves empty result sets as successful outcomes."
        ),
    )
    return PlaylistImagesListWrapper(metadata=metadata)

def build_playlist_images_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistImages.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    metadata payload and a `media` upload payload on authorized requests, and
    keeps the upload-sensitive contract visible for higher-layer reuse.

    :return: Representative wrapper configured for `playlistImages.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistImages",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/playlistImages",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body", "media"),
            validators=(
                require_mapping_fields("body", required_keys=("snippet",)),
                require_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body` for playlist-image metadata, "
            "use `media` for playlist-image upload content, and keep the required "
            "creation boundary visible for review."
        ),
    )
    return PlaylistImagesInsertWrapper(metadata=metadata)

def build_playlist_images_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistImages.update`.

    Official quota cost: ``50`` quota units. The wrapper requires identifying
    `body` metadata plus a `media` update payload on authorized requests, and
    keeps the media-sensitive update contract visible for higher-layer reuse.

    :return: Representative wrapper configured for `playlistImages.update`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistImages",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/playlistImages",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body", "media"),
            validators=(
                _require_playlist_images_update_body,
                require_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.id` to identify the existing "
            "playlist image, use `body.snippet.playlistId` for the owning playlist "
            "context, use `media` for playlist-image update content, and keep the "
            "required update boundary visible for review."
        ),
    )
    return PlaylistImagesUpdateWrapper(metadata=metadata)

def build_playlist_images_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlistImages.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist-image ``id`` on authorized requests, keeps the destructive delete
    boundary visible for review, and preserves target-state-sensitive guidance
    for downstream reuse.

    :return: Representative wrapper configured for `playlistImages.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="playlistImages",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/playlistImages",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_playlist_images_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the playlist image "
            "being deleted, keep requests scoped to one target playlist image "
            "at a time, and note that deletion remains target-state sensitive "
            "even with authorized access."
        ),
    )
    return PlaylistImagesDeleteWrapper(metadata=metadata)

FAMILY_NAME = "playlist_images"
RESOURCE_NAMES = ("playlistImages",)
BUILDER_FUNCTIONS = {
    "playlistImages.list": build_playlist_images_list_wrapper,
    "playlistImages.insert": build_playlist_images_insert_wrapper,
    "playlistImages.update": build_playlist_images_update_wrapper,
    "playlistImages.delete": build_playlist_images_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistImagesDeleteWrapper",
    "PlaylistImagesInsertWrapper",
    "PlaylistImagesListWrapper",
    "PlaylistImagesUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlist_images_delete_wrapper",
    "build_playlist_images_insert_wrapper",
    "build_playlist_images_list_wrapper",
    "build_playlist_images_update_wrapper",
]
