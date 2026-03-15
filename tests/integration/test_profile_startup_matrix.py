import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app


class ProfileStartupMatrixTests(unittest.TestCase):
    def test_dev_profile_starts_without_secret(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        self.assertEqual(app.handle("/ready", {})["status"], "ready")

    def test_staging_profile_requires_secret(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging", "YOUTUBE_API_KEY": "abc"})
        self.assertEqual(app.handle("/ready", {})["status"], "ready")

    def test_prod_profile_requires_secret(self):
        app = create_app(env={"MCP_ENVIRONMENT": "prod", "YOUTUBE_API_KEY": "abc"})
        self.assertEqual(app.handle("/ready", {})["status"], "ready")

    def test_unsupported_profile_fails(self):
        with self.assertRaisesRegex(RuntimeError, "MCP_ENVIRONMENT"):
            create_app(env={"MCP_ENVIRONMENT": "qa"})


if __name__ == "__main__":
    unittest.main()
