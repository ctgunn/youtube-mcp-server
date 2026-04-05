import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.executor import IntegrationExecutor, build_observability_hooks
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper
from mcp_server.observability import InMemoryObservability


class Layer1FoundationIntegrationTests(unittest.TestCase):
    def test_representative_wrapper_execution_uses_shared_observability_hooks(self):
        observability = InMemoryObservability()

        def transport(execution):
            return {
                "resource": execution.metadata.resource_name,
                "operation": execution.metadata.operation_name,
                "authMode": execution.auth_context.mode.value,
                "items": [{"id": execution.arguments["id"]}],
            }

        metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        wrapper = RepresentativeEndpointWrapper(metadata=metadata)
        executor = IntegrationExecutor(
            transport=transport,
            retry_policy=RetryPolicy(max_attempts=1),
            hooks=build_observability_hooks(observability, request_id="req-layer1-1"),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["resource"], "videos")
        self.assertEqual(result["authMode"], "api_key")
        events = [entry for entry in observability.logs if entry.get("event") == "integration.execution"]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["phase"], "request")
        self.assertEqual(events[1]["phase"], "response")
        self.assertEqual(events[1]["resourceName"], "videos")

    def test_shared_executor_normalizes_failures_for_wrappers(self):
        observability = InMemoryObservability()

        def transport(_execution):
            raise RuntimeError("quota temporarily exhausted")

        metadata = EndpointMetadata(
            resource_name="search",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/search",
            request_shape=EndpointRequestShape(required_fields=("part", "q")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=100,
        )
        wrapper = RepresentativeEndpointWrapper(metadata=metadata)
        executor = IntegrationExecutor(
            transport=transport,
            retry_policy=RetryPolicy(max_attempts=1, retryable_statuses=(429, 500, 503)),
            hooks=build_observability_hooks(observability, request_id="req-layer1-2"),
        )

        with self.assertRaisesRegex(RuntimeError, "quota temporarily exhausted"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "q": "mcp"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        events = [entry for entry in observability.logs if entry.get("event") == "integration.execution"]
        self.assertEqual(events[-1]["phase"], "error")
        self.assertEqual(events[-1]["status"], "error")
        self.assertEqual(events[-1]["errorCategory"], "transient")

    def test_higher_layer_consumer_composes_typed_methods(self):
        from mcp_server.integrations.consumer import RepresentativeHigherLayerConsumer

        metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        wrapper = RepresentativeEndpointWrapper(metadata=metadata)
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


if __name__ == "__main__":
    unittest.main()
