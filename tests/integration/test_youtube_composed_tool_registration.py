"""Integration-style tests for composed YouTube tool registration readiness."""

import pytest

from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_composed import (
    REPRESENTATIVE_TOOL_CONTRACTS,
    build_representative_tool_descriptor,
)


class SuccessfulVideoLookup:
    """Return one source video for concrete registration tests."""

    def __init__(self):
        """Initialize the recorded lower-level requests."""
        self.calls = []

    def __call__(self, arguments):
        """Record lookup arguments and return an available source video.

        :param arguments: Arguments passed to the lower-level lookup.
        :return: One-item lower-level result.
        """
        self.calls.append(arguments)
        return {"items": [{"id": "abc123", "snippet": {"title": "Example video"}, "contentDetails": {}}]}


def test_representative_youtube_composed_descriptor_registers_without_tool_execution():
    """Register representative Layer 3 metadata while keeping the handler inert."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_TOOL_CONTRACTS[0])
    dispatcher = InMemoryToolDispatcher(tools=[])

    dispatcher.register_tool(
        name=descriptor["name"],
        description=descriptor["description"],
        input_schema=descriptor["inputSchema"],
        handler=descriptor["handler"],
        metadata=descriptor["metadata"],
    )

    listed = dispatcher.list_tools()
    result = dispatcher.call_tool(descriptor["name"], {"videoId": "video-123"})

    assert listed[0]["metadata"]["representativeOnly"] is True
    assert result["representativeOnly"] is True
    assert result["concreteToolExecuted"] is False


def test_representative_youtube_composed_descriptor_exposes_family_and_composition_metadata():
    """Expose Layer 3 family and composition metadata through discovery shape."""
    descriptor = build_representative_tool_descriptor(REPRESENTATIVE_TOOL_CONTRACTS[-1])
    metadata = descriptor["metadata"]

    assert metadata["family"] == "playlists"
    assert metadata["compositionBoundary"]["kind"] == "fan_out"
    assert metadata["lowerLayerDependencies"] == ["playlistItems.list", "captions.list", "captions.download"]


def test_concrete_video_details_descriptor_registers_and_executes():
    """Register and execute the concrete one-video descriptor."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    lookup = SuccessfulVideoLookup()
    descriptor = build_videos_get_video_tool_descriptor(lookup=lookup)
    dispatcher = InMemoryToolDispatcher(tools=[descriptor])

    result = dispatcher.call_tool("videos_getVideo", {"videoId": "abc123"})

    assert lookup.calls == [{"id": "abc123", "part": "snippet,contentDetails"}]
    assert result == {"videoId": "abc123", "title": "Example video"}
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_video_details_descriptor_returns_requested_optional_groups():
    """Return selected optional groups while retaining the core result."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    class OptionalGroupLookup:
        """Return source groups selected by the video-detail request."""

        def __call__(self, arguments):
            """Return a complete source item for optional-group mapping.

            :param arguments: Lower-level lookup arguments.
            :return: One source item with optional groups.
            """
            assert arguments["part"] == "snippet,contentDetails,statistics,topicDetails"
            return {
                "items": [
                    {
                        "id": "abc123",
                        "snippet": {"title": "Example video", "defaultLanguage": "en"},
                        "contentDetails": {"definition": "hd"},
                        "statistics": {"viewCount": "1000"},
                        "topicDetails": {"topicCategories": ["https://example.invalid/topic"]},
                    }
                ]
            }

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_video_tool_descriptor(lookup=OptionalGroupLookup())])

    result = dispatcher.call_tool("videos_getVideo", {"videoId": "abc123", "parts": ["statistics", "topicDetails"]})

    assert result["videoId"] == "abc123"
    assert result["statistics"] == {"viewCount": "1000"}
    assert result["topicDetails"] == {"topicCategories": ["https://example.invalid/topic"]}
    assert "snippet" not in result


def test_concrete_video_details_descriptor_returns_safe_failure_categories():
    """Expose public failures without leaking lower-level diagnostics."""
    from mcp_server.tools.youtube_common.videos import VideosListToolError
    from mcp_server.tools.youtube_composed.videos import VideosGetVideoToolError, build_videos_get_video_tool_descriptor

    class FailingLookup:
        """Raise a lower-level quota failure containing unsafe diagnostics."""

        def __call__(self, _arguments):
            """Raise the configured quota failure.

            :param _arguments: Ignored lookup arguments.
            :raises VideosListToolError: Always raised for the test.
            """
            raise VideosListToolError(
                "quota exceeded",
                category="quota_exhausted",
                details={"reason": "quota exceeded", "api_key": "secret", "raw_body": "hidden"},
            )

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_video_tool_descriptor(lookup=FailingLookup())])

    with pytest.raises(VideosGetVideoToolError) as exc_info:
        dispatcher.call_tool("videos_getVideo", {"videoId": "abc123"})

    assert exc_info.value.category == "quota_exhaustion"
    assert exc_info.value.details == {"reason": "quota exceeded"}
