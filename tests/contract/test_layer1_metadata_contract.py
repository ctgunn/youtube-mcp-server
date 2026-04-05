import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthMode
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape


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


if __name__ == "__main__":
    unittest.main()
