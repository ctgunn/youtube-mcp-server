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
        self.assertIn("MCP_SECRET_ACCESS_MODE", content)
        self.assertIn("MCP_SECRET_REFERENCE_NAMES", content)
        self.assertIn("PUBLIC_INVOCATION_INTENT", content)
        self.assertIn("public_remote_mcp", content)
        self.assertIn("MCP_ALLOWED_ORIGINS", content)
        self.assertIn("Access-Control-Request-Method", content)
        self.assertIn("http://localhost:3000", content)
        self.assertIn('"name":"search"', content)
        self.assertIn('"name":"fetch"', content)
        self.assertIn("remote MCP research", content)
        self.assertIn("req-fetch-uri", content)
        self.assertIn("req-fetch-both", content)
        self.assertIn("resourceId", content)
        self.assertIn("uri", content)
        self.assertIn('"code": -32602', content)
        self.assertIn('"code": -32001', content)
        self.assertIn('"category": "invalid_argument"', content)
        self.assertIn('"category": "unknown_tool"', content)
        self.assertIn("Minimal local runtime path", content)
        self.assertIn("Hosted-like local verification path", content)
        self.assertIn("docker compose -f infrastructure/local/compose.yaml up -d", content)
        self.assertIn("INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json", content)
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL", content)

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
            "MCP_SECRET_ACCESS_MODE",
            "MCP_SECRET_REFERENCE_NAMES",
            "PUBLIC_INVOCATION_INTENT",
            "MIN_INSTANCES",
            "MAX_INSTANCES",
            "CONCURRENCY",
            "TIMEOUT_SECONDS",
            "MCP_AUTH_TOKEN",
            "MCP_ALLOWED_ORIGINS",
            "MCP_ALLOW_ORIGINLESS_CLIENTS",
            "MCP_SESSION_CONNECTIVITY_MODEL",
            "INFRA_OUTPUTS_FILE",
        ):
            self.assertIn(f"{key}=", content)


if __name__ == "__main__":
    unittest.main()
