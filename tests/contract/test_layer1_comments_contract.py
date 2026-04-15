import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_comments_list_wrapper


class Layer1CommentsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/116-comments-list/contracts")

    def test_contract_artifacts_define_wrapper_and_lookup_access_guidance(self):
        root = self._feature_contract_root()
        with open(os.path.join(root, "layer1-comments-list-wrapper-contract.md"), "r", encoding="utf-8") as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-comments-list-lookup-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            lookup_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`id` and `parentId`", wrapper_contract)
        self.assertIn("direct comment lookup", lookup_contract)
        self.assertIn("reply lookup", lookup_contract)
        self.assertIn("successful retrieval with no matches", lookup_contract)

    def test_comments_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_comments_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "comments.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "parentId"))

    def test_contract_documents_selector_boundaries_and_optional_modifier_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-comments-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("exactly one selector", wrapper_contract)
        self.assertIn("pageToken", wrapper_contract)
        self.assertIn("maxResults", wrapper_contract)
        self.assertIn("textFormat", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_contract_documents_invalid_combination_and_empty_result_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-comments-list-lookup-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            lookup_contract = handle.read()

        self.assertIn("mutually exclusive", lookup_contract)
        self.assertIn("missing selectors", lookup_contract)
        self.assertIn("zero comment items", lookup_contract)
        self.assertIn("access mismatches", lookup_contract)


if __name__ == "__main__":
    unittest.main()
