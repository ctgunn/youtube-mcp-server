import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class CloudRunDeploymentMetadataIntegrationTests(unittest.TestCase):
    def _env(self, fake_gcloud: str) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "PROJECT_ID": "project-id",
                "REGION": "us-central1",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "us-docker.pkg.dev/project/app/image:sha",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "MCP_ENVIRONMENT": "staging",
                "PUBLIC_INVOCATION_INTENT": "public_remote_mcp",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "2",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
                "SECRET_REFERENCES": "YOUTUBE_API_KEY,MCP_AUTH_TOKEN",
                "GCLOUD_BIN": fake_gcloud,
            }
        )
        return env

    def _fake_gcloud(self, body: str, exit_code: int = 0) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "fake-gcloud"
            script_path.write_text(f"#!/usr/bin/env bash\nprintf '%s' '{body}'\nexit {exit_code}\n")
            script_path.chmod(0o755)
            yield str(script_path)

    def test_deploy_script_emits_revision_metadata_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "fake-gcloud"
            script_path.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s' '{\"status\":{\"latestReadyRevisionName\":\"youtube-mcp-server-00008\",\"url\":\"https://example-service.run.app\"}}'\n"
            )
            script_path.chmod(0o755)
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=True,
                capture_output=True,
                text=True,
                env=self._env(str(script_path)),
            )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["outcome"], "success")
        self.assertEqual(payload["revisionName"], "youtube-mcp-server-00008")
        self.assertEqual(payload["serviceUrl"], "https://example-service.run.app")
        self.assertEqual(payload["connectionPoint"], "https://example-service.run.app")
        self.assertEqual(payload["publicInvocationIntent"], "public_remote_mcp")
        self.assertEqual(payload["runtimeSettings"]["runtimeIdentity"], "svc@example.iam.gserviceaccount.com")
        self.assertEqual(payload["runtimeSettings"]["serverImplementation"], "uvicorn")
        self.assertEqual(payload["runtimeSettings"]["appModule"], "mcp_server.cloud_run_entrypoint:app")

    def test_deploy_script_marks_incomplete_when_metadata_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "fake-gcloud"
            script_path.write_text("#!/usr/bin/env bash\nprintf '%s' '{\"status\":{}}'\n")
            script_path.chmod(0o755)
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=False,
                capture_output=True,
                text=True,
                env=self._env(str(script_path)),
            )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["outcome"], "incomplete")
        self.assertEqual(payload["failureStage"], "metadata_capture")


if __name__ == "__main__":
    unittest.main()
