import unittest
from pathlib import Path


class CloudRunDocsExamplesIntegrationTests(unittest.TestCase):
    def test_scoped_guides_include_deploy_and_verify_commands(self):
        """Require scoped local, hosted, and architecture guides to remain linked.

        :return: ``None`` after checking essential operator and protocol guidance.
        """
        content = "\n".join(
            (
                Path("docs/architecture.md").read_text(),
                Path("docs/local-development.md").read_text(),
                Path("docs/engineering.md").read_text(),
                Path("docs/hosted-deployment.md").read_text(),
                Path("infrastructure/gcp/README.md").read_text(),
            )
        )
        self.assertIn("scripts/deploy_cloud_run.sh", content)
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
        self.assertIn("bash scripts/dev_local.sh", content)
        self.assertIn("LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh", content)
        self.assertIn(".env.local", content)
        self.assertIn("INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json", content)
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL", content)
        self.assertIn("Terraform-managed hosted network layer", content)
        self.assertIn("session egress reference", content)

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
