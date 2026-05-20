import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

import mcp_server.integrations.wrappers as wrappers_module


class Layer1WatermarksContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/154-watermarks-set-wrapper/contracts")

    def _unset_feature_contract_root(self) -> str:
        return os.path.abspath("specs/155-watermarks-unset-wrapper/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_upload_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-watermarks-set-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-watermarks-set-auth-upload-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_upload_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`channelId`", wrapper_contract)
        self.assertIn("`body`", wrapper_contract)
        self.assertIn("`media`", wrapper_contract)
        self.assertIn("Internal-only Layer 1 wrapper behavior", wrapper_contract)
        self.assertIn("without leaving the repository artifacts", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_upload_contract)
        self.assertIn("10 MB", auth_upload_contract)
        self.assertIn("image/png", auth_upload_contract)

    def test_watermarks_set_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = wrappers_module.build_watermarks_set_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "watermarks")
        self.assertEqual(review_surface["operationName"], "set")
        self.assertEqual(review_surface["operationKey"], "watermarks.set")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("channelId", "body", "media"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["pathShape"], "/upload/youtube/v3/watermarks/set")
        self.assertIn("onBehalfOfContentOwner", review_surface["notes"])

    def test_contract_documents_invalid_shape_and_failure_boundary(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-watermarks-set-auth-upload-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_upload_contract = handle.read()

        self.assertIn("invalid_request", auth_upload_contract)
        self.assertIn("access-related failures", auth_upload_contract)
        self.assertIn("unsupported media", auth_upload_contract)
        self.assertIn("upstream image validation failures", auth_upload_contract)
        self.assertIn("forbidden", auth_upload_contract)
        self.assertIn("successful watermark-update acknowledgement", auth_upload_contract)

    def test_unset_contract_artifacts_define_wrapper_and_auth_boundary_guidance(self):
        root = self._unset_feature_contract_root()
        with open(
            os.path.join(root, "layer1-watermarks-unset-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-watermarks-unset-auth-boundary-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("`channelId`", wrapper_contract)
        self.assertIn("does not include watermark resource metadata", wrapper_contract)
        self.assertIn("does not include media upload content", wrapper_contract)
        self.assertIn("Internal-only Layer 1 wrapper behavior", wrapper_contract)
        self.assertIn("without leaving the repository artifacts", wrapper_contract)
        self.assertIn("OAuth-backed access", auth_contract)
        self.assertIn("no-removal-possible", auth_contract)
        self.assertIn("unsupported payload", auth_contract)

    def test_watermarks_unset_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = wrappers_module.build_watermarks_unset_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "watermarks")
        self.assertEqual(review_surface["operationName"], "unset")
        self.assertEqual(review_surface["operationKey"], "watermarks.unset")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("channelId",))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/watermarks/unset")
        self.assertIn("no media upload", review_surface["notes"])
        self.assertIn("onBehalfOfContentOwner", review_surface["notes"])

    def test_unset_contract_documents_invalid_shape_and_failure_boundary(self):
        with open(
            os.path.join(
                self._unset_feature_contract_root(),
                "layer1-watermarks-unset-auth-boundary-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_contract = handle.read()

        self.assertIn("invalid_request", auth_contract)
        self.assertIn("access-related failures", auth_contract)
        self.assertIn("unsupported payload", auth_contract)
        self.assertIn("forbidden", auth_contract)
        self.assertIn("no-removal-possible", auth_contract)
        self.assertIn("upstream unavailability", auth_contract)
        self.assertIn("successful watermark-removal acknowledgement", auth_contract)


if __name__ == "__main__":
    unittest.main()
