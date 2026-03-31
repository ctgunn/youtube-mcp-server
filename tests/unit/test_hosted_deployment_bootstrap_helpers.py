import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import (
    BOOTSTRAP_PREREQUISITES,
    classify_bootstrap_failure,
    collect_missing_bootstrap_prerequisites,
)


class HostedDeploymentBootstrapHelpersUnitTests(unittest.TestCase):
    def test_bootstrap_prerequisites_keep_operator_and_automation_ownership_separate(self):
        owners = {item.name: item.owner for item in BOOTSTRAP_PREREQUISITES}
        self.assertEqual(owners["YOUTUBE_API_KEY"], "operator")
        self.assertEqual(owners["MCP_AUTH_TOKEN"], "operator")
        self.assertEqual(owners["GCP_WORKLOAD_IDENTITY_PROVIDER"], "automation")

    def test_collect_missing_bootstrap_prerequisites_accepts_boolean_flags(self):
        missing = collect_missing_bootstrap_prerequisites(
            {
                "GCP_PROJECT_ID": True,
                "GCP_REGION": True,
                "GCP_WORKLOAD_IDENTITY_PROVIDER": True,
                "GCP_SERVICE_ACCOUNT": True,
                "GCP_ARTIFACT_REGISTRY_REPOSITORY": True,
                "GCP_TERRAFORM_VAR_FILE": True,
                "YOUTUBE_API_KEY": True,
                "MCP_AUTH_TOKEN": False,
            }
        )
        self.assertEqual([item.name for item in missing], ["MCP_AUTH_TOKEN"])

    def test_classify_bootstrap_failure_distinguishes_quality_gate_and_reconcile(self):
        self.assertEqual(
            classify_bootstrap_failure("quality_gate", "Missing bootstrap prerequisites: GCP_PROJECT_ID"),
            "bootstrap_input_failure",
        )
        self.assertEqual(
            classify_bootstrap_failure(
                "infrastructure_reconcile",
                "Managed network bootstrap failed while reconciling infrastructure.",
            ),
            "network_reconcile_failure",
        )


if __name__ == "__main__":
    unittest.main()
