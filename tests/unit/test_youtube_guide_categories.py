"""Unit tests for the concrete Layer 2 ``guideCategories_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.guide_categories import (
    GUIDE_CATEGORIES_LIST_INPUT_SCHEMA,
    GuideCategoriesListToolError,
    build_guide_categories_list_tool_descriptor,
    map_guide_categories_list_result,
    validate_guide_categories_list_arguments,
)


def test_guide_categories_list_schema_preserves_legacy_lookup_inputs():
    """Expose required part, mutually exclusive selectors, and optional localization."""
    properties = GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["properties"]

    assert GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert {"part", "regionCode", "id", "hl"}.issubset(properties)
    assert properties["regionCode"]["minLength"] == 2
    assert properties["regionCode"]["maxLength"] == 2
    assert GUIDE_CATEGORIES_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_guide_categories_list_arguments_accepts_region_request():
    """Accept region-scoped guide-category retrieval arguments."""
    selected = validate_guide_categories_list_arguments({"part": "snippet", "regionCode": "US"})

    assert selected == ("regionCode", "US")


def test_validate_guide_categories_list_arguments_accepts_id_request():
    """Accept direct guide category identifier retrieval arguments."""
    selected = validate_guide_categories_list_arguments(
        {"part": "snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl"}
    )

    assert selected == ("id", "GCQmVzdCBvZiBZb3VUdWJl")


def test_map_guide_categories_list_result_preserves_region_items_and_availability():
    """Map upstream region results into a safe near-raw list result."""
    result = map_guide_categories_list_result(
        {
            "items": [
                {
                    "kind": "youtube#guideCategory",
                    "id": "GCQmVzdCBvZiBZb3VUdWJl",
                    "snippet": {"title": "Best of YouTube"},
                }
            ],
            "kind": "youtube#guideCategoryListResponse",
        },
        {"part": "snippet", "regionCode": "US"},
    )

    assert result["endpoint"] == "guideCategories.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"mode": "regionCode", "regionCode": "US"}
    assert result["availability"] == {"state": "deprecated"}
    assert result["items"][0]["snippet"]["title"] == "Best of YouTube"
    assert result["kind"] == "youtube#guideCategoryListResponse"


def test_map_guide_categories_list_result_preserves_id_and_localization_context():
    """Map upstream ID results with optional localization context."""
    result = map_guide_categories_list_result(
        {"items": [{"id": "GCQmVzdCBvZiBZb3VUdWJl", "snippet": {"title": "Lo mejor de YouTube"}}]},
        {"part": "id,snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl", "hl": "es"},
    )

    assert result["requestedParts"] == ["id", "snippet"]
    assert result["selector"] == {"mode": "id", "id": ["GCQmVzdCBvZiBZb3VUdWJl"]}
    assert result["localization"] == {"hl": "es"}


def test_map_guide_categories_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful empty results."""
    result = map_guide_categories_list_result({"items": []}, {"part": "snippet", "regionCode": "US"})

    assert result["items"] == []
    assert result["availability"] == {"state": "deprecated"}


def test_guide_categories_list_handler_invokes_wrapper_once_for_region_request():
    """Execute one valid region lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``guideCategories_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative guide-category list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: API-key auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "GCQmVzdCBvZiBZb3VUdWJl"}]}

    wrapper = FakeWrapper()
    descriptor = build_guide_categories_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet", "regionCode": "US"})

    assert result["items"] == [{"id": "GCQmVzdCBvZiBZb3VUdWJl"}]
    assert wrapper.calls[0][1] == {"part": "snippet", "regionCode": "US"}
    assert wrapper.calls[0][2].mode.value == "api_key"


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({}, "part"),
        ({"part": "", "regionCode": "US"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "regionCode": "US", "id": "GCQmVzdCBvZiBZb3VUdWJl"}, "selector"),
        ({"part": "snippet", "regionCode": ""}, "selector"),
        ({"part": "snippet", "regionCode": "U1"}, "regionCode"),
        ({"part": "snippet", "id": ""}, "selector"),
        ({"part": "snippet", "id": "   "}, "selector"),
        ({"part": "snippet", "regionCode": "US", "hl": ""}, "hl"),
        ({"part": "snippet", "regionCode": "US", "hl": "bad language"}, "hl"),
        ({"part": "snippet", "regionCode": "US", "body": {}}, "body"),
        ({"part": "snippet", "regionCode": "US", "videoCategoryId": "17"}, "videoCategoryId"),
        ({"part": "snippet", "regionCode": "US", "searchTerms": "music"}, "searchTerms"),
        ({"part": "snippet", "regionCode": "US", "ranking": "popular"}, "ranking"),
        ({"part": "snippet", "regionCode": "US", "summarization": True}, "summarization"),
    ],
)
def test_validate_guide_categories_list_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid and out-of-scope ``guideCategories_list`` request shapes."""
    with pytest.raises(GuideCategoriesListToolError, match=match):
        validate_guide_categories_list_arguments(arguments)


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("invalid_request", "invalid_request"),
        ("authentication", "authentication_failed"),
        ("auth", "authorization_failed"),
        ("authorization", "authorization_failed"),
        ("permission", "authorization_failed"),
        ("rate_limit", "quota_exhausted"),
        ("not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("deprecated", "deprecated_endpoint"),
        ("removed", "resource_not_found"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_guide_categories_list_handler_maps_upstream_errors_safely(category, expected):
    """Map normalized upstream failures into safe public guide-category categories."""
    class FailingWrapper:
        """Raise one normalized upstream error for handler mapping tests."""

        def call(self, executor, *, arguments, auth_context):
            """Raise a fake upstream error.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to the wrapper.
            :param auth_context: API-key auth context selected by the handler.
            :raises NormalizedUpstreamError: Always raised for this test.
            """
            raise NormalizedUpstreamError(
                "upstream failed",
                category=category,
                retryable=False,
                details={
                    "reason": "guideCategoryUnavailable",
                    "apiKey": "secret",
                    "oauthToken": "oauth-secret",
                    "stackTrace": "traceback",
                    "signedUrl": "https://example.test/signed",
                    "request": {"rawBody": "secret", "safeCode": "legacyUnavailable"},
                },
            )

    descriptor = build_guide_categories_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(GuideCategoriesListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet", "regionCode": "US"})

    assert exc_info.value.category == expected
    assert exc_info.value.details["reason"] == "guideCategoryUnavailable"
    assert exc_info.value.details["request"] == {"safeCode": "legacyUnavailable"}
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "signed" not in str(exc_info.value.details).lower()
