import unittest
from pathlib import Path


class IaCFoundationContractTests(unittest.TestCase):
    def test_gcp_contract_lists_required_inputs_and_outputs(self):
        content = Path("specs/019-iac-foundation/contracts/gcp-hosted-foundation-contract.md").read_text()
        for expected in (
            "project_id",
            "region",
            "service_name",
            "service_account_name",
            "Cloud Run service foundation",
            "Redis-compatible durable session backend",
            "MCP_SESSION_STORE_URL",
            "IMAGE_REFERENCE",
            "scripts/deploy_cloud_run.sh",
        ):
            self.assertIn(expected, content)

    def test_local_contract_preserves_minimal_local_runtime(self):
        content = Path("specs/019-iac-foundation/contracts/local-hosted-dependency-contract.md").read_text()
        for expected in (
            "Minimal Local Runtime",
            "Hosted-Like Local Verification",
            "MCP_SESSION_BACKEND=redis",
            "MCP_SESSION_STORE_URL",
            "must not be required to configure hosted infrastructure inputs",
        ):
            self.assertIn(expected, content)

    def test_gcp_infrastructure_files_define_required_foundation_components(self):
        versions = Path("infrastructure/gcp/versions.tf").read_text()
        variables = Path("infrastructure/gcp/variables.tf").read_text()
        main = Path("infrastructure/gcp/main.tf").read_text()
        session = Path("infrastructure/gcp/session.tf").read_text()
        outputs = Path("infrastructure/gcp/outputs.tf").read_text()
        ignore = Path(".terraformignore").read_text()

        self.assertIn("hashicorp/google", versions)
        self.assertIn('variable "project_id"', variables)
        self.assertIn('variable "service_name"', variables)
        self.assertIn("google_cloud_run_v2_service", main)
        self.assertIn("google_service_account", main)
        self.assertIn("google_secret_manager_secret", main)
        self.assertIn("google_redis_instance", session)
        self.assertIn('output "service_account_email"', outputs)
        self.assertIn('output "mcp_session_store_url"', outputs)
        for pattern in (".terraform/", "*.tfstate", "*.tfvars", ".terraform.lock.hcl"):
            self.assertIn(pattern, ignore)

    def test_local_dependency_assets_define_redis_backed_workflow(self):
        compose = Path("infrastructure/local/compose.yaml").read_text()
        readme = Path("infrastructure/local/README.md").read_text()
        env_example = Path("infrastructure/local/.env.example").read_text()

        self.assertIn("redis:7-alpine", compose)
        self.assertIn("docker compose -f infrastructure/local/compose.yaml up -d", readme)
        self.assertIn("MCP_SESSION_BACKEND=redis", readme)
        self.assertIn("MCP_SESSION_STORE_URL=redis://127.0.0.1:6379/0", env_example)


if __name__ == "__main__":
    unittest.main()
