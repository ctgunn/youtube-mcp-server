"""Unit tests for the concrete Layer 2 ``membershipsLevels_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.tools.youtube_common.memberships_levels import (
    MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA,
    MembershipsLevelsListToolError,
    build_memberships_levels_list_tool_descriptor,
    map_memberships_levels_list_result,
    validate_memberships_levels_list_arguments,
)


def test_memberships_levels_list_schema_preserves_required_part_input():
    """Expose required part and no unsupported optional controls."""
    properties = MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA["properties"]

    assert MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"]["enum"] == ["snippet"]
    assert "pageToken" not in properties
    assert "maxResults" not in properties


def test_validate_memberships_levels_list_arguments_accepts_snippet_request():
    """Accept membership-level retrieval arguments."""
    selected = validate_memberships_levels_list_arguments({"part": "snippet"})

    assert selected == {"part": "snippet"}


def test_map_memberships_levels_list_result_preserves_items_and_upstream_fields():
    """Map upstream membership-level results into a safe near-raw list result."""
    result = map_memberships_levels_list_result(
        {
            "items": [{"kind": "youtube#membershipsLevel", "id": "level-123"}],
            "kind": "youtube#membershipsLevelListResponse",
            "etag": "etag-123",
        },
        {"part": "snippet"},
    )

    assert result["endpoint"] == "membershipsLevels.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert result["items"][0]["id"] == "level-123"
    assert result["kind"] == "youtube#membershipsLevelListResponse"
    assert result["etag"] == "etag-123"


def test_map_memberships_levels_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful empty results."""
    result = map_memberships_levels_list_result({"items": []}, {"part": "snippet"})

    assert result["items"] == []
    assert result["requestedParts"] == ["snippet"]


def test_memberships_levels_list_handler_invokes_wrapper_once_for_owner_request():
    """Execute one valid owner-scoped lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``membershipsLevels_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative membership-level list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "level-123"}]}

    wrapper = FakeWrapper()
    descriptor = build_memberships_levels_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet"})

    assert result["items"] == [{"id": "level-123"}]
    assert wrapper.calls[0][1] == {"part": "snippet"}
    assert wrapper.calls[0][2].mode.value == "oauth_required"


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"part": ""},
        {"part": "id"},
        {"part": "snippet,id"},
        {"part": "snippet", "pageToken": "NEXT_PAGE"},
        {"part": "snippet", "maxResults": 25},
        {"part": "snippet", "onBehalfOfContentOwner": "owner"},
        {"part": "snippet", "filterByMemberChannelId": "channel-123"},
        {"part": "snippet", "hasAccessToLevel": "level-123"},
    ],
)
def test_validate_memberships_levels_list_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed, delegated, filtered, and out-of-scope membership-level requests."""
    with pytest.raises(MembershipsLevelsListToolError) as exc_info:
        validate_memberships_levels_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
