import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import deployment_input_from_iac_outputs, load_iac_outputs_file


class IaCFoundationInputsUnitTests(unittest.TestCase):
    def _terraform_outputs(self):
        return {
            "project_id": {"value": "project-id"},
            "region": {"value": "us-central1"},
            "environment": {"value": "staging"},
            "service_name": {"value": "youtube-mcp-server"},
            "service_account_email": {"value": "svc@example.iam.gserviceaccount.com"},
            "secret_reference_names": {"value": ["YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"]},
            "mcp_auth_required": {"value": True},
            "mcp_allowed_origins": {"value": "https://chat.openai.com"},
            "mcp_allow_originless_clients": {"value": True},
            "mcp_session_backend": {"value": "redis"},
            "mcp_session_store_url": {"value": "redis://10.0.0.3:6379/0"},
            "mcp_session_durability_required": {"value": True},
            "mcp_session_ttl_seconds": {"value": 1800},
            "mcp_session_replay_ttl_seconds": {"value": 300},
            "min_instances": {"value": 0},
            "max_instances": {"value": 2},
            "concurrency": {"value": 20},
            "timeout_seconds": {"value": 180},
        }

    def test_load_iac_outputs_file_reads_terraform_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "outputs.json"
            path.write_text(json.dumps(self._terraform_outputs()))
            payload = load_iac_outputs_file(path)
        self.assertEqual(payload["project_id"]["value"], "project-id")
        self.assertEqual(payload["service_account_email"]["value"], "svc@example.iam.gserviceaccount.com")

    def test_deployment_input_from_iac_outputs_maps_expected_values(self):
        settings = deployment_input_from_iac_outputs(
            self._terraform_outputs(),
            image_reference="us-docker.pkg.dev/project/app/image:sha",
        )
        self.assertEqual(settings.project_id, "project-id")
        self.assertEqual(settings.region, "us-central1")
        self.assertEqual(settings.environment, "staging")
        self.assertEqual(settings.service_name, "youtube-mcp-server")
        self.assertEqual(settings.runtime_identity, "svc@example.iam.gserviceaccount.com")
        self.assertEqual(settings.secret_references, ("YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"))
        self.assertEqual(settings.config_values["MCP_ALLOWED_ORIGINS"], "https://chat.openai.com")
        self.assertEqual(settings.config_values["MCP_SESSION_BACKEND"], "redis")
        self.assertEqual(settings.config_values["MCP_SESSION_STORE_URL"], "redis://10.0.0.3:6379/0")
        self.assertEqual(settings.timeout_seconds, 180)
        self.assertEqual(settings.validate(), [])

    def test_explicit_inputs_override_iac_outputs(self):
        settings = deployment_input_from_iac_outputs(
            self._terraform_outputs(),
            image_reference="override-image",
            explicit_values={"MAX_INSTANCES": "5", "MCP_ALLOWED_ORIGINS": "https://override.example"},
        )
        self.assertEqual(settings.max_instances, 5)
        self.assertEqual(settings.config_values["MCP_ALLOWED_ORIGINS"], "https://override.example")
        self.assertEqual(settings.image_reference, "override-image")


if __name__ == "__main__":
    unittest.main()
