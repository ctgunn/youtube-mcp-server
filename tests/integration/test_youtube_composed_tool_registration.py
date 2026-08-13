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


def test_concrete_transcript_language_descriptor_registers_and_executes_one_listing():
    """Register and invoke one bounded language-discovery descriptor."""
    from mcp_server.tools.youtube_composed.transcripts import build_transcripts_list_languages_tool_descriptor

    calls = []

    def caption_list(arguments):
        """Return caption options and record the one discovery request.

        :param arguments: Lower-layer caption-list arguments.
        :return: Controlled caption-list result.
        """
        calls.append(arguments)
        return {"items": [{"id": "caption-1", "snippet": {"language": "en", "trackKind": "standard"}}]}

    descriptor = build_transcripts_list_languages_tool_descriptor(caption_list=caption_list)
    dispatcher = InMemoryToolDispatcher(tools=[descriptor])
    result = dispatcher.call_tool("transcripts_listLanguages", {"videoId": "abc"})

    assert calls == [{"part": "snippet", "videoId": "abc"}]
    assert result["languageOptions"][0]["captionTrackId"] == "caption-1"
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


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


def test_concrete_playlist_details_descriptor_registers_and_exposes_scope():
    """Register and execute the concrete playlist detail descriptor.

    :return: ``None`` after validating registration, provenance, and scope.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_tool_descriptor

    calls = []

    def lookup(arguments):
        """Return one public playlist and record its direct request.

        :param arguments: Lower-level playlist-list arguments.
        :return: One available public playlist result.
        """
        calls.append(arguments)
        return {"items": [{"id": "PL123", "snippet": {"title": "Example"}, "contentDetails": {}, "status": {}}]}

    dispatcher = InMemoryToolDispatcher(tools=[build_playlists_get_playlist_tool_descriptor(lookup=lookup)])
    result = dispatcher.call_tool("playlists_getPlaylist", {"playlistId": "PL123"})

    assert calls == [{"part": "snippet,contentDetails,status", "id": "PL123"}]
    assert result["playlistId"] == "PL123"
    assert result["fieldProvenance"]["playlistId"] == "raw_upstream"
    assert result["contentScope"] == {
        "playlistItemsIncluded": False,
        "playlistItemsTool": "playlists_getPlaylistItems",
        "stateObservedAtRequest": True,
    }
    assert "items" not in result
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_playlist_items_descriptor_registers_and_executes_one_listing():
    """Register and invoke the composed playlist-items descriptor once.

    :return: ``None`` after asserting one bounded injected lower-layer listing.
    """
    from mcp_server.tools.youtube_composed.playlists import build_playlists_get_playlist_items_tool_descriptor

    calls = []

    def playlist_items(arguments):
        """Return one public playlist item and record its request.

        :param arguments: Lower-layer playlist-item listing arguments.
        :return: One available public playlist-item result.
        """
        calls.append(arguments)
        return {
            "items": [
                {
                    "id": "playlist-item-1",
                    "snippet": {"position": 0, "resourceId": {"videoId": "video-1"}, "title": "Example"},
                    "contentDetails": {"videoId": "video-1"},
                    "status": {"privacyStatus": "public"},
                }
            ]
        }

    dispatcher = InMemoryToolDispatcher(tools=[build_playlists_get_playlist_items_tool_descriptor(playlist_items=playlist_items)])
    result = dispatcher.call_tool("playlists_getPlaylistItems", {"playlistId": "PL123", "maxResults": 1})

    assert calls == [{"part": "snippet,contentDetails,status", "playlistId": "PL123", "maxResults": 1}]
    assert result["items"][0]["videoId"] == "video-1"
    assert result["items"][0]["availabilityState"] == "available"
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


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


def test_concrete_channel_details_descriptor_registers_with_injected_dependencies():
    """Register the concrete channel descriptor with controlled dependencies."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_tool_descriptor

    def channels(arguments):
        """Return one public channel for the requested identifier.

        :param arguments: Lower-level channel-list arguments.
        :return: One available public channel result.
        """
        assert arguments == {"part": "snippet,contentDetails", "id": "UC123"}
        return {"items": [{"id": "UC123", "snippet": {"title": "Example"}, "contentDetails": {}}]}

    descriptor = build_channels_get_channel_tool_descriptor(channels=channels, playlist_items=lambda _arguments: {"items": []})
    dispatcher = InMemoryToolDispatcher(tools=[descriptor])

    result = dispatcher.call_tool("channels_getChannel", {"channelId": "UC123"})

    assert result["channelId"] == "UC123"
    assert result["enrichment"] == {"status": "unavailable"}
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_channel_details_descriptor_returns_partial_profile_after_enrichment_failure():
    """Keep an injected core profile available when latest enrichment fails."""
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channel_tool_descriptor

    def channels(_arguments):
        """Return one channel with a public uploads playlist.

        :param _arguments: Ignored lower-level channel request.
        :return: One available channel result.
        """
        return {"items": [{"id": "UC123", "snippet": {"title": "Example"}, "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]}

    def playlist_items(_arguments):
        """Raise a safe capacity error after core lookup success.

        :param _arguments: Ignored lower-level playlist request.
        :raises PlaylistItemsListToolError: Always raised for partial-profile coverage.
        """
        raise PlaylistItemsListToolError("quota", category="quota_exhausted", details={"api_key": "hidden"})

    dispatcher = InMemoryToolDispatcher(tools=[build_channels_get_channel_tool_descriptor(channels=channels, playlist_items=playlist_items)])

    result = dispatcher.call_tool("channels_getChannel", {"channelId": "UC123"})

    assert result["channelId"] == "UC123"
    assert result["enrichment"]["category"] == "partial_enrichment_failure"
    assert result["enrichment"]["causeCategory"] == "quota_exhaustion"


def test_concrete_batch_channel_details_descriptor_registers_and_executes():
    """Register and invoke the concrete batch channel descriptor."""
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_tool_descriptor

    def channels(arguments):
        """Return two source records for one controlled batch lookup.

        :param arguments: Lower-level bulk lookup arguments.
        :return: Two available public channels.
        """
        assert arguments == {"part": "snippet,contentDetails", "id": "UC123,UC456"}
        return {
            "items": [
                {"id": "UC123", "snippet": {"title": "First"}, "contentDetails": {}},
                {"id": "UC456", "snippet": {"title": "Second"}, "contentDetails": {}},
            ]
        }

    dispatcher = InMemoryToolDispatcher(
        tools=[build_channels_get_channels_tool_descriptor(channels=channels, playlist_items=lambda _arguments: {"items": []})]
    )
    result = dispatcher.call_tool("channels_getChannels", {"channelIds": ["UC123", "UC456"]})

    assert [item["channelId"] for item in result["results"]] == ["UC123", "UC456"]
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_batch_channel_details_descriptor_returns_mixed_safe_outcomes():
    """Keep registered batch results usable across unavailable and partial items."""
    from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError
    from mcp_server.tools.youtube_composed.channels import build_channels_get_channels_tool_descriptor

    def channels(_arguments):
        """Return only one available source item from the requested batch.

        :param _arguments: Ignored lower-level bulk request.
        :return: One available source channel.
        """
        return {
            "items": [
                {
                    "id": "UC123",
                    "snippet": {"title": "Available"},
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
                }
            ]
        }

    def playlist_items(_arguments):
        """Raise a safe source failure after core item success.

        :param _arguments: Ignored lower-level playlist request.
        :raises PlaylistItemsListToolError: Always raised for partial-outcome coverage.
        """
        raise PlaylistItemsListToolError("hidden", category="upstream_failure", details={"api_key": "secret"})

    dispatcher = InMemoryToolDispatcher(
        tools=[build_channels_get_channels_tool_descriptor(channels=channels, playlist_items=playlist_items)]
    )
    result = dispatcher.call_tool("channels_getChannels", {"channelIds": ["UC123", "UC404"]})

    assert [item["outcome"]["status"] for item in result["results"]] == ["partial", "unavailable"]
    assert result["summary"] == {"requested": 2, "successful": 0, "unavailable": 1, "partiallyEnriched": 1}
    assert "secret" not in str(result)


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


def test_concrete_video_statistics_descriptor_registers_and_executes_one_lookup():
    """Register and invoke the public statistics descriptor with injected data."""
    from mcp_server.tools.youtube_composed.videos import build_videos_get_statistics_tool_descriptor

    calls = []

    def lookup(arguments):
        """Return controlled statistics for one expected direct lookup.

        :param arguments: Lower-level video-list request.
        :return: One source video with public statistics.
        """
        calls.append(arguments)
        return {"items": [{"id": "abc123", "statistics": {"viewCount": "1000", "likeCount": "45"}}]}

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_statistics_tool_descriptor(lookup=lookup)])
    result = dispatcher.call_tool("videos_getStatistics", {"videoId": "abc123"})

    assert calls == [{"id": "abc123", "part": "statistics"}]
    assert result["statistics"]["viewCount"]["value"] == "1000"
    assert result["statistics"]["commentCount"]["state"] == "unavailable"
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_video_statistics_descriptor_returns_safe_lookup_failures():
    """Expose translated errors without unsafe lower-layer diagnostic details."""
    from mcp_server.tools.youtube_common.videos import VideosListToolError
    from mcp_server.tools.youtube_composed.videos import VideosGetStatisticsToolError, build_videos_get_statistics_tool_descriptor

    def lookup(_arguments):
        """Raise a controlled quota failure with unsafe source details.

        :param _arguments: Ignored lower-level video request.
        :raises VideosListToolError: Always raised for safe error coverage.
        """
        raise VideosListToolError("quota", category="quota_exhausted", details={"api_key": "hidden", "stack_trace": "hidden"})

    dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_statistics_tool_descriptor(lookup=lookup)])

    try:
        dispatcher.call_tool("videos_getStatistics", {"videoId": "abc123"})
    except VideosGetStatisticsToolError as error:
        assert error.category == "quota_exhaustion"
        assert "hidden" not in str(error.details)
    else:
        raise AssertionError("expected a translated statistics lookup failure")


