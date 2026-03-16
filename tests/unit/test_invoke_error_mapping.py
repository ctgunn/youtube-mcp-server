import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class InvokeErrorMappingTests(unittest.TestCase):
    def test_unknown_tool_returns_resource_not_found(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-call-1",
            "method": "tools/call",
            "params": {"name": "unknown_tool", "arguments": {}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(response["error"]["data"], {"toolName": "unknown_tool"})

    def test_invalid_arguments_type_returns_invalid_argument(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-call-2",
            "method": "tools/call",
            "params": {"name": "server_ping", "arguments": "bad"},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_invalid_arguments_against_contract_returns_invalid_argument(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="strict",
            description="Strict tool",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"ok": True},
        )
        payload = {
            "jsonrpc": "2.0",
            "id": "req-call-3",
            "method": "tools/call",
            "params": {"name": "strict", "arguments": {"extra": "x"}},
        }
        response = route_mcp_request(payload, dispatcher)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("unsupported field", response["error"]["message"])

    def test_successful_tool_call_returns_protocol_native_content(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-call-4",
            "method": "tools/call",
            "params": {"name": "server_ping", "arguments": {}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["jsonrpc"], "2.0")
        payload = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()
