import os
import sys
import unittest
import json

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import initialize_succeeded, route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


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


if __name__ == "__main__":
    unittest.main()
