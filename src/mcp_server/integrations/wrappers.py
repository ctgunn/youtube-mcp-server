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
_CHANNEL_SECTIONS_PLAYLIST_TYPES = frozenset({"singlePlaylist", "multiplePlaylists"})
_CHANNEL_SECTIONS_CHANNEL_TYPES = frozenset({"multipleChannels"})
_CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES = frozenset({"multiplePlaylists", "multipleChannels"})
_SEARCH_RESTRICTED_FIELDS = frozenset({"forContentOwner", "forDeveloper", "forMine"})
_SEARCH_VIDEO_ONLY_FIELDS = frozenset(
    {
        "videoCaption",
        "videoDefinition",
        "videoDuration",
        "videoEmbeddable",
        "videoLicense",
        "videoPaidProductPlacement",
        "videoSyndicated",
        "videoType",
    }
)


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
class SubscriptionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `subscriptions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public selector
    paths through ``channelId`` and ``id`` and OAuth-backed retrieval through
    ``mine``, ``myRecentSubscribers``, and ``mySubscribers`` with selector-aware
    paging and ordering rules kept visible for maintainers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `subscriptions.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector in {"mine", "myRecentSubscribers", "mySubscribers"} and auth_context.mode is not AuthMode.OAUTH_REQUIRED:
            raise ValueError(f"{selector} requires oauth_required auth")
        if selector in {"channelId", "id"} and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one subscriptions request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``channelId``, ``id``, ``mine``, ``myRecentSubscribers``, or ``mySubscribers``.
        :raises ValueError: If no selector is present.
        """
        for field in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if value is True:
                return field
        raise ValueError(
            "exactly one selector is required from: channelId, id, mine, myRecentSubscribers, mySubscribers"
        )


@dataclass(frozen=True)
class SearchListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `search.list`.

    Official quota cost: ``100`` quota units. The wrapper supports public
    API-key search for standard queries and restricted-filter searches that
    require stronger authorization.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `search.list` with filter-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selected search path requires a different auth mode.
        """
        if self._uses_restricted_filters(arguments):
            if auth_context.mode is not AuthMode.OAUTH_REQUIRED:
                raise ValueError("restricted search filters require oauth_required auth")
        elif auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("public search requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    @staticmethod
    def _uses_restricted_filters(arguments: dict[str, Any]) -> bool:
        """Return whether one search request uses a restricted auth path.

        :param arguments: Wrapper arguments to inspect.
        :return: ``True`` when any restricted filter is present.
        """
        return any(
            (arguments.get(field) is True) or (isinstance(arguments.get(field), str) and str(arguments.get(field)).strip())
            for field in _SEARCH_RESTRICTED_FIELDS
        )


@dataclass(frozen=True)
class CommentsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `comments.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports direct comment
    lookup through ``id`` and reply lookup through ``parentId`` on public API
    key requests.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `comments.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector in {"id", "parentId"} and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one comments request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``id`` or ``parentId``.
        :raises ValueError: If no selector is present.
        """
        for field in ("id", "parentId"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if isinstance(value, (list, tuple)) and value:
                return field
        raise ValueError("comments.list requires a supported selector")


@dataclass(frozen=True)
class CommentThreadsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `commentThreads.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports thread lookup
    through ``videoId``, ``allThreadsRelatedToChannelId``, and ``id`` on
    public API-key requests.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `commentThreads.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector in {"videoId", "allThreadsRelatedToChannelId", "id"} and auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one comment-threads request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``videoId``, ``allThreadsRelatedToChannelId``, or ``id``.
        :raises ValueError: If no selector is present.
        """
        for field in ("videoId", "allThreadsRelatedToChannelId", "id"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if isinstance(value, (list, tuple)) and value:
                return field
        raise ValueError("commentThreads.list requires a supported selector")


@dataclass(frozen=True)
class GuideCategoriesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `guideCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    region-scoped lookup using ``part`` plus ``regionCode`` on public API-key
    requests while keeping deprecated lifecycle caveats visible for reviewers.
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


@dataclass(frozen=True)
class I18nLanguagesListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `i18nLanguages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-language lookup using ``part`` plus ``hl`` on public API-key
    requests and keeps localization guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `i18nLanguages.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("i18nLanguages.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class I18nRegionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `i18nRegions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-region lookup using ``part`` plus ``hl`` on public API-key
    requests and keeps region guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `i18nRegions.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("i18nRegions.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class VideoAbuseReportReasonsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videoAbuseReportReasons.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one localized
    abuse-reason lookup using ``part`` plus ``hl`` on public API-key requests
    and keeps localization guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videoAbuseReportReasons.list` with API-key validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("videoAbuseReportReasons.list requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


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


@dataclass(frozen=True)
class VideosListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports direct video
    lookup through ``id``, chart-oriented collection retrieval through
    ``chart``, and caller-specific rating retrieval through ``myRating`` while
    keeping selector-aware auth and refinement guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.list` with selector-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selector requires a different auth mode.
        """
        selector = self._selected_selector(arguments)
        if selector == "myRating":
            if not auth_context.requires_oauth_access():
                raise ValueError("myRating requires oauth_required auth")
        elif auth_context.mode is not AuthMode.API_KEY:
            raise ValueError(f"{selector} requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    def _selected_selector(self, arguments: dict[str, Any]) -> str:
        """Return the active selector field for one videos request.

        :param arguments: Wrapper arguments to inspect.
        :return: One of ``id``, ``chart``, or ``myRating``.
        :raises ValueError: If no selector is present.
        """
        for field in ("id", "chart", "myRating"):
            value = arguments.get(field)
            if isinstance(value, str) and value.strip():
                return field
            if value is True:
                return field
        raise ValueError("videos.list requires a supported selector")


@dataclass(frozen=True)
class MembersListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `members.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    owner-only membership lookup using ``part`` plus ``mode`` on OAuth-backed
    requests and keeps owner-visibility guidance visible for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `members.list` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("members.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class MembershipsLevelsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `membershipsLevels.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    owner-only membership-level lookup using required ``part`` on
    OAuth-backed requests and keeps unsupported-modifier guidance visible
    for reviewers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `membershipsLevels.list` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("membershipsLevels.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


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
class CommentsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `comments.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a reply
    comment ``body`` payload aligned to ``body.snippet.parentId`` and
    ``body.snippet.textOriginal`` on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `comments.insert` with OAuth and reply-shape validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("comments.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CommentThreadsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `commentThreads.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a top-level
    comment-thread ``body`` payload aligned to ``body.snippet.videoId`` and
    ``body.snippet.topLevelComment.snippet.textOriginal`` on an authorized
    request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `commentThreads.insert` with OAuth and top-level validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("commentThreads.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CommentsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `comments.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    comment ``body`` payload aligned to ``body.id`` and
    ``body.snippet.textOriginal`` on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `comments.update` with OAuth and writable-field validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("comments.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CommentsSetModerationStatusWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `comments.setModerationStatus`.

    Official quota cost: ``50`` quota units. The wrapper uses query-only
    arguments with one or more comment ``id`` values, one
    ``moderationStatus`` value, optional ``banAuthor`` support when the
    moderation status is ``rejected``, and optional
    ``onBehalfOfContentOwner`` delegation on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `comments.setModerationStatus` with OAuth and state validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("comments.setModerationStatus requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


@dataclass(frozen=True)
class CommentsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `comments.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one comment
    ``id`` and supports optional ``onBehalfOfContentOwner`` delegation on an
    authorized request with target-state-sensitive behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `comments.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("comments.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)


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


@dataclass(frozen=True)
class ThumbnailsSetWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `thumbnails.set`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    ``videoId`` plus one ``media`` upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `thumbnails.set` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("thumbnails.set requires oauth_required auth")
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
class SubscriptionsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `subscriptions.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet.resourceId.channelId` target on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `subscriptions.insert` with OAuth and write validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("subscriptions.insert requires oauth_required auth")
        response = super().call(executor, arguments=arguments, auth_context=auth_context)
        response.setdefault("part", arguments.get("part"))
        response.setdefault("subscriptionId", response.get("id"))
        response.setdefault(
            "targetChannelId",
            _subscriptions_insert_target_channel_id(arguments, response),
        )
        response.setdefault(
            "targetResourceKind",
            _subscriptions_insert_target_resource_kind(arguments, response),
        )
        return response


@dataclass(frozen=True)
class SubscriptionsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `subscriptions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    subscription ``id`` on an authorized request with target-state-sensitive
    behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `subscriptions.delete` with OAuth and delete validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("subscriptions.delete requires oauth_required auth")
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


def build_comments_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `comments.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports direct comment
    lookup through ``id``, reply lookup through ``parentId``, and optional
    pagination and text-format modifiers on API-key requests.

    :return: Representative wrapper configured for `comments.list`.
    """
    metadata = EndpointMetadata(
        resource_name="comments",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/comments",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("id", "parentId", "pageToken", "maxResults", "textFormat"),
            exactly_one_of=("id", "parentId"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Use `id` for direct comment lookup, use `parentId` for reply "
            "lookup under one parent comment, treat selector combinations as "
            "mutually exclusive, allow `pageToken`, `maxResults`, and "
            "`textFormat` as optional near-raw modifiers, and preserve empty "
            "result sets as successful no-match outcomes."
        ),
    )
    return CommentsListWrapper(metadata=metadata)


def build_search_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `search.list`.

    Official quota cost: ``100`` quota units. The wrapper requires ``part``
    plus ``q`` for baseline search, keeps near-raw search refinements
    reviewable, and documents restricted filters that require stronger
    authorization.

    :return: Representative wrapper configured for `search.list`.
    """
    metadata = EndpointMetadata(
        resource_name="search",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/search",
        request_shape=EndpointRequestShape(
            required_fields=("part", "q"),
            optional_fields=(
                "channelId",
                "forContentOwner",
                "forDeveloper",
                "forMine",
                "publishedAfter",
                "publishedBefore",
                "regionCode",
                "relevanceLanguage",
                "safeSearch",
                "type",
                "videoCaption",
                "videoDefinition",
                "videoDuration",
                "videoEmbeddable",
                "videoLicense",
                "videoPaidProductPlacement",
                "videoSyndicated",
                "videoType",
                "order",
                "pageToken",
                "maxResults",
            ),
            validators=(_require_search_list_arguments,),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=100,
        lifecycle_state="inconsistent-docs",
        caveat_note=(
            "Official quota guidance differs between public overview and "
            "endpoint reference pages for `search.list`."
        ),
        auth_condition_note=(
            "Use API-key auth for baseline public search requests. Use "
            "`forContentOwner`, `forDeveloper`, or `forMine` only when "
            "oauth_required auth is available."
        ),
        notes=(
            "Requires `part` plus `q` for one deterministic search request, "
            "keeps `type`, pagination, date filtering, and language or region "
            "refinements reviewable, rejects undocumented modifiers, preserves "
            "empty result sets as successful no-match outcomes, and keeps the "
            "high-cost quota guidance visible for later reuse."
        ),
    )
    return SearchListWrapper(metadata=metadata)


def build_subscriptions_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `subscriptions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports public
    subscription lookup through ``channelId`` and ``id`` and OAuth-backed
    retrieval through ``mine``, ``myRecentSubscribers``, and
    ``mySubscribers``, while limiting paging and ordering inputs to
    collection lookups.

    :return: Representative wrapper configured for `subscriptions.list`.
    """
    metadata = EndpointMetadata(
        resource_name="subscriptions",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/subscriptions",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=(
                "channelId",
                "id",
                "mine",
                "myRecentSubscribers",
                "mySubscribers",
                "pageToken",
                "maxResults",
                "order",
            ),
            exactly_one_of=("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers"),
            validators=(_require_subscriptions_list_arguments,),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `channelId` or `id` for public-compatible subscription lookup "
            "paths. Use `mine`, `myRecentSubscribers`, or `mySubscribers` for "
            "owner-scoped or subscriber-management retrieval with "
            "oauth_required auth."
        ),
        notes=(
            "Requires required `part` plus exactly one selector from "
            "`channelId`, `id`, `mine`, `myRecentSubscribers`, or "
            "`mySubscribers` for one deterministic subscription lookup, "
            "allows `pageToken`, `maxResults`, and `order` only for "
            "collection-style lookups, rejects undocumented modifiers, and "
            "preserves empty result sets as successful outcomes."
        ),
    )
    return SubscriptionsListWrapper(metadata=metadata)


def build_subscriptions_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `subscriptions.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a writable
    `body.snippet.resourceId.channelId` target on authorized requests, keeps
    `part=snippet` explicit for maintainers, and rejects unsupported optional
    write fields unless the contract is deliberately expanded.

    :return: Representative wrapper configured for `subscriptions.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="subscriptions",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/subscriptions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_subscriptions_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Keep `part=snippet` explicit, use "
            "`body.snippet.resourceId.channelId` for the required target "
            "channel, allow `body.snippet.resourceId.kind` only when it is "
            "`youtube#channel`, and reject unsupported optional fields such as "
            "`body.title`, `body.status`, or extra `body.snippet` mappings "
            "unless they are explicitly added to the contract."
        ),
    )
    return SubscriptionsInsertWrapper(metadata=metadata)


def build_subscriptions_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `subscriptions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    subscription ``id`` on authorized requests, keeps the destructive delete
    boundary visible for review, and preserves target-state-sensitive guidance
    for downstream reuse.

    :return: Representative wrapper configured for `subscriptions.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="subscriptions",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/subscriptions",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_subscriptions_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the subscription "
            "relationship being deleted, keep requests scoped to one target "
            "subscription at a time, and note that deletion remains target-"
            "state sensitive even with authorized access."
        ),
    )
    return SubscriptionsDeleteWrapper(metadata=metadata)


def build_comment_threads_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `commentThreads.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports thread lookup
    through ``videoId``, ``allThreadsRelatedToChannelId``, and ``id`` with
    optional pagination, ordering, search-term, and text-format modifiers on
    API-key requests.

    :return: Representative wrapper configured for `commentThreads.list`.
    """
    metadata = EndpointMetadata(
        resource_name="commentThreads",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/commentThreads",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=(
                "videoId",
                "allThreadsRelatedToChannelId",
                "id",
                "pageToken",
                "maxResults",
                "order",
                "searchTerms",
                "textFormat",
            ),
            exactly_one_of=("videoId", "allThreadsRelatedToChannelId", "id"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Use `videoId` for video-based thread lookup, use "
            "`allThreadsRelatedToChannelId` for channel-related thread lookup, "
            "use `id` for direct thread lookup, treat selector combinations as "
            "mutually exclusive, allow `pageToken`, `maxResults`, `order`, "
            "`searchTerms`, and `textFormat` as optional near-raw modifiers, "
            "and preserve empty result sets as successful no-match outcomes."
        ),
    )
    return CommentThreadsListWrapper(metadata=metadata)


def build_guide_categories_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `guideCategories.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    region-scoped lookup through ``part`` plus ``regionCode`` on API-key
    requests and keeps deprecated-or-unavailable lifecycle guidance visible.

    :return: Representative wrapper configured for `guideCategories.list`.
    """
    metadata = EndpointMetadata(
        resource_name="guideCategories",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/guideCategories",
        request_shape=EndpointRequestShape(
            required_fields=("part", "regionCode"),
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
            "Requires `part` plus `regionCode` for one deterministic "
            "region-scoped lookup, rejects undocumented modifiers, preserves "
            "empty result sets as successful outcomes, and keeps lifecycle "
            "caveats visible for reuse decisions."
        ),
    )
    return GuideCategoriesListWrapper(metadata=metadata)


def build_i18n_languages_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `i18nLanguages.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-language lookup through ``part`` plus ``hl`` on API-key
    requests and keeps localization guidance visible.

    :return: Representative wrapper configured for `i18nLanguages.list`.
    """
    metadata = EndpointMetadata(
        resource_name="i18nLanguages",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/i18nLanguages",
        request_shape=EndpointRequestShape(
            required_fields=("part", "hl"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` plus `hl` for one deterministic localization "
            "lookup, rejects undocumented modifiers, preserves empty result "
            "sets as successful outcomes, and keeps localization guidance "
            "visible for reuse decisions."
        ),
    )
    return I18nLanguagesListWrapper(metadata=metadata)


def build_i18n_regions_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `i18nRegions.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    localization-region lookup through ``part`` plus ``hl`` on API-key
    requests and keeps region guidance visible.

    :return: Representative wrapper configured for `i18nRegions.list`.
    """
    metadata = EndpointMetadata(
        resource_name="i18nRegions",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/i18nRegions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "hl"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` plus `hl` for one deterministic region "
            "lookup, rejects undocumented modifiers, preserves empty result "
            "sets as successful outcomes, and keeps region guidance "
            "visible for reuse decisions."
        ),
    )
    return I18nRegionsListWrapper(metadata=metadata)


def build_video_abuse_report_reasons_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videoAbuseReportReasons.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one localized
    abuse-reason lookup through ``part`` plus ``hl`` on API-key requests and
    keeps localization guidance visible.

    :return: Representative wrapper configured for `videoAbuseReportReasons.list`.
    """
    metadata = EndpointMetadata(
        resource_name="videoAbuseReportReasons",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/videoAbuseReportReasons",
        request_shape=EndpointRequestShape(
            required_fields=("part", "hl"),
        ),
        auth_mode=AuthMode.API_KEY,
        quota_cost=1,
        notes=(
            "Requires `part` plus `hl` for one deterministic localization "
            "lookup, rejects undocumented modifiers, preserves empty result "
            "sets as successful outcomes, and keeps localization guidance "
            "visible for reuse decisions."
        ),
    )
    return VideoAbuseReportReasonsListWrapper(metadata=metadata)


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


def build_videos_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports exact lookup
    through ``id``, chart-oriented retrieval through ``chart``, and
    caller-specific retrieval through ``myRating`` while making selector-aware
    auth and refinement boundaries reviewable.

    :return: Representative wrapper configured for `videos.list`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/videos",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("id", "chart", "myRating", "pageToken", "maxResults", "regionCode", "videoCategoryId"),
            exactly_one_of=("id", "chart", "myRating"),
            validators=(_require_videos_list_arguments,),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=1,
        auth_condition_note=(
            "Use `id` or `chart` for public-compatible retrieval with api_key auth. "
            "Use `myRating` for caller-specific retrieval with oauth_required auth."
        ),
        notes=(
            "Requires `part` plus exactly one selector from `id`, `chart`, or "
            "`myRating`, allows `pageToken` and `maxResults` only for chart or "
            "`myRating` collection lookups, treats `regionCode` and "
            "`videoCategoryId` as chart-only refinements, rejects undocumented "
            "modifiers, and preserves empty result sets as successful outcomes."
        ),
    )
    return VideosListWrapper(metadata=metadata)


def build_members_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `members.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    owner-only membership lookup through ``part`` plus ``mode`` on
    OAuth-required requests and keeps delegation boundaries visible.

    :return: Representative wrapper configured for `members.list`.
    """
    metadata = EndpointMetadata(
        resource_name="members",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/members",
        request_shape=EndpointRequestShape(
            required_fields=("part", "mode"),
            optional_fields=("pageToken", "maxResults"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        notes=(
            "Requires `part` plus `mode` for one deterministic owner-only "
            "membership lookup, allows optional `pageToken` and `maxResults` "
            "within the documented boundary, rejects undocumented modifiers, "
            "treats delegation-related inputs as unsupported in this slice, "
            "and preserves empty result sets as successful outcomes."
        ),
    )
    return MembersListWrapper(metadata=metadata)


def build_memberships_levels_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `membershipsLevels.list`.

    Official quota cost: ``1`` quota unit. The wrapper supports one
    owner-only membership-level lookup through required ``part`` on
    OAuth-required requests and rejects undocumented modifiers.

    :return: Representative wrapper configured for `membershipsLevels.list`.
    """
    metadata = EndpointMetadata(
        resource_name="membershipsLevels",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/membershipsLevels",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        notes=(
            "Requires required `part` for one deterministic owner-only "
            "membership-level lookup, treats undocumented filters, paging "
            "inputs, and delegation-related modifiers as unsupported, and "
            "preserves empty result sets as successful outcomes."
        ),
    )
    return MembershipsLevelsListWrapper(metadata=metadata)


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
            "the referenced video, keep the minimum writable `snippet` "
            "boundary visible for review, and reject unsupported optional "
            "placement or content-details fields unless explicitly added to "
            "the contract."
        ),
    )
    return PlaylistItemsInsertWrapper(metadata=metadata)


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


def build_comments_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `comments.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    reply payload, keeps `body.snippet.parentId` and
    `body.snippet.textOriginal` visible for review, and treats
    `onBehalfOfContentOwner` as optional delegation context.

    :return: Representative wrapper configured for `comments.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="comments",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/comments",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_comments_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.snippet.parentId` for the "
            "comment being answered, use `body.snippet.textOriginal` for reply "
            "content, reject unsupported top-level comment-create shapes, and "
            "treat `onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CommentsInsertWrapper(metadata=metadata)


def build_comment_threads_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `commentThreads.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires a video-
    targeted top-level thread ``body``, keeps ``body.snippet.videoId`` and
    ``body.snippet.topLevelComment.snippet.textOriginal`` visible for review,
    and treats ``onBehalfOfContentOwner`` as optional delegation context.

    :return: Representative wrapper configured for `commentThreads.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="commentThreads",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/commentThreads",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_comment_threads_insert_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.snippet.videoId` for the "
            "supported discussion target, use "
            "`body.snippet.topLevelComment.snippet.textOriginal` for top-level "
            "comment content, reject reply-style or mixed comment-thread "
            "create shapes, and treat `onBehalfOfContentOwner` as optional "
            "delegation context."
        ),
    )
    return CommentThreadsInsertWrapper(metadata=metadata)


def build_comments_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `comments.update`.

    Official quota cost: ``50`` quota units. The wrapper requires a `body`
    update payload, keeps `body.id` and `body.snippet.textOriginal` visible
    for review, and treats `onBehalfOfContentOwner` as optional delegation
    context.

    :return: Representative wrapper configured for `comments.update`.
    """
    metadata = EndpointMetadata(
        resource_name="comments",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/comments",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_comments_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.id` to identify the "
            "existing comment being updated, use `body.snippet.textOriginal` "
            "for writable updated comment content, reject unsupported or "
            "read-only comment fields, and treat `onBehalfOfContentOwner` as "
            "optional delegation context."
        ),
    )
    return CommentsUpdateWrapper(metadata=metadata)


def build_comments_set_moderation_status_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `comments.setModerationStatus`.

    Official quota cost: ``50`` quota units. The wrapper uses query-only
    moderation arguments through `id` and `moderationStatus`, supports
    `published`, `heldForReview`, and `rejected`, allows `banAuthor` only
    when `moderationStatus` is `rejected`, and treats
    `onBehalfOfContentOwner` as optional delegation context.

    :return: Representative wrapper configured for `comments.setModerationStatus`.
    """
    metadata = EndpointMetadata(
        resource_name="comments",
        operation_name="setModerationStatus",
        http_method="POST",
        path_shape="/youtube/v3/comments/setModerationStatus",
        request_shape=EndpointRequestShape(
            required_fields=("id", "moderationStatus"),
            optional_fields=("banAuthor", "onBehalfOfContentOwner"),
            validators=(
                _require_comments_set_moderation_status_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use query-only `id` values for one "
            "or more target comments, use `moderationStatus` with supported "
            "`published`, `heldForReview`, or `rejected` outcomes, allow "
            "`banAuthor` only when moderationStatus is `rejected`, and treat "
            "`onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CommentsSetModerationStatusWrapper(metadata=metadata)


def build_comments_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `comments.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one comment
    `id`, supports optional `onBehalfOfContentOwner` delegation, and keeps
    destructive delete guidance visible for higher-layer reuse.

    :return: Representative wrapper configured for `comments.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="comments",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/comments",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_comments_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the comment being "
            "deleted, keep requests scoped to one target comment at a time, "
            "note that deletion remains target-state sensitive even with "
            "authorized access, and treat `onBehalfOfContentOwner` as "
            "optional delegation context."
        ),
    )
    return CommentsDeleteWrapper(metadata=metadata)


def _validated_reference_values(
    raw_values: object,
    *,
    reference_label: str,
    required_message: str,
    duplicate_message: str,
) -> tuple[str, ...]:
    """Return validated channel or playlist references from one request body.

    :param raw_values: Candidate list-like value from ``contentDetails``.
    :param reference_label: Human-readable label for one reference type.
    :param required_message: Validation message used when no usable values exist.
    :param duplicate_message: Validation message used when duplicates appear.
    :return: Normalized ordered references without duplicates.
    :raises ValueError: If the list is missing, empty, malformed, or duplicated.
    """
    if not isinstance(raw_values, list):
        raise ValueError(required_message)
    values: list[str] = []
    for raw_value in raw_values:
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ValueError(required_message)
        normalized = raw_value.strip()
        if normalized in values:
            raise ValueError(duplicate_message)
        values.append(normalized)
    if not values:
        raise ValueError(required_message)
    return tuple(values)


def _validate_channel_sections_body(
    arguments: dict[str, object],
    *,
    require_existing_id: bool,
) -> None:
    """Validate the supported channel-sections write request body.

    :param arguments: Wrapper arguments to validate.
    :param require_existing_id: Whether the request body must identify an existing section.
    :raises ValueError: If the request body does not match supported section rules.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    supported_body_fields = {"snippet", "contentDetails"}
    if require_existing_id:
        supported_body_fields = {"id", *supported_body_fields}
    unsupported_fields = [field for field in body if field not in supported_body_fields]
    if unsupported_fields:
        raise ValueError(f"body.{unsupported_fields[0]} is read-only or unsupported")

    if require_existing_id:
        raw_id = body.get("id")
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_type = snippet.get("type")
    if not isinstance(raw_type, str) or not raw_type.strip():
        raise ValueError("body.snippet.type is required")
    section_type = raw_type.strip()

    raw_channel_id = snippet.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("body.snippet.channelId is required")

    title = snippet.get("title")
    if section_type in _CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES:
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{section_type} requires body.snippet.title")

    content_details = body.get("contentDetails")
    if section_type in _CHANNEL_SECTIONS_PLAYLIST_TYPES:
        if not isinstance(content_details, dict):
            raise ValueError("body.contentDetails.playlists is required")
        if content_details.get("channels") not in (None, [], ()):
            raise ValueError(f"{section_type} does not accept body.contentDetails.channels")
        playlist_ids = _validated_reference_values(
            content_details.get("playlists"),
            reference_label="playlist",
            required_message="body.contentDetails.playlists is required",
            duplicate_message="duplicate playlist references are unsupported",
        )
        if section_type == "singlePlaylist" and len(playlist_ids) != 1:
            raise ValueError("singlePlaylist requires exactly one playlist id")
        return

    if section_type in _CHANNEL_SECTIONS_CHANNEL_TYPES:
        if not isinstance(content_details, dict):
            raise ValueError("body.contentDetails.channels is required")
        if content_details.get("playlists") not in (None, [], ()):
            raise ValueError(f"{section_type} does not accept body.contentDetails.playlists")
        _validated_reference_values(
            content_details.get("channels"),
            reference_label="channel",
            required_message="body.contentDetails.channels is required",
            duplicate_message="duplicate channel references are unsupported",
        )
        return

    if not isinstance(content_details, dict):
        return
    if content_details.get("playlists") not in (None, [], ()):
        raise ValueError(f"{section_type} does not accept body.contentDetails.playlists")
    if content_details.get("channels") not in (None, [], ()):
        raise ValueError(f"{section_type} does not accept body.contentDetails.channels")


def _require_channel_sections_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channelSections.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported section rules.
    """
    _validate_channel_sections_body(arguments, require_existing_id=False)


def _require_comments_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported reply rules.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_parent_id = snippet.get("parentId")
    if not isinstance(raw_parent_id, str) or not raw_parent_id.strip():
        raise ValueError("body.snippet.parentId is required")

    raw_reply_text = snippet.get("textOriginal")
    if not isinstance(raw_reply_text, str) or not raw_reply_text.strip():
        raise ValueError("body.snippet.textOriginal is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"parentId", "textOriginal"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _require_comment_threads_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `commentThreads.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported top-level rules.
    """
    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_video_id = snippet.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.videoId is required")

    top_level_comment = snippet.get("topLevelComment")
    if not isinstance(top_level_comment, dict):
        raise ValueError("body.snippet.topLevelComment is required")

    top_level_snippet = top_level_comment.get("snippet")
    if not isinstance(top_level_snippet, dict):
        raise ValueError("body.snippet.topLevelComment.snippet is required")

    raw_comment_text = top_level_snippet.get("textOriginal")
    if not isinstance(raw_comment_text, str) or not raw_comment_text.strip():
        raise ValueError("body.snippet.topLevelComment.snippet.textOriginal is required")

    unsupported_top_level_fields = [
        field for field in top_level_comment if field not in {"kind", "snippet"}
    ]
    if unsupported_top_level_fields:
        raise ValueError(
            f"body.snippet.topLevelComment.{unsupported_top_level_fields[0]} is read-only or unsupported"
        )

    unsupported_top_level_snippet_fields = [
        field for field in top_level_snippet if field not in {"textOriginal"}
    ]
    if unsupported_top_level_snippet_fields:
        raise ValueError(
            "body.snippet.topLevelComment.snippet."
            f"{unsupported_top_level_snippet_fields[0]} is read-only or unsupported"
        )

    unsupported_snippet_fields = [field for field in snippet if field not in {"videoId", "topLevelComment"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _require_comments_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_comment_id = body.get("id")
    if not isinstance(raw_comment_id, str) or not raw_comment_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_reply_text = snippet.get("textOriginal")
    if not isinstance(raw_reply_text, str) or not raw_reply_text.strip():
        raise ValueError("body.snippet.textOriginal is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"textOriginal"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _require_playlist_images_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlistImages.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging fields are supplied for non-playlist lookups.
    """
    has_playlist_selector = isinstance(arguments.get("playlistId"), str) and bool(
        str(arguments.get("playlistId")).strip()
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_playlist_selector:
        raise ValueError("paging fields are only supported for playlistId lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for playlistId lookups")


def _require_playlist_items_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlistItems.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging fields are supplied for non-playlist lookups.
    """
    has_playlist_selector = isinstance(arguments.get("playlistId"), str) and bool(
        str(arguments.get("playlistId")).strip()
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_playlist_selector:
        raise ValueError("paging fields are only supported for playlistId lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for playlistId lookups")


def _require_playlists_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `playlists.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging fields are supplied for direct ID lookups.
    """
    has_collection_selector = any(
        (
            isinstance(arguments.get("channelId"), str) and bool(str(arguments.get("channelId")).strip()),
            arguments.get("mine") is True,
        )
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_collection_selector:
        raise ValueError("paging fields are only supported for channelId or mine lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for channelId or mine lookups")


def _require_search_list_arguments(arguments: dict[str, object]) -> None:
    """Validate supported argument combinations for `search.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If restricted filters conflict or video filters lack `type=video`.
    """
    restricted_filters = [
        field
        for field in _SEARCH_RESTRICTED_FIELDS
        if (arguments.get(field) is True)
        or (isinstance(arguments.get(field), str) and bool(str(arguments.get(field)).strip()))
    ]
    if len(restricted_filters) > 1:
        raise ValueError("restricted search filters are mutually exclusive")

    uses_video_only_filters = any(
        arguments.get(field) not in (None, "")
        for field in _SEARCH_VIDEO_ONLY_FIELDS
    )
    search_type = str(arguments.get("type", "")).strip()
    if uses_video_only_filters and search_type != "video":
        raise ValueError("video-specific refinements require type=video")


def _require_videos_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `videos.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If unsupported refinements are supplied for the selector path.
    """
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_chart_selector = isinstance(arguments.get("chart"), str) and bool(str(arguments.get("chart")).strip())
    has_rating_selector = isinstance(arguments.get("myRating"), str) and bool(str(arguments.get("myRating")).strip())
    has_collection_selector = has_chart_selector or has_rating_selector
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    if has_paging and not has_collection_selector:
        raise ValueError("paging fields are only supported for chart or myRating lookups")
    if has_id_selector and has_paging:
        raise ValueError("paging fields are only supported for chart or myRating lookups")

    has_chart_refinements = any(
        arguments.get(field) not in (None, "")
        for field in ("regionCode", "videoCategoryId")
    )
    if has_chart_refinements and not has_chart_selector:
        raise ValueError("chart-only refinements require chart lookup")


def _require_subscriptions_list_arguments(arguments: dict[str, object]) -> None:
    """Validate selector-specific arguments for `subscriptions.list`.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If paging or ordering fields are supplied for direct ID lookups.
    """
    has_collection_selector = any(
        (
            isinstance(arguments.get("channelId"), str) and bool(str(arguments.get("channelId")).strip()),
            arguments.get("mine") is True,
            arguments.get("myRecentSubscribers") is True,
            arguments.get("mySubscribers") is True,
        )
    )
    has_id_selector = isinstance(arguments.get("id"), str) and bool(str(arguments.get("id")).strip())
    has_paging = any(arguments.get(field) not in (None, "") for field in ("pageToken", "maxResults"))
    has_order = arguments.get("order") not in (None, "")
    if has_paging and not has_collection_selector:
        raise ValueError(
            "paging fields are only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_id_selector and has_paging:
        raise ValueError(
            "paging fields are only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_order and not has_collection_selector:
        raise ValueError(
            "order is only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )
    if has_id_selector and has_order:
        raise ValueError(
            "order is only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups"
        )


def _require_subscriptions_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `subscriptions.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported create rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_channel_id = resource_id.get("channelId")
    if not isinstance(raw_channel_id, str) or not raw_channel_id.strip():
        raise ValueError("body.snippet.resourceId.channelId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#channel"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#channel when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "channelId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )


def _require_subscriptions_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `subscriptions.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_subscription_id = arguments.get("id")
    if not isinstance(raw_subscription_id, str) or not raw_subscription_id.strip():
        raise ValueError("id must identify one subscription")


def _subscriptions_insert_target_channel_id(
    arguments: dict[str, object],
    response: dict[str, Any],
) -> str | None:
    """Return the stable target channel identifier for one create response.

    :param arguments: Wrapper arguments used for the request.
    :param response: Successful response payload to normalize.
    :return: Target channel identifier when one is available.
    """
    response_snippet = response.get("snippet")
    if isinstance(response_snippet, dict):
        response_resource_id = response_snippet.get("resourceId")
        if isinstance(response_resource_id, dict):
            channel_id = response_resource_id.get("channelId")
            if isinstance(channel_id, str) and channel_id.strip():
                return channel_id

    body = arguments.get("body")
    if isinstance(body, dict):
        snippet = body.get("snippet")
        if isinstance(snippet, dict):
            resource_id = snippet.get("resourceId")
            if isinstance(resource_id, dict):
                channel_id = resource_id.get("channelId")
                if isinstance(channel_id, str) and channel_id.strip():
                    return channel_id
    return None


def _subscriptions_insert_target_resource_kind(
    arguments: dict[str, object],
    response: dict[str, Any],
) -> str:
    """Return the stable target resource kind for one create response.

    :param arguments: Wrapper arguments used for the request.
    :param response: Successful response payload to normalize.
    :return: Target resource kind with the channel default preserved.
    """
    response_snippet = response.get("snippet")
    if isinstance(response_snippet, dict):
        response_resource_id = response_snippet.get("resourceId")
        if isinstance(response_resource_id, dict):
            resource_kind = response_resource_id.get("kind")
            if isinstance(resource_kind, str) and resource_kind.strip():
                return resource_kind

    body = arguments.get("body")
    if isinstance(body, dict):
        snippet = body.get("snippet")
        if isinstance(snippet, dict):
            resource_id = snippet.get("resourceId")
            if isinstance(resource_id, dict):
                resource_kind = resource_id.get("kind")
                if isinstance(resource_kind, str) and resource_kind.strip():
                    return resource_kind
    return "youtube#channel"


def _require_playlist_items_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported create rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_video_id = resource_id.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.resourceId.videoId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#video"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#video when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "videoId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )


def _require_playlists_insert_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.insert` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported create rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("snippet",))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_title = snippet.get("title")
    if not isinstance(raw_title, str) or not raw_title.strip():
        raise ValueError("body.snippet.title is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"title"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _require_playlists_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_playlist_id = body.get("id")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_title = snippet.get("title")
    if not isinstance(raw_title, str) or not raw_title.strip():
        raise ValueError("body.snippet.title is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"title"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _require_playlist_items_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    part = str(arguments.get("part", "")).strip()
    if part != "snippet":
        raise ValueError("unsupported writable part: only snippet is supported")

    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_playlist_item_id = body.get("id")
    if not isinstance(raw_playlist_item_id, str) or not raw_playlist_item_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    resource_id = snippet.get("resourceId")
    if not isinstance(resource_id, dict):
        raise ValueError("body.snippet.resourceId is required")

    raw_video_id = resource_id.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("body.snippet.resourceId.videoId is required")

    resource_kind = resource_id.get("kind")
    if resource_kind not in (None, "", "youtube#video"):
        raise ValueError("body.snippet.resourceId.kind must be youtube#video when provided")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "resourceId"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")

    unsupported_resource_fields = [field for field in resource_id if field not in {"kind", "videoId"}]
    if unsupported_resource_fields:
        raise ValueError(
            f"body.snippet.resourceId.{unsupported_resource_fields[0]} is read-only or unsupported"
        )


def _require_playlist_items_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistItems.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_item_id = arguments.get("id")
    if not isinstance(raw_playlist_item_id, str) or not raw_playlist_item_id.strip():
        raise ValueError("id must identify one playlist item")


def _require_playlists_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlists.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_id = arguments.get("id")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("id must identify one playlist")


def _require_playlist_images_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistImages.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    require_mapping_fields("body", required_keys=("id", "snippet"))(arguments)
    body = arguments.get("body")
    assert isinstance(body, dict)  # Narrowed by validator above.
    unsupported_body_fields = [field for field in body if field not in {"id", "kind", "snippet"}]
    if unsupported_body_fields:
        raise ValueError(f"body.{unsupported_body_fields[0]} is read-only or unsupported")

    raw_playlist_image_id = body.get("id")
    if not isinstance(raw_playlist_image_id, str) or not raw_playlist_image_id.strip():
        raise ValueError("body.id is required")

    snippet = body.get("snippet")
    if not isinstance(snippet, dict):
        raise ValueError("body.snippet is required")

    raw_playlist_id = snippet.get("playlistId")
    if not isinstance(raw_playlist_id, str) or not raw_playlist_id.strip():
        raise ValueError("body.snippet.playlistId is required")

    unsupported_snippet_fields = [field for field in snippet if field not in {"playlistId", "type"}]
    if unsupported_snippet_fields:
        raise ValueError(f"body.snippet.{unsupported_snippet_fields[0]} is read-only or unsupported")


def _validated_comment_ids(raw_values: object) -> tuple[str, ...]:
    """Return validated comment identifiers for moderation requests.

    :param raw_values: Candidate comment identifier value or collection.
    :return: Normalized ordered comment identifiers without duplicates.
    :raises ValueError: If no usable identifiers are present or duplicates appear.
    """
    if isinstance(raw_values, str):
        values = [raw_values]
    elif isinstance(raw_values, (list, tuple)):
        values = list(raw_values)
    else:
        raise ValueError("id must contain at least one comment identifier")

    normalized_ids: list[str] = []
    for raw_value in values:
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ValueError("id must contain at least one comment identifier")
        normalized = raw_value.strip()
        if normalized in normalized_ids:
            raise ValueError("duplicate comment identifiers are unsupported")
        normalized_ids.append(normalized)
    if not normalized_ids:
        raise ValueError("id must contain at least one comment identifier")
    return tuple(normalized_ids)


def _require_comments_set_moderation_status_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.setModerationStatus` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the moderation request is incomplete or unsupported.
    """
    _validated_comment_ids(arguments.get("id"))

    raw_status = arguments.get("moderationStatus")
    if not isinstance(raw_status, str) or not raw_status.strip():
        raise ValueError("moderationStatus is required")
    moderation_status = raw_status.strip()
    supported_statuses = {"published", "heldForReview", "rejected"}
    if moderation_status not in supported_statuses:
        raise ValueError(f"unsupported moderationStatus: {moderation_status}")

    ban_author = arguments.get("banAuthor")
    if ban_author is not None and not isinstance(ban_author, bool):
        raise ValueError("banAuthor must be a boolean when provided")
    if ban_author and moderation_status != "rejected":
        raise ValueError("banAuthor is only supported when moderationStatus is rejected")


def _require_comments_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `comments.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_comment_id = arguments.get("id")
    if not isinstance(raw_comment_id, str) or not raw_comment_id.strip():
        raise ValueError("id must identify one comment")


def _require_playlist_images_delete_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `playlistImages.delete` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the delete request is incomplete or unsupported.
    """
    raw_playlist_image_id = arguments.get("id")
    if not isinstance(raw_playlist_image_id, str) or not raw_playlist_image_id.strip():
        raise ValueError("id must identify one playlist image")


def _require_channel_sections_update_body(arguments: dict[str, object]) -> None:
    """Validate the supported `channelSections.update` request body.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the request body does not match supported update rules.
    """
    _validate_channel_sections_body(arguments, require_existing_id=True)


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


def _require_thumbnails_set_arguments(arguments: dict[str, object]) -> None:
    """Validate the supported `thumbnails.set` request arguments.

    :param arguments: Wrapper arguments to validate.
    :raises ValueError: If the target or upload payload is incomplete.
    """
    raw_video_id = arguments.get("videoId")
    if not isinstance(raw_video_id, str) or not raw_video_id.strip():
        raise ValueError("videoId is required")
    require_mapping_fields("media", required_keys=("mimeType", "content"))(arguments)
    media = arguments.get("media")
    assert isinstance(media, dict)  # Narrowed by validator above.
    mime_type = media.get("mimeType")
    if not isinstance(mime_type, str) or not mime_type.strip():
        raise ValueError("media.mimeType is required")
    content = media.get("content")
    content_bytes = content if isinstance(content, bytes) else str(content).encode("utf-8")
    if not content_bytes:
        raise ValueError("media.content is required")


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


def build_thumbnails_set_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `thumbnails.set`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    `videoId` plus one `media` upload payload on authorized requests and keeps
    the upload-sensitive update boundary visible for higher-layer reuse.

    :return: Representative wrapper configured for `thumbnails.set`.
    """
    metadata = EndpointMetadata(
        resource_name="thumbnails",
        operation_name="set",
        http_method="POST",
        path_shape="/youtube/v3/thumbnails/set",
        request_shape=EndpointRequestShape(
            required_fields=("videoId", "media"),
            validators=(
                _require_thumbnails_set_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `videoId` for the single target "
            "video, use `media` for thumbnail upload content, reject upload-only "
            "or target-only request shapes, and keep the update boundary visible "
            "for review."
        ),
    )
    return ThumbnailsSetWrapper(metadata=metadata)


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
