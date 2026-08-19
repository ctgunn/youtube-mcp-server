import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import initialize_succeeded, route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class Layer3ToolError(ValueError):
    """Represent one YT-303 public tool failure for routing tests.

    :param category: Stable public Layer 3 failure category.
    """

    def __init__(self, category):
        """Initialize the configured routing-test failure.

        :param category: Stable public Layer 3 failure category.
        """
        super().__init__("safe public failure")
        self.category = category
        self.details = {"api_key": "hidden", "reason": "safe reason"}


class MethodRoutingTests(unittest.TestCase):
    """Unit coverage for MCP method routing behavior."""

    def setUp(self):
        """Create a default in-memory dispatcher for each routing test."""
        self.dispatcher = InMemoryToolDispatcher()

    def test_unsupported_method_returns_structured_error(self):
        """Return a structured error for unsupported MCP methods."""
        payload = {"jsonrpc": "2.0", "id": "req-1", "method": "unknown/method", "params": {}}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-1")
        self.assertEqual(response["error"]["code"], -32601)
        self.assertEqual(response["error"]["data"]["category"], "unsupported_method")

    def test_non_object_params_returns_invalid_argument(self):
        """Return a malformed request error when params are not an object."""
        payload = {"jsonrpc": "2.0", "id": "req-2", "method": "initialize", "params": "bad"}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], -32600)
        self.assertEqual(response["error"]["data"]["category"], "malformed_request")

    def test_registered_tool_dispatch_success(self):
        """Route a valid tools/call request to a registered handler."""
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="echo",
            description="Echo",
            input_schema={"type": "object", "properties": {"value": {"type": "string"}}, "additionalProperties": False},
            handler=lambda arguments: {"value": arguments.get("value", "")},
        )
        payload = {
            "jsonrpc": "2.0",
            "id": "req-3",
            "method": "tools/call",
            "params": {"name": "echo", "arguments": {"value": "ok"}},
        }
        response = route_mcp_request(payload, dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        payload = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(payload["value"], "ok")

    def test_layer3_tool_categories_return_numeric_safe_mcp_errors(self):
        """Serialize every YT-303 Layer 3 category without leaking secrets."""
        expected_protocol_categories = {
            "invalid_parameters": "invalid_argument",
            "language_unavailable": "resource_missing",
            "unavailable_resource": "resource_missing",
            "authorization_sensitive_data": "authorization_denied",
            "quota_exhaustion": "transport_not_supported",
            "source_unavailable": "unavailable_source",
            "upstream_failure": "internal_execution_failure",
            "partial_enrichment_failure": "unavailable_source",
            "unsupported_filter_or_sort": "invalid_argument",
        }
        for category, protocol_category in expected_protocol_categories.items():
            with self.subTest(category=category):
                dispatcher = InMemoryToolDispatcher(tools=[])

                def handler(_arguments, error_category=category):
                    """Raise the configured public Layer 3 test error.

                    :param _arguments: Ignored tool arguments.
                    :param error_category: Category exposed by the test error.
                    :raises Layer3ToolError: Always raised to exercise routing.
                    """
                    raise Layer3ToolError(error_category)

                dispatcher.register_tool(
                    name="videos_searchVideos",
                    description="Test Layer 3 category routing.",
                    input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                    handler=handler,
                )
                response = route_mcp_request(
                    {
                        "jsonrpc": "2.0",
                        "id": f"req-layer3-{category}",
                        "method": "tools/call",
                        "params": {"name": "videos_searchVideos", "arguments": {}},
                    },
                    dispatcher,
                )

                self.assertIsInstance(response["error"]["code"], int)
                self.assertEqual(response["error"]["data"]["category"], category)
                self.assertNotIn("api_key", str(response["error"]))
                self.assertEqual(response["error"]["data"]["toolName"], "videos_searchVideos")
                self.assertEqual(protocol_category, response["error"]["data"]["protocolCategory"])

    def test_channel_detail_error_categories_route_safely(self):
        """Serialize channel-detail failures without exposing unsafe details."""
        from mcp_server.tools.youtube_composed.channels import (
            ChannelsGetChannelToolError,
            build_channels_get_channel_tool_descriptor,
        )

        def channels(_arguments):
            """Raise a lower-level quota failure with unsafe diagnostic values.

            :param _arguments: Ignored lower-level request arguments.
            :raises Exception: Always raised to exercise safe public mapping.
            """
            from mcp_server.tools.youtube_common.channels import ChannelsListToolError

            raise ChannelsListToolError("quota", category="quota_exhausted", details={"api_key": "hidden", "raw_body": "hidden"})

        dispatcher = InMemoryToolDispatcher(
            tools=[build_channels_get_channel_tool_descriptor(channels=channels, playlist_items=lambda _arguments: {"items": []})]
        )
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-channel-detail-error",
                "method": "tools/call",
                "params": {"name": "channels_getChannel", "arguments": {"channelId": "UC123"}},
            },
            dispatcher,
        )

        assert response["error"]["data"]["category"] == "quota_exhaustion"
        assert response["error"]["data"]["protocolCategory"] == "transport_not_supported"
        assert "hidden" not in str(response["error"])
        assert ChannelsGetChannelToolError is not None

    def test_channel_video_listing_error_categories_route_safely(self):
        """Serialize required collection failures without unsafe diagnostics."""
        from mcp_server.tools.youtube_common.playlist_items import (
            PlaylistItemsListToolError,
        )
        from mcp_server.tools.youtube_composed.channels import (
            ChannelsListVideosToolError,
            build_channels_list_videos_tool_descriptor,
        )

        def channels(_arguments):
            """Return a channel with a public uploads collection reference.

            :param _arguments: Ignored lower-level channel request.
            :return: One channel record for protocol error coverage.
            """
            return {"items": [{"id": "UC123", "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}}}]}

        def playlist_items(_arguments):
            """Raise a safe capacity failure containing unsafe details.

            :param _arguments: Ignored lower-level playlist-item request.
            :raises PlaylistItemsListToolError: Always raised for routing coverage.
            """
            raise PlaylistItemsListToolError("quota", category="quota_exhausted", details={"api_key": "hidden", "raw_body": "hidden"})

        dispatcher = InMemoryToolDispatcher(
            tools=[build_channels_list_videos_tool_descriptor(channels=channels, playlist_items=playlist_items)]
        )
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-channel-videos-error",
                "method": "tools/call",
                "params": {"name": "channels_listVideos", "arguments": {"channelId": "UC123"}},
            },
            dispatcher,
        )

        assert response["error"]["data"]["category"] == "quota_exhaustion"
        assert response["error"]["data"]["protocolCategory"] == "transport_not_supported"
        assert "hidden" not in str(response["error"])
        assert ChannelsListVideosToolError is not None

    def test_playlist_detail_error_categories_route_safely(self):
        """Serialize playlist-detail capacity failures without unsafe details.

        :return: ``None`` after validating safe protocol error serialization.
        """
        from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError
        from mcp_server.tools.youtube_composed.playlists import (
            build_playlists_get_playlist_tool_descriptor,
        )

        def lookup(_arguments):
            """Raise a capacity failure containing unsafe lower-layer details.

            :param _arguments: Ignored lower-layer playlist request.
            :raises PlaylistsListToolError: Always raised for routing coverage.
            """
            raise PlaylistsListToolError(
                "quota",
                category="quota_exhausted",
                details={"api_key": "hidden", "raw_body": "hidden"},
            )

        dispatcher = InMemoryToolDispatcher(tools=[build_playlists_get_playlist_tool_descriptor(lookup=lookup)])
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-playlist-detail-error",
                "method": "tools/call",
                "params": {"name": "playlists_getPlaylist", "arguments": {"playlistId": "PL123"}},
            },
            dispatcher,
        )

        assert response["error"]["data"]["category"] == "quota_exhaustion"
        assert response["error"]["data"]["protocolCategory"] == "transport_not_supported"
        assert "hidden" not in str(response["error"])

    def test_playlist_item_retrieval_error_categories_route_safely(self):
        """Serialize playlist-item capacity failures without unsafe details.

        :return: ``None`` after validating safe protocol error serialization.
        """
        from mcp_server.tools.youtube_common.playlist_items import (
            PlaylistItemsListToolError,
        )
        from mcp_server.tools.youtube_composed.playlists import (
            build_playlists_get_playlist_items_tool_descriptor,
        )

        def playlist_items(_arguments):
            """Raise a capacity failure containing unsafe lower-layer details.

            :param _arguments: Ignored lower-layer playlist-item request.
            :raises PlaylistItemsListToolError: Always raised for routing coverage.
            """
            raise PlaylistItemsListToolError(
                "quota",
                category="quota_exhausted",
                details={"api_key": "hidden", "raw_body": "hidden"},
            )

        dispatcher = InMemoryToolDispatcher(
            tools=[build_playlists_get_playlist_items_tool_descriptor(playlist_items=playlist_items)]
        )
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-playlist-items-error",
                "method": "tools/call",
                "params": {"name": "playlists_getPlaylistItems", "arguments": {"playlistId": "PL123"}},
            },
            dispatcher,
        )

        assert response["error"]["data"]["category"] == "quota_exhaustion"
        assert response["error"]["data"]["protocolCategory"] == "transport_not_supported"
        assert "hidden" not in str(response["error"])

    def test_baseline_tools_are_discoverable(self):
        """List the built-in baseline tools through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-4", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        names = [item["name"] for item in response["result"]["tools"]]
        self.assertIn("server_ping", names)
        self.assertIn("server_info", names)
        self.assertIn("server_list_tools", names)

    def test_activities_list_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid activities_list call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-activities-ok",
            "method": "tools/call",
            "params": {"name": "activities_list", "arguments": {"part": "snippet", "channelId": "UC123"}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "activities.list")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["requestedParts"], ["snippet"])

    def test_activities_list_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid activities_list call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-activities-invalid",
            "method": "tools/call",
            "params": {
                "name": "activities_list",
                "arguments": {"part": "snippet", "channelId": "UC123", "mine": True},
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "activities_list")

    def test_channels_list_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid channels_list selector combination."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channels-invalid",
            "method": "tools/call",
            "params": {
                "name": "channels_list",
                "arguments": {"part": "snippet", "id": "UC123", "mine": True},
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "channels_list")

    def test_channels_list_tools_call_mine_without_oauth_returns_safe_error(self):
        """Return a safe auth error for owner-scoped channels_list without OAuth."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channels-auth",
            "method": "tools/call",
            "params": {"name": "channels_list", "arguments": {"part": "snippet", "mine": True}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "authentication_failed")
        self.assertEqual(response["error"]["data"]["toolName"], "channels_list")
        self.assertNotIn("public-channel-access", str(response["error"]))

    def test_channel_sections_list_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid channelSections_list call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channel-sections-ok",
            "method": "tools/call",
            "params": {"name": "channelSections_list", "arguments": {"part": "snippet", "channelId": "UC123"}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "channelSections.list")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["requestedParts"], ["snippet"])
        self.assertEqual(result["selector"], {"name": "channelId"})

    def test_channel_sections_list_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid channelSections_list selector combination."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channel-sections-invalid",
            "method": "tools/call",
            "params": {
                "name": "channelSections_list",
                "arguments": {"part": "snippet", "channelId": "UC123", "mine": True},
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "channelSections_list")

    def test_channel_sections_list_tools_call_mine_without_oauth_returns_safe_error(self):
        """Return a safe auth error for owner-scoped channelSections_list without OAuth."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channel-sections-auth",
            "method": "tools/call",
            "params": {"name": "channelSections_list", "arguments": {"part": "snippet", "mine": True}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "authentication_failed")
        self.assertEqual(response["error"]["data"]["toolName"], "channelSections_list")
        self.assertNotIn("public-channel-section-access", str(response["error"]))

    def test_channel_sections_insert_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid channelSections_insert body."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channel-sections-insert-invalid",
            "method": "tools/call",
            "params": {
                "name": "channelSections_insert",
                "arguments": {
                    "part": "snippet",
                    "body": {"snippet": {"channelId": "UC-secret"}},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "channelSections_insert")
        self.assertNotIn("authorized-channel-section-write", str(response["error"]))
        self.assertNotIn("UC-secret", str(response["error"]))

    def test_channel_sections_update_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid channelSections_update body."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channel-sections-update-invalid",
            "method": "tools/call",
            "params": {
                "name": "channelSections_update",
                "arguments": {
                    "part": "snippet",
                    "body": {"snippet": {"type": "singlePlaylist"}},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "channelSections_update")
        self.assertNotIn("authorized-channel-section-write", str(response["error"]))
        self.assertNotIn("UC-secret", str(response["error"]))

    def test_captions_list_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid captions_list call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-ok",
            "method": "tools/call",
            "params": {"name": "captions_list", "arguments": {"part": "snippet", "videoId": "video-123"}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "captions.list")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["requestedParts"], ["snippet"])

    def test_captions_list_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid captions_list call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-invalid",
            "method": "tools/call",
            "params": {"name": "captions_list", "arguments": {"part": "snippet", "videoId": "video-123", "maxResults": 51}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "captions_list")

    def test_captions_insert_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid captions_insert call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-insert-ok",
            "method": "tools/call",
            "params": {
                "name": "captions_insert",
                "arguments": {
                    "part": "snippet",
                    "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English captions"}},
                    "media": {"mimeType": "text/xml", "content": "caption text"},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "captions.insert")
        self.assertEqual(result["item"]["id"], "created-caption")
        self.assertEqual(result["requestedParts"], ["snippet"])

    def test_captions_insert_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid captions_insert call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-insert-invalid",
            "method": "tools/call",
            "params": {
                "name": "captions_insert",
                "arguments": {
                    "part": "snippet",
                    "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English captions"}},
                    "media": {"mimeType": "text/xml"},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "captions_insert")

    def test_captions_update_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid captions_update call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-update-ok",
            "method": "tools/call",
            "params": {
                "name": "captions_update",
                "arguments": {
                    "part": "snippet",
                    "body": {"id": "caption-1", "snippet": {"isDraft": False}},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "captions.update")
        self.assertEqual(result["item"]["id"], "caption-1")
        self.assertEqual(result["requestedParts"], ["snippet"])

    def test_captions_update_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid captions_update call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-update-invalid",
            "method": "tools/call",
            "params": {
                "name": "captions_update",
                "arguments": {
                    "part": "snippet",
                    "body": {"id": "caption-1"},
                    "media": {"mimeType": "text/xml"},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "captions_update")

    def test_captions_download_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid captions_download call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-download-ok",
            "method": "tools/call",
            "params": {
                "name": "captions_download",
                "arguments": {"id": "caption-1", "tfmt": "vtt", "tlang": "es"},
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "captions.download")
        self.assertEqual(result["content"], "caption content")
        self.assertEqual(result["requestedFormat"], "vtt")
        self.assertEqual(result["requestedLanguage"], "es")

    def test_captions_download_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid captions_download call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-captions-download-invalid",
            "method": "tools/call",
            "params": {
                "name": "captions_download",
                "arguments": {"id": "caption-1", "tfmt": "unsupported"},
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "captions_download")

    def test_channels_update_tools_call_success_returns_structured_result(self):
        """Return structured content for a valid channels_update call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channels-update-ok",
            "method": "tools/call",
            "params": {
                "name": "channels_update",
                "arguments": {
                    "part": "brandingSettings",
                    "body": {"id": "UC123", "brandingSettings": {"channel": {"description": "Updated"}}},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(result["endpoint"], "channels.update")
        self.assertEqual(result["quotaCost"], 50)
        self.assertEqual(result["updatedPart"], "brandingSettings")
        self.assertEqual(result["requestedParts"], ["brandingSettings"])
        self.assertEqual(result["item"]["id"], "UC123")

    def test_channels_update_tools_call_invalid_request_returns_safe_error(self):
        """Return a safe error for an invalid channels_update call."""
        payload = {
            "jsonrpc": "2.0",
            "id": "req-channels-update-invalid",
            "method": "tools/call",
            "params": {
                "name": "channels_update",
                "arguments": {
                    "part": "brandingSettings,localizations",
                    "body": {"id": "UC123", "brandingSettings": {"channel": {}}},
                },
            },
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["data"]["category"], "invalid_request")
        self.assertEqual(response["error"]["data"]["toolName"], "channels_update")
        self.assertNotIn("authorized-channel-update", str(response["error"]))

    def test_initialize_success_detection_accepts_initialize_result(self):
        """Treat a successful initialize response as initialized."""
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-init-success",
                "method": "initialize",
                "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
            },
            self.dispatcher,
        )
        self.assertTrue(initialize_succeeded(response))

    def test_initialize_success_detection_rejects_initialize_error(self):
        """Treat an initialize error response as not initialized."""
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-init-fail",
                "method": "initialize",
                "params": {},
            },
            self.dispatcher,
        )
        self.assertFalse(initialize_succeeded(response))

    def test_video_statistics_lookup_failure_routes_without_sensitive_details(self):
        """Serialize a statistics lookup failure as a safe MCP error."""
        from mcp_server.tools.youtube_common.videos import VideosListToolError
        from mcp_server.tools.youtube_composed.videos import (
            build_videos_get_statistics_tool_descriptor,
        )

        def lookup(_arguments):
            """Raise a controlled capacity failure with unsafe detail fields.

            :param _arguments: Ignored lower-layer request arguments.
            :raises VideosListToolError: Always raised to verify protocol mapping.
            """
            raise VideosListToolError(
                "quota",
                category="quota_exhausted",
                details={"api_key": "hidden", "stack_trace": "hidden"},
            )

        dispatcher = InMemoryToolDispatcher(tools=[build_videos_get_statistics_tool_descriptor(lookup=lookup)])
        response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-video-statistics-error",
                "method": "tools/call",
                "params": {"name": "videos_getStatistics", "arguments": {"videoId": "abc123"}},
            },
            dispatcher,
        )

        self.assertEqual(response["error"]["data"]["category"], "quota_exhaustion")
        self.assertEqual(response["error"]["data"]["protocolCategory"], "transport_not_supported")
        self.assertNotIn("hidden", str(response["error"]))