def test_concrete_channel_search_descriptor_registers_and_executes_query_only_search():
    """Register and execute the concrete query-only channel search descriptor."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_tool_descriptor

    def search(arguments):
        """Return one base channel candidate for the configured query.

        :param arguments: Lower-level search request.
        :return: One public channel reference.
        """
        assert arguments == {"part": "snippet", "q": "creator", "type": "channel", "maxResults": 10, "order": "relevance"}
        return {"items": [{"id": {"channelId": "UC123"}, "snippet": {"title": "Creator"}}]}

    dispatcher = InMemoryToolDispatcher(tools=[build_channels_search_channels_tool_descriptor(search=search)])

    result = dispatcher.call_tool("channels_searchChannels", {"query": "creator"})

    assert result["items"][0]["channelId"] == "UC123"
    assert result["items"][0]["title"] == "Creator"
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_concrete_channel_search_descriptor_composes_public_refinement():
    """Execute bounded channel enrichment through the registered descriptor."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_tool_descriptor

    def search(_arguments):
        """Return one public base channel.

        :param _arguments: Ignored base-search request.
        :return: One channel reference.
        """
        return {"items": [{"id": {"channelId": "UC123"}, "snippet": {"title": "Creator Sam"}}]}

    def channels(arguments):
        """Return public metadata required for the filter.

        :param arguments: Lower-level batched channels-list arguments.
        :return: One channel record with public statistics.
        """
        assert arguments == {"part": "snippet,statistics,contentDetails", "id": "UC123"}
        return {"items": [{"id": "UC123", "snippet": {"title": "Creator Sam"}, "statistics": {"subscriberCount": "12"}}]}

    result = InMemoryToolDispatcher(tools=[build_channels_search_channels_tool_descriptor(search=search, channels=channels)]).call_tool(
        "channels_searchChannels", {"query": "creator", "minSubscribers": 10}
    )

    assert result["items"][0]["statistics"] == {"subscriberCount": "12"}


