import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import HostedDeploymentWorkflowStage, serialize_workflow_run


class HostedDeploymentWorkflowIntegrationTests(unittest.TestCase):
    def test_cloud_build_file_contains_end_to_end_stage_sequence(self):
        content = Path("cloudbuild.yaml").read_text()
        ordered_markers = [
            "validate-bootstrap-prerequisites",
            "install-and-test",
            "build-image",
            "terraform-apply",
            "export-terraform-outputs",
            "deploy-hosted-revision",
            "verify-hosted-deployment",
        ]
        positions = [content.index(marker) for marker in ordered_markers]
        self.assertEqual(positions, sorted(positions))

    def test_github_workflow_is_documented_as_fallback(self):
        content = Path(".github/workflows/hosted-deploy.yml").read_text()
        self.assertIn("workflow_dispatch:", content)
        self.assertIn("hosted-deploy-fallback-", content)

    def test_workflow_summary_serialization_captures_deploy_and_verify_artifacts(self):
        payload = serialize_workflow_run(
            "main",
            "abc123",
            [
                HostedDeploymentWorkflowStage("quality_gate", "pass", "ok"),
                HostedDeploymentWorkflowStage("image_publish", "pass", "ok", "artifacts/image.txt"),
                HostedDeploymentWorkflowStage(
                    "deploy",
                    "pass",
                    "ok",
                    "artifacts/cloud-run-deployment.json",
                ),
                HostedDeploymentWorkflowStage(
                    "hosted_verification",
                    "pass",
                    "ok",
                    "artifacts/cloud-run-verification.json",
                ),
            ],
        )
        self.assertEqual(payload["overallResult"], "pass")
        self.assertIn("deploy", payload["artifacts"])
        self.assertIn("hosted_verification", payload["artifacts"])


if __name__ == "__main__":
    unittest.main()
