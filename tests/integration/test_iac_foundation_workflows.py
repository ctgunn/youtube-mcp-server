import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class IaCFoundationWorkflowsIntegrationTests(unittest.TestCase):
    def _terraform_outputs(self):
        return {
            "project_id": {"value": "project-id"},
            "region": {"value": "us-central1"},
            "environment": {"value": "staging"},
            "service_name": {"value": "youtube-mcp-server"},
            "service_account_email": {"value": "svc@example.iam.gserviceaccount.com"},
            "secret_reference_names": {"value": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"]},
            "mcp_auth_required": {"value": True},
            "mcp_allowed_origins": {"value": "https://chat.openai.com"},
            "mcp_allow_originless_clients": {"value": True},
            "mcp_session_backend": {"value": "redis"},
            "mcp_session_store_url": {"value": "redis://10.0.0.3:6379/0"},
            "mcp_session_connectivity_model": {"value": "serverless_vpc_connector"},
            "mcp_session_network_reference": {"value": "projects/project-id/global/networks/youtube-mcp-server-staging-network"},
            "mcp_session_subnet_reference": {"value": "projects/project-id/regions/us-central1/subnetworks/youtube-mcp-server-staging-subnet"},
            "mcp_session_connector_reference": {"value": "projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector"},
            "mcp_session_durability_required": {"value": True},
            "mcp_session_ttl_seconds": {"value": 1800},
            "mcp_session_replay_ttl_seconds": {"value": 300},
            "min_instances": {"value": 0},
            "max_instances": {"value": 2},
            "concurrency": {"value": 20},
            "timeout_seconds": {"value": 180},
        }

    def test_deploy_script_can_consume_terraform_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            outputs = Path(tmp) / "outputs.json"
            outputs.write_text(json.dumps(self._terraform_outputs()))
            fake_gcloud = Path(tmp) / "fake-gcloud"
            fake_gcloud.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s' '{\"status\":{\"latestReadyRevisionName\":\"youtube-mcp-server-00009\",\"url\":\"https://example-service.run.app\"}}'\n"
            )
            fake_gcloud.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "INFRA_OUTPUTS_FILE": str(outputs),
                    "IMAGE_REFERENCE": "us-docker.pkg.dev/project/app/image:sha",
                    "GCLOUD_BIN": str(fake_gcloud),
                }
            )
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["outcome"], "success")
        self.assertEqual(payload["runtimeSettings"]["serviceName"], "youtube-mcp-server")
        self.assertEqual(payload["runtimeSettings"]["configSummary"]["MCP_SESSION_BACKEND"], "redis")
        self.assertEqual(payload["runtimeSettings"]["secretReferenceNames"], ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"])
        self.assertEqual(
            payload["runtimeSettings"]["sessionNetworkReference"],
            "projects/project-id/global/networks/youtube-mcp-server-staging-network",
        )
        self.assertEqual(
            payload["runtimeSettings"]["sessionSubnetReference"],
            "projects/project-id/regions/us-central1/subnetworks/youtube-mcp-server-staging-subnet",
        )
        self.assertEqual(
            payload["runtimeSettings"]["sessionConnectorReference"],
            "projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector",
        )

    def test_gcp_readme_describes_plan_apply_and_handoff(self):
        content = Path("infrastructure/gcp/README.md").read_text()
        self.assertIn("terraform -chdir=infrastructure/gcp init", content)
        self.assertIn("terraform -chdir=infrastructure/gcp plan -var-file=staging.tfvars", content)
        self.assertIn("terraform -chdir=infrastructure/gcp apply -var-file=staging.tfvars", content)
        self.assertIn("terraform -chdir=infrastructure/gcp output -json > artifacts/gcp-foundation-outputs.json", content)
        self.assertIn("INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json", content)
        self.assertIn("Terraform-managed hosted network layer", content)
        self.assertIn("managed VPC network", content)
        self.assertIn("Serverless VPC Access connector", content)

    def test_readme_distinguishes_minimal_local_from_hosted_like_local(self):
        content = Path("README.md").read_text()
        self.assertIn("Minimal local runtime path", content)
        self.assertIn("Hosted-like local verification path", content)
        self.assertIn("bash scripts/dev_local.sh", content)
        self.assertIn("Hosted deployment-only inputs", content)
        self.assertIn("docker compose -f infrastructure/local/compose.yaml up -d", content)
        self.assertIn("INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json", content)


if __name__ == "__main__":
    unittest.main()
