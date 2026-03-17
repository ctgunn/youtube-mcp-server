import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import build_asgi_app, execute_hosted_request


class HostedHTTPRoutesIntegrationTests(unittest.TestCase):
    def _runtime_transport(self):
        hosted_app = build_asgi_app(validate_startup=False)
        return getattr(hosted_app, "transport", getattr(getattr(hosted_app, "state", None), "transport", None))

    def _initialize_session(self, app):
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-init-routes",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        return response.headers["MCP-Session-Id"]

    def test_health_and_ready_use_expected_hosted_statuses(self):
        ready_app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        ready = execute_hosted_request(ready_app, method="GET", path="/ready")
        self.assertEqual(ready.status, 200)
        self.assertEqual(ready.headers["Content-Type"], "application/json")
        self.assertEqual(ready.payload["status"], "ready")

        not_ready_app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        not_ready = execute_hosted_request(not_ready_app, method="GET", path="/ready")
        self.assertEqual(not_ready.status, 503)
        self.assertEqual(not_ready.headers["Content-Type"], "application/json")
        self.assertEqual(not_ready.payload["status"], "not_ready")

        liveness = execute_hosted_request(ready_app, method="GET", path="/health")
        self.assertEqual(liveness.status, 200)
        self.assertEqual(liveness.payload, {"status": "ok"})

    def test_mcp_rejects_malformed_json_and_unsupported_media_type(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        malformed = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"id":"req-bad"',
        )
        self.assertEqual(malformed.status, 400)
        self.assertEqual(malformed.payload["error"]["code"], "INVALID_ARGUMENT")

        unsupported_media_type = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "text/plain", "Accept": "application/json, text/event-stream"},
            body=b"plain-text",
        )
        self.assertEqual(unsupported_media_type.status, 415)
        self.assertEqual(unsupported_media_type.payload["error"]["code"], "UNSUPPORTED_MEDIA_TYPE")

    def test_unsupported_method_and_unknown_path_use_distinct_statuses(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        wrong_method = execute_hosted_request(app, method="DELETE", path="/mcp")
        self.assertEqual(wrong_method.status, 405)
        self.assertEqual(wrong_method.payload["error"]["code"], "METHOD_NOT_ALLOWED")

        missing_path = execute_hosted_request(app, method="GET", path="/missing")
        self.assertEqual(missing_path.status, 404)
        self.assertEqual(missing_path.payload["error"]["code"], "RESOURCE_NOT_FOUND")

    def test_hosted_mcp_initialize_and_session_list_use_json_protocol_result(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        session_id = self._initialize_session(app)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps({"jsonrpc": "2.0", "id": "req-hosted-1", "method": "tools/list", "params": {}}).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.payload["jsonrpc"], "2.0")
        self.assertIsInstance(response.payload["result"]["tools"], list)
        self.assertIn("inputSchema", response.payload["result"]["tools"][0])

    def test_hosted_tool_call_returns_structured_content(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        session_id = self._initialize_session(app)
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-hosted-call",
                    "method": "tools/call",
                    "params": {"name": "server_ping", "arguments": {}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "text/event-stream")
        self.assertIn('"structuredContent"', response.body.decode("utf-8"))

    def test_migrated_runtime_transport_preserves_mcp_route_execution(self):
        transport = self._runtime_transport()
        response = execute_hosted_request(
            transport,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-asgi-routes-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertIn("MCP-Session-Id", response.headers)


if __name__ == "__main__":
    unittest.main()
