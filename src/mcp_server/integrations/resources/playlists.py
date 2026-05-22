# ruff: noqa: F405
"""Playlists resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class PlaylistsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlists.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public selector
    paths through ``channelId`` and ``id`` and owner-scoped retrieval through
    ``mine`` with selector-aware paging rules kept visible for maintainers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlists.list` with selector-aware auth validation.

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
        """Return the active selector field for one playlists request.

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
        raise ValueError("exactly one selector is required from: channelId, id, mine")

@dataclass(frozen=True)
class PlaylistsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlists.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet` payload carrying the minimum playlist title details on an
    authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlists.insert` with OAuth and write validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlists.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlists.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a target
    `body.id` plus a writable `body.snippet` payload carrying the minimum
    playlist title details on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlists.update` with OAuth and write validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlists.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class PlaylistsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `playlists.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist ``id`` on an authorized request with target-state-sensitive
    behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `playlists.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("playlists.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_playlists_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlists.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public
    playlist lookup through ``channelId`` and ``id`` and owner-scoped
    retrieval through ``mine``, while limiting paging inputs to collection
    lookups.

    :return: Representative wrapper configured for `playlists.list`.
    """
    metadata = EndpointMetadata(
        resource_name="playlists",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/playlists",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("channelId", "id", "mine", "pageToken", "maxResults"),
            exactly_one_of=("channelId", "id", "mine"),
            validators=(_require_playlists_list_arguments,),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `channelId` or `id` for public playlist lookup paths. "
            "Use `mine` for owner-scoped retrieval with oauth_required auth."
        ),
        notes=(
            "Requires required `part` plus exactly one selector from "
            "`channelId`, `id`, or `mine` for one deterministic playlist "
            "lookup, allows `pageToken` and `maxResults` only for `channelId` "
            "or `mine` requests, rejects undocumented modifiers, and preserves "
            "empty result sets as successful outcomes."
        ),
    )
    return PlaylistsListWrapper(metadata=metadata)

def build_playlists_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlists.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet` payload with the minimum playlist title on authorized
    requests, keeps `part=snippet` explicit for maintainers, and rejects
    unsupported optional write fields such as `description`, `status`, or
    `localization` unless the contract is deliberately expanded.

    :return: Representative wrapper configured for `playlists.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="playlists",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/playlists",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_playlists_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Keep `part=snippet` explicit, use "
            "`body.snippet.title` for the required playlist title, and reject "
            "unsupported optional fields such as `body.snippet.description`, "
            "`body.status`, or `body.localization` unless they are explicitly "
            "added to the contract."
        ),
    )
    return PlaylistsInsertWrapper(metadata=metadata)

def build_playlists_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlists.update`.

    Official quota cost: ``50`` quota units. The wrapper requires `body.id`
    for the existing playlist, keeps `part=snippet` explicit for maintainers,
    requires `body.snippet.title` for the minimum supported update path, and
    rejects unsupported optional write fields such as `description`, `status`,
    or `localizations` unless the contract is deliberately expanded.

    :return: Representative wrapper configured for `playlists.update`.
    """
    metadata = EndpointMetadata(
        resource_name="playlists",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/playlists",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_playlists_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.id` for the existing "
            "playlist identifier, keep `part=snippet` explicit, use "
            "`body.snippet.title` for the minimum writable playlist field, "
            "and reject unsupported optional fields such as "
            "`body.snippet.description`, `body.status`, or "
            "`body.localizations` unless they are explicitly added to the "
            "contract."
        ),
    )
    return PlaylistsUpdateWrapper(metadata=metadata)

def build_playlists_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `playlists.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    playlist ``id`` on authorized requests, keeps the destructive delete
    boundary visible for review, and preserves target-state-sensitive guidance
    for downstream reuse.

    :return: Representative wrapper configured for `playlists.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="playlists",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/playlists",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_playlists_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the playlist being "
            "deleted, keep requests scoped to one target playlist at a time, "
            "and note that deletion remains target-state sensitive even with "
            "authorized access."
        ),
    )
    return PlaylistsDeleteWrapper(metadata=metadata)

FAMILY_NAME = "playlists"
RESOURCE_NAMES = ("playlists",)
BUILDER_FUNCTIONS = {
    "playlists.list": build_playlists_list_wrapper,
    "playlists.insert": build_playlists_insert_wrapper,
    "playlists.update": build_playlists_update_wrapper,
    "playlists.delete": build_playlists_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "PlaylistsDeleteWrapper",
    "PlaylistsInsertWrapper",
    "PlaylistsListWrapper",
    "PlaylistsUpdateWrapper",
    "RESOURCE_NAMES",
    "build_playlists_delete_wrapper",
    "build_playlists_insert_wrapper",
    "build_playlists_list_wrapper",
    "build_playlists_update_wrapper",
]
