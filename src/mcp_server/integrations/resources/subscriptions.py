# ruff: noqa: F405
"""Subscriptions resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

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

FAMILY_NAME = "subscriptions"
RESOURCE_NAMES = ("subscriptions",)
BUILDER_FUNCTIONS = {
    "subscriptions.list": build_subscriptions_list_wrapper,
    "subscriptions.insert": build_subscriptions_insert_wrapper,
    "subscriptions.delete": build_subscriptions_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "SubscriptionsDeleteWrapper",
    "SubscriptionsInsertWrapper",
    "SubscriptionsListWrapper",
    "build_subscriptions_delete_wrapper",
    "build_subscriptions_insert_wrapper",
    "build_subscriptions_list_wrapper",
]
