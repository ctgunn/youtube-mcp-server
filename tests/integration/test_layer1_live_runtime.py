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
