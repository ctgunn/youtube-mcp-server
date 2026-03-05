import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


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
        app.handle("/healthz", {})
        app.handle("/readyz", {})

        logs = app.observability.logs
        health = [entry for entry in logs if entry["path"] == "/healthz"][-1]
        ready = [entry for entry in logs if entry["path"] == "/readyz"][-1]

        for item in (health, ready):
            self.assertIn("requestId", item)
            self.assertIn("latencyMs", item)
            self.assertIn("status", item)

    def test_ready_not_ready_reason_still_present_with_instrumentation(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/readyz", {})
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
        app.handle("/healthz", {})
        app.handle("/mcp", {"id": "req-m1", "method": "tools/list", "params": {}})
        app.handle("/mcp", {"id": "req-m2", "method": "tools/call", "params": {"toolName": "missing", "arguments": {}}})

        snapshot = app.observability.snapshot()
        self.assertGreaterEqual(snapshot["counts"]["/healthz"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["error"], 1)
        self.assertIn("p50", snapshot["latency"]["byEndpoint"]["/mcp"])
        self.assertIn("p95", snapshot["latency"]["byEndpoint"]["/mcp"])

    def test_mixed_traffic_regression(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        app.handle("/healthz", {})
        app.handle("/readyz", {})
        app.handle("/mcp", {"id": "req-r1", "method": "initialize", "params": {"clientInfo": {"name": "x"}}})
        app.handle("/mcp", {"id": "req-r2", "method": "tools/list", "params": {}})
        app.handle("/nope", {})

        snapshot = app.observability.snapshot()
        self.assertGreaterEqual(snapshot["counts"]["/healthz"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/readyz"]["success"], 1)
        self.assertGreaterEqual(snapshot["counts"]["/mcp"]["success"], 2)
        self.assertGreaterEqual(snapshot["counts"]["not_found"]["error"], 1)


if __name__ == "__main__":
    unittest.main()
