import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.transport.http import MCPHTTPTransport


class MCPRequestFlowIntegrationTests(unittest.TestCase):
    def test_initialize_list_call_sequence(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
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
        self.assertIn("timestamp", call_resp["data"]["result"])

    def test_server_ping_repeated_invocations_are_stable(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()
        payload = {
            "id": "req-r1",
            "method": "tools/call",
            "params": {"toolName": "server_ping", "arguments": {}},
        }
        first = app.handle("/mcp", payload)
        second = app.handle("/mcp", payload | {"id": "req-r2"})
        self.assertTrue(first["success"])
        self.assertTrue(second["success"])
        self.assertEqual(first["data"]["result"]["status"], "ok")
        self.assertEqual(second["data"]["result"]["status"], "ok")
        self.assertIsInstance(first["data"]["result"]["timestamp"], str)
        self.assertIsInstance(second["data"]["result"]["timestamp"], str)

    def test_server_info_configured_and_fallback(self):
        configured = MCPHTTPTransport(
            server_metadata={
                "version": "9.9.9",
                "environment": "staging",
                "build": {"buildId": "b-1", "commit": "abc", "buildTime": "2026-03-02T00:00:00Z"},
            }
        )
        configured_resp = configured.handle(
            "/mcp",
            {
                "id": "req-i-info-1",
                "method": "tools/call",
                "params": {"toolName": "server_info", "arguments": {}},
            },
        )
        self.assertTrue(configured_resp["success"])
        self.assertEqual(configured_resp["data"]["result"]["version"], "9.9.9")
        self.assertEqual(configured_resp["data"]["result"]["environment"], "staging")
        self.assertEqual(configured_resp["data"]["result"]["build"]["buildId"], "b-1")

        fallback = MCPHTTPTransport(server_metadata={"version": "1.0.0"})
        fallback_resp = fallback.handle(
            "/mcp",
            {
                "id": "req-i-info-2",
                "method": "tools/call",
                "params": {"toolName": "server_info", "arguments": {}},
            },
        )
        self.assertTrue(fallback_resp["success"])
        self.assertEqual(fallback_resp["data"]["result"]["version"], "1.0.0")
        self.assertEqual(fallback_resp["data"]["result"]["environment"], "dev")
        self.assertEqual(fallback_resp["data"]["result"]["build"]["buildId"], "local")

    def test_server_list_tools_reflects_dynamic_registry(self):
        dispatcher = InMemoryToolDispatcher()
        app = MCPHTTPTransport(dispatcher=dispatcher)

        baseline = app.handle(
            "/mcp",
            {
                "id": "req-i-list-1",
                "method": "tools/call",
                "params": {"toolName": "server_list_tools", "arguments": {}},
            },
        )
        self.assertTrue(baseline["success"])
        baseline_names = [entry["name"] for entry in baseline["data"]["result"]]
        self.assertIn("server_ping", baseline_names)
        self.assertIn("server_info", baseline_names)
        self.assertIn("server_list_tools", baseline_names)

        dispatcher.register_tool(
            name="extra_tool",
            description="extra",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"ok": True},
        )

        updated = app.handle(
            "/mcp",
            {
                "id": "req-i-list-2",
                "method": "tools/call",
                "params": {"toolName": "server_list_tools", "arguments": {}},
            },
        )
        self.assertTrue(updated["success"])
        updated_names = [entry["name"] for entry in updated["data"]["result"]]
        self.assertIn("extra_tool", updated_names)

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

    def test_tool_call_logs_include_latency_and_status(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()
        response = app.handle(
            "/mcp",
            {
                "id": "req-i-log-1",
                "method": "tools/call",
                "params": {"toolName": "server_ping", "arguments": {}},
            },
        )
        self.assertTrue(response["success"])

        logs = app.observability.logs
        event = logs[-1]
        self.assertEqual(event["requestId"], "req-i-log-1")
        self.assertEqual(event["path"], "/mcp")
        self.assertEqual(event["toolName"], "server_ping")
        self.assertEqual(event["status"], "success")
        self.assertGreaterEqual(event["latencyMs"], 0.0)

    def test_hosted_mcp_success_and_invalid_request_behaviors(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()
        success = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json"},
            body=b'{"id":"req-hosted-i1","method":"tools/list","params":{}}',
        )
        self.assertEqual(success.status, 200)
        self.assertEqual(success.headers["Content-Type"], "application/json")
        self.assertTrue(success.payload["success"])

        invalid = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json"},
            body=b'{"id":"req-hosted-i2","method":"","params":{}}',
        )
        self.assertEqual(invalid.status, 400)
        self.assertFalse(invalid.payload["success"])
        self.assertEqual(invalid.payload["error"]["code"], "INVALID_ARGUMENT")

    def test_hosted_runtime_logs_capture_tool_name_for_hosted_mcp_call(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json"},
            body=b'{"id":"req-hosted-log-1","method":"tools/call","params":{"toolName":"server_ping","arguments":{}}}',
        )

        self.assertEqual(response.status, 200)
        event = json.loads(stdout.getvalue().splitlines()[-1])
        self.assertEqual(event["requestId"], "req-hosted-log-1")
        self.assertEqual(event["toolName"], "server_ping")
        self.assertEqual(event["path"], "/mcp")


if __name__ == "__main__":
    unittest.main()
