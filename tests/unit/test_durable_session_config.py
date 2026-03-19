import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import load_hosted_runtime_settings, validate_runtime_config


class DurableSessionConfigTests(unittest.TestCase):
    def test_runtime_settings_include_session_configuration(self):
        settings = load_hosted_runtime_settings(
            {
                "MCP_ENVIRONMENT": "dev",
                "MCP_SESSION_BACKEND": "redis",
                "MCP_SESSION_STORE_URL": "redis://localhost:6379/0",
                "MCP_SESSION_DURABILITY_REQUIRED": "true",
                "MCP_SESSION_TTL_SECONDS": "900",
                "MCP_SESSION_REPLAY_TTL_SECONDS": "60",
            }
        )
        self.assertEqual(settings.session.backend, "redis")
        self.assertEqual(settings.session.store_url, "redis://localhost:6379/0")
        self.assertTrue(settings.session.durability_required)
        self.assertEqual(settings.session.session_ttl_seconds, 900)
        self.assertEqual(settings.session.replay_ttl_seconds, 60)

    def test_invalid_session_backend_fails_validation(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "dev", "MCP_SESSION_BACKEND": "bogus"})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "MCP_SESSION_BACKEND" for item in result.failures))

    def test_non_positive_ttls_fail_validation(self):
        result = validate_runtime_config(
            {
                "MCP_ENVIRONMENT": "dev",
                "MCP_SESSION_TTL_SECONDS": "0",
                "MCP_SESSION_REPLAY_TTL_SECONDS": "-1",
            }
        )
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "MCP_SESSION_TTL_SECONDS" for item in result.failures))
        self.assertTrue(any(item.key == "MCP_SESSION_REPLAY_TTL_SECONDS" for item in result.failures))


if __name__ == "__main__":
    unittest.main()
