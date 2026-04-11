import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_channels_list_wrapper


class Layer1ChannelsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/110-channels-list-wrapper/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_filter_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-channels-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channels-list-auth-filter-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("mixed-auth behavior", wrapper_contract)
        self.assertIn("owner-scoped retrieval path through `mine`", auth_filter_contract)
        self.assertIn("username-style lookup", auth_filter_contract)

    def test_channels_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channels_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channels")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channels.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["exclusiveSelectors"],
            ("id", "mine", "forHandle", "forUsername"),
        )

    def test_contract_documents_selector_boundaries_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-channels-list-auth-filter-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("mutually exclusive", auth_filter_contract)
        self.assertIn("missing selectors", auth_filter_contract)
        self.assertIn("conflicting selectors", auth_filter_contract)
        self.assertIn("zero channel items", auth_filter_contract)


if __name__ == "__main__":
    unittest.main()
