import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

import mcp_server.integrations as integrations_package
from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.errors import NormalizedUpstreamError, normalize_upstream_error
from mcp_server.integrations.executor import IntegrationExecutor, IntegrationHooks, RequestExecution, timed_execution
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
    build_playlist_images_update_wrapper,
    build_playlist_items_delete_wrapper,
    build_playlist_items_insert_wrapper,
    build_playlist_items_update_wrapper,
    build_playlists_delete_wrapper,
    build_playlists_insert_wrapper,
    build_search_list_wrapper,
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
    build_playlists_update_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)


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


class Layer1FoundationUnitTests(unittest.TestCase):
    def test_activities_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_activities_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "activities.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/activities")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertIn("channelId", wrapper.metadata.auth_condition_note)

    def test_activities_list_wrapper_requires_one_selector_field(self):
        wrapper = build_activities_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_activities_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_activities_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "mine": True}
            )

    def test_activities_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_activities_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: playlistId"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "playlistId": "PL123"}
            )

    def test_activities_list_wrapper_rejects_authorized_selector_with_api_key_mode(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "mine requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_activities_list_wrapper_rejects_public_selector_with_oauth_mode(self):
        wrapper = build_activities_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_channels_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_channels_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channels.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channels")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertIn("forHandle", wrapper.metadata.auth_condition_note)
        self.assertIn("forUsername", wrapper.metadata.request_shape.optional_fields)

    def test_channels_list_wrapper_requires_one_selector_field(self):
        wrapper = build_channels_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_channels_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_channels_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": "UC123", "mine": True}
            )

    def test_channels_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_channels_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: channelId"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": "UC123", "channelId": "UC999"}
            )

    def test_channels_list_wrapper_requires_oauth_mode_for_mine_selector(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "mine requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channels_list_wrapper_requires_api_key_mode_for_public_selectors(self):
        wrapper = build_channels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "forHandle requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "forHandle": "@channel-handle"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_channels_list_wrapper_allows_username_style_selector(self):
        wrapper = build_channels_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {"part": "snippet", "forUsername": "legacy-user"}
        )

    def test_channels_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_channels_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channels.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channels")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("brandingSettings", wrapper.metadata.notes)
        self.assertIn("localizations", wrapper.metadata.notes)

    def test_channels_update_wrapper_requires_body_field(self):
        wrapper = build_channels_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "brandingSettings"})

    def test_channels_update_wrapper_rejects_unsupported_part(self):
        wrapper = build_channels_update_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: statistics"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "statistics", "body": {"id": "UC123", "statistics": {"viewCount": "1"}}}
            )

    def test_channels_update_wrapper_rejects_part_body_mismatch(self):
        wrapper = build_channels_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.brandingSettings is required for selected part"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "brandingSettings", "body": {"id": "UC123", "localizations": {"en": {"title": "Title"}}}}
            )

    def test_channels_update_wrapper_rejects_read_only_fields(self):
        wrapper = build_channels_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.statistics is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "brandingSettings",
                    "body": {
                        "id": "UC123",
                        "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                        "statistics": {"viewCount": "1"},
                    },
                }
            )

    def test_channels_update_wrapper_requires_oauth_mode(self):
        wrapper = build_channels_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "UC123", "kind": "youtube#channel"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channels.update requires oauth_required auth"):
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
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_channel_sections_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channelSections.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channelSections")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(wrapper.metadata.request_shape.exactly_one_of, ("channelId", "id", "mine"))
        self.assertIn("channelId", wrapper.metadata.auth_condition_note)
        self.assertIn("lifecycle", wrapper.metadata.notes)

    def test_channel_sections_list_wrapper_requires_one_selector_field(self):
        wrapper = build_channel_sections_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_channel_sections_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_channel_sections_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "mine": True}
            )

    def test_channel_sections_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_channel_sections_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: forHandle"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "forHandle": "@channel"}
            )

    def test_channel_sections_list_wrapper_requires_oauth_mode_for_mine_selector(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "mine requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_list_wrapper_requires_api_key_mode_for_public_selectors(self):
        wrapper = build_channel_sections_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comments_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_comments_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "comments.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/comments")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(wrapper.metadata.request_shape.exactly_one_of, ("id", "parentId"))
        self.assertIn("textFormat", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("no-match", wrapper.metadata.notes)

    def test_comments_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comments_list_wrapper))

    def test_comments_insert_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comments_insert_wrapper))

    def test_comments_list_wrapper_requires_one_selector_field(self):
        wrapper = build_comments_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_comments_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_comments_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": ["comment-123"], "parentId": "comment-456"}
            )

    def test_comments_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_comments_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: videoId"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": ["comment-123"], "videoId": "video-123"}
            )

    def test_comments_list_wrapper_allows_selector_specific_optional_fields(self):
        wrapper = build_comments_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "parentId": "comment-123",
                "pageToken": "cursor-1",
                "maxResults": 5,
                "textFormat": "plainText",
            }
        )

    def test_comments_list_wrapper_requires_api_key_mode_for_id_selector(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": ["comment-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comments_list_wrapper_requires_api_key_mode_for_parent_selector(self):
        wrapper = build_comments_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "parentId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "parentId": "comment-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comment_threads_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_comment_threads_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "commentThreads.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/commentThreads")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(
            wrapper.metadata.request_shape.exactly_one_of,
            ("videoId", "allThreadsRelatedToChannelId", "id"),
        )
        self.assertIn("searchTerms", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("no-match", wrapper.metadata.notes)

    def test_comment_threads_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comment_threads_list_wrapper))

    def test_comment_threads_insert_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comment_threads_insert_wrapper))

    def test_comment_threads_list_wrapper_requires_one_selector_field(self):
        wrapper = build_comment_threads_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_comment_threads_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_comment_threads_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "videoId": "video-123",
                    "id": ["thread-456"],
                }
            )

    def test_comment_threads_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_comment_threads_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: parentId"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "videoId": "video-123", "parentId": "comment-123"}
            )

    def test_comment_threads_list_wrapper_allows_selector_specific_optional_fields(self):
        wrapper = build_comment_threads_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "allThreadsRelatedToChannelId": "UC123",
                "pageToken": "cursor-1",
                "maxResults": 5,
                "order": "time",
                "searchTerms": "release",
                "textFormat": "plainText",
            }
        )

    def test_comment_threads_list_wrapper_requires_api_key_mode_for_video_selector(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "videoId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "videoId": "video-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_comment_threads_list_wrapper_requires_api_key_mode_for_channel_selector(self):
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

    def test_comment_threads_list_wrapper_requires_api_key_mode_for_id_selector(self):
        wrapper = build_comment_threads_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "id requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "id": ["thread-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_guide_categories_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_guide_categories_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "guideCategories.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/guideCategories")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.lifecycle_state, "deprecated")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "regionCode"))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("deprecated", wrapper.metadata.caveat_note)
        self.assertIn("regionCode", wrapper.metadata.notes)

    def test_guide_categories_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_guide_categories_list_wrapper))

    def test_guide_categories_list_wrapper_requires_part_and_region_code(self):
        wrapper = build_guide_categories_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"regionCode": "US"})

        with self.assertRaisesRegex(ValueError, "missing required field: regionCode"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_guide_categories_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_guide_categories_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: pageToken"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "regionCode": "US", "pageToken": "cursor-1"}
            )

    def test_guide_categories_list_wrapper_requires_api_key_mode(self):
        wrapper = build_guide_categories_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "guideCategories.list requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "regionCode": "US"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_i18n_languages_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_i18n_languages_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "i18nLanguages.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/i18nLanguages")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "hl"))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("hl", wrapper.metadata.notes)
        self.assertIn("localization", wrapper.metadata.notes)

    def test_i18n_languages_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_i18n_languages_list_wrapper))

    def test_i18n_languages_list_wrapper_requires_part_and_hl(self):
        wrapper = build_i18n_languages_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"hl": "en_US"})

        with self.assertRaisesRegex(ValueError, "missing required field: hl"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_i18n_languages_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_i18n_languages_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: pageToken"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "hl": "en_US", "pageToken": "cursor-1"}
            )

    def test_i18n_languages_list_wrapper_requires_api_key_mode(self):
        wrapper = build_i18n_languages_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "i18nLanguages.list requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "hl": "en_US"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_i18n_regions_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_i18n_regions_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "i18nRegions.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/i18nRegions")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "hl"))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("hl", wrapper.metadata.notes)
        self.assertIn("region", wrapper.metadata.notes)

    def test_i18n_regions_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_i18n_regions_list_wrapper))

    def test_i18n_regions_list_wrapper_requires_part_and_hl(self):
        wrapper = build_i18n_regions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"hl": "en_US"})

        with self.assertRaisesRegex(ValueError, "missing required field: hl"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_i18n_regions_list_wrapper_executes_successful_calls(self):
        wrapper = build_i18n_regions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "US", "hl": execution.arguments["hl"]}],
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

    def test_i18n_regions_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_i18n_regions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: pageToken"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "hl": "en_US", "pageToken": "cursor-1"}
            )

    def test_members_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_members_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "members.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/members")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "mode"))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ("pageToken", "maxResults"))
        self.assertIn("owner-only", wrapper.metadata.notes)
        self.assertIn("mode", wrapper.metadata.notes)

    def test_members_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_members_list_wrapper))

    def test_members_list_wrapper_requires_part_and_mode(self):
        wrapper = build_members_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"mode": "updates"})

        with self.assertRaisesRegex(ValueError, "missing required field: mode"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_members_list_wrapper_allows_optional_paging_fields(self):
        wrapper = build_members_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "mode": "updates",
                "pageToken": "cursor-123",
                "maxResults": 25,
            }
        )

    def test_members_list_wrapper_executes_successful_calls(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "member-123", "mode": execution.arguments["mode"]}],
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

    def test_members_list_wrapper_requires_oauth_mode(self):
        wrapper = build_members_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "members.list requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mode": "updates"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_members_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_members_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: onBehalfOfContentOwner"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "mode": "updates",
                    "onBehalfOfContentOwner": "owner-123",
                }
            )

    def test_memberships_levels_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_memberships_levels_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "membershipsLevels.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/membershipsLevels")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("owner-only", wrapper.metadata.notes)
        self.assertIn("part", wrapper.metadata.notes)

    def test_memberships_levels_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_memberships_levels_list_wrapper))

    def test_memberships_levels_list_wrapper_requires_part(self):
        wrapper = build_memberships_levels_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_memberships_levels_list_wrapper_executes_successful_calls(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "level-123", "part": execution.arguments["part"]}],
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

    def test_memberships_levels_list_wrapper_requires_oauth_mode(self):
        wrapper = build_memberships_levels_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError, "membershipsLevels.list requires oauth_required auth"
        ):
            wrapper.call(
                executor,
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_memberships_levels_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_memberships_levels_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: pageToken"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet", "pageToken": "cursor-1"})

    def test_playlist_images_list_wrapper_exposes_expected_metadata(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistImages.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistImages")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(
            wrapper.metadata.request_shape.optional_fields,
            ("playlistId", "id", "pageToken", "maxResults"),
        )
        self.assertEqual(wrapper.metadata.request_shape.exactly_one_of, ("playlistId", "id"))
        self.assertIn("OAuth-required", wrapper.metadata.notes)
        self.assertIn("pageToken", wrapper.metadata.notes)

    def test_playlist_images_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_images_list_wrapper))

    def test_playlist_images_list_wrapper_requires_part(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"playlistId": "PL123"})

    def test_playlist_images_list_wrapper_requires_exactly_one_selector(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: playlistId, id"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: playlistId, id"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "playlistId": "PL123", "id": "img-123"}
            )

    def test_playlist_images_list_wrapper_allows_playlist_paging_fields(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "playlistId": "PL123",
                "pageToken": "cursor-123",
                "maxResults": 10,
            }
        )

    def test_playlist_images_list_wrapper_rejects_paging_fields_for_id_selector(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        with self.assertRaisesRegex(ValueError, "paging fields are only supported for playlistId lookups"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "id": "img-123",
                    "pageToken": "cursor-123",
                }
            )

    def test_playlist_images_list_wrapper_executes_successful_calls(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "img-123", "selector": "playlistId"}],
                "selector": next(
                    selector for selector in ("playlistId", "id") if selector in execution.arguments
                ),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "playlistId": "PL123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "img-123")
        self.assertEqual(result["selector"], "playlistId")

    def test_playlist_images_list_wrapper_requires_oauth_mode(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistImages.list requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "playlistId": "PL123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_images_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = integrations_package.build_playlist_images_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: textFormat"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "playlistId": "PL123", "textFormat": "plainText"}
            )

    def test_playlist_items_list_wrapper_exposes_expected_metadata(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistItems.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistItems")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "api_key")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(
            wrapper.metadata.request_shape.optional_fields,
            ("playlistId", "id", "pageToken", "maxResults"),
        )
        self.assertEqual(wrapper.metadata.request_shape.exactly_one_of, ("playlistId", "id"))
        self.assertIn("API-key", wrapper.metadata.notes)
        self.assertIn("pageToken", wrapper.metadata.notes)

    def test_playlist_items_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_items_list_wrapper))

    def test_playlist_items_list_wrapper_requires_part(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"playlistId": "PL123"})

    def test_playlist_items_list_wrapper_requires_exactly_one_selector(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: playlistId, id"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: playlistId, id"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "playlistId": "PL123", "id": "item-123"}
            )

    def test_playlist_items_list_wrapper_allows_playlist_paging_fields(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "playlistId": "PL123",
                "pageToken": "cursor-123",
                "maxResults": 10,
            }
        )

    def test_playlist_items_list_wrapper_rejects_paging_fields_for_id_selector(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        with self.assertRaisesRegex(ValueError, "paging fields are only supported for playlistId lookups"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "id": "item-123",
                    "pageToken": "cursor-123",
                }
            )

    def test_playlist_items_list_wrapper_executes_successful_calls(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "item-123", "selector": "playlistId"}],
                "selector": next(
                    selector for selector in ("playlistId", "id") if selector in execution.arguments
                ),
            },
            retry_policy=RetryPolicy(max_attempts=1),
        )

        result = wrapper.call(
            executor,
            arguments={"part": "snippet", "playlistId": "PL123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        self.assertEqual(result["items"][0]["id"], "item-123")
        self.assertEqual(result["selector"], "playlistId")

    def test_playlist_items_list_wrapper_requires_api_key_mode(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistItems.list requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "playlistId": "PL123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlist_items_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = integrations_package.build_playlist_items_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: textFormat"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "playlistId": "PL123", "textFormat": "plainText"}
            )

    def test_playlists_list_wrapper_exposes_expected_metadata(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlists.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlists")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(
            wrapper.metadata.request_shape.optional_fields,
            ("channelId", "id", "mine", "pageToken", "maxResults"),
        )
        self.assertEqual(wrapper.metadata.request_shape.exactly_one_of, ("channelId", "id", "mine"))
        self.assertIn("owner-scoped", wrapper.metadata.auth_condition_note)
        self.assertIn("pageToken", wrapper.metadata.notes)

    def test_playlists_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlists_list_wrapper))

    def test_playlists_list_wrapper_requires_part(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"channelId": "UC123"})

    def test_playlists_list_wrapper_requires_exactly_one_selector(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: channelId, id, mine"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

        with self.assertRaisesRegex(ValueError, "exactly one selector is required from: channelId, id, mine"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "id": "PL123"}
            )

    def test_playlists_list_wrapper_allows_channel_paging_fields(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {"part": "snippet", "channelId": "UC123", "pageToken": "cursor-123", "maxResults": 10}
        )

    def test_playlists_list_wrapper_allows_mine_paging_fields(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {"part": "snippet", "mine": True, "pageToken": "cursor-123", "maxResults": 10}
        )

    def test_playlists_list_wrapper_rejects_paging_fields_for_id_selector(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        with self.assertRaisesRegex(ValueError, "paging fields are only supported for channelId or mine lookups"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": "PL123", "pageToken": "cursor-123"}
            )

    def test_playlists_list_wrapper_executes_successful_channel_calls(self):
        wrapper = integrations_package.build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "PL123", "selector": "channelId"}],
                "selector": next(
                    selector for selector in ("channelId", "id", "mine") if selector in execution.arguments
                ),
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

        self.assertEqual(result["items"][0]["id"], "PL123")
        self.assertEqual(result["selector"], "channelId")

    def test_playlists_list_wrapper_requires_oauth_for_mine_selector(self):
        wrapper = integrations_package.build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "mine requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlists_list_wrapper_requires_api_key_for_public_selectors(self):
        wrapper = integrations_package.build_playlists_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_playlists_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = integrations_package.build_playlists_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: textFormat"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "textFormat": "plainText"}
            )

    def test_search_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_search_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "search.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/search")
        self.assertEqual(wrapper.metadata.quota_cost, 100)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "q"))
        self.assertIn("type", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("publishedAfter", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("relevanceLanguage", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("quota guidance differs", wrapper.metadata.caveat_note)

    def test_search_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_search_list_wrapper))

    def test_search_list_wrapper_executes_public_queries_with_normalized_context(self):
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
            arguments={"part": "snippet", "q": "mcp server", "type": "video", "maxResults": 5},
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
                "maxResults": 5,
            },
        )
        self.assertEqual(result["authPath"], "public")
        self.assertEqual(result["nextPageToken"], "cursor-2")

    def test_search_list_wrapper_rejects_missing_required_query(self):
        wrapper = build_search_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: q"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_search_list_wrapper_rejects_video_refinements_without_video_type(self):
        wrapper = build_search_list_wrapper()

        with self.assertRaisesRegex(ValueError, "video-specific refinements require type=video"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "q": "mcp server",
                    "videoDuration": "long",
                }
            )

    def test_search_list_wrapper_requires_oauth_for_restricted_filters(self):
        wrapper = build_search_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "restricted search filters require oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "q": "mcp server", "forMine": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_subscriptions_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_subscriptions_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "subscriptions.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/subscriptions")
        self.assertEqual(wrapper.metadata.quota_cost, 1)
        self.assertEqual(wrapper.metadata.review_auth_mode, "mixed/conditional")
        self.assertEqual(wrapper.metadata.lifecycle_state, "active")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part",))
        self.assertEqual(
            wrapper.metadata.request_shape.optional_fields,
            (
                "channelId",
                "id",
                "mine",
                "myRecentSubscribers",
                "mySubscribers",
                "pageToken",
                "maxResults",
                "order",
            ),
        )
        self.assertEqual(
            wrapper.metadata.request_shape.exactly_one_of,
            ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers"),
        )
        self.assertIn("oauth_required", wrapper.metadata.auth_condition_note)
        self.assertIn("order", wrapper.metadata.notes)

    def test_subscriptions_list_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_subscriptions_list_wrapper))

    def test_subscriptions_list_wrapper_requires_part(self):
        wrapper = build_subscriptions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments({"channelId": "UC123"})

    def test_subscriptions_list_wrapper_requires_exactly_one_selector(self):
        wrapper = build_subscriptions_list_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "exactly one selector is required from: channelId, id, mine, myRecentSubscribers, mySubscribers",
        ):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

        with self.assertRaisesRegex(
            ValueError,
            "exactly one selector is required from: channelId, id, mine, myRecentSubscribers, mySubscribers",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "id": "sub-123"}
            )

    def test_subscriptions_list_wrapper_allows_collection_paging_and_order_fields(self):
        wrapper = build_subscriptions_list_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "channelId": "UC123",
                "pageToken": "cursor-123",
                "maxResults": 10,
                "order": "alphabetical",
            }
        )
        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "mySubscribers": True,
                "pageToken": "cursor-123",
                "maxResults": 10,
                "order": "relevance",
            }
        )

    def test_subscriptions_list_wrapper_rejects_paging_and_order_for_id_selector(self):
        wrapper = build_subscriptions_list_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "paging fields are only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": "sub-123", "pageToken": "cursor-123"}
            )

        with self.assertRaisesRegex(
            ValueError,
            "order is only supported for channelId, mine, myRecentSubscribers, or mySubscribers lookups",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "id": "sub-123", "order": "alphabetical"}
            )

    def test_subscriptions_list_wrapper_executes_successful_channel_calls(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "sub-123", "selector": "channelId"}],
                "selector": next(
                    selector
                    for selector in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
                    if selector in execution.arguments
                ),
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

        self.assertEqual(result["items"][0]["id"], "sub-123")
        self.assertEqual(result["selector"], "channelId")

    def test_subscriptions_list_wrapper_executes_successful_mine_calls(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda execution: {
                "items": [{"id": "sub-234", "selector": "mine"}],
                "selector": next(
                    selector
                    for selector in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
                    if selector in execution.arguments
                ),
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

        self.assertEqual(result["items"][0]["id"], "sub-234")
        self.assertEqual(result["selector"], "mine")

    def test_subscriptions_list_wrapper_requires_oauth_for_private_selectors(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "mySubscribers requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "mySubscribers": True},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_subscriptions_list_wrapper_requires_api_key_for_public_selectors(self):
        wrapper = build_subscriptions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelId requires api_key auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-123"),
                ),
            )

    def test_subscriptions_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_subscriptions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: textFormat"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "channelId": "UC123", "textFormat": "plainText"}
            )

    def test_comments_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_comments_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "comments.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/comments")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("textOriginal", wrapper.metadata.notes)

    def test_comments_insert_wrapper_requires_body_field(self):
        wrapper = build_comments_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_comments_insert_wrapper_rejects_incomplete_reply_payload(self):
        wrapper = build_comments_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.textOriginal is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"parentId": "comment-123"}},
                }
            )

    def test_comments_insert_wrapper_rejects_unsupported_reply_fields(self):
        wrapper = build_comments_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.videoId is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "parentId": "comment-123",
                            "textOriginal": "Reply text",
                            "videoId": "video-123",
                        }
                    },
                }
            )

    def test_comments_insert_wrapper_allows_optional_delegation_field(self):
        wrapper = build_comments_insert_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_comments_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_comments_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "comment-456", "kind": "youtube#comment"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "comments.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_comment_threads_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_comment_threads_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "commentThreads.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/commentThreads")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("videoId", wrapper.metadata.notes)
        self.assertIn("topLevelComment", wrapper.metadata.notes)

    def test_comment_threads_insert_wrapper_requires_body_field(self):
        wrapper = build_comment_threads_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_comment_threads_insert_wrapper_rejects_incomplete_top_level_payload(self):
        wrapper = build_comment_threads_insert_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "body.snippet.topLevelComment.snippet.textOriginal is required",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"videoId": "video-123", "topLevelComment": {"snippet": {}}}},
                }
            )

    def test_comment_threads_insert_wrapper_rejects_reply_style_shapes(self):
        wrapper = build_comment_threads_insert_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "body.snippet.parentId is read-only or unsupported",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "videoId": "video-123",
                            "parentId": "comment-123",
                            "topLevelComment": {"snippet": {"textOriginal": "Top-level text"}},
                        }
                    },
                }
            )

    def test_comment_threads_insert_wrapper_allows_optional_delegation_field(self):
        wrapper = build_comment_threads_insert_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "body": {
                    "snippet": {
                        "videoId": "video-123",
                        "topLevelComment": {"snippet": {"textOriginal": "Top-level text"}},
                    }
                },
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_comment_threads_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_comment_threads_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "thread-456", "kind": "youtube#commentThread"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "commentThreads.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "videoId": "video-123",
                            "topLevelComment": {"snippet": {"textOriginal": "Top-level text"}},
                        }
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_comments_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_comments_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "comments.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/comments")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("body.id", wrapper.metadata.notes)
        self.assertIn("textOriginal", wrapper.metadata.notes)

    def test_comments_update_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comments_update_wrapper))

    def test_comments_update_wrapper_requires_body_field(self):
        wrapper = build_comments_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_comments_update_wrapper_requires_existing_comment_identity(self):
        wrapper = build_comments_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"textOriginal": "Updated comment"}},
                }
            )

    def test_comments_update_wrapper_rejects_missing_updated_text(self):
        wrapper = build_comments_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.textOriginal is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"id": "comment-123", "snippet": {}},
                }
            )

    def test_comments_update_wrapper_rejects_unsupported_read_only_fields(self):
        wrapper = build_comments_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.authorChannelId is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "id": "comment-123",
                        "snippet": {
                            "textOriginal": "Updated comment",
                            "authorChannelId": {"value": "UC123"},
                        },
                    },
                }
            )

    def test_comments_update_wrapper_allows_optional_delegation_field(self):
        wrapper = build_comments_update_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_comments_update_wrapper_requires_oauth_mode(self):
        wrapper = build_comments_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "comment-456", "kind": "youtube#comment"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "comments.update requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_comments_set_moderation_status_wrapper_exposes_expected_metadata(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "comments.setModerationStatus")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/comments/setModerationStatus")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id", "moderationStatus"))
        self.assertIn("banAuthor", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("published", wrapper.metadata.notes)
        self.assertIn("heldForReview", wrapper.metadata.notes)
        self.assertIn("rejected", wrapper.metadata.notes)

    def test_comments_set_moderation_status_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comments_set_moderation_status_wrapper))

    def test_comments_set_moderation_status_wrapper_requires_id_field(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({"moderationStatus": "rejected"})

    def test_comments_set_moderation_status_wrapper_requires_moderation_status_field(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: moderationStatus"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["comment-123"]})

    def test_comments_set_moderation_status_wrapper_rejects_unsupported_status(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported moderationStatus: spam"):
            wrapper.metadata.request_shape.validate_arguments(
                {"id": ["comment-123"], "moderationStatus": "spam"}
            )

    def test_comments_set_moderation_status_wrapper_rejects_duplicate_comment_ids(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        with self.assertRaisesRegex(ValueError, "duplicate comment identifiers are unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {"id": ["comment-123", "comment-123"], "moderationStatus": "rejected"}
            )

    def test_comments_set_moderation_status_wrapper_rejects_ban_author_for_non_rejected_status(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "banAuthor is only supported when moderationStatus is rejected",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "id": ["comment-123"],
                    "moderationStatus": "published",
                    "banAuthor": True,
                }
            )

    def test_comments_set_moderation_status_wrapper_allows_supported_arguments(self):
        wrapper = build_comments_set_moderation_status_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "id": ["comment-123", "comment-456"],
                "moderationStatus": "rejected",
                "banAuthor": True,
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_comments_set_moderation_status_wrapper_requires_oauth_mode(self):
        wrapper = build_comments_set_moderation_status_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"isModerated": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(
            ValueError,
            "comments.setModerationStatus requires oauth_required auth",
        ):
            wrapper.call(
                executor,
                arguments={
                    "id": ["comment-123"],
                    "moderationStatus": "rejected",
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_comments_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_comments_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "comments.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/comments")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("target comment", wrapper.metadata.notes)
        self.assertIn("target-state", wrapper.metadata.notes)

    def test_comments_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_comments_delete_wrapper))

    def test_comments_delete_wrapper_requires_id_field(self):
        wrapper = build_comments_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_comments_delete_wrapper_rejects_invalid_id_shape(self):
        wrapper = build_comments_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "id must identify one comment"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["comment-123"]})

    def test_comments_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_comments_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: commentId"):
            wrapper.metadata.request_shape.validate_arguments({"id": "comment-123", "commentId": "comment-456"})

    def test_comments_delete_wrapper_allows_optional_delegation_field(self):
        wrapper = build_comments_delete_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "id": "comment-123",
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_comments_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_comments_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"commentId": "comment-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "comments.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "comment-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_channel_sections_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channelSections.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channelSections")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("snippet.type", wrapper.metadata.notes)
        self.assertIn("title", wrapper.metadata.notes)

    def test_channel_sections_insert_wrapper_requires_body_field(self):
        wrapper = build_channel_sections_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_channel_sections_insert_wrapper_rejects_incomplete_body_payload(self):
        wrapper = build_channel_sections_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet", "body": {"contentDetails": {}}})

    def test_channel_sections_insert_wrapper_rejects_single_playlist_with_multiple_playlists(self):
        wrapper = build_channel_sections_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "singlePlaylist requires exactly one playlist id"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                        "contentDetails": {"playlists": ["PL123", "PL456"]},
                    },
                }
            )

    def test_channel_sections_insert_wrapper_rejects_multiple_playlists_without_title(self):
        wrapper = build_channel_sections_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "multiplePlaylists requires body.snippet.title"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {"type": "multiplePlaylists", "channelId": "UC123"},
                        "contentDetails": {"playlists": ["PL123", "PL456"]},
                    },
                }
            )

    def test_channel_sections_insert_wrapper_rejects_duplicate_channel_references(self):
        wrapper = build_channel_sections_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "duplicate channel references are unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {
                            "type": "multipleChannels",
                            "channelId": "UC123",
                            "title": "Featured channels",
                        },
                        "contentDetails": {"channels": ["UC777", "UC777"]},
                    },
                }
            )

    def test_channel_sections_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_channel_sections_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "section-123", "kind": "youtube#channelSection"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelSections.insert requires oauth_required auth"):
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
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_channel_sections_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channelSections.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channelSections")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("body.id", wrapper.metadata.notes)
        self.assertIn("snippet.type", wrapper.metadata.notes)

    def test_channel_sections_update_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_channel_sections_update_wrapper))

    def test_channel_sections_update_wrapper_requires_body_field(self):
        wrapper = build_channel_sections_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_channel_sections_update_wrapper_requires_existing_section_identity(self):
        wrapper = build_channel_sections_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet,contentDetails",
                    "body": {
                        "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                        "contentDetails": {"playlists": ["PL123"]},
                    },
                }
            )

    def test_channel_sections_update_wrapper_rejects_read_only_fields(self):
        wrapper = build_channel_sections_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.kind is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "id": "section-123",
                        "kind": "youtube#channelSection",
                        "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                    },
                }
            )

    def test_channel_sections_update_wrapper_rejects_duplicate_playlist_references(self):
        wrapper = build_channel_sections_update_wrapper()

        with self.assertRaisesRegex(ValueError, "duplicate playlist references are unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet,contentDetails",
                    "body": {
                        "id": "section-123",
                        "snippet": {
                            "type": "multiplePlaylists",
                            "channelId": "UC123",
                            "title": "Featured playlists",
                        },
                        "contentDetails": {"playlists": ["PL123", "PL123"]},
                    },
                }
            )

    def test_channel_sections_update_wrapper_requires_oauth_mode(self):
        wrapper = build_channel_sections_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "section-123", "kind": "youtube#channelSection"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelSections.update requires oauth_required auth"):
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
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_sections_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_channel_sections_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channelSections.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channelSections")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("onBehalfOfContentOwnerChannel", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("owner-scoped", wrapper.metadata.notes)
        self.assertIn("one target", wrapper.metadata.notes)

    def test_channel_sections_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_channel_sections_delete_wrapper))

    def test_channel_sections_delete_wrapper_requires_id_field(self):
        wrapper = build_channel_sections_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_channel_sections_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_channel_sections_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: part"):
            wrapper.metadata.request_shape.validate_arguments({"id": "section-123", "part": "snippet"})

    def test_channel_sections_delete_wrapper_allows_delegation_fields(self):
        wrapper = build_channel_sections_delete_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "id": "section-123",
                "onBehalfOfContentOwner": "owner-123",
                "onBehalfOfContentOwnerChannel": "UC123",
            }
        )

    def test_channel_sections_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_channel_sections_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"channelSectionId": "section-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelSections.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "section-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_captions_list_wrapper_exposes_expected_metadata(self):
        wrapper = build_captions_list_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "captions.list")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/captions")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.notes)

    def test_captions_list_wrapper_requires_one_selector_field(self):
        wrapper = build_captions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_captions_list_wrapper_rejects_multiple_selector_fields(self):
        wrapper = build_captions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "exactly one selector is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "videoId": "video-123", "id": "caption-123"}
            )

    def test_captions_list_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_captions_list_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: tlang"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "videoId": "video-123", "tlang": "en"}
            )

    def test_captions_list_wrapper_requires_oauth_mode(self):
        wrapper = build_captions_list_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"items": []},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "captions.list requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"part": "snippet", "videoId": "video-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_captions_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_captions_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "captions.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/captions")
        self.assertEqual(wrapper.metadata.quota_cost, 400)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertIn("body", wrapper.metadata.request_shape.required_fields)
        self.assertIn("media", wrapper.metadata.request_shape.required_fields)
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.notes)

    def test_captions_insert_wrapper_requires_metadata_and_media_fields(self):
        wrapper = build_captions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: media"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"videoId": "video-123"}}}
            )

    def test_captions_insert_wrapper_rejects_incomplete_body_payload(self):
        wrapper = build_captions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"kind": "youtube#caption"},
                    "media": {"mimeType": "text/plain", "content": "caption"},
                }
            )

    def test_captions_insert_wrapper_rejects_incomplete_media_payload(self):
        wrapper = build_captions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"videoId": "video-123"}},
                    "media": {"mimeType": "text/plain"},
                }
            )

    def test_captions_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_captions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "caption-123", "kind": "youtube#caption"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "captions.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"videoId": "video-123", "language": "en"}},
                    "media": {"mimeType": "text/plain", "content": "caption body"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_captions_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_captions_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "captions.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/captions")
        self.assertEqual(wrapper.metadata.quota_cost, 450)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("media", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.notes)

    def test_captions_update_wrapper_requires_body_field(self):
        wrapper = build_captions_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_captions_update_wrapper_rejects_incomplete_body_payload(self):
        wrapper = build_captions_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"language": "en"}}}
            )

    def test_captions_update_wrapper_rejects_incomplete_optional_media_payload(self):
        wrapper = build_captions_update_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"id": "caption-123", "snippet": {"language": "en"}},
                    "media": {"mimeType": "text/plain"},
                }
            )

    def test_captions_update_wrapper_requires_oauth_mode(self):
        wrapper = build_captions_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "caption-123", "kind": "youtube#caption"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "captions.update requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "caption-123", "snippet": {"language": "en"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_captions_download_wrapper_exposes_expected_metadata(self):
        wrapper = build_captions_download_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "captions.download")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/captions/{id}")
        self.assertEqual(wrapper.metadata.quota_cost, 200)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertIn("tfmt", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("tlang", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.notes)

    def test_captions_download_wrapper_requires_id_field(self):
        wrapper = build_captions_download_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_captions_download_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_captions_download_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: videoId"):
            wrapper.metadata.request_shape.validate_arguments({"id": "caption-123", "videoId": "video-123"})

    def test_captions_download_wrapper_allows_output_variant_fields(self):
        wrapper = build_captions_download_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "id": "caption-123",
                "tfmt": "srt",
                "tlang": "es",
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_captions_download_wrapper_requires_oauth_mode(self):
        wrapper = build_captions_download_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"captionId": "caption-123", "content": "caption body"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "captions.download requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "caption-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_captions_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_captions_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "captions.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/captions/{id}")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertIn("onBehalfOfContentOwner", wrapper.metadata.request_shape.optional_fields)
        self.assertIn("ownership", wrapper.metadata.notes)

    def test_captions_delete_wrapper_requires_id_field(self):
        wrapper = build_captions_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_captions_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_captions_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: videoId"):
            wrapper.metadata.request_shape.validate_arguments({"id": "caption-123", "videoId": "video-123"})

    def test_captions_delete_wrapper_allows_delegation_field(self):
        wrapper = build_captions_delete_wrapper()

        wrapper.metadata.request_shape.validate_arguments(
            {
                "id": "caption-123",
                "onBehalfOfContentOwner": "owner-123",
            }
        )

    def test_captions_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_captions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"captionId": "caption-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "captions.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "caption-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_channel_banners_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_channel_banners_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "channelBanners.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/channelBanners/insert")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("media",))
        self.assertIn("response URL", wrapper.metadata.notes)

    def test_channel_banners_insert_wrapper_requires_media_field(self):
        wrapper = build_channel_banners_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: media"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_channel_banners_insert_wrapper_rejects_incomplete_media_payload(self):
        wrapper = build_channel_banners_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"media": {"mimeType": "image/png"}}
            )

    def test_channel_banners_insert_wrapper_rejects_unsupported_mime_type(self):
        wrapper = build_channel_banners_insert_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "media.mimeType must be image/jpeg, image/png, or application/octet-stream",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {"media": {"mimeType": "image/gif", "content": b"banner-bytes"}}
            )

    def test_channel_banners_insert_wrapper_rejects_oversized_uploads(self):
        wrapper = build_channel_banners_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content exceeds the 6 MB channel banner limit"):
            wrapper.metadata.request_shape.validate_arguments(
                {"media": {"mimeType": "image/png", "content": b"x" * (6 * 1024 * 1024 + 1)}}
            )

    def test_channel_banners_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_channel_banners_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"bannerUrl": "https://yt.example/banner"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "channelBanners.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_images_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlist_images_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistImages.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistImages")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body", "media"))
        self.assertIn("body", wrapper.metadata.notes)
        self.assertIn("media", wrapper.metadata.notes)

    def test_playlist_images_insert_wrapper_requires_media_field(self):
        wrapper = build_playlist_images_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: media"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"playlistId": "PL123"}}}
            )

    def test_playlist_images_insert_wrapper_executes_authorized_create_requests(self):
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

    def test_playlist_images_insert_wrapper_requires_body_field(self):
        wrapper = build_playlist_images_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"}}
            )

    def test_playlist_images_insert_wrapper_rejects_incomplete_media_payload(self):
        wrapper = build_playlist_images_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123"}},
                    "media": {"mimeType": "image/png"},
                }
            )

    def test_playlist_images_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_images_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-image-123", "kind": "youtube#playlistImage"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistImages.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "type": "featured"}},
                    "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_items_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlist_items_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistItems.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistItems")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("playlistId", wrapper.metadata.notes)
        self.assertIn("videoId", wrapper.metadata.notes)

    def test_playlist_items_insert_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_items_insert_wrapper))

    def test_playlist_items_insert_wrapper_requires_body_field(self):
        wrapper = build_playlist_items_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_playlist_items_insert_wrapper_rejects_unsupported_part(self):
        wrapper = build_playlist_items_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: only snippet is supported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "contentDetails",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                }
            )

    def test_playlist_items_insert_wrapper_requires_playlist_and_video_fields(self):
        wrapper = build_playlist_items_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.playlistId is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"resourceId": {"videoId": "video-123"}}}}
            )
        with self.assertRaisesRegex(ValueError, "body.snippet.resourceId.videoId is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"playlistId": "PL123", "resourceId": {}}}}
            )

    def test_playlist_items_insert_wrapper_rejects_unsupported_optional_fields(self):
        wrapper = build_playlist_items_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.position is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "playlistId": "PL123",
                            "resourceId": {"videoId": "video-123"},
                            "position": 0,
                        }
                    },
                }
            )

    def test_playlist_items_insert_wrapper_executes_authorized_create_requests(self):
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

    def test_playlist_items_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_items_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-item-123", "kind": "youtube#playlistItem"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistItems.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_items_update_wrapper_exposes_expected_metadata(self):
        wrapper = integrations_package.build_playlist_items_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistItems.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistItems")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("body.id", wrapper.metadata.notes)
        self.assertIn("playlistId", wrapper.metadata.notes)
        self.assertIn("videoId", wrapper.metadata.notes)

    def test_playlist_items_update_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_items_update_wrapper))

    def test_playlist_items_update_wrapper_requires_body_field(self):
        wrapper = build_playlist_items_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_playlist_items_update_wrapper_rejects_unsupported_part(self):
        wrapper = build_playlist_items_update_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: only snippet is supported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "contentDetails",
                    "body": {
                        "id": "playlist-item-123",
                        "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                    },
                }
            )

    def test_playlist_items_update_wrapper_requires_identifier_playlist_and_video_fields(self):
        wrapper = build_playlist_items_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                }
            )
        with self.assertRaisesRegex(ValueError, "body.snippet.playlistId is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"id": "playlist-item-123", "snippet": {"resourceId": {"videoId": "video-123"}}},
                }
            )
        with self.assertRaisesRegex(ValueError, "body.snippet.resourceId.videoId is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"id": "playlist-item-123", "snippet": {"playlistId": "PL123", "resourceId": {}}},
                }
            )

    def test_playlist_items_update_wrapper_rejects_unsupported_optional_fields(self):
        wrapper = build_playlist_items_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.position is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "id": "playlist-item-123",
                        "snippet": {
                            "playlistId": "PL123",
                            "resourceId": {"videoId": "video-123"},
                            "position": 0,
                        },
                    },
                }
            )

    def test_playlist_items_update_wrapper_executes_authorized_update_requests(self):
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
                    "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
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

    def test_playlist_items_update_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_items_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-item-123", "kind": "youtube#playlistItem"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistItems.update requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {
                        "id": "playlist-item-123",
                        "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                    },
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlists_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlists_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlists.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlists")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("title", wrapper.metadata.notes)
        self.assertIn("snippet", wrapper.metadata.notes)

    def test_playlists_insert_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlists_insert_wrapper))

    def test_playlists_insert_wrapper_requires_body_field(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_playlists_insert_wrapper_requires_part_field(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments(
                {"body": {"snippet": {"title": "Layer 1 Playlist"}}}
            )

    def test_playlists_insert_wrapper_rejects_unsupported_writable_part(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: only snippet is supported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "status",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                }
            )

    def test_playlists_insert_wrapper_requires_playlist_title(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.title is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {}}}
            )

    def test_playlists_insert_wrapper_rejects_unsupported_top_level_body_fields(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.status is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {"title": "Layer 1 Playlist"},
                        "status": {"privacyStatus": "private"},
                    },
                }
            )

    def test_playlists_insert_wrapper_rejects_unsupported_snippet_fields(self):
        wrapper = build_playlists_insert_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "body.snippet.description is read-only or unsupported",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "title": "Layer 1 Playlist",
                            "description": "Not supported in this slice",
                        }
                    },
                }
            )

    def test_playlists_insert_wrapper_executes_authorized_create_requests(self):
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

    def test_playlists_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_playlists_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-123", "kind": "youtube#playlist"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlists.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_subscriptions_insert_wrapper_exposes_expected_metadata(self):
        wrapper = build_subscriptions_insert_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "subscriptions.insert")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/subscriptions")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("resourceId.channelId", wrapper.metadata.notes)
        self.assertIn("part=snippet", wrapper.metadata.notes)

    def test_subscriptions_insert_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_subscriptions_insert_wrapper))

    def test_subscriptions_insert_wrapper_requires_body_field(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_subscriptions_insert_wrapper_requires_part_field(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments(
                {"body": {"snippet": {"resourceId": {"channelId": "UC123"}}}}
            )

    def test_subscriptions_insert_wrapper_rejects_unsupported_writable_part(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: only snippet is supported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "status",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                }
            )

    def test_subscriptions_insert_wrapper_requires_target_channel_id(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.resourceId.channelId is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"resourceId": {}}}}
            )

    def test_subscriptions_insert_wrapper_rejects_invalid_resource_kind(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "body.snippet.resourceId.kind must be youtube#channel when provided",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "resourceId": {"channelId": "UC123", "kind": "youtube#video"}
                        }
                    },
                }
            )

    def test_subscriptions_insert_wrapper_rejects_unsupported_top_level_body_fields(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.status is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {"resourceId": {"channelId": "UC123"}},
                        "status": {"privacyStatus": "private"},
                    },
                }
            )

    def test_subscriptions_insert_wrapper_rejects_unsupported_snippet_fields(self):
        wrapper = build_subscriptions_insert_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.title is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "snippet": {
                            "resourceId": {"channelId": "UC123"},
                            "title": "Not supported",
                        }
                    },
                }
            )

    def test_subscriptions_insert_wrapper_executes_authorized_create_requests(self):
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

    def test_subscriptions_insert_wrapper_requires_oauth_mode(self):
        wrapper = build_subscriptions_insert_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "subscription-123", "kind": "youtube#subscription"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "subscriptions.insert requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"resourceId": {"channelId": "UC123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_subscriptions_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_subscriptions_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "subscriptions.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/subscriptions")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("id", wrapper.metadata.notes)
        self.assertIn("target-state", wrapper.metadata.notes)

    def test_subscriptions_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_subscriptions_delete_wrapper))

    def test_subscriptions_delete_wrapper_requires_id_field(self):
        wrapper = build_subscriptions_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_subscriptions_delete_wrapper_rejects_invalid_id_shape(self):
        wrapper = build_subscriptions_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "id must identify one subscription"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["subscription-123"]})

    def test_subscriptions_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_subscriptions_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: part"):
            wrapper.metadata.request_shape.validate_arguments({"id": "subscription-123", "part": "snippet"})

    def test_subscriptions_delete_wrapper_executes_authorized_delete_requests(self):
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
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_subscriptions_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_subscriptions_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"subscriptionId": "subscription-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "subscriptions.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "subscription-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlists_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlists_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlists.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlists")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body"))
        self.assertIn("body.id", wrapper.metadata.notes)
        self.assertIn("body.snippet.title", wrapper.metadata.notes)

    def test_playlists_update_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlists_update_wrapper))

    def test_playlists_update_wrapper_requires_body_field(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments({"part": "snippet"})

    def test_playlists_update_wrapper_requires_part_field(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: part"):
            wrapper.metadata.request_shape.validate_arguments(
                {"body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}}}
            )

    def test_playlists_update_wrapper_rejects_unsupported_writable_part(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "unsupported writable part: only snippet is supported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "status",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                }
            )

    def test_playlists_update_wrapper_requires_playlist_identifier(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"snippet": {"title": "Layer 1 Playlist"}}}
            )

    def test_playlists_update_wrapper_requires_playlist_title(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.snippet.title is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"id": "playlist-123", "snippet": {}}}
            )

    def test_playlists_update_wrapper_rejects_unsupported_top_level_body_fields(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.status is read-only or unsupported"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "id": "playlist-123",
                        "snippet": {"title": "Layer 1 Playlist"},
                        "status": {"privacyStatus": "private"},
                    },
                }
            )

    def test_playlists_update_wrapper_rejects_unsupported_snippet_fields(self):
        wrapper = build_playlists_update_wrapper()

        with self.assertRaisesRegex(
            ValueError,
            "body.snippet.description is read-only or unsupported",
        ):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {
                        "id": "playlist-123",
                        "snippet": {
                            "title": "Layer 1 Playlist",
                            "description": "Not supported in this slice",
                        },
                    },
                }
            )

    def test_playlists_update_wrapper_executes_authorized_update_requests(self):
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

    def test_playlists_update_wrapper_requires_oauth_mode(self):
        wrapper = build_playlists_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-123", "kind": "youtube#playlist"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlists.update requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlists_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlists_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlists.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlists")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("id", wrapper.metadata.notes)
        self.assertIn("target-state", wrapper.metadata.notes)

    def test_playlists_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlists_delete_wrapper))

    def test_playlists_delete_wrapper_requires_id_field(self):
        wrapper = build_playlists_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_playlists_delete_wrapper_rejects_invalid_id_shape(self):
        wrapper = build_playlists_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "id must identify one playlist"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["playlist-123"]})

    def test_playlists_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_playlists_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: part"):
            wrapper.metadata.request_shape.validate_arguments({"id": "playlist-123", "part": "snippet"})

    def test_playlists_delete_wrapper_executes_authorized_delete_requests(self):
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

    def test_playlists_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_playlists_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistId": "playlist-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlists.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "playlist-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_images_update_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlist_images_update_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistImages.update")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistImages")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("part", "body", "media"))
        self.assertIn("body", wrapper.metadata.notes)
        self.assertIn("media", wrapper.metadata.notes)

    def test_playlist_images_update_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_images_update_wrapper))

    def test_playlist_images_update_wrapper_requires_body_field(self):
        wrapper = build_playlist_images_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: body"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"}}
            )

    def test_playlist_images_update_wrapper_requires_media_field(self):
        wrapper = build_playlist_images_update_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: media"):
            wrapper.metadata.request_shape.validate_arguments(
                {"part": "snippet", "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}}}
            )

    def test_playlist_images_update_wrapper_requires_existing_playlist_image_identity(self):
        wrapper = build_playlist_images_update_wrapper()

        with self.assertRaisesRegex(ValueError, "body.id is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "type": "featured"}},
                    "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                }
            )

    def test_playlist_images_update_wrapper_rejects_incomplete_media_payload(self):
        wrapper = build_playlist_images_update_wrapper()

        with self.assertRaisesRegex(ValueError, "media.content is required"):
            wrapper.metadata.request_shape.validate_arguments(
                {
                    "part": "snippet",
                    "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                    "media": {"mimeType": "image/png"},
                }
            )

    def test_playlist_images_update_wrapper_executes_authorized_update_requests(self):
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

    def test_playlist_images_update_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_images_update_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"id": "playlist-image-123", "kind": "youtube#playlistImage"},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistImages.update requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "featured"}},
                    "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_images_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlist_images_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistImages.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistImages")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("id", wrapper.metadata.notes)
        self.assertIn("target-state", wrapper.metadata.notes)

    def test_playlist_images_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_images_delete_wrapper))

    def test_playlist_images_delete_wrapper_requires_id_field(self):
        wrapper = build_playlist_images_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_playlist_images_delete_wrapper_rejects_invalid_id_shape(self):
        wrapper = build_playlist_images_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "id must identify one playlist image"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["playlist-image-123"]})

    def test_playlist_images_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_playlist_images_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: playlistId"):
            wrapper.metadata.request_shape.validate_arguments({"id": "playlist-image-123", "playlistId": "PL123"})

    def test_playlist_images_delete_wrapper_executes_authorized_delete_requests(self):
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

    def test_playlist_images_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_images_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistImageId": "playlist-image-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistImages.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "playlist-image-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

    def test_playlist_items_delete_wrapper_exposes_expected_metadata(self):
        wrapper = build_playlist_items_delete_wrapper()

        self.assertEqual(wrapper.metadata.operation_key, "playlistItems.delete")
        self.assertEqual(wrapper.metadata.path_shape, "/youtube/v3/playlistItems")
        self.assertEqual(wrapper.metadata.quota_cost, 50)
        self.assertEqual(wrapper.metadata.review_auth_mode, "oauth_required")
        self.assertEqual(wrapper.metadata.request_shape.required_fields, ("id",))
        self.assertEqual(wrapper.metadata.request_shape.optional_fields, ())
        self.assertIn("id", wrapper.metadata.notes)
        self.assertIn("target-state", wrapper.metadata.notes)

    def test_playlist_items_delete_wrapper_is_exported_from_integrations_package(self):
        self.assertTrue(callable(integrations_package.build_playlist_items_delete_wrapper))

    def test_playlist_items_delete_wrapper_requires_id_field(self):
        wrapper = build_playlist_items_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "missing required field: id"):
            wrapper.metadata.request_shape.validate_arguments({})

    def test_playlist_items_delete_wrapper_rejects_invalid_id_shape(self):
        wrapper = build_playlist_items_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "id must identify one playlist item"):
            wrapper.metadata.request_shape.validate_arguments({"id": ["playlist-item-123"]})

    def test_playlist_items_delete_wrapper_rejects_unexpected_request_fields(self):
        wrapper = build_playlist_items_delete_wrapper()

        with self.assertRaisesRegex(ValueError, "unexpected field: playlistId"):
            wrapper.metadata.request_shape.validate_arguments({"id": "playlist-item-123", "playlistId": "PL123"})

    def test_playlist_items_delete_wrapper_executes_authorized_delete_requests(self):
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

    def test_playlist_items_delete_wrapper_requires_oauth_mode(self):
        wrapper = build_playlist_items_delete_wrapper()
        executor = IntegrationExecutor(
            transport=lambda _execution: {"playlistItemId": "playlist-item-123", "isDeleted": True},
            retry_policy=RetryPolicy(max_attempts=1),
        )

        with self.assertRaisesRegex(ValueError, "playlistItems.delete requires oauth_required auth"):
            wrapper.call(
                executor,
                arguments={"id": "playlist-item-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )

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

    def test_requires_auth_condition_note_for_conditional_metadata(self):
        with self.assertRaises(ValueError):
            EndpointMetadata(
                resource_name="activities",
                operation_name="list",
                http_method="GET",
                path_shape="/youtube/v3/activities",
                request_shape=EndpointRequestShape(required_fields=("part",)),
                auth_mode=AuthMode.CONDITIONAL,
                quota_cost=1,
            )

    def test_requires_caveat_note_for_lifecycle_states_that_need_review_context(self):
        with self.assertRaises(ValueError):
            EndpointMetadata(
                resource_name="captions",
                operation_name="insert",
                http_method="POST",
                path_shape="/youtube/v3/captions",
                request_shape=EndpointRequestShape(required_fields=("part", "videoId")),
                auth_mode=AuthMode.OAUTH_REQUIRED,
                quota_cost=400,
                lifecycle_state="limited",
            )

    def test_exposes_review_surface_for_metadata_visibility(self):
        metadata = EndpointMetadata(
            resource_name="search",
            operation_name="list",
            http_method="GET",
            path_shape="/youtube/v3/search",
            request_shape=EndpointRequestShape(required_fields=("part", "q")),
            auth_mode=AuthMode.CONDITIONAL,
            quota_cost=100,
            auth_condition_note="Requires OAuth when private or partner-only filters are used.",
            lifecycle_state="inconsistent-docs",
            caveat_note="Official quota guidance differs between the public overview and endpoint reference.",
        )

        self.assertEqual(metadata.review_auth_mode, "mixed/conditional")
        self.assertTrue(metadata.requires_caveat_note)
        review_surface = metadata.review_surface()
        self.assertEqual(review_surface["operationKey"], "search.list")
        self.assertEqual(review_surface["quotaCost"], 100)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertIn("Official quota guidance differs", review_surface["caveatNote"])

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
