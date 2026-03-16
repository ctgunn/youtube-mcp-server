import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class InitializeMethodTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = InMemoryToolDispatcher()

    def test_initialize_success(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-init",
            "method": "initialize",
            "params": {"clientInfo": {"name": "test", "version": "1.0.0"}},
        }
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-init")
        self.assertIn("protocolVersion", response["result"])
        self.assertIn("serverInfo", response["result"])
        self.assertIn("capabilities", response["result"])

    def test_initialize_missing_client_info_returns_invalid_argument(self):
        payload = {"jsonrpc": "2.0", "id": "req-init-2", "method": "initialize", "params": {}}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-init-2")
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")


if __name__ == "__main__":
    unittest.main()
