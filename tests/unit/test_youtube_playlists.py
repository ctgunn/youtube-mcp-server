"""Unit tests for the concrete Layer 2 ``playlists_list`` tool."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.youtube_common.playlists import (
    PLAYLISTS_DELETE_INPUT_SCHEMA,
    PLAYLISTS_INSERT_INPUT_SCHEMA,
    PLAYLISTS_UPDATE_INPUT_SCHEMA,
    PlaylistsDeleteToolError,
    PlaylistsInsertToolError,
    PLAYLISTS_LIST_INPUT_SCHEMA,
    PlaylistsListToolError,
    PlaylistsUpdateToolError,
    build_playlists_insert_handler,
    build_playlists_insert_tool_descriptor,
    build_playlists_delete_handler,
    build_playlists_delete_tool_descriptor,
    build_playlists_update_handler,
    build_playlists_update_tool_descriptor,
    build_playlists_list_handler,
    build_playlists_list_tool_descriptor,
    map_playlists_insert_result,
    map_playlists_delete_result,
    map_playlists_update_result,
    map_playlists_list_result,
    validate_playlists_insert_arguments,
    validate_playlists_delete_arguments,
    validate_playlists_update_arguments,
    validate_playlists_list_arguments,
)


class FakePlaylistsListWrapper:
    """Capture wrapper calls for ``playlists_list`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped response to return.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlistListResponse",
            "etag": "etag-playlists",
            "items": [
                {
                    "kind": "youtube#playlist",
                    "etag": "etag-playlist",
                    "id": "PL123",
                    "snippet": {"channelId": "UC123", "title": "Example playlist"},
                    "contentDetails": {"itemCount": 3},
                }
            ],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :return: Configured upstream-shaped response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingPlaylistsListWrapper:
    """Raise one configured upstream failure for handler tests."""

    def __init__(self, error: NormalizedUpstreamError):
        """Initialize the fake wrapper with its failure.

        :param error: Normalized upstream failure to raise from ``call``.
        """
        self.error = error

    def call(self, executor, *, arguments, auth_context):
        """Raise the configured normalized upstream failure.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for this fake wrapper.
        """
        raise self.error


class FakePlaylistsInsertWrapper:
    """Capture wrapper calls for ``playlists_insert`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped created playlist response.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlist",
            "etag": "etag-created-playlist",
            "id": "PL123",
            "snippet": {"title": "Research playlist", "channelId": "UC123"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :return: Configured upstream-shaped created playlist response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingPlaylistsInsertWrapper:
    """Raise one configured upstream failure for insert handler tests."""

    def __init__(self, error: NormalizedUpstreamError):
        """Initialize the fake wrapper with its failure.

        :param error: Normalized upstream failure to raise from ``call``.
        """
        self.error = error

    def call(self, executor, *, arguments, auth_context):
        """Raise the configured normalized upstream failure.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for this fake wrapper.
        """
        raise self.error


class FakePlaylistsUpdateWrapper:
    """Capture wrapper calls for ``playlists_update`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped updated playlist response.
        """
        self.calls = []
        self.response = response or {
            "kind": "youtube#playlist",
            "etag": "etag-updated-playlist",
            "id": "PL123",
            "snippet": {"title": "Updated research playlist", "channelId": "UC123"},
        }

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :return: Configured upstream-shaped updated playlist response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingPlaylistsUpdateWrapper:
    """Raise one configured upstream failure for update handler tests."""

    def __init__(self, error: NormalizedUpstreamError):
        """Initialize the fake wrapper with its failure.

        :param error: Normalized upstream failure to raise from ``call``.
        """
        self.error = error

    def call(self, executor, *, arguments, auth_context):
        """Raise the configured normalized upstream failure.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for this fake wrapper.
        """
        raise self.error


class FakePlaylistsDeleteWrapper:
    """Capture wrapper calls for ``playlists_delete`` tests."""

    def __init__(self, response: dict | None = None):
        """Initialize the fake wrapper call log and response.

        :param response: Optional upstream-shaped deletion response.
        """
        self.calls = []
        self.response = response or {}

    def call(self, executor, *, arguments, auth_context):
        """Record call arguments and return the configured response.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :return: Configured upstream-shaped deletion response.
        """
        self.calls.append((executor, arguments, auth_context))
        return self.response


class FailingPlaylistsDeleteWrapper:
    """Raise one configured upstream failure for delete handler tests."""

    def __init__(self, error: NormalizedUpstreamError):
        """Initialize the fake wrapper with its failure.

        :param error: Normalized upstream failure to raise from ``call``.
        """
        self.error = error

    def call(self, executor, *, arguments, auth_context):
        """Raise the configured normalized upstream failure.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context selected by the handler.
        :raises NormalizedUpstreamError: Always raised for this fake wrapper.
        """
        raise self.error


def _insert_arguments() -> dict:
    """Build one valid ``playlists_insert`` request.

    :return: Valid insert arguments with the minimum writable title.
    """
    return {"part": "snippet", "body": {"snippet": {"title": "Research playlist"}}}


def _update_arguments() -> dict:
    """Build one valid ``playlists_update`` request.

    :return: Valid update arguments with target playlist and title.
    """
    return {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}}


