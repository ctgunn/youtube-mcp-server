import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import deployment_input_from_mapping, execute_deploy_command, serialize_deployment_run


class CloudRunDeployExecutionUnitTests(unittest.TestCase):
    def _settings(self):
        return deployment_input_from_mapping(
            {
                "PROJECT_ID": "project-id",
                "REGION": "us-central1",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "us-docker.pkg.dev/project/app/image:sha",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "MCP_ENVIRONMENT": "staging",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "2",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
                "SECRET_REFERENCES": "YOUTUBE_API_KEY,MCP_AUTH_TOKEN",
            }
        )

    def test_execute_deploy_command_records_successful_revision(self):
        settings = self._settings()

        def runner(command, **_kwargs):
            self.assertEqual(command[0], "fake-gcloud")
            self.assertIn("--format", command)
            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"status":{"latestReadyRevisionName":"youtube-mcp-server-00008","url":"https://example-service.run.app"}}',
                stderr="",
            )

        record = execute_deploy_command(settings, runner=runner, gcloud_bin="fake-gcloud")
        payload = serialize_deployment_run(record)
        self.assertEqual(payload["outcome"], "success")
        self.assertEqual(payload["revisionName"], "youtube-mcp-server-00008")
        self.assertEqual(payload["serviceUrl"], "https://example-service.run.app")
        self.assertEqual(payload["runtimeSettings"]["environmentProfile"], "staging")

    def test_execute_deploy_command_fails_before_runner_on_invalid_inputs(self):
        settings = deployment_input_from_mapping(
            {
                "PROJECT_ID": "project-id",
                "REGION": "us-central1",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "MCP_ENVIRONMENT": "staging",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
            }
        )

        def runner(*_args, **_kwargs):  # pragma: no cover - should never run
            raise AssertionError("runner should not be invoked when validation fails")

        record = execute_deploy_command(settings, runner=runner)
        self.assertEqual(record.outcome, "failed")
        self.assertEqual(record.failure_stage, "input_validation")
        self.assertIn("YOUTUBE_API_KEY", record.summary)

    def test_execute_deploy_command_marks_incomplete_when_metadata_missing(self):
        settings = self._settings()

        def runner(command, **_kwargs):
            return subprocess.CompletedProcess(command, 0, stdout='{"status":{}}', stderr="")

        record = execute_deploy_command(settings, runner=runner)
        self.assertEqual(record.outcome, "incomplete")
        self.assertEqual(record.failure_stage, "metadata_capture")


if __name__ == "__main__":
    unittest.main()
