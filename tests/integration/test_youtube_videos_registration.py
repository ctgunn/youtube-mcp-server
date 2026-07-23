"""Integration tests for ``videos_list`` registration."""

from __future__ import annotations

import pytest

from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.videos import VideosListToolError, build_videos_list_tool_descriptor


class RecordingWrapper:
    """Layer 1 wrapper double for registration-level execution."""

    def __init__(self, payload=None):
        """Initialize call history and fake payload.

        :param payload: Optional payload returned by each wrapper call.
        """
        self.payload = payload or {"items": [{"id": "abc123", "snippet": {"title": "Example"}}]}
        self.calls = []

    def call(self, executor, *, arguments, auth_context):
        """Record the call and return the configured payload.

        :param executor: Executor supplied by the handler.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :return: Configured fake payload.
        """
        self.calls.append({"executor": executor, "arguments": arguments, "auth_context": auth_context})
        return self.payload


class AccessFailingWrapper:
    """Layer 1 wrapper double that raises an access failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a safe-normalized authorization failure with unsafe raw details.

        :param _executor: Ignored fake executor.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :raises NormalizedUpstreamError: Always raised for access mapping.
        """
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={"oauth_token": "secret", "reason": "forbidden"},
        )


class UnsafeInsertFailingWrapper:
    """Layer 1 wrapper double that raises an unsafe insert failure."""

    def call(self, _executor, *, arguments, auth_context):
        """Raise a normalized failure with details that must be sanitized.

        :param _executor: Ignored fake executor.
        :param arguments: Normalized arguments supplied by the handler.
        :param auth_context: Auth context supplied by the handler.
        :raises NormalizedUpstreamError: Always raised for safety checks.
        """
        raise NormalizedUpstreamError(
            message="forbidden",
            category="auth",
            retryable=False,
            upstream_status=403,
            details={
                "oauth_token": "secret",
                "raw_media": "raw-video",
                "signed_url": "https://example.invalid/upload?token=secret",
                "reason": "forbidden",
            },
        )


def test_descriptor_registers_as_executable_videos_tool():
    """Register and execute the concrete descriptor through the dispatcher."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videos_list", {"part": "snippet", "id": "abc123"})

    assert listed["videos_list"]["metadata"]["upstream"]["operationKey"] == "videos.list"
    assert listed["videos_list"]["metadata"]["quotaCost"] == 1
    assert listed["videos_list"]["metadata"]["authMode"] == "mixed/conditional"
    assert result["endpoint"] == "videos.list"
    assert result["quotaCost"] == 1
    assert result["selector"] == {"mode": "id", "id": ["abc123"]}
    assert result["auth"] == {"mode": "api_key", "path": "public"}
    assert result["items"] == [{"id": "abc123", "snippet": {"title": "Example"}}]


def test_descriptor_schema_rejects_missing_part_before_execution():
    """Reject missing required part before the handler reaches Layer 1."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="arguments missing required field: part"):
        dispatcher.call_tool("videos_list", {"id": "abc123"})

    assert wrapper.calls == []


def test_descriptor_schema_rejects_missing_selector_before_execution():
    """Reject missing selector through dispatcher schema validation."""
    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="required combinations"):
        dispatcher.call_tool("videos_list", {"part": "snippet"})

    assert wrapper.calls == []


