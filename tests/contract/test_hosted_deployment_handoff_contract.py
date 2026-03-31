import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import iac_outputs_to_mapping, load_json_artifact


class HostedDeploymentHandoffContractTests(unittest.TestCase):
    def test_cloud_build_uses_terraform_output_handoff_and_not_direct_image_only_update(self):
        content = Path("cloudbuild.yaml").read_text()
        self.assertIn("INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json", content)
        self.assertIn("bash scripts/deploy_cloud_run.sh", content)
        self.assertNotIn("gcloud run deploy $SERVICE_NAME", content)

    def test_iac_outputs_map_into_workflow_expected_environment_keys(self):
        payload = iac_outputs_to_mapping(
            {
                "project_id": {"value": "project-id"},
                "region": {"value": "us-central1"},
                "environment": {"value": "staging"},
                "service_name": {"value": "youtube-mcp-server"},
                "service_account_email": {"value": "svc@example.iam.gserviceaccount.com"},
            }
        )
        self.assertEqual(payload["PROJECT_ID"], "project-id")
        self.assertEqual(payload["REGION"], "us-central1")
        self.assertEqual(payload["MCP_ENVIRONMENT"], "staging")

    def test_load_json_artifact_reads_deployment_record_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cloud-run-deployment.json"
            path.write_text(json.dumps({"serviceUrl": "https://example.run.app"}))
            payload = load_json_artifact(path)
        self.assertEqual(payload["serviceUrl"], "https://example.run.app")


if __name__ == "__main__":
    unittest.main()
