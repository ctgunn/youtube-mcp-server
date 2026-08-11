"""Integration-style tests for composed YouTube tool registration readiness."""

import pytest


from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_composed import (
    REPRESENTATIVE_TOOL_CONTRACTS,
    build_representative_tool_descriptor,
)


def test_concrete_transcript_descriptor_registers_and_executes():
    """Register and invoke the concrete transcript descriptor."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_get_transcript_tool_descriptor

    calls = []
    def caption_list(arguments):
        """Return one accessible caption track.

        :param arguments: Caption-list arguments.
        :return: Controlled list result.
        """
        calls.append(("list", arguments))
        return {"items": [{"id": "caption-1", "snippet": {"language": "en", "status": "serving"}}]}
    def caption_download(arguments):
        """Return one VTT download.

        :param arguments: Caption-download arguments.
        :return: Controlled download result.
        """
        calls.append(("download", arguments))
        return {"content": "WEBVTT\n\n00:00.000 --> 00:01.000\nHello"}
    descriptor = build_transcripts_get_transcript_tool_descriptor(caption_list=caption_list, caption_download=caption_download)
    result = InMemoryToolDispatcher(tools=[descriptor]).call_tool("transcripts_getTranscript", {"videoId": "abc"})
    assert result["text"] == "Hello"
    assert calls == [("list", {"part": "snippet", "videoId": "abc"}), ("download", {"id": "caption-1", "tfmt": "vtt"})]


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


def test_concrete_video_details_registration_preserves_lower_layer_provenance():
    """Keep concrete video details tied to the public ``videos.list`` boundary.

    :return: ``None`` after validating registration metadata and result shape.
    """
    from mcp_server.tools.youtube_composed.videos import build_videos_get_video_tool_descriptor

    descriptor = build_videos_get_video_tool_descriptor(lookup=SuccessfulVideoLookup())

    assert descriptor["metadata"]["lowerLayerDependencies"] == ["videos.list"]
    assert "representativeOnly" not in descriptor["metadata"]
    assert descriptor["inputSchema"]["required"] == ["videoId"]


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


def test_concrete_video_search_descriptor_registers_and_executes_query_only_search():
    """Register and invoke the concrete query-only video-search descriptor."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_tool_descriptor

    class SearchLookup:
        """Return one video-search item and record public arguments."""

        def __init__(self):
            """Initialize the call history."""
            self.calls = []

        def __call__(self, arguments):
            """Record base-search arguments and return one source item.

            :param arguments: Public Layer 2 search arguments.
            :return: One video-search source result.
            """
            self.calls.append(arguments)
            return {"items": [{"id": {"videoId": "abc123"}, "snippet": {"title": "Example video", "channelId": "UC123"}}]}

    search = SearchLookup()
    dispatcher = InMemoryToolDispatcher(tools=[build_videos_search_videos_tool_descriptor(search=search)])

    result = dispatcher.call_tool("videos_searchVideos", {"query": "example"})

    assert search.calls == [{"part": "snippet", "q": "example", "type": "video", "maxResults": 10, "order": "relevance"}]
    assert result["items"] == [{"videoId": "abc123", "title": "Example video", "channelId": "UC123"}]
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_video_search_descriptor_composes_channel_filtering():
    """Register channel-aware search composition with injected dependencies."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_tool_descriptor

    def search(arguments):
        """Return one base candidate for the configured search request.

        :param arguments: Public Layer 2 search arguments.
        :return: One video-search result.
        """
        assert arguments["type"] == "video"
        return {"items": [{"id": {"videoId": "abc123"}, "snippet": {"title": "Example", "channelId": "UC123"}}]}

    def channels(arguments):
        """Return one public channel matching the batched selector.

        :param arguments: Public Layer 2 channel arguments.
        :return: One channel metadata result.
        """
        assert arguments == {"part": "snippet,statistics,contentDetails", "id": "UC123"}
        return {"items": [{"id": "UC123", "snippet": {"title": "Creator Sam"}, "statistics": {"subscriberCount": "12"}}]}

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_search_videos_tool_descriptor(search=search, channels=channels)])

    result = dispatcher.call_tool("videos_searchVideos", {"query": "example", "channelMinSubscribers": 10})

    assert result["items"][0]["channel"]["subscriberCount"] == "12"


def test_concrete_video_search_descriptor_ranks_before_unique_channel_selection():
    """Expose ranked, one-per-channel output through the executable descriptor."""
    from mcp_server.tools.youtube_composed.videos import build_videos_search_videos_tool_descriptor

    def search(_arguments):
        """Return candidates whose base order differs from subscriber ranking.

        :param _arguments: Ignored Layer 2 search request.
        :return: Three candidates including a repeated channel.
        """
        return {
            "items": [
                {"id": {"videoId": "high-first"}, "snippet": {"title": "High", "channelId": "UCH"}},
                {"id": {"videoId": "low"}, "snippet": {"title": "Low", "channelId": "UCL"}},
                {"id": {"videoId": "high-second"}, "snippet": {"title": "High again", "channelId": "UCH"}},
            ]
        }

    def channels(_arguments):
        """Return ranking metadata for both distinct candidate channels.

        :param _arguments: Ignored Layer 2 channel request.
        :return: Subscriber counts ordered opposite to base search.
        """
        return {
            "items": [
                {"id": "UCH", "statistics": {"subscriberCount": "100"}},
                {"id": "UCL", "statistics": {"subscriberCount": "1"}},
            ]
        }

    descriptor = build_videos_search_videos_tool_descriptor(search=search, channels=channels)
    result = InMemoryToolDispatcher(tools=[descriptor]).call_tool(
        "videos_searchVideos", {"query": "example", "sortBy": "subscribers_asc", "uniqueChannels": True}
    )

    assert [item["videoId"] for item in result["items"]] == ["low", "high-first"]