def test_descriptor_propagates_safe_access_failures():
    """Expose sanitized access failures from the registered handler."""
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_list_tool_descriptor(wrapper=AccessFailingWrapper())])

    with pytest.raises(VideosListToolError) as exc_info:
        dispatcher.call_tool("videos_list", {"part": "snippet", "id": "abc123"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)


def test_videos_insert_descriptor_registers_as_executable_upload_tool():
    """Register and execute the ``videos_insert`` descriptor through the dispatcher."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper(payload={"id": "video-123", "snippet": {"title": "Example upload"}})
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool(
        "videos_insert",
        {
            "part": "snippet,status",
            "body": {"snippet": {"title": "Example upload"}},
            "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            "uploadMode": "resumable",
        },
    )

    assert listed["videos_insert"]["metadata"]["upstream"]["operationKey"] == "videos.insert"
    assert listed["videos_insert"]["metadata"]["quotaCost"] == 1600
    assert listed["videos_insert"]["metadata"]["authMode"] == "oauth_required"
    assert listed["videos_insert"]["metadata"]["availabilityState"] == "media_constrained"
    assert result["endpoint"] == "videos.insert"
    assert result["quotaCost"] == 1600
    assert result["requestedParts"] == ["snippet", "status"]
    assert result["upload"] == {"mode": "resumable", "mimeType": "video/mp4", "contentProvided": True}
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["mutation"] == {"type": "created"}
    assert result["item"]["id"] == "video-123"
    assert "fake-video-content" not in str(result)


def test_videos_insert_descriptor_exposes_caller_metadata_and_examples():
    """Expose usage notes and examples needed before high-cost upload calls."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor()])
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    metadata = listed["videos_insert"]["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}
    metadata_text = " ".join([listed["videos_insert"]["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert "Quota cost: 1600" in metadata_text
    assert "OAuth" in metadata_text
    assert "media" in metadata_text
    assert "uploadMode" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "automatic publishing" in metadata_text
    assert {"authorized_video_creation", "missing_oauth", "out_of_scope_video_workflow"}.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (
            {"part": "snippet", "body": {"snippet": {"title": "Example"}}},
            "arguments missing required field: media",
        ),
        (
            {"part": "snippet", "media": {"mimeType": "video/mp4", "content": "data"}},
            "arguments missing required field: body",
        ),
    ],
)
def test_videos_insert_descriptor_schema_rejects_missing_required_inputs(arguments, message):
    """Reject missing required upload fields before handler execution."""
    from mcp_server.tools.youtube_common.videos import build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match=message):
        dispatcher.call_tool("videos_insert", arguments)

    assert wrapper.calls == []


def test_videos_insert_descriptor_rejects_missing_oauth_safely():
    """Reject valid upload requests with missing OAuth before Layer 1 execution."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor(wrapper=wrapper, oauth_token=None)])

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            },
        )

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_videos_insert_descriptor_rejects_unsupported_upload_mode():
    """Reject unsupported upload modes through the executable descriptor."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_insert_tool_descriptor()])

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
                "uploadMode": "direct",
            },
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == "uploadMode"


def test_videos_insert_descriptor_propagates_sanitized_access_failures():
    """Expose sanitized insert access failures from the registered handler."""
    from mcp_server.tools.youtube_common.videos import VideosInsertToolError, build_videos_insert_tool_descriptor

    dispatcher = InMemoryToolDispatcher(
        tools=[build_videos_insert_tool_descriptor(wrapper=UnsafeInsertFailingWrapper())]
    )

    with pytest.raises(VideosInsertToolError) as exc_info:
        dispatcher.call_tool(
            "videos_insert",
            {
                "part": "snippet",
                "body": {"snippet": {"title": "Example upload"}},
                "media": {"mimeType": "video/mp4", "content": "fake-video-content"},
            },
        )

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)


def test_videos_update_descriptor_registers_as_executable_mutation_tool():
    """Register and execute the ``videos_update`` descriptor through the dispatcher."""
    from mcp_server.tools.youtube_common.videos import build_videos_update_tool_descriptor

    wrapper = RecordingWrapper(payload={"id": "abc123", "snippet": {"title": "Updated title"}})
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool(
        "videos_update",
        {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}},
    )

    assert listed["videos_update"]["metadata"]["upstream"]["operationKey"] == "videos.update"
    assert listed["videos_update"]["metadata"]["quotaCost"] == 50
    assert listed["videos_update"]["metadata"]["authMode"] == "oauth_required"
    assert listed["videos_update"]["metadata"]["availabilityState"] == "active"
    assert result["endpoint"] == "videos.update"
    assert result["quotaCost"] == 50
    assert result["requestedParts"] == ["snippet"]
    assert result["update"] == {
        "videoId": "abc123",
        "bodyFields": ["id", "snippet"],
        "snippetFields": ["title"],
    }
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["mutation"] == {"type": "updated"}
    assert result["item"]["id"] == "abc123"


