"""Unit tests for the concrete Layer 2 ``members_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.tools.youtube_common.members import (
    MEMBERS_LIST_INPUT_SCHEMA,
    MembersListToolError,
    build_members_list_tool_descriptor,
    map_members_list_result,
    validate_members_list_arguments,
)


def test_members_list_schema_preserves_part_mode_and_paging_inputs():
    """Expose required part and mode plus optional paging controls."""
    properties = MEMBERS_LIST_INPUT_SCHEMA["properties"]

    assert MEMBERS_LIST_INPUT_SCHEMA["required"] == ["part", "mode"]
    assert properties["part"]["enum"] == ["snippet"]
    assert properties["mode"]["enum"] == ["all_current", "updates"]
    assert properties["pageToken"]["minLength"] == 1
    assert properties["maxResults"]["minimum"] == 0
    assert properties["maxResults"]["maximum"] == 1000


def test_validate_members_list_arguments_accepts_current_members_request():
    """Accept current member-list retrieval arguments."""
    selected = validate_members_list_arguments({"part": "snippet", "mode": "all_current"})

    assert selected == {"part": "snippet", "mode": "all_current"}


def test_validate_members_list_arguments_accepts_updates_request():
    """Accept membership-update retrieval arguments."""
    selected = validate_members_list_arguments({"part": "snippet", "mode": "updates"})

    assert selected == {"part": "snippet", "mode": "updates"}


def test_validate_members_list_arguments_accepts_paged_request():
    """Accept member-list retrieval with documented paging controls."""
    selected = validate_members_list_arguments(
        {"part": "snippet", "mode": "all_current", "pageToken": "NEXT_PAGE", "maxResults": 25}
    )

    assert selected == {"part": "snippet", "mode": "all_current", "pageToken": "NEXT_PAGE", "maxResults": 25}


def test_map_members_list_result_preserves_items_mode_and_paging():
    """Map upstream member-list results into a safe near-raw list result."""
    result = map_members_list_result(
        {
            "items": [{"kind": "youtube#member", "id": "member-123"}],
            "kind": "youtube#memberListResponse",
            "etag": "etag-123",
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet", "mode": "all_current", "maxResults": 25},
    )

    assert result["endpoint"] == "members.list"
    assert result["quotaCost"] == 2
    assert result["requestedParts"] == ["snippet"]
    assert result["mode"] == "all_current"
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert result["items"][0]["id"] == "member-123"
    assert result["kind"] == "youtube#memberListResponse"
    assert result["etag"] == "etag-123"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}
    assert result["pageRequest"] == {"maxResults": 25}


def test_map_members_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful empty results."""
    result = map_members_list_result({"items": []}, {"part": "snippet", "mode": "updates"})

    assert result["items"] == []
    assert result["mode"] == "updates"


def test_members_list_handler_invokes_wrapper_once_for_current_members_request():
    """Execute one valid owner-scoped lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``members_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative member-list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: OAuth auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "member-123"}]}

    wrapper = FakeWrapper()
    descriptor = build_members_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet", "mode": "all_current"})

    assert result["items"] == [{"id": "member-123"}]
    assert wrapper.calls[0][1] == {"part": "snippet", "mode": "all_current"}
    assert wrapper.calls[0][2].mode.value == "oauth_required"


@pytest.mark.parametrize(
    "arguments",
    [
        {"mode": "all_current"},
        {"part": "id", "mode": "all_current"},
        {"part": "snippet"},
        {"part": "snippet", "mode": "expired"},
        {"part": "snippet", "mode": "all_current", "maxResults": 1001},
        {"part": "snippet", "mode": "all_current", "maxResults": -1},
        {"part": "snippet", "mode": "all_current", "pageToken": ""},
        {"part": "snippet", "mode": "all_current", "onBehalfOfContentOwner": "owner"},
        {"part": "snippet", "mode": "all_current", "hasAccessToLevel": "level-123"},
        {"part": "snippet", "mode": "all_current", "filterByMemberChannelId": "channel-123"},
    ],
)
def test_validate_members_list_arguments_rejects_unsupported_requests(arguments):
    """Reject malformed, delegated, filtered, and out-of-scope member-list requests."""
    with pytest.raises(MembersListToolError) as exc_info:
        validate_members_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
