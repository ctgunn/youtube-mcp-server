import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_captions_list_wrapper


class Layer1CaptionsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/104-captions-list/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_selector_guidance(self):
        root = self._feature_contract_root()
        with open(os.path.join(root, "layer1-captions-wrapper-contract.md"), "r", encoding="utf-8") as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-captions-auth-selector-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_selector_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("videoId", wrapper_contract)
        self.assertIn("OAuth", auth_selector_contract)
        self.assertIn("onBehalfOfContentOwner", auth_selector_contract)
        self.assertIn("zero caption tracks", auth_selector_contract)

    def test_captions_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_captions_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "captions")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "captions.list")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["exclusiveSelectors"], ("videoId", "id"))

    def test_captions_contract_documents_supported_selectors(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-captions-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("videoId", wrapper_contract)
        self.assertIn("id", wrapper_contract)

    def test_captions_contract_documents_delegation_context(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-captions-auth-selector-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_selector_contract = handle.read()

        self.assertIn("delegation context", auth_selector_contract)
        self.assertIn("onBehalfOfContentOwner", auth_selector_contract)
        self.assertIn("authorized access", auth_selector_contract)

    def test_captions_contract_documents_empty_results_as_success(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-captions-auth-selector-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_selector_contract = handle.read()

        self.assertIn("zero caption tracks", auth_selector_contract)
        self.assertIn("successful but empty collection", auth_selector_contract)


if __name__ == "__main__":
    unittest.main()
