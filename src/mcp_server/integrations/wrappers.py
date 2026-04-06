"""Representative internal endpoint wrappers for Layer 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext, AuthMode
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
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
