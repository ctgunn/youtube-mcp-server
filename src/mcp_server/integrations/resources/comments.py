# ruff: noqa: F405
"""Comments resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

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

FAMILY_NAME = "comments"
RESOURCE_NAMES = ("comments",)
BUILDER_FUNCTIONS = {
    "comments.list": build_comments_list_wrapper,
    "comments.insert": build_comments_insert_wrapper,
    "comments.update": build_comments_update_wrapper,
    "comments.setModerationStatus": build_comments_set_moderation_status_wrapper,
    "comments.delete": build_comments_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "CommentsDeleteWrapper",
    "CommentsInsertWrapper",
    "CommentsListWrapper",
    "CommentsSetModerationStatusWrapper",
    "CommentsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_comments_delete_wrapper",
    "build_comments_insert_wrapper",
    "build_comments_list_wrapper",
    "build_comments_set_moderation_status_wrapper",
    "build_comments_update_wrapper",
]
