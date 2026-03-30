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
        self.assertEqual(payload["publicInvocationIntent"], "public_remote_mcp")
        self.assertEqual(payload["connectionPoint"], "https://example-service.run.app")

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

    def test_deploy_script_can_write_json_record_to_workflow_artifact_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_gcloud = Path(tmp) / "fake-gcloud"
            fake_gcloud.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s' '{\"status\":{\"latestReadyRevisionName\":\"youtube-mcp-server-00008\",\"url\":\"https://example-service.run.app\"}}'\n"
            )
            fake_gcloud.chmod(0o755)
            artifact = Path(tmp) / "cloud-run-deployment.json"
            env = self._env(str(fake_gcloud))
            env["DEPLOYMENT_RECORD_FILE"] = str(artifact)
            completed = subprocess.run(
                ["bash", "scripts/deploy_cloud_run.sh"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            file_payload = json.loads(artifact.read_text())

        stdout_payload = json.loads(completed.stdout)
        self.assertEqual(stdout_payload["revisionName"], file_payload["revisionName"])
        self.assertEqual(file_payload["serviceUrl"], "https://example-service.run.app")

    def test_docker_assets_include_required_patterns(self):
        dockerfile = Path("Dockerfile").read_text()
        dockerignore = Path(".dockerignore").read_text()
        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("mcp_server.cloud_run_entrypoint", dockerfile)
        self.assertIn("python3\", \"-m\", \"uvicorn\"", dockerfile)
        for pattern in (".git/", ".env", ".codex/", "specs/"):
            self.assertIn(pattern, dockerignore)

    def test_workflow_asset_list_includes_deploy_and_verify_artifacts(self):
        workflow = Path(".github/workflows/hosted-deploy.yml").read_text()
        cloudbuild = Path("cloudbuild.yaml").read_text()
        for artifact in (
            "artifacts/gcp-foundation-outputs.json",
            "artifacts/cloud-run-deployment.json",
            "artifacts/cloud-run-verification.json",
            "artifacts/cloud-run-verification.txt",
        ):
            self.assertIn(artifact, workflow)
            self.assertIn(artifact, cloudbuild)

    def test_github_workflow_is_manual_fallback_not_main_push_owner(self):
        workflow = Path(".github/workflows/hosted-deploy.yml").read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("push:\n    branches:\n      - main", workflow)


if __name__ == "__main__":
    unittest.main()
