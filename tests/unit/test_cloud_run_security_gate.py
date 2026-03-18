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
        self.assertEqual(response.payload["error"]["code"], "UNAUTHENTICATED")

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
        self.assertEqual(response.payload["error"]["code"], "ORIGIN_DENIED")

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
        self.assertEqual(response.payload["error"]["code"], "MALFORMED_SECURITY_INPUT")


if __name__ == "__main__":
    unittest.main()
