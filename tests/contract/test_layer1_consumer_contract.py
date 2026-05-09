import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

import mcp_server.integrations.wrappers as wrappers_module
from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.consumer import RepresentativeHigherLayerConsumer
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError
from mcp_server.integrations.executor import IntegrationExecutor
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
    build_comments_delete_wrapper,
    build_comments_insert_wrapper,
    build_comments_list_wrapper,
    build_comments_set_moderation_status_wrapper,
    build_comments_update_wrapper,
    build_guide_categories_list_wrapper,
    build_i18n_languages_list_wrapper,
    build_i18n_regions_list_wrapper,
    build_members_list_wrapper,
    build_memberships_levels_list_wrapper,
    build_playlist_images_delete_wrapper,
    build_playlist_images_insert_wrapper,
    build_playlist_images_list_wrapper,
    build_playlist_items_delete_wrapper,
    build_playlist_items_insert_wrapper,
    build_playlist_items_list_wrapper,
    build_playlist_items_update_wrapper,
    build_playlist_images_update_wrapper,
    build_playlists_delete_wrapper,
    build_playlists_insert_wrapper,
    build_search_list_wrapper,
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
    build_playlists_update_wrapper,
    build_playlists_list_wrapper,
    build_video_abuse_report_reasons_list_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
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

    def test_consumer_can_summarize_channels_results_for_higher_layers(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [{"id": execution.arguments.get("id", "UC123")}]},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_channels_summary(
            arguments={"part": "snippet", "forHandle": "@channel"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["channelCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "forHandle")
        self.assertEqual(result["sourceOperation"], "channels.list")
        self.assertEqual(result["sourceAuthMode"], "mixed/conditional")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("owner-scoped", result["sourceAuthConditionNote"])
        self.assertIn("forUsername", result["sourceNotes"])

    def test_consumer_can_summarize_empty_channels_results_for_higher_layers(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_channels_summary(
            arguments={"part": "snippet", "forUsername": "legacy-user"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["channelCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "forUsername")

    def test_consumer_can_summarize_playlists_results_for_higher_layers(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "PL123", "channelId": execution.arguments.get("channelId")}]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_playlists_summary(
            arguments={"part": "snippet", "channelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["playlistCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "channelId")
        self.assertEqual(result["sourceOperation"], "playlists.list")
        self.assertEqual(result["sourceAuthMode"], "mixed/conditional")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("owner-scoped", result["sourceAuthConditionNote"])
        self.assertIn("pageToken", result["sourceNotes"])

    def test_consumer_can_summarize_empty_playlists_results_for_higher_layers(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_playlists_summary(
            arguments={"part": "snippet", "mine": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "mine")

    def test_consumer_can_summarize_search_results_for_higher_layers(self):
        wrapper = build_search_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "items": [{"id": {"videoId": "video-123"}}],
                "nextPageToken": "cursor-2",
                "authPath": "public",
                "queryContext": {
                    "part": "snippet",
                    "q": "mcp server",
                    "type": "video",
                    "maxResults": 5,
                },
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_search_summary(
            arguments={"part": "snippet", "q": "mcp server", "type": "video", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["query"], "mcp server")
        self.assertEqual(result["resultCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["searchType"], "video")
        self.assertEqual(result["nextPageToken"], "cursor-2")
        self.assertEqual(result["authPathUsed"], "public")
        self.assertEqual(
            result["queryContext"],
            {
                "part": "snippet",
                "q": "mcp server",
                "type": "video",
                "maxResults": 5,
            },
        )
        self.assertEqual(result["sourceOperation"], "search.list")
        self.assertEqual(result["sourceAuthMode"], "mixed/conditional")
        self.assertEqual(result["sourceQuotaCost"], 100)
        self.assertIn("oauth_required", result["sourceAuthConditionNote"])
        self.assertIn("quota guidance differs", result["sourceCaveatNote"])
        self.assertIn("empty result sets", result["sourceNotes"])

    def test_consumer_can_summarize_subscriptions_results_for_higher_layers(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "sub-123", "channelId": execution.arguments.get("channelId")}],
                "nextPageToken": "cursor-2",
                "authPath": "public",
                "requestContext": {
                    "part": "snippet",
                    "selectorName": "channelId",
                    "selectorValue": "UC123",
                    "maxResults": 5,
                },
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_subscriptions_summary(
            arguments={"part": "snippet", "channelId": "UC123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["subscriptionCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "channelId")
        self.assertEqual(result["nextPageToken"], "cursor-2")
        self.assertEqual(result["authPathUsed"], "public")
        self.assertEqual(
            result["requestContext"],
            {
                "part": "snippet",
                "selectorName": "channelId",
                "selectorValue": "UC123",
                "maxResults": 5,
            },
        )
        self.assertEqual(result["sourceOperation"], "subscriptions.list")
        self.assertEqual(result["sourceAuthMode"], "mixed/conditional")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("oauth_required", result["sourceAuthConditionNote"])
        self.assertIn("order", result["sourceNotes"])

    def test_consumer_can_summarize_empty_subscriptions_results_for_higher_layers(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_subscriptions_summary(
            arguments={"part": "snippet", "mySubscribers": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["subscriptionCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "mySubscribers")

    def test_consumer_can_summarize_channel_sections_results_for_higher_layers(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "section-123",
                        "snippet": {"type": "singlePlaylist"},
                        "channelId": execution.arguments.get("channelId"),
                    }
                ]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_channel_sections_summary(
            arguments={"part": "snippet", "channelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["channelSectionCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "channelId")
        self.assertEqual(result["sourceOperation"], "channelSections.list")
        self.assertEqual(result["sourceAuthMode"], "mixed/conditional")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("owner-scoped", result["sourceAuthConditionNote"])
        self.assertIn("lifecycle", result["sourceNotes"])

    def test_consumer_can_summarize_comments_results_for_higher_layers(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "comment-123", "parentId": execution.arguments.get("parentId")}]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_comments_summary(
            arguments={"part": "snippet", "parentId": "comment-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["commentCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "parentId")
        self.assertEqual(result["sourceOperation"], "comments.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("reply lookup", result["sourceNotes"])

    def test_consumer_can_summarize_empty_comments_results_for_higher_layers(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_comments_summary(
            arguments={"part": "snippet", "id": ["comment-123"]},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["commentCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "id")

    def test_consumer_can_summarize_comment_threads_results_for_higher_layers(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "thread-123", "videoId": execution.arguments.get("videoId")}]
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_comment_threads_summary(
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["commentThreadCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "videoId")
        self.assertEqual(result["sourceOperation"], "commentThreads.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("channel-related", result["sourceNotes"])

    def test_consumer_can_summarize_empty_comment_threads_results_for_higher_layers(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_comment_threads_summary(
            arguments={"part": "snippet", "id": ["thread-123"]},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["commentThreadCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "id")

    def test_consumer_can_summarize_guide_categories_results_for_higher_layers(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "GC1", "regionCode": execution.arguments["regionCode"]}],
                "regionCode": execution.arguments["regionCode"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_guide_categories_summary(
            arguments={"part": "snippet", "regionCode": "US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["guideCategoryCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["regionCode"], "US")
        self.assertEqual(result["sourceOperation"], "guideCategories.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)

    def test_consumer_can_summarize_i18n_languages_results_for_higher_layers(self):
        wrapper = build_i18n_languages_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "en", "hl": execution.arguments["hl"]}],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_i18n_languages_summary(
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["languageCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["hl"], "en_US")
        self.assertEqual(result["sourceOperation"], "i18nLanguages.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)

    def test_consumer_can_summarize_i18n_regions_results_for_higher_layers(self):
        wrapper = build_i18n_regions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "US", "hl": execution.arguments["hl"]}],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_i18n_regions_summary(
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["regionCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["hl"], "en_US")
        self.assertEqual(result["sourceOperation"], "i18nRegions.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("region", result["sourceNotes"])
        self.assertIn("hl", result["sourceNotes"])

    def test_consumer_can_summarize_video_abuse_report_reasons_results_for_higher_layers(self):
        wrapper = build_video_abuse_report_reasons_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "reason-1", "hl": execution.arguments["hl"]}],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_video_abuse_report_reasons_summary(
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["abuseReasonCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["hl"], "en_US")
        self.assertEqual(result["sourceOperation"], "videoAbuseReportReasons.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("localization", result["sourceNotes"])
        self.assertIn("hl", result["sourceNotes"])

    def test_consumer_can_summarize_members_results_for_higher_layers(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "member-123", "mode": execution.arguments["mode"]}],
                "mode": execution.arguments["mode"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_members_summary(
            arguments={"part": "snippet", "mode": "updates"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["memberCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["mode"], "updates")
        self.assertEqual(result["sourceOperation"], "members.list")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("owner-only", result["sourceNotes"])

    def test_consumer_can_summarize_memberships_levels_results_for_higher_layers(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "level-123", "part": execution.arguments["part"]}],
                "part": execution.arguments["part"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_memberships_levels_summary(
            arguments={"part": "snippet"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["membershipLevelCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["sourceOperation"], "membershipsLevels.list")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("owner-only", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_images_results_for_higher_layers(self):
        wrapper = build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "image-123", "selector": execution.arguments.get("playlistId")}],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_playlist_images_summary(
            arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistImageCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "playlistId")
        self.assertEqual(result["sourceOperation"], "playlistImages.list")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("pageToken", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_items_results_for_higher_layers(self):
        wrapper = build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "item-123", "selector": execution.arguments.get("playlistId")}],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_playlist_items_summary(
            arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["playlistItemCount"], 1)
        self.assertFalse(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "playlistId")
        self.assertEqual(result["sourceOperation"], "playlistItems.list")
        self.assertEqual(result["sourceAuthMode"], "api_key")
        self.assertEqual(result["sourceQuotaCost"], 1)
        self.assertIn("pageToken", result["sourceNotes"])

    def test_consumer_can_summarize_comment_creation_for_higher_layers(self):
        wrapper = build_comments_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "comment-999",
                "snippet": {"parentId": "comment-123", "textOriginal": "Reply text"},
                "delegatedOwner": "owner-123",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_comment_summary(
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

        self.assertEqual(result["commentId"], "comment-999")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["parentCommentId"], "comment-123")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["sourceOperation"], "comments.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("textOriginal", result["sourceNotes"])

    def test_consumer_can_summarize_comment_thread_creation_for_higher_layers(self):
        wrapper = build_comment_threads_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "thread-999",
                "snippet": {
                    "videoId": "video-123",
                    "topLevelComment": {
                        "id": "comment-999",
                        "snippet": {"textOriginal": "Top-level text"},
                    },
                },
                "delegatedOwner": "owner-123",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_comment_thread_summary(
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

        self.assertEqual(result["commentThreadId"], "thread-999")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["topLevelCommentId"], "comment-999")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["sourceOperation"], "commentThreads.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("topLevelComment", result["sourceNotes"])

    def test_consumer_can_summarize_comment_updates_for_higher_layers(self):
        wrapper = build_comments_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "comment-999",
                "snippet": {"textOriginal": "Updated comment"},
                "delegatedOwner": "owner-123",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_comment_summary(
            arguments={
                "part": "snippet",
                "body": {"id": "comment-999", "snippet": {"textOriginal": "Updated comment"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["commentId"], "comment-999")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["updatedText"], "Updated comment")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["sourceOperation"], "comments.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("body.id", result["sourceNotes"])

    def test_consumer_can_summarize_comment_moderation_for_higher_layers(self):
        wrapper = build_comments_set_moderation_status_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "commentIds": ("comment-123", "comment-456"),
                "isModerated": True,
                "moderationStatus": "rejected",
                "authorBanApplied": True,
                "delegatedOwner": "owner-123",
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.moderate_comments_summary(
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
        self.assertEqual(result["sourceOperation"], "comments.setModerationStatus")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("heldForReview", result["sourceNotes"])

    def test_consumer_can_summarize_comment_deletes_for_higher_layers(self):
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
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_comment_summary(
            arguments={"id": "comment-888", "onBehalfOfContentOwner": "owner-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["commentId"], "comment-888")
        self.assertTrue(result["isDeleted"])
        self.assertTrue(result["delegationApplied"])
        self.assertEqual(result["sourceOperation"], "comments.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("target-state", result["sourceNotes"])

    def test_consumer_can_summarize_empty_channel_sections_results_for_higher_layers(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.fetch_channel_sections_summary(
            arguments={"part": "snippet", "mine": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["channelSectionCount"], 0)
        self.assertTrue(result["isEmpty"])
        self.assertEqual(result["selectorUsed"], "mine")

    def test_consumer_can_summarize_channel_section_creates_for_higher_layers(self):
        wrapper = build_channel_sections_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "section-123",
                "snippet": {"type": "multipleChannels", "title": "Featured channels"},
                "delegatedOwner": "owner-123",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_channel_section_summary(
            arguments={
                "part": "snippet,contentDetails",
                "body": {
                    "snippet": {
                        "type": "multipleChannels",
                        "channelId": "UC123",
                        "title": "Featured channels",
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

        self.assertEqual(result["channelSectionId"], "section-123")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["createdType"], "multipleChannels")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["sourceOperation"], "channelSections.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("snippet.type", result["sourceNotes"])

    def test_consumer_can_summarize_channel_updates_for_higher_layers(self):
        wrapper = build_channels_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "UC999",
                "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                "kind": "youtube#channel",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_channel_summary(
            arguments={
                "part": "brandingSettings",
                "body": {
                    "id": "UC999",
                    "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                },
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["channelId"], "UC999")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["updatedParts"], ("brandingSettings",))
        self.assertEqual(result["sourceOperation"], "channels.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("bannerExternalUrl", result["sourceNotes"])

    def test_consumer_can_summarize_channel_section_updates_for_higher_layers(self):
        wrapper = build_channel_sections_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "section-123",
                "snippet": {"type": "multiplePlaylists", "title": "Updated featured playlists"},
                "delegatedOwner": "owner-123",
                "delegatedOwnerChannel": "UC123",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_channel_section_summary(
            arguments={
                "part": "snippet,contentDetails",
                "body": {
                    "id": "section-123",
                    "snippet": {
                        "type": "multiplePlaylists",
                        "channelId": "UC123",
                        "title": "Updated featured playlists",
                    },
                    "contentDetails": {"playlists": ["PL123", "PL456"]},
                },
                "onBehalfOfContentOwner": "owner-123",
                "onBehalfOfContentOwnerChannel": "UC123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["channelSectionId"], "section-123")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["updatedType"], "multiplePlaylists")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["delegatedOwnerChannel"], "UC123")
        self.assertEqual(result["sourceOperation"], "channelSections.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("body.id", result["sourceNotes"])

    def test_consumer_can_summarize_channel_section_deletes_for_higher_layers(self):
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
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_channel_section_summary(
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

        self.assertEqual(result["channelSectionId"], "section-123")
        self.assertTrue(result["isDeleted"])
        self.assertTrue(result["delegationApplied"])
        self.assertEqual(result["delegatedOwnerChannel"], "UC123")
        self.assertEqual(result["sourceOperation"], "channelSections.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("owner-scoped", result["sourceNotes"])

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

    def test_consumer_can_summarize_caption_creation_for_higher_layers(self):
        wrapper = build_captions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "caption-999", "kind": "youtube#caption"},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_caption_summary(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"videoId": "video-123", "language": "en"}},
                "media": {"mimeType": "text/plain", "content": "caption payload"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-999")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["sourceOperation"], "captions.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 400)
        self.assertIn("body", result["sourceNotes"])
        self.assertIn("media", result["sourceNotes"])

    def test_consumer_can_summarize_caption_updates_for_higher_layers(self):
        wrapper = build_captions_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "caption-555", "kind": "youtube#caption"},
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_caption_summary(
            arguments={
                "part": "snippet",
                "body": {"id": "caption-555", "snippet": {"language": "en"}},
                "media": {"mimeType": "text/plain", "content": "updated caption payload"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-555")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["sourceOperation"], "captions.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 450)
        self.assertIn("body", result["sourceNotes"])
        self.assertIn("media", result["sourceNotes"])

    def test_consumer_can_summarize_caption_downloads_for_higher_layers(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "content": "caption line 1",
                "contentFormat": execution.arguments.get("tfmt"),
                "contentLanguage": execution.arguments.get("tlang"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.download_caption_summary(
            arguments={"id": "caption-777", "tfmt": "srt", "tlang": "es"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-777")
        self.assertTrue(result["hasContent"])
        self.assertEqual(result["contentFormat"], "srt")
        self.assertEqual(result["contentLanguage"], "es")
        self.assertEqual(result["sourceOperation"], "captions.download")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 200)
        self.assertIn("tfmt", result["sourceNotes"])

    def test_consumer_can_summarize_caption_deletes_for_higher_layers(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "captionId": execution.arguments["id"],
                "isDeleted": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_caption_summary(
            arguments={"id": "caption-888", "onBehalfOfContentOwner": "owner-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-888")
        self.assertTrue(result["isDeleted"])
        self.assertTrue(result["delegationApplied"])
        self.assertEqual(result["sourceOperation"], "captions.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("ownership", result["sourceNotes"])

    def test_consumer_can_summarize_channel_banner_uploads_for_higher_layers(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "bannerUrl": "https://yt.example/banner",
                "isUploaded": True,
                "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.upload_channel_banner_summary(
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
        self.assertTrue(result["isUploaded"])
        self.assertTrue(result["delegationApplied"])
        self.assertEqual(result["sourceOperation"], "channelBanners.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("response URL", result["sourceNotes"])

    def test_consumer_can_summarize_thumbnail_updates_for_higher_layers(self):
        wrapper = wrappers_module.build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "videoId": execution.arguments["videoId"],
                "thumbnailUrl": "https://yt.example/thumb.jpg",
                "isUpdated": True,
                "kind": "youtube#thumbnailSetResponse",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.set_thumbnail_summary(
            arguments={
                "videoId": "video-123",
                "media": {"mimeType": "image/png", "content": b"thumbnail-bytes"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["thumbnailUrl"], "https://yt.example/thumb.jpg")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["sourceOperation"], "thumbnails.set")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertEqual(result["sourceRequiredFields"], ("videoId", "media"))
        self.assertEqual(result["sourcePathShape"], "/youtube/v3/thumbnails/set")
        self.assertIn("videoId", result["sourceNotes"])
        self.assertIn("media", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_image_creation_for_higher_layers(self):
        wrapper = build_playlist_images_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-image-123",
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlistImage",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_playlist_image_summary(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "type": "featured"}},
                "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistImageId"], "playlist-image-123")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["sourceOperation"], "playlistImages.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("body", result["sourceNotes"])
        self.assertIn("media", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_item_creation_for_higher_layers(self):
        wrapper = build_playlist_items_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-item-123",
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlistItem",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_playlist_item_summary(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistItemId"], "playlist-item-123")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["sourceOperation"], "playlistItems.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("playlistId", result["sourceNotes"])
        self.assertIn("videoId", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_creation_for_higher_layers(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-123",
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_playlist_summary(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistId"], "playlist-123")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["title"], "Layer 1 Playlist")
        self.assertEqual(result["sourceOperation"], "playlists.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertEqual(result["sourceRequiredFields"], ("part", "body"))
        self.assertEqual(result["sourceWritablePart"], "snippet")
        self.assertEqual(result["sourceRequiredTitleField"], "body.snippet.title")
        self.assertIn("title", result["sourceNotes"])
        self.assertIn("snippet", result["sourceNotes"])
        self.assertIn("body.status", result["sourceNotes"])

    def test_consumer_can_summarize_subscription_creation_for_higher_layers(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "subscription-123",
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#subscription",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.create_subscription_summary(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["subscriptionId"], "subscription-123")
        self.assertTrue(result["isCreated"])
        self.assertEqual(result["targetChannelId"], "UC123")
        self.assertEqual(result["sourceOperation"], "subscriptions.insert")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertEqual(result["sourceRequiredFields"], ("part", "body"))
        self.assertEqual(result["sourceWritablePart"], "snippet")
        self.assertEqual(result["sourceRequiredTargetField"], "body.snippet.resourceId.channelId")
        self.assertIn("resourceId.channelId", result["sourceNotes"])
        self.assertIn("part=snippet", result["sourceNotes"])
        self.assertIn("body.status", result["sourceNotes"])

    def test_consumer_can_summarize_subscription_deletes_for_higher_layers(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "subscriptionId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_subscription_summary(
            arguments={"id": "subscription-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["subscriptionId"], "subscription-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["sourceOperation"], "subscriptions.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("id", result["sourceNotes"])
        self.assertIn("target-state", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_item_updates_for_higher_layers(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlistItem",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_playlist_item_summary(
            arguments={
                "part": "snippet",
                "body": {
                    "id": "playlist-item-123",
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"videoId": "video-123"},
                    },
                },
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistItemId"], "playlist-item-123")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(result["sourceOperation"], "playlistItems.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("body.id", result["sourceNotes"])
        self.assertIn("playlistId", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_updates_for_higher_layers(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_playlist_summary(
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistId"], "playlist-123")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["title"], "Layer 1 Playlist")
        self.assertEqual(result["sourceOperation"], "playlists.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertEqual(result["sourceRequiredFields"], ("part", "body"))
        self.assertEqual(result["sourceWritablePart"], "snippet")
        self.assertEqual(result["sourceRequiredIdentifierField"], "body.id")
        self.assertEqual(result["sourceRequiredTitleField"], "body.snippet.title")
        self.assertIn("body.id", result["sourceNotes"])
        self.assertIn("body.snippet.description", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_image_updates_for_higher_layers(self):
        wrapper = build_playlist_images_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "snippet": execution.arguments["body"]["snippet"],
                "kind": "youtube#playlistImage",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.update_playlist_image_summary(
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "featured"}},
                "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistImageId"], "playlist-image-123")
        self.assertTrue(result["isUpdated"])
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["sourceOperation"], "playlistImages.update")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("body", result["sourceNotes"])
        self.assertIn("media", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_image_deletes_for_higher_layers(self):
        wrapper = build_playlist_images_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistImageId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_playlist_image_summary(
            arguments={"id": "playlist-image-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistImageId"], "playlist-image-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["sourceOperation"], "playlistImages.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("id", result["sourceNotes"])
        self.assertIn("target-state", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_item_deletes_for_higher_layers(self):
        wrapper = build_playlist_items_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistItemId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_playlist_item_summary(
            arguments={"id": "playlist-item-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistItemId"], "playlist-item-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["sourceOperation"], "playlistItems.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("id", result["sourceNotes"])
        self.assertIn("target-state", result["sourceNotes"])

    def test_consumer_can_summarize_playlist_deletes_for_higher_layers(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )
        consumer = RepresentativeHigherLayerConsumer(wrapper=wrapper, executor=executor)

        result = consumer.delete_playlist_summary(
            arguments={"id": "playlist-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistId"], "playlist-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["sourceOperation"], "playlists.delete")
        self.assertEqual(result["sourceAuthMode"], "oauth_required")
        self.assertEqual(result["sourceQuotaCost"], 50)
        self.assertIn("id", result["sourceNotes"])
        self.assertIn("target-state", result["sourceNotes"])


if __name__ == "__main__":
    unittest.main()
