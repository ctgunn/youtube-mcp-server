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
    def _initialize_hosted_session(self, app):
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-hosted-init","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        self.assertEqual(response.status, 200)
        return response.headers["MCP-Session-Id"]

    def test_initialize_list_call_sequence(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()

        init_payload = {
            "jsonrpc": "2.0",
            "id": "req-i1",
            "method": "initialize",
            "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
        }
        init_resp = app.handle("/mcp", init_payload)
        self.assertEqual(init_resp["jsonrpc"], "2.0")

        list_payload = {"jsonrpc": "2.0", "id": "req-i2", "method": "tools/list", "params": {}}
        list_resp = app.handle("/mcp", list_payload)
        names = [tool["name"] for tool in list_resp["result"]["tools"]]
        self.assertIn("server_ping", names)
        self.assertIn("inputSchema", list_resp["result"]["tools"][0])

        call_payload = {
            "jsonrpc": "2.0",
            "id": "req-i3",
            "method": "tools/call",
            "params": {"name": "server_ping", "arguments": {}},
        }
        call_resp = app.handle("/mcp", call_payload)
        content_item = call_resp["result"]["content"][0]
        payload = json.loads(content_item["text"])
        self.assertEqual(content_item["structuredContent"]["status"], "ok")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("timestamp", payload)

    def test_rejected_initialize_and_successful_continuation_emit_distinct_session_decisions(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)

        failed = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-init-bad-obsv","method":"initialize","params":{}}',
        )
        self.assertEqual(failed.status, 400)

        session_id = self._initialize_hosted_session(app)
        continued = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-tools-after-init","method":"tools/list","params":{}}',
        )
        self.assertEqual(continued.status, 200)

        session_events = [event for event in app.observability.logs if event.get("event") == "session.decision"]
        outcomes = [event.get("sessionOutcome") for event in session_events]
        self.assertIn("initialize_rejected", outcomes)
        self.assertIn("continued", outcomes)

    def test_server_ping_repeated_invocations_are_stable(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()
        payload = {
            "jsonrpc": "2.0",
            "id": "req-r1",
            "method": "tools/call",
            "params": {"name": "server_ping", "arguments": {}},
        }
        first = app.handle("/mcp", payload)
        second = app.handle("/mcp", payload | {"id": "req-r2"})
        first_content = first["result"]["content"][0]
        second_content = second["result"]["content"][0]
        first_payload = json.loads(first_content["text"])
        second_payload = json.loads(second_content["text"])
        self.assertEqual(first_payload["status"], "ok")
        self.assertEqual(second_payload["status"], "ok")
        self.assertIsInstance(first_payload["timestamp"], str)
        self.assertIsInstance(second_payload["timestamp"], str)
        self.assertEqual(set(first_content.keys()), set(second_content.keys()))

    def test_search_tool_success_and_no_result_flows(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()

        success = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search-1",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "remote MCP research"}},
            },
        )
        success_content = success["result"]["content"][0]["structuredContent"]
        self.assertGreaterEqual(len(success_content["results"]), 1)
        self.assertEqual(set(success_content["results"][0].keys()), {"id", "title", "url"})

        empty = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search-2",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "no-match-sentinel"}},
            },
        )
        empty_content = empty["result"]["content"][0]["structuredContent"]
        self.assertEqual(empty_content["results"], [])

        invalid = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search-invalid-extra",
                "method": "tools/call",
                "params": {
                    "name": "search",
                    "arguments": {"query": "remote MCP research", "pageSize": 1, "unsupported": True},
                },
            },
        )
        self.assertEqual(invalid["error"]["code"], -32602)
        self.assertEqual(invalid["error"]["data"]["category"], "invalid_argument")

    def test_search_to_fetch_handoff_and_missing_fetch(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()

        search = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search-3",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "remote MCP research"}},
            },
        )
        result = search["result"]["content"][0]["structuredContent"]["results"][0]

        fetch = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-1",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": result["id"]}},
            },
        )
        fetch_content = fetch["result"]["content"][0]["structuredContent"]
        self.assertEqual(fetch_content["id"], result["id"])
        self.assertEqual(fetch_content["url"], result["url"])
        self.assertIn("text", fetch_content)

        missing = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-2",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": "missing-resource"}},
            },
        )
        self.assertEqual(missing["error"]["code"], -32001)
        self.assertEqual(missing["error"]["data"]["category"], "unavailable_source")

        legacy_shape = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-3",
                "method": "tools/call",
                "params": {
                    "name": "fetch",
                    "arguments": {"resourceId": "res_remote_mcp_001"},
                },
            },
        )
        self.assertEqual(legacy_shape["error"]["code"], -32602)
        self.assertEqual(legacy_shape["error"]["data"]["category"], "invalid_argument")

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
                "jsonrpc": "2.0",
                "id": "req-i-info-1",
                "method": "tools/call",
                "params": {"name": "server_info", "arguments": {}},
            },
        )
        configured_content = configured_resp["result"]["content"][0]
        configured_payload = json.loads(configured_content["text"])
        self.assertEqual(configured_payload["version"], "9.9.9")
        self.assertEqual(configured_payload["environment"], "staging")
        self.assertEqual(configured_payload["build"]["buildId"], "b-1")
        self.assertEqual(configured_content["structuredContent"], configured_payload)

        fallback = MCPHTTPTransport(server_metadata={"version": "1.0.0"})
        fallback_resp = fallback.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-i-info-2",
                "method": "tools/call",
                "params": {"name": "server_info", "arguments": {}},
            },
        )
        fallback_payload = json.loads(fallback_resp["result"]["content"][0]["text"])
        self.assertEqual(fallback_payload["version"], "1.0.0")
        self.assertEqual(fallback_payload["environment"], "dev")
        self.assertEqual(fallback_payload["build"]["buildId"], "local")

    def test_server_list_tools_reflects_dynamic_registry(self):
        dispatcher = InMemoryToolDispatcher()
        app = MCPHTTPTransport(dispatcher=dispatcher)

        baseline = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-i-list-1",
                "method": "tools/call",
                "params": {"name": "server_list_tools", "arguments": {}},
            },
        )
        baseline_content = baseline["result"]["content"][0]
        baseline_names = [entry["name"] for entry in baseline_content["structuredContent"]]
        self.assertIn("server_ping", baseline_names)
        self.assertIn("server_info", baseline_names)
        self.assertIn("server_list_tools", baseline_names)
        self.assertIn("inputSchema", baseline_content["structuredContent"][0])

        dispatcher.register_tool(
            name="extra_tool",
            description="extra",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"ok": True},
        )

        updated = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-i-list-2",
                "method": "tools/call",
                "params": {"name": "server_list_tools", "arguments": {}},
            },
        )
        updated_names = [entry["name"] for entry in updated["result"]["content"][0]["structuredContent"]]
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

        list_resp = app.handle("/mcp", {"jsonrpc": "2.0", "id": "req-i4", "method": "tools/list", "params": {}})
        self.assertEqual([tool["name"] for tool in list_resp["result"]["tools"]], ["echo"])
        self.assertEqual(
            list_resp["result"]["tools"][0]["inputSchema"],
            {"type": "object", "properties": {"value": {"type": "string"}}, "additionalProperties": False},
        )

        call_resp = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-i5",
                "method": "tools/call",
                "params": {"name": "echo", "arguments": {"value": "hello"}},
            },
        )
        content_item = call_resp["result"]["content"][0]
        self.assertEqual(content_item["structuredContent"]["value"], "hello")
        self.assertEqual(json.loads(content_item["text"])["value"], "hello")

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
                "jsonrpc": "2.0",
                "id": "req-i6",
                "method": "tools/call",
                "params": {"name": "missing", "arguments": {}},
            },
        )
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["data"], {"category": "unknown_tool", "toolName": "missing"})
        self.assertFalse(called["value"])

    def test_tool_call_logs_include_latency_and_status(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        app = create_app()
        response = app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-i-log-1",
                "method": "tools/call",
                "params": {"name": "server_ping", "arguments": {}},
            },
        )
        self.assertIn("result", response)

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
        session_id = self._initialize_hosted_session(app)
        success = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-i1","method":"tools/list","params":{}}',
        )
        self.assertEqual(success.status, 200)
        self.assertEqual(success.headers["Content-Type"], "application/json")
        self.assertEqual(success.payload["jsonrpc"], "2.0")
        self.assertIn("result", success.payload)

        invalid = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-i2","method":"","params":{}}',
        )
        self.assertEqual(invalid.status, 400)
        self.assertIn("error", invalid.payload)
        self.assertEqual(invalid.payload["error"]["code"], -32600)
        self.assertEqual(invalid.payload["error"]["data"]["category"], "malformed_request")

    def test_hosted_runtime_logs_capture_tool_name_for_hosted_mcp_call(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)
        session_id = self._initialize_hosted_session(app)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-hosted-log-1","method":"tools/call","params":{"name":"server_ping","arguments":{}}}',
        )
        self.assertEqual(response.status, 200)
        combined = stdout.getvalue() + stderr.getvalue()
        self.assertIn('"toolName": "server_ping"', combined)


if __name__ == "__main__":
    unittest.main()
