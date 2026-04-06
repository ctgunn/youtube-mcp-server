import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.consumer import RepresentativeHigherLayerConsumer
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.wrappers import (
    RepresentativeEndpointWrapper,
    build_activities_list_wrapper,
    build_captions_list_wrapper,
)


class Layer1ConsumerContractTests(unittest.TestCase):
    def _build_wrapper(self):
        metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        return RepresentativeEndpointWrapper(metadata=metadata)

    def test_consumer_depends_on_typed_wrapper_methods(self):
        wrapper = self._build_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"id": execution.arguments["id"], "title": "Layered MCP"}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_video_summary(
            arguments={"part": "snippet", "id": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["sourceOperation"], "videos.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)

    def test_consumer_surfaces_normalized_failures_without_raw_upstream_shapes(self):
        wrapper = self._build_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(RuntimeError("upstream timeout")),
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        with self.assertRaises(NormalizedUpstreamError) as context:
            consumer.fetch_video_summary(
                arguments={"part": "snippet", "id": "video-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        self.assertEqual(context.exception.category, "transient")
        self.assertNotIn("traceback", context.exception.details)

    def test_contract_artifacts_reference_required_foundation_elements(self):
        root = os.path.abspath("specs/101-layer1-client-foundation/contracts")
        with open(os.path.join(root, "layer1-wrapper-contract.md"), "r", encoding="utf-8") as handle:
            wrapper_contract = handle.read()
        with open(os.path.join(root, "layer1-consumer-contract.md"), "r", encoding="utf-8") as handle:
            consumer_contract = handle.read()

        self.assertIn("shared request executor", wrapper_contract)
        self.assertIn("normalized upstream failures", wrapper_contract)
        self.assertIn("typed Layer 1 methods", consumer_contract)
        self.assertIn("normalized failure", consumer_contract)

    def test_consumer_can_summarize_activities_results_for_higher_layers(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_activity_summary(
            arguments={"part": "snippet", "home": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["activityCount"], 0)
        self.assertEqual(result["sourceOperation"], "activities.list")
        self.assertEqual(result["sourceQuotaCost"], 1)

    def test_consumer_can_summarize_captions_results_for_higher_layers(self):
        wrapper = build_captions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_caption_summary(
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["captionCount"], 0)
        self.assertEqual(result["sourceOperation"], "captions.list")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("onBehalfOfContentOwner", result["sourceNotes"])


if __name__ == "__main__":
    unittest.main()
