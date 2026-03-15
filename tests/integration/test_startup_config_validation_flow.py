import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class StartupConfigValidationFlowTests(unittest.TestCase):
    def test_startup_fails_fast_when_environment_missing(self):
        with self.assertRaisesRegex(RuntimeError, "Startup configuration validation failed"):
            create_app(env={})

    def test_startup_succeeds_for_valid_dev_profile(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        response = app.handle("/ready", {})
        self.assertEqual(response["status"], "ready")

    def test_startup_fails_for_staging_without_secret(self):
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY"):
            create_app(env={"MCP_ENVIRONMENT": "staging"})


if __name__ == "__main__":
    unittest.main()
