import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class MethodRoutingTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = InMemoryToolDispatcher()

    def test_unsupported_method_returns_structured_error(self):
        payload = {"id": "req-1", "method": "unknown/method", "params": {}}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "METHOD_NOT_SUPPORTED")
        self.assertEqual(response["meta"]["requestId"], "req-1")

    def test_non_object_params_returns_invalid_argument(self):
        payload = {"id": "req-2", "method": "initialize", "params": "bad"}
        response = route_mcp_request(payload, self.dispatcher)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_registered_tool_dispatch_success(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="echo",
            description="Echo",
            input_schema={"type": "object", "properties": {"value": {"type": "string"}}, "additionalProperties": False},
            handler=lambda arguments: {"value": arguments.get("value", "")},
        )
        payload = {
            "id": "req-3",
            "method": "tools/call",
            "params": {"toolName": "echo", "arguments": {"value": "ok"}},
        }
        response = route_mcp_request(payload, dispatcher)
        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["toolName"], "echo")
        self.assertEqual(response["data"]["result"]["value"], "ok")


if __name__ == "__main__":
    unittest.main()
