import unittest
from pathlib import Path


class HostedNetworkBootstrapDocsIntegrationTests(unittest.TestCase):
    def test_hosted_guide_documents_managed_network_bootstrap_boundary(self):
        """Require the scoped hosted guide to describe the network boundary.

        :return: ``None`` after checking bootstrap failure guidance.
        """
        content = Path("docs/hosted-deployment.md").read_text()
        for expected in (
            "managed network bootstrap",
            "network reconciliation happens before deploy",
            "bootstrap_input_failure",
            "network_reconcile_failure",
            "one-time bootstrap inputs",
        ):
            self.assertIn(expected, content)

    def test_gcp_readme_documents_non_network_bootstrap_boundary(self):
        content = Path("infrastructure/gcp/README.md").read_text()
        for expected in (
            "managed hosted network layer remains automation-managed",
            "remaining one-time bootstrap inputs are non-network prerequisites",
            "network_reconcile_failure",
            "recurring manual network provisioning",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
