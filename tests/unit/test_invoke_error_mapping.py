import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class InvokeErrorMappingTests(unittest.TestCase):
    def test_unknown_tool_returns_resource_not_found(self):
        payload = {
            "id": "req-call-1",
            "method": "tools/call",
            "params": {"toolName": "unknown_tool", "arguments": {}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "RESOURCE_NOT_FOUND")

    def test_invalid_arguments_type_returns_invalid_argument(self):
        payload = {
            "id": "req-call-2",
            "method": "tools/call",
            "params": {"toolName": "server_ping", "arguments": "bad"},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")


if __name__ == "__main__":
    unittest.main()
