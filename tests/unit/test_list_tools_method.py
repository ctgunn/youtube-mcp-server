import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class ListToolsMethodTests(unittest.TestCase):
    def test_list_tools_with_default_registry(self):
        payload = {"jsonrpc": "2.0", "id": "req-list", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIsInstance(response["result"]["tools"], list)
        self.assertGreaterEqual(len(response["result"]["tools"]), 1)
        self.assertIn("name", response["result"]["tools"][0])

    def test_list_tools_with_empty_registry(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        payload = {"jsonrpc": "2.0", "id": "req-list-empty", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertEqual(response["result"]["tools"], [])

    def test_list_tools_is_deterministic(self):
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

    def test_server_list_tools_matches_tools_list_descriptors(self):
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
        self.assertEqual(json.loads(call_response["result"]["content"][0]["text"]), list_response["result"]["tools"])


if __name__ == "__main__":
    unittest.main()
