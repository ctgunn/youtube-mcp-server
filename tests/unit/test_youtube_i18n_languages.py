"""Unit tests for the concrete Layer 2 ``i18nLanguages_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.localization import (
    I18N_LANGUAGES_LIST_INPUT_SCHEMA,
    I18nLanguagesListToolError,
    build_i18n_languages_list_tool_descriptor,
    map_i18n_languages_list_result,
    validate_i18n_languages_list_arguments,
)


def test_i18n_languages_list_schema_preserves_part_and_optional_display_language():
    """Expose required part and optional display-language preference."""
    properties = I18N_LANGUAGES_LIST_INPUT_SCHEMA["properties"]

    assert I18N_LANGUAGES_LIST_INPUT_SCHEMA["required"] == ["part"]
    assert properties["part"]["enum"] == ["snippet"]
    assert "hl" in properties
    assert I18N_LANGUAGES_LIST_INPUT_SCHEMA["additionalProperties"] is False


def test_validate_i18n_languages_list_arguments_accepts_default_request():
    """Accept default localization-language retrieval arguments."""
    selected = validate_i18n_languages_list_arguments({"part": "snippet"})

    assert selected == {"part": "snippet"}


def test_validate_i18n_languages_list_arguments_accepts_display_language_request():
    """Accept localization-language retrieval with display-language preference."""
    selected = validate_i18n_languages_list_arguments({"part": "snippet", "hl": "es"})

    assert selected == {"part": "snippet", "hl": "es"}


def test_map_i18n_languages_list_result_preserves_items_and_active_availability():
    """Map upstream localization-language results into a safe near-raw list result."""
    result = map_i18n_languages_list_result(
        {
            "items": [
                {
                    "kind": "youtube#i18nLanguage",
                    "id": "en",
                    "snippet": {"hl": "en", "name": "English"},
                }
            ],
            "kind": "youtube#i18nLanguageListResponse",
            "etag": "etag-123",
        },
        {"part": "snippet"},
    )

    assert result["endpoint"] == "i18nLanguages.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["availability"] == {"state": "active"}
    assert result["items"][0]["snippet"]["name"] == "English"
    assert result["kind"] == "youtube#i18nLanguageListResponse"
    assert result["etag"] == "etag-123"
    assert "localization" not in result


def test_map_i18n_languages_list_result_preserves_display_language_context():
    """Map upstream localization-language results with optional display-language context."""
    result = map_i18n_languages_list_result(
        {"items": [{"id": "en", "snippet": {"hl": "en", "name": "Ingles"}}]},
        {"part": "snippet", "hl": "es"},
    )

    assert result["localization"] == {"hl": "es"}


def test_map_i18n_languages_list_result_preserves_empty_collection_success():
    """Preserve empty upstream collections as successful empty results."""
    result = map_i18n_languages_list_result({"items": []}, {"part": "snippet"})

    assert result["items"] == []
    assert result["availability"] == {"state": "active"}


def test_i18n_languages_list_handler_invokes_wrapper_once_for_default_request():
    """Execute one valid default lookup through the descriptor handler."""
    class FakeWrapper:
        """Capture wrapper call arguments for ``i18nLanguages_list``."""

        def __init__(self):
            """Initialize an empty call log."""
            self.calls = []

        def call(self, executor, *, arguments, auth_context):
            """Return a representative localization-language list response.

            :param executor: Executor supplied by the handler.
            :param arguments: Arguments forwarded to Layer 1.
            :param auth_context: API-key auth context selected by the handler.
            :return: Fake upstream list response.
            """
            self.calls.append((executor, arguments, auth_context))
            return {"items": [{"id": "en"}]}

    wrapper = FakeWrapper()
    descriptor = build_i18n_languages_list_tool_descriptor(wrapper=wrapper, executor=object())
    result = descriptor["handler"]({"part": "snippet"})

    assert result["items"] == [{"id": "en"}]
    assert wrapper.calls[0][1] == {"part": "snippet"}
    assert wrapper.calls[0][2].mode.value == "api_key"


@pytest.mark.parametrize(
    ("arguments", "match"),
    [
        ({}, "part"),
        ({"part": ""}, "part"),
        ({"part": "id"}, "part"),
        ({"part": "snippet,id"}, "part"),
        ({"part": "snippet", "hl": ""}, "hl"),
        ({"part": "snippet", "hl": "bad language"}, "hl"),
        ({"part": "snippet", "regionCode": "US"}, "regionCode"),
        ({"part": "snippet", "captionId": "caption-1"}, "captionId"),
        ({"part": "snippet", "translate": "hello"}, "translate"),
        ({"part": "snippet", "languageDetection": True}, "languageDetection"),
        ({"part": "snippet", "searchTerms": "English"}, "searchTerms"),
        ({"part": "snippet", "ranking": "popular"}, "ranking"),
        ({"part": "snippet", "summarization": True}, "summarization"),
    ],
)
def test_validate_i18n_languages_list_arguments_rejects_invalid_requests(arguments, match):
    """Reject invalid and out-of-scope ``i18nLanguages_list`` request shapes."""
    with pytest.raises(I18nLanguagesListToolError, match=match):
        validate_i18n_languages_list_arguments(arguments)


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
        ("resource_not_found", "resource_not_found"),
        ("unavailable", "endpoint_unavailable"),
        ("unexpected", "upstream_failure"),
    ],
)
def test_i18n_languages_list_handler_maps_upstream_errors_safely(category, expected):
    """Map normalized upstream failures into safe public i18n-language categories."""
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
                    "reason": "languageLookupFailed",
                    "apiKey": "secret",
                    "oauthToken": "oauth-secret",
                    "stackTrace": "traceback",
                    "signedUrl": "https://example.test/signed",
                    "request": {"rawBody": "secret", "safeCode": "languageUnavailable"},
                },
            )

    descriptor = build_i18n_languages_list_tool_descriptor(wrapper=FailingWrapper(), executor=object())

    with pytest.raises(I18nLanguagesListToolError) as exc_info:
        descriptor["handler"]({"part": "snippet"})

    assert exc_info.value.category == expected
    assert exc_info.value.details["reason"] == "languageLookupFailed"
    assert exc_info.value.details["request"] == {"safeCode": "languageUnavailable"}
    assert "api" not in str(exc_info.value.details).lower()
    assert "token" not in str(exc_info.value.details).lower()
    assert "stack" not in str(exc_info.value.details).lower()
    assert "signed" not in str(exc_info.value.details).lower()
