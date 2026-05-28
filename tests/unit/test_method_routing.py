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
