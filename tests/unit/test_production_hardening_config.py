"""Red/green tests for production-hardening runtime configuration."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import load_production_hardening_settings, validate_runtime_config


class ProductionHardeningConfigTests(unittest.TestCase):
    """Verify safe defaults and hosted configuration boundaries."""

    def test_dev_defaults_use_local_memory_without_alert_delivery(self) -> None:
        """Keep local hardening state process-local by default."""
        settings = load_production_hardening_settings({"MCP_ENVIRONMENT": "dev"})

        self.assertEqual(settings.rate_limit.identified_requests_per_minute, 60)
        self.assertEqual(settings.rate_limit.anonymous_requests_per_minute, 10)
        self.assertEqual(settings.rate_limit.backend, "memory")
        self.assertEqual(settings.result_cache.max_freshness_seconds, 300)
        self.assertFalse(settings.alerting.enabled)

    def test_invalid_hardening_values_fail_startup_validation(self) -> None:
        """Reject invalid policy values before a hosted service starts."""
        result = validate_runtime_config(
            {
                "MCP_ENVIRONMENT": "dev",
                "MCP_RATE_LIMIT_IDENTIFIED_REQUESTS_PER_MINUTE": "0",
                "MCP_RESULT_CACHE_MAX_FRESHNESS_SECONDS": "301",
            }
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(
            {failure.key for failure in result.failures},
            {
                "MCP_RATE_LIMIT_IDENTIFIED_REQUESTS_PER_MINUTE",
                "MCP_RESULT_CACHE_MAX_FRESHNESS_SECONDS",
            },
        )


if __name__ == "__main__":
    unittest.main()
