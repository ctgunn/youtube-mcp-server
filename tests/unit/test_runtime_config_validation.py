import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import config_validation_error_details, ensure_runtime_config, validate_runtime_config


class RuntimeConfigValidationTests(unittest.TestCase):
    def test_missing_environment_is_invalid(self):
        result = validate_runtime_config({})
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason_code, "CONFIG_VALIDATION_ERROR")
        self.assertTrue(any(item.key == "MCP_ENVIRONMENT" for item in result.failures))

    def test_blank_environment_is_invalid(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "   "})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "MCP_ENVIRONMENT" for item in result.failures))

    def test_supported_dev_environment_is_valid(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "dev"})
        self.assertTrue(result.is_valid)
        self.assertEqual(result.profile, "dev")

    def test_staging_requires_secret(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "staging"})
        self.assertFalse(result.is_valid)
        self.assertTrue(any(item.key == "YOUTUBE_API_KEY" for item in result.failures))

    def test_staging_with_secret_is_valid(self):
        result = validate_runtime_config(
            {
                "MCP_ENVIRONMENT": "staging",
                "YOUTUBE_API_KEY": "secret-value",
            }
        )
        self.assertTrue(result.is_valid)

    def test_error_details_redact_secret_values(self):
        result = validate_runtime_config({"MCP_ENVIRONMENT": "prod"})
        details = config_validation_error_details(result)
        serialized = str(details)
        self.assertIn("YOUTUBE_API_KEY", serialized)
        self.assertNotIn("secret-value", serialized)

    def test_ensure_runtime_config_raises_on_invalid_config(self):
        with self.assertRaisesRegex(RuntimeError, "Required runtime configuration is invalid"):
            ensure_runtime_config({})


if __name__ == "__main__":
    unittest.main()
