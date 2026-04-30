import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_playlist_items_list_wrapper


class Layer1PlaylistItemsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/132-playlist-items-list/contracts")

    def test_contract_artifacts_define_wrapper_and_selector_mode_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-playlist-items-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-playlist-items-list-selector-modes-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_modes_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("API-key", wrapper_contract)
        self.assertIn("exactly one selector", selector_modes_contract)
        self.assertIn("pageToken", selector_modes_contract)
        self.assertIn("maxResults", selector_modes_contract)

    def test_playlist_items_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_playlist_items_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "playlistItems.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["exclusiveSelectors"], ("playlistId", "id"))

    def test_contract_documents_selector_boundaries_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-playlist-items-list-selector-modes-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_modes_contract = handle.read()

        self.assertIn("missing selectors", selector_modes_contract)
        self.assertIn("conflicting selectors", selector_modes_contract)
        self.assertIn("empty playlist-item results", selector_modes_contract)
        self.assertIn("unsupported paging", selector_modes_contract)
