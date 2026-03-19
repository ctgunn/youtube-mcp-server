import unittest
from pathlib import Path


class CloudRunDocsExamplesIntegrationTests(unittest.TestCase):
    def test_readme_includes_deploy_and_verify_commands(self):
        content = Path("README.md").read_text()
        self.assertIn("scripts/deploy_cloud_run.sh", content)
        self.assertIn("scripts/verify_cloud_run_foundation.py", content)
        self.assertIn("python3 -m uvicorn", content)
        self.assertIn("mcp_server.cloud_run_entrypoint:app", content)
        self.assertIn("SERVICE_ACCOUNT_EMAIL", content)
        self.assertIn("TIMEOUT_SECONDS", content)
        self.assertIn("MCP-Session-Id", content)
        self.assertIn("text/event-stream", content)
        self.assertIn("Last-Event-ID", content)
        self.assertIn("Authorization: Bearer", content)
        self.assertIn("MCP_AUTH_TOKEN", content)
        self.assertIn("MCP_ALLOWED_ORIGINS", content)
        self.assertIn("Access-Control-Request-Method", content)
        self.assertIn("http://localhost:3000", content)
        self.assertIn('"name":"search"', content)
        self.assertIn('"name":"fetch"', content)
        self.assertIn("remote MCP research", content)

    def test_env_example_contains_hosted_deploy_inputs(self):
        content = Path(".env.example").read_text()
        for key in (
            "PROJECT_ID",
            "REGION",
            "SERVICE_NAME",
            "IMAGE_REFERENCE",
            "SERVICE_ACCOUNT_EMAIL",
            "MCP_SERVER_IMPLEMENTATION",
            "MCP_ASGI_APP",
            "MIN_INSTANCES",
            "MAX_INSTANCES",
            "CONCURRENCY",
            "TIMEOUT_SECONDS",
            "MCP_AUTH_TOKEN",
            "MCP_ALLOWED_ORIGINS",
            "MCP_ALLOW_ORIGINLESS_CLIENTS",
        ):
            self.assertIn(f"{key}=", content)


if __name__ == "__main__":
    unittest.main()
