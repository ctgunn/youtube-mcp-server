import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import build_asgi_app, execute_hosted_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.transport.http import MCPHTTPTransport


class MCPTransportContractTests(unittest.TestCase):
    def setUp(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        self.app = create_app()

    def _runtime_transport(self, env=None):
        hosted_app = build_asgi_app(env=env, validate_startup=False)
        return getattr(hosted_app, "transport", getattr(getattr(hosted_app, "state", None), "transport", None))

    def test_initialize_contract_success(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-c1",
            "method": "initialize",
            "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
        }
        response = self.app.handle("/mcp", payload)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], "req-c1")
        self.assertIn("protocolVersion", response["result"])
        self.assertIn("serverInfo", response["result"])

    def test_initialize_contract_malformed(self):
        payload = {"jsonrpc": "2.0", "id": "req-c2", "method": "initialize", "params": {}}
        response = self.app.handle("/mcp", payload)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_tools_list_contract(self):
        payload = {"jsonrpc": "2.0", "id": "req-c3", "method": "tools/list", "params": {}}
        response = self.app.handle("/mcp", payload)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIsInstance(response["result"]["tools"], list)
        self.assertIn("inputSchema", response["result"]["tools"][0])

    def test_tools_call_success_and_unknown_error(self):
        success_payload = {
            "jsonrpc": "2.0",
            "id": "req-c4",
            "method": "tools/call",
            "params": {"name": "server_ping", "arguments": {}},
        }
        success_response = self.app.handle("/mcp", success_payload)
        self.assertEqual(success_response["jsonrpc"], "2.0")
        content_item = success_response["result"]["content"][0]
        result_payload = json.loads(content_item["text"])
        self.assertEqual(result_payload["status"], "ok")
        self.assertEqual(content_item["structuredContent"]["status"], "ok")

        fail_payload = {
            "jsonrpc": "2.0",
            "id": "req-c5",
            "method": "tools/call",
            "params": {"name": "missing", "arguments": {}},
        }
        fail_response = self.app.handle("/mcp", fail_payload)
        self.assertEqual(fail_response["jsonrpc"], "2.0")
        self.assertEqual(fail_response["error"]["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(fail_response["error"]["data"], {"toolName": "missing"})
        self.assertIn("timestamp", result_payload)

    def test_server_info_contract(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-c-info",
            "method": "tools/call",
            "params": {"name": "server_info", "arguments": {}},
        }
        response = self.app.handle("/mcp", payload)
        content_item = response["result"]["content"][0]
        result = json.loads(content_item["text"])
        self.assertEqual(content_item["structuredContent"]["version"], result["version"])
        self.assertIn("version", result)
        self.assertIn("environment", result)
        self.assertIn("build", result)
        self.assertIn("buildId", result["build"])
        self.assertIn("commit", result["build"])
        self.assertIn("buildTime", result["build"])

    def test_server_list_tools_contract(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-c-listtools",
            "method": "tools/call",
            "params": {"name": "server_list_tools", "arguments": {}},
        }
        response = self.app.handle("/mcp", payload)
        content_item = response["result"]["content"][0]
        entries = json.loads(content_item["text"])
        self.assertEqual(content_item["structuredContent"], entries)
        names = [entry["name"] for entry in entries]
        self.assertIn("server_ping", names)
        self.assertIn("server_info", names)
        self.assertIn("server_list_tools", names)
        self.assertIn("inputSchema", entries[0])

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
            "jsonrpc": "2.0",
            "id": "req-c6",
            "method": "tools/call",
            "params": {"name": "strict", "arguments": {"unexpected": "x"}},
        }
        response = app.handle("/mcp", payload)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("unsupported field", response["error"]["message"])

    def test_generated_request_id_when_payload_id_missing(self):
        payload = {"jsonrpc": "2.0", "method": "tools/list", "params": {}}
        response = self.app.handle("/mcp", payload)
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertTrue(str(response["id"]).startswith("req-"))

    def test_hosted_mcp_status_codes_and_json_error_envelope(self):
        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-hosted-init","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        self.assertEqual(init.status, 200)

        success = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": init.headers["MCP-Session-Id"],
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-c1","method":"tools/list","params":{}}',
        )
        self.assertEqual(success.status, 200)
        self.assertEqual(success.headers["Content-Type"], "application/json")
        self.assertEqual(success.payload["jsonrpc"], "2.0")
        self.assertIn("result", success.payload)

        invalid = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": init.headers["MCP-Session-Id"],
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-c2","method":"","params":{}}',
        )
        self.assertEqual(invalid.status, 400)
        self.assertEqual(invalid.payload["jsonrpc"], "2.0")
        self.assertEqual(invalid.payload["error"]["code"], "INVALID_ARGUMENT")
        self.assertEqual(invalid.payload["error"].keys(), {"code", "message", "data"})

    def test_migrated_runtime_preserves_health_and_ready_routes(self):
        transport = self._runtime_transport(env={"MCP_ENVIRONMENT": "staging"})
        health = execute_hosted_request(transport, method="GET", path="/health")
        ready = execute_hosted_request(transport, method="GET", path="/ready")
        self.assertEqual(health.status, 200)
        self.assertEqual(health.payload["status"], "ok")
        self.assertEqual(ready.status, 503)
        self.assertEqual(ready.payload["status"], "not_ready")


if __name__ == "__main__":
    unittest.main()
