import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import deployment_input_from_iac_outputs, execute_deploy_command, load_json_artifact, serialize_deployment_run


class HostedDeploymentHandoffIntegrationTests(unittest.TestCase):
    def test_iac_outputs_can_drive_deploy_command_inputs(self):
        settings = deployment_input_from_iac_outputs(
            {
                "project_id": {"value": "project-id"},
                "region": {"value": "us-central1"},
                "environment": {"value": "staging"},
                "service_name": {"value": "youtube-mcp-server"},
                "service_account_email": {"value": "svc@example.iam.gserviceaccount.com"},
                "secret_reference_names": {"value": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"]},
                "public_invocation_intent": {"value": "public_remote_mcp"},
                "mcp_session_network_reference": {"value": "projects/project-id/global/networks/youtube-mcp-server-staging-network"},
                "mcp_session_subnet_reference": {"value": "projects/project-id/regions/us-central1/subnetworks/youtube-mcp-server-staging-subnet"},
                "mcp_session_connector_reference": {"value": "projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector"},
                "min_instances": {"value": 0},
                "max_instances": {"value": 2},
                "concurrency": {"value": 20},
                "timeout_seconds": {"value": 180},
            },
            image_reference="us-docker.pkg.dev/project/app/image:sha",
        )
        self.assertEqual(settings.project_id, "project-id")
        self.assertEqual(settings.service_name, "youtube-mcp-server")
        self.assertEqual(settings.secret_references, ("YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"))
        self.assertEqual(
            settings.session_connector_reference,
            "projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector",
        )

    def test_deployment_record_written_by_deploy_helper_can_be_reloaded_as_workflow_artifact(self):
        settings = deployment_input_from_iac_outputs(
            {
                "project_id": {"value": "project-id"},
                "region": {"value": "us-central1"},
                "environment": {"value": "staging"},
                "service_name": {"value": "youtube-mcp-server"},
                "service_account_email": {"value": "svc@example.iam.gserviceaccount.com"},
                "secret_reference_names": {"value": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"]},
                "public_invocation_intent": {"value": "public_remote_mcp"},
                "mcp_session_network_reference": {"value": "projects/project-id/global/networks/youtube-mcp-server-staging-network"},
                "mcp_session_subnet_reference": {"value": "projects/project-id/regions/us-central1/subnetworks/youtube-mcp-server-staging-subnet"},
                "mcp_session_connector_reference": {"value": "projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector"},
                "min_instances": {"value": 0},
                "max_instances": {"value": 2},
                "concurrency": {"value": 20},
                "timeout_seconds": {"value": 180},
            },
            image_reference="us-docker.pkg.dev/project/app/image:sha",
        )

        def runner(command, **_kwargs):
            import subprocess

            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"status":{"latestReadyRevisionName":"youtube-mcp-server-00008","url":"https://example.run.app"}}',
                stderr="",
            )

        record = execute_deploy_command(settings, runner=runner, gcloud_bin="fake-gcloud")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cloud-run-deployment.json"
            path.write_text(json.dumps(serialize_deployment_run(record)))
            payload = load_json_artifact(path)
        self.assertEqual(payload["revisionName"], "youtube-mcp-server-00008")
        self.assertEqual(
            payload["runtimeSettings"]["sessionNetworkReference"],
            "projects/project-id/global/networks/youtube-mcp-server-staging-network",
        )


if __name__ == "__main__":
    unittest.main()
