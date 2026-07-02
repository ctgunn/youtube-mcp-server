"""Integration tests for registering and invoking ``membershipsLevels_list``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.memberships_levels import (
    MembershipsLevelsListToolError,
    build_memberships_levels_list_tool_descriptor,
)


def _register_memberships_levels_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete memberships-levels list tool in a fresh dispatcher."""
    descriptor = build_memberships_levels_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_memberships_levels_list_descriptor_registers_as_executable_tool():
    """Register and execute ``membershipsLevels_list`` for owner membership-level retrieval."""
    dispatcher = _register_memberships_levels_list()

    result = dispatcher.call_tool("membershipsLevels_list", {"part": "snippet"})

    assert result["endpoint"] == "membershipsLevels.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert result["items"][0]["id"] == "level-123"


def test_memberships_levels_list_dispatcher_rejects_missing_required_fields():
    """Reject incomplete membership-level list calls before handler execution."""
    dispatcher = _register_memberships_levels_list()

    with pytest.raises(ValueError, match="part"):
        dispatcher.call_tool("membershipsLevels_list", {})


def test_memberships_levels_list_dispatcher_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for unsupported membership-level fields."""
    dispatcher = _register_memberships_levels_list()

    with pytest.raises(MembershipsLevelsListToolError) as exc_info:
        dispatcher.call_tool("membershipsLevels_list", {"part": "id"})

    assert exc_info.value.category == "invalid_request"
    assert "id" not in str(exc_info.value.details)
    assert "token" not in str(exc_info.value.details).lower()


def test_memberships_levels_list_dispatcher_propagates_safe_access_failures():
    """Propagate safe upstream access failures from the registered handler."""
    class FailingWrapper:
        """Raise an access failure from a registered dispatcher tool."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a normalized access failure with unsafe details.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this fake wrapper.
            """
            raise NormalizedUpstreamError(
                message="owner access required",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"field": "part", "oauth_token": "secret"},
            )

    dispatcher = _register_memberships_levels_list(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(MembershipsLevelsListToolError) as exc_info:
        dispatcher.call_tool("membershipsLevels_list", {"part": "snippet"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "part"}
