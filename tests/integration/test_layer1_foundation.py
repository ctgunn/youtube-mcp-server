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
    build_channel_banners_insert_wrapper,
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
    build_comment_threads_insert_wrapper,
    build_comment_threads_list_wrapper,
    build_channels_list_wrapper,
    build_channels_update_wrapper,
    build_comments_insert_wrapper,
    build_comments_delete_wrapper,
    build_comments_list_wrapper,
    build_comments_set_moderation_status_wrapper,
    build_comments_update_wrapper,
    build_guide_categories_list_wrapper,
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

    def test_channels_list_wrapper_executes_id_selector_requests_through_shared_executor(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"id": execution.arguments["id"]}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "UC123")

    def test_channels_list_wrapper_executes_handle_selector_requests_through_shared_executor(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"handle": execution.arguments["forHandle"]}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "forHandle": "@channel"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["handle"], "@channel")

    def test_channels_list_wrapper_executes_mine_selector_requests_through_shared_executor(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [{"id": "mine-123"}]},
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

        self.assertEqual(result["items"][0]["id"], "mine-123")

    def test_channels_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "forUsername": "legacy-user"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])

    def test_comments_list_wrapper_executes_id_selector_requests_through_shared_executor(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": execution.arguments["id"][0],
                        "kind": "youtube#comment",
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": ["comment-123"]},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "comment-123")

    def test_comments_list_wrapper_executes_parent_selector_requests_through_shared_executor(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "reply-123",
                        "parentId": execution.arguments["parentId"],
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "parentId": "comment-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["parentId"], "comment-123")

    def test_comments_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "parentId": "comment-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])

    def test_comment_threads_list_wrapper_executes_video_selector_requests_through_shared_executor(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "thread-123",
                        "videoId": execution.arguments["videoId"],
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["videoId"], "video-123")

    def test_comment_threads_list_wrapper_executes_channel_selector_requests_through_shared_executor(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "thread-123",
                        "channelId": execution.arguments["allThreadsRelatedToChannelId"],
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "allThreadsRelatedToChannelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["channelId"], "UC123")

    def test_comment_threads_list_wrapper_executes_id_selector_requests_through_shared_executor(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": execution.arguments["id"][0],
                        "kind": "youtube#commentThread",
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": ["thread-123"]},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "thread-123")

    def test_comment_threads_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])

    def test_comment_threads_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "commentThreads.list requires a supported selector"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_comment_threads_list_wrapper_rejects_oauth_requests_for_public_selectors(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "allThreadsRelatedToChannelId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "allThreadsRelatedToChannelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_guide_categories_list_wrapper_executes_region_requests_through_shared_executor(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "GC1",
                        "regionCode": execution.arguments["regionCode"],
                        "kind": "youtube#guideCategory",
                    }
                ],
                "regionCode": execution.arguments["regionCode"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "regionCode": "US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "GC1")
        self.assertEqual(result["regionCode"], "US")

    def test_guide_categories_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "regionCode": execution.arguments["regionCode"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "regionCode": "US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["regionCode"], "US")

    def test_guide_categories_list_wrapper_rejects_missing_region_requests(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: regionCode"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_guide_categories_list_wrapper_surfaces_lifecycle_unavailable_failures(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("guideCategories is deprecated and unavailable"),
                    category="lifecycle_unavailable",
                    status_code=410,
                    details={"reason": "deprecated"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaises(NormalizedUpstreamError) as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "regionCode": "US"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        self.assertEqual(context.exception.category, "lifecycle_unavailable")

    def test_comments_insert_wrapper_executes_authorized_reply_requests_through_shared_executor(self):
        wrapper = build_comments_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "comment-456",
                "snippet": {
                    "parentId": execution.arguments["body"]["snippet"]["parentId"],
                    "textOriginal": execution.arguments["body"]["snippet"]["textOriginal"],
                },
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "kind": "youtube#comment",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "comment-456")
        self.assertEqual(result["snippet"]["parentId"], "comment-123")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_comment_threads_insert_wrapper_executes_authorized_top_level_requests_through_shared_executor(self):
        wrapper = build_comment_threads_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "thread-456",
                "snippet": {
                    "videoId": execution.arguments["body"]["snippet"]["videoId"],
                    "topLevelComment": {
                        "id": "comment-999",
                        "snippet": {
                            "textOriginal": execution.arguments["body"]["snippet"]["topLevelComment"]["snippet"][
                                "textOriginal"
                            ]
                        },
                    },
                },
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "kind": "youtube#commentThread",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {
                    "snippet": {
                        "videoId": "video-123",
                        "topLevelComment": {"snippet": {"textOriginal": "Top-level text"}},
                    }
                },
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "thread-456")
        self.assertEqual(result["snippet"]["videoId"], "video-123")
        self.assertEqual(result["snippet"]["topLevelComment"]["id"], "comment-999")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_comments_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_comments_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "snippet": {
                    "textOriginal": execution.arguments["body"]["snippet"]["textOriginal"],
                },
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "kind": "youtube#comment",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "comment-123")
        self.assertEqual(result["snippet"]["textOriginal"], "Updated comment")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_comments_update_wrapper_rejects_unsupported_write_shapes_before_executor(self):
        wrapper = build_comments_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "body.snippet.textOriginal is required"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "comment-123", "snippet": {}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comments_update_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_comments_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Comment update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Comment update denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_comments_set_moderation_status_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_comments_set_moderation_status_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "commentIds": tuple(execution.arguments["id"]),
                "isModerated": True,
                "moderationStatus": execution.arguments["moderationStatus"],
                "authorBanApplied": bool(execution.arguments.get("banAuthor")),
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "id": ["comment-123", "comment-456"],
                "moderationStatus": "rejected",
                "banAuthor": True,
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["commentIds"], ("comment-123", "comment-456"))
        self.assertTrue(result["isModerated"])
        self.assertEqual(result["moderationStatus"], "rejected")
        self.assertTrue(result["authorBanApplied"])
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_comments_set_moderation_status_wrapper_rejects_unsupported_states_before_executor(self):
        wrapper = build_comments_set_moderation_status_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"isModerated": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "unsupported moderationStatus: spam"):
            wrapper.call(
                executor,
                arguments={
                    "id": ["comment-123"],
                    "moderationStatus": "spam",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comments_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_comments_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "commentId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "id": "comment-123",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["commentId"], "comment-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_comments_delete_wrapper_rejects_invalid_identifier_shapes_before_executor(self):
        wrapper = build_comments_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"commentId": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id must identify one comment"):
            wrapper.call(
                executor,
                arguments={"id": ["comment-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comments_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_comments_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Comment delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Comment delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "comment-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_comments_set_moderation_status_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_comments_set_moderation_status_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Comment moderation denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Comment moderation denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "id": ["comment-123"],
                    "moderationStatus": "rejected",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

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

    def test_channels_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_channels_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "brandingSettings": execution.arguments["body"].get("brandingSettings"),
                "localizations": execution.arguments["body"].get("localizations"),
                "kind": "youtube#channel",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "brandingSettings,localizations",
                "body": {
                    "id": "UC123",
                    "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                    "localizations": {"en": {"title": "Updated Channel"}},
                },
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "UC123")
        self.assertIn("brandingSettings", result)
        self.assertIn("localizations", result)

    def test_channels_update_wrapper_rejects_unsupported_write_shapes_before_executor(self):
        wrapper = build_channels_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "body.brandingSettings is required for selected part"):
            wrapper.call(
                executor,
                arguments={
                    "part": "brandingSettings",
                    "body": {"id": "UC123", "localizations": {"en": {"title": "Updated Channel"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_channels_update_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_channels_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Channel update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Channel update denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "brandingSettings",
                    "body": {
                        "id": "UC123",
                        "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_channel_sections_list_wrapper_executes_channel_selector_requests_through_shared_executor(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "section-123",
                        "channelId": execution.arguments["channelId"],
                        "kind": "youtube#channelSection",
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

        self.assertEqual(result["items"][0]["id"], "section-123")
        self.assertEqual(result["items"][0]["channelId"], "UC123")

    def test_channel_sections_list_wrapper_executes_id_selector_requests_through_shared_executor(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"id": execution.arguments["id"]}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "section-456"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "section-456")

    def test_channel_sections_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
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

        self.assertEqual(result["items"], [])

    def test_channel_sections_list_wrapper_rejects_unsupported_selector_shapes_before_executor(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [{"id": "should-not-run"}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "channelId": "UC123", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Channel sections access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Channel sections access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_channel_sections_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_channel_sections_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "section-123",
                "snippet": execution.arguments["body"]["snippet"],
                "contentDetails": execution.arguments["body"]["contentDetails"],
                "kind": "youtube#channelSection",
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet,contentDetails",
                "body": {
                    "snippet": {
                        "type": "multiplePlaylists",
                        "channelId": "UC123",
                        "title": "Featured playlists",
                    },
                    "contentDetails": {"playlists": ["PL123", "PL456"]},
                },
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "section-123")
        self.assertEqual(result["snippet"]["type"], "multiplePlaylists")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_channel_sections_insert_wrapper_rejects_invalid_create_shapes_before_executor(self):
        wrapper = build_channel_sections_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "multipleChannels requires body.snippet.title"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {"type": "multipleChannels", "channelId": "UC123"},
                        "contentDetails": {"channels": ["UC777", "UC888"]},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_channel_sections_insert_wrapper_preserves_upstream_create_failures_from_shared_executor(self):
        wrapper = build_channel_sections_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("The channel already has the maximum number of sections"),
                    status_code=400,
                    details={"reason": "limit"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "maximum number of sections",
        ) as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                        "contentDetails": {"playlists": ["PL123"]},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_channel_sections_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_channel_sections_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "snippet": execution.arguments["body"].get("snippet"),
                "contentDetails": execution.arguments["body"].get("contentDetails"),
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "kind": "youtube#channelSection",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet,contentDetails",
                "body": {
                    "id": "section-123",
                    "snippet": {
                        "type": "multipleChannels",
                        "channelId": "UC123",
                        "title": "Updated featured channels",
                    },
                    "contentDetails": {"channels": ["UC777", "UC888"]},
                },
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "section-123")
        self.assertEqual(result["snippet"]["title"], "Updated featured channels")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_channel_sections_update_wrapper_rejects_invalid_update_shapes_before_executor(self):
        wrapper = build_channel_sections_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "multipleChannels does not accept body.contentDetails.playlists"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet,contentDetails",
                    "body": {
                        "id": "section-123",
                        "snippet": {
                            "type": "multipleChannels",
                            "channelId": "UC123",
                            "title": "Updated featured channels",
                        },
                        "contentDetails": {"playlists": ["PL123"]},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_channel_sections_update_wrapper_preserves_upstream_auth_failures_from_shared_executor(self):
        wrapper = build_channel_sections_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Channel section update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Channel section update denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet,contentDetails",
                    "body": {
                        "id": "section-123",
                        "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                        "contentDetails": {"playlists": ["PL123"]},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_channel_sections_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_channel_sections_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "channelSectionId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "delegatedOwnerChannel": execution.arguments.get("onBehalfOfContentOwnerChannel"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "section-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["channelSectionId"], "section-123")
        self.assertTrue(result["isDeleted"])

    def test_channel_sections_delete_wrapper_executes_delegated_requests_through_shared_executor(self):
        wrapper = build_channel_sections_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "channelSectionId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
                "delegatedOwnerChannel": execution.arguments.get("onBehalfOfContentOwnerChannel"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "id": "section-123",
                "onBehalfOfContentOwner": "owner-123",
                "onBehalfOfContentOwnerChannel": "UC123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["delegatedOwnerChannel"], "UC123")

    def test_channel_sections_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_channel_sections_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Channel section delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Channel section delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "section-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_channel_sections_delete_wrapper_preserves_not_found_failures_from_shared_executor(self):
        wrapper = build_channel_sections_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Channel section not found"),
                    status_code=404,
                    details={"reason": "notFound"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Channel section not found") as context:
            wrapper.call(
                executor,
                arguments={"id": "section-404"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "not_found")

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

    def test_channel_banners_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "bannerUrl": "https://yt.example/banner",
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["bannerUrl"], "https://yt.example/banner")

    def test_channel_banners_insert_wrapper_executes_delegated_requests_through_shared_executor(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "bannerUrl": "https://yt.example/banner",
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "media": {"mimeType": "image/png", "content": b"banner-bytes"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["bannerUrl"], "https://yt.example/banner")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_channel_banners_insert_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Banner upload denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Banner upload denied") as context:
            wrapper.call(
                executor,
                arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_channel_banners_insert_wrapper_preserves_invalid_upload_failures_from_shared_executor(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Banner upload payload invalid"),
                    category="invalid_request",
                    status_code=400,
                    details={"reason": "mediaBodyRequired"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Banner upload payload invalid") as context:
            wrapper.call(
                executor,
                arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_channel_banners_insert_wrapper_preserves_target_channel_failures_from_shared_executor(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Target channel cannot accept banner update"),
                    category="target_channel",
                    status_code=404,
                    details={"reason": "missing"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Target channel cannot accept banner update",
        ) as context:
            wrapper.call(
                executor,
                arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "target_channel")

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
