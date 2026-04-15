import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthMode
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.wrappers import (
    build_channel_banners_insert_wrapper,
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
    build_channels_list_wrapper,
    build_channels_update_wrapper,
    build_comments_insert_wrapper,
    build_comments_list_wrapper,
)


class Layer1MetadataContractTests(unittest.TestCase):
    def _feature_contract_root(self) -> str:
        return os.path.abspath("specs/102-layer1-metadata-standards/contracts")

    def _build_conditional_metadata(self) -> EndpointMetadata:
        return EndpointMetadata(
            resource_name="search",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/search",
            request_shape=EndpointRequestShape(required_fields=("part", "q")),
            auth_mode=AuthMode.CONDITIONAL,
            quota_cost=100,
            auth_condition_note="Uses API key for public search and OAuth for restricted filters.",
            lifecycle_state="inconsistent-docs",
            caveat_note="Official quota guidance conflicts across YouTube documentation pages.",
        )

    def test_contract_artifacts_define_metadata_visibility_requirements(self):
        root = self._feature_contract_root()
        with open(os.path.join(root, "layer1-metadata-standard.md"), "r", encoding="utf-8") as handle:
            metadata_contract = handle.read()
        with open(os.path.join(root, "layer1-reviewability-contract.md"), "r", encoding="utf-8") as handle:
            reviewability_contract = handle.read()

        self.assertIn("quota cost", metadata_contract.lower())
        self.assertIn("mixed/conditional", metadata_contract)
        self.assertIn("caveat", metadata_contract.lower())
        self.assertIn("quota cost", reviewability_contract.lower())
        self.assertIn("auth expectations", reviewability_contract.lower())

    def test_review_surface_exposes_quota_auth_and_caveat_details(self):
        review_surface = self._build_conditional_metadata().review_surface()

        self.assertEqual(review_surface["resourceName"], "search")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["quotaCost"], 100)
        self.assertIn("OAuth", review_surface["authConditionNote"])
        self.assertIn("quota guidance conflicts", review_surface["caveatNote"])

    def test_review_surface_supports_higher_layer_comparison(self):
        public_wrapper = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        restricted_wrapper = self._build_conditional_metadata()

        public_surface = public_wrapper.review_surface()
        restricted_surface = restricted_wrapper.review_surface()

        self.assertLess(public_surface["quotaCost"], restricted_surface["quotaCost"])
        self.assertEqual(public_surface["authMode"], "api_key")
        self.assertEqual(restricted_surface["authMode"], "mixed/conditional")
        self.assertNotEqual(public_surface["operationKey"], restricted_surface["operationKey"])

    def test_contract_requires_caveat_implications_to_be_visible(self):
        root = self._feature_contract_root()
        with open(os.path.join(root, "layer1-reviewability-contract.md"), "r", encoding="utf-8") as handle:
            reviewability_contract = handle.read()

        self.assertIn("what type of caveat applies", reviewability_contract)
        self.assertIn("why it matters for reuse", reviewability_contract)
        self.assertIn("Free-form notes", reviewability_contract)

    def test_channel_banners_insert_review_surface_exposes_quota_auth_and_upload_notes(self):
        review_surface = build_channel_banners_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelBanners")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelBanners.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("media",))
        self.assertIn("response URL", review_surface["notes"])

    def test_channels_list_review_surface_exposes_quota_auth_and_selector_notes(self):
        review_surface = build_channels_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channels")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channels.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertIn("forHandle", review_surface["optionalFields"])
        self.assertIn("forUsername", review_surface["optionalFields"])
        self.assertIn("mine", review_surface["exclusiveSelectors"])
        self.assertIn("owner-scoped", review_surface["authConditionNote"])

    def test_channels_update_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channels_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channels")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "channels.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("brandingSettings", review_surface["notes"])
        self.assertIn("bannerExternalUrl", review_surface["notes"])

    def test_channel_sections_list_review_surface_exposes_quota_auth_and_caveat_notes(self):
        review_surface = build_channel_sections_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channelSections.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["exclusiveSelectors"], ("channelId", "id", "mine"))
        self.assertIn("owner-scoped", review_surface["authConditionNote"])
        self.assertIn("lifecycle", review_surface["notes"])

    def test_comments_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_comments_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "comments.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "parentId"))
        self.assertIn("textFormat", review_surface["optionalFields"])
        self.assertIn("reply lookup", review_surface["notes"])

    def test_comments_insert_review_surface_exposes_identity_quota_and_auth_notes(self):
        review_surface = build_comments_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "comments.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("parentId", review_surface["notes"])
        self.assertIn("textOriginal", review_surface["notes"])

    def test_channel_sections_insert_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channel_sections_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelSections.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("snippet.type", review_surface["notes"])
        self.assertIn("title", review_surface["notes"])

    def test_channel_sections_update_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channel_sections_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "channelSections.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("snippet.type", review_surface["notes"])

    def test_channel_sections_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_channel_sections_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "channelSections.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("owner-scoped", review_surface["notes"])
        self.assertIn("one target", review_surface["notes"])


if __name__ == "__main__":
    unittest.main()