def test_channel_playlist_listing_routes_sanitized_source_errors():
    """Serialize channel playlist-listing failures without unsafe details.

    :return: ``None`` after validating the safe protocol error category.
    """
    from mcp_server.tools.youtube_common.playlists import PlaylistsListToolError
    from mcp_server.tools.youtube_composed.channels import (
        build_channels_list_playlists_tool_descriptor,
    )

    def playlists(_arguments):
        """Raise a source failure with details forbidden to public callers.

        :param _arguments: Ignored lower-layer playlist-list arguments.
        :raises PlaylistsListToolError: Always raised for protocol coverage.
        """
        raise PlaylistsListToolError("hidden", category="quota_exhausted", details={"api_key": "hidden", "raw_body": "hidden"})

    dispatcher = InMemoryToolDispatcher(
        tools=[build_channels_list_playlists_tool_descriptor(channels=lambda _arguments: {"items": [{"id": "UC123"}]}, playlists=playlists)]
    )
    response = route_mcp_request(
        {"jsonrpc": "2.0", "id": "req-channel-playlists-error", "method": "tools/call", "params": {"name": "channels_listPlaylists", "arguments": {"channelId": "UC123"}}},
        dispatcher,
    )

    assert response["error"]["data"]["category"] == "quota_exhaustion"
    assert "hidden" not in str(response["error"])


