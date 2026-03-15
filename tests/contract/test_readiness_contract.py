import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request


class ReadinessContractTests(unittest.TestCase):
    def test_health_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/health", {})
        self.assertEqual(payload, {"status": "ok"})

    def test_ready_contract_shape_when_ready(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["checks"]["configuration"], "pass")
        self.assertEqual(payload["checks"]["secrets"], "pass")

    def test_ready_contract_shape_when_not_ready(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/ready", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["checks"]["configuration"], "fail")
        self.assertEqual(payload["checks"]["secrets"], "fail")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_hosted_ready_uses_non_success_status_when_not_ready(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        response = execute_hosted_request(app, method="GET", path="/ready")
        self.assertEqual(response.status, 503)
        self.assertEqual(response.payload["status"], "not_ready")

    def test_hosted_health_uses_success_status(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        response = execute_hosted_request(app, method="GET", path="/health")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.payload, {"status": "ok"})

    def test_startup_validation_error_details_shape(self):
        with self.assertRaisesRegex(RuntimeError, "MCP_ENVIRONMENT"):
            create_app(env={"MCP_ENVIRONMENT": "qa"})


if __name__ == "__main__":
    unittest.main()
