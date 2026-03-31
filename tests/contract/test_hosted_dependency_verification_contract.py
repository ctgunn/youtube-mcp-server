import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, serialize_verification_run


class HostedDependencyVerificationContractTests(unittest.TestCase):
    def _revision(self) -> HostedRevisionRecord:
        return HostedRevisionRecord(
            revision_name="rev-022",
            service_name="youtube-mcp-server",
            deployment_timestamp="2026-03-24T00:00:00Z",
            endpoint_url="https://example.com",
            runtime_identity="svc@example.iam.gserviceaccount.com",
            scaling_settings={"minInstances": 0, "maxInstances": 1, "concurrency": 20},
            timeout_seconds=180,
            status="created",
            secret_reference_names=("YOUTUBE_API_KEY", "MCP_AUTH_TOKEN"),
            secret_access_mode="secret_manager_env",
            session_backend="redis",
            session_store_url="redis://10.0.0.3:6379/0",
            session_connectivity_model="serverless_vpc_connector",
            session_network_reference="projects/project-id/global/networks/youtube-mcp-server-staging-network",
            session_subnet_reference="projects/project-id/regions/us-central1/subnetworks/youtube-mcp-server-staging-subnet",
            session_connector_reference="projects/project-id/locations/us-central1/connectors/youtube-mcp-server-staging-connector",
        )

    def test_contract_defines_dependency_verification_order(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/hosted-dependency-verification-contract.md"
        ).read_text()
        self.assertIn("1. `deployment-evidence`", content)
        self.assertIn("2. `secret-access`", content)
        self.assertIn("4. `session-connectivity`", content)
        self.assertIn("5. `session-continuation`", content)

    def test_contract_requires_secret_and_session_failure_layers(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/hosted-dependency-verification-contract.md"
        ).read_text()
        self.assertIn("failure layer (`secret_access` or `session_connectivity`)", content)
        self.assertIn("remediation", content)

    def test_verifier_runs_dependency_checks_before_session_continuation(self):
        payloads = {
            "/": {"statusCode": 404},
            "/ready": {
                "status": "ready",
                "checks": {
                    "configuration": "pass",
                    "secrets": "pass",
                    "runtime": "pass",
                    "sessionDurability": "pass",
                },
                "statusCode": 200,
            },
            "/health": {"status": "ok", "statusCode": 200},
            "initialize": {
                "jsonrpc": "2.0",
                "id": "verify-init",
                "result": {"capabilities": {"tools": {"listChanged": False}}},
                "statusCode": 200,
            },
            "tools/list": {
                "jsonrpc": "2.0",
                "id": "verify-list",
                "result": {"tools": [{"name": "search"}, {"name": "fetch"}]},
                "statusCode": 200,
            },
        }

        def requester(path, payload):
            if path == "/":
                return payloads["/"]
            if path == "/health":
                return payloads["/health"]
            if path == "/ready":
                return payloads["/ready"]
            if payload["method"] == "initialize":
                return payloads["initialize"]
            if payload["method"] == "tools/list":
                return payloads["tools/list"]
            return {
                "jsonrpc": "2.0",
                "id": payload.get("id", "call"),
                "result": {
                    "content": [{"type": "text", "structuredContent": {"results": [{"resourceId": "r1", "uri": "https://example.com/r1"}]}}],
                    "isError": False,
                },
                "statusCode": 200,
                "_sseEvents": [{"id": "evt-1", "data": "{\"jsonrpc\":\"2.0\",\"result\":{}}"}],
            }

        run = run_hosted_verification(self._revision(), requester=requester)
        self.assertEqual(run.checks[0].check_name, "deployment-evidence")
        self.assertEqual(run.checks[1].check_name, "reachability")
        self.assertEqual(run.checks[2].check_name, "liveness")
        self.assertEqual(run.checks[3].check_name, "secret-access")
        self.assertEqual(run.checks[5].check_name, "session-connectivity")

    def test_verifier_serialization_preserves_dependency_failure_layers(self):
        def requester(path, payload):
            if path == "/":
                return {"statusCode": 404}
            if path == "/health":
                return {"status": "ok", "statusCode": 200}
            if path == "/ready":
                return {
                    "status": "not_ready",
                    "checks": {
                        "configuration": "fail",
                        "secrets": "fail",
                        "runtime": "fail",
                        "sessionDurability": "pass",
                    },
                    "reason": {"code": "SECRET_ACCESS_UNAVAILABLE"},
                    "statusCode": 503,
                }
            return {}

        run = run_hosted_verification(self._revision(), requester=requester)
        payload = serialize_verification_run(run)
        failing = [check for check in payload["checks"] if check["result"] == "fail"][0]
        self.assertEqual(failing["failureLayer"], "secret_access")
        self.assertIn("remediation", failing)


if __name__ == "__main__":
    unittest.main()