def test_videos_update_descriptor_exposes_caller_metadata_and_examples():
    """Expose usage notes and examples needed before video update calls."""
    from mcp_server.tools.youtube_common.videos import build_videos_update_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor()])
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    metadata = listed["videos_update"]["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}
    metadata_text = " ".join([listed["videos_update"]["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "body.id" in metadata_text
    assert "body.snippet.title" in metadata_text
    assert "replacement" in metadata_text
    assert "media upload" in metadata_text
    assert {"authorized_metadata_update", "missing_oauth", "out_of_scope_video_workflow"}.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"body": {"id": "abc123", "snippet": {"title": "Updated"}}}, "arguments missing required field: part"),
        ({"part": "snippet"}, "arguments missing required field: body"),
    ],
)
def test_videos_update_descriptor_schema_rejects_missing_required_inputs(arguments, message):
    """Reject missing required update fields before handler execution."""
    from mcp_server.tools.youtube_common.videos import build_videos_update_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match=message):
        dispatcher.call_tool("videos_update", arguments)

    assert wrapper.calls == []


def test_videos_update_descriptor_rejects_missing_oauth_safely():
    """Reject valid update requests with missing OAuth before Layer 1 execution."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, build_videos_update_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor(wrapper=wrapper, oauth_token=None)])

    with pytest.raises(VideosUpdateToolError) as exc_info:
        dispatcher.call_tool(
            "videos_update",
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}},
        )

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_videos_update_descriptor_rejects_unsupported_body_field():
    """Reject unsupported update body fields through the executable descriptor."""
    from mcp_server.tools.youtube_common.videos import VideosUpdateToolError, build_videos_update_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor()])

    with pytest.raises(VideosUpdateToolError) as exc_info:
        dispatcher.call_tool(
            "videos_update",
            {
                "part": "snippet",
                "body": {"id": "abc123", "snippet": {"title": "Updated", "description": "Unsupported"}},
            },
        )

    assert exc_info.value.category == "invalid_request"
    assert exc_info.value.details["field"] == "body.snippet.description"


def test_videos_update_descriptor_rejects_out_of_scope_upload_field():
    """Reject upload workflow fields through the executable update descriptor."""
    from mcp_server.tools.youtube_common.videos import build_videos_update_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_update_tool_descriptor()])

    with pytest.raises(ValueError, match="arguments contain unsupported field: media"):
        dispatcher.call_tool(
            "videos_update",
            {"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated"}}, "media": {}},
        )


@pytest.mark.parametrize("rating", ["like", "dislike", "none"])
def test_videos_rate_descriptor_registers_as_executable_mutation_tool(rating):
    """Register and execute the ``videos_rate`` descriptor through the dispatcher."""
    from mcp_server.tools.youtube_common.videos import build_videos_rate_tool_descriptor

    wrapper = RecordingWrapper(payload={})
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videos_rate", {"id": "abc123", "rating": rating})

    assert listed["videos_rate"]["metadata"]["upstream"]["operationKey"] == "videos.rate"
    assert listed["videos_rate"]["metadata"]["quotaCost"] == 50
    assert listed["videos_rate"]["metadata"]["authMode"] == "oauth_required"
    assert listed["videos_rate"]["metadata"]["availabilityState"] == "active"
    assert result["endpoint"] == "videos.rate"
    assert result["quotaCost"] == 50
    assert result["rating"]["videoId"] == "abc123"
    assert result["rating"]["requestedRating"] == rating
    assert result["rating"].get("clearsRating", False) is (rating == "none")
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert result["mutation"] == {"type": "rated", "acknowledged": True}
    assert result["status"] == {"code": 204, "body": "none"}
    assert wrapper.calls[0]["arguments"] == {"id": "abc123", "rating": rating}


def test_videos_rate_descriptor_exposes_caller_metadata_and_examples():
    """Expose usage notes and examples needed before video rating calls."""
    from mcp_server.tools.youtube_common.videos import build_videos_rate_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor()])
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    metadata = listed["videos_rate"]["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}
    metadata_text = " ".join([listed["videos_rate"]["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert "Quota cost: 50" in metadata_text
    assert "OAuth" in metadata_text
    assert "id" in metadata_text
    assert "rating" in metadata_text
    assert "none" in metadata_text
    assert "no request body" in metadata_text
    assert {"authorized_like_rating", "authorized_clear_rating", "missing_oauth"}.issubset(example_names)


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"rating": "like"}, "arguments missing required field: id"),
        ({"id": "abc123"}, "arguments missing required field: rating"),
    ],
)
def test_videos_rate_descriptor_schema_rejects_missing_required_inputs(arguments, message):
    """Reject missing required rating fields before handler execution."""
    from mcp_server.tools.youtube_common.videos import build_videos_rate_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match=message):
        dispatcher.call_tool("videos_rate", arguments)

    assert wrapper.calls == []


def test_videos_rate_descriptor_rejects_missing_oauth_safely():
    """Reject valid rating requests with missing OAuth before Layer 1 execution."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, build_videos_rate_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor(wrapper=wrapper, oauth_token=None)])

    with pytest.raises(VideosRateToolError) as exc_info:
        dispatcher.call_tool("videos_rate", {"id": "abc123", "rating": "like"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_videos_rate_descriptor_rejects_unsupported_rating_and_body():
    """Reject unsupported rating and request body fields through the descriptor."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, build_videos_rate_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor()])

    with pytest.raises(VideosRateToolError) as rating_exc:
        dispatcher.call_tool("videos_rate", {"id": "abc123", "rating": "LIKE"})
    with pytest.raises(ValueError, match="arguments contain unsupported field: body"):
        dispatcher.call_tool("videos_rate", {"id": "abc123", "rating": "like", "body": {}})

    assert rating_exc.value.category == "invalid_request"
    assert rating_exc.value.details["field"] == "rating"


def test_videos_rate_descriptor_propagates_sanitized_access_failures():
    """Expose sanitized rating access failures from the registered handler."""
    from mcp_server.tools.youtube_common.videos import VideosRateToolError, build_videos_rate_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_rate_tool_descriptor(wrapper=AccessFailingWrapper())])

    with pytest.raises(VideosRateToolError) as exc_info:
        dispatcher.call_tool("videos_rate", {"id": "abc123", "rating": "like"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)


def test_videos_get_rating_descriptor_registers_as_executable_lookup_tool():
    """Register and execute the ``videos_getRating`` descriptor through the dispatcher."""
    from mcp_server.tools.youtube_common.videos import build_videos_get_rating_tool_descriptor

    wrapper = RecordingWrapper(
        payload={"items": [{"videoId": "abc123", "rating": "like"}, {"videoId": "def456", "rating": "none"}]}
    )
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor(wrapper=wrapper)])

    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    result = dispatcher.call_tool("videos_getRating", {"id": "abc123,def456"})

    assert listed["videos_getRating"]["metadata"]["upstream"]["operationKey"] == "videos.getRating"
    assert listed["videos_getRating"]["metadata"]["quotaCost"] == 1
    assert listed["videos_getRating"]["metadata"]["authMode"] == "oauth_required"
    assert listed["videos_getRating"]["metadata"]["availabilityState"] == "active"
    assert result["endpoint"] == "videos.getRating"
    assert result["quotaCost"] == 1
    assert result["lookup"]["requestedIds"] == ["abc123", "def456"]
    assert result["items"][0]["rating"] == "like"
    assert result["items"][1]["isUnrated"] is True
    assert result["auth"] == {"mode": "oauth_required", "path": "restricted"}
    assert wrapper.calls[0]["arguments"] == {"id": "abc123,def456"}


def test_videos_get_rating_descriptor_exposes_caller_metadata_and_examples():
    """Expose usage notes and examples needed before video rating lookup calls."""
    from mcp_server.tools.youtube_common.videos import build_videos_get_rating_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor()])
    listed = {tool["name"]: tool for tool in dispatcher.list_tools()}
    metadata = listed["videos_getRating"]["metadata"]
    example_names = {example["name"] for example in metadata["examples"]}
    metadata_text = " ".join([listed["videos_getRating"]["description"], *metadata["usageNotes"], *metadata["caveats"]])

    assert "Quota cost: 1" in metadata_text
    assert "OAuth" in metadata_text
    assert "one to fifty" in metadata_text
    assert "onBehalfOfContentOwner" in metadata_text
    assert "none" in metadata_text
    assert "unspecified" in metadata_text
    assert "no request body" in metadata_text
    assert {"authorized_single_video_lookup", "authorized_multi_video_lookup", "missing_oauth"}.issubset(example_names)


def test_videos_get_rating_descriptor_schema_rejects_missing_required_inputs():
    """Reject missing required rating lookup fields before handler execution."""
    from mcp_server.tools.youtube_common.videos import build_videos_get_rating_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor(wrapper=wrapper)])

    with pytest.raises(ValueError, match="arguments missing required field: id"):
        dispatcher.call_tool("videos_getRating", {})

    assert wrapper.calls == []


def test_videos_get_rating_descriptor_rejects_missing_oauth_safely():
    """Reject valid lookup requests with missing OAuth before Layer 1 execution."""
    from mcp_server.tools.youtube_common.videos import VideosGetRatingToolError, build_videos_get_rating_tool_descriptor

    wrapper = RecordingWrapper()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor(wrapper=wrapper, oauth_token=None)])

    with pytest.raises(VideosGetRatingToolError) as exc_info:
        dispatcher.call_tool("videos_getRating", {"id": "abc123"})

    assert exc_info.value.category == "authentication_failed"
    assert exc_info.value.details == {"authMode": "oauth_required"}
    assert wrapper.calls == []


def test_videos_get_rating_descriptor_rejects_duplicate_over_limit_body_and_delegation():
    """Reject malformed identifier, body, and delegation fields through the descriptor."""
    from mcp_server.tools.youtube_common.videos import VideosGetRatingToolError, build_videos_get_rating_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor()])

    with pytest.raises(VideosGetRatingToolError) as duplicate_exc:
        dispatcher.call_tool("videos_getRating", {"id": "abc123,abc123"})
    with pytest.raises(VideosGetRatingToolError) as limit_exc:
        dispatcher.call_tool("videos_getRating", {"id": ",".join(f"video-{index}" for index in range(51))})
    with pytest.raises(ValueError, match="arguments contain unsupported field: body"):
        dispatcher.call_tool("videos_getRating", {"id": "abc123", "body": {}})
    with pytest.raises(ValueError, match="onBehalfOfContentOwner must be at least 1 characters"):
        dispatcher.call_tool("videos_getRating", {"id": "abc123", "onBehalfOfContentOwner": ""})

    assert duplicate_exc.value.category == "invalid_request"
    assert duplicate_exc.value.details["field"] == "id"
    assert limit_exc.value.details["field"] == "id"


def test_videos_get_rating_descriptor_propagates_sanitized_access_failures():
    """Expose sanitized rating lookup access failures from the registered handler."""
    from mcp_server.tools.youtube_common.videos import VideosGetRatingToolError, build_videos_get_rating_tool_descriptor

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_rating_tool_descriptor(wrapper=AccessFailingWrapper())])

    with pytest.raises(VideosGetRatingToolError) as exc_info:
        dispatcher.call_tool("videos_getRating", {"id": "abc123"})

    assert exc_info.value.category == "authorization_failed"
    assert exc_info.value.details == {"reason": "forbidden"}
    assert "secret" not in str(exc_info.value.details)
