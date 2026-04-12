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

_CHANNEL_BANNER_ALLOWED_MIME_TYPES = frozenset({"image/jpeg", "image/png", "application/octet-stream"})
_CHANNEL_BANNER_MAX_BYTES = 6 * 1024 * 1024
_CHANNELS_UPDATE_SUPPORTED_PARTS = frozenset({"brandingSettings", "localizations"})


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


@dataclass(frozen=True)
class CaptionsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires a caption
    track ``id`` and supports optional ``onBehalfOfContentOwner`` delegation on
    an authorized request with ownership-sensitive behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.delete` with OAuth and delegation validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class ChannelBannersInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelBanners.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires one `media`
    upload payload and supports optional `onBehalfOfContentOwner` delegation on
    an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelBanners.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channelBanners.insert requires oauth_required auth")
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


def _channels_update_parts(arguments: dict[str, object]) -> tuple[str, ...]:
    """Return normalized writable parts for one `channels.update` request.

    :param arguments: Wrapper arguments to inspect.
    :return: Ordered supported writable parts without duplicates.
    :raises ValueError: If no writable part is declared.
    """
    raw_part = arguments.get("part")
    if not isinstance(raw_part, str):
        raise ValueError("part must identify at least one supported writable part")
    parts: list[str] = []
    for part_name in raw_part.split(","):
        normalized = part_name.strip()
        if normalized and normalized not in parts:
            parts.append(normalized)
    if not parts:
        raise ValueError("part must identify at least one supported writable part")
    return tuple(parts)


def _require_channels_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channels.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported writable parts.
    """
    require_mapping_fields("body", required_keys=("id",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    parts = _channels_update_parts(arguments)
    unsupported_parts = [part for part in parts if part not in _CHANNELS_UPDATE_SUPPORTED_PARTS]
    if unsupported_parts:
        raise ValueError(f"unsupported writable part: {unsupported_parts[0]}")
    for part_name in parts:
        if part_name not in body:
            raise ValueError(f"body.{part_name} is required for selected part")
    allowed_keys = {"id", *parts}
    unsupported_fields = [field for field in body if field not in allowed_keys]
    if unsupported_fields:
        raise ValueError(f"body.{unsupported_fields[0]} is read-only or unsupported")


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


def build_captions_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one caption
    track ``id`` and supports optional ``onBehalfOfContentOwner`` delegation
    while keeping ownership-sensitive delete guidance visible for higher-layer
    reuse.

    :return: Representative wrapper configured for `captions.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/captions/{id}",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("onBehalfOfContentOwner",),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the caption track being "
            "deleted, note that deletion remains ownership-sensitive even with "
            "authorized access, and treat `onBehalfOfContentOwner` as optional "
            "delegation context."
        ),
    )
    return CaptionsDeleteWrapper(metadata=metadata)


def _require_channel_banner_media(arguments: dict[str, object]) -> None:
    """Validate the supported `channelBanners.insert` media payload.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the media payload is missing, unsupported, or too large.
    """
    media = arguments.get("media")
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    assert isinstance(media, dict)  # Narrowed by the validator above.
    mime_type = str(media.get("mimeType"))
    if mime_type not in _CHANNEL_BANNER_ALLOWED_MIME_TYPES:
        raise ValueError("media.mimeType must be image/jpeg, image/png, or application/octet-stream")
    content = media.get("content")
    content_bytes = content if isinstance(content, bytes) else str(content).encode("utf-8")
    if not content_bytes:
        raise ValueError("media.content is required")
    if len(content_bytes) > _CHANNEL_BANNER_MAX_BYTES:
        raise ValueError("media.content exceeds the 6 MB channel banner limit")


def build_channel_banners_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelBanners.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires one `media`
    upload payload, supports optional `onBehalfOfContentOwner` delegation on
    authorized requests, and keeps image constraints plus the returned response
    URL visible for higher-layer reuse.

    :return: Representative wrapper configured for `channelBanners.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="channelBanners",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/channelBanners/insert",
        request_shape=EndpointRequestShape(
            required_fields=("media",),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_channel_banner_media,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `media` for the banner image "
            "upload payload, keep the documented 16:9 image constraints, 6 MB "
            "size limit, and accepted MIME types visible for review, treat "
            "`onBehalfOfContentOwner` as optional delegation context, and "
            "preserve the returned response URL for later `channels.update` reuse."
        ),
    )
    return ChannelBannersInsertWrapper(metadata=metadata)
