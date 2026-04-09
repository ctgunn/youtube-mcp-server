import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.executor import IntegrationExecutor, build_observability_hooks
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.wrappers import (
    RepresentativeEndpointWrapper,
    build_activities_list_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)
from mcp_server.observability import InMemoryObservability


class Layer1FoundationIntegrationTests(unittest.TestCase):
    def test_activities_list_wrapper_executes_channel_requests_through_shared_executor(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "activity-123",
                        "channelId": execution.arguments["channelId"],
                        "kind": "youtube#activity",
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "channelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "activity-123")
        self.assertEqual(result["items"][0]["channelId"], "UC123")

    def test_activities_list_wrapper_executes_authorized_user_requests_through_shared_executor(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "activity-234",
                        "source": "authorized",
                        "selector": "mine" if execution.arguments.get("mine") else "home",
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "mine": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "activity-234")
        self.assertEqual(result["items"][0]["selector"], "mine")

    def test_activities_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "home": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"], [])

    def test_captions_list_wrapper_executes_video_requests_through_shared_executor(self):
        wrapper = build_captions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "caption-123",
                        "videoId": execution.arguments["videoId"],
                        "kind": "youtube#caption",
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "caption-123")
        self.assertEqual(result["items"][0]["videoId"], "video-123")

    def test_captions_list_wrapper_executes_delegated_requests_through_shared_executor(self):
        wrapper = build_captions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": execution.arguments["id"],
                        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "id": "caption-234",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "caption-234")
        self.assertEqual(result["items"][0]["delegatedOwner"], "owner-123")

    def test_captions_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_captions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "caption-345"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"], [])

    def test_captions_insert_wrapper_executes_authorized_create_requests_through_shared_executor(self):
        wrapper = build_captions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "caption-456",
                "videoId": execution.arguments["body"]["snippet"]["videoId"],
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "kind": "youtube#caption",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}},
                "media": {"mimeType": "text/plain", "content": "caption body"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "caption-456")
        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_captions_update_wrapper_executes_body_only_requests_through_shared_executor(self):
        wrapper = build_captions_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "language": execution.arguments["body"]["snippet"]["language"],
                "kind": "youtube#caption",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "caption-567", "snippet": {"language": "en", "name": "Updated English"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "caption-567")
        self.assertEqual(result["language"], "en")

    def test_captions_update_wrapper_executes_body_plus_media_requests_through_shared_executor(self):
        wrapper = build_captions_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "hasMedia": "media" in execution.arguments,
                "kind": "youtube#caption",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "caption-678", "snippet": {"language": "en", "name": "Updated English"}},
                "media": {"mimeType": "text/plain", "content": "updated caption body"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "caption-678")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertTrue(result["hasMedia"])

    def test_captions_download_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "content": "caption body",
                "contentFormat": execution.arguments.get("tfmt"),
                "contentLanguage": execution.arguments.get("tlang"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "caption-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-123")
        self.assertEqual(result["content"], "caption body")

    def test_captions_download_wrapper_executes_optioned_delegated_requests_through_shared_executor(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "content": "caption body",
                "contentFormat": execution.arguments.get("tfmt"),
                "contentLanguage": execution.arguments.get("tlang"),
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "id": "caption-234",
                "tfmt": "srt",
                "tlang": "es",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-234")
        self.assertEqual(result["contentFormat"], "srt")
        self.assertEqual(result["contentLanguage"], "es")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_captions_download_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Caption access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Caption access denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "caption-403"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_captions_download_wrapper_preserves_not_found_failures_from_shared_executor(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Caption track not found"),
                    status_code=404,
                    details={"reason": "missing"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Caption track not found") as context:
            wrapper.call(
                executor,
                arguments={"id": "caption-404"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_captions_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "caption-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-123")
        self.assertTrue(result["isDeleted"])

    def test_captions_delete_wrapper_executes_delegated_requests_through_shared_executor(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "caption-234", "onBehalfOfContentOwner": "owner-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-234")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_captions_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Caption delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Caption delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "caption-403"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_captions_delete_wrapper_preserves_not_found_failures_from_shared_executor(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Caption track not found"),
                    status_code=404,
                    details={"reason": "missing"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Caption track not found") as context:
            wrapper.call(
                executor,
                arguments={"id": "caption-404"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "not_found")

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

    def test_representative_wrappers_can_be_compared_for_quota_and_auth_review(self):
        public_metadata = EndpointMetadata(
            resource_name="videos",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/videos",
            request_shape=EndpointRequestShape(required_fields=("part", "id")),
            auth_mode=AuthMode.API_KEY,
            quota_cost=1,
        )
        restricted_metadata = EndpointMetadata(
            resource_name="search",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/search",
            request_shape=EndpointRequestShape(required_fields=("part", "q")),
            auth_mode=AuthMode.CONDITIONAL,
            quota_cost=100,
            auth_condition_note="Requires OAuth when private or partner-only filters are used.",
            lifecycle_state="limited",
            caveat_note="Restricted filters are not available for every caller context.",
        )

        public_surface = public_metadata.review_surface()
        restricted_surface = restricted_metadata.review_surface()

        self.assertEqual(public_surface["authMode"], "api_key")
        self.assertEqual(restricted_surface["authMode"], "mixed/conditional")
        self.assertLess(public_surface["quotaCost"], restricted_surface["quotaCost"])
        self.assertIn("Restricted filters", restricted_surface["caveatNote"])


if __name__ == "__main__":
    unittest.main()
