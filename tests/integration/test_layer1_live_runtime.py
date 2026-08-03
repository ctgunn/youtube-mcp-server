import json
import os
import sys
import unittest
from io import BytesIO
from urllib.error import HTTPError

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.config import load_youtube_live_runtime_settings
from mcp_server.integrations.runtime import build_configured_youtube_runtime
from mcp_server.tools.dispatcher import InMemoryToolDispatcher
from mcp_server.tools.youtube_common.activities import ActivitiesListToolError


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, object] | str):
        self._payload = json.dumps(payload).encode("utf-8") if isinstance(payload, dict) else payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class Layer1LiveRuntimeIntegrationTests(unittest.TestCase):
    def test_configured_runtime_is_injected_into_every_catalog_membership_and_playlist_descriptor(self):
        """Inject configured live dependencies into every YT-159 descriptor.

        :return: ``None`` after checking the configured dispatcher boundary.
        """
        runtime = build_configured_youtube_runtime(
            load_youtube_live_runtime_settings(
                {
                    "YOUTUBE_API_KEY": "configured-api-key",
                    "YOUTUBE_OAUTH_TOKEN": "configured-oauth-token",
                }
            )
        )
        dispatcher = InMemoryToolDispatcher(youtube_runtime=runtime)
        scoped_tools = (
            "guideCategories_list",
            "i18nLanguages_list",
            "i18nRegions_list",
            "members_list",
            "membershipsLevels_list",
            "playlistImages_list",
            "playlistImages_insert",
            "playlistImages_update",
            "playlistImages_delete",
            "playlistItems_list",
            "playlistItems_insert",
            "playlistItems_update",
            "playlistItems_delete",
            "playlists_list",
            "playlists_insert",
            "playlists_update",
            "playlists_delete",
        )

        for tool_name in scoped_tools:
            handler = dispatcher._tools[tool_name.lower()]["handler"]
            closure_values = tuple(cell.cell_contents for cell in handler.__closure__ or ())
            self.assertIn(runtime.executor, closure_values, tool_name)
            self.assertNotIn("local-api-key", str(closure_values), tool_name)
            self.assertNotIn("local-oauth-token", str(closure_values), tool_name)

    def test_configured_runtime_is_injected_into_every_channel_and_community_descriptor(self):
        """Inject one configured executor and only configured credentials into every scoped tool.

        :return: ``None`` after verifying the dispatcher construction boundary.
        """
        runtime = build_configured_youtube_runtime(
            load_youtube_live_runtime_settings(
                {
                    "YOUTUBE_API_KEY": "configured-api-key",
                    "YOUTUBE_OAUTH_TOKEN": "configured-oauth-token",
                }
            )
        )
        dispatcher = InMemoryToolDispatcher(youtube_runtime=runtime)
        scoped_tools = (
            "activities_list",
            "captions_list",
            "captions_insert",
            "captions_update",
            "captions_download",
            "captions_delete",
            "channelBanners_insert",
            "channels_list",
            "channels_update",
            "channelSections_list",
            "channelSections_insert",
            "channelSections_update",
            "channelSections_delete",
            "comments_list",
            "comments_insert",
            "comments_update",
            "comments_setModerationStatus",
            "comments_delete",
            "commentThreads_list",
            "commentThreads_insert",
        )

        for tool_name in scoped_tools:
            handler = dispatcher._tools[tool_name.lower()]["handler"]
            closure_values = tuple(cell.cell_contents for cell in handler.__closure__ or ())
            self.assertIn(runtime.executor, closure_values, tool_name)
            self.assertNotIn("public-channel-access", closure_values, tool_name)
            self.assertNotIn("eligible-caption-access", closure_values, tool_name)
            self.assertNotIn("authorized-comment-write", closure_values, tool_name)

    def test_configured_app_routes_activities_through_live_transport(self):
        captured = []
        transport = create_app(
            env={"MCP_ENVIRONMENT": "dev", "YOUTUBE_API_KEY": "configured-api-key"},
            youtube_opener=lambda request, timeout: captured.append((request, timeout))
            or _FakeHTTPResponse({"items": [{"id": "activity-123"}]}),
        )

        result = transport.dispatcher.call_tool(
            "activities_list",
            {"part": "snippet", "channelId": "UC123"},
        )

        self.assertEqual(result["items"], [{"id": "activity-123"}])
        self.assertEqual(len(captured), 1)
        self.assertIn("key=configured-api-key", captured[0][0].full_url)
        self.assertNotIn("Representative", str(result))

    def test_configured_app_routes_every_catalog_membership_and_playlist_operation_through_live_transport(self):
        """Route every configured YT-159 public tool through the live executor.

        :return: ``None`` after checking request paths, credential placement,
            methods, and distinctive controlled responses for all operations.
        """
        flows = (
            ("guideCategories_list", {"part": "snippet", "regionCode": "US"}, "guideCategories", "api_key", "GET"),
            ("i18nLanguages_list", {"part": "snippet"}, "i18nLanguages", "api_key", "GET"),
            ("i18nRegions_list", {"part": "snippet"}, "i18nRegions", "api_key", "GET"),
            ("members_list", {"part": "snippet", "mode": "updates"}, "members", "oauth", "GET"),
            ("membershipsLevels_list", {"part": "snippet"}, "membershipsLevels", "oauth", "GET"),
            ("playlistImages_list", {"part": "snippet", "playlistId": "PL123"}, "playlistImages", "oauth", "GET"),
            (
                "playlistImages_insert",
                {
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123"}},
                    "media": {"mimeType": "image/jpeg", "content": "image-content"},
                },
                "playlistImages",
                "oauth",
                "POST",
            ),
            (
                "playlistImages_update",
                {
                    "part": "snippet",
                    "body": {"id": "playlist-image-123", "snippet": {"playlistId": "PL123"}},
                    "media": {"mimeType": "image/jpeg", "content": "image-content"},
                },
                "playlistImages",
                "oauth",
                "PUT",
            ),
            ("playlistImages_delete", {"id": "playlist-image-123"}, "playlistImages", "oauth", "DELETE"),
            ("playlistItems_list", {"part": "snippet", "playlistId": "PL123"}, "playlistItems", "api_key", "GET"),
            (
                "playlistItems_insert",
                {
                    "part": "snippet",
                    "body": {"snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}}},
                },
                "playlistItems",
                "oauth",
                "POST",
            ),
            (
                "playlistItems_update",
                {
                    "part": "snippet",
                    "body": {
                        "id": "playlist-item-123",
                        "snippet": {"playlistId": "PL123", "resourceId": {"videoId": "video-123"}},
                    },
                },
                "playlistItems",
                "oauth",
                "PUT",
            ),
            ("playlistItems_delete", {"id": "playlist-item-123"}, "playlistItems", "oauth", "DELETE"),
            ("playlists_list", {"part": "snippet", "channelId": "UC123"}, "playlists", "api_key", "GET"),
            (
                "playlists_insert",
                {"part": "snippet", "body": {"snippet": {"title": "Live playlist"}}},
                "playlists",
                "oauth",
                "POST",
            ),
            (
                "playlists_update",
                {"part": "snippet", "body": {"id": "PL123", "snippet": {"title": "Updated live playlist"}}},
                "playlists",
                "oauth",
                "PUT",
            ),
            ("playlists_delete", {"id": "PL123"}, "playlists", "oauth", "DELETE"),
        )

        for tool_name, arguments, expected_path, credential_mode, expected_method in flows:
            captured = []
            transport = create_app(
                env={
                    "MCP_ENVIRONMENT": "dev",
                    "YOUTUBE_API_KEY": "configured-api-key",
                    "YOUTUBE_OAUTH_TOKEN": "configured-oauth-token",
                },
                youtube_opener=lambda request, timeout: captured.append((request, timeout))
                or _FakeHTTPResponse({"items": [{"id": f"live-{tool_name}"}]}),
            )

            result = transport.dispatcher.call_tool(tool_name, arguments)

            self.assertEqual(len(captured), 1, tool_name)
            request = captured[0][0]
            self.assertIn(f"/youtube/v3/{expected_path}", request.full_url, tool_name)
            self.assertEqual(request.method, expected_method, tool_name)
            if credential_mode == "api_key":
                self.assertIn("key=configured-api-key", request.full_url, tool_name)
                self.assertIsNone(request.headers.get("Authorization"), tool_name)
            else:
                self.assertEqual(request.headers.get("Authorization"), "Bearer configured-oauth-token", tool_name)
                self.assertNotIn("key=", request.full_url, tool_name)
            if expected_method == "DELETE":
                self.assertTrue(result["deleted"], tool_name)
                self.assertTrue(result["acknowledged"], tool_name)
            else:
                self.assertIn(f"live-{tool_name}", str(result), tool_name)
            self.assertNotIn("representative", str(result).lower(), tool_name)

    def test_configured_public_family_flows_normalize_upstream_failures_without_fallback(self):
        """Map a live upstream failure safely for one public tool per family.

        :return: ``None`` after verifying no family substitutes representative
            data or leaks the configured credential in a public failure.
        """
        flows = (
            ("guideCategories_list", {"part": "snippet", "regionCode": "US"}),
            ("i18nLanguages_list", {"part": "snippet"}),
            ("members_list", {"part": "snippet", "mode": "updates"}),
            ("membershipsLevels_list", {"part": "snippet"}),
            ("playlistImages_list", {"part": "snippet", "playlistId": "PL123"}),
            ("playlistItems_list", {"part": "snippet", "playlistId": "PL123"}),
            ("playlists_list", {"part": "snippet", "channelId": "UC123"}),
        )

        for tool_name, arguments in flows:
            captured = []
            transport = create_app(
                env={
                    "MCP_ENVIRONMENT": "dev",
                    "YOUTUBE_API_KEY": "configured-api-key",
                    "YOUTUBE_OAUTH_TOKEN": "configured-oauth-token",
                },
                youtube_opener=lambda request, timeout: captured.append((request, timeout))
                or (_ for _ in ()).throw(
                    HTTPError(
                        url=request.full_url,
                        code=403,
                        msg="Forbidden",
                        hdrs=None,
                        fp=BytesIO(b'{"error":{"message":"configured-api-key must remain secret"}}'),
                    )
                ),
            )

            with self.assertRaises(ValueError) as exc_info:
                transport.dispatcher.call_tool(tool_name, arguments)

            self.assertTrue(exc_info.exception.category, tool_name)
            self.assertGreaterEqual(len(captured), 1, tool_name)
            self.assertNotIn("representative", str(exc_info.exception).lower(), tool_name)
            self.assertNotIn("configured-api-key", str(exc_info.exception), tool_name)
            self.assertNotIn("configured-oauth-token", str(exc_info.exception), tool_name)

    def test_missing_configured_catalog_and_membership_credentials_fail_per_call(self):
        """Reject missing configured credentials after dispatcher construction.

        :return: ``None`` after verifying safe per-call failures and no network use.
        """
        flows = (
            ("guideCategories_list", {"part": "snippet", "regionCode": "US"}),
            ("i18nLanguages_list", {"part": "snippet"}),
            ("i18nRegions_list", {"part": "snippet"}),
            ("members_list", {"part": "snippet", "mode": "updates"}),
            ("membershipsLevels_list", {"part": "snippet"}),
            ("playlistImages_list", {"part": "snippet", "playlistId": "PL123"}),
            ("playlistItems_list", {"part": "snippet", "playlistId": "PL123"}),
            ("playlists_list", {"part": "snippet", "mine": True}),
        )

        for tool_name, arguments in flows:
            captured = []
            transport = create_app(
                env={"MCP_ENVIRONMENT": "dev"},
                youtube_opener=lambda request, timeout: captured.append((request, timeout)),
            )

            with self.assertRaises(ValueError) as exc_info:
                transport.dispatcher.call_tool(tool_name, arguments)

            self.assertEqual(exc_info.exception.category, "authentication_failed", tool_name)
            self.assertEqual(captured, [], tool_name)
            self.assertNotIn("representative", str(exc_info.exception).lower(), tool_name)

    def test_missing_configured_credential_returns_safe_failure_without_sample_data(self):
        transport = create_app(env={"MCP_ENVIRONMENT": "dev"})

        with self.assertRaises(ActivitiesListToolError) as exc_info:
            transport.dispatcher.call_tool(
                "activities_list",
                {"part": "snippet", "channelId": "UC123"},
            )

        self.assertEqual(exc_info.exception.category, "authentication_failed")
        self.assertEqual(exc_info.exception.details, {"selector": "channelId"})
        self.assertNotIn("items", str(exc_info.exception))

    def test_missing_oauth_credential_returns_safe_failure_without_sample_data(self):
        """Reject an OAuth-required selector before it can return local data."""
        transport = create_app(env={"MCP_ENVIRONMENT": "dev", "YOUTUBE_API_KEY": "configured-api-key"})

        with self.assertRaises(ActivitiesListToolError) as exc_info:
            transport.dispatcher.call_tool(
                "activities_list",
                {"part": "snippet", "mine": True},
            )

        self.assertEqual(exc_info.exception.category, "authentication_failed")
        self.assertEqual(exc_info.exception.details, {"selector": "mine"})
        self.assertNotIn("items", str(exc_info.exception))

    def test_live_failure_retries_and_redacts_configured_credential(self):
        calls = []

        def failing_opener(request, timeout):
            """Raise a controlled timeout without exposing request credentials.

            :param request: Outgoing request captured for retry counting.
            :param timeout: Configured upstream timeout.
            :raises TimeoutError: Always, to exercise terminal retry handling.
            """
            calls.append((request, timeout))
            raise TimeoutError("configured-api-key")

        transport = create_app(
            env={"MCP_ENVIRONMENT": "dev", "YOUTUBE_API_KEY": "configured-api-key"},
            youtube_opener=failing_opener,
        )

        with self.assertRaises(ActivitiesListToolError) as exc_info:
            transport.dispatcher.call_tool(
                "activities_list",
                {"part": "snippet", "channelId": "UC123"},
            )

        self.assertEqual(len(calls), 3)
        self.assertEqual(exc_info.exception.category, "endpoint_unavailable")
        self.assertNotIn("configured-api-key", str(exc_info.exception))
        self.assertNotIn("configured-api-key", str(exc_info.exception.details))
        self.assertNotIn("configured-api-key", str(transport.observability.logs))

    def test_live_authorization_and_malformed_response_failures_are_normalized(self):
        """Map controlled live failures without returning raw upstream diagnostics."""
        authorization_transport = create_app(
            env={"MCP_ENVIRONMENT": "dev", "YOUTUBE_API_KEY": "configured-api-key"},
            youtube_opener=lambda request, timeout: (_ for _ in ()).throw(
                HTTPError(
                    url=request.full_url,
                    code=403,
                    msg="Forbidden",
                    hdrs=None,
                    fp=BytesIO(b'{"error":{"message":"Bearer configured-api-key is invalid"}}'),
                )
            ),
        )
        malformed_transport = create_app(
            env={"MCP_ENVIRONMENT": "dev", "YOUTUBE_API_KEY": "configured-api-key"},
            youtube_opener=lambda request, timeout: _FakeHTTPResponse("[]"),
        )

        for transport, expected_category in (
            (authorization_transport, "authorization_failed"),
            (malformed_transport, "upstream_failure"),
        ):
            with self.assertRaises(ActivitiesListToolError) as exc_info:
                transport.dispatcher.call_tool(
                    "activities_list",
                    {"part": "snippet", "channelId": "UC123"},
                )
            self.assertEqual(exc_info.exception.category, expected_category)
            self.assertNotIn("configured-api-key", str(exc_info.exception))
            self.assertNotIn("configured-api-key", str(exc_info.exception.details))


if __name__ == "__main__":
    unittest.main()
