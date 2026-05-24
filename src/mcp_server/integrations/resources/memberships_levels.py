# ruff: noqa: F405
"""Memberships Levels resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

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

FAMILY_NAME = "memberships_levels"
RESOURCE_NAMES = ("membershipsLevels",)
BUILDER_FUNCTIONS = {"membershipsLevels.list": build_memberships_levels_list_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "MembershipsLevelsListWrapper",
    "RESOURCE_NAMES",
    "build_memberships_levels_list_wrapper",
]
