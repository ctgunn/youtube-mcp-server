"""Contract tests for the Layer 2 ``membershipsLevels_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.memberships_levels import (
    MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES,
    MEMBERSHIPS_LEVELS_LIST_DESCRIPTION,
    MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA,
    MEMBERSHIPS_LEVELS_LIST_TOOL_NAME,
    MembershipsLevelsListToolError,
    build_memberships_levels_list_contract,
    build_memberships_levels_list_handler,
    build_memberships_levels_list_tool_descriptor,
    validate_memberships_levels_list_arguments,
)


def test_memberships_levels_list_public_symbols_are_exported():
    """Expose ``membershipsLevels_list`` symbols from the shared package."""
    from mcp_server.tools.youtube_common import memberships_levels

    assert youtube_common.MEMBERSHIPS_LEVELS_LIST_TOOL_NAME == "membershipsLevels_list"
    assert MEMBERSHIPS_LEVELS_LIST_TOOL_NAME == "membershipsLevels_list"
    assert callable(memberships_levels.build_memberships_levels_list_tool_descriptor)


def test_memberships_levels_list_schema_preserves_required_part_input():
    """Expose the supported upstream-like request field for ``membershipsLevels_list``."""
    properties = MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA["properties"]

    assert MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"]["enum"] == ["snippet"]
    assert "pageToken" not in properties
    assert "maxResults" not in properties
    assert MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_memberships_levels_list_public_contract_identifies_owner_scoped_endpoint():
    """Expose endpoint identity, quota, auth, availability, and list response metadata."""
    contract = build_memberships_levels_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.auth_mode is AuthMode.OAUTH_REQUIRED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["name"] == "membershipsLevels_list"
    assert metadata["upstream"]["operationKey"] == "membershipsLevels.list"
    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "oauth_required"
    assert metadata["availabilityState"] == "active"
    assert metadata["inputContract"]["required"] == ["part"]
    assert metadata["inputContract"]["properties"]["part"]["enum"] == ["snippet"]
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["itemsPath"] == "items"


def test_memberships_levels_list_descriptor_uses_public_contract_shape():
    """Build an executable descriptor aligned with the public contract."""
    descriptor = build_memberships_levels_list_tool_descriptor()

    assert descriptor["name"] == "membershipsLevels_list"
    assert descriptor["inputSchema"] == MEMBERSHIPS_LEVELS_LIST_INPUT_SCHEMA
    assert descriptor["metadata"]["upstream"]["operationKey"] == "membershipsLevels.list"
    assert descriptor["metadata"]["quotaCost"] == 1


def test_memberships_levels_list_contract_documents_successful_result_shape():
    """Document the owner-scoped membership-level list result shape."""
    result = build_memberships_levels_list_tool_descriptor()["handler"]({"part": "snippet"})

    assert result["endpoint"] == "membershipsLevels.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["auth"] == {"mode": "oauth_required", "ownerScoped": True}
    assert "items" in result


def test_memberships_levels_list_metadata_documents_access_and_boundaries():
    """Expose quota, auth, owner access, and out-of-scope guidance safely."""
    descriptor = build_memberships_levels_list_tool_descriptor()
    metadata = descriptor["metadata"]
    metadata_text = " ".join([descriptor["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert MEMBERSHIPS_LEVELS_LIST_DESCRIPTION == descriptor["description"]
    assert "Quota cost: 1" in metadata_text
    assert "oauth_required" in metadata_text
    assert "owner" in metadata_text.lower()
    assert "channel-membership" in metadata_text
    assert "subscriber lookup" in metadata_text
    assert "member listing" in metadata_text
    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()


def test_memberships_levels_list_examples_cover_success_and_failure_cases():
    """Expose representative examples for success, empty, and failure outcomes."""
    example_names = {example["name"] for example in MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES}

    assert {
        "membership_levels_listing",
        "empty_success",
        "missing_part",
        "invalid_part",
        "unsupported_option",
        "access_or_membership_eligibility_failure",
        "out_of_scope_member_or_analytics_request",
    }.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({}, "part"),
        ({"part": "id"}, "part"),
        ({"part": "snippet", "pageToken": "NEXT_PAGE"}, "pageToken"),
        ({"part": "snippet", "maxResults": 25}, "maxResults"),
        ({"part": "snippet", "onBehalfOfContentOwner": "owner"}, "onBehalfOfContentOwner"),
    ],
)
def test_memberships_levels_list_validation_failures_are_safe(arguments, message):
    """Map unsupported requests to safe validation errors without sensitive diagnostics."""
    with pytest.raises(MembershipsLevelsListToolError) as exc_info:
        validate_memberships_levels_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert message in str(exc_info.value)
    assert "oauth" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_memberships_levels_list_handler_sanitizes_upstream_failures():
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
                details={"field": "part", "oauth_token": "secret", "stack": "trace"},
            )

    handler = build_memberships_levels_list_handler(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(MembershipsLevelsListToolError) as exc_info:
        handler({"part": "snippet"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"field": "part"}
