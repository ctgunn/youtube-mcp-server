import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class OperationalObservabilityContractTests(unittest.TestCase):
    def test_health_and_ready_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        self.assertEqual(app.handle("/health", {}), {"status": "ok"})

        ready = app.handle("/ready", {})
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(ready["checks"]["configuration"], "pass")

    def test_ready_not_ready_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["checks"]["configuration"], "fail")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_error_shape_for_invalid_path(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/missing", {})

        self.assertEqual(payload["jsonrpc"], "2.0")
        self.assertIn("code", payload["error"])
        self.assertIn("message", payload["error"])
        self.assertIn("data", payload["error"])

    def test_hosted_invalid_path_and_method_statuses(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        missing = execute_hosted_request(app, method="GET", path="/missing")
        self.assertEqual(missing.status, 404)
        self.assertEqual(missing.payload["error"]["code"], "RESOURCE_NOT_FOUND")

        wrong_method = execute_hosted_request(app, method="POST", path="/health")
        self.assertEqual(wrong_method.status, 405)
        self.assertEqual(wrong_method.payload["error"]["code"], "METHOD_NOT_ALLOWED")

    def test_error_shape_for_invalid_method(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/mcp", {"jsonrpc": "2.0", "method": "", "params": {}})

        self.assertEqual(payload["jsonrpc"], "2.0")
        self.assertEqual(payload["error"].keys(), {"code", "message", "data"})
        self.assertTrue(str(payload.get("id", "")).startswith("req-"))

    def test_hosted_runtime_log_event_contract(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        app = create_app(env={"MCP_ENVIRONMENT": "dev"}, runtime_stdout=stdout, runtime_stderr=stderr)
        execute_hosted_request(app, method="GET", path="/health")
        init = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-contract-init","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
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
            body=b'{"jsonrpc":"2.0","id":"req-contract-log","method":"tools/call","params":{"name":"server_ping","arguments":{}}}',
        )
        health_event = json.loads(stdout.getvalue().splitlines()[0])
        tool_event = json.loads(stdout.getvalue().splitlines()[-1])
        self.assertEqual(
            health_event.keys(),
            {"timestamp", "severity", "requestId", "path", "status", "latencyMs"},
        )
        self.assertEqual(tool_event["toolName"], "server_ping")
        self.assertEqual(tool_event["methodName"], "tools/call")
        self.assertEqual(tool_event["path"], "/mcp")


if __name__ == "__main__":
    unittest.main()
