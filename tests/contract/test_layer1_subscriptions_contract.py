import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import (
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
)


class Layer1SubscriptionsContractTests(unittest.TestCase):
    def _feature_list_contract_root(self) -> str:
        return os.path.abspath("specs/141-subscriptions-list/contracts")

    def _feature_insert_contract_root(self) -> str:
        return os.path.abspath("specs/142-subscriptions-insert/contracts")

    def _feature_delete_contract_root(self) -> str:
        return os.path.abspath("specs/143-subscriptions-delete/contracts")

    def test_contract_artifacts_define_wrapper_and_filter_mode_guidance(self):
        root = self._feature_list_contract_root()
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
                self._feature_list_contract_root(),
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

    def test_contract_artifacts_define_wrapper_and_auth_write_guidance_for_subscriptions_insert(self):
        root = self._feature_insert_contract_root()
        with open(
            os.path.join(root, "layer1-subscriptions-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-subscriptions-insert-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_write_contract)
        self.assertIn("body.snippet.resourceId.channelId", auth_write_contract)
        self.assertIn("part=snippet", auth_write_contract)

    def test_subscriptions_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_subscriptions_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "subscriptions.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/subscriptions")

    def test_contract_documents_subscription_insert_failure_boundaries(self):
        with open(
            os.path.join(
                self._feature_insert_contract_root(),
                "layer1-subscriptions-insert-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("invalid_request", auth_write_contract)
        self.assertIn("duplicate or ineligible target failures", auth_write_contract)
        self.assertIn("normalized upstream create failures", auth_write_contract)
        self.assertIn("successful subscription creation outcomes", auth_write_contract)

    def test_contract_artifacts_define_wrapper_and_auth_delete_guidance_for_subscriptions_delete(self):
        root = self._feature_delete_contract_root()
        with open(
            os.path.join(root, "layer1-subscriptions-delete-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-subscriptions-delete-auth-delete-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("authorized access", wrapper_contract)
        self.assertIn("OAuth-only", auth_delete_contract)
        self.assertIn("target subscription identifier", auth_delete_contract)
        self.assertIn("does not require `part` or `body`", auth_delete_contract)

    def test_subscriptions_delete_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_subscriptions_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "subscriptions.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/subscriptions")

    def test_contract_documents_subscription_delete_failure_boundaries(self):
        with open(
            os.path.join(
                self._feature_delete_contract_root(),
                "layer1-subscriptions-delete-auth-delete-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("invalid_request", auth_delete_contract)
        self.assertIn("upstream delete failures", auth_delete_contract)
        self.assertIn("successful deletion acknowledgments", auth_delete_contract)
        self.assertIn("already removed", auth_delete_contract)


if __name__ == "__main__":
    unittest.main()
