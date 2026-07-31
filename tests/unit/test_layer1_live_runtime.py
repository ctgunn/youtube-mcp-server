import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.config import load_youtube_live_runtime_settings
from mcp_server.integrations.auth import AuthMode
from mcp_server.integrations.runtime import (
    LiveRuntimeConfigurationError,
    build_configured_youtube_runtime,
)
from mcp_server.integrations.resources.activities import build_activities_list_wrapper


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, object]):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class Layer1LiveRuntimeTests(unittest.TestCase):
    def test_configured_runtime_uses_concrete_transport_with_existing_defaults(self):
        captured = []
        settings = load_youtube_live_runtime_settings({"YOUTUBE_API_KEY": "api-key-for-test"})
        runtime = build_configured_youtube_runtime(
            settings,
            opener=lambda request, timeout: captured.append((request, timeout)) or _FakeHTTPResponse({"items": []}),
        )
        wrapper = build_activities_list_wrapper()

        result = wrapper.call(
            runtime.executor,
            arguments={"part": "snippet", "channelId": "UC123"},
            auth_context=runtime.auth_context_for(AuthMode.API_KEY),
        )

        self.assertEqual(result, {"items": []})
        self.assertEqual(runtime.timeout_seconds, 10.0)
        self.assertEqual(runtime.retry_policy.max_attempts, 3)
        self.assertEqual(len(captured), 1)
        self.assertIn("key=api-key-for-test", captured[0][0].full_url)
        self.assertEqual(captured[0][1], 10.0)

    def test_runtime_rejects_missing_required_credential_without_disclosing_values(self):
        settings = load_youtube_live_runtime_settings({"YOUTUBE_API_KEY": "api-key-for-test"})
        runtime = build_configured_youtube_runtime(settings)

        with self.assertRaises(LiveRuntimeConfigurationError) as exc_info:
            runtime.auth_context_for(AuthMode.OAUTH_REQUIRED)

        self.assertEqual(exc_info.exception.category, "authorization_failed")
        self.assertEqual(exc_info.exception.details, {"credential": "YOUTUBE_OAUTH_TOKEN"})
        self.assertNotIn("api-key-for-test", str(exc_info.exception))

    def test_runtime_rejects_an_unresolved_conditional_auth_mode(self):
        """Require handlers to resolve conditional authorization before execution."""
        runtime = build_configured_youtube_runtime(
            load_youtube_live_runtime_settings(
                {"YOUTUBE_API_KEY": "api-key-for-test", "YOUTUBE_OAUTH_TOKEN": "oauth-token-for-test"}
            )
        )

        with self.assertRaises(LiveRuntimeConfigurationError) as exc_info:
            runtime.auth_context_for(AuthMode.CONDITIONAL)

        self.assertEqual(exc_info.exception.category, "invalid_request")
        self.assertEqual(exc_info.exception.details, {"authMode": "conditional"})
        self.assertNotIn("api-key-for-test", str(exc_info.exception))
        self.assertNotIn("oauth-token-for-test", str(exc_info.exception))

    def test_runtime_factory_is_available_from_integration_compatibility_exports(self):
        from mcp_server.integrations import build_configured_youtube_runtime as exported_factory

        self.assertIs(exported_factory, build_configured_youtube_runtime)


if __name__ == "__main__":
    unittest.main()
