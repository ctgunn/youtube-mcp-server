import unittest
from pathlib import Path


class HostedDeploymentBootstrapDocsIntegrationTests(unittest.TestCase):
    def test_root_readme_documents_cloud_build_primary_and_github_fallback(self):
        content = Path("README.md").read_text()
        for expected in (
            "Automated hosted deployment",
            "`cloudbuild.yaml`",
            "Cloud Build is the primary",
            "GitHub Actions workflow is a manual fallback",
            "bootstrap prerequisites",
            "operator-managed secret values",
        ):
            self.assertIn(expected, content)

    def test_gcp_readme_documents_bootstrap_prerequisites_and_secret_boundary(self):
        content = Path("infrastructure/gcp/README.md").read_text()
        for expected in (
            "Push-triggered deployment bootstrap",
            "Terraform provisioning remains automation-managed",
            "Secret values remain operator-managed",
            "Cloud Build trigger",
            "GitHub Actions fallback",
            "Terraform-managed hosted network layer",
            "managed VPC network",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
