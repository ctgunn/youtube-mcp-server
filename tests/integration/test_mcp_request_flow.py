import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.transport.http import MCPHTTPTransport


class MCPRequestFlowIntegrationTests(unittest.TestCase):
    def test_initialize_list_call_sequence(self):
        app = create_app()

        init_payload = {
            "id": "req-i1",
            "method": "initialize",
            "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
        }
        init_resp = app.handle("/mcp", init_payload)
        self.assertTrue(init_resp["success"])

        list_payload = {"id": "req-i2", "method": "tools/list", "params": {}}
        list_resp = app.handle("/mcp", list_payload)
        self.assertTrue(list_resp["success"])
        names = [tool["name"] for tool in list_resp["data"]]
        self.assertIn("server_ping", names)

        call_payload = {
            "id": "req-i3",
            "method": "tools/call",
            "params": {"toolName": "server_ping", "arguments": {}},
        }
        call_resp = app.handle("/mcp", call_payload)
        self.assertTrue(call_resp["success"])
        self.assertEqual(call_resp["data"]["result"]["status"], "ok")

    def test_register_list_call_happy_path(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="echo",
            description="Echo",
            input_schema={"type": "object", "properties": {"value": {"type": "string"}}, "additionalProperties": False},
            handler=lambda arguments: {"value": arguments.get("value")},
        )
        app = MCPHTTPTransport(dispatcher=dispatcher)

        list_resp = app.handle("/mcp", {"id": "req-i4", "method": "tools/list", "params": {}})
        self.assertTrue(list_resp["success"])
        self.assertEqual([tool["name"] for tool in list_resp["data"]], ["echo"])

        call_resp = app.handle(
            "/mcp",
            {
                "id": "req-i5",
                "method": "tools/call",
                "params": {"toolName": "echo", "arguments": {"value": "hello"}},
            },
        )
        self.assertTrue(call_resp["success"])
        self.assertEqual(call_resp["data"]["result"]["value"], "hello")

    def test_unknown_tool_returns_error_without_execution(self):
        called = {"value": False}

        def _handler(_arguments):
            called["value"] = True
            return {"ok": True}

        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="known",
            description="Known",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=_handler,
        )
        app = MCPHTTPTransport(dispatcher=dispatcher)

        response = app.handle(
            "/mcp",
            {
                "id": "req-i6",
                "method": "tools/call",
                "params": {"toolName": "missing", "arguments": {}},
            },
        )
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(response["error"]["details"], {"toolName": "missing"})
        self.assertFalse(called["value"])


if __name__ == "__main__":
    unittest.main()
