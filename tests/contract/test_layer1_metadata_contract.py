import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

import mcp_server.integrations as integrations_package
from mcp_server.integrations.auth import AuthMode
from mcp_server.integrations.contracts import EndpointMetadata, EndpointRequestShape
from mcp_server.integrations.wrappers import (
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
    build_playlists_delete_wrapper,
    build_playlists_insert_wrapper,
    build_search_list_wrapper,
    build_subscriptions_delete_wrapper,
    build_subscriptions_insert_wrapper,
    build_subscriptions_list_wrapper,
    build_videos_list_wrapper,
    build_playlists_update_wrapper,
    build_playlist_images_update_wrapper,
    build_video_categories_list_wrapper,
    build_video_abuse_report_reasons_list_wrapper,
)


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

    def test_channel_banners_insert_review_surface_exposes_quota_auth_and_upload_notes(self):
        review_surface = build_channel_banners_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelBanners")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelBanners.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("media",))
        self.assertIn("response URL", review_surface["notes"])

    def test_playlist_images_insert_review_surface_exposes_quota_auth_and_upload_notes(self):
        review_surface = build_playlist_images_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistImages")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "playlistImages.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body", "media"))
        self.assertIn("body", review_surface["notes"])
        self.assertIn("media", review_surface["notes"])

    def test_playlist_items_insert_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_playlist_items_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "playlistItems.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("playlistId", review_surface["notes"])
        self.assertIn("videoId", review_surface["notes"])

    def test_playlists_insert_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_playlists_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlists")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "playlists.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["httpMethod"], "POST")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/playlists")
        self.assertIn("title", review_surface["notes"])
        self.assertIn("snippet", review_surface["notes"])
        self.assertIn("part=snippet", review_surface["notes"])
        self.assertIn("body.status", review_surface["notes"])

    def test_subscriptions_insert_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_subscriptions_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "subscriptions.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["httpMethod"], "POST")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/subscriptions")
        self.assertIn("resourceId.channelId", review_surface["notes"])
        self.assertIn("part=snippet", review_surface["notes"])
        self.assertIn("youtube#channel", review_surface["notes"])
        self.assertIn("body.status", review_surface["notes"])

    def test_subscriptions_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_subscriptions_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "subscriptions.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertEqual(review_surface["httpMethod"], "DELETE")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/subscriptions")
        self.assertIn("id", review_surface["notes"])
        self.assertIn("target-state", review_surface["notes"])

    def test_thumbnails_set_review_surface_exposes_quota_auth_and_upload_notes(self):
        review_surface = integrations_package.build_thumbnails_set_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "thumbnails")
        self.assertEqual(review_surface["operationName"], "set")
        self.assertEqual(review_surface["operationKey"], "thumbnails.set")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("videoId", "media"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["httpMethod"], "POST")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/thumbnails/set")
        self.assertIn("videoId", review_surface["notes"])
        self.assertIn("media", review_surface["notes"])
        self.assertIn("upload-only", review_surface["notes"])
        self.assertIn("target-only", review_surface["notes"])

    def test_playlist_images_update_review_surface_exposes_quota_auth_and_update_notes(self):
        review_surface = build_playlist_images_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistImages")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "playlistImages.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body", "media"))
        self.assertIn("body", review_surface["notes"])
        self.assertIn("media", review_surface["notes"])

    def test_playlist_items_update_review_surface_exposes_quota_auth_and_update_notes(self):
        review_surface = build_playlist_items_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "playlistItems.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("playlistId", review_surface["notes"])
        self.assertIn("videoId", review_surface["notes"])

    def test_playlists_update_review_surface_exposes_quota_auth_and_update_notes(self):
        review_surface = build_playlists_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlists")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "playlists.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["httpMethod"], "PUT")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/playlists")
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("body.snippet.title", review_surface["notes"])
        self.assertIn("body.snippet.description", review_surface["notes"])

    def test_playlist_images_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_playlist_images_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistImages")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "playlistImages.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("id", review_surface["notes"])
        self.assertIn("target-state", review_surface["notes"])

    def test_playlist_items_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_playlist_items_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "playlistItems.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("id", review_surface["notes"])
        self.assertIn("target-state", review_surface["notes"])

    def test_playlists_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_playlists_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlists")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "playlists.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertEqual(review_surface["httpMethod"], "DELETE")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/playlists")
        self.assertIn("id", review_surface["notes"])
        self.assertIn("target-state", review_surface["notes"])

    def test_channels_list_review_surface_exposes_quota_auth_and_selector_notes(self):
        review_surface = build_channels_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channels")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channels.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertIn("forHandle", review_surface["optionalFields"])
        self.assertIn("forUsername", review_surface["optionalFields"])
        self.assertIn("mine", review_surface["exclusiveSelectors"])
        self.assertIn("owner-scoped", review_surface["authConditionNote"])

    def test_channels_update_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channels_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channels")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "channels.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))

    def test_search_list_review_surface_exposes_quota_caveat_auth_and_refinements(self):
        review_surface = build_search_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "search")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "search.list")
        self.assertEqual(review_surface["httpMethod"], "GET")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/search")
        self.assertEqual(review_surface["requiredFields"], ("part", "q"))
        self.assertEqual(review_surface["quotaCost"], 100)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["lifecycleState"], "inconsistent-docs")
        self.assertIn("forMine", review_surface["optionalFields"])
        self.assertIn("videoDuration", review_surface["optionalFields"])
        self.assertIn("quota guidance differs", review_surface["caveatNote"])
        self.assertIn("oauth_required", review_surface["authConditionNote"])
        self.assertIn("pagination", review_surface["notes"])
        self.assertIn("empty result sets", review_surface["notes"])

    def test_channel_sections_list_review_surface_exposes_quota_auth_and_caveat_notes(self):
        review_surface = build_channel_sections_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "channelSections.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["exclusiveSelectors"], ("channelId", "id", "mine"))
        self.assertIn("owner-scoped", review_surface["authConditionNote"])
        self.assertIn("lifecycle", review_surface["notes"])

    def test_comments_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_comments_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "comments.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "parentId"))
        self.assertIn("textFormat", review_surface["optionalFields"])
        self.assertIn("reply lookup", review_surface["notes"])

    def test_comment_threads_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_comment_threads_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "commentThreads")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "commentThreads.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["exclusiveSelectors"],
            ("videoId", "allThreadsRelatedToChannelId", "id"),
        )
        self.assertIn("searchTerms", review_surface["optionalFields"])
        self.assertIn("channel-related", review_surface["notes"])

    def test_guide_categories_list_review_surface_exposes_identity_quota_and_lifecycle_notes(self):
        review_surface = build_guide_categories_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "guideCategories")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "guideCategories.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "regionCode"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["lifecycleState"], "deprecated")
        self.assertIn("deprecated", review_surface["caveatNote"])
        self.assertIn("regionCode", review_surface["notes"])

    def test_i18n_languages_list_review_surface_exposes_identity_quota_and_lookup_notes(self):
        review_surface = build_i18n_languages_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "i18nLanguages")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "i18nLanguages.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "hl"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("hl", review_surface["notes"])
        self.assertIn("localization", review_surface["notes"])

    def test_i18n_regions_list_review_surface_exposes_identity_quota_and_lookup_notes(self):
        review_surface = build_i18n_regions_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "i18nRegions")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "i18nRegions.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "hl"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("hl", review_surface["notes"])
        self.assertIn("region", review_surface["notes"])
        self.assertIn("successful outcomes", review_surface["notes"])

    def test_video_abuse_report_reasons_list_review_surface_exposes_identity_quota_and_lookup_notes(self):
        review_surface = build_video_abuse_report_reasons_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videoAbuseReportReasons")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videoAbuseReportReasons.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part", "hl"))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("hl", review_surface["notes"])
        self.assertIn("localization", review_surface["notes"])
        self.assertIn("successful outcomes", review_surface["notes"])

    def test_video_categories_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_video_categories_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videoCategories")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videoCategories.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["optionalFields"], ("id", "regionCode", "hl"))
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "regionCode"))
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("region", review_surface["notes"])
        self.assertIn("hl", review_surface["notes"])
        self.assertIn("successful outcomes", review_surface["notes"])

    def test_videos_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_videos_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "videos.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"],
            ("id", "chart", "myRating", "pageToken", "maxResults", "regionCode", "videoCategoryId"),
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("id", "chart", "myRating"))
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("myRating", review_surface["authConditionNote"])
        self.assertIn("chart", review_surface["notes"])
        self.assertIn("successful outcomes", review_surface["notes"])

    def test_videos_insert_review_surface_exposes_quota_auth_and_caveat_notes(self):
        review_surface = integrations_package.build_videos_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "videos.insert")
        self.assertEqual(review_surface["quotaCost"], 1600)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body", "media"))
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos")
        self.assertIn("upload", review_surface["notes"])
        self.assertIn("private", review_surface["caveatNote"])

    def test_videos_update_review_surface_exposes_quota_auth_and_update_notes(self):
        review_surface = integrations_package.build_videos_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "videos")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "videos.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertEqual(review_surface["httpMethod"], "PUT")
        self.assertEqual(review_surface["pathShape"], "/youtube/v3/videos")
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("body.snippet.title", review_surface["notes"])
        self.assertIn("body.snippet.description", review_surface["notes"])
        self.assertIn("body.snippet.tags", review_surface["notes"])
        self.assertIn("body.localizations", review_surface["notes"])

    def test_members_list_review_surface_exposes_identity_quota_and_owner_notes(self):
        review_surface = build_members_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "members")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "members.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "mode"))
        self.assertEqual(review_surface["optionalFields"], ("pageToken", "maxResults"))
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("owner-only", review_surface["notes"])
        self.assertIn("delegation", review_surface["notes"])

    def test_memberships_levels_list_review_surface_exposes_identity_quota_and_owner_notes(self):
        review_surface = build_memberships_levels_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "membershipsLevels")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "membershipsLevels.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(review_surface["optionalFields"], ())
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("owner-only", review_surface["notes"])
        self.assertIn("unsupported", review_surface["notes"])

    def test_playlist_images_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_playlist_images_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistImages")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "playlistImages.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"], ("playlistId", "id", "pageToken", "maxResults")
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("playlistId", "id"))
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("pageToken", review_surface["notes"])
        self.assertIn("OAuth-required", review_surface["notes"])

    def test_playlist_items_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_playlist_items_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlistItems")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "playlistItems.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "api_key")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"], ("playlistId", "id", "pageToken", "maxResults")
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("playlistId", "id"))
        self.assertEqual(review_surface["lifecycleState"], "active")
        self.assertIsNone(review_surface["caveatNote"])
        self.assertIn("pageToken", review_surface["notes"])
        self.assertIn("API-key", review_surface["notes"])

    def test_playlists_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = integrations_package.build_playlists_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "playlists")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "playlists.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"], ("channelId", "id", "mine", "pageToken", "maxResults")
        )
        self.assertEqual(review_surface["exclusiveSelectors"], ("channelId", "id", "mine"))
        self.assertIn("owner-scoped", review_surface["authConditionNote"])
        self.assertIn("pageToken", review_surface["notes"])

    def test_subscriptions_list_review_surface_exposes_identity_quota_and_selector_notes(self):
        review_surface = build_subscriptions_list_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "subscriptions")
        self.assertEqual(review_surface["operationName"], "list")
        self.assertEqual(review_surface["operationKey"], "subscriptions.list")
        self.assertEqual(review_surface["quotaCost"], 1)
        self.assertEqual(review_surface["authMode"], "mixed/conditional")
        self.assertEqual(review_surface["requiredFields"], ("part",))
        self.assertEqual(
            review_surface["optionalFields"],
            ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers", "pageToken", "maxResults", "order"),
        )
        self.assertEqual(
            review_surface["exclusiveSelectors"],
            ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers"),
        )
        self.assertIn("oauth_required", review_surface["authConditionNote"])
        self.assertIn("order", review_surface["notes"])

    def test_comments_insert_review_surface_exposes_identity_quota_and_auth_notes(self):
        review_surface = build_comments_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "comments.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("parentId", review_surface["notes"])
        self.assertIn("textOriginal", review_surface["notes"])

    def test_comment_threads_insert_review_surface_exposes_identity_quota_and_auth_notes(self):
        review_surface = build_comment_threads_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "commentThreads")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "commentThreads.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("videoId", review_surface["notes"])
        self.assertIn("topLevelComment", review_surface["notes"])

    def test_comments_update_review_surface_exposes_identity_quota_auth_and_write_notes(self):
        review_surface = build_comments_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "comments.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("textOriginal", review_surface["notes"])

    def test_comments_set_moderation_status_review_surface_exposes_identity_quota_auth_and_moderation_notes(self):
        review_surface = build_comments_set_moderation_status_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "setModerationStatus")
        self.assertEqual(review_surface["operationKey"], "comments.setModerationStatus")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id", "moderationStatus"))
        self.assertIn("banAuthor", review_surface["optionalFields"])
        self.assertIn("published", review_surface["notes"])
        self.assertIn("heldForReview", review_surface["notes"])
        self.assertIn("rejected", review_surface["notes"])

    def test_comments_delete_review_surface_exposes_identity_quota_auth_and_delete_notes(self):
        review_surface = build_comments_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "comments")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "comments.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("target comment", review_surface["notes"])
        self.assertIn("target-state", review_surface["notes"])

    def test_channel_sections_insert_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channel_sections_insert_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "insert")
        self.assertEqual(review_surface["operationKey"], "channelSections.insert")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("snippet.type", review_surface["notes"])
        self.assertIn("title", review_surface["notes"])

    def test_channel_sections_update_review_surface_exposes_quota_auth_and_write_notes(self):
        review_surface = build_channel_sections_update_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "update")
        self.assertEqual(review_surface["operationKey"], "channelSections.update")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("part", "body"))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("body.id", review_surface["notes"])
        self.assertIn("snippet.type", review_surface["notes"])

    def test_channel_sections_delete_review_surface_exposes_quota_auth_and_delete_notes(self):
        review_surface = build_channel_sections_delete_wrapper().review_surface()

        self.assertEqual(review_surface["resourceName"], "channelSections")
        self.assertEqual(review_surface["operationName"], "delete")
        self.assertEqual(review_surface["operationKey"], "channelSections.delete")
        self.assertEqual(review_surface["quotaCost"], 50)
        self.assertEqual(review_surface["authMode"], "oauth_required")
        self.assertEqual(review_surface["requiredFields"], ("id",))
        self.assertIn("onBehalfOfContentOwner", review_surface["optionalFields"])
        self.assertIn("owner-scoped", review_surface["notes"])
        self.assertIn("one target", review_surface["notes"])


if __name__ == "__main__":
    unittest.main()
