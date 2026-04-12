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
    build_channel_sections_list_wrapper,
    build_channels_list_wrapper,
    build_channels_update_wrapper,
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
