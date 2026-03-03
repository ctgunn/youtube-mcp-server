import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class ReadinessContractTests(unittest.TestCase):
    def test_healthz_contract_shape(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/healthz", {})
        self.assertEqual(payload, {"status": "ok"})

    def test_readyz_contract_shape_when_ready(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/readyz", {})
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["checks"]["configuration"], "pass")
        self.assertEqual(payload["checks"]["secrets"], "pass")

    def test_readyz_contract_shape_when_not_ready(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/readyz", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["checks"]["configuration"], "fail")
        self.assertEqual(payload["checks"]["secrets"], "fail")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_startup_validation_error_details_shape(self):
        with self.assertRaisesRegex(RuntimeError, "MCP_ENVIRONMENT"):
            create_app(env={"MCP_ENVIRONMENT": "qa"})


if __name__ == "__main__":
    unittest.main()
