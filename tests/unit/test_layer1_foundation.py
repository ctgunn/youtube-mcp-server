import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.executor import IntegrationExecutor, IntegrationHooks, RequestExecution, timed_execution
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper


class Layer1FoundationUnitTests(unittest.TestCase):
    def test_requires_metadata_fields_for_endpoint_wrappers(self):
        with self.assertRaises(ValueError):
            EndpointMetadata(
                resource_name="videos",
                operation_name="list",
                http_method="GET",
                path_shape="/youtube/v3/videos",
                request_shape=EndpointRequestShape(required_fields=("part",)),
                auth_mode=AuthMode.API_KEY,
                quota_cost=0,
            )

    def test_requires_conditional_auth_reason(self):
        with self.assertRaises(ValueError):
            AuthContext(
                mode=AuthMode.CONDITIONAL,
                credentials=CredentialBundle(api_key="key-123"),
            )

    def test_normalizes_retryable_upstream_failures(self):
        error = normalize_upstream_error(
            RuntimeError("temporary upstream outage"),
            category="transient",
            status_code=503,
            retryable=True,
            details={"resource": "videos"},
        )
        self.assertIsInstance(error, NormalizedUpstreamError)
        self.assertEqual(error.category, "transient")
        self.assertTrue(error.retryable)
        self.assertEqual(error.upstream_status, 503)

    def test_wrapper_executes_with_shared_executor(self):
        captured = {}

        def fake_transport(execution):
            captured["execution"] = execution
            return {"items": [{"id": "video-123"}]}

        metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part",), optional_fields=("id",)),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        wrapper = RepresentativeEndpointWrapper(metadata=metadata)
        executor = IntegrationExecutor(transport=fake_transport, retry_policy=RetryPolicy(max_attempts=1))
        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )
        self.assertEqual(result["items"][0]["id"], "video-123")
        execution = captured["execution"]
        self.assertIsInstance(execution, RequestExecution)
        self.assertEqual(execution.metadata.resource_name, "videos")
        self.assertEqual(execution.credentials["apiKey"], "key-123")

    def test_executor_records_hook_events(self):
        events = []

        def fake_transport(_execution):
            return {"ok": True}

        hooks = IntegrationHooks(
            on_request=lambda execution: events.append(("request", execution.metadata.operation_name)),
            on_response=lambda execution, response: events.append(("response", response["ok"])),
            on_error=lambda execution, error: events.append(("error", error.category)),
        )
        metadata = EndpointMetadata(
            resource_name="search",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/search",
            request_shape=EndpointRequestShape(required_fields=("part",), optional_fields=("q",)),
            auth_mode=AuthMode.API_KEY,
            quota_cost=100,
        )
        executor = IntegrationExecutor(transport=fake_transport, retry_policy=RetryPolicy(max_attempts=1), hooks=hooks)
        executor.execute(
            RequestExecution(
                metadata=metadata,
                arguments={"part": "snippet", "q": "mcp"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )
        )
        self.assertEqual(events, [("request", "list"), ("response", True)])

    def test_timed_execution_returns_response_and_latency(self):
        metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"id": execution.arguments["id"]}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        response, latency_ms = timed_execution(
            executor,
            RequestExecution(
                metadata=metadata,
                arguments={"part": "snippet", "id": "video-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            ),
        )
        self.assertEqual(response["items"][0]["id"], "video-123")
        self.assertGreaterEqual(latency_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
