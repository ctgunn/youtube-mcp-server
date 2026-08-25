import unittest
from pathlib import Path


class HostedDeploymentBootstrapDocsIntegrationTests(unittest.TestCase):
    def test_root_readme_documents_github_actions_and_cloud_build_deprecation(self):
        """Require the root runbook to name the current release topology.

        :return: ``None`` after checking deployment ownership documentation.
        :raises AssertionError: If retired Cloud Build returns as the primary path.
        """
        content = Path("README.md").read_text()
        for expected in (
            "Hosted deployment workflow",
            "GitHub Actions workflow",
            "Cloud Build configuration",
            "deprecated",
            "Hosted deployment prerequisites",
            "operator-managed secret values",
        ):
            self.assertIn(expected, content)

    def test_gcp_readme_documents_hosted_workflow_and_secret_boundary(self):
        """Require the GCP runbook to describe the supported release workflow.

        :return: ``None`` after checking operator prerequisites.
        :raises AssertionError: If the GCP runbook points to retired automation.
        """
        content = Path("infrastructure/gcp/README.md").read_text()
        for expected in (
            "Hosted deployment workflow",
            "Terraform provisioning remains automation-managed",
            "Secret values remain operator-managed",
            "GitHub Actions workflow",
            "Cloud Build triggers are disabled",
            "Terraform-managed hosted network layer",
            "managed VPC network",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
