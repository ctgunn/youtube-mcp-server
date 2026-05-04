import io
import json
import os
import sys
import unittest
from urllib.error import HTTPError

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.integrations.auth import AuthContext, AuthMode, CredentialBundle
from mcp_server.integrations.executor import RequestExecution
from mcp_server.integrations.youtube import (
    build_youtube_data_api_executor,
    build_youtube_data_api_request,
    build_youtube_data_api_transport,
)
from mcp_server.integrations.wrappers import (
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
    build_subscriptions_list_wrapper,
    build_playlists_update_wrapper,
    build_playlists_list_wrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)


class _FakeHTTPResponse:
    def __init__(self, payload: dict | str):
        if isinstance(payload, dict):
            self._payload = json.dumps(payload).encode("utf-8")
        else:
            self._payload = payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class YouTubeTransportUnitTests(unittest.TestCase):
    def _execution(self, *, arguments: dict[str, object], auth_context: AuthContext) -> RequestExecution:
        return RequestExecution(
            metadata=build_activities_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _captions_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_captions_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channels_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channels_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channels_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channels_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlists_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlists_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _search_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_search_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _subscriptions_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_subscriptions_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_images_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_images_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_images_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_images_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channel_sections_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channel_sections_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comments_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comments_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comment_threads_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comment_threads_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _guide_categories_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_guide_categories_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _i18n_languages_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_i18n_languages_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _i18n_regions_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_i18n_regions_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _members_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_members_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _memberships_levels_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_memberships_levels_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_images_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_images_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_items_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_items_list_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_items_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_items_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlists_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlists_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlists_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlists_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlists_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlists_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_items_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_items_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channel_sections_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channel_sections_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comments_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comments_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comment_threads_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comment_threads_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comments_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comments_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comments_set_moderation_status_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comments_set_moderation_status_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _comments_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_comments_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_images_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_images_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _playlist_items_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_playlist_items_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channel_sections_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channel_sections_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channel_sections_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channel_sections_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _captions_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_captions_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _captions_update_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_captions_update_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _captions_download_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_captions_download_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _captions_delete_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_captions_delete_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def _channel_banners_insert_execution(
        self,
        *,
        arguments: dict[str, object],
        auth_context: AuthContext,
    ) -> RequestExecution:
        return RequestExecution(
            metadata=build_channel_banners_insert_wrapper().metadata,
            arguments=arguments,
            auth_context=auth_context,
        )

    def test_builds_api_key_request_for_public_channel_activity(self):
        execution = self._execution(
            arguments={"part": "snippet", "channelId": "UC123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/activities?", request.full_url)
        self.assertIn("channelId=UC123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_builds_oauth_request_for_authorized_activity(self):
        execution = self._execution(
            arguments={"part": "snippet", "mine": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("mine=true", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_api_key_request_for_channels_id_selector(self):
        execution = self._channels_execution(
            arguments={"part": "snippet", "id": "UC123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/channels?", request.full_url)
        self.assertIn("id=UC123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("key=yt-key", request.full_url)

    def test_builds_api_key_request_for_channels_handle_selector(self):
        execution = self._channels_execution(
            arguments={"part": "snippet", "forHandle": "@channel"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("forHandle=%40channel", request.full_url)

    def test_builds_api_key_request_for_channels_username_selector(self):
        execution = self._channels_execution(
            arguments={"part": "snippet", "forUsername": "legacy-user"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("forUsername=legacy-user", request.full_url)

    def test_builds_api_key_request_for_playlists_channel_selector(self):
        execution = self._playlists_execution(
            arguments={"part": "snippet", "channelId": "UC123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlists?", request.full_url)
        self.assertIn("channelId=UC123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_builds_api_key_request_for_playlists_id_selector(self):
        execution = self._playlists_execution(
            arguments={"part": "snippet", "id": "PL123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("id=PL123", request.full_url)
        self.assertIn("key=yt-key", request.full_url)

    def test_builds_oauth_request_for_playlists_mine_selector(self):
        execution = self._playlists_execution(
            arguments={"part": "snippet", "mine": True, "pageToken": "cursor-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("mine=true", request.full_url)
        self.assertIn("pageToken=cursor-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_api_key_request_for_search_list_public_query(self):
        execution = self._search_execution(
            arguments={
                "part": "snippet",
                "q": "mcp server",
                "type": "video",
                "publishedAfter": "2026-01-01T00:00:00Z",
                "relevanceLanguage": "en",
                "regionCode": "US",
                "pageToken": "cursor-1",
                "maxResults": 5,
            },
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/search?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("q=mcp+server", request.full_url)
        self.assertIn("type=video", request.full_url)
        self.assertIn("publishedAfter=2026-01-01T00%3A00%3A00Z", request.full_url)
        self.assertIn("relevanceLanguage=en", request.full_url)
        self.assertIn("regionCode=US", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_search_list_transport_returns_normalized_query_context(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": {"videoId": "video-123"}}], "nextPageToken": "cursor-2"}
            )
        )

        result = transport(
            self._search_execution(
                arguments={
                    "part": "snippet",
                    "q": "mcp server",
                    "type": "video",
                    "publishedAfter": "2026-01-01T00:00:00Z",
                    "maxResults": 5,
                },
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
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

    def test_builds_api_key_request_for_subscriptions_channel_selector(self):
        execution = self._subscriptions_execution(
            arguments={"part": "snippet", "channelId": "UC123", "maxResults": 5, "order": "alphabetical"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/subscriptions?", request.full_url)
        self.assertIn("channelId=UC123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("order=alphabetical", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_builds_oauth_request_for_subscriptions_private_selector(self):
        execution = self._subscriptions_execution(
            arguments={"part": "snippet", "mySubscribers": True, "pageToken": "cursor-1"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("mySubscribers=true", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_subscriptions_list_transport_returns_normalized_selector_context(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "sub-123"}], "nextPageToken": "cursor-2"}
            )
        )
        execution = self._subscriptions_execution(
            arguments={"part": "snippet", "mySubscribers": True, "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        result = transport(execution)

        self.assertEqual(result["selectorName"], "mySubscribers")
        self.assertTrue(result["selectorValue"])
        self.assertEqual(result["authPath"], "oauth")
        self.assertEqual(
            result["requestContext"],
            {
                "part": "snippet",
                "selectorName": "mySubscribers",
                "selectorValue": True,
                "maxResults": 5,
            },
        )

    def test_transport_normalizes_subscriptions_list_invalid_request_errors(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: (_ for _ in ()).throw(
                HTTPError(
                    request.full_url,
                    400,
                    "Bad Request",
                    hdrs=None,
                    fp=io.BytesIO(b'{"error":{"message":"Missing selector","errors":[{"reason":"required"}]}}'),
                )
            )
        )
        execution = self._subscriptions_execution(
            arguments={"part": "snippet", "channelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        with self.assertRaisesRegex(Exception, "Missing selector") as context:
            transport(execution)

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_search_list_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/search",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"videoDuration requires type=video"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "videoDuration requires type=video") as context:
            transport(
                self._search_execution(
                    arguments={"part": "snippet", "q": "mcp server", "videoDuration": "long"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_search_list_upstream_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/search",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Search backend unavailable"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Search backend unavailable") as context:
            transport(
                self._search_execution(
                    arguments={"part": "snippet", "q": "mcp server"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "transient")

    def test_builds_api_key_request_for_guide_categories_region_lookup(self):
        execution = self._guide_categories_execution(
            arguments={"part": "snippet", "regionCode": "US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/guideCategories?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("regionCode=US", request.full_url)

    def test_builds_api_key_request_for_i18n_languages_display_language_lookup(self):
        execution = self._i18n_languages_execution(
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/i18nLanguages?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("hl=en_US", request.full_url)
        self.assertIn("key=yt-key", request.full_url)

    def test_builds_api_key_request_for_i18n_regions_display_language_lookup(self):
        execution = self._i18n_regions_execution(
            arguments={"part": "snippet", "hl": "en_US"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/i18nRegions?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("hl=en_US", request.full_url)
        self.assertIn("key=yt-key", request.full_url)

    def test_builds_oauth_request_for_members_mode_lookup(self):
        execution = self._members_execution(
            arguments={"part": "snippet", "mode": "updates", "pageToken": "cursor-1", "maxResults": 25},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/members?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("mode=updates", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertIn("maxResults=25", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_oauth_request_for_channels_mine_selector(self):
        execution = self._channels_execution(
            arguments={"part": "snippet", "mine": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("mine=true", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_api_key_request_for_channel_sections_channel_selector(self):
        execution = self._channel_sections_execution(
            arguments={"part": "snippet", "channelId": "UC123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/channelSections?", request.full_url)
        self.assertIn("channelId=UC123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertIn("key=yt-key", request.full_url)

    def test_builds_api_key_request_for_channel_sections_id_selector(self):
        execution = self._channel_sections_execution(
            arguments={"part": "snippet", "id": "section-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("id=section-123", request.full_url)

    def test_builds_oauth_request_for_channel_sections_mine_selector(self):
        execution = self._channel_sections_execution(
            arguments={"part": "snippet", "mine": True, "pageToken": "cursor-1"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("mine=true", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_api_key_request_for_comments_id_selector(self):
        execution = self._comments_execution(
            arguments={"part": "snippet", "id": ["comment-123", "comment-456"], "textFormat": "plainText"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/comments?", request.full_url)
        self.assertIn("id=comment-123", request.full_url)
        self.assertIn("id=comment-456", request.full_url)
        self.assertIn("textFormat=plainText", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_builds_api_key_request_for_comments_parent_selector(self):
        execution = self._comments_execution(
            arguments={"part": "snippet", "parentId": "comment-123", "pageToken": "cursor-1", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("parentId=comment-123", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertIn("maxResults=5", request.full_url)

    def test_transport_returns_comments_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"items": [{"id": "comment-123"}], "nextPageToken": "cursor-2"})
        )

        result = transport(
            self._comments_execution(
                arguments={"part": "snippet", "id": ["comment-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["items"][0]["id"], "comment-123")
        self.assertEqual(result["nextPageToken"], "cursor-2")

    def test_builds_api_key_request_for_comment_threads_video_selector(self):
        execution = self._comment_threads_execution(
            arguments={
                "part": "snippet",
                "videoId": "video-123",
                "order": "time",
                "searchTerms": "launch",
                "textFormat": "plainText",
            },
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("/youtube/v3/commentThreads?", request.full_url)
        self.assertIn("videoId=video-123", request.full_url)
        self.assertIn("order=time", request.full_url)
        self.assertIn("searchTerms=launch", request.full_url)
        self.assertIn("textFormat=plainText", request.full_url)
        self.assertIn("key=yt-key", request.full_url)
        self.assertIsNone(request.headers.get("Authorization"))

    def test_builds_api_key_request_for_comment_threads_channel_selector(self):
        execution = self._comment_threads_execution(
            arguments={
                "part": "snippet",
                "allThreadsRelatedToChannelId": "UC123",
                "pageToken": "cursor-1",
                "maxResults": 5,
            },
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("allThreadsRelatedToChannelId=UC123", request.full_url)
        self.assertIn("pageToken=cursor-1", request.full_url)
        self.assertIn("maxResults=5", request.full_url)

    def test_transport_returns_comment_threads_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "thread-123"}], "nextPageToken": "cursor-2"}
            )
        )

        result = transport(
            self._comment_threads_execution(
                arguments={"part": "snippet", "id": ["thread-123"]},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["items"][0]["id"], "thread-123")
        self.assertEqual(result["nextPageToken"], "cursor-2")

    def test_transport_returns_guide_categories_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "GC1"}], "regionCode": "US"}
            )
        )

        result = transport(
            self._guide_categories_execution(
                arguments={"part": "snippet", "regionCode": "US"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["regionCode"], "US")
        self.assertEqual(result["items"][0]["id"], "GC1")

    def test_transport_returns_i18n_languages_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "en"}], "hl": "en_US"}
            )
        )

        result = transport(
            self._i18n_languages_execution(
                arguments={"part": "snippet", "hl": "en_US"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["hl"], "en_US")
        self.assertEqual(result["items"][0]["id"], "en")

    def test_transport_returns_i18n_regions_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "US"}], "hl": "en_US"}
            )
        )

        result = transport(
            self._i18n_regions_execution(
                arguments={"part": "snippet", "hl": "en_US"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["hl"], "en_US")
        self.assertEqual(result["items"][0]["id"], "US")

    def test_transport_normalizes_i18n_regions_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/i18nRegions",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"hl is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "hl is required") as context:
            transport(
                self._i18n_regions_execution(
                    arguments={"part": "snippet", "hl": "en_US"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_returns_members_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "member-123"}], "mode": "updates"}
            )
        )

        result = transport(
            self._members_execution(
                arguments={"part": "snippet", "mode": "updates"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["mode"], "updates")
        self.assertEqual(result["items"][0]["id"], "member-123")

    def test_builds_oauth_request_for_memberships_levels_list(self):
        execution = self._memberships_levels_execution(
            arguments={"part": "snippet"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("https://www.googleapis.com/youtube/v3/membershipsLevels?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertNotIn("key=", request.full_url)
        self.assertEqual(request.headers.get("Authorization"), "Bearer oauth-token")

    def test_transport_returns_memberships_levels_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "level-123"}], "part": "snippet"}
            )
        )

        result = transport(
            self._memberships_levels_execution(
                arguments={"part": "snippet"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["items"][0]["id"], "level-123")

    def test_transport_normalizes_memberships_levels_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/membershipsLevels",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"part is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "part is required") as context:
            transport(
                self._memberships_levels_execution(
                    arguments={"part": "snippet"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_preserves_memberships_levels_auth_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/membershipsLevels",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Membership level access denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Membership level access denied") as context:
            transport(
                self._memberships_levels_execution(
                    arguments={"part": "snippet"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_request_for_playlist_images_list(self):
        execution = self._playlist_images_execution(
            arguments={
                "part": "snippet",
                "playlistId": "PL123",
                "pageToken": "cursor-123",
                "maxResults": 10,
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("https://www.googleapis.com/youtube/v3/playlistImages?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("playlistId=PL123", request.full_url)
        self.assertIn("pageToken=cursor-123", request.full_url)
        self.assertIn("maxResults=10", request.full_url)
        self.assertNotIn("key=", request.full_url)
        self.assertEqual(request.headers.get("Authorization"), "Bearer oauth-token")

    def test_transport_returns_playlist_images_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "image-123"}]}
            )
        )

        result = transport(
            self._playlist_images_execution(
                arguments={"part": "snippet", "playlistId": "PL123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["selectorName"], "playlistId")
        self.assertEqual(result["selectorValue"], "PL123")
        self.assertEqual(result["items"][0]["id"], "image-123")

    def test_transport_returns_empty_playlist_images_payload_as_success(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"items": []})
        )

        result = transport(
            self._playlist_images_execution(
                arguments={"part": "snippet", "id": "image-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["items"], [])
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["selectorName"], "id")
        self.assertEqual(result["selectorValue"], "image-123")

    def test_transport_normalizes_playlist_images_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlistId or id is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlistId or id is required") as context:
            transport(
                self._playlist_images_execution(
                    arguments={"part": "snippet", "playlistId": "PL123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_preserves_playlist_images_auth_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image access denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image access denied") as context:
            transport(
                self._playlist_images_execution(
                    arguments={"part": "snippet", "id": "image-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_members_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/members",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"mode is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "mode is required") as context:
            transport(
                self._members_execution(
                    arguments={"part": "snippet", "mode": "updates"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_members_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/members",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Membership access denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Membership access denied") as context:
            transport(
                self._members_execution(
                    arguments={"part": "snippet", "mode": "updates"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_guide_categories_lifecycle_unavailable_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/guideCategories",
            code=410,
            msg="Gone",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"guideCategories is deprecated and unavailable"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "guideCategories is deprecated and unavailable") as context:
            transport(
                self._guide_categories_execution(
                    arguments={"part": "snippet", "regionCode": "US"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "lifecycle_unavailable")

    def test_transport_normalizes_i18n_languages_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/i18nLanguages",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"hl is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "hl is required") as context:
            transport(
                self._i18n_languages_execution(
                    arguments={"part": "snippet", "hl": "en_US"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comment_threads_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/commentThreads",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"part is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "part is required") as context:
            transport(
                self._comment_threads_execution(
                    arguments={"part": "snippet", "videoId": "video-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_returns_comment_threads_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {
                    "id": "thread-456",
                    "snippet": {
                        "videoId": "video-123",
                        "topLevelComment": {
                            "id": "comment-999",
                            "snippet": {"textOriginal": "Top-level text"},
                        },
                    },
                }
            )
        )

        result = transport(
            self._comment_threads_insert_execution(
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
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "thread-456")
        self.assertEqual(result["snippet"]["videoId"], "video-123")
        self.assertEqual(result["snippet"]["topLevelComment"]["id"], "comment-999")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_transport_normalizes_comment_threads_insert_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/commentThreads",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(
                b'{"error":{"message":"body.snippet.topLevelComment.snippet.textOriginal is required"}}'
            ),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(
            RuntimeError,
            "body.snippet.topLevelComment.snippet.textOriginal is required",
        ) as context:
            transport(
                self._comment_threads_insert_execution(
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
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comment_threads_insert_target_eligibility_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/commentThreads",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Comments disabled for this discussion target"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Comments disabled for this discussion target") as context:
            transport(
                self._comment_threads_insert_execution(
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
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "target_eligibility")

    def test_transport_returns_comments_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {
                    "id": "comment-456",
                    "snippet": {"parentId": "comment-123", "textOriginal": "Reply text"},
                }
            )
        )

        result = transport(
            self._comments_insert_execution(
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                    "onBehalfOfContentOwner": "owner-123",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "comment-456")
        self.assertEqual(result["snippet"]["parentId"], "comment-123")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_transport_normalizes_comments_insert_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"body.snippet.textOriginal is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "body.snippet.textOriginal is required") as context:
            transport(
                self._comments_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comments_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Required selector is missing"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Required selector is missing") as context:
            transport(
                self._comments_execution(
                    arguments={"part": "snippet", "id": ["comment-123"]},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="yt-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comments_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"API key not valid. Please pass a valid API key."}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "API key not valid") as context:
            transport(
                self._comments_execution(
                    arguments={"part": "snippet", "parentId": "comment-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="bad-key"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_put_request_for_channels_update(self):
        execution = self._channels_update_execution(
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
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/channels?", request.full_url)
        self.assertIn("part=brandingSettings%2Clocalizations", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "UC123"', request.data)
        self.assertIn(b'"bannerExternalUrl": "https://yt.example/banner"', request.data)

    def test_builds_oauth_put_request_for_comments_update(self):
        execution = self._comments_update_execution(
            arguments={
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/comments?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "comment-123"', request.data)
        self.assertIn(b'"textOriginal": "Updated comment"', request.data)

    def test_builds_oauth_put_request_for_playlist_items_update(self):
        execution = self._playlist_items_update_execution(
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
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistItems?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "playlist-item-123"', request.data)
        self.assertIn(b'"playlistId": "PL123"', request.data)
        self.assertIn(b'"videoId": "video-123"', request.data)

    def test_builds_oauth_post_request_for_comments_set_moderation_status(self):
        execution = self._comments_set_moderation_status_execution(
            arguments={
                "id": ["comment-123", "comment-456"],
                "moderationStatus": "rejected",
                "banAuthor": True,
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/comments/setModerationStatus?", request.full_url)
        self.assertIn("id=comment-123", request.full_url)
        self.assertIn("id=comment-456", request.full_url)
        self.assertIn("moderationStatus=rejected", request.full_url)
        self.assertIn("banAuthor=true", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertIsNone(request.data)

    def test_transport_returns_parsed_channel_sections_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {
                    "items": [{"id": "section-123", "snippet": {"type": "singlePlaylist"}}],
                    "nextPageToken": "cursor-2",
                }
            )
        )

        result = transport(
            self._channel_sections_execution(
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["items"][0]["id"], "section-123")
        self.assertEqual(result["nextPageToken"], "cursor-2")

    def test_builds_oauth_post_request_for_channel_sections_insert(self):
        execution = self._channel_sections_insert_execution(
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
                "onBehalfOfContentOwnerChannel": "UC123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/channelSections?", request.full_url)
        self.assertIn("part=snippet%2CcontentDetails", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertIn("onBehalfOfContentOwnerChannel=UC123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"type": "multiplePlaylists"', request.data)
        self.assertIn(b'"title": "Featured playlists"', request.data)

    def test_transport_normalizes_successful_channel_sections_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {
                    "id": "section-123",
                    "snippet": {"type": "multipleChannels", "title": "Featured channels"},
                }
            )
        )

        result = transport(
            self._channel_sections_insert_execution(
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
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "section-123")
        self.assertEqual(result["snippet"]["type"], "multipleChannels")
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_transport_preserves_channel_sections_insert_create_limit_failures_as_upstream_service(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"The channel already has the maximum number of sections"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "maximum number of sections") as context:
            transport(
                self._channel_sections_insert_execution(
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
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_transport_normalizes_channel_sections_insert_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section create denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel section create denied") as context:
            transport(
                self._channel_sections_insert_execution(
                    arguments={
                        "part": "snippet,contentDetails",
                        "body": {
                            "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                            "contentDetails": {"playlists": ["PL123"]},
                        },
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_put_request_for_channel_sections_update(self):
        execution = self._channel_sections_update_execution(
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
                "onBehalfOfContentOwnerChannel": "UC123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/channelSections?", request.full_url)
        self.assertIn("part=snippet%2CcontentDetails", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertIn("onBehalfOfContentOwnerChannel=UC123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "section-123"', request.data)
        self.assertIn(b'"type": "multipleChannels"', request.data)

    def test_transport_normalizes_successful_channel_sections_update_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {
                    "id": "section-123",
                    "snippet": {"type": "multipleChannels", "title": "Updated featured channels"},
                }
            )
        )

        result = transport(
            self._channel_sections_update_execution(
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
                    "onBehalfOfContentOwnerChannel": "UC123",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "section-123")
        self.assertEqual(result["snippet"]["type"], "multipleChannels")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["delegatedOwnerChannel"], "UC123")

    def test_transport_normalizes_channel_sections_update_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section update body contains read-only fields"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "read-only fields") as context:
            transport(
                self._channel_sections_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {
                            "id": "section-123",
                            "snippet": {"type": "singlePlaylist", "channelId": "UC123"},
                            "contentDetails": {"playlists": ["PL123"]},
                        },
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_channel_sections_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel section update denied") as context:
            transport(
                self._channel_sections_update_execution(
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
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_request_for_channel_sections_delete(self):
        execution = self._channel_sections_delete_execution(
            arguments={
                "id": "section-123",
                "onBehalfOfContentOwner": "owner-123",
                "onBehalfOfContentOwnerChannel": "UC123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/channelSections?", request.full_url)
        self.assertIn("id=section-123", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertIn("onBehalfOfContentOwnerChannel=UC123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_channel_sections_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._channel_sections_delete_execution(
                arguments={
                    "id": "section-123",
                    "onBehalfOfContentOwner": "owner-123",
                    "onBehalfOfContentOwnerChannel": "UC123",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["channelSectionId"], "section-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["delegatedOwnerChannel"], "UC123")

    def test_transport_normalizes_channel_sections_delete_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections?id=section-123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section delete request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel section delete request is invalid") as context:
            transport(
                self._channel_sections_delete_execution(
                    arguments={"id": "section-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_channel_sections_delete_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections?id=section-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section delete denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel section delete denied") as context:
            transport(
                self._channel_sections_delete_execution(
                    arguments={"id": "section-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_channel_sections_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelSections?id=section-404",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel section not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel section not found") as context:
            transport(
                self._channel_sections_delete_execution(
                    arguments={"id": "section-404"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_builds_oauth_request_for_captions_video_lookup(self):
        execution = self._captions_execution(
            arguments={"part": "snippet", "videoId": "video-123", "maxResults": 5},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/captions?", request.full_url)
        self.assertIn("videoId=video-123", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("maxResults=5", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_oauth_request_for_captions_delegation(self):
        execution = self._captions_execution(
            arguments={
                "part": "snippet",
                "id": "caption-123",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("id=caption-123", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)

    def test_builds_oauth_request_for_captions_insert_upload(self):
        execution = self._captions_insert_execution(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"videoId": "video-123", "language": "en", "name": "English"}},
                "media": {"mimeType": "text/plain", "content": "caption payload"},
                "sync": True,
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/captions?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("sync=true", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", request.headers["Content-type"])
        self.assertIn(b'"videoId": "video-123"', request.data)
        self.assertIn(b"caption payload", request.data)

    def test_builds_oauth_request_for_comments_insert_reply(self):
        execution = self._comments_insert_execution(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/comments?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"parentId": "comment-123"', request.data)
        self.assertIn(b'"textOriginal": "Reply text"', request.data)

    def test_builds_oauth_request_for_comment_threads_insert(self):
        execution = self._comment_threads_insert_execution(
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
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/commentThreads?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"videoId": "video-123"', request.data)
        self.assertIn(b'"textOriginal": "Top-level text"', request.data)

    def test_builds_oauth_request_for_captions_update_body_only(self):
        execution = self._captions_update_execution(
            arguments={
                "part": "snippet",
                "body": {"id": "caption-123", "snippet": {"language": "en", "name": "Updated English"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/captions?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "caption-123"', request.data)

    def test_builds_oauth_request_for_captions_update_body_plus_media(self):
        execution = self._captions_update_execution(
            arguments={
                "part": "snippet",
                "body": {"id": "caption-123", "snippet": {"language": "en", "name": "Updated English"}},
                "media": {"mimeType": "text/plain", "content": "updated caption payload"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", request.headers["Content-type"])
        self.assertIn(b'"id": "caption-123"', request.data)
        self.assertIn(b"updated caption payload", request.data)

    def test_builds_oauth_request_for_captions_download(self):
        execution = self._captions_download_execution(
            arguments={
                "id": "caption-123",
                "tfmt": "srt",
                "tlang": "es",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/captions/caption-123?", request.full_url)
        self.assertIn("tfmt=srt", request.full_url)
        self.assertIn("tlang=es", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_builds_oauth_request_for_captions_delete(self):
        execution = self._captions_delete_execution(
            arguments={
                "id": "caption-123",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/captions/caption-123?", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_captions_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._captions_delete_execution(
                arguments={"id": "caption-123", "onBehalfOfContentOwner": "owner-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["captionId"], "caption-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["delegatedOwner"], "owner-123")

    def test_builds_oauth_request_for_channel_banners_insert(self):
        execution = self._channel_banners_insert_execution(
            arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/channelBanners/insert", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "image/png")
        self.assertEqual(request.data, b"banner-bytes")

    def test_builds_oauth_request_for_channel_banners_insert_delegation(self):
        execution = self._channel_banners_insert_execution(
            arguments={
                "media": {"mimeType": "image/png", "content": b"banner-bytes"},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)

    def test_transport_normalizes_successful_channel_banners_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"url": "https://yt.example/banner"})
        )

        result = transport(
            self._channel_banners_insert_execution(
                arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["bannerUrl"], "https://yt.example/banner")
        self.assertTrue(result["isUploaded"])

    def test_builds_oauth_request_for_playlist_images_insert_upload(self):
        execution = self._playlist_images_insert_execution(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "type": "featured"}},
                "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistImages?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", request.headers["Content-type"])
        self.assertIn(b'"playlistId": "PL123"', request.data)
        self.assertIn(b"playlist-image-bytes", request.data)

    def test_transport_normalizes_successful_playlist_images_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"id": "playlist-image-123", "kind": "youtube#playlistImage"}
            )
        )

        result = transport(
            self._playlist_images_insert_execution(
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "type": "featured"}},
                    "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-image-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["playlistId"], "PL123")

    def test_transport_normalizes_playlist_images_insert_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Required body metadata missing"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Required body metadata missing") as context:
            transport(
                self._playlist_images_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_images_insert_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image create denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image create denied") as context:
            transport(
                self._playlist_images_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_images_insert_upstream_create_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=409,
            msg="Conflict",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image create rejected"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image create rejected") as context:
            transport(
                self._playlist_images_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_builds_oauth_request_for_playlist_images_update_upload(self):
        execution = self._playlist_images_update_execution(
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "featured"}},
                "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistImages?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", request.headers["Content-type"])
        self.assertIn(b'"id": "playlist-image-123"', request.data)
        self.assertIn(b"playlist-image-bytes", request.data)

    def test_transport_normalizes_successful_playlist_images_update_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"id": "playlist-image-123", "kind": "youtube#playlistImage"})
        )

        result = transport(
            self._playlist_images_update_execution(
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123", "type": "featured"}},
                    "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-image-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["playlistId"], "PL123")

    def test_transport_normalizes_playlist_images_update_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Required body metadata missing"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Required body metadata missing") as context:
            transport(
                self._playlist_images_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_images_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image update denied") as context:
            transport(
                self._playlist_images_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_images_update_upstream_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages",
            code=409,
            msg="Conflict",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image update rejected"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image update rejected") as context:
            transport(
                self._playlist_images_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                        "media": {"mimeType": "image/png", "content": b"playlist-image-bytes"},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_builds_api_key_request_for_playlist_items_list_playlist_lookup(self):
        execution = self._playlist_items_execution(
            arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123", "maxResults": 10},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="key-123"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "GET")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistItems?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("playlistId=PL123", request.full_url)
        self.assertIn("pageToken=cursor-123", request.full_url)
        self.assertIn("maxResults=10", request.full_url)
        self.assertIn("key=key-123", request.full_url)
        self.assertNotIn("Authorization", request.headers)

    def test_transport_normalizes_successful_playlist_items_list_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"items": [{"id": "item-123", "kind": "youtube#playlistItem"}], "nextPageToken": "cursor-456"}
            )
        )

        result = transport(
            self._playlist_items_execution(
                arguments={"part": "snippet", "playlistId": "PL123", "pageToken": "cursor-123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="key-123"),
                ),
            )
        )

        self.assertEqual(result["items"][0]["id"], "item-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["selectorName"], "playlistId")
        self.assertEqual(result["selectorValue"], "PL123")

    def test_transport_normalizes_playlist_items_list_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist item request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist item request is invalid") as context:
            transport(
                self._playlist_items_execution(
                    arguments={"part": "snippet", "playlistId": "PL123"},
                    auth_context=AuthContext(
                        mode=AuthMode.API_KEY,
                        credentials=CredentialBundle(api_key="key-123"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_builds_oauth_post_request_for_playlist_items_insert(self):
        execution = self._playlist_items_insert_execution(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistItems?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("Authorization", request.headers)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"playlistId": "PL123"', request.data)
        self.assertIn(b'"videoId": "video-123"', request.data)

    def test_transport_normalizes_successful_playlist_items_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"id": "playlist-item-123", "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}}
            )
        )

        result = transport(
            self._playlist_items_insert_execution(
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-item-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")

    def test_transport_normalizes_playlist_items_insert_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist item create request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist item create request is invalid") as context:
            transport(
                self._playlist_items_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_items_insert_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist item create denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist item create denied") as context:
            transport(
                self._playlist_items_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_post_request_for_playlists_insert(self):
        execution = self._playlists_insert_execution(
            arguments={
                "part": "snippet",
                "body": {"snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "POST")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlists?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("Authorization", request.headers)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"title": "Layer 1 Playlist"', request.data)

    def test_transport_normalizes_successful_playlists_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}}
            )
        )

        result = transport(
            self._playlists_insert_execution(
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_transport_falls_back_to_request_title_for_playlists_insert_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"id": "playlist-123", "kind": "youtube#playlist"})
        )

        result = transport(
            self._playlists_insert_execution(
                arguments={
                    "part": "snippet",
                    "body": {"snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_transport_normalizes_playlists_insert_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist create request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist create request is invalid") as context:
            transport(
                self._playlists_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlists_insert_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist create denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist create denied") as context:
            transport(
                self._playlists_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlists_insert_upstream_create_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=409,
            msg="Conflict",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist create rejected by policy"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist create rejected by policy") as context:
            transport(
                self._playlists_insert_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_builds_oauth_put_request_for_playlists_update(self):
        execution = self._playlists_update_execution(
            arguments={
                "part": "snippet",
                "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "PUT")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlists?", request.full_url)
        self.assertIn("part=snippet", request.full_url)
        self.assertIn("Authorization", request.headers)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")
        self.assertEqual(request.headers["Content-type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "playlist-123"', request.data)
        self.assertIn(b'"title": "Layer 1 Playlist"', request.data)

    def test_transport_normalizes_successful_playlists_update_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}}
            )
        )

        result = transport(
            self._playlists_update_execution(
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["part"], "snippet")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_transport_falls_back_to_request_identity_and_title_for_playlists_update_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse({"kind": "youtube#playlist"})
        )

        result = transport(
            self._playlists_update_execution(
                arguments={
                    "part": "snippet",
                    "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["id"], "playlist-123")
        self.assertEqual(result["title"], "Layer 1 Playlist")

    def test_transport_normalizes_playlists_update_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist update request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist update request is invalid") as context:
            transport(
                self._playlists_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlists_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist update denied") as context:
            transport(
                self._playlists_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlists_update_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist target not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist target not found") as context:
            transport(
                self._playlists_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_transport_normalizes_playlists_update_upstream_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists",
            code=409,
            msg="Conflict",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist update rejected by policy"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist update rejected by policy") as context:
            transport(
                self._playlists_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "playlist-123", "snippet": {"title": "Layer 1 Playlist"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_builds_oauth_delete_request_for_playlists_delete(self):
        execution = self._playlists_delete_execution(
            arguments={"id": "playlist-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlists?", request.full_url)
        self.assertIn("id=playlist-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_playlists_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._playlists_delete_execution(
                arguments={"id": "playlist-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["playlistId"], "playlist-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_transport_normalizes_playlists_delete_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists?id=playlist-123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist delete request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist delete request is invalid") as context:
            transport(
                self._playlists_delete_execution(
                    arguments={"id": "playlist-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlists_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists?id=playlist-123",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist target not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist target not found") as context:
            transport(
                self._playlists_delete_execution(
                    arguments={"id": "playlist-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_transport_normalizes_playlists_delete_upstream_failures(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlists?id=playlist-123",
            code=409,
            msg="Conflict",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist delete rejected by policy"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist delete rejected by policy") as context:
            transport(
                self._playlists_delete_execution(
                    arguments={"id": "playlist-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "upstream_service")

    def test_transport_normalizes_channel_banners_invalid_upload_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelBanners/insert",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"mediaBodyRequired"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "mediaBodyRequired") as context:
            transport(
                self._channel_banners_insert_execution(
                    arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_channel_banners_target_channel_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channelBanners/insert",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel banner target not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel banner target not found") as context:
            transport(
                self._channel_banners_insert_execution(
                    arguments={"media": {"mimeType": "image/png", "content": b"banner-bytes"}},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "target_channel")

    def test_transport_normalizes_channels_update_invalid_write_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channels",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Read-only field specified in channel update"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Read-only field specified in channel update") as context:
            transport(
                self._channels_update_execution(
                    arguments={
                        "part": "brandingSettings",
                        "body": {
                            "id": "UC123",
                            "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                        },
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_channels_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/channels",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Channel update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Channel update denied") as context:
            transport(
                self._channels_update_execution(
                    arguments={
                        "part": "brandingSettings",
                        "body": {
                            "id": "UC123",
                            "brandingSettings": {"image": {"bannerExternalUrl": "https://yt.example/banner"}},
                        },
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_comments_update_invalid_write_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Read-only field specified in comment update"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Read-only field specified in comment update") as context:
            transport(
                self._comments_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comments_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Comment update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Comment update denied") as context:
            transport(
                self._comments_update_execution(
                    arguments={
                        "part": "snippet",
                        "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_items_update_invalid_write_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Read-only field specified in playlist item update"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Read-only field specified in playlist item update") as context:
            transport(
                self._playlist_items_update_execution(
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
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_items_update_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist item update denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist item update denied") as context:
            transport(
                self._playlist_items_update_execution(
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
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_items_update_missing_target_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist item target not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist item target not found") as context:
            transport(
                self._playlist_items_update_execution(
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
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_transport_returns_comments_set_moderation_status_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._comments_set_moderation_status_execution(
                arguments={
                    "id": ["comment-123", "comment-456"],
                    "moderationStatus": "rejected",
                    "banAuthor": True,
                    "onBehalfOfContentOwner": "owner-123",
                },
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["commentIds"], ("comment-123", "comment-456"))
        self.assertTrue(result["isModerated"])
        self.assertEqual(result["moderationStatus"], "rejected")
        self.assertTrue(result["authorBanApplied"])
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_transport_normalizes_comments_set_moderation_status_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments/setModerationStatus",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"moderationStatus is required"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "moderationStatus is required") as context:
            transport(
                self._comments_set_moderation_status_execution(
                    arguments={
                        "id": ["comment-123"],
                        "moderationStatus": "rejected",
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comments_set_moderation_status_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments/setModerationStatus",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Comment moderation denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Comment moderation denied") as context:
            transport(
                self._comments_set_moderation_status_execution(
                    arguments={
                        "id": ["comment-123"],
                        "moderationStatus": "rejected",
                    },
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_builds_oauth_delete_request_for_comments_delete(self):
        execution = self._comments_delete_execution(
            arguments={
                "id": "comment-123",
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/comments?", request.full_url)
        self.assertIn("id=comment-123", request.full_url)
        self.assertIn("onBehalfOfContentOwner=owner-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_comments_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._comments_delete_execution(
                arguments={"id": "comment-123", "onBehalfOfContentOwner": "owner-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["commentId"], "comment-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_transport_normalizes_comments_delete_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments?id=comment-123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"comment delete request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "comment delete request is invalid") as context:
            transport(
                self._comments_delete_execution(
                    arguments={"id": "comment-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_comments_delete_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments?id=comment-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Comment delete denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Comment delete denied") as context:
            transport(
                self._comments_delete_execution(
                    arguments={"id": "comment-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_comments_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/comments?id=comment-123",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Comment not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Comment not found") as context:
            transport(
                self._comments_delete_execution(
                    arguments={"id": "comment-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_builds_oauth_delete_request_for_playlist_images_delete(self):
        execution = self._playlist_images_delete_execution(
            arguments={"id": "playlist-image-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistImages?", request.full_url)
        self.assertIn("id=playlist-image-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_playlist_images_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._playlist_images_delete_execution(
                arguments={"id": "playlist-image-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["playlistImageId"], "playlist-image-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_transport_normalizes_playlist_images_delete_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages?id=playlist-image-123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist image delete request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist image delete request is invalid") as context:
            transport(
                self._playlist_images_delete_execution(
                    arguments={"id": "playlist-image-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_images_delete_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages?id=playlist-image-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image delete denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image delete denied") as context:
            transport(
                self._playlist_images_delete_execution(
                    arguments={"id": "playlist-image-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_images_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistImages?id=playlist-image-123",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist image not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist image not found") as context:
            transport(
                self._playlist_images_delete_execution(
                    arguments={"id": "playlist-image-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_builds_oauth_delete_request_for_playlist_items_delete(self):
        execution = self._playlist_items_delete_execution(
            arguments={"id": "playlist-item-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        request = build_youtube_data_api_request(execution)

        self.assertEqual(request.method, "DELETE")
        self.assertIn("https://www.googleapis.com/youtube/v3/playlistItems?", request.full_url)
        self.assertIn("id=playlist-item-123", request.full_url)
        self.assertEqual(request.headers["Authorization"], "Bearer oauth-token")

    def test_transport_normalizes_successful_playlist_items_delete_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse("")
        )

        result = transport(
            self._playlist_items_delete_execution(
                arguments={"id": "playlist-item-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )
        )

        self.assertEqual(result["playlistItemId"], "playlist-item-123")
        self.assertTrue(result["isDeleted"])
        self.assertEqual(result["upstreamBodyState"], "empty")

    def test_transport_normalizes_playlist_items_delete_invalid_request_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems?id=playlist-item-123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"playlist item delete request is invalid"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "playlist item delete request is invalid") as context:
            transport(
                self._playlist_items_delete_execution(
                    arguments={"id": "playlist-item-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "invalid_request")

    def test_transport_normalizes_playlist_items_delete_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems?id=playlist-item-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist item delete denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist item delete denied") as context:
            transport(
                self._playlist_items_delete_execution(
                    arguments={"id": "playlist-item-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_playlist_items_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/playlistItems?id=playlist-item-123",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Playlist item not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Playlist item not found") as context:
            transport(
                self._playlist_items_delete_execution(
                    arguments={"id": "playlist-item-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_transport_parses_successful_youtube_payload(self):
        transport = build_youtube_data_api_transport(
            opener=lambda request, timeout: _FakeHTTPResponse(
                {"kind": "youtube#activityListResponse", "items": [{"id": "activity-1"}]}
            )
        )

        result = transport(
            self._execution(
                arguments={"part": "snippet", "channelId": "UC123"},
                auth_context=AuthContext(
                    mode=AuthMode.API_KEY,
                    credentials=CredentialBundle(api_key="yt-key"),
                ),
            )
        )

        self.assertEqual(result["items"][0]["id"], "activity-1")

    def test_transport_normalizes_http_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/activities",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Access forbidden"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Access forbidden"):
            transport(
                self._execution(
                    arguments={"part": "snippet", "mine": True},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

    def test_transport_normalizes_captions_download_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/captions/caption-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Caption access denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Caption access denied") as context:
            transport(
                self._captions_download_execution(
                    arguments={"id": "caption-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_captions_download_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/captions/caption-404",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Caption track not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Caption track not found") as context:
            transport(
                self._captions_download_execution(
                    arguments={"id": "caption-404"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_transport_normalizes_captions_delete_auth_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/captions/caption-123",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Caption delete denied"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Caption delete denied") as context:
            transport(
                self._captions_delete_execution(
                    arguments={"id": "caption-123"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "auth")

    def test_transport_normalizes_captions_delete_not_found_errors(self):
        error = HTTPError(
            url="https://www.googleapis.com/youtube/v3/captions/caption-404",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":{"message":"Caption track not found"}}'),
        )
        transport = build_youtube_data_api_transport(opener=lambda request, timeout: (_ for _ in ()).throw(error))

        with self.assertRaisesRegex(RuntimeError, "Caption track not found") as context:
            transport(
                self._captions_delete_execution(
                    arguments={"id": "caption-404"},
                    auth_context=AuthContext(
                        mode=AuthMode.OAUTH_REQUIRED,
                        credentials=CredentialBundle(oauth_token="oauth-token"),
                    ),
                )
            )

        self.assertEqual(context.exception.category, "not_found")

    def test_executor_can_run_live_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=12.5)
        result = build_activities_list_wrapper().call(
            executor,
            arguments={"part": "snippet", "home": True},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertIn("home=true", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["timeout"], 12.5)

    def test_executor_can_run_live_captions_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=9.0)
        result = build_captions_list_wrapper().call(
            executor,
            arguments={"part": "snippet", "videoId": "video-123"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertIn("videoId=video-123", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["timeout"], 9.0)

    def test_executor_can_run_live_channels_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=8.0)
        result = build_channels_list_wrapper().call(
            executor,
            arguments={"part": "snippet", "forHandle": "@channel"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertIn("forHandle=%40channel", captured["url"])
        self.assertIsNone(captured["authorization"])
        self.assertEqual(captured["timeout"], 8.0)

    def test_executor_can_run_live_comments_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=7.5)
        result = build_comments_list_wrapper().call(
            executor,
            arguments={"part": "snippet", "parentId": "comment-123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertIn("parentId=comment-123", captured["url"])
        self.assertIsNone(captured["authorization"])
        self.assertEqual(captured["timeout"], 7.5)

    def test_executor_can_run_live_comment_threads_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=8.5)
        result = build_comment_threads_list_wrapper().call(
            executor,
            arguments={"part": "snippet", "allThreadsRelatedToChannelId": "UC123"},
            auth_context=AuthContext(
                mode=AuthMode.API_KEY,
                credentials=CredentialBundle(api_key="yt-key"),
            ),
        )

        self.assertEqual(result["items"], [])
        self.assertIn("allThreadsRelatedToChannelId=UC123", captured["url"])
        self.assertIsNone(captured["authorization"])
        self.assertEqual(captured["timeout"], 8.5)

    def test_executor_rejects_comment_threads_transport_shape_with_oauth_mode(self):
        captured = {"called": False}

        def opener(request, timeout):
            captured["called"] = True
            return _FakeHTTPResponse({"items": []})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=8.5)

        with self.assertRaisesRegex(ValueError, "videoId requires api_key auth"):
            build_comment_threads_list_wrapper().call(
                executor,
                arguments={"part": "snippet", "videoId": "video-123"},
                auth_context=AuthContext(
                    mode=AuthMode.OAUTH_REQUIRED,
                    credentials=CredentialBundle(oauth_token="oauth-token"),
                ),
            )

        self.assertFalse(captured["called"])

    def test_executor_can_run_live_captions_insert_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse({"id": "caption-123", "kind": "youtube#caption"})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=11.0)
        result = build_captions_insert_wrapper().call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"videoId": "video-123", "language": "en"}},
                "media": {"mimeType": "text/plain", "content": "caption payload"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "caption-123")
        self.assertEqual(captured["method"], "POST")
        self.assertIn("part=snippet", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", captured["content_type"])
        self.assertIn(b"caption payload", captured["data"])
        self.assertEqual(captured["timeout"], 11.0)

    def test_executor_can_run_live_comments_insert_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse(
                {"id": "comment-123", "snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}}
            )

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=11.5)
        result = build_comments_insert_wrapper().call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"snippet": {"parentId": "comment-123", "textOriginal": "Reply text"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "comment-123")
        self.assertEqual(captured["method"], "POST")
        self.assertIn("part=snippet", captured["url"])
        self.assertIn("onBehalfOfContentOwner=owner-123", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["content_type"], "application/json; charset=utf-8")
        self.assertIn(b'"parentId": "comment-123"', captured["data"])
        self.assertEqual(captured["timeout"], 11.5)

    def test_executor_can_run_live_comment_threads_insert_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse(
                {
                    "id": "thread-123",
                    "snippet": {
                        "videoId": "video-123",
                        "topLevelComment": {"id": "comment-123", "snippet": {"textOriginal": "Top-level text"}},
                    },
                }
            )

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=12.0)
        result = build_comment_threads_insert_wrapper().call(
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
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "thread-123")
        self.assertEqual(captured["method"], "POST")
        self.assertIn("part=snippet", captured["url"])
        self.assertIn("onBehalfOfContentOwner=owner-123", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["content_type"], "application/json; charset=utf-8")
        self.assertIn(b'"videoId": "video-123"', captured["data"])
        self.assertEqual(captured["timeout"], 12.0)

    def test_executor_can_run_live_comments_update_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse(
                {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}, "kind": "youtube#comment"}
            )

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=10.5)
        result = build_comments_update_wrapper().call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment"}},
                "onBehalfOfContentOwner": "owner-123",
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "comment-123")
        self.assertEqual(result["delegatedOwner"], "owner-123")
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("part=snippet", captured["url"])
        self.assertIn("onBehalfOfContentOwner=owner-123", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")

    def test_executor_can_run_live_playlist_items_update_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse(
                {
                    "id": "playlist-item-123",
                    "snippet": {
                        "playlistId": "PL123",
                        "resourceId": {"videoId": "video-123"},
                    },
                    "kind": "youtube#playlistItem",
                }
            )

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=10.5)
        result = build_playlist_items_update_wrapper().call(
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
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "playlist-item-123")
        self.assertEqual(result["playlistId"], "PL123")
        self.assertEqual(result["videoId"], "video-123")
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("part=snippet", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["content_type"], "application/json; charset=utf-8")
        self.assertIn(b'"id": "playlist-item-123"', captured["data"])
        self.assertIn(b'"playlistId": "PL123"', captured["data"])
        self.assertIn(b'"videoId": "video-123"', captured["data"])
        self.assertEqual(captured["timeout"], 10.5)

    def test_executor_can_run_live_captions_update_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            captured["content_type"] = request.headers.get("Content-type")
            captured["data"] = request.data
            return _FakeHTTPResponse({"id": "caption-123", "kind": "youtube#caption"})

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=7.5)
        result = build_captions_update_wrapper().call(
            executor,
            arguments={
                "part": "snippet",
                "body": {"id": "caption-123", "snippet": {"language": "en"}},
                "media": {"mimeType": "text/plain", "content": "updated caption payload"},
            },
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["id"], "caption-123")
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("part=snippet", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertIn("multipart/related", captured["content_type"])
        self.assertIn(b"updated caption payload", captured["data"])
        self.assertEqual(captured["timeout"], 7.5)

    def test_executor_can_run_live_captions_download_transport_shape(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers.get("Authorization")
            captured["timeout"] = timeout
            captured["method"] = request.method
            return _FakeHTTPResponse("caption line 1")

        executor = build_youtube_data_api_executor(opener=opener, timeout_seconds=6.0)
        result = build_captions_download_wrapper().call(
            executor,
            arguments={"id": "caption-123", "tfmt": "srt", "tlang": "es"},
            auth_context=AuthContext(
                mode=AuthMode.OAUTH_REQUIRED,
                credentials=CredentialBundle(oauth_token="oauth-token"),
            ),
        )

        self.assertEqual(result["captionId"], "caption-123")
        self.assertEqual(result["content"], "caption line 1")
        self.assertEqual(result["contentFormat"], "srt")
        self.assertEqual(result["contentLanguage"], "es")
        self.assertEqual(captured["method"], "GET")
        self.assertIn("/youtube/v3/captions/caption-123?", captured["url"])
        self.assertEqual(captured["authorization"], "Bearer oauth-token")
        self.assertEqual(captured["timeout"], 6.0)


if __name__ == "__main__":
    unittest.main()
