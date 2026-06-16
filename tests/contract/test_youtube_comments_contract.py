"""Contract tests for the concrete Layer 2 ``comments`` tools."""

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools import youtube_common
from mcp_server.tools.youtube_common import AuthMode, AvailabilityState
from mcp_server.tools.youtube_common.comments import (
    COMMENTS_LIST_CALLER_EXAMPLES,
    COMMENTS_LIST_INPUT_SCHEMA,
    COMMENTS_LIST_TOOL_NAME,
    CommentsListToolError,
    build_comments_list_contract,
    build_comments_list_tool_descriptor,
)


def test_concrete_comments_module_exports_public_tool_contract():
    """Require the concrete comments Layer 2 module and exports to exist."""
    from mcp_server.tools.youtube_common import comments

    assert comments.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert youtube_common.COMMENTS_LIST_TOOL_NAME == "comments_list"
    assert callable(comments.build_comments_list_tool_descriptor)


def test_comments_list_contract_exposes_identity_quota_auth_and_selectors():
    """Expose public metadata required before ``comments_list`` invocation."""
    contract = build_comments_list_contract()
    metadata = contract.to_tool_metadata()

    assert contract.tool_name == COMMENTS_LIST_TOOL_NAME
    assert contract.upstream_resource == "comments"
    assert contract.upstream_method == "list"
    assert contract.quota_cost == 1
    assert contract.auth_mode is AuthMode.MIXED
    assert contract.availability_state is AvailabilityState.ACTIVE
    assert metadata["upstream"]["operationKey"] == "comments.list"
    assert metadata["inputContract"]["required"] == ["part"]
    assert {"id", "parentId"}.issubset(metadata["inputContract"]["properties"])
    assert metadata["responseBoundary"]["boundaryKind"] == "near_raw"
    assert any("Quota cost: 1" in note for note in metadata["usageNotes"])


def test_comments_list_descriptor_matches_contract_and_schema():
    """Build a dispatcher descriptor that matches the public contract."""
    descriptor = build_comments_list_tool_descriptor()

    assert descriptor["name"] == "comments_list"
    assert "Quota cost: 1" in descriptor["description"]
    assert descriptor["metadata"]["upstream"]["operationKey"] == "comments.list"
    assert descriptor["inputSchema"]["required"] == ["part"]
    assert {"id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(
        descriptor["inputSchema"]["properties"]
    )
    assert callable(descriptor["handler"])


def test_comments_list_contract_documents_successful_result_shape():
    """Require successful results to preserve near-raw comment collection fields."""
    result = build_comments_list_tool_descriptor()["handler"]({"part": "id,snippet", "id": "comment-123"})

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "comment-123"}]
    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"name": "id"}
    assert result["textFormat"] == "html"


def test_comments_list_contract_documents_parent_reply_result_shape():
    """Require parent-comment retrieval to preserve paging and formatting context."""
    result = build_comments_list_tool_descriptor()["handler"](
        {
            "part": "snippet",
            "parentId": "comment-parent-123",
            "maxResults": 2,
            "pageToken": "NEXT_PAGE",
            "textFormat": "plainText",
        }
    )

    assert result["endpoint"] == "comments.list"
    assert result["quotaCost"] == 1
    assert result["items"] == [{"id": "reply-123"}]
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "parentId"}
    assert result["textFormat"] == "plainText"
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_comments_list_metadata_exposes_lookup_cost_auth_and_caveats():
    """Expose quota, auth, selectors, pagination, formatting, and exclusions."""
    metadata = build_comments_list_contract().to_tool_metadata()
    metadata_text = " ".join(
        [
            metadata["description"],
            *metadata["usageNotes"],
            *metadata["caveats"],
        ]
    )

    assert metadata["quotaCost"] == 1
    assert metadata["authMode"] == "mixed/conditional"
    assert metadata["availabilityState"] == "active"
    assert metadata["responseConvention"]["resultKind"] == "list"
    assert metadata["responseConvention"]["emptyResultPolicy"] == "empty_success_when_upstream_returns_empty_items"
    assert "id" in metadata_text
    assert "parentId" in metadata_text
    assert "maxResults" in metadata_text
    assert "pageToken" in metadata_text
    assert "textFormat" in metadata_text
    assert "plainText" in metadata_text
    assert "comment-thread discovery" in metadata_text
    assert "summarization" in metadata_text


def test_comments_list_caller_examples_cover_success_and_failure_modes():
    """Expose representative examples for every required caller scenario."""
    examples = {example["name"]: example for example in COMMENTS_LIST_CALLER_EXAMPLES}

    assert {
        "id_lookup",
        "parent_reply_lookup",
        "paginated_parent_lookup",
        "plain_text_parent_lookup",
        "empty_success",
        "missing_selector",
        "conflicting_selectors",
        "invalid_id",
        "unsupported_option",
        "access_sensitive_failure",
    }.issubset(examples)
    assert all(
        example.get("quotaCost") == 1 or "Quota cost: 1" in str(example)
        for example in COMMENTS_LIST_CALLER_EXAMPLES
    )


def test_comments_list_public_metadata_is_safe():
    """Avoid exposing credentials or unsafe diagnostics in public metadata."""
    metadata = build_comments_list_contract().to_tool_metadata()

    assert "oauthToken" not in str(metadata)
    assert "apiKey" not in str(metadata)
    assert "stack" not in str(metadata).lower()
    assert "raw_media" not in str(metadata).lower()


def test_comments_list_safe_errors_do_not_leak_secret_details():
    """Avoid leaking credentials or raw diagnostics from public errors."""
    class FailingWrapper:
        """Raise a normalized upstream error with unsafe-looking details."""

        def call(self, executor, *, arguments, auth_context):
            """Raise one fake upstream authorization failure.

            :param executor: Executor passed by the handler.
            :param arguments: Arguments forwarded to the wrapper.
            :param auth_context: Auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "forbidden",
                category="auth",
                retryable=False,
                upstream_status=403,
                details={"apiKey": "secret", "oauthToken": "secret", "stackTrace": "traceback"},
            )

    descriptor = build_comments_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(CommentsListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "id": "comment-123"})

    assert exc_info.value.category == "authorization_failed"
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()


def test_comments_list_input_schema_preserves_contract_shape():
    """Expose the endpoint-like request shape for ``comments_list``."""
    properties = COMMENTS_LIST_INPUT_SCHEMA["properties"]

    assert COMMENTS_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "id", "parentId", "maxResults", "pageToken", "textFormat"}.issubset(properties)
    assert properties["maxResults"]["maximum"] == 100
    assert properties["textFormat"]["enum"] == ["html", "plainText"]
    assert COMMENTS_LIST_INPUT_SCHEMA["additionalProperties"] is False