def _delete_arguments() -> dict:
    """Build one valid ``playlists_delete`` request.

    :return: Valid delete arguments with target playlist identifier.
    """
    return {"id": "PL123"}


def test_validate_playlists_list_arguments_normalizes_channel_selector_with_paging():
    """Normalize channel-scoped playlist list arguments."""
    normalized = validate_playlists_list_arguments(
        {"part": "snippet,contentDetails", "channelId": " UC123 ", "pageToken": " NEXT ", "maxResults": 25}
    )

    assert normalized == {
        "part": "snippet,contentDetails",
        "channelId": "UC123",
        "pageToken": "NEXT",
        "maxResults": 25,
    }


def test_validate_playlists_list_arguments_normalizes_id_selector():
    """Normalize direct playlist identifier lookups."""
    assert validate_playlists_list_arguments({"part": "id,snippet", "id": " PL123 "}) == {
        "part": "id,snippet",
        "id": "PL123",
    }


def test_validate_playlists_list_arguments_normalizes_mine_selector():
    """Normalize owner-scoped playlist lookups."""
    assert validate_playlists_list_arguments({"part": "snippet", "mine": True}) == {
        "part": "snippet",
        "mine": True,
    }


def test_map_playlists_list_result_preserves_context_and_paging():
    """Map an upstream playlists payload to a public list result."""
    result = map_playlists_list_result(
        {
            "items": [{"id": "PL123", "snippet": {"title": "Example playlist"}}],
            "nextPageToken": "NEXT_PAGE",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        },
        {"part": "snippet", "channelId": "UC123", "maxResults": 25},
        auth_mode="api_key",
    )

    assert result["endpoint"] == "playlists.list"
    assert result["quotaCost"] == 1
    assert result["requestedParts"] == ["snippet"]
    assert result["selector"] == {"name": "channelId", "value": "UC123"}
    assert result["auth"] == {"mode": "api_key"}
    assert result["items"] == [{"id": "PL123", "snippet": {"title": "Example playlist"}}]
    assert result["empty"] is False
    assert result["paging"] == {"maxResults": 25}
    assert result["nextPageToken"] == "NEXT_PAGE"
    assert result["pageInfo"] == {"totalResults": 1, "resultsPerPage": 1}


def test_map_playlists_list_result_preserves_empty_success():
    """Keep empty upstream item collections as successful list results."""
    result = map_playlists_list_result({"items": []}, {"part": "snippet", "channelId": "UC123"}, auth_mode="api_key")

    assert result["endpoint"] == "playlists.list"
    assert result["items"] == []
    assert result["empty"] is True
    assert result["selector"] == {"name": "channelId", "value": "UC123"}


def test_playlists_list_handler_forwards_api_key_context_to_layer1_wrapper():
    """Validate, execute, and map one public channel-scoped request."""
    wrapper = FakePlaylistsListWrapper()
    executor = object()
    handler = build_playlists_list_handler(wrapper=wrapper, executor=executor, api_key="local-api-key")

    result = handler({"part": "snippet,contentDetails", "channelId": "UC123"})

    assert result["endpoint"] == "playlists.list"
    assert result["items"][0]["id"] == "PL123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == {"part": "snippet,contentDetails", "channelId": "UC123"}
    assert wrapper.calls[0][2].mode.value == "api_key"
    assert wrapper.calls[0][2].credentials.api_key == "local-api-key"
    assert "local-api-key" not in str(result)


