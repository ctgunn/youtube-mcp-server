import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import build_deploy_command, deployment_input_from_mapping
from mcp_server.infrastructure_contract import (
    is_supported_access_failure_layer,
    is_supported_dependency_failure_layer,
    is_supported_public_invocation_intent,
)


class CloudRunConfigUnitTests(unittest.TestCase):
    def test_dev_deployment_inputs_are_valid(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "dev",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "us-docker.pkg.dev/project/app/image:sha",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "2",
                "CONCURRENCY": "80",
                "TIMEOUT_SECONDS": "300",
            }
        )
        self.assertEqual(settings.validate(), [])

    def test_staging_requires_youtube_api_key_secret_reference(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "staging",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "10",
                "TIMEOUT_SECONDS": "120",
            }
        )
        self.assertIn("YOUTUBE_API_KEY secret reference is required for staging and prod", settings.validate())
        self.assertIn("MCP_AUTH_TOKEN secret reference is required for staging and prod", settings.validate())

    def test_build_deploy_command_contains_required_runtime_flags(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "prod",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "1",
                "MAX_INSTANCES": "3",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
                "SECRET_REFERENCES": "YOUTUBE_API_KEY,MCP_AUTH_TOKEN",
                "MCP_SECRET_ACCESS_MODE": "secret_manager_env",
                "MCP_SECRET_REFERENCE_NAMES": "YOUTUBE_API_KEY,MCP_AUTH_TOKEN",
                "MCP_SESSION_BACKEND": "redis",
                "MCP_SESSION_STORE_URL": "redis://10.0.0.3:6379/0",
                "MCP_SESSION_CONNECTIVITY_MODEL": "serverless_vpc_connector",
            }
        )
        command = build_deploy_command(settings)
        rendered = " ".join(command)
        self.assertIn("--service-account svc@example.iam.gserviceaccount.com", rendered)
        self.assertIn("--min-instances 1", rendered)
        self.assertIn("--max-instances 3", rendered)
        self.assertIn("--concurrency 20", rendered)
        self.assertIn("--timeout 180", rendered)
        self.assertIn("--set-secrets YOUTUBE_API_KEY=YOUTUBE_API_KEY:latest,MCP_AUTH_TOKEN=MCP_AUTH_TOKEN:latest", rendered)
        self.assertIn("MCP_SERVER_IMPLEMENTATION=uvicorn", rendered)
        self.assertIn("MCP_ASGI_APP=mcp_server.cloud_run_entrypoint:app", rendered)
        self.assertIn("MCP_SECRET_ACCESS_MODE=secret_manager_env", rendered)
        self.assertIn("MCP_SECRET_REFERENCE_NAMES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN", rendered)
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL=serverless_vpc_connector", rendered)

    def test_invalid_scaling_inputs_raise(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "dev",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "2",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "20",
                "TIMEOUT_SECONDS": "180",
            }
        )
        with self.assertRaisesRegex(ValueError, "max_instances must be >= min_instances"):
            build_deploy_command(settings)

    def test_public_invocation_intent_helper_accepts_supported_values(self):
        self.assertTrue(is_supported_public_invocation_intent("public_remote_mcp"))
        self.assertTrue(is_supported_public_invocation_intent("private-only"))
        self.assertFalse(is_supported_public_invocation_intent("internet-open"))

    def test_access_failure_layer_helper_accepts_supported_values(self):
        self.assertTrue(is_supported_access_failure_layer("cloud_platform"))
        self.assertTrue(is_supported_access_failure_layer("mcp-application"))
        self.assertFalse(is_supported_access_failure_layer("network_edge"))

    def test_dependency_failure_layer_helper_accepts_supported_values(self):
        self.assertTrue(is_supported_dependency_failure_layer("secret_access"))
        self.assertTrue(is_supported_dependency_failure_layer("session-connectivity"))
        self.assertFalse(is_supported_dependency_failure_layer("runtime"))

    def test_public_invocation_intent_defaults_private_only(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "dev",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "10",
                "TIMEOUT_SECONDS": "120",
            }
        )
        self.assertEqual(settings.public_invocation_intent, "private_only")

    def test_invalid_public_invocation_intent_is_rejected(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "dev",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "10",
                "TIMEOUT_SECONDS": "120",
                "PUBLIC_INVOCATION_INTENT": "implicit-default",
            }
        )
        self.assertIn("public_invocation_intent must be one of public_remote_mcp, private_only", settings.validate())

    def test_redis_backend_requires_session_store_url(self):
        settings = deployment_input_from_mapping(
            {
                "MCP_ENVIRONMENT": "dev",
                "SERVICE_NAME": "youtube-mcp-server",
                "IMAGE_REFERENCE": "image",
                "SERVICE_ACCOUNT_EMAIL": "svc@example.iam.gserviceaccount.com",
                "REGION": "us-central1",
                "PROJECT_ID": "project-id",
                "MIN_INSTANCES": "0",
                "MAX_INSTANCES": "1",
                "CONCURRENCY": "10",
                "TIMEOUT_SECONDS": "120",
                "MCP_SESSION_BACKEND": "redis",
            }
        )
        self.assertIn("MCP_SESSION_STORE_URL is required when MCP_SESSION_BACKEND=redis", settings.validate())


if __name__ == "__main__":
    unittest.main()
