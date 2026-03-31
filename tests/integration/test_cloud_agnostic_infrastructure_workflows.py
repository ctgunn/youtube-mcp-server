import unittest
from pathlib import Path


class CloudAgnosticInfrastructureWorkflowTests(unittest.TestCase):
    def test_gcp_readme_reframes_gcp_as_primary_provider_adapter(self):
        content = Path("infrastructure/gcp/README.md").read_text()
        for expected in (
            "primary provider adapter",
            "shared platform contract",
            "provider-specific implementation",
            "scripts/deploy_cloud_run.sh",
        ):
            self.assertIn(expected, content)

    def test_root_readme_links_shared_contract_to_hosted_and_local_modes(self):
        content = Path("README.md").read_text()
        for expected in (
            "shared platform contract",
            "primary hosted provider adapter",
            "Minimal local runtime path",
            "Hosted-like local verification path",
            "provider adapter",
            "bash scripts/dev_local.sh",
        ):
            self.assertIn(expected, content)

    def test_local_readme_preserves_minimal_local_and_hosted_like_separation(self):
        content = Path("infrastructure/local/README.md").read_text()
        for expected in (
            "shared platform contract",
            "Minimal local runtime",
            "Hosted-like local verification",
            "provider-free",
            "docker compose -f infrastructure/local/compose.yaml up -d",
            "LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh",
        ):
            self.assertIn(expected, content)

    def test_feature_quickstart_covers_shared_contract_gcp_aws_and_execution_modes(self):
        content = Path("specs/020-cloud-agnostic-iac/quickstart.md").read_text()
        for expected in (
            "shared platform contract",
            "primary provider adapter",
            "AWS provider adapter",
            "execution modes",
            "pytest",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