def test_playlists_list_handler_forwards_oauth_context_for_mine_selector():
    """Validate, execute, and map one owner-scoped request."""
    wrapper = FakePlaylistsListWrapper()
    handler = build_playlists_list_handler(wrapper=wrapper, oauth_token="local-oauth-token")

    result = handler({"part": "snippet", "mine": True})

    assert result["selector"] == {"name": "mine", "value": True}
    assert result["auth"] == {"mode": "oauth_required"}
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlists_list_descriptor_includes_handler_and_schema():
    """Expose dispatcher-ready descriptor shape for ``playlists_list``."""
    descriptor = build_playlists_list_tool_descriptor(wrapper=FakePlaylistsListWrapper())

    assert descriptor["name"] == "playlists_list"
    assert descriptor["inputSchema"] == PLAYLISTS_LIST_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlists.list"
    assert descriptor["metadata"]["quotaCost"] == 1
    assert descriptor["metadata"]["authMode"] == "mixed/conditional"


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"channelId": "UC123"}, "part"),
        ({"part": "statistics", "channelId": "UC123"}, "part"),
        ({"part": "snippet"}, "selector"),
        ({"part": "snippet", "channelId": "UC123", "id": "PL123"}, "selector"),
        ({"part": "snippet", "channelId": ""}, "channelId"),
        ({"part": "snippet", "id": " "}, "id"),
        ({"part": "snippet", "mine": False}, "mine"),
        ({"part": "snippet", "channelId": "UC123", "pageToken": ""}, "pageToken"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": -1}, "maxResults"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": 51}, "maxResults"),
        ({"part": "snippet", "channelId": "UC123", "maxResults": True}, "maxResults"),
        ({"part": "snippet", "id": "PL123", "pageToken": "NEXT_PAGE"}, "paging"),
        ({"part": "snippet", "channelId": "UC123", "includePlaylistItems": True}, "includePlaylistItems"),
    ],
)
def test_validate_playlists_list_arguments_rejects_malformed_inputs(arguments, field):
    """Reject malformed playlist-list requests with safe field details.

    :param arguments: Candidate invalid request arguments.
    :param field: Expected safe error field.
    """
    with pytest.raises(PlaylistsListToolError) as exc_info:
        validate_playlists_list_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlists_list_handler_rejects_owner_scoped_request_without_oauth():
    """Surface missing owner-scoped OAuth access as a safe authentication failure."""
    handler = build_playlists_list_handler(wrapper=FakePlaylistsListWrapper(), oauth_token=None)

    with pytest.raises(PlaylistsListToolError) as exc_info:
        handler({"part": "snippet", "mine": True})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"selector": "mine", "authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (NormalizedUpstreamError("quota", "quota", True, 429, {"quota": "daily"}), "quota_exhausted"),
        (NormalizedUpstreamError("missing", "not_found", False, 404, {"resource": "playlist"}), "resource_not_found"),
        (NormalizedUpstreamError("unavailable", "transient", True, 503, {}), "endpoint_unavailable"),
        (NormalizedUpstreamError("deprecated", "deprecated", False, 410, {}), "deprecated_endpoint"),
        (NormalizedUpstreamError("invalid", "invalid_request", False, 400, {"reason": "bad"}), "invalid_request"),
        (NormalizedUpstreamError("unexpected", "weird", False, 500, {}), "upstream_failure"),
    ],
)
def test_playlists_list_handler_maps_safe_upstream_error_categories(error, category):
    """Convert upstream playlist-list failures into MCP-safe categories.

    :param error: Upstream failure raised by the fake wrapper.
    :param category: Expected public safe error category.
    """
    handler = build_playlists_list_handler(wrapper=FailingPlaylistsListWrapper(error))

    with pytest.raises(PlaylistsListToolError) as exc_info:
        handler({"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == category


def test_playlists_list_tool_error_sanitizes_unsafe_details():
    """Avoid leaking credentials, headers, stack traces, or raw bodies in errors."""
    handler = build_playlists_list_handler(
        wrapper=FailingPlaylistsListWrapper(
            NormalizedUpstreamError(
                "quota",
                "quota",
                True,
                429,
                {
                    "api_key": "secret",
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "stack_trace": "traceback",
                    "raw_body": {"error": "secret"},
                    "quota": "daily",
                },
            )
        )
    )

    with pytest.raises(PlaylistsListToolError) as exc_info:
        handler({"part": "snippet", "channelId": "UC123"})

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_validate_playlists_insert_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist creation request."""
    selected = validate_playlists_insert_arguments(
        {"part": " snippet ", "body": {"snippet": {"title": " Research playlist "}}}
    )

    assert selected == _insert_arguments()


def test_map_playlists_insert_result_preserves_resource_and_context():
    """Map upstream playlist creation into a safe near-raw mutation result."""
    result = map_playlists_insert_result(
        {
            "kind": "youtube#playlist",
            "etag": "etag-created-playlist",
            "id": "PL123",
            "snippet": {"title": "Research playlist", "channelId": "UC123"},
        },
        _insert_arguments(),
    )

    assert result["endpoint"] == "playlists.insert"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["created"] is True
    assert result["creation"] == {"writableFields": ["body.snippet.title"], "title": "Research playlist"}
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["playlist"]["id"] == "PL123"
    assert result["kind"] == "youtube#playlist"
    assert result["etag"] == "etag-created-playlist"


def test_playlists_insert_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one insert request through Layer 1."""
    wrapper = FakePlaylistsInsertWrapper()
    executor = object()
    handler = build_playlists_insert_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_insert_arguments())

    assert result["endpoint"] == "playlists.insert"
    assert result["playlist"]["id"] == "PL123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _insert_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlists_insert_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready insert descriptor metadata and examples."""
    descriptor = build_playlists_insert_tool_descriptor(wrapper=FakePlaylistsInsertWrapper())

    assert descriptor["name"] == "playlists_insert"
    assert descriptor["inputSchema"] == PLAYLISTS_INSERT_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlists.insert"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"body": {"snippet": {"title": "Research playlist"}}}, "part"),
        ({"part": "status", "body": {"snippet": {"title": "Research playlist"}}}, "part"),
        ({"part": "snippet,snippet", "body": {"snippet": {"title": "Research playlist"}}}, "part"),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": []}, "body"),
        ({"part": "snippet", "body": {}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": []}}, "body.snippet"),
        ({"part": "snippet", "body": {"snippet": {}}}, "body.snippet.title"),
        ({"part": "snippet", "body": {"snippet": {"title": " "}}}, "body.snippet.title"),
        (
            {"part": "snippet", "body": {"snippet": {"title": "Research playlist", "description": "unsupported"}}},
            "body.snippet.description",
        ),
        ({"part": "snippet", "body": {"snippet": {"title": "Research playlist"}, "status": {}}}, "body.status"),
        (
            {"part": "snippet", "body": {"snippet": {"title": "Research playlist"}}, "insertPlaylistItems": True},
            "insertPlaylistItems",
        ),
    ],
)
def test_validate_playlists_insert_arguments_rejects_malformed_inputs(arguments, field):
    """Reject malformed playlist-insert requests with safe field details.

    :param arguments: Candidate invalid request arguments.
    :param field: Expected safe error field.
    """
    with pytest.raises(PlaylistsInsertToolError) as exc_info:
        validate_playlists_insert_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlists_insert_handler_rejects_request_without_oauth():
    """Surface missing playlist creation OAuth access as safe authentication failure."""
    handler = build_playlists_insert_handler(wrapper=FakePlaylistsInsertWrapper(), oauth_token=None)

    with pytest.raises(PlaylistsInsertToolError) as exc_info:
        handler(_insert_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (NormalizedUpstreamError("quota", "quota", True, 429, {"quota": "daily"}), "quota_exhausted"),
        (NormalizedUpstreamError("auth", "auth", False, 403, {"reason": "denied"}), "authorization_failed"),
        (NormalizedUpstreamError("forbidden", "forbidden", False, 403, {"reason": "policy"}), "forbidden_create"),
        (NormalizedUpstreamError("missing", "not_found", False, 404, {"resource": "playlist"}), "resource_not_found"),
        (NormalizedUpstreamError("unavailable", "transient", True, 503, {}), "endpoint_unavailable"),
        (NormalizedUpstreamError("deprecated", "deprecated", False, 410, {}), "deprecated_endpoint"),
        (NormalizedUpstreamError("invalid", "invalid_request", False, 400, {"reason": "bad"}), "invalid_request"),
        (NormalizedUpstreamError("unexpected", "weird", False, 500, {}), "upstream_failure"),
    ],
)
def test_playlists_insert_handler_maps_safe_upstream_error_categories(error, category):
    """Convert upstream playlist-insert failures into MCP-safe categories.

    :param error: Upstream failure raised by the fake wrapper.
    :param category: Expected public safe error category.
    """
    handler = build_playlists_insert_handler(wrapper=FailingPlaylistsInsertWrapper(error))

    with pytest.raises(PlaylistsInsertToolError) as exc_info:
        handler(_insert_arguments())

    assert exc_info.value.category == category


