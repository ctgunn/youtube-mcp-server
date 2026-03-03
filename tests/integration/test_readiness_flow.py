import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class ReadinessFlowTests(unittest.TestCase):
    def test_readyz_reports_ready_for_valid_startup(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        payload = app.handle("/readyz", {})
        self.assertEqual(payload["status"], "ready")

    def test_readyz_reports_not_ready_for_invalid_state_when_startup_validation_skipped(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        payload = app.handle("/readyz", {})
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()
