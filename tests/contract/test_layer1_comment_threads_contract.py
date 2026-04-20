import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import (
    build_comment_threads_insert_wrapper,
    build_comment_threads_list_wrapper,
)


class Layer1CommentThreadsContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/121-comment-threads-list/contracts")

    def _insert_feature_contract_root(self) -> str:
        return os.path.abspath("specs/122-comment-threads-insert/contracts")

    def test_contract_artifacts_define_wrapper_and_lookup_access_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-comment-threads-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-comment-threads-list-lookup-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            lookup_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("`videoId`, `allThreadsRelatedToChannelId`, and `id`", wrapper_contract)
        self.assertIn("video-based retrieval", lookup_contract)
        self.assertIn("channel-related retrieval", lookup_contract)
        self.assertIn("successful retrieval with no matches", lookup_contract)

    def test_comment_threads_list_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_comment_threads_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "commentThreads")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "commentThreads.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["exclusiveSelectors"],
            ("videoId", "allThreadsRelatedToChannelId", "id"),
        )

    def test_contract_documents_selector_boundaries_and_optional_modifier_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-comment-threads-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("exactly one selector", wrapper_contract)
        self.assertIn("pageToken", wrapper_contract)
        self.assertIn("maxResults", wrapper_contract)
        self.assertIn("order", wrapper_contract)
        self.assertIn("searchTerms", wrapper_contract)
        self.assertIn("textFormat", wrapper_contract)
        self.assertIn("silently rewritten", wrapper_contract)

    def test_contract_documents_invalid_combination_and_empty_result_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-comment-threads-list-lookup-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            lookup_contract = handle.read()

        self.assertIn("mutually exclusive", lookup_contract)
        self.assertIn("missing selectors", lookup_contract)
        self.assertIn("zero comment-thread items", lookup_contract)
        self.assertIn("access mismatches", lookup_contract)

    def test_insert_contract_artifacts_define_wrapper_and_auth_write_guidance(self):
        root = self._insert_feature_contract_root()
        with open(
            os.path.join(root, "layer1-comment-threads-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-comment-threads-insert-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost (`50`)", wrapper_contract)
        self.assertIn("top-level thread `body`", wrapper_contract)
        self.assertIn("OAuth-required", auth_write_contract)
        self.assertIn("top-level thread creation", auth_write_contract)
        self.assertIn("reply-style or mixed", auth_write_contract)

    def test_comment_threads_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_comment_threads_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "commentThreads")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "commentThreads.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])

    def test_insert_contract_documents_supported_shape_and_target_eligibility_rules(self):
        with open(
            os.path.join(
                self._insert_feature_contract_root(),
                "layer1-comment-threads-insert-auth-write-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("supported discussion target", auth_write_contract)
        self.assertIn("top-level comment content", auth_write_contract)
        self.assertIn("target-eligibility failures", auth_write_contract)
        self.assertIn("comments-disabled", auth_write_contract)