def test_concrete_channel_search_descriptor_applies_subscriber_ranking():
    """Execute deterministic public subscriber ranking through the descriptor."""
    from mcp_server.tools.youtube_composed.channels import build_channels_search_channels_tool_descriptor

    def search(_arguments):
        """Return two base channels in reverse subscriber order.

        :param _arguments: Ignored base-search request.
        :return: Two public channel references.
        """
        return {"items": [{"id": {"channelId": "UCH"}, "snippet": {"title": "High"}}, {"id": {"channelId": "UCL"}, "snippet": {"title": "Low"}}]}

    def channels(_arguments):
        """Return public subscriber counts for both candidates.

        :param _arguments: Ignored batched channel request.
        :return: Two public channel records.
        """
        return {"items": [{"id": "UCH", "statistics": {"subscriberCount": "100"}}, {"id": "UCL", "statistics": {"subscriberCount": "1"}}]}

    result = InMemoryToolDispatcher(tools=[build_channels_search_channels_tool_descriptor(search=search, channels=channels)]).call_tool(
        "channels_searchChannels", {"query": "creator", "sortBy": "subscribers_asc"}
    )

    assert [item["channelId"] for item in result["items"]] == ["UCL", "UCH"]


def test_creator_discovery_descriptor_executes_query_only_video_grouping():
    """Execute creator discovery through an injected public video search."""
    from mcp_server.tools.youtube_composed.channels import build_channels_find_creators_tool_descriptor

    def search(arguments):
        """Return one video-derived public channel.

        :param arguments: Lower-layer public video-search arguments.
        :return: One public video search result.
        """
        assert arguments["type"] == "video"
        return {"items": [{"id": {"videoId": "v1"}, "snippet": {"channelId": "UC1", "channelTitle": "Creator", "title": "Topic"}}]}

    result = InMemoryToolDispatcher(tools=[build_channels_find_creators_tool_descriptor(search=search)]).call_tool(
        "channels_findCreators", {"query": "creator"}
    )

    assert result["items"][0]["channelId"] == "UC1"


