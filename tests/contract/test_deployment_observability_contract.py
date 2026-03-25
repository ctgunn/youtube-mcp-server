import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import DeploymentRunRecord, RuntimeSettingsSnapshot, serialize_deployment_run


class DeploymentObservabilityContractTests(unittest.TestCase):
    def test_contract_document_lists_required_deployment_record_fields(self):
        content = Path(
            "specs/008-deployment-cloud-observability/contracts/deployment-observability-contract.md"
        ).read_text()
        for expected in (
            "success",
            "failed",
            "incomplete",
            "revisionName",
            "serviceUrl",
            "runtime identity",
            "request concurrency",
            "latencyMs",
        ):
            self.assertIn(expected, content)

    def test_serialized_deployment_record_contains_contract_fields(self):
        record = DeploymentRunRecord(
            deployment_id="deploy-1",
            executed_at="2026-03-15T00:00:00Z",
            outcome="success",
            summary="ok",
            revision_name="rev-001",
            service_url="https://example.run.app",
            runtime_settings=RuntimeSettingsSnapshot(
                service_name="youtube-mcp-server",
                environment_profile="staging",
                runtime_identity="svc@example.iam.gserviceaccount.com",
                min_instances=0,
                max_instances=2,
                concurrency=20,
                timeout_seconds=180,
                secret_reference_names=("YOUTUBE_API_KEY",),
                config_summary={"MCP_ENVIRONMENT": "staging"},
            ),
        )
        payload = serialize_deployment_run(record)
        self.assertEqual(
            payload.keys(),
            {
                "deploymentId",
                "executedAt",
                "outcome",
                "summary",
                "publicInvocationIntent",
                "revisionName",
                "serviceUrl",
                "connectionPoint",
                "failureStage",
                "remediation",
                "runtimeSettings",
            },
        )
        self.assertEqual(
            payload["runtimeSettings"].keys(),
            {
                "serviceName",
                "environmentProfile",
                "runtimeIdentity",
                "publicInvocationIntent",
                "serverImplementation",
                "appModule",
                "minInstances",
                "maxInstances",
                "concurrency",
                "timeoutSeconds",
                "secretReferenceNames",
                "configSummary",
            },
        )


if __name__ == "__main__":
    unittest.main()
