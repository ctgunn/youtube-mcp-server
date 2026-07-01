"""Contract tests for the Layer 2 ``members_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.members import (
    MEMBERS_LIST_INPUT_SCHEMA,
    MEMBERS_LIST_CALLER_EXAMPLES,
    MEMBERS_LIST_DESCRIPTION,
    MEMBERS_LIST_TOOL_NAME,
    MembersListToolError,
    build_members_list_handler,
    build_members_list_contract,
    build_members_list_tool_descriptor,
    validate_members_list_arguments,
)


def test_members_list_public_symbols_are_exported():
    """Expose ``members_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import members

    assert youtube_common.MEMBERS_LIST_TOOL_NAME == "members_list"
    assert MEMBERS_LIST_TOOL_NAME == "members_list"
    assert callable(members.build_members_list_tool_descriptor)


def test_members_list_schema_preserves_part_mode_and_paging_inputs():
    """Expose the supported upstream-like request fields for ``members_list``."""
    properties = MEMBERS_LIST_INPUT_SCHEMA["properties"]

    assert MEMBERS_LIST_INPUT_SCHEMA["required"] == ["part", "mode"]
    assert properties["part"]["enum"] == ["snippet"]
    assert properties["mode"]["enum"] == ["all_current", "updates"]
    assert "pageToken" in properties
    assert "maxResults" in properties
    assert MEMBERS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_members_list_public_contract_identifies_owner_scoped_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list response metadata."""
    contract = build_members_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "members_list"
    assert metadata["upstream"]["operationKey"] == "members.list"
    assert metadata["quotaCost"] == 2
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part", "mode"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert metadata["inputContract"]["properties"]["mode"]["enum"] == ["all_current", "updates"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"


def test_members_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_members_list_tool_descriptor()

    assert descriptor["name"] == "members_list"
    assert descriptor["inputSchema"] == MEMBERS_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "members.list"
    assert descriptor["metadata"]["quotaCost"] == 2


def test_members_list_contract_documents_successful_result_shape():
    """Document the owner-scoped member-list result shape."""
    result = build_members_list_tool_descriptor()["handler"]({"part": "snippet", "mode": "all_current"})

    assert result["endpoint"] == "members.list"
    assert result["quotaCost"] == 2
    assert result["requestedParts"] == ["snippet"]
    assert result["mode"] == "all_current"
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert "items" in result


def test_members_list_metadata_documents_access_and_boundaries():
    """Expose quota, auth, owner access, and out-of-scope guidance safely."""
    descriptor = build_members_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert MEMBERS_LIST_DESCRIPTION == descriptor["description"]
    assert "Quota cost: 2" in metadata_text
    assert "oauth_required" in metadata_text
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text
    assert "subscriber lookup" in metadata_text
    assert "membership-level" in metadata_text
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_members_list_examples_cover_success_and_failure_cases():
    """Expose representative examples for success, paging, empty, and failure outcomes."""
    example_names = {example["name"] for example in MEMBERS_LIST_CALLER_EXAMPLES}

    assert {
        "current_members_listing",
        "membership_updates_listing",
        "paged_members_listing",
        "empty_success",
        "missing_part",
        "missing_mode",
        "unsupported_mode",
        "invalid_max_results",
        "unsupported_option",
        "access_or_membership_eligibility_failure",
        "out_of_scope_subscriber_or_analytics_request",
    }.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"mode": "all_current"}, "part"),
        ({"part": "id", "mode": "all_current"}, "part"),
        ({"part": "snippet"}, "mode"),
        ({"part": "snippet", "mode": "expired"}, "mode"),
        ({"part": "snippet", "mode": "all_current", "maxResults": 1001}, "maxResults"),
        ({"part": "snippet", "mode": "all_current", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "mode": "all_current", "hasAccessToLevel": "level-123"}, "hasAccessToLevel"),
    ],
)
def test_members_list_validation_failures_are_safe(arguments, message):
    """Map unsupported requests to safe validation errors without sensitive diagnostics."""
    with pytest.raises(MembersListToolError) as exc_info:
        validate_members_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_members_list_handler_sanitizes_upstream_failures():
    """Map normalized upstream access failures to safe caller-facing errors."""
    class FailingWrapper:
        """Raise a normalized upstream error for handler mapping coverage."""

        def call(self, executor, *, arguments, auth_context):
            """Raise an access failure containing unsafe diagnostic fields.

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
                details={"field": "mode", "oauth_token": "secret", "stack": "trace"},
            )

    handler = build_members_list_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(MembersListToolError) as exc_info:
        handler({"part": "snippet", "mode": "all_current"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "mode"}
