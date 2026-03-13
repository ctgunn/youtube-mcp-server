import os
import subprocess
import unittest
from pathlib import Path


class CloudRunDeploymentAssetsIntegrationTests(unittest.TestCase):
    def test_deploy_script_renders_gcloud_command(self):
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
            }
        )
        completed = subprocess.run(
            ["bash", "scripts/deploy_cloud_run.sh"],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        output = completed.stdout.strip()
        self.assertIn("gcloud run deploy youtube-mcp-server", output)
        self.assertIn("--service-account svc@example.iam.gserviceaccount.com", output)
        self.assertIn("--set-secrets YOUTUBE_API_KEY=YOUTUBE_API_KEY:latest", output)

    def test_docker_assets_include_required_patterns(self):
        dockerfile = Path("Dockerfile").read_text()
        dockerignore = Path(".dockerignore").read_text()
        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("mcp_server.cloud_run_entrypoint", dockerfile)
        for pattern in (".git/", ".env", ".codex/", "specs/"):
            self.assertIn(pattern, dockerignore)


if __name__ == "__main__":
    unittest.main()
