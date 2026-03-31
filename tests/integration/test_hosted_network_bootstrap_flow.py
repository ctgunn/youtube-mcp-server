import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import (  # noqa: E402
    HostedDeploymentWorkflowStage,
    classify_bootstrap_failure,
    serialize_workflow_run,
)


class HostedNetworkBootstrapFlowIntegrationTests(unittest.TestCase):
    def test_cloud_build_declares_managed_network_reconcile_before_deploy(self):
        content = Path("cloudbuild.yaml").read_text()
        reconcile_marker = "Reconcile managed network bootstrap and infrastructure"
        deploy_marker = "Deploy hosted revision"
        self.assertIn(reconcile_marker, content)
        self.assertIn(deploy_marker, content)
        self.assertLess(content.index(reconcile_marker), content.index(deploy_marker))

    def test_github_workflow_declares_managed_network_reconcile_before_deploy(self):
        content = Path(".github/workflows/hosted-deploy.yml").read_text()
        reconcile_marker = "Reconcile managed network bootstrap and infrastructure"
        deploy_marker = "Deploy hosted revision"
        self.assertIn(reconcile_marker, content)
        self.assertIn(deploy_marker, content)
        self.assertLess(content.index(reconcile_marker), content.index(deploy_marker))

    def test_workflow_summary_reports_bootstrap_failure_boundary(self):
        payload = serialize_workflow_run(
            "main",
            "abc123",
            [
                HostedDeploymentWorkflowStage("quality_gate", "pass", "ok"),
                HostedDeploymentWorkflowStage(
                    "infrastructure_reconcile",
                    "fail",
                    "Managed network bootstrap failed while reconciling infrastructure.",
                ),
            ],
        )
        self.assertEqual(payload["overallResult"], "fail")
        self.assertEqual(payload["firstFailedStage"], "infrastructure_reconcile")
        self.assertEqual(payload["firstFailedBoundary"], "network_reconcile_failure")

    def test_failure_classifier_distinguishes_bootstrap_and_deploy_failures(self):
        self.assertEqual(
            classify_bootstrap_failure("quality_gate", "Missing bootstrap prerequisites: GCP_PROJECT_ID"),
            "bootstrap_input_failure",
        )
        self.assertEqual(
            classify_bootstrap_failure(
                "infrastructure_reconcile",
                "Managed network bootstrap failed while reconciling infrastructure.",
            ),
            "network_reconcile_failure",
        )
        self.assertEqual(
            classify_bootstrap_failure("deploy", "Deployment command failed."),
            "deployment_failure",
        )
        self.assertEqual(
            classify_bootstrap_failure("hosted_verification", "Hosted verification reported fail."),
            "hosted_verification_failure",
        )


if __name__ == "__main__":
    unittest.main()
