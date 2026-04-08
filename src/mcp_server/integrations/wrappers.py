"""Representative internal endpoint wrappers for Layer 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext, AuthMode
from mcp_server.integrations.contracts import (
    EndpointMetadata,
    EndpointRequestShape,
    require_mapping_fields,
    require_optional_mapping_fields,
)
from mcp_server.integrations.executor import IntegrationExecutor, RequestExecution


@dataclass(frozen=True)
class RepresentativeEndpointWrapper:
    """Represent one metadata-driven Layer 1 wrapper.

    :param metadata: Declared wrapper metadata and request shape.
    :ivar metadata: Includes upstream identity, quota cost, auth mode, and review notes.
    """

    metadata: EndpointMetadata

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute the representative wrapper through the shared executor.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        """
        self.metadata.request_shape.validate_arguments(arguments)
        execution = RequestExecution(
            metadata=self.metadata,
            arguments=arguments,
            auth_context=auth_context,
        )
        return executor.execute(execution)

    def review_surface(self) -> dict[str, object]:
        """Return the maintainer-facing metadata surface for this wrapper.

        The returned payload keeps endpoint identity, quota cost, auth mode,
        and lifecycle caveats visible near the wrapper definition.

        :return: Reviewable metadata derived from the wrapper contract.
        """
        return self.metadata.review_surface()


@dataclass(frozen=True)
class ActivitiesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `activities.list`.

    Official quota cost: ``1`` quota unit. The wrapper uses `channelId` for the
    public path and `mine` or `home` for authorized-user paths.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `activities.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector == "channelId" and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("channelId requires api_key auth")
        if selector in {"mine", "home"} and auth_context.mode is not AuthMode.OAUTH_REQUIRED:
            raise ValueError(f"{selector} requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one activities request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of `channelId`, `mine`, or `home`.
        :raises ValueError: If no selector is present.
        """
        for field in ("channelId", "mine", "home"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if value is True:
                return field
        raise ValueError("activities.list requires a supported selector")


@dataclass(frozen=True)
class CaptionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.list`.

    Official quota cost: ``50`` quota units. The wrapper uses ``videoId`` for
    caption inventory lookup and ``id`` for direct caption-track lookup.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.list` with OAuth and delegation validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CaptionsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.insert`.

    Official quota cost: ``400`` quota units. The wrapper requires a `body`
    metadata payload plus a `media` upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CaptionsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.update`.

    Official quota cost: ``450`` quota units. The wrapper requires a `body`
    caption resource payload and supports an optional `media` payload for
    body-plus-media content replacement on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.update` with OAuth and update validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CaptionsDownloadWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.download`.

    Official quota cost: ``200`` quota units. The wrapper requires a caption
    track ``id`` and supports optional ``tfmt`` and ``tlang`` modifiers plus
    optional `onBehalfOfContentOwner` delegation on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.download` with OAuth and option validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.download requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


def build_activities_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `activities.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports a public
    channel selector via ``channelId`` and authorized-user selectors via
    ``mine`` or ``home``.

    :return: Representative wrapper configured for `activities.list`.
    """
    metadata = EndpointMetadata(
        resource_name="activities",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/activities",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("channelId", "mine", "home", "maxResults", "pageToken", "publishedAfter"),
            exactly_one_of=("channelId", "mine", "home"),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `channelId` for public channel activity. Use `mine` or `home` "
            "when authorized user activity views are required."
        ),
    )
    return ActivitiesListWrapper(metadata=metadata)


def build_captions_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.list`.

    Official quota cost: ``50`` quota units. The wrapper supports selector
    paths via ``videoId`` and ``id`` and allows optional
    ``onBehalfOfContentOwner`` delegation on authorized requests.

    :return: Representative wrapper configured for `captions.list`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("videoId", "id", "onBehalfOfContentOwner", "pageToken", "maxResults"),
            exactly_one_of=("videoId", "id"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `videoId` for caption inventory "
            "lookup, use `id` for direct caption-track lookup, and treat "
            "`onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CaptionsListWrapper(metadata=metadata)


def build_captions_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.insert`.

    Official quota cost: ``400`` quota units. The wrapper requires a `body`
    metadata payload and a `media` upload payload, allows optional
    `onBehalfOfContentOwner` delegation on authorized requests, and keeps the
    upload-sensitive contract visible for higher-layer reuse.

    :return: Representative wrapper configured for `captions.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body", "media"),
            optional_fields=("onBehalfOfContentOwner", "sync"),
            validators=(
                require_mapping_fields("body", required_keys=("snippet",)),
                require_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=400,
        notes=(
            "Requires oauth_required auth. Use `body` for caption metadata, "
            "use `media` for caption upload content, and treat "
            "`onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CaptionsInsertWrapper(metadata=metadata)


def build_captions_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.update`.

    Official quota cost: ``450`` quota units. The wrapper requires a `body`
    caption-resource payload, supports body-only updates and body-plus-media
    content replacement, allows optional `onBehalfOfContentOwner` delegation on
    authorized requests, and keeps the update boundary visible for higher-layer
    reuse.

    :return: Representative wrapper configured for `captions.update`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("media", "onBehalfOfContentOwner"),
            validators=(
                require_mapping_fields("body", required_keys=("id", "snippet")),
                require_optional_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=450,
        notes=(
            "Requires oauth_required auth. Use `body` for the caption resource "
            "being updated, use `media` only for supported body-plus-media "
            "content replacement, and treat `onBehalfOfContentOwner` as "
            "optional delegation context."
        ),
    )
    return CaptionsUpdateWrapper(metadata=metadata)


def build_captions_download_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.download`.

    Official quota cost: ``200`` quota units. The wrapper requires one caption
    track ``id``, supports optional ``tfmt`` format conversion and ``tlang``
    translation inputs, and keeps permission-sensitive and delegated download
    guidance visible for higher-layer reuse.

    :return: Representative wrapper configured for `captions.download`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="download",
        http_method="GET",
        path_shape="/youtube/v3/captions/{id}",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("tfmt", "tlang", "onBehalfOfContentOwner"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=200,
        notes=(
            "Requires oauth_required auth. Use `id` for the caption track being "
            "downloaded, use `tfmt` and `tlang` only for supported output "
            "variants, note that some downloads remain permission-sensitive "
            "even with authorized access, and treat `onBehalfOfContentOwner` "
            "as optional delegation context."
        ),
    )
    return CaptionsDownloadWrapper(metadata=metadata)
