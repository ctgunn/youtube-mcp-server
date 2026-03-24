import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class CloudRunSecurityGateTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            env={
                "MCP_ENVIRONMENT": "dev",
                "MCP_AUTH_TOKEN": "local-dev-token",
                "MCP_ALLOWED_ORIGINS": "http://localhost:3000",
                "PUBLIC_INVOCATION_INTENT": "public_remote_mcp",
            }
        )
        self.payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": "req-secure-init",
                "method": "initialize",
                "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
            }
        ).encode("utf-8")

    def test_missing_auth_is_rejected(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=self.payload,
        )
        self.assertEqual(response.status, 401)
        self.assertEqual(response.payload["error"]["code"], -32002)
        self.assertEqual(response.payload["error"]["data"]["category"], "unauthenticated")

    def test_public_invocation_intent_does_not_bypass_mcp_authentication(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=self.payload,
        )
        self.assertEqual(response.status, 401)
        self.assertEqual(response.payload["error"]["data"]["category"], "unauthenticated")

    def test_disallowed_origin_is_rejected(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer local-dev-token",
                "Origin": "https://evil.example",
            },
            body=self.payload,
        )
        self.assertEqual(response.status, 403)
        self.assertEqual(response.payload["error"]["code"], -32003)
        self.assertEqual(response.payload["error"]["data"]["category"], "origin_denied")

    def test_malformed_auth_is_rejected(self):
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Token local-dev-token",
            },
            body=self.payload,
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(response.payload["error"]["code"], -32600)
        self.assertEqual(response.payload["error"]["data"]["category"], "malformed_security_input")

    def test_malformed_origin_and_unsupported_browser_method_are_rejected(self):
        malformed_origin = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "bad-origin",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(malformed_origin.status, 400)
        self.assertEqual(malformed_origin.payload["error"]["code"], -32600)
        self.assertEqual(malformed_origin.payload["error"]["data"]["category"], "malformed_origin")

        unsupported_method = execute_hosted_request(
            self.app,
            method="OPTIONS",
            path="/mcp",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "DELETE",
            },
        )
        self.assertEqual(unsupported_method.status, 405)
        self.assertEqual(unsupported_method.payload["error"]["code"], -32601)
        self.assertEqual(unsupported_method.payload["error"]["data"]["category"], "unsupported_browser_method")


if __name__ == "__main__":
    unittest.main()
