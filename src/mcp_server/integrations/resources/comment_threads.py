# ruff: noqa: F405
"""Comment Threads resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

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

FAMILY_NAME = "comment_threads"
RESOURCE_NAMES = ("commentThreads",)
BUILDER_FUNCTIONS = {
    "commentThreads.list": build_comment_threads_list_wrapper,
    "commentThreads.insert": build_comment_threads_insert_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "CommentThreadsInsertWrapper",
    "CommentThreadsListWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_comment_threads_insert_wrapper",
    "build_comment_threads_list_wrapper",
]
