import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import load_hosted_runtime_settings, validate_runtime_config


class HostedSecurityConfigTests(unittest.TestCase):
    def test_dev_defaults_do_not_require_auth(self):
        settings = load_hosted_runtime_settings({"MCP_ENVIRONMENT": "dev"})
        self.assertFalse(settings.security.auth_required)
        self.assertTrue(settings.security.allow_originless_clients)

    def test_auth_token_enables_auth_requirement_in_dev(self):
        settings = load_hosted_runtime_settings({"MCP_ENVIRONMENT": "dev", "MCP_AUTH_TOKEN": "dev-token"})
        self.assertTrue(settings.security.auth_required)
        self.assertEqual(settings.security.auth_token, "dev-token")

    def test_allowed_origins_and_originless_flag_are_parsed(self):
        settings = load_hosted_runtime_settings(
            {
                "MCP_ENVIRONMENT": "dev",
                "MCP_AUTH_TOKEN": "dev-token",
                "MCP_ALLOWED_ORIGINS": "http://localhost:3000, https://example.com/path",
                "MCP_ALLOW_ORIGINLESS_CLIENTS": "false",
            }
        )
        self.assertEqual(settings.security.allowed_origins, ("http://localhost:3000", "https://example.com"))
        self.assertFalse(settings.security.allow_originless_clients)

    def test_staging_requires_auth_secret(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "staging", "YOUTUBE_API_KEY": "yt-secret"})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "MCP_AUTH_TOKEN" for item in result.failures))

    def test_invalid_allowed_origins_value_is_rejected(self):
        result = validate_runtime_config(
            {
                "MCP_ENVIRONMENT": "dev",
                "MCP_ALLOWED_ORIGINS": "not-an-origin",
            }
        )
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "MCP_ALLOWED_ORIGINS" for item in result.failures))


if __name__ == "__main__":
    unittest.main()
