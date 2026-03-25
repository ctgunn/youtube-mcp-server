import unittest
from pathlib import Path


class CloudRunPublicAccessContractTests(unittest.TestCase):
    def test_contract_defines_public_and_private_intents(self):
        content = Path(
            "specs/021-cloud-run-reachability/contracts/cloud-run-public-access-contract.md"
        ).read_text()
        self.assertIn("public_remote_mcp", content)
        self.assertIn("private_only", content)

    def test_contract_preserves_separation_from_mcp_authentication(self):
        content = Path(
            "specs/021-cloud-run-reachability/contracts/cloud-run-public-access-contract.md"
        ).read_text()
        self.assertIn("Cloud Run public invocation determines whether the hosted service can be reached at all.", content)
        self.assertIn("MCP bearer-token authentication determines whether a reachable caller may use protected `/mcp` routes.", content)

    def test_operator_docs_call_out_public_invocation_intent(self):
        readme = Path("README.md").read_text()
        self.assertIn("PUBLIC_INVOCATION_INTENT", readme)
        self.assertIn("public_remote_mcp", readme)


if __name__ == "__main__":
    unittest.main()
