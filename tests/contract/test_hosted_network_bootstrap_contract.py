import unittest
from pathlib import Path


class HostedNetworkBootstrapContractTests(unittest.TestCase):
    def test_pipeline_contract_requires_managed_network_reconcile_before_deploy(self):
        content = Path(
            "specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-pipeline-contract.md"
        ).read_text()
        for expected in (
            "cloudbuild.yaml",
            ".github/workflows/hosted-deploy.yml",
            "managed hosted network layer",
            "infrastructure_reconcile",
            "deploy",
            "must not begin until",
        ):
            self.assertIn(expected, content)

    def test_failure_boundary_contract_lists_required_failure_classes(self):
        content = Path(
            "specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-failure-boundary-contract.md"
        ).read_text()
        for expected in (
            "bootstrap_input_failure",
            "network_reconcile_failure",
            "deployment_failure",
            "hosted_verification_failure",
            "operator-visible failure classes",
        ):
            self.assertIn(expected, content)

    def test_prerequisite_contract_excludes_recurring_manual_network_provisioning(self):
        content = Path(
            "specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-prerequisite-contract.md"
        ).read_text()
        for expected in (
            "one-time external prerequisites",
            "operator-managed secret values",
            "must not require a separate recurring manual network provisioning sequence",
            "local development",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
