import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_subscriptions_list_wrapper


class Layer1SubscriptionsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/141-subscriptions-list/contracts")

    def test_contract_artifacts_define_wrapper_and_filter_mode_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-subscriptions-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-subscriptions-list-filter-modes-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            filter_modes_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("Mixed or conditional auth behavior", wrapper_contract)
        self.assertIn("`channelId` and `id` remain public-compatible selector paths", filter_modes_contract)
        self.assertIn("`mine`, `myRecentSubscribers`, and `mySubscribers` remain OAuth-backed selector paths", filter_modes_contract)

    def test_subscriptions_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_subscriptions_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "subscriptions.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["exclusiveSelectors"],
            ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers"),
        )

    def test_contract_documents_filter_boundaries_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-subscriptions-list-filter-modes-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            filter_modes_contract = handle.read()

        self.assertIn("exactly one supported selector", filter_modes_contract)
        self.assertIn("pageToken", filter_modes_contract)
        self.assertIn("malformed requests fail differently from access problems", filter_modes_contract)
        self.assertIn("valid empty results remain distinct", filter_modes_contract)


if __name__ == "__main__":
    unittest.main()
