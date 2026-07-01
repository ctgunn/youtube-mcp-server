# ruff: noqa: F405
"""Members resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class MembersListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `members.list`.

    Official quota cost: ``2`` quota units. The wrapper supports one
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

def build_members_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `members.list`.

    Official quota cost: ``2`` quota units. The wrapper supports one
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
        quota_cost=2,
        notes=(
            "Requires `part` plus `mode` for one deterministic owner-only "
            "membership lookup, allows optional `pageToken` and `maxResults` "
            "within the documented boundary, rejects undocumented modifiers, "
            "treats delegation-related inputs as unsupported in this slice, "
            "and preserves empty result sets as successful outcomes."
        ),
    )
    return MembersListWrapper(metadata=metadata)

FAMILY_NAME = "members"
RESOURCE_NAMES = ("members",)
BUILDER_FUNCTIONS = {"members.list": build_members_list_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "MembersListWrapper", "RESOURCE_NAMES", "build_members_list_wrapper"]
