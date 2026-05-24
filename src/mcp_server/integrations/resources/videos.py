# ruff: noqa: F405
"""Videos resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

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
class VideosInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.insert`.

    Official quota cost: ``1600`` quota units. The wrapper requires a `body`
    metadata payload plus a `media` upload payload on an authorized request and
    keeps upload-mode and audit/private-default caveat guidance visible.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class VideosUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.update`.

    Official quota cost: ``50`` quota units. The wrapper requires `body.id`
    for the existing video, keeps `part=snippet` explicit for maintainers,
    requires `body.snippet.title` for the minimum supported update path, and
    rejects unsupported optional write fields unless the contract is expanded.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.update` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class VideosRateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.rate`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    video ``id`` plus one supported ``rating`` action on an authorized request,
    keeps ``like``, ``dislike``, and ``none`` visible for maintainers, and
    rejects undocumented modifiers unless the contract is deliberately expanded.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.rate` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.rate requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class VideosGetRatingWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.getRating`.

    Official quota cost: ``1`` quota unit. The wrapper requires one or more
    comma-delimited video identifiers through ``id`` on an OAuth-backed
    request, keeps ``liked``, ``disliked``, and ``none`` visible for
    maintainers, and rejects undocumented identifier forms unless the
    contract is deliberately expanded.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.getRating` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.getRating requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class VideosReportAbuseWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.reportAbuse`.

    Official quota cost: ``50`` quota units. The wrapper requires an
    OAuth-backed request with ``body.videoId`` and ``body.reasonId``, supports
    ``body.secondaryReasonId``, ``body.comments``, and ``body.language`` as
    bounded optional report details, and rejects partner-only delegated query
    modifiers unless the contract is deliberately expanded.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.reportAbuse` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured report acknowledgement payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.reportAbuse requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class VideosDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `videos.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    video ``id`` on an OAuth-backed request, sends no request body, rejects
    delegated ``onBehalfOfContentOwner`` query behavior unless the contract is
    deliberately expanded, and keeps destructive acknowledgement semantics
    visible for maintainers.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `videos.delete` with OAuth-required validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured deletion acknowledgement payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("videos.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

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

def build_videos_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.insert`.

    Official quota cost: ``1600`` quota units. The wrapper requires a `body`
    metadata payload and a `media` upload payload on authorized requests,
    accepts reviewable `multipart` or `resumable` upload-mode guidance, and
    keeps the audit/private-default caveat visible for higher-layer reuse.

    :return: Representative wrapper configured for `videos.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/videos",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body", "media"),
            optional_fields=("uploadMode", "notifySubscribers", "onBehalfOfContentOwner"),
            validators=(
                _require_videos_insert_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1600,
        lifecycle_state="limited",
        caveat_note=(
            "New uploads may remain private or otherwise audit-constrained until "
            "the caller completes the required review or release workflow."
        ),
        notes=(
            "Requires oauth_required auth. Use `body` for video metadata, use "
            "`media` for upload content, keep quota cost highly visible, accept "
            "reviewable `multipart` or `resumable` upload-mode guidance, reject "
            "metadata-only or upload-only shapes, and keep the audit/private-default "
            "caveat visible for downstream reuse decisions."
        ),
    )
    return VideosInsertWrapper(metadata=metadata)

def build_videos_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.update`.

    Official quota cost: ``50`` quota units. The wrapper requires `body.id`
    for the existing video, keeps `part=snippet` explicit for maintainers,
    requires `body.snippet.title` for the minimum supported update path, and
    rejects unsupported optional write fields such as `description`, `tags`,
    `status`, or `localizations` unless the contract is deliberately expanded.

    :return: Representative wrapper configured for `videos.update`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/videos",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            validators=(
                _require_videos_update_body,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.id` for the existing "
            "video identifier, keep `part=snippet` explicit, use "
            "`body.snippet.title` for the minimum writable video field, and "
            "reject unsupported optional fields such as "
            "`body.snippet.description`, `body.snippet.tags`, `body.status`, "
            "or `body.localizations` unless they are explicitly added to the "
            "contract."
        ),
    )
    return VideosUpdateWrapper(metadata=metadata)

def build_videos_rate_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.rate`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    video ``id`` plus one supported ``rating`` action on authorized requests,
    supports ``like``, ``dislike``, and ``none`` as the bounded action set,
    and rejects undocumented modifiers unless the contract is deliberately
    expanded.

    :return: Representative wrapper configured for `videos.rate`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="rate",
        http_method="POST",
        path_shape="/youtube/v3/videos/rate",
        request_shape=EndpointRequestShape(
            required_fields=("id", "rating"),
            validators=(
                _require_videos_rate_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the target video "
            "identifier, use `rating` with supported `like`, `dislike`, or "
            "`none` semantics, treat `none` as the clear-rating path, reject "
            "undocumented modifiers, and preserve successful acknowledgement "
            "outcomes as distinct from invalid-request, access, or upstream "
            "rating failures."
        ),
    )
    return VideosRateWrapper(metadata=metadata)

def build_videos_get_rating_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.getRating`.

    Official quota cost: ``1`` quota unit. The wrapper requires one or more
    comma-delimited video identifiers through ``id`` on authorized requests,
    keeps ``liked``, ``disliked``, and ``none`` visible as the supported
    returned rating-state set, and rejects undocumented identifier forms or
    modifiers unless the contract is deliberately expanded.

    :return: Representative wrapper configured for `videos.getRating`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="getRating",
        http_method="GET",
        path_shape="/youtube/v3/videos/getRating",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_videos_get_rating_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=1,
        notes=(
            "Requires oauth_required auth. Use `id` for one or more "
            "comma-delimited video identifiers with a maximum of 50 per "
            "request, keep lookup boundaries reviewable, preserve successful "
            "`liked`, `disliked`, and `none` results per requested video, "
            "treat successful unrated outcomes as successful lookup results "
            "rather than failures, reject undocumented modifiers, and keep "
            "lookup failures distinct from invalid-request, access, "
            "`not_found`, and `upstream_unavailable` failures."
        ),
    )
    return VideosGetRatingWrapper(metadata=metadata)

def build_videos_report_abuse_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.reportAbuse`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    OAuth-backed report body with ``videoId`` and ``reasonId``, supports
    ``secondaryReasonId``, ``comments``, and ``language`` as bounded optional
    body fields, rejects delegated ``onBehalfOfContentOwner`` query behavior
    in this slice, and keeps no-content acknowledgement outcomes distinct from
    invalid-request, access, rate-limit, not-found, and upstream failures.

    :return: Representative wrapper configured for `videos.reportAbuse`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="reportAbuse",
        http_method="POST",
        path_shape="/youtube/v3/videos/reportAbuse",
        request_shape=EndpointRequestShape(
            required_fields=("body",),
            validators=(
                _require_videos_report_abuse_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `body.videoId` for the target "
            "video and `body.reasonId` for the primary abuse reason; "
            "`body.secondaryReasonId`, `body.comments`, and `body.language` "
            "are the only supported optional report details. "
            "`onBehalfOfContentOwner` and undocumented fields remain outside "
            "the guaranteed boundary. Preserve successful no-content report "
            "acknowledgement outcomes as distinct from `invalid_request`, "
            "access, invalid reason, `rate_limited`, `not_found`, and "
            "`upstream_unavailable` failures."
        ),
    )
    return VideosReportAbuseWrapper(metadata=metadata)

def build_videos_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `videos.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    video ``id`` on authorized requests, sends no request body, rejects
    delegated ``onBehalfOfContentOwner`` query behavior in this slice, and
    keeps no-content deletion acknowledgement outcomes distinct from
    invalid-request, access, forbidden, not-found, and upstream failures.

    :return: Representative wrapper configured for `videos.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="videos",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/videos",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            validators=(
                _require_videos_delete_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the target video "
            "identifier and send no request body for this destructive delete "
            "operation. `onBehalfOfContentOwner`, request bodies, bulk delete "
            "shapes, and undocumented fields remain outside the guaranteed "
            "boundary. Preserve successful no-content deletion acknowledgement "
            "outcomes as distinct from `invalid_request`, access, `forbidden`, "
            "`not_found`, and `upstream_unavailable` failures."
        ),
    )
    return VideosDeleteWrapper(metadata=metadata)

FAMILY_NAME = "videos"
RESOURCE_NAMES = ("videos",)
BUILDER_FUNCTIONS = {
    "videos.list": build_videos_list_wrapper,
    "videos.insert": build_videos_insert_wrapper,
    "videos.update": build_videos_update_wrapper,
    "videos.rate": build_videos_rate_wrapper,
    "videos.getRating": build_videos_get_rating_wrapper,
    "videos.reportAbuse": build_videos_report_abuse_wrapper,
    "videos.delete": build_videos_delete_wrapper,
}
RESPONSE_NORMALIZER_KEYS = (
    "videos.list",
    "videos.insert",
    "videos.update",
    "videos.rate",
    "videos.getRating",
    "videos.reportAbuse",
    "videos.delete",
)

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "VideosDeleteWrapper",
    "VideosGetRatingWrapper",
    "VideosInsertWrapper",
    "VideosListWrapper",
    "VideosRateWrapper",
    "VideosReportAbuseWrapper",
    "VideosUpdateWrapper",
    "build_videos_delete_wrapper",
    "build_videos_get_rating_wrapper",
    "build_videos_insert_wrapper",
    "build_videos_list_wrapper",
    "build_videos_rate_wrapper",
    "build_videos_report_abuse_wrapper",
    "build_videos_update_wrapper",
]
