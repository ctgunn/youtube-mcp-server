import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class HostedMCPSecurityFlowsIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            env={
                "MCP_ENVIRONMENT": "dev",
                "MCP_AUTH_TOKEN": "integration-token",
                "MCP_ALLOWED_ORIGINS": "http://localhost:3000",
            }
        )

    def test_authorized_origin_can_initialize_and_call_tool(self):
        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer integration-token",
                "Origin": "http://localhost:3000",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-int-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(init.status, 200)
        session_id = init.headers["MCP-Session-Id"]

        call = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer integration-token",
                "MCP-Session-Id": session_id,
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-int-call",
                    "method": "tools/call",
                    "params": {"name": "server_ping", "arguments": {}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(call.status, 200)
        self.assertEqual(call.headers["Content-Type"], "text/event-stream")

    def test_denied_request_does_not_create_session(self):
        denied = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Origin": "https://evil.example",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-int-denied",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(denied.status, 403)
        self.assertNotIn("MCP-Session-Id", denied.headers)

    def test_originless_non_browser_client_can_authenticate(self):
        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer integration-token",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-originless-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(init.status, 200)

    def test_approved_browser_preflight_and_post_flow_share_documented_headers(self):
        preflight = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        self.assertEqual(preflight.status, 204)
        self.assertEqual(preflight.headers["Access-Control-Allow-Origin"], "http://localhost:3000")

        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer integration-token",
                "Origin": "http://localhost:3000",
            },
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-browser-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "browser-client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(init.status, 200)
        self.assertEqual(init.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("MCP-Session-Id", init.headers["Access-Control-Expose-Headers"])

    def test_browser_denial_and_unsupported_preflight_patterns_are_stable(self):
        denied = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        self.assertEqual(denied.status, 403)
        self.assertEqual(denied.payload["error"]["code"], -32003)
        self.assertEqual(denied.payload["error"]["data"]["category"], "origin_denied")

        unsupported_headers = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "x-custom-header",
            },
        )
        self.assertEqual(unsupported_headers.status, 400)
        self.assertEqual(unsupported_headers.payload["error"]["code"], -32602)
        self.assertEqual(unsupported_headers.payload["error"]["data"]["category"], "unsupported_browser_headers")

        unsupported_route = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/ready",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(unsupported_route.status, 405)
        self.assertEqual(unsupported_route.payload["error"]["code"], -32601)
        self.assertEqual(unsupported_route.payload["error"]["data"]["category"], "unsupported_browser_route")


if __name__ == "__main__":
    unittest.main()
