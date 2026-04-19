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
from mcp_server.integrations.wrappers import (
    RepresentativeEndpointWrapper,
    build_activities_list_wrapper,
    build_channel_banners_insert_wrapper,
    build_channel_sections_delete_wrapper,
    build_channel_sections_insert_wrapper,
    build_channel_sections_list_wrapper,
    build_channel_sections_update_wrapper,
    build_comment_threads_list_wrapper,
    build_channels_list_wrapper,
    build_channels_update_wrapper,
    build_comments_insert_wrapper,
    build_comments_delete_wrapper,
    build_comments_list_wrapper,
    build_comments_set_moderation_status_wrapper,
    build_comments_update_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)


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
