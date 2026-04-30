import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import (
    build_playlist_items_delete_wrapper,
    build_playlist_items_insert_wrapper,
    build_playlist_items_list_wrapper,
    build_playlist_items_update_wrapper,
)


class Layer1PlaylistItemsContractTests(unittest.TestCase):
    def _list_contract_root(self) -> str:
        return os.path.abspath("specs/132-playlist-items-list/contracts")

    def _insert_contract_root(self) -> str:
        return os.path.abspath("specs/133-playlist-items-insert/contracts")

    def _update_contract_root(self) -> str:
        return os.path.abspath("specs/134-playlist-items-update/contracts")

    def _delete_contract_root(self) -> str:
        return os.path.abspath("specs/135-playlist-items-delete/contracts")

    def test_contract_artifacts_define_wrapper_and_selector_mode_guidance(self):
        root = self._list_contract_root()
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
                self._list_contract_root(),
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

    def test_contract_artifacts_define_wrapper_and_auth_write_guidance_for_insert(self):
        root = self._insert_contract_root()
        with open(
            os.path.join(root, "layer1-playlist-items-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-playlist-items-insert-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_write_contract)
        self.assertIn("optional placement", auth_write_contract)
        self.assertIn("invalid_request", auth_write_contract)

    def test_playlist_items_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_playlist_items_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "playlistItems.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))

    def test_contract_documents_write_boundaries_and_failure_rules(self):
        with open(
            os.path.join(
                self._insert_contract_root(),
                "layer1-playlist-items-insert-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("unsupported writable parts", auth_write_contract)
        self.assertIn("target playlist identifier", auth_write_contract)
        self.assertIn("referenced resource identifier", auth_write_contract)
        self.assertIn("upstream create failures", auth_write_contract)

    def test_contract_artifacts_define_wrapper_and_auth_write_guidance_for_update(self):
        root = self._update_contract_root()
        with open(
            os.path.join(root, "layer1-playlist-items-update-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-playlist-items-update-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_write_contract)
        self.assertIn("optional placement", auth_write_contract)
        self.assertIn("upstream update failures", auth_write_contract)

    def test_playlist_items_update_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_playlist_items_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "playlistItems.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))

    def test_contract_documents_update_boundaries_and_failure_rules(self):
        with open(
            os.path.join(
                self._update_contract_root(),
                "layer1-playlist-items-update-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("target playlist-item identifier", auth_write_contract)
        self.assertIn("target playlist identifier", auth_write_contract)
        self.assertIn("referenced video identifier", auth_write_contract)
        self.assertIn("unsupported writable parts", auth_write_contract)
        self.assertIn("upstream update failures", auth_write_contract)

    def test_contract_artifacts_define_wrapper_and_auth_delete_guidance_for_delete(self):
        root = self._delete_contract_root()
        with open(
            os.path.join(root, "layer1-playlist-items-delete-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-playlist-items-delete-auth-delete-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("OAuth-only", auth_delete_contract)
        self.assertIn("invalid_request", auth_delete_contract)
        self.assertIn("upstream delete failures", auth_delete_contract)

    def test_playlist_items_delete_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_playlist_items_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "playlistItems.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))

    def test_contract_documents_delete_boundaries_and_failure_rules(self):
        with open(
            os.path.join(
                self._delete_contract_root(),
                "layer1-playlist-items-delete-auth-delete-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("target playlist-item identifier", auth_delete_contract)
        self.assertIn("unsupported delete fields", auth_delete_contract)
        self.assertIn("bulk deletion", auth_delete_contract)
        self.assertIn("upstream delete failures", auth_delete_contract)