def test_channel_statistics_lookup_failure_routes_without_sensitive_details():
    """Serialize a channel-statistics failure as a safe MCP error.

    :return: ``None`` after validating protocol-safe error serialization.
    """
    from mcp_server.tools.youtube_common.channels import ChannelsListToolError
    from mcp_server.tools.youtube_composed.channels import (
        build_channels_get_statistics_tool_descriptor,
    )

    def channels(_arguments):
        """Raise a controlled capacity failure with unsafe detail fields.

        :param _arguments: Ignored lower-level request arguments.
        :raises ChannelsListToolError: Always raised to verify protocol mapping.
        """
        raise ChannelsListToolError(
            "quota",
            category="quota_exhausted",
            details={"api_key": "hidden", "stack_trace": "hidden"},
        )

    dispatcher = InMemoryToolDispatcher(tools=[build_channels_get_statistics_tool_descriptor(channels=channels)])
    response = route_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": "req-channel-statistics-error",
            "method": "tools/call",
            "params": {"name": "channels_getStatistics", "arguments": {"channelId": "UC123"}},
        },
        dispatcher,
    )

    assert response["error"]["data"]["category"] == "quota_exhaustion"
    assert "hidden" not in str(response["error"])


def test_tools_list_routes_the_default_channel_content_search_descriptor():
    """Expose the concrete channel-content search contract through MCP discovery.

    :return: ``None`` after validating public tool-list routing.
    """
    response = route_mcp_request(
        {"jsonrpc": "2.0", "id": "req-channel-content-list", "method": "tools/list", "params": {}},
        InMemoryToolDispatcher(),
    )
    listed = {tool["name"]: tool for tool in response["result"]["tools"]}

    assert listed["channels_searchContent"]["inputSchema"]["required"] == ["channelId", "query"]
    assert listed["channels_searchContent"]["metadata"]["compositionBoundary"]["kind"] == "direct_search_normalization"


