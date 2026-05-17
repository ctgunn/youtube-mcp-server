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

    def test_videos_get_rating_contract_artifacts_define_lookup_and_auth_guidance(self):
        root = os.path.abspath("specs/151-videos-get-rating/contracts")
        with open(
            os.path.join(root, "layer1-videos-get-rating-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-get-rating-auth-rating-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_rating_contract = handle.read()

        self.assertIn("quota cost of `1`", wrapper_contract)
        self.assertIn("successful unrated results remain successful outcomes", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_rating_contract)
        self.assertIn("successful positive-rating state", auth_rating_contract)
        self.assertIn("successful unrated lookup outcomes", auth_rating_contract)

    def test_videos_get_rating_wrapper_review_surface_exposes_lookup_identity_and_quota(self):
        review_surface = wrappers_module.build_videos_get_rating_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "getRating")
        self.assertEqual(review_surface["operationKey"], "videos.getRating")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos/getRating")
        self.assertIn("liked", review_surface["notes"])
        self.assertIn("disliked", review_surface["notes"])
        self.assertIn("none", review_surface["notes"])
        self.assertIn("maximum of 50", review_surface["notes"])

    def test_videos_get_rating_contract_artifacts_define_multi_id_and_state_reviewability(self):
        root = os.path.abspath("specs/151-videos-get-rating/contracts")
        with open(
            os.path.join(root, "layer1-videos-get-rating-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-get-rating-auth-rating-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_rating_contract = handle.read()

        self.assertIn("one or more comma-delimited video identifiers", wrapper_contract)
        self.assertIn("successful unrated results remain successful outcomes", wrapper_contract)
        self.assertIn("`liked`, `disliked`, and `none`", auth_rating_contract)
        self.assertIn("under 1 minute", auth_rating_contract)

    def test_videos_get_rating_contract_artifacts_define_failure_boundary_guidance(self):
        root = os.path.abspath("specs/151-videos-get-rating/contracts")
        with open(
            os.path.join(root, "layer1-videos-get-rating-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-get-rating-auth-rating-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_rating_contract = handle.read()

        self.assertIn("at most 50 video identifiers", wrapper_contract)
        self.assertIn("upstream_unavailable", auth_rating_contract)

    def test_videos_report_abuse_contract_artifacts_define_payload_and_auth_guidance(self):
        root = os.path.abspath("specs/152-videos-report-abuse/contracts")
        with open(
            os.path.join(root, "layer1-videos-report-abuse-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-report-abuse-auth-payload-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_payload_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`body.videoId`", wrapper_contract)
        self.assertIn("`body.reasonId`", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_payload_contract)
        self.assertIn("`body.secondaryReasonId`", auth_payload_contract)
        self.assertIn("`body.comments`", auth_payload_contract)
        self.assertIn("`body.language`", auth_payload_contract)

    def test_videos_report_abuse_wrapper_review_surface_exposes_identity_quota_and_payload_requirements(self):
        review_surface = wrappers_module.build_videos_report_abuse_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "reportAbuse")
        self.assertEqual(review_surface["operationKey"], "videos.reportAbuse")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("body",))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos/reportAbuse")
        self.assertIn("videoId", review_surface["notes"])
        self.assertIn("reasonId", review_surface["notes"])
        self.assertIn("secondaryReasonId", review_surface["notes"])
        self.assertIn("comments", review_surface["notes"])
        self.assertIn("language", review_surface["notes"])
        self.assertIn("onBehalfOfContentOwner", review_surface["notes"])

    def test_videos_report_abuse_contract_artifacts_define_failure_boundary_guidance(self):
        with open(
            os.path.join(
                os.path.abspath("specs/152-videos-report-abuse/contracts"),
                "layer1-videos-report-abuse-auth-payload-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_payload_contract = handle.read()

        self.assertIn("invalid_request", auth_payload_contract)
        self.assertIn("access-related failures", auth_payload_contract)
        self.assertIn("invalid abuse-reason failures", auth_payload_contract)
        self.assertIn("rate-limit failures", auth_payload_contract)
        self.assertIn("video-not-found failures", auth_payload_contract)
        self.assertIn("successful report acknowledgement outcomes", auth_payload_contract)

    def test_videos_delete_contract_artifacts_define_delete_and_auth_guidance(self):
        root = os.path.abspath("specs/153-videos-delete/contracts")
        with open(
            os.path.join(root, "layer1-videos-delete-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-videos-delete-auth-delete-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`id` identifies the target video", wrapper_contract)
        self.assertIn("does not accept a request body", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_delete_contract)
        self.assertIn("successful deletion acknowledgement outcomes", auth_delete_contract)
        self.assertIn("onBehalfOfContentOwner", auth_delete_contract)

    def test_videos_delete_wrapper_review_surface_exposes_identity_quota_and_delete_requirements(self):
        review_surface = wrappers_module.build_videos_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "videos.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["httpMethod"], "DELETE")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos")
        self.assertIn("no request body", review_surface["notes"])
        self.assertIn("acknowledgement", review_surface["notes"])
        self.assertIn("onBehalfOfContentOwner", review_surface["notes"])

    def test_videos_delete_contract_artifacts_define_failure_boundary_guidance(self):
        with open(
            os.path.join(
                os.path.abspath("specs/153-videos-delete/contracts"),
                "layer1-videos-delete-auth-delete-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_delete_contract = handle.read()

        self.assertIn("invalid_request", auth_delete_contract)
        self.assertIn("access-related failures", auth_delete_contract)
        self.assertIn("forbidden delete failures", auth_delete_contract)
        self.assertIn("video-not-found failures", auth_delete_contract)
        self.assertIn("upstream unavailability failures", auth_delete_contract)
        self.assertIn("successful deletion acknowledgement outcomes", auth_delete_contract)
