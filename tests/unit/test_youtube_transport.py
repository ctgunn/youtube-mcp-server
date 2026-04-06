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
from mcp_server.integrations.wrappers import build_activities_list_wrapper


class _FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

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


if __name__ == "__main__":
    unittest.main()