def test_channels_list_videos_descriptor_registers_and_executes_bounded_listing():
    """Register and execute the source-ordered channel video descriptor."""
    from mcp_server.tools.youtube_composed.channels import build_channels_list_videos_tool_descriptor

    def channels(arguments):
        """Return an uploads reference for the requested public channel.

        :param arguments: Lower-level channel-list request.
        :return: One public channel record with an uploads collection reference.
        """
        assert arguments == {"part": "contentDetails", "id": "UC123"}
        return {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]}

    def playlist_items(arguments):
        """Return two public videos in uploads-collection order.

        :param arguments: Lower-level playlist-item list request.
        :return: Ordered public uploads-collection items.
        """
        assert arguments == {"part": "snippet,contentDetails", "playlistId": "UU123", "maxResults": 10}
        return {"items": [{"snippet": {"resourceId": {"videoId": "v1"}, "title": "First"}}, {"snippet": {"resourceId": {"videoId": "v2"}, "title": "Second"}}]}

    descriptor = build_channels_list_videos_tool_descriptor(channels=channels, playlist_items=playlist_items)
    dispatcher = InMemoryToolDispatcher(tools=[descriptor])

    result = dispatcher.call_tool("channels_listVideos", {"channelId": "UC123"})

    assert [item["videoId"] for item in result["items"]] == ["v1", "v2"]
    assert result["returnedCount"] == 2
    assert "representativeOnly" not in dispatcher.list_tools()[0]["metadata"]


def test_channels_list_videos_descriptor_discloses_non_search_behavior_to_clients():
    """Keep the registered descriptor distinguishable from relevance-ranked search."""
    from mcp_server.tools.youtube_composed.channels import build_channels_list_videos_tool_descriptor

    descriptor = build_channels_list_videos_tool_descriptor()
    metadata = InMemoryToolDispatcher(tools=[descriptor]).list_tools()[0]["metadata"]

    assert metadata["orderingSemantics"]["rankingApplied"] is False
    assert metadata["publicContentPolicy"].startswith("Only publicly available")
    assert "search-oriented" in metadata["searchGuidance"].lower()
