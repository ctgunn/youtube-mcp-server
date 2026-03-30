import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import (
    HostedDeploymentWorkflowStage,
    WORKFLOW_STAGE_ORDER,
    collect_missing_bootstrap_prerequisites,
    load_json_artifact,
    serialize_workflow_run,
    serialize_workflow_stage,
    workflow_overall_result,
)


class HostedDeploymentPipelineHelpersUnitTests(unittest.TestCase):
    def test_serialize_workflow_stage_preserves_artifact_path(self):
        payload = serialize_workflow_stage(
            HostedDeploymentWorkflowStage(
                stage_name="deploy",
                result="pass",
                summary="Deployment completed.",
                artifact_path="artifacts/cloud-run-deployment.json",
            )
        )
        self.assertEqual(payload["stageName"], "deploy")
        self.assertEqual(payload["artifactPath"], "artifacts/cloud-run-deployment.json")

    def test_workflow_overall_result_fails_on_first_failed_stage(self):
        result = workflow_overall_result(
            [
                HostedDeploymentWorkflowStage("quality_gate", "pass", "ok"),
                HostedDeploymentWorkflowStage("deploy", "fail", "boom"),
                HostedDeploymentWorkflowStage("hosted_verification", "pass", "ok"),
            ]
        )
        self.assertEqual(result, "fail")

    def test_serialize_workflow_run_exposes_stage_order_and_artifacts(self):
        payload = serialize_workflow_run(
            "main",
            "abc123",
            [
                HostedDeploymentWorkflowStage("quality_gate", "pass", "ok"),
                HostedDeploymentWorkflowStage(
                    "deploy",
                    "pass",
                    "Deployment completed.",
                    artifact_path="artifacts/cloud-run-deployment.json",
                ),
                HostedDeploymentWorkflowStage(
                    "hosted_verification",
                    "pass",
                    "Verification completed.",
                    artifact_path="artifacts/cloud-run-verification.json",
                ),
            ],
        )
        self.assertEqual(payload["branchName"], "main")
        self.assertEqual(payload["revisionRef"], "abc123")
        self.assertEqual(payload["stageOrder"], list(WORKFLOW_STAGE_ORDER))
        self.assertEqual(payload["overallResult"], "pass")
        self.assertEqual(payload["artifacts"]["deploy"], "artifacts/cloud-run-deployment.json")

    def test_load_json_artifact_reads_workflow_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "artifact.json"
            artifact.write_text(json.dumps({"overallResult": "pass"}))
            payload = load_json_artifact(artifact)
        self.assertEqual(payload["overallResult"], "pass")

    def test_collect_missing_bootstrap_prerequisites_reports_blank_values(self):
        missing = collect_missing_bootstrap_prerequisites(
            {
                "GCP_PROJECT_ID": "project-id",
                "GCP_REGION": "us-central1",
                "GCP_WORKLOAD_IDENTITY_PROVIDER": "",
                "GCP_SERVICE_ACCOUNT": "svc@example.iam.gserviceaccount.com",
                "GCP_ARTIFACT_REGISTRY_REPOSITORY": "apps",
                "GCP_TERRAFORM_VAR_FILE": "staging.tfvars",
                "YOUTUBE_API_KEY": "masked",
                "MCP_AUTH_TOKEN": "",
            }
        )
        self.assertEqual(
            [item.name for item in missing],
            ["GCP_WORKLOAD_IDENTITY_PROVIDER", "MCP_AUTH_TOKEN"],
        )


if __name__ == "__main__":
    unittest.main()
