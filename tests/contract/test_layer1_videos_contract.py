import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_videos_list_wrapper


class Layer1VideosContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/147-videos-list/contracts")

    def test_contract_artifacts_define_wrapper_and_selector_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-videos-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-list-selector-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("exactly one selector from `id`, `chart`, or `myRating`", wrapper_contract)
        self.assertIn("mixed-auth behavior", selector_contract)
        self.assertIn("successful empty results", selector_contract)

    def test_videos_list_wrapper_review_surface_exposes_identity_quota_and_selectors(self):
        review_surface = build_videos_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videos.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"],
            ("id", "chart", "myRating", "pageToken", "maxResults", "regionCode", "videoCategoryId"),
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "chart", "myRating"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_contract_documents_request_boundaries_and_auth_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-videos-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` is required", wrapper_contract)
        self.assertIn("`pageToken` and `maxResults` are supported only for collection-style retrieval", wrapper_contract)
        self.assertIn("`regionCode` and `videoCategoryId` are chart-oriented refinements", wrapper_contract)
        self.assertIn("auth_condition_note", wrapper_contract)

    def test_contract_documents_selector_conflict_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-videos-list-selector-auth-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("may not supply more than one selector", selector_contract)
        self.assertIn("chart-only refinements", selector_contract)
        self.assertIn("successful empty results", selector_contract)
        self.assertIn("invalid requests remain separate", selector_contract)
