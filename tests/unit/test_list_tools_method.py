import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class ListToolsMethodTests(unittest.TestCase):
    def test_list_tools_with_default_registry(self):
        payload = {"id": "req-list", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertTrue(response["success"])
        self.assertIsInstance(response["data"], list)
        self.assertGreaterEqual(len(response["data"]), 1)
        self.assertIn("name", response["data"][0])

    def test_list_tools_with_empty_registry(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        payload = {"id": "req-list-empty", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], [])

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

        payload = {"id": "req-list-order", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertTrue(response["success"])
        self.assertEqual([item["name"] for item in response["data"]], ["alpha", "Zulu"])

    def test_server_list_tools_matches_tools_list_descriptors(self):
        dispatcher = InMemoryToolDispatcher()
        list_response = route_mcp_request(
            {"id": "req-list-1", "method": "tools/list", "params": {}},
            dispatcher,
        )
        call_response = route_mcp_request(
            {
                "id": "req-list-2",
                "method": "tools/call",
                "params": {"toolName": "server_list_tools", "arguments": {}},
            },
            dispatcher,
        )
        self.assertTrue(list_response["success"])
        self.assertTrue(call_response["success"])
        self.assertEqual(call_response["data"]["result"], list_response["data"])


if __name__ == "__main__":
    unittest.main()
