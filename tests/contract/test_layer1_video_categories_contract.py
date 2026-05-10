import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_video_categories_list_wrapper


class Layer1VideoCategoriesContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/146-video-categories-list/contracts")

    def test_contract_artifacts_define_wrapper_and_selector_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-video-categories-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-video-categories-list-selector-region-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("exactly one selector from `id` or `regionCode`", wrapper_contract)
        self.assertIn("region-scoped category browsing", selector_contract)
        self.assertIn("successful empty results", selector_contract)

    def test_video_categories_list_wrapper_review_surface_exposes_identity_quota_and_selectors(self):
        review_surface = build_video_categories_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videoCategories")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videoCategories.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["optionalFields"], ("id", "regionCode", "hl"))
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "regionCode"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_contract_documents_request_boundaries_and_invalid_request_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-video-categories-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` is required", wrapper_contract)
        self.assertIn("`hl` is optional guidance", wrapper_contract)
        self.assertIn("undocumented modifiers", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_contract_documents_selector_conflict_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-video-categories-list-selector-region-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("may not supply both `id` and `regionCode`", selector_contract)
        self.assertIn("successful empty results", selector_contract)
        self.assertIn("invalid requests remain separate", selector_contract)
