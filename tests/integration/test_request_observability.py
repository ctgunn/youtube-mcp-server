import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class RequestObservabilityIntegrationTests(unittest.TestCase):
    def test_invalid_path_is_instrumented(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        response = app.handle("/unknown", {})

        self.assertFalse(response["success"])
        logs = app.observability.logs
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[-1]["path"], "/unknown")
        self.assertEqual(logs[-1]["status"], "error")
        self.assertIn("requestId", logs[-1])

    def test_health_and_ready_log_fields_present(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        app.handle("/health", {})
        app.handle("/ready", {})

        logs = app.observability.logs
        health = [entry for entry in logs if entry["path"] == "/health"][-1]
        ready = [entry for entry in logs if entry["path"] == "/ready"][-1]

        for item in (health, ready):
            self.assertIn("requestId", item)
            self.assertIn("latencyMs", item)
            self.assertIn("status", item)

    def test_ready_not_ready_reason_still_present_with_instrumentation(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_mcp_request_id_generation_when_missing(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle(
            "/mcp",
            {
                "method": "tools/list",
                "params": {},
            },
        )
        self.assertTrue(payload["success"])
        self.assertTrue(payload["meta"]["requestId"].startswith("req-"))

        logs = app.observability.logs
        self.assertEqual(logs[-1]["requestId"], payload["meta"]["requestId"])

    def test_tool_logs_include_tool_name(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        app.handle(
            "/mcp",
            {
                "id": "req-tool-1",
                "method": "tools/call",
                "params": {"toolName": "server_ping", "arguments": {}},
            },
        )

        logs = app.observability.logs
        tool_log = [entry for entry in logs if entry["path"] == "/mcp"][-1]
        self.assertEqual(tool_log["requestId"], "req-tool-1")
        self.assertEqual(tool_log["toolName"], "server_ping")
        self.assertEqual(tool_log["status"], "success")

    def test_metrics_count_and_latency_outputs(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        app.handle("/health", {})
        app.handle("/mcp", {"id": "req-m1", "method": "tools/list", "params": {}})
        app.handle("/mcp", {"id": "req-m2", "method": "tools/call", "params": {"toolName": "missing", "arguments": {}}})

        snapshot = app.observability.snapshot()
        self.assertGreaterEqual(snapshot["counts"]["/health"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["error"], 1)
        self.assertIn("p50", snapshot["latency"]["byEndpoint"]["/mcp"])
        self.assertIn("p95", snapshot["latency"]["byEndpoint"]["/mcp"])

    def test_mixed_traffic_regression(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        app.handle("/health", {})
        app.handle("/ready", {})
        app.handle("/mcp", {"id": "req-r1", "method": "initialize", "params": {"clientInfo": {"name": "x"}}})
        app.handle("/mcp", {"id": "req-r2", "method": "tools/list", "params": {}})
        app.handle("/nope", {})

        snapshot = app.observability.snapshot()
        self.assertGreaterEqual(snapshot["counts"]["/health"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/ready"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["success"], 2)
        self.assertGreaterEqual(snapshot["counts"]["not_found"]["error"], 1)

    def test_structured_runtime_logs_emit_to_stdout_and_stderr(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)

        app.handle("/health", {})
        app.handle("/unknown", {})

        stdout_event = json.loads(stdout.getvalue().splitlines()[0])
        stderr_event = json.loads(stderr.getvalue().splitlines()[0])
        self.assertEqual(stdout_event["path"], "/health")
        self.assertEqual(stdout_event["status"], "success")
        self.assertEqual(stderr_event["path"], "/unknown")
        self.assertEqual(stderr_event["status"], "error")

    def test_runtime_tool_logs_include_tool_name_only_for_tool_calls(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)

        app.handle("/ready", {})
        app.handle(
            "/mcp",
            {
                "id": "req-runtime-tool-1",
                "method": "tools/call",
                "params": {"toolName": "server_ping", "arguments": {}},
            },
        )

        ready_event = json.loads(stdout.getvalue().splitlines()[0])
        tool_event = json.loads(stdout.getvalue().splitlines()[-1])
        self.assertNotIn("toolName", ready_event)
        self.assertEqual(tool_event["toolName"], "server_ping")

    def test_hosted_streamable_requests_log_method_name(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)

        init = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"id":"req-stream-log-init","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": init.headers["MCP-Session-Id"],
            },
            body=b'{"id":"req-stream-log-call","method":"tools/call","params":{"toolName":"server_ping","arguments":{}}}',
        )

        events = [json.loads(line) for line in stdout.getvalue().splitlines()]
        init_event = [event for event in events if event["requestId"] == "req-stream-log-init"][-1]
        call_event = [event for event in events if event["requestId"] == "req-stream-log-call"][-1]
        self.assertEqual(init_event["methodName"], "initialize")
        self.assertEqual(call_event["methodName"], "tools/call")
        self.assertEqual(call_event["toolName"], "server_ping")


if __name__ == "__main__":
    unittest.main()
