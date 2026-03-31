import unittest
from pathlib import Path


class HostedDeploymentPipelineContractTests(unittest.TestCase):
    def test_contract_document_lists_required_ordered_stages(self):
        content = Path(
            "specs/025-hosted-deploy-orchestration/contracts/hosted-deployment-pipeline-contract.md"
        ).read_text()
        for expected in (
            "quality_gate",
            "image_publish",
            "infrastructure_reconcile",
            "terraform_output_export",
            "deploy",
            "hosted_verification",
            "scripts/deploy_cloud_run.sh",
            "scripts/verify_cloud_run_foundation.py",
        ):
            self.assertIn(expected, content)

    def test_cloud_build_file_declares_required_stage_commands(self):
        content = Path("cloudbuild.yaml").read_text()
        for expected in (
            "terraform -chdir=infrastructure/gcp apply",
            "terraform -chdir=infrastructure/gcp output -json",
            "bash scripts/deploy_cloud_run.sh",
            "python3 scripts/verify_cloud_run_foundation.py",
            "pytest",
            "ruff check .",
        ):
            self.assertIn(expected, content)

    def test_github_workflow_is_manual_fallback(self):
        content = Path(".github/workflows/hosted-deploy.yml").read_text()
        for expected in (
            "workflow_dispatch:",
            "target_ref:",
            "target_environment:",
            "pytest",
            "ruff check .",
            "bash scripts/deploy_cloud_run.sh",
            "python3 scripts/verify_cloud_run_foundation.py",
        ):
            self.assertIn(expected, content)
        self.assertNotIn("push:\n    branches:\n      - main", content)


if __name__ == "__main__":
    unittest.main()
