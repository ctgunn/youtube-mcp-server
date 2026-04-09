import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.wrappers import build_channel_banners_insert_wrapper


class Layer1ChannelBannersContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/109-channel-banners-insert/contracts")

    def test_contract_artifacts_define_wrapper_and_auth_upload_guidance(self):
        root = self._feature_contract_root()
        with open(
            os.path.join(root, "layer1-channel-banners-insert-wrapper-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            wrapper_contract = handle.read()
        with open(
            os.path.join(root, "layer1-channel-banners-insert-auth-upload-contract.md"),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_upload_contract = handle.read()

        self.assertIn("quota cost of `50`", wrapper_contract)
        self.assertIn("media upload payload", wrapper_contract)
        self.assertIn("OAuth-required", auth_upload_contract)
        self.assertIn("onBehalfOfContentOwner", auth_upload_contract)
        self.assertIn("banner URL", auth_upload_contract)

    def test_channel_banners_insert_wrapper_review_surface_exposes_identity_quota_and_auth(self):
        review_surface = build_channel_banners_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelBanners")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelBanners.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("media",))

    def test_contract_documents_upload_constraints_and_failure_boundary(self):
        with open(
            os.path.join(
                self._feature_contract_root(),
                "layer1-channel-banners-insert-auth-upload-contract.md",
            ),
            "r",
            encoding="utf-8",
        ) as handle:
            auth_upload_contract = handle.read()

        self.assertIn("16:9", auth_upload_contract)
        self.assertIn("maximum 6 MB", auth_upload_contract)
        self.assertIn("invalid upload input", auth_upload_contract)
        self.assertIn("target-channel restrictions", auth_upload_contract)


if __name__ == "__main__":
    unittest.main()
