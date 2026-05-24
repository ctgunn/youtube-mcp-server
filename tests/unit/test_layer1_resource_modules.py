import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))


REQUIRED_RESOURCE_FAMILIES = (
    "activities",
    "captions",
    "channel_banners",
    "channels",
    "channel_sections",
    "comments",
    "comment_threads",
    "guide_categories",
    "localization",
    "members",
    "memberships_levels",
    "playlist_images",
    "playlist_items",
    "playlists",
    "search",
    "subscriptions",
    "thumbnails",
    "video_abuse_report_reasons",
    "video_categories",
    "videos",
    "watermarks",
)


class Layer1ResourceModuleUnitTests(unittest.TestCase):
    def test_required_resource_families_are_declared_in_test_fixture(self):
        self.assertEqual(len(REQUIRED_RESOURCE_FAMILIES), 21)
        self.assertIn("captions", REQUIRED_RESOURCE_FAMILIES)
        self.assertIn("videos", REQUIRED_RESOURCE_FAMILIES)
        self.assertIn("watermarks", REQUIRED_RESOURCE_FAMILIES)

    def test_resource_package_exposes_required_family_inventory(self):
        resources = importlib.import_module("mcp_server.integrations.resources")

        self.assertEqual(resources.REQUIRED_RESOURCE_FAMILIES, REQUIRED_RESOURCE_FAMILIES)

    def test_resource_package_registers_and_returns_family_builders(self):
        resources = importlib.import_module("mcp_server.integrations.resources")

        def build_fake_wrapper():
            return "fake-wrapper"

        registry = resources.build_family_builder_registry(
            {"fake_family": {"fake.operation": build_fake_wrapper}}
        )

        self.assertEqual(resources.get_family_builder(registry, "fake_family", "fake.operation")(), "fake-wrapper")
        self.assertEqual(resources.get_family_builders(registry, "fake_family"), {"fake.operation": build_fake_wrapper})

    def test_resource_package_rejects_unknown_family_and_operation(self):
        resources = importlib.import_module("mcp_server.integrations.resources")
        registry = resources.build_family_builder_registry({"fake_family": {}})

        with self.assertRaisesRegex(KeyError, "unknown resource family"):
            resources.get_family_builders(registry, "missing_family")

        with self.assertRaisesRegex(KeyError, "unknown operation"):
            resources.get_family_builder(registry, "fake_family", "missing.operation")

    def test_list_and_mixed_auth_families_expose_resource_builders(self):
        resources = importlib.import_module("mcp_server.integrations.resources")

        activities = importlib.import_module("mcp_server.integrations.resources.activities")
        channels = importlib.import_module("mcp_server.integrations.resources.channels")
        search = importlib.import_module("mcp_server.integrations.resources.search")

        self.assertEqual(activities.build_activities_list_wrapper().metadata.operation_key, "activities.list")
        self.assertEqual(channels.build_channels_list_wrapper().metadata.operation_key, "channels.list")
        self.assertEqual(search.build_search_list_wrapper().metadata.operation_key, "search.list")
        self.assertEqual(
            resources.get_family_builder(resources.DEFAULT_FAMILY_BUILDER_REGISTRY, "channels", "channels.list")()
            .metadata.operation_key,
            "channels.list",
        )

    def test_upload_mutation_delete_and_oauth_families_expose_resource_builders(self):
        resources = importlib.import_module("mcp_server.integrations.resources")

        captions = importlib.import_module("mcp_server.integrations.resources.captions")
        thumbnails = importlib.import_module("mcp_server.integrations.resources.thumbnails")
        videos = importlib.import_module("mcp_server.integrations.resources.videos")
        watermarks = importlib.import_module("mcp_server.integrations.resources.watermarks")

        self.assertEqual(captions.build_captions_insert_wrapper().metadata.operation_key, "captions.insert")
        self.assertEqual(thumbnails.build_thumbnails_set_wrapper().metadata.operation_key, "thumbnails.set")
        self.assertEqual(videos.build_videos_delete_wrapper().metadata.operation_key, "videos.delete")
        self.assertEqual(watermarks.build_watermarks_unset_wrapper().metadata.operation_key, "watermarks.unset")
        self.assertEqual(
            resources.get_family_builder(
                resources.DEFAULT_FAMILY_BUILDER_REGISTRY,
                "watermarks",
                "watermarks.unset",
            )().metadata.operation_key,
            "watermarks.unset",
        )

    def test_wrappers_facade_matches_resource_family_builders(self):
        wrappers = importlib.import_module("mcp_server.integrations.wrappers")
        videos = importlib.import_module("mcp_server.integrations.resources.videos")
        watermarks = importlib.import_module("mcp_server.integrations.resources.watermarks")

        self.assertEqual(
            wrappers.build_videos_list_wrapper().review_surface(),
            videos.build_videos_list_wrapper().review_surface(),
        )
        self.assertEqual(
            wrappers.build_watermarks_set_wrapper().review_surface(),
            watermarks.build_watermarks_set_wrapper().review_surface(),
        )

    def test_wrapper_implementations_live_in_resource_family_modules(self):
        wrappers = importlib.import_module("mcp_server.integrations.wrappers")
        activities = importlib.import_module("mcp_server.integrations.resources.activities")
        videos = importlib.import_module("mcp_server.integrations.resources.videos")

        self.assertEqual(
            activities.ActivitiesListWrapper.__module__,
            "mcp_server.integrations.resources.activities",
        )
        self.assertEqual(
            wrappers.ActivitiesListWrapper.__module__,
            "mcp_server.integrations.resources.activities",
        )
        self.assertEqual(
            videos.VideosReportAbuseWrapper.__module__,
            "mcp_server.integrations.resources.videos",
        )
        with open(wrappers.__file__, "r", encoding="utf-8") as handle:
            self.assertLess(len(handle.readlines()), 80)

    def test_resource_family_access_matches_legacy_builder_surfaces(self):
        resources = importlib.import_module("mcp_server.integrations.resources")
        wrappers = importlib.import_module("mcp_server.integrations.wrappers")

        builder = resources.get_family_builder(
            resources.DEFAULT_FAMILY_BUILDER_REGISTRY,
            "videos",
            "videos.reportAbuse",
        )

        self.assertEqual(
            builder().review_surface(),
            wrappers.build_videos_report_abuse_wrapper().review_surface(),
        )

    def test_response_normalizers_are_family_owned(self):
        normalizers = importlib.import_module("mcp_server.integrations.resources.normalizers")

        registry = normalizers.default_response_normalizer_registry()

        self.assertEqual(registry["videos.list"].family_name, "videos")
        self.assertEqual(
            registry["videos.list"]._handler.__module__,
            "mcp_server.integrations.resources.response_normalizers.videos",
        )
        self.assertEqual(
            registry["captions.download"]._handler.__module__,
            "mcp_server.integrations.resources.response_normalizers.captions",
        )

    def test_consumer_summary_methods_are_family_mixins(self):
        consumer_module = importlib.import_module("mcp_server.integrations.consumer")
        consumer = consumer_module.RepresentativeHigherLayerConsumer

        self.assertIn("VideosConsumerMixin", {base.__name__ for base in consumer.__mro__})
        self.assertIn("CaptionsConsumerMixin", {base.__name__ for base in consumer.__mro__})
        self.assertEqual(
            consumer.fetch_videos_summary.__module__,
            "mcp_server.integrations.resources.consumers.videos",
        )
        self.assertEqual(
            consumer.download_caption_summary.__module__,
            "mcp_server.integrations.resources.consumers.captions",
        )
        with open(consumer_module.__file__, "r", encoding="utf-8") as handle:
            self.assertLess(len(handle.readlines()), 40)


if __name__ == "__main__":
    unittest.main()
