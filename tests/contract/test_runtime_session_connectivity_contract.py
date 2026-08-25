import unittest
from pathlib import Path


class RuntimeSessionConnectivityContractTests(unittest.TestCase):
    def test_contract_defines_session_backend_and_connectivity_model(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/runtime-session-connectivity-contract.md"
        ).read_text()
        self.assertIn("durable session backend", content)
        self.assertIn("provider-specific connectivity path", content)
        self.assertIn("session-connectivity failures", content)

    def test_contract_requires_connectivity_and_continuation_proof(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/runtime-session-connectivity-contract.md"
        ).read_text()
        self.assertIn("backend is reachable", content)
        self.assertIn("hosted session continuation flow", content)

    def test_operator_docs_call_out_session_connectivity_inputs(self):
        """Require the GCP runbook to cover durable-session infrastructure inputs.

        :return: ``None`` after checking session-connectivity documentation.
        """
        content = "\n".join(
            (
                Path("docs/architecture.md").read_text(),
                Path("infrastructure/gcp/README.md").read_text(),
            )
        )
        self.assertIn("MCP_SESSION_CONNECTIVITY_MODEL", content)
        self.assertIn("MCP_SESSION_STORE_URL", content)
        self.assertIn("Terraform-managed hosted network layer", content)
        self.assertIn("session egress reference", content)


if __name__ == "__main__":
    unittest.main()
