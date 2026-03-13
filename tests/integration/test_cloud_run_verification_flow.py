import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, write_verification_evidence


class CloudRunVerificationFlowIntegrationTests(unittest.TestCase):
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
        run = run_hosted_verification(self._revision(), requester=app.handle, evidence_path="artifacts/verify.txt")
        self.assertEqual(run.overall_result, "pass")
        self.assertEqual(len(run.checks), 5)
        self.assertTrue(all(check.result == "pass" for check in run.checks))

    def test_not_ready_app_fails_before_mcp_checks(self):
        app = create_app(env={"MCP_ENVIRONMENT": "staging"}, validate_startup=False)
        run = run_hosted_verification(self._revision(), requester=app.handle)
        self.assertEqual(run.overall_result, "fail")
        self.assertEqual([check.check_name for check in run.checks], ["liveness", "readiness"])

    def test_verification_evidence_is_written(self):
        app = create_app(env={"MCP_ENVIRONMENT": "dev"})
        run = run_hosted_verification(self._revision(), requester=app.handle)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_verification_evidence(os.path.join(tmp, "verification.txt"), run)
            content = path.read_text()
        self.assertIn("revisionName: rev-001", content)
        self.assertIn("checkName: liveness", content)
        self.assertIn("checkName: baseline-tool-call", content)


if __name__ == "__main__":
    unittest.main()
