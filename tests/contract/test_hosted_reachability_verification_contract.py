import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, serialize_verification_run


class HostedReachabilityVerificationContractTests(unittest.TestCase):
    def _revision(self) -> HostedRevisionRecord:
        return HostedRevisionRecord(
            revision_name="rev-001",
            service_name="youtube-mcp-server",
            deployment_timestamp="2026-03-24T00:00:00Z",
            endpoint_url="https://example.com",
            runtime_identity="svc@example.iam.gserviceaccount.com",
            scaling_settings={"minInstances": 0, "maxInstances": 1, "concurrency": 20},
            timeout_seconds=180,
            status="created",
        )

    def test_contract_defines_reachability_first_verification_order(self):
        content = Path(
            "specs/021-cloud-run-reachability/contracts/hosted-reachability-verification-contract.md"
        ).read_text()
        self.assertIn("1. `reachability`", content)
        self.assertIn("4. `mcp-authenticated`", content)
        self.assertIn("5. `mcp-denied`", content)

    def test_contract_requires_failure_layer_evidence(self):
        content = Path(
            "specs/021-cloud-run-reachability/contracts/hosted-reachability-verification-contract.md"
        ).read_text()
        self.assertIn("failure layer (`cloud_platform` or `mcp_application`)", content)
        self.assertIn("whether the request reached the application layer", content)

    def test_verifier_runs_reachability_before_liveness(self):
        payloads = {
            "/": {"statusCode": 404},
            "/health": {"status": "ok", "statusCode": 200},
            "/ready": {"status": "ready", "statusCode": 200},
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
            if path != "/mcp":
                return payloads[path]
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
        self.assertEqual(run.checks[0].check_name, "reachability")
        self.assertEqual(run.checks[1].check_name, "liveness")

    def test_verifier_distinguishes_cloud_and_mcp_failure_layers(self):
        def cloud_denied(path, payload):
            if path == "/":
                return {"statusCode": 403}
            return {"status": "ok", "statusCode": 200}

        cloud_run = run_hosted_verification(self._revision(), requester=cloud_denied)
        cloud_payload = serialize_verification_run(cloud_run)
        self.assertEqual(cloud_payload["checks"][0]["failureLayer"], "cloud_platform")
        self.assertFalse(cloud_payload["checks"][0]["requestReachedApplication"])

        def mcp_denied(path, payload):
            if path == "/":
                return {"statusCode": 404}
            if path == "/health":
                return {"status": "ok", "statusCode": 200}
            if path == "/ready":
                return {"status": "ready", "statusCode": 200}
            return {
                "jsonrpc": "2.0",
                "id": "verify-init",
                "error": {"code": -32002, "data": {"category": "unauthenticated"}},
                "statusCode": 401,
            }

        mcp_run = run_hosted_verification(self._revision(), requester=mcp_denied)
        mcp_payload = serialize_verification_run(mcp_run)
        failing = [check for check in mcp_payload["checks"] if check["result"] == "fail"][0]
        self.assertEqual(failing["failureLayer"], "mcp_application")
        self.assertTrue(failing["requestReachedApplication"])
        self.assertIn("remediation", failing)


if __name__ == "__main__":
    unittest.main()
