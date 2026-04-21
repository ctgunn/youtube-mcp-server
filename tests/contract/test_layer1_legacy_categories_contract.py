import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_guide_categories_list_wrapper


class Layer1LegacyCategoriesContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/123-guide-categories-list/contracts")

    def test_contract_artifacts_define_wrapper_and_lifecycle_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-guide-categories-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-guide-categories-list-region-lifecycle-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            lifecycle_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`part` plus `regionCode`", wrapper_contract)
        self.assertIn("deprecated lifecycle", lifecycle_contract)
        self.assertIn("successful empty results", lifecycle_contract)

    def test_guide_categories_list_wrapper_review_surface_exposes_identity_quota_and_lifecycle(self):
        review_surface = build_guide_categories_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "guideCategories")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "guideCategories.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "regionCode"))
        self.assertEqual(review_surface["lifecycleState"], "deprecated")

    def test_contract_documents_request_boundaries_and_invalid_request_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-guide-categories-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` and `regionCode` are required", wrapper_contract)
        self.assertIn("undocumented modifiers", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_contract_documents_lifecycle_aware_failure_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-guide-categories-list-region-lifecycle-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            lifecycle_contract = handle.read()

        self.assertIn("lifecycle-aware unavailable", lifecycle_contract)
        self.assertIn("empty-result", lifecycle_contract)
        self.assertIn("missing `part` or `regionCode`", lifecycle_contract)
