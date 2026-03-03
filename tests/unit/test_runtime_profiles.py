import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import PROFILE_REQUIREMENTS, SUPPORTED_PROFILES, validate_runtime_config


class RuntimeProfileTests(unittest.TestCase):
    def test_supported_profiles_are_stable(self):
        self.assertEqual(SUPPORTED_PROFILES, {"dev", "staging", "prod"})

    def test_each_profile_has_deterministic_requirements(self):
        for profile in SUPPORTED_PROFILES:
            requirements = PROFILE_REQUIREMENTS[profile]
            self.assertIn("required_config", requirements)
            self.assertIn("required_secrets", requirements)

    def test_unsupported_profile_is_rejected(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "qa"})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.reason == "unsupported value" for item in result.failures))

    def test_prod_requires_secret(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "prod"})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "YOUTUBE_API_KEY" for item in result.failures))


if __name__ == "__main__":
    unittest.main()
