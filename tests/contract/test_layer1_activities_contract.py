import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_activities_list_wrapper


class Layer1ActivitiesContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/103-activities-list/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_filter_guidance(self):
        root = self._feature_contract_root()
        with open(os.path.join(root, "layer1-activities-wrapper-contract.md"), "r", encoding="utf-8") as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-activities-auth-filter-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("quota cost of `1`", wrapper_contract)
        self.assertIn("public channel activity retrieval", wrapper_contract)
        self.assertIn("authorized-user activity views", auth_filter_contract)
        self.assertIn("unsupported combinations", auth_filter_contract)
        self.assertIn("zero activity items", auth_filter_contract)

    def test_activities_wrapper_review_surface_exposes_identity_quota_and_mixed_auth(self):
        review_surface = build_activities_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "activities")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "activities.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["exclusiveSelectors"], ("channelId", "mine", "home"))
        self.assertIn("channelId", review_surface["authConditionNote"])
        self.assertIn("mine", review_surface["authConditionNote"])
        self.assertIn("home", review_surface["authConditionNote"])

    def test_activities_contract_documents_channel_selector_as_supported_public_path(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-activities-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("channelId", wrapper_contract)
        self.assertIn("public channel activity retrieval", wrapper_contract)

    def test_activities_contract_documents_authorized_user_paths(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-activities-auth-filter-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("mine", auth_filter_contract)
        self.assertIn("home", auth_filter_contract)
        self.assertIn("authorized-user-only", auth_filter_contract)

    def test_activities_contract_documents_empty_results_as_success(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-activities-auth-filter-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_filter_contract = handle.read()

        self.assertIn("zero activity items", auth_filter_contract)
        self.assertIn("successful but empty collection", auth_filter_contract)


if __name__ == "__main__":
    unittest.main()
