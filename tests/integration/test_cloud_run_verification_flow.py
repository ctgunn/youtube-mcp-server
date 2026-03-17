import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request
from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, write_verification_evidence


class CloudRunVerificationFlowIntegrationTests(unittest.TestCase):
    def _hosted_requester(self, app, *, auth_token=None, origin=None):
        session_state = {"session_id": None}

        def _request(path, payload):
            if path in {"/health", "/ready"}:
                return execute_hosted_request(app, method="GET", path=path)
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            if origin:
                headers["Origin"] = origin
            if session_state["session_id"]:
                headers["MCP-Session-Id"] = session_state["session_id"]
            result = execute_hosted_request(
                app,
                method="POST",
                path=path,
                headers=headers,
                body=json.dumps(payload).encode("utf-8"),
            )
            session_state["session_id"] = result.headers.get("MCP-Session-Id", session_state["session_id"])
            return result

        return _request

    def _revision(self) -> HostedRevisionRecord:
        return HostedRevisionRecord(
            revision_name="rev-001",
            service_name="youtube-mcp-server",
            deployment_timestamp="2026-03-13T00:00:00Z",
            endpoint_url="https://example.com",
            runtime_identity="svc@example.iam.gserviceaccount.com",
            scaling_settings={"minInstances": 0, "maxInstances": 1, "concurrency": 80},
            timeout_seconds=300,
            status="created",
        )

    def test_ready_app_passes_full_hosted_verification(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        run = run_hosted_verification(
            self._revision(),
            requester=self._hosted_requester(app),
            evidence_path="artifacts/verify.txt",
        )
        self.assertEqual(run.overall_result, "pass")
        self.assertEqual(len(run.checks), 5)
        self.assertTrue(all(check.result == "pass" for check in run.checks))

    def test_not_ready_app_fails_before_mcp_checks(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        run = run_hosted_verification(self._revision(), requester=self._hosted_requester(app))
        self.assertEqual(run.overall_result, "fail")
        self.assertEqual([check.check_name for check in run.checks], ["liveness", "readiness"])

    def test_verification_evidence_is_written(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        run = run_hosted_verification(self._revision(), requester=self._hosted_requester(app))
        with tempfile.TemporaryDirectory() as tmp:
            path = write_verification_evidence(os.path.join(tmp, "verification.txt"), run)
            content = path.read_text()
        self.assertIn("revisionName: rev-001", content)
        self.assertIn("checkName: liveness", content)
        self.assertIn("checkName: baseline-tool-call", content)
        self.assertIn("runtimeIdentity: svc@example.iam.gserviceaccount.com", content)

    def test_hosted_route_payloads_remain_consistent_with_verification_inputs(self):
        ready_app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        local_ready = ready_app.handle("/ready", {})
        hosted_ready = execute_hosted_request(ready_app, method="GET", path="/ready")
        self.assertEqual(hosted_ready.status, 200)
        self.assertEqual(hosted_ready.payload["status"], local_ready["status"])

        not_ready_app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        local_not_ready = not_ready_app.handle("/ready", {})
        hosted_not_ready = execute_hosted_request(not_ready_app, method="GET", path="/ready")
        self.assertEqual(hosted_not_ready.status, 503)
        self.assertEqual(hosted_not_ready.payload["status"], local_not_ready["status"])

    def test_hosted_verification_uses_session_aware_transport(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        requester = self._hosted_requester(app)
        run = run_hosted_verification(self._revision(), requester=requester)
        baseline = [check for check in run.checks if check.check_name == "baseline-tool-call"][0]
        self.assertEqual(baseline.result, "pass")

    def test_verification_serialization_carries_runtime_identity(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        run = run_hosted_verification(self._revision(), requester=self._hosted_requester(app))
        self.assertEqual(run.revision_name, "rev-001")

    def test_secure_app_passes_verification_with_authentication(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev", "MCP_AUTH_TOKEN": "verify-token"})
        run = run_hosted_verification(
            self._revision(),
            requester=self._hosted_requester(app, auth_token="verify-token"),
        )
        self.assertEqual(run.overall_result, "pass")

    def test_secure_app_fails_verification_without_authentication(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev", "MCP_AUTH_TOKEN": "verify-token"})
        run = run_hosted_verification(self._revision(), requester=self._hosted_requester(app))
        self.assertEqual(run.overall_result, "fail")


if __name__ == "__main__":
    unittest.main()
