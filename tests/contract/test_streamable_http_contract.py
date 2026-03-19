import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import build_asgi_app, execute_hosted_request
from mcp_server.transport.session_store import reset_memory_session_store_registry
from tests.contract.conftest import stream_headers
from tests.unit.conftest import parse_sse_payload


class StreamableHTTPContractTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(env={"MCP_ENVIRONMENT": "dev"})

    def tearDown(self):
        reset_memory_session_store_registry()

    def _initialize(self):
        result = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers()},
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-contract-init",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(result.status, 200)
        return result

    def test_initialize_issues_session_header(self):
        result = self._initialize()
        self.assertEqual(result.headers["Content-Type"], "application/json")
        self.assertEqual(result.payload["jsonrpc"], "2.0")
        self.assertIn("MCP-Session-Id", result.headers)
        self.assertEqual(result.headers["MCP-Protocol-Version"], "2025-11-25")

    def test_tools_call_can_return_sse(self):
        init = self._initialize()
        result = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id=init.headers["MCP-Session-Id"])},
            body=b'{"jsonrpc":"2.0","id":"req-contract-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}',
        )
        self.assertEqual(result.status, 200)
        self.assertEqual(result.headers["Content-Type"], "text/event-stream")
        events = parse_sse_payload(result.body)
        self.assertEqual(len(events), 2)
        self.assertIn('"result"', events[1]["data"])
        self.assertIn('"structuredContent"', events[1]["data"])

    def test_get_stream_requires_valid_session(self):
        missing = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers=stream_headers(include_json=False),
        )
        self.assertEqual(missing.status, 400)

        init = self._initialize()
        valid = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers=stream_headers(session_id=init.headers["MCP-Session-Id"], include_json=False),
        )
        self.assertEqual(valid.status, 200)
        self.assertEqual(valid.headers["Content-Type"], "text/event-stream")

    def test_migrated_runtime_exposes_asgi_application_with_transport(self):
        hosted_app = build_asgi_app(validate_startup=False)
        transport = getattr(hosted_app, "transport", getattr(getattr(hosted_app, "state", None), "transport", None))
        self.assertIsNotNone(transport)
        self.assertEqual(transport.runtime_settings.server_implementation, "uvicorn")
        self.assertEqual(transport.runtime_settings.app_module, "mcp_server.cloud_run_entrypoint:app")

    def test_invalid_protocol_version_and_origin_fail(self):
        invalid_version = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                **stream_headers(protocol_version="1999-01-01"),
            },
            body=b'{"jsonrpc":"2.0","id":"req-invalid-version","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        self.assertEqual(invalid_version.status, 400)

        invalid_origin = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Host": "localhost:8080",
                **stream_headers(origin="https://evil.example"),
            },
            body=b'{"jsonrpc":"2.0","id":"req-invalid-origin","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        self.assertEqual(invalid_origin.status, 403)

    def test_follow_up_post_can_continue_on_second_instance_with_shared_store(self):
        shared_env = {
            "MCP_ENVIRONMENT": "dev",
            "MCP_SESSION_BACKEND": "memory",
            "MCP_SESSION_STORE_URL": "memory://contract-shared",
            "MCP_SESSION_DURABILITY_REQUIRED": "true",
        }
        first = create_app(env=shared_env)
        second = create_app(env=shared_env)
        init = execute_hosted_request(
            first,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers()},
            body=b'{"jsonrpc":"2.0","id":"req-contract-init-shared","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        result = execute_hosted_request(
            second,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id=init.headers["MCP-Session-Id"])},
            body=b'{"jsonrpc":"2.0","id":"req-contract-list-shared","method":"tools/list","params":{}}',
        )
        self.assertEqual(result.status, 200)
        self.assertIn("tools", result.payload["result"])

    def test_replay_unavailable_uses_distinct_failure(self):
        shared_env = {
            "MCP_ENVIRONMENT": "dev",
            "MCP_SESSION_BACKEND": "memory",
            "MCP_SESSION_STORE_URL": "memory://contract-replay",
            "MCP_SESSION_DURABILITY_REQUIRED": "true",
        }
        app = create_app(env=shared_env)
        init = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers()},
            body=b'{"jsonrpc":"2.0","id":"req-contract-init-replay","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        result = execute_hosted_request(
            app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id=init.headers["MCP-Session-Id"])},
            body=b'{"jsonrpc":"2.0","id":"req-contract-call-replay","method":"tools/call","params":{"name":"server_ping","arguments":{}}}',
        )
        first_event_id = parse_sse_payload(result.body)[0]["id"]
        for stream_id in app.stream_manager.streams:
            record = app.stream_manager._store.load_stream(stream_id)
            record["replay_window_ends_at"] = "2000-01-01T00:00:00+00:00"
            app.stream_manager._store.save_stream(stream_id, record)
        replay = execute_hosted_request(
            app,
            method="GET",
            path="/mcp",
            headers={**stream_headers(session_id=init.headers["MCP-Session-Id"], include_json=False), "Last-Event-ID": first_event_id},
        )
        self.assertEqual(replay.status, 409)
        self.assertEqual(replay.payload["error"]["data"]["category"], "replay_unavailable")


if __name__ == "__main__":
    unittest.main()
