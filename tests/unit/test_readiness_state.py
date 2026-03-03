import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import validate_runtime_config
from mcp_server.health import readiness_payload


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


if __name__ == "__main__":
    unittest.main()
