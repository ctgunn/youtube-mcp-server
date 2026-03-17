import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import validate_runtime_config
from mcp_server.health import initialize_runtime_lifecycle, readiness_payload


class ReadinessStateTests(unittest.TestCase):
    def test_ready_payload_for_valid_config(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "dev"})
        payload = readiness_payload(result)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["checks"]["configuration"], "pass")

    def test_not_ready_payload_for_invalid_config(self):
        result = validate_runtime_config({})
        payload = readiness_payload(result)
        self.assertEqual(payload["status"], "not_ready")
        self.assertEqual(payload["reason"]["code"], "CONFIG_VALIDATION_ERROR")

    def test_lifecycle_transitions_from_ready_to_stopping(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "dev"})
        lifecycle = initialize_runtime_lifecycle(result)
        self.assertEqual(lifecycle.state, "ready")
        self.assertTrue(lifecycle.accepting_traffic)

        lifecycle.mark_stopping()
        self.assertEqual(lifecycle.state, "stopping")
        self.assertFalse(lifecycle.accepting_traffic)


if __name__ == "__main__":
    unittest.main()
