import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import (
    config_validation_error_details,
    ensure_runtime_config,
    load_youtube_live_runtime_settings,
    youtube_capability_readiness,
    validate_runtime_config,
)


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
                "MCP_AUTH_TOKEN": "token",
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

    def test_live_youtube_settings_load_available_credentials_without_exposing_them(self):
        settings = load_youtube_live_runtime_settings(
            {
                "YOUTUBE_API_KEY": "api-key-for-test",
                "YOUTUBE_OAUTH_TOKEN": "oauth-token-for-test",
            }
        )

        self.assertTrue(settings.has_api_key)
        self.assertTrue(settings.has_oauth_token)
        self.assertEqual(settings.timeout_seconds, 10.0)
        self.assertEqual(settings.max_attempts, 3)
        self.assertEqual(
            settings.safe_details(),
            {
                "apiKeyConfigured": True,
                "oauthTokenConfigured": True,
                "oauthLifecycle": "static",
                "timeoutSeconds": 10.0,
                "maxAttempts": 3,
            },
        )
        self.assertNotIn("api-key-for-test", str(settings.safe_details()))
        self.assertNotIn("oauth-token-for-test", str(settings.safe_details()))

    def test_live_youtube_settings_treat_blank_credentials_as_unavailable(self):
        settings = load_youtube_live_runtime_settings(
            {
                "YOUTUBE_API_KEY": "   ",
                "YOUTUBE_OAUTH_TOKEN": "\t",
            }
        )

        self.assertFalse(settings.has_api_key)
        self.assertFalse(settings.has_oauth_token)
        self.assertEqual(settings.safe_details()["apiKeyConfigured"], False)
        self.assertEqual(settings.safe_details()["oauthTokenConfigured"], False)

    def test_youtube_capability_readiness_distinguishes_public_and_oauth_access(self):
        """Report API-key and OAuth capability independently without exposing secrets."""
        api_key_only = youtube_capability_readiness(
            load_youtube_live_runtime_settings({"YOUTUBE_API_KEY": "api-key-for-test"})
        )
        complete = youtube_capability_readiness(
            load_youtube_live_runtime_settings(
                {"YOUTUBE_API_KEY": "api-key-for-test", "YOUTUBE_OAUTH_TOKEN": "oauth-token-for-test"}
            )
        )

        self.assertEqual(
            api_key_only,
            {
                "apiKeyRead": "available",
                "oauthOwnerAndMutation": "not_configured",
                "oauthLifecycle": "not_configured",
            },
        )
        self.assertEqual(
            complete,
            {
                "apiKeyRead": "available",
                "oauthOwnerAndMutation": "available",
                "oauthLifecycle": "static",
            },
        )
        self.assertNotIn("api-key-for-test", str(complete))
        self.assertNotIn("oauth-token-for-test", str(complete))


if __name__ == "__main__":
    unittest.main()
