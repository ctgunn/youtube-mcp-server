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
        dispatcher = InMemoryToolDispatcher(tools={})
        payload = {"id": "req-list-empty", "method": "tools/list", "params": {}}
        response = route_mcp_request(payload, dispatcher)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"], [])


if __name__ == "__main__":
    unittest.main()
