import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import classify_bootstrap_failure, serialize_workflow_stage  # noqa: E402


class HostedNetworkBootstrapFailureHelpersUnitTests(unittest.TestCase):
    def test_classifier_maps_reconcile_stage_to_network_failure_boundary(self):
        self.assertEqual(
            classify_bootstrap_failure(
                "infrastructure_reconcile",
                "Managed network bootstrap failed while reconciling infrastructure.",
            ),
            "network_reconcile_failure",
        )

    def test_classifier_maps_quality_gate_to_bootstrap_input_boundary(self):
        self.assertEqual(
            classify_bootstrap_failure("quality_gate", "Missing bootstrap prerequisites: GCP_REGION"),
            "bootstrap_input_failure",
        )

    def test_serialized_workflow_stage_includes_failure_boundary(self):
        payload = serialize_workflow_stage(
            type(
                "Stage",
                (),
                {
                    "stage_name": "infrastructure_reconcile",
                    "result": "fail",
                    "summary": "Managed network bootstrap failed while reconciling infrastructure.",
                    "artifact_path": None,
                    "failure_boundary": "network_reconcile_failure",
                },
            )()
        )
        self.assertEqual(payload["failureBoundary"], "network_reconcile_failure")


if __name__ == "__main__":
    unittest.main()
