import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

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
    build_channels_list_wrapper,
    build_channels_update_wrapper,
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


if __name__ == "__main__":
    unittest.main()
