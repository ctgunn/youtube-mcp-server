import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class HostedMCPSecurityContractTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            env={
                "MCP_ENVIRONMENT": "dev",
                "MCP_AUTH_TOKEN": "contract-token",
                "MCP_ALLOWED_ORIGINS": "http://localhost:3000",
            }
        )
        self.initialize_body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "req-contract-init",
                "method": "initialize",
                "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
            }
        ).encode("utf-8")

    def test_initialize_requires_authentication(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=self.initialize_body,
        )
        self.assertEqual(response.status, 401)
        self.assertEqual(response.payload["error"]["code"], -32002)
        self.assertEqual(response.payload["error"]["data"]["category"], "unauthenticated")
        self.assertNotIn("MCP-Session-Id", response.headers)

    def test_initialize_with_invalid_credential_does_not_issue_session_header(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer wrong-token",
            },
            body=self.initialize_body,
        )
        self.assertEqual(response.status, 403)
        self.assertEqual(response.payload["error"]["data"]["category"], "invalid_credential")
        self.assertNotIn("MCP-Session-Id", response.headers)

    def test_disallowed_browser_origin_is_forbidden(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer contract-token",
                "Origin": "https://evil.example",
            },
            body=self.initialize_body,
        )
        self.assertEqual(response.status, 403)
        self.assertEqual(response.payload["error"]["code"], -32003)
        self.assertEqual(response.payload["error"]["data"]["category"], "origin_denied")

    def test_authorized_initialize_and_stream_access_succeed(self):
        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer contract-token",
                "Origin": "http://localhost:3000",
            },
            body=self.initialize_body,
        )
        self.assertEqual(init.status, 200)
        self.assertIn("MCP-Session-Id", init.headers)

        denied_stream = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers={"Accept": "text/event-stream", "MCP-Session-Id": init.headers["MCP-Session-Id"]},
        )
        self.assertEqual(denied_stream.status, 401)

        allowed_stream = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers={
                "Accept": "text/event-stream",
                "Authorization": "Bearer contract-token",
                "Origin": "http://localhost:3000",
                "MCP-Session-Id": init.headers["MCP-Session-Id"],
            },
        )
        self.assertEqual(allowed_stream.status, 200)
        self.assertEqual(allowed_stream.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("X-Stream-Id", allowed_stream.headers)

    def test_approved_browser_preflight_returns_allow_headers(self):
        response = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        self.assertEqual(response.status, 204)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])
        self.assertIn("authorization", response.headers["Access-Control-Allow-Headers"].lower())

    def test_approved_browser_initialize_exposes_session_headers(self):
        init = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer contract-token",
                "Origin": "http://localhost:3000",
            },
            body=self.initialize_body,
        )
        self.assertEqual(init.status, 200)
        self.assertEqual(init.headers["Access-Control-Allow-Origin"], "http://localhost:3000")
        self.assertIn("MCP-Session-Id", init.headers["Access-Control-Expose-Headers"])
        self.assertIn("MCP-Session-Id", init.headers)

    def test_disallowed_browser_preflight_is_forbidden(self):
        response = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            },
        )
        self.assertEqual(response.status, 403)
        self.assertEqual(response.payload["error"]["code"], -32003)
        self.assertEqual(response.payload["error"]["data"]["category"], "origin_denied")

    def test_unsupported_browser_preflight_patterns_are_explicit(self):
        wrong_method = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "DELETE",
            },
        )
        self.assertEqual(wrong_method.status, 405)
        self.assertEqual(wrong_method.payload["error"]["code"], -32601)
        self.assertEqual(wrong_method.payload["error"]["data"]["category"], "unsupported_browser_method")

        wrong_route = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(wrong_route.status, 405)
        self.assertEqual(wrong_route.payload["error"]["code"], -32601)
        self.assertEqual(wrong_route.payload["error"]["data"]["category"], "unsupported_browser_route")


if __name__ == "__main__":
    unittest.main()
