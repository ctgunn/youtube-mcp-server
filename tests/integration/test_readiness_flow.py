import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class ReadinessFlowTests(unittest.TestCase):
    def test_ready_reports_ready_for_valid_startup(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "ready")

    def test_ready_reports_not_ready_for_invalid_state_when_startup_validation_skipped(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_hosted_ready_status_matches_ready_and_not_ready_states(self):
        ready_app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        ready_response = execute_hosted_request(ready_app, method="GET", path="/ready")
        self.assertEqual(ready_response.status, 200)
        self.assertEqual(ready_response.payload["status"], "ready")

        not_ready_app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        not_ready_response = execute_hosted_request(not_ready_app, method="GET", path="/ready")
        self.assertEqual(not_ready_response.status, 503)
        self.assertEqual(not_ready_response.payload["status"], "not_ready")


if __name__ == "__main__":
    unittest.main()
