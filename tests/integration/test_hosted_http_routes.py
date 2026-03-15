import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class HostedHTTPRoutesIntegrationTests(unittest.TestCase):
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
            headers={"Content-Type": "application/json"},
            body=b'{"id":"req-bad"',
        )
        self.assertEqual(malformed.status, 400)
        self.assertEqual(malformed.payload["error"]["code"], "INVALID_ARGUMENT")

        unsupported_media_type = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "text/plain"},
            body=b"plain-text",
        )
        self.assertEqual(unsupported_media_type.status, 415)
        self.assertEqual(unsupported_media_type.payload["error"]["code"], "UNSUPPORTED_MEDIA_TYPE")

    def test_unsupported_method_and_unknown_path_use_distinct_statuses(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})

        wrong_method = execute_hosted_request(app, method="GET", path="/mcp")
        self.assertEqual(wrong_method.status, 405)
        self.assertEqual(wrong_method.payload["error"]["code"], "METHOD_NOT_ALLOWED")

        missing_path = execute_hosted_request(app, method="GET", path="/missing")
        self.assertEqual(missing_path.status, 404)
        self.assertEqual(missing_path.payload["error"]["code"], "RESOURCE_NOT_FOUND")

    def test_hosted_mcp_success_uses_json_envelope(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        response = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"id": "req-hosted-1", "method": "tools/list", "params": {}}).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertTrue(response.payload["success"])
        self.assertIsInstance(response.payload["data"], list)


if __name__ == "__main__":
    unittest.main()