def test_playlist_search_routes_sanitized_item_listing_failures():
    """Serialize playlist-search lower-layer failures as safe MCP errors.

    :return: ``None`` after validating the public category and hidden diagnostics.
    """
    from mcp_server.tools.youtube_common.playlist_items import (
        PlaylistItemsListToolError,
    )
    from mcp_server.tools.youtube_composed.playlists import (
        build_playlists_search_items_tool_descriptor,
    )

    def playlists(_arguments):
        """Return one available source playlist for search routing coverage.

        :param _arguments: Ignored lower-layer playlist-list arguments.
        :return: One available source playlist result.
        """
        return {"items": [{"id": "PL123"}]}

    def playlist_items(_arguments):
        """Raise a capacity failure containing forbidden lower-layer details.

        :param _arguments: Ignored lower-layer playlist-item listing arguments.
        :raises PlaylistItemsListToolError: Always raised for safe-routing coverage.
        """
        raise PlaylistItemsListToolError(
            "hidden",
            category="quota_exhausted",
            details={"api_key": "hidden", "raw_body": "hidden"},
        )

    dispatcher = InMemoryToolDispatcher(
        tools=[build_playlists_search_items_tool_descriptor(playlists=playlists, playlist_items=playlist_items)]
    )
    response = route_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": "req-playlist-search-error",
            "method": "tools/call",
            "params": {"name": "playlists_searchItems", "arguments": {"playlistId": "PL123", "query": "needle"}},
        },
        dispatcher,
    )

    assert response["error"]["data"]["category"] == "quota_exhaustion"
    assert response["error"]["data"]["protocolCategory"] == "transport_not_supported"
    assert "hidden" not in str(response["error"])


if __name__ == "__main__":
    unittest.main()