def test_playlists_insert_tool_error_sanitizes_unsafe_details():
    """Avoid leaking credentials, headers, stack traces, or raw bodies in insert errors."""
    handler = build_playlists_insert_handler(
        wrapper=FailingPlaylistsInsertWrapper(
            NormalizedUpstreamError(
                "quota",
                "quota",
                True,
                429,
                {
                    "api_key": "secret",
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "stack_trace": "traceback",
                    "raw_body": {"error": "secret"},
                    "quota": "daily",
                },
            )
        )
    )

    with pytest.raises(PlaylistsInsertToolError) as exc_info:
        handler(_insert_arguments())

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_validate_playlists_update_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist update request."""
    selected = validate_playlists_update_arguments(
        {
            "part": " snippet ",
            "body": {"id": " PL123 ", "snippet": {"title": " Updated research playlist "}},
        }
    )

    assert selected == _update_arguments()


def test_map_playlists_update_result_preserves_resource_and_context():
    """Map upstream playlist update into a safe near-raw mutation result."""
    result = map_playlists_update_result(
        {
            "kind": "youtube#playlist",
            "etag": "etag-updated-playlist",
            "id": "PL123",
            "snippet": {"title": "Updated research playlist", "channelId": "UC123"},
        },
        _update_arguments(),
    )

    assert result["endpoint"] == "playlists.update"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["updated"] is True
    assert result["target"] == {"playlistId": "PL123"}
    assert result["update"] == {
        "writableFields": ["body.snippet.title"],
        "title": "Updated research playlist",
    }
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["playlist"]["id"] == "PL123"
    assert result["kind"] == "youtube#playlist"
    assert result["etag"] == "etag-updated-playlist"


def test_playlists_update_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one update request through Layer 1."""
    wrapper = FakePlaylistsUpdateWrapper()
    executor = object()
    handler = build_playlists_update_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_update_arguments())

    assert result["endpoint"] == "playlists.update"
    assert result["playlist"]["id"] == "PL123"
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _update_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlists_update_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready update descriptor metadata and examples."""
    descriptor = build_playlists_update_tool_descriptor(wrapper=FakePlaylistsUpdateWrapper())

    assert descriptor["name"] == "playlists_update"
    assert descriptor["inputSchema"] == PLAYLISTS_UPDATE_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlists.update"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({"body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}}, "part"),
        ({"part": "status", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}}, "part"),
        (
            {"part": "snippet,snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}}},
            "part",
        ),
        ({"part": "snippet"}, "body"),
        ({"part": "snippet", "body": []}, "body"),
        ({"part": "snippet", "body": {"snippet": {"title": "Updated research playlist"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": " ", "snippet": {"title": "Updated research playlist"}}}, "body.id"),
        ({"part": "snippet", "body": {"id": "PL123"}}, "body.snippet"),
        ({"part": "snippet", "body": {"id": "PL123", "snippet": []}}, "body.snippet"),
        ({"part": "snippet", "body": {"id": "PL123", "snippet": {}}}, "body.snippet.title"),
        ({"part": "snippet", "body": {"id": "PL123", "snippet": {"title": " "}}}, "body.snippet.title"),
        (
            {
                "part": "snippet",
                "body": {
                    "id": "PL123",
                    "snippet": {"title": "Updated research playlist", "description": "unsupported"},
                },
            },
            "body.snippet.description",
        ),
        (
            {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}, "status": {}}},
            "body.status",
        ),
        (
            {
                "part": "snippet",
                "body": {"id": "PL123", "snippet": {"title": "Updated research playlist"}},
                "insertPlaylistItems": True,
            },
            "insertPlaylistItems",
        ),
    ],
)
def test_validate_playlists_update_arguments_rejects_malformed_inputs(arguments, field):
    """Reject malformed playlist-update requests with safe field details.

    :param arguments: Candidate invalid request arguments.
    :param field: Expected safe error field.
    """
    with pytest.raises(PlaylistsUpdateToolError) as exc_info:
        validate_playlists_update_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlists_update_handler_rejects_request_without_oauth():
    """Surface missing playlist update OAuth access as safe authentication failure."""
    handler = build_playlists_update_handler(wrapper=FakePlaylistsUpdateWrapper(), oauth_token=None)

    with pytest.raises(PlaylistsUpdateToolError) as exc_info:
        handler(_update_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (NormalizedUpstreamError("quota", "quota", True, 429, {"quota": "daily"}), "quota_exhausted"),
        (NormalizedUpstreamError("auth", "auth", False, 403, {"reason": "denied"}), "authorization_failed"),
        (NormalizedUpstreamError("forbidden", "forbidden", False, 403, {"reason": "policy"}), "forbidden_update"),
        (NormalizedUpstreamError("missing", "not_found", False, 404, {"resource": "playlist"}), "resource_not_found"),
        (NormalizedUpstreamError("unavailable", "transient", True, 503, {}), "endpoint_unavailable"),
        (NormalizedUpstreamError("deprecated", "deprecated", False, 410, {}), "deprecated_endpoint"),
        (NormalizedUpstreamError("invalid", "invalid_request", False, 400, {"reason": "bad"}), "invalid_request"),
        (NormalizedUpstreamError("unexpected", "weird", False, 500, {}), "upstream_failure"),
    ],
)
def test_playlists_update_handler_maps_safe_upstream_error_categories(error, category):
    """Convert upstream playlist-update failures into MCP-safe categories.

    :param error: Upstream failure raised by the fake wrapper.
    :param category: Expected public safe error category.
    """
    handler = build_playlists_update_handler(wrapper=FailingPlaylistsUpdateWrapper(error))

    with pytest.raises(PlaylistsUpdateToolError) as exc_info:
        handler(_update_arguments())

    assert exc_info.value.category == category


def test_playlists_update_tool_error_sanitizes_unsafe_details():
    """Avoid leaking credentials, headers, stack traces, or raw bodies in update errors."""
    handler = build_playlists_update_handler(
        wrapper=FailingPlaylistsUpdateWrapper(
            NormalizedUpstreamError(
                "quota",
                "quota",
                True,
                429,
                {
                    "api_key": "secret",
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "stack_trace": "traceback",
                    "raw_body": {"error": "secret"},
                    "quota": "daily",
                },
            )
        )
    )

    with pytest.raises(PlaylistsUpdateToolError) as exc_info:
        handler(_update_arguments())

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}


def test_validate_playlists_delete_arguments_accepts_supported_request():
    """Accept and normalize a supported playlist deletion request."""
    selected = validate_playlists_delete_arguments({"id": " PL123 "})

    assert selected == _delete_arguments()


def test_map_playlists_delete_result_preserves_acknowledgment_and_context():
    """Map upstream playlist deletion into a safe acknowledgment result."""
    result = map_playlists_delete_result({}, _delete_arguments())

    assert result["endpoint"] == "playlists.delete"
    assert result["quotaCost"] == 50
    assert result["deleted"] is True
    assert result["acknowledged"] is True
    assert result["auth"] == {"mode": "oauth_required"}
    assert result["target"] == {"playlistId": "PL123"}
    assert "playlist" not in result
    assert "items" not in result


def test_playlists_delete_handler_forwards_oauth_context_to_layer1_wrapper():
    """Validate, execute, and map one delete request through Layer 1."""
    wrapper = FakePlaylistsDeleteWrapper()
    executor = object()
    handler = build_playlists_delete_handler(wrapper=wrapper, executor=executor, oauth_token="local-oauth-token")

    result = handler(_delete_arguments())

    assert result["endpoint"] == "playlists.delete"
    assert result["deleted"] is True
    assert wrapper.calls[0][0] is executor
    assert wrapper.calls[0][1] == _delete_arguments()
    assert wrapper.calls[0][2].mode.value == "oauth_required"
    assert wrapper.calls[0][2].credentials.oauth_token == "local-oauth-token"
    assert "local-oauth-token" not in str(result)


def test_playlists_delete_descriptor_includes_handler_metadata_and_examples():
    """Expose dispatcher-ready delete descriptor metadata and examples."""
    descriptor = build_playlists_delete_tool_descriptor(wrapper=FakePlaylistsDeleteWrapper())

    assert descriptor["name"] == "playlists_delete"
    assert descriptor["inputSchema"] == PLAYLISTS_DELETE_INPUT_SCHEMA
    assert callable(descriptor["handler"])
    assert descriptor["metadata"]["upstream"]["operationKey"] == "playlists.delete"
    assert descriptor["metadata"]["quotaCost"] == 50
    assert descriptor["metadata"]["authMode"] == "oauth_required"
    assert descriptor["metadata"]["examples"]


@pytest.mark.parametrize(
    ("arguments", "field"),
    [
        ({}, "id"),
        ({"id": ""}, "id"),
        ({"id": " "}, "id"),
        ({"id": 123}, "id"),
        ({"id": "PL123", "part": "snippet"}, "part"),
        ({"id": "PL123", "body": {}}, "body"),
        ({"id": "PL123", "channelId": "UC123"}, "channelId"),
        ({"id": "PL123", "mine": True}, "mine"),
        ({"id": "PL123", "pageToken": "NEXT_PAGE"}, "pageToken"),
        ({"id": "PL123", "playlistItemId": "PLI123"}, "playlistItemId"),
        ({"id": "PL123", "playlistImageId": "IMG123"}, "playlistImageId"),
        ({"id": "PL123", "analytics": True}, "analytics"),
        ({"id": "PL123", "restore": True}, "restore"),
    ],
)
def test_validate_playlists_delete_arguments_rejects_malformed_inputs(arguments, field):
    """Reject malformed playlist-delete requests with safe field details.

    :param arguments: Candidate invalid request arguments.
    :param field: Expected safe error field.
    """
    with pytest.raises(PlaylistsDeleteToolError) as exc_info:
        validate_playlists_delete_arguments(arguments)

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details.get("field") == field


def test_playlists_delete_handler_rejects_request_without_oauth():
    """Surface missing playlist deletion OAuth access as safe authentication failure."""
    handler = build_playlists_delete_handler(wrapper=FakePlaylistsDeleteWrapper(), oauth_token=None)

    with pytest.raises(PlaylistsDeleteToolError) as exc_info:
        handler(_delete_arguments())

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (NormalizedUpstreamError("quota", "quota", True, 429, {"quota": "daily"}), "quota_exhausted"),
        (NormalizedUpstreamError("auth", "auth", False, 403, {"reason": "denied"}), "authorization_failed"),
        (NormalizedUpstreamError("forbidden", "forbidden", False, 403, {"reason": "policy"}), "authorization_failed"),
        (NormalizedUpstreamError("missing", "not_found", False, 404, {"resource": "playlist"}), "resource_not_found"),
        (NormalizedUpstreamError("deleted", "resource_not_found", False, 404, {"resource": "playlist"}), "resource_not_found"),
        (NormalizedUpstreamError("unavailable", "transient", True, 503, {}), "endpoint_unavailable"),
        (NormalizedUpstreamError("deprecated", "deprecated", False, 410, {}), "deprecated_endpoint"),
        (NormalizedUpstreamError("invalid", "invalid_request", False, 400, {"reason": "bad"}), "invalid_request"),
        (NormalizedUpstreamError("unexpected", "weird", False, 500, {}), "upstream_failure"),
    ],
)
def test_playlists_delete_handler_maps_safe_upstream_error_categories(error, category):
    """Convert upstream playlist-delete failures into MCP-safe categories.

    :param error: Upstream failure raised by the fake wrapper.
    :param category: Expected public safe error category.
    """
    handler = build_playlists_delete_handler(wrapper=FailingPlaylistsDeleteWrapper(error))

    with pytest.raises(PlaylistsDeleteToolError) as exc_info:
        handler(_delete_arguments())

    assert exc_info.value.category == category


def test_playlists_delete_tool_error_sanitizes_unsafe_details():
    """Avoid leaking credentials, headers, stack traces, or raw bodies in delete errors."""
    handler = build_playlists_delete_handler(
        wrapper=FailingPlaylistsDeleteWrapper(
            NormalizedUpstreamError(
                "quota",
                "quota",
                True,
                429,
                {
                    "api_key": "secret",
                    "oauth_token": "secret",
                    "authorization": "Bearer secret",
                    "stack_trace": "traceback",
                    "raw_body": {"error": "secret"},
                    "quota": "daily",
                },
            )
        )
    )

    with pytest.raises(PlaylistsDeleteToolError) as exc_info:
        handler(_delete_arguments())

    assert exc_info.value.category == "quota_exhausted"
    assert exc_info.value.details == {"quota": "daily"}
