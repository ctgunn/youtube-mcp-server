import unittest

from mcp_server.infrastructure_contract import (
    EXECUTION_MODES,
    SHARED_PLATFORM_CAPABILITIES,
    is_supported_execution_mode,
    normalize_capability_name,
)


class CloudAgnosticInfrastructureHelpersTests(unittest.TestCase):
    def test_normalize_capability_name_returns_canonical_snake_case(self):
        self.assertEqual(
            normalize_capability_name("Secret Backed Configuration"),
            "secret_backed_configuration",
        )
        self.assertEqual(
            normalize_capability_name("Hosted-runtime"),
            "hosted_runtime",
        )

    def test_supported_execution_modes_are_explicit(self):
        self.assertEqual(
            EXECUTION_MODES,
            ("minimal_local", "hosted_like_local", "hosted"),
        )
        self.assertTrue(is_supported_execution_mode("hosted_like_local"))
        self.assertTrue(is_supported_execution_mode("Hosted Like Local"))
        self.assertFalse(is_supported_execution_mode("provider_only"))

    def test_shared_platform_capabilities_include_portability_baseline(self):
        self.assertEqual(
            SHARED_PLATFORM_CAPABILITIES,
            (
                "hosted_runtime",
                "network_ingress",
                "runtime_identity",
                "secret_backed_configuration",
                "observability_integration",
                "durable_session_support",
            ),
        )


if __name__ == "__main__":
    unittest.main()
