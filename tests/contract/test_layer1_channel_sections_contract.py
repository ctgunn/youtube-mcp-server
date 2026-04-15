import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import (
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
)


class Layer1ChannelSectionsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/112-channel-sections-list-wrapper/contracts")

    def _insert_contract_root(self) -> str:
        return os.path.abspath("specs/113-channel-sections-insert/contracts")

    def _update_contract_root(self) -> str:
        return os.path.abspath("specs/114-channel-sections-update/contracts")

    def _delete_contract_root(self) -> str:
        return os.path.abspath("specs/115-channel-sections-delete/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_filter_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-channel-sections-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channel-sections-list-auth-filter-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("mixed-auth behavior", wrapper_contract)
        self.assertIn("owner-scoped `mine` behavior", auth_filter_contract)
        self.assertIn("channelId", auth_filter_contract)

    def test_channel_sections_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channel_sections_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channelSections.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["exclusiveSelectors"], ("channelId", "id", "mine"))

    def test_contract_documents_selector_boundaries_lifecycle_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-channel-sections-list-auth-filter-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("mutually exclusive", auth_filter_contract)
        self.assertIn("missing selectors", auth_filter_contract)
        self.assertIn("zero channel section items", auth_filter_contract)
        self.assertIn("lifecycle metadata", auth_filter_contract)

    def test_insert_contract_artifacts_define_auth_and_section_type_guidance(self):
        root = self._insert_contract_root()
        with open(
            os.path.join(root, "layer1-channel-sections-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channel-sections-insert-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost (`50`)", wrapper_contract)
        self.assertIn("snippet.type", wrapper_contract)
        self.assertIn("OAuth-required", auth_write_contract)
        self.assertIn("singlePlaylist", auth_write_contract)
        self.assertIn("multiplePlaylists", auth_write_contract)
        self.assertIn("multipleChannels", auth_write_contract)
        self.assertIn("onBehalfOfContentOwner", auth_write_contract)

    def test_channel_sections_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channel_sections_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelSections.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])

    def test_insert_contract_documents_failure_boundaries_and_title_rules(self):
        with open(
            os.path.join(
                self._insert_contract_root(),
                "layer1-channel-sections-insert-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("duplicate", auth_write_contract)
        self.assertIn("title-required", auth_write_contract)
        self.assertIn("maximum number of sections", auth_write_contract)
        self.assertIn("normalized upstream create failures", auth_write_contract)

    def test_update_contract_artifacts_define_auth_and_writable_update_guidance(self):
        root = self._update_contract_root()
        with open(
            os.path.join(root, "layer1-channel-sections-update-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channel-sections-update-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost (`50`)", wrapper_contract)
        self.assertIn("identify the existing channel section", wrapper_contract)
        self.assertIn("OAuth-required", auth_write_contract)
        self.assertIn("onBehalfOfContentOwner", auth_write_contract)
        self.assertIn("duplicate", auth_write_contract)
        self.assertIn("title", auth_write_contract)

    def test_channel_sections_update_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channel_sections_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "channelSections.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])

    def test_update_contract_documents_failure_boundaries_and_identity_rules(self):
        with open(
            os.path.join(
                self._update_contract_root(),
                "layer1-channel-sections-update-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("identify the existing section", auth_write_contract)
        self.assertIn("duplicate", auth_write_contract)
        self.assertIn("normalized upstream update failures", auth_write_contract)
        self.assertIn("OAuth-required", auth_write_contract)

    def test_delete_contract_artifacts_define_auth_and_delete_guidance(self):
        root = self._delete_contract_root()
        with open(
            os.path.join(root, "layer1-channel-sections-delete-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channel-sections-delete-auth-delete-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("quota cost (`50`)", wrapper_contract)
        self.assertIn("one channel-section identifier", wrapper_contract)
        self.assertIn("OAuth-required", auth_delete_contract)
        self.assertIn("onBehalfOfContentOwner", auth_delete_contract)
        self.assertIn("onBehalfOfContentOwnerChannel", auth_delete_contract)
        self.assertIn("target-state failures", auth_delete_contract)

    def test_channel_sections_delete_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channel_sections_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "channelSections.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])

    def test_delete_contract_documents_failure_boundary_and_delegation_rules(self):
        with open(
            os.path.join(
                self._delete_contract_root(),
                "layer1-channel-sections-delete-auth-delete-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("malformed delete requests fail differently from auth problems", auth_delete_contract)
        self.assertIn("unavailable or inaccessible delete targets", auth_delete_contract)
        self.assertIn("normalized upstream delete failures", auth_delete_contract)
        self.assertIn("onBehalfOfContentOwnerChannel", auth_delete_contract)


if __name__ == "__main__":
    unittest.main()
