import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_members_list_wrapper


class Layer1MembersContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/126-members-list/contracts")

    def test_contract_artifacts_define_wrapper_and_owner_visibility_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-members-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-members-list-owner-visibility-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            owner_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`part` plus `mode`", wrapper_contract)
        self.assertIn("owner-only", owner_contract.lower())
        self.assertIn("unsupported delegation", owner_contract.lower())

    def test_members_list_wrapper_review_surface_exposes_identity_quota_and_owner_notes(self):
        review_surface = build_members_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "members")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "members.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "mode"))
        self.assertEqual(review_surface["optionalFields"], ("pageToken", "maxResults"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_contract_documents_request_boundaries_and_invalid_request_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-members-list-wrapper-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` and `mode` are required", wrapper_contract)
        self.assertIn("undocumented modifiers", wrapper_contract)
        self.assertIn("delegation-related inputs are unsupported", wrapper_contract)

    def test_contract_documents_owner_visibility_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-members-list-owner-visibility-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            owner_contract = handle.read()

        self.assertIn("oauth-required", owner_contract.lower())
        self.assertIn("owner-only", owner_contract.lower())
        self.assertIn("empty results", owner_contract.lower())
        self.assertIn("access problems", owner_contract.lower())


if __name__ == "__main__":
    unittest.main()
