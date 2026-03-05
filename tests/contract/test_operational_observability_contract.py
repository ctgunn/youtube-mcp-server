import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class OperationalObservabilityContractTests(unittest.TestCase):
    def test_healthz_and_readyz_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        self.assertEqual(app.handle("/healthz", {}), {"status": "ok"})

        ready = app.handle("/readyz", {})
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(ready["checks"]["configuration"], "pass")

    def test_readyz_not_ready_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/readyz", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["checks"]["configuration"], "fail")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_error_shape_for_invalid_path(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/missing", {})

        self.assertFalse(payload["success"])
        self.assertIn("code", payload["error"])
        self.assertIn("message", payload["error"])
        self.assertIn("details", payload["error"])

    def test_error_shape_for_invalid_method(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/mcp", {"method": "", "params": {}})

        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"].keys(), {"code", "message", "details"})
        self.assertTrue(str(payload["meta"].get("requestId", "")).startswith("req-"))


if __name__ == "__main__":
    unittest.main()
