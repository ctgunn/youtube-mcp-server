"""Integration tests for registering and invoking ``members_list``."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.members import MembersListToolError, build_members_list_tool_descriptor


def _register_members_list(**descriptor_kwargs) -> InMemoryToolDispatcher:
    """Register the concrete members list tool in a fresh dispatcher."""
    descriptor = build_members_list_tool_descriptor(**descriptor_kwargs)
    dispatcher = InMemoryToolDispatcher(tools=[])
    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )
    return dispatcher


def test_members_list_descriptor_registers_as_executable_tool_for_current_members():
    """Register and execute ``members_list`` for current member retrieval."""
    dispatcher = _register_members_list()

    result = dispatcher.call_tool("members_list", {"part": "snippet", "mode": "all_current"})

    assert result["endpoint"] == "members.list"
    assert result["quotaCost"] == 2
    assert result["requestedParts"] == ["snippet"]
    assert result["mode"] == "all_current"
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert result["items"][0]["id"] == "member-123"


def test_members_list_descriptor_registers_as_executable_tool_for_updates_page():
    """Register and execute ``members_list`` for an update-stream page."""
    dispatcher = _register_members_list()

    result = dispatcher.call_tool(
        "members_list",
        {"part": "snippet", "mode": "updates", "pageToken": "NEXT_PAGE", "maxResults": 25},
    )

    assert result["mode"] == "updates"
    assert result["pageRequest"] == {"pageToken": "NEXT_PAGE", "maxResults": 25}
    assert result["nextPageToken"] == "NEXT_PAGE"


def test_members_list_dispatcher_rejects_missing_required_fields():
    """Reject incomplete member-list calls before handler execution."""
    dispatcher = _register_members_list()

    with pytest.raises(ValueError, match="part"):
        dispatcher.call_tool("members_list", {"mode": "all_current"})


def test_members_list_dispatcher_propagates_safe_validation_failures():
    """Propagate safe handler validation failures for unsupported member-list fields."""
    dispatcher = _register_members_list()

    with pytest.raises(MembersListToolError) as exc_info:
        dispatcher.call_tool("members_list", {"part": "snippet", "mode": "expired"})

    assert exc_info.value.category == "invalid_request"
    assert "expired" not in str(exc_info.value.details)
    assert "token" not in str(exc_info.value.details).lower()


def test_members_list_dispatcher_propagates_safe_access_failures():
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
                details={"field": "mode", "oauth_token": "secret"},
            )

    dispatcher = _register_members_list(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(MembersListToolError) as exc_info:
        dispatcher.call_tool("members_list", {"part": "snippet", "mode": "all_current"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "mode"}
