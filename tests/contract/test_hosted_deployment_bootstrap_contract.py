import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import BOOTSTRAP_PREREQUISITES


class HostedDeploymentBootstrapContractTests(unittest.TestCase):
    def test_bootstrap_contract_document_defines_secret_boundary(self):
        content = Path(
            "specs/025-hosted-deploy-orchestration/contracts/deployment-bootstrap-boundary-contract.md"
        ).read_text()
        for expected in (
            "Automation-managed responsibilities",
            "Operator-managed responsibilities",
            "YOUTUBE_API_KEY",
            "MCP_AUTH_TOKEN",
            "secret values",
        ):
            self.assertIn(expected, content)

    def test_github_workflow_contains_non_secret_bootstrap_checks(self):
        """Require the supported workflow to preflight safe prerequisite names.

        :return: ``None`` after checking the non-secret preflight boundary.
        :raises AssertionError: If preflight stops checking required identifiers.
        """
        content = Path(".github/workflows/hosted-deploy.yml").read_text()
        for expected in (
            "validate-bootstrap-prerequisites",
            "GCP_PROJECT_ID",
            "GCP_REGION",
            "GCP_WORKLOAD_IDENTITY_PROVIDER",
            "GCP_DEPLOYER_SERVICE_ACCOUNT",
        ):
            self.assertIn(expected, content)

    def test_bootstrap_prerequisite_set_includes_operator_managed_secrets(self):
        names = {item.name for item in BOOTSTRAP_PREREQUISITES if item.owner == "operator"}
        self.assertEqual(names, {"YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"})


if __name__ == "__main__":
    unittest.main()
