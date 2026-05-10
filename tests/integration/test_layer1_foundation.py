import io
import os
import sys
import unittest
from urllib.error import HTTPError

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.executor import IntegrationExecutor, build_observability_hooks
from mcp_server.integrations.retry import RetryPolicy
from mcp_server.integrations.youtube import build_youtube_data_api_transport
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
    build_videos_list_wrapper,
    build_thumbnails_set_wrapper,
    build_video_categories_list_wrapper,
    build_video_abuse_report_reasons_list_wrapper,
    build_playlists_update_wrapper,
    build_playlists_list_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)
from mcp_server.observability import InMemoryObservability


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, object]):
        import json

        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


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

    def test_i18n_languages_list_wrapper_executes_display_language_requests_through_shared_executor(self):
        wrapper = build_i18n_languages_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "en",
                        "hl": execution.arguments["hl"],
                        "kind": "youtube#i18nLanguage",
                    }
                ],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "en")
        self.assertEqual(result["hl"], "en_US")

    def test_i18n_languages_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_i18n_languages_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "hl": execution.arguments["hl"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["hl"], "en_US")

    def test_i18n_languages_list_wrapper_rejects_missing_display_language_requests(self):
        wrapper = build_i18n_languages_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: hl"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_i18n_regions_list_wrapper_executes_display_language_requests_through_shared_executor(self):
        wrapper = build_i18n_regions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "US",
                        "hl": execution.arguments["hl"],
                        "kind": "youtube#i18nRegion",
                    }
                ],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "US")
        self.assertEqual(result["hl"], "en_US")

    def test_i18n_regions_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_i18n_regions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "hl": execution.arguments["hl"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["hl"], "en_US")

    def test_i18n_regions_list_wrapper_rejects_missing_display_language_requests(self):
        wrapper = build_i18n_regions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: hl"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_video_abuse_report_reasons_list_wrapper_executes_display_language_requests_through_shared_executor(self):
        wrapper = build_video_abuse_report_reasons_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "reason-1",
                        "hl": execution.arguments["hl"],
                        "kind": "youtube#videoAbuseReportReason",
                    }
                ],
                "hl": execution.arguments["hl"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "reason-1")
        self.assertEqual(result["hl"], "en_US")

    def test_video_abuse_report_reasons_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_video_abuse_report_reasons_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "hl": execution.arguments["hl"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["hl"], "en_US")

    def test_video_abuse_report_reasons_list_wrapper_rejects_missing_display_language_requests(self):
        wrapper = build_video_abuse_report_reasons_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: hl"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_video_categories_list_wrapper_executes_region_requests_through_shared_executor(self):
        wrapper = build_video_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "cat-1",
                        "regionCode": execution.arguments["regionCode"],
                        "kind": "youtube#videoCategory",
                    }
                ],
                "selectedSelector": "regionCode",
                "regionCode": execution.arguments["regionCode"],
                "hl": execution.arguments.get("hl"),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "regionCode": "US", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "cat-1")
        self.assertEqual(result["regionCode"], "US")
        self.assertEqual(result["selectedSelector"], "regionCode")

    def test_video_categories_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_video_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [],
                "selectedSelector": "regionCode",
                "regionCode": execution.arguments["regionCode"],
                "hl": execution.arguments.get("hl"),
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

        self.assertEqual(result["items"], [])
        self.assertEqual(result["regionCode"], "US")

    def test_video_categories_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_video_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_video_categories_list_wrapper_rejects_conflicting_selector_requests(self):
        wrapper = build_video_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": "cat-1", "regionCode": "US"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_videos_list_wrapper_executes_direct_id_requests_through_shared_executor(self):
        wrapper = build_videos_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": execution.arguments["id"],
                        "kind": "youtube#video",
                    }
                ],
                "selectedSelector": "id",
                "id": execution.arguments["id"],
                "authPath": "api_key",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "video-123")
        self.assertEqual(result["selectedSelector"], "id")
        self.assertEqual(result["authPath"], "api_key")

    def test_videos_list_wrapper_executes_chart_requests_through_shared_executor(self):
        wrapper = build_videos_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "video-234",
                        "chart": execution.arguments["chart"],
                        "kind": "youtube#video",
                    }
                ],
                "selectedSelector": "chart",
                "chart": execution.arguments["chart"],
                "regionCode": execution.arguments.get("regionCode"),
                "videoCategoryId": execution.arguments.get("videoCategoryId"),
                "authPath": "api_key",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "chart": "mostPopular",
                "regionCode": "US",
                "videoCategoryId": "10",
            },
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "video-234")
        self.assertEqual(result["selectedSelector"], "chart")
        self.assertEqual(result["regionCode"], "US")
        self.assertEqual(result["videoCategoryId"], "10")

    def test_videos_list_wrapper_executes_my_rating_requests_through_shared_executor(self):
        wrapper = build_videos_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "video-345",
                        "rating": execution.arguments["myRating"],
                        "kind": "youtube#video",
                    }
                ],
                "selectedSelector": "myRating",
                "myRating": execution.arguments["myRating"],
                "authPath": "oauth_required",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "myRating": "like"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "video-345")
        self.assertEqual(result["selectedSelector"], "myRating")
        self.assertEqual(result["authPath"], "oauth_required")

    def test_videos_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_videos_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [],
                "selectedSelector": "id",
                "id": execution.arguments["id"],
                "authPath": "api_key",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["selectedSelector"], "id")
        self.assertEqual(result["id"], "video-123")

    def test_videos_list_wrapper_rejects_conflicting_selector_requests(self):
        wrapper = build_videos_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": "video-123", "chart": "mostPopular"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_members_list_wrapper_executes_owner_scoped_requests_through_shared_executor(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "member-123",
                        "mode": execution.arguments["mode"],
                        "kind": "youtube#member",
                    }
                ],
                "mode": execution.arguments["mode"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "mode": "updates"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "member-123")
        self.assertEqual(result["mode"], "updates")

    def test_members_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "mode": execution.arguments["mode"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "mode": "updates"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["mode"], "updates")

    def test_members_list_wrapper_rejects_missing_mode_requests(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: mode"):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_members_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Membership access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Membership access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mode": "updates"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_memberships_levels_list_wrapper_executes_owner_scoped_requests_through_shared_executor(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "level-123",
                        "part": execution.arguments["part"],
                        "kind": "youtube#membershipsLevel",
                    }
                ],
                "part": execution.arguments["part"],
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "level-123")
        self.assertEqual(result["part"], "snippet")

    def test_memberships_levels_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {"items": [], "part": execution.arguments["part"]},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["part"], "snippet")

    def test_memberships_levels_list_wrapper_rejects_missing_part_requests(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.call(
                executor,
                arguments={},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_memberships_levels_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Membership level access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Membership level access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_images_list_wrapper_executes_playlist_requests_through_shared_executor(self):
        wrapper = build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "image-123",
                        "playlistId": execution.arguments.get("playlistId"),
                        "kind": "youtube#playlistImage",
                    }
                ],
                "selector": "playlistId",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["playlistId"], "PL123")
        self.assertEqual(result["selector"], "playlistId")

    def test_playlist_images_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [], "selector": "id"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "image-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["selector"], "id")

    def test_playlist_images_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError, "exactly one selector is required from: playlistId, id"
        ):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlist_images_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": "image-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlists_list_wrapper_executes_channel_requests_through_shared_executor(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "PL123",
                        "channelId": execution.arguments.get("channelId"),
                        "kind": "youtube#playlist",
                    }
                ],
                "selector": "channelId",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "channelId": "UC123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["channelId"], "UC123")
        self.assertEqual(result["selector"], "channelId")

    def test_playlists_list_wrapper_executes_id_requests_through_shared_executor(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": execution.arguments.get("id"), "kind": "youtube#playlist"}],
                "selector": "id",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "PL123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "PL123")
        self.assertEqual(result["selector"], "id")

    def test_playlists_list_wrapper_executes_mine_requests_through_shared_executor(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "PL234", "mine": bool(execution.arguments.get("mine"))}],
                "selector": "mine",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "mine": True, "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertTrue(result["items"][0]["mine"])
        self.assertEqual(result["selector"], "mine")

    def test_playlists_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [], "selector": "id"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "PL123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["selector"], "id")

    def test_playlists_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError, "exactly one selector is required from: channelId, id, mine"
        ):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlists_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_subscriptions_list_wrapper_executes_channel_requests_through_shared_executor(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "sub-123",
                        "channelId": execution.arguments.get("channelId"),
                        "kind": "youtube#subscription",
                    }
                ],
                "selector": "channelId",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "channelId": "UC123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["channelId"], "UC123")
        self.assertEqual(result["selector"], "channelId")

    def test_subscriptions_list_wrapper_executes_private_requests_through_shared_executor(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "sub-234", "privateSelector": bool(execution.arguments.get("mySubscribers"))}],
                "selector": "mySubscribers",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "mySubscribers": True, "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertTrue(result["items"][0]["privateSelector"])
        self.assertEqual(result["selector"], "mySubscribers")

    def test_subscriptions_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [], "selector": "id"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "sub-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["selector"], "id")

    def test_subscriptions_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError,
            "exactly one selector is required from: channelId, id, mine, myRecentSubscribers, mySubscribers",
        ):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_subscriptions_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Subscription access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mySubscribers": True},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_items_list_wrapper_executes_playlist_requests_through_shared_executor(self):
        wrapper = build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [
                    {
                        "id": "item-123",
                        "playlistId": execution.arguments.get("playlistId"),
                        "kind": "youtube#playlistItem",
                    }
                ],
                "selector": "playlistId",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["playlistId"], "PL123")
        self.assertEqual(result["selector"], "playlistId")

    def test_playlist_items_list_wrapper_treats_empty_results_as_success(self):
        wrapper = build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": [], "selector": "id"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "id": "item-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["selector"], "id")

    def test_playlist_items_list_wrapper_rejects_missing_selector_requests(self):
        wrapper = build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError, "exactly one selector is required from: playlistId, id"
        ):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_items_list_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item access denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item access denied") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": "item-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

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

    def test_playlist_images_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_images_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistImageId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "playlist-image-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistImageId"], "playlist-image-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_playlist_images_delete_wrapper_rejects_invalid_identifier_shapes_before_executor(self):
        wrapper = build_playlist_images_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistImageId": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id must identify one playlist image"):
            wrapper.call(
                executor,
                arguments={"id": ["playlist-image-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlist_images_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_images_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "playlist-image-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_items_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_items_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistItemId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "playlist-item-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistItemId"], "playlist-item-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_playlist_items_delete_wrapper_rejects_invalid_identifier_shapes_before_executor(self):
        wrapper = build_playlist_items_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistItemId": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id must identify one playlist item"):
            wrapper.call(
                executor,
                arguments={"id": ["playlist-item-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlist_items_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_items_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "playlist-item-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlists_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "playlistId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "playlist-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["playlistId"], "playlist-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_playlists_delete_wrapper_rejects_invalid_identifier_shapes_before_executor(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistId": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id must identify one playlist"):
            wrapper.call(
                executor,
                arguments={"id": ["playlist-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlists_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "playlist-123"},
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

    def test_playlist_images_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_images_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-image-123",
                "playlistId": execution.arguments["body"]["snippet"]["playlistId"],
                "kind": "youtube#playlistImage",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
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

        self.assertEqual(result["id"], "playlist-image-123")
        self.assertEqual(result["playlistId"], "PL123")

    def test_playlist_images_insert_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_images_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image create denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image create denied") as context:
            wrapper.call(
                executor,
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

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_images_insert_wrapper_preserves_upstream_create_failures_from_shared_executor(self):
        wrapper = build_playlist_images_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image create rejected"),
                    category="upstream_service",
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image create rejected"):
            wrapper.call(
                executor,
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

    def test_thumbnails_set_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda request, timeout: _FakeHTTPResponse({"url": "https://yt.example/thumb.jpg"})
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
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

    def test_thumbnails_set_wrapper_rejects_invalid_upload_requests_before_executor(self):
        wrapper = build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"videoId": "video-123", "isUpdated": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.call(
                executor,
                arguments={
                    "videoId": "video-123",
                    "media": {"mimeType": "image/png", "content": b""},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_thumbnails_set_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda request, timeout: (_ for _ in ()).throw(
                    HTTPError(
                        url="https://www.googleapis.com/youtube/v3/thumbnails/set",
                        code=403,
                        msg="Forbidden",
                        hdrs=None,
                        fp=io.BytesIO(b'{"error":{"message":"Thumbnail update denied"}}'),
                    )
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Thumbnail update denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "videoId": "video-123",
                    "media": {"mimeType": "image/png", "content": b"thumbnail-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_thumbnails_set_wrapper_preserves_target_video_failures_from_shared_executor(self):
        wrapper = build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda request, timeout: (_ for _ in ()).throw(
                    HTTPError(
                        url="https://www.googleapis.com/youtube/v3/thumbnails/set",
                        code=404,
                        msg="Not Found",
                        hdrs=None,
                        fp=io.BytesIO(b'{"error":{"message":"Target video cannot accept thumbnail update"}}'),
                    )
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Target video cannot accept thumbnail update") as context:
            wrapper.call(
                executor,
                arguments={
                    "videoId": "video-123",
                    "media": {"mimeType": "image/png", "content": b"thumbnail-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "target_video")

    def test_thumbnails_set_wrapper_preserves_upstream_update_failures_from_shared_executor(self):
        wrapper = build_thumbnails_set_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda request, timeout: (_ for _ in ()).throw(
                    HTTPError(
                        url="https://www.googleapis.com/youtube/v3/thumbnails/set",
                        code=409,
                        msg="Conflict",
                        hdrs=None,
                        fp=io.BytesIO(b'{"error":{"message":"Thumbnail update rejected"}}'),
                    )
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Thumbnail update rejected") as context:
            wrapper.call(
                executor,
                arguments={
                    "videoId": "video-123",
                    "media": {"mimeType": "image/png", "content": b"thumbnail-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_playlist_items_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_items_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-item-123",
                "playlistId": execution.arguments["body"]["snippet"]["playlistId"],
                "videoId": execution.arguments["body"]["snippet"]["resourceId"]["videoId"],
                "kind": "youtube#playlistItem",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "playlist-item-123")
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")

    def test_playlist_items_insert_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_items_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item create denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item create denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_items_insert_wrapper_preserves_upstream_create_failures_from_shared_executor(self):
        wrapper = build_playlist_items_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item create rejected"),
                    category="upstream_service",
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item create rejected"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlists_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "playlist-123",
                "title": execution.arguments["body"]["snippet"]["title"],
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_playlists_insert_wrapper_preserves_part_and_title_in_successful_results(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "playlist-123",
                "part": "snippet",
                "title": "Layer 1 Playlist",
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_playlists_insert_wrapper_preserves_invalid_request_failures_from_shared_executor(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist create payload invalid"),
                    category="invalid_request",
                    status_code=400,
                    details={"reason": "required"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist create payload invalid") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_playlists_insert_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist create denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist create denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlists_insert_wrapper_preserves_upstream_create_failures_from_shared_executor(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist create rejected by policy"),
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Playlist create rejected by policy",
        ) as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_subscriptions_insert_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": "subscription-123",
                "targetChannelId": execution.arguments["body"]["snippet"]["resourceId"]["channelId"],
                "kind": "youtube#subscription",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "subscription-123")
        self.assertEqual(result["targetChannelId"], "UC123")

    def test_subscriptions_insert_wrapper_preserves_part_and_target_channel_in_successful_results(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "subscription-123",
                "snippet": {"resourceId": {"channelId": "UC123"}},
                "kind": "youtube#subscription",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["targetChannelId"], "UC123")

    def test_subscriptions_insert_wrapper_preserves_invalid_request_failures_from_shared_executor(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription create payload invalid"),
                    category="invalid_request",
                    status_code=400,
                    details={"reason": "required"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Subscription create payload invalid",
        ) as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_subscriptions_insert_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription create denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Subscription create denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_subscriptions_insert_wrapper_preserves_duplicate_target_failures_from_shared_executor(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription already exists"),
                    category="duplicate_or_ineligible_target",
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Subscription already exists") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "duplicate_or_ineligible_target")

    def test_subscriptions_insert_wrapper_preserves_upstream_create_failures_from_shared_executor(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription create rejected by policy"),
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Subscription create rejected by policy",
        ) as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_subscriptions_delete_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "subscriptionId": execution.arguments["id"],
                "isDeleted": True,
                "upstreamBodyState": "empty",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"id": "subscription-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["subscriptionId"], "subscription-123")
        self.assertTrue(result["isDeleted"])

    def test_subscriptions_delete_wrapper_rejects_invalid_identifier_shapes_before_executor(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"subscriptionId": "subscription-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id must identify one subscription"):
            wrapper.call(
                executor,
                arguments={"id": ["subscription-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_subscriptions_delete_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription delete denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Subscription delete denied") as context:
            wrapper.call(
                executor,
                arguments={"id": "subscription-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_subscriptions_delete_wrapper_preserves_not_found_failures_from_shared_executor(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Subscription not found"),
                    category="not_found",
                    status_code=404,
                    details={"reason": "notFound"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Subscription not found") as context:
            wrapper.call(
                executor,
                arguments={"id": "subscription-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_playlists_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "title": execution.arguments["body"]["snippet"]["title"],
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_playlists_update_wrapper_preserves_part_and_title_in_successful_results(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {
                "id": "playlist-123",
                "part": "snippet",
                "title": "Layer 1 Playlist",
                "kind": "youtube#playlist",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_playlists_update_wrapper_preserves_invalid_request_failures_from_shared_executor(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist update payload invalid"),
                    category="invalid_request",
                    status_code=400,
                    details={"reason": "required"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist update payload invalid") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_playlists_update_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist update denied") as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "auth")

    def test_playlists_delete_wrapper_preserves_invalid_request_failures_from_shared_executor(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist delete payload invalid"),
                    category="invalid_request",
                    status_code=400,
                    details={"reason": "required"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist delete payload invalid") as context:
            wrapper.call(
                executor,
                arguments={"id": "playlist-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_playlists_delete_wrapper_preserves_upstream_delete_failures_from_shared_executor(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist delete rejected by policy"),
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Playlist delete rejected by policy",
        ) as context:
            wrapper.call(
                executor,
                arguments={"id": "playlist-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_playlists_update_wrapper_preserves_upstream_update_failures_from_shared_executor(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist update rejected by policy"),
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            NormalizedUpstreamError,
            "Playlist update rejected by policy",
        ) as context:
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_playlist_items_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "playlistId": execution.arguments["body"]["snippet"]["playlistId"],
                "videoId": execution.arguments["body"]["snippet"]["resourceId"]["videoId"],
                "kind": "youtube#playlistItem",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
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

        self.assertEqual(result["id"], "playlist-item-123")
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")

    def test_playlist_items_update_wrapper_rejects_unsupported_write_shapes_before_executor(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "should-not-run"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "body.snippet.resourceId.videoId is required"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123", "resourceId": {}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlist_items_update_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item update denied") as context:
            wrapper.call(
                executor,
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

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_items_update_wrapper_preserves_upstream_update_failures_from_shared_executor(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist item update rejected"),
                    category="upstream_service",
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist item update rejected"):
            wrapper.call(
                executor,
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

    def test_playlist_images_update_wrapper_executes_authorized_requests_through_shared_executor(self):
        wrapper = build_playlist_images_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "id": execution.arguments["body"]["id"],
                "playlistId": execution.arguments["body"]["snippet"]["playlistId"],
                "kind": "youtube#playlistImage",
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
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

        self.assertEqual(result["id"], "playlist-image-123")
        self.assertEqual(result["playlistId"], "PL123")

    def test_playlist_images_update_wrapper_preserves_auth_failures_from_shared_executor(self):
        wrapper = build_playlist_images_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image update denied"),
                    status_code=403,
                    details={"reason": "forbidden"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image update denied") as context:
            wrapper.call(
                executor,
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

        self.assertEqual(context.exception.category, "auth")

    def test_playlist_images_update_wrapper_preserves_upstream_update_failures_from_shared_executor(self):
        wrapper = build_playlist_images_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Playlist image update rejected"),
                    category="upstream_service",
                    status_code=409,
                    details={"reason": "conflict"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Playlist image update rejected") as context:
            wrapper.call(
                executor,
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

        self.assertEqual(context.exception.category, "upstream_service")

        self.assertEqual(context.exception.category, "upstream_service")

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

    def test_search_list_wrapper_executes_supported_search_requests_through_shared_executor(self):
        wrapper = build_search_list_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda _request, timeout: _FakeHTTPResponse(
                    {"items": [{"id": {"videoId": "video-123"}}], "nextPageToken": "cursor-2"}
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={
                "part": "snippet",
                "q": "mcp server",
                "type": "video",
                "publishedAfter": "2026-01-01T00:00:00Z",
                "maxResults": 5,
            },
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(
            result["queryContext"],
            {
                "part": "snippet",
                "q": "mcp server",
                "type": "video",
                "publishedAfter": "2026-01-01T00:00:00Z",
                "maxResults": 5,
            },
        )
        self.assertEqual(result["authPath"], "public")
        self.assertEqual(result["nextPageToken"], "cursor-2")

    def test_search_list_wrapper_preserves_invalid_request_failures_from_shared_executor(self):
        wrapper = build_search_list_wrapper()
        executor = IntegrationExecutor(
            transport=build_youtube_data_api_transport(
                opener=lambda _request, timeout: (_ for _ in ()).throw(
                    HTTPError(
                        url="https://www.googleapis.com/youtube/v3/search",
                        code=400,
                        msg="Bad Request",
                        hdrs=None,
                        fp=io.BytesIO(b'{"error":{"message":"videoDuration requires type=video"}}'),
                    )
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "videoDuration requires type=video") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "q": "mcp server"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_search_list_wrapper_preserves_upstream_search_failures_from_shared_executor(self):
        wrapper = build_search_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: (_ for _ in ()).throw(
                normalize_upstream_error(
                    RuntimeError("Search backend unavailable"),
                    category="upstream_service",
                    status_code=503,
                    details={"reason": "backend_unavailable"},
                )
            ),
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(NormalizedUpstreamError, "Search backend unavailable") as context:
            wrapper.call(
                executor,
                arguments={"part": "snippet", "q": "mcp server"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

        self.assertEqual(context.exception.category, "upstream_service")


if __name__ == "__main__":
    unittest.main()
