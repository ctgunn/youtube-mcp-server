import os
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CloudRunDeploymentAssetsIntegrationTests(unittest.TestCase):
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
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "2",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
                "SECRET_REFERENCES": "YOUTUBE_API_KEY",
                "GCLOUD_BIN": fake_gcloud,
            }
        )
        return env

    def test_deploy_script_executes_gcloud_and_outputs_json_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_gcloud = Path(tmp) / "fake-gcloud"
            fake_gcloud.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s' '{\"status\":{\"latestReadyRevisionName\":\"youtube-mcp-server-00008\",\"url\":\"https://example-service.run.app\"}}'\n"
            )
            fake_gcloud.chmod(0o755)
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=True,
                capture_output=True,
                text=True,
                env=self._env(str(fake_gcloud)),
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["outcome"], "success")
        self.assertEqual(payload["revisionName"], "youtube-mcp-server-00008")
        self.assertEqual(payload["serviceUrl"], "https://example-service.run.app")

    def test_deploy_script_reports_failed_outcome_when_gcloud_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_gcloud = Path(tmp) / "fake-gcloud"
            fake_gcloud.write_text("#!/usr/bin/env bash\necho 'boom' 1>&2\nexit 9\n")
            fake_gcloud.chmod(0o755)
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=False,
                capture_output=True,
                text=True,
                env=self._env(str(fake_gcloud)),
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["outcome"], "failed")
        self.assertEqual(payload["failureStage"], "deployment_execution")
        self.assertIn("boom", payload["summary"])

    def test_docker_assets_include_required_patterns(self):
        dockerfile = Path("Dockerfile").read_text()
        dockerignore = Path(".dockerignore").read_text()
        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("mcp_server.cloud_run_entrypoint", dockerfile)
        self.assertIn("python3\", \"-m\", \"uvicorn\"", dockerfile)
        for pattern in (".git/", ".env", ".codex/", "specs/"):
            self.assertIn(pattern, dockerignore)


if __name__ == "__main__":
    unittest.main()
