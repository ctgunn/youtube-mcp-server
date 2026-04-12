import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_channel_sections_list_wrapper


class Layer1ChannelSectionsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/112-channel-sections-list-wrapper/contracts")

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


if __name__ == "__main__":
    unittest.main()
