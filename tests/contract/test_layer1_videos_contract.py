import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

import mcp_server.integrations.wrappers as wrappers_module
from mcp_server.integrations.wrappers import build_videos_list_wrapper


class Layer1VideosContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/147-videos-list/contracts")

    def test_contract_artifacts_define_wrapper_and_selector_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-videos-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-list-selector-auth-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("quota cost (`1`)", wrapper_contract)
        self.assertIn("exactly one selector from `id`, `chart`, or `myRating`", wrapper_contract)
        self.assertIn("mixed-auth behavior", selector_contract)
        self.assertIn("successful empty results", selector_contract)

    def test_videos_list_wrapper_review_surface_exposes_identity_quota_and_selectors(self):
        review_surface = build_videos_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videos.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"],
            ("id", "chart", "myRating", "pageToken", "maxResults", "regionCode", "videoCategoryId"),
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "chart", "myRating"))
        self.assertEqual(review_surface["lifecycleState"], "active")

    def test_contract_documents_request_boundaries_and_auth_rules(self):
        with open(
            os.path.join(self._feature_contract_root(), "layer1-videos-list-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()

        self.assertIn("`part` is required", wrapper_contract)
        self.assertIn("`pageToken` and `maxResults` are supported only for collection-style retrieval", wrapper_contract)
        self.assertIn("`regionCode` and `videoCategoryId` are chart-oriented refinements", wrapper_contract)
        self.assertIn("auth_condition_note", wrapper_contract)

    def test_contract_documents_selector_conflict_and_empty_result_rules(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-videos-list-selector-auth-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            selector_contract = handle.read()

        self.assertIn("may not supply more than one selector", selector_contract)
        self.assertIn("chart-only refinements", selector_contract)
        self.assertIn("successful empty results", selector_contract)
        self.assertIn("invalid requests remain separate", selector_contract)

    def test_videos_insert_contract_artifacts_define_upload_and_caveat_guidance(self):
        root = os.path.abspath("specs/148-videos-insert/contracts")
        with open(
            os.path.join(root, "layer1-videos-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-insert-auth-upload-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_upload_contract = handle.read()

        self.assertIn("quota cost of `1600`", wrapper_contract)
        self.assertIn("supported upload modes", wrapper_contract)
        self.assertIn("OAuth-only", auth_upload_contract)
        self.assertIn("audit/private-default caveat", auth_upload_contract)

    def test_videos_insert_wrapper_review_surface_exposes_identity_quota_and_upload_requirements(self):
        review_surface = wrappers_module.build_videos_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "videos.insert")
        self.assertEqual(review_surface["quotaCost"], 1600)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body", "media"))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos")

    def test_videos_update_contract_artifacts_define_write_and_auth_guidance(self):
        root = os.path.abspath("specs/149-videos-update/contracts")
        with open(
            os.path.join(root, "layer1-videos-update-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-update-auth-write-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_write_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`part=snippet`", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_write_contract)
        self.assertIn("body.snippet.title", auth_write_contract)
        self.assertIn("body.id", wrapper_contract)
        self.assertIn("body.snippet.tags", wrapper_contract)
        self.assertIn("body.localizations", wrapper_contract)

    def test_videos_update_wrapper_review_surface_exposes_identity_quota_and_write_requirements(self):
        review_surface = wrappers_module.build_videos_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "videos.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos")
        self.assertIn("body.snippet.tags", review_surface["notes"])
        self.assertIn("body.localizations", review_surface["notes"])

    def test_videos_rate_contract_artifacts_define_rating_and_auth_guidance(self):
        root = os.path.abspath("specs/150-videos-rate/contracts")
        with open(
            os.path.join(root, "layer1-videos-rate-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-rate-auth-rating-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_rating_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`like`, `dislike`, and `none`", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_rating_contract)
        self.assertIn("clear-rating path", auth_rating_contract)
        self.assertIn("unsupported rating values", auth_rating_contract)

    def test_videos_rate_wrapper_review_surface_exposes_identity_quota_and_rating_requirements(self):
        review_surface = wrappers_module.build_videos_rate_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "rate")
        self.assertEqual(review_surface["operationKey"], "videos.rate")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id", "rating"))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos/rate")
        self.assertIn("like", review_surface["notes"])
        self.assertIn("dislike", review_surface["notes"])
        self.assertIn("none", review_surface["notes"])
        self.assertIn("invalid-request", review_surface["notes"])
