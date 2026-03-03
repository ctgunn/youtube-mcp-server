import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.transport.http import MCPHTTPTransport


class MCPTransportContractTests(unittest.TestCase):
    def setUp(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        self.app = create_app()

    def test_initialize_contract_success(self):
        payload = {
            "id": "req-c1",
            "method": "initialize",
            "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
        }
        response = self.app.handle("/mcp", payload)
        self.assertTrue(response["success"])
        self.assertEqual(response["meta"]["requestId"], "req-c1")
        self.assertIn("serverName", response["data"])

    def test_initialize_contract_malformed(self):
        payload = {"id": "req-c2", "method": "initialize", "params": {}}
        response = self.app.handle("/mcp", payload)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_tools_list_contract(self):
        payload = {"id": "req-c3", "method": "tools/list", "params": {}}
        response = self.app.handle("/mcp", payload)
        self.assertTrue(response["success"])
        self.assertIsInstance(response["data"], list)

    def test_tools_call_success_and_unknown_error(self):
        success_payload = {
            "id": "req-c4",
            "method": "tools/call",
            "params": {"toolName": "server_ping", "arguments": {}},
        }
        success_response = self.app.handle("/mcp", success_payload)
        self.assertTrue(success_response["success"])
        self.assertEqual(success_response["data"]["toolName"], "server_ping")

        fail_payload = {
            "id": "req-c5",
            "method": "tools/call",
            "params": {"toolName": "missing", "arguments": {}},
        }
        fail_response = self.app.handle("/mcp", fail_payload)
        self.assertFalse(fail_response["success"])
        self.assertEqual(fail_response["error"]["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(fail_response["error"]["details"], {"toolName": "missing"})
        self.assertEqual(success_response["data"]["result"]["status"], "ok")
        self.assertIn("timestamp", success_response["data"]["result"])

    def test_server_info_contract(self):
        payload = {
            "id": "req-c-info",
            "method": "tools/call",
            "params": {"toolName": "server_info", "arguments": {}},
        }
        response = self.app.handle("/mcp", payload)
        self.assertTrue(response["success"])
        result = response["data"]["result"]
        self.assertIn("version", result)
        self.assertIn("environment", result)
        self.assertIn("build", result)
        self.assertIn("buildId", result["build"])
        self.assertIn("commit", result["build"])
        self.assertIn("buildTime", result["build"])

    def test_server_list_tools_contract(self):
        payload = {
            "id": "req-c-listtools",
            "method": "tools/call",
            "params": {"toolName": "server_list_tools", "arguments": {}},
        }
        response = self.app.handle("/mcp", payload)
        self.assertTrue(response["success"])
        entries = response["data"]["result"]
        names = [entry["name"] for entry in entries]
        self.assertIn("server_ping", names)
        self.assertIn("server_info", names)
        self.assertIn("server_list_tools", names)

    def test_tools_call_invalid_arguments_contract(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="strict",
            description="Strict",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"ok": True},
        )
        app = MCPHTTPTransport(dispatcher=dispatcher)

        payload = {
            "id": "req-c6",
            "method": "tools/call",
            "params": {"toolName": "strict", "arguments": {"unexpected": "x"}},
        }
        response = app.handle("/mcp", payload)
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("unsupported field", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
