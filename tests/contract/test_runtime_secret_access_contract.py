import unittest
from pathlib import Path


class RuntimeSecretAccessContractTests(unittest.TestCase):
    def test_contract_defines_runtime_identity_and_secret_bindings(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/runtime-secret-access-contract.md"
        ).read_text()
        self.assertIn("Runtime identity reference", content)
        self.assertIn("Required secret names", content)
        self.assertIn("reviewable secret-access bindings", content)

    def test_contract_requires_least_privilege_and_secret_safe_evidence(self):
        content = Path(
            "specs/022-hosted-dependency-wiring/contracts/runtime-secret-access-contract.md"
        ).read_text()
        self.assertIn("limited to the secret reads required", content)
        self.assertIn("Secret values must never appear", content)

    def test_operator_docs_call_out_runtime_secret_access_inputs(self):
        readme = Path("README.md").read_text()
        self.assertIn("MCP_SECRET_ACCESS_MODE", readme)
        self.assertIn("MCP_SECRET_REFERENCE_NAMES", readme)


if __name__ == "__main__":
    unittest.main()
