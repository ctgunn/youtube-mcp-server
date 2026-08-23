import unittest
from pathlib import Path


class HostedDeploymentPipelineContractTests(unittest.TestCase):
    def test_contract_document_lists_required_ordered_stages(self):
        """Require the hosted deployment contract to retain its stage sequence.

        :return: ``None`` after validating the documented release stages.
        """
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
        """Require Cloud Build to use canonical quality and deployment commands.

        :return: ``None`` after validating the checked-in Cloud Build contract.
        """
        content = Path("cloudbuild.yaml").read_text()
        for expected in (
            "terraform -chdir=infrastructure/gcp apply",
            "terraform -chdir=infrastructure/gcp output -json",
            "bash scripts/deploy_cloud_run.sh",
            "python3 scripts/verify_cloud_run_foundation.py",
            "make quality",
            "resolve-source-revision",
            "release-provenance.json",
        ):
            self.assertIn(expected, content)

    def test_github_workflow_is_manual_fallback(self):
        """Require the manual fallback to share the guarded release contract.

        :return: ``None`` after validating fallback-only workflow behavior.
        """
        content = Path(".github/workflows/hosted-deploy.yml").read_text()
        for expected in (
            "workflow_dispatch:",
            "target_ref:",
            "target_environment:",
            "make quality",
            "resolve-source-revision",
            "release-provenance.json",
            "bash scripts/deploy_cloud_run.sh",
            "python3 scripts/verify_cloud_run_foundation.py",
        ):
            self.assertIn(expected, content)
        self.assertNotIn("push:\n    branches:\n      - main", content)


if __name__ == "__main__":
    unittest.main()
