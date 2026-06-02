import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class ListToolsMethodTests(unittest.TestCase):
    """Unit coverage for MCP tools/list behavior."""

    def test_list_tools_with_default_registry(self):
        """List default registry tools with public descriptor fields."""
        payload = {"jsonrpc": "2.0", "id": "req-list", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIsInstance(response["result"]["tools"], list)
        self.assertGreaterEqual(len(response["result"]["tools"]), 1)
        self.assertIn("name", response["result"]["tools"][0])
        self.assertIn("description", response["result"]["tools"][0])
        self.assertIn("inputSchema", response["result"]["tools"][0])

    def test_activities_list_discovery_preserves_safe_metadata(self):
        """Expose safe activities_list metadata through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-list-activities", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}

        activities = tools["activities_list"]

        self.assertEqual(activities["metadata"]["upstream"]["operationKey"], "activities.list")
        self.assertEqual(activities["metadata"]["quotaCost"], 1)
        self.assertEqual(activities["metadata"]["authMode"], "mixed/conditional")
        self.assertIn("usageNotes", activities["metadata"])

    def test_captions_list_discovery_preserves_safe_metadata(self):
        """Expose safe captions_list metadata through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-list-captions", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}

        captions = tools["captions_list"]

        self.assertEqual(captions["metadata"]["upstream"]["operationKey"], "captions.list")
        self.assertEqual(captions["metadata"]["quotaCost"], 50)
        self.assertEqual(captions["metadata"]["authMode"], "oauth_required")
        self.assertIn("usageNotes", captions["metadata"])

    def test_captions_insert_discovery_preserves_safe_metadata(self):
        """Expose safe captions_insert metadata through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-list-captions-insert", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}

        captions = tools["captions_insert"]

        self.assertEqual(captions["metadata"]["upstream"]["operationKey"], "captions.insert")
        self.assertEqual(captions["metadata"]["quotaCost"], 400)
        self.assertEqual(captions["metadata"]["authMode"], "oauth_required")
        self.assertEqual(captions["inputSchema"]["required"], ["part", "body", "media"])
        self.assertIn("media", captions["metadata"]["inputContract"]["properties"])
        self.assertIn("usageNotes", captions["metadata"])
        self.assertTrue(any("media" in note for note in captions["metadata"]["usageNotes"]))

    def test_captions_update_discovery_preserves_safe_metadata(self):
        """Expose safe captions_update metadata through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-list-captions-update", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}

        captions = tools["captions_update"]

        self.assertEqual(captions["metadata"]["upstream"]["operationKey"], "captions.update")
        self.assertEqual(captions["metadata"]["quotaCost"], 450)
        self.assertEqual(captions["metadata"]["authMode"], "oauth_required")
        self.assertEqual(captions["inputSchema"]["required"], ["part", "body"])
        self.assertIn("body", captions["metadata"]["inputContract"]["properties"])
        self.assertIn("media", captions["metadata"]["inputContract"]["properties"])
        self.assertIn("usageNotes", captions["metadata"])
        self.assertTrue(any("body" in note for note in captions["metadata"]["usageNotes"]))

    def test_captions_download_discovery_preserves_safe_metadata(self):
        """Expose safe captions_download metadata through tools/list."""
        payload = {"jsonrpc": "2.0", "id": "req-list-captions-download", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}

        captions = tools["captions_download"]

        self.assertEqual(captions["metadata"]["upstream"]["operationKey"], "captions.download")
        self.assertEqual(captions["metadata"]["quotaCost"], 200)
        self.assertEqual(captions["metadata"]["authMode"], "oauth_required")
        self.assertEqual(captions["inputSchema"]["required"], ["id"])
        self.assertIn("tfmt", captions["metadata"]["inputContract"]["properties"])
        self.assertIn("tlang", captions["metadata"]["inputContract"]["properties"])
        self.assertIn("usageNotes", captions["metadata"])
        self.assertTrue(any("tfmt" in note for note in captions["metadata"]["usageNotes"]))
        self.assertTrue(any("tlang" in note for note in captions["metadata"]["usageNotes"]))

    def test_list_tools_with_empty_registry(self):
        """Return an empty tools list for an empty dispatcher."""
        dispatcher = InMemoryToolDispatcher(tools=[])
        payload = {"jsonrpc": "2.0", "id": "req-list-empty", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertEqual(response["result"]["tools"], [])

    def test_list_tools_is_deterministic(self):
        """Return tools in stable normalized-name order."""
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="Zulu",
            description="z",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"name": "z"},
        )
        dispatcher.register_tool(
            name="alpha",
            description="a",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"name": "a"},
        )

        payload = {"jsonrpc": "2.0", "id": "req-list-order", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertEqual([item["name"] for item in response["result"]["tools"]], ["alpha", "Zulu"])
        self.assertEqual(
            response["result"]["tools"][0]["inputSchema"],
            {"type": "object", "properties": {}, "additionalProperties": False},
        )

    def test_server_list_tools_matches_tools_list_descriptors(self):
        """Return the same descriptors from server_list_tools and tools/list."""
        dispatcher = InMemoryToolDispatcher()
        list_response = route_mcp_request(
            {"jsonrpc": "2.0", "id": "req-list-1", "method": "tools/list", "params": {}},
            dispatcher,
        )
        call_response = route_mcp_request(
            {
                "jsonrpc": "2.0",
                "id": "req-list-2",
                "method": "tools/call",
                "params": {"name": "server_list_tools", "arguments": {}},
            },
            dispatcher,
        )
        self.assertEqual(
            call_response["result"]["content"][0]["structuredContent"],
            list_response["result"]["tools"],
        )
        self.assertEqual(
            json.loads(call_response["result"]["content"][0]["text"]),
            list_response["result"]["tools"],
        )


if __name__ == "__main__":
    unittest.main()
