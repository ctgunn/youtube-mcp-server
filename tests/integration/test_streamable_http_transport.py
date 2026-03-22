import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request
from mcp_server.transport.session_store import reset_memory_session_store_registry
from tests.integration.conftest import parse_sse_payload, stream_headers


class StreamableHTTPTransportIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(env={"MCP_ENVIRONMENT": "dev"})

    def tearDown(self):
        reset_memory_session_store_registry()

    def _initialize_session(self) -> str:
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers()},
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "req-init-1",
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "client", "version": "1.0.0"}},
                }
            ).encode("utf-8"),
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        return response.headers["MCP-Session-Id"]

    def test_initialize_returns_json_and_session_header(self):
        session_id = self._initialize_session()
        self.assertTrue(session_id)

    def test_invalid_session_and_invalid_accept_are_rejected(self):
        invalid_session = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id="missing")},
            body=b'{"jsonrpc":"2.0","id":"req-tools","method":"tools/list","params":{}}',
        )
        self.assertEqual(invalid_session.status, 404)
        self.assertEqual(invalid_session.payload["error"]["code"], -32001)
        self.assertEqual(invalid_session.payload["error"]["data"]["category"], "session_not_found")

        invalid_accept = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            body=b'{"jsonrpc":"2.0","id":"req-tools","method":"tools/list","params":{}}',
        )
        self.assertEqual(invalid_accept.status, 400)
        self.assertEqual(invalid_accept.payload["error"]["code"], -32602)
        self.assertEqual(invalid_accept.payload["error"]["data"]["category"], "invalid_argument")

    def test_tools_call_streams_over_sse(self):
        session_id = self._initialize_session()
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id=session_id)},
            body=b'{"jsonrpc":"2.0","id":"req-call-1","method":"tools/call","params":{"name":"server_ping","arguments":{}}}',
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "text/event-stream")
        events = parse_sse_payload(response.body)
        self.assertEqual(len(events), 2)
        self.assertIn('"result"', events[1]["data"])

    def test_get_stream_replays_queued_server_events(self):
        session_id = self._initialize_session()
        self.app.queue_server_event(session_id, {"jsonrpc": "2.0", "method": "notifications/message", "params": {"text": "hi"}})

        first = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers=stream_headers(session_id=session_id, include_json=False),
        )
        self.assertEqual(first.status, 200)
        self.assertEqual(first.headers["Content-Type"], "text/event-stream")
        events = parse_sse_payload(first.body)
        self.assertGreaterEqual(len(events), 1)
        replay_from = events[0]["id"]

        self.app.queue_server_event(session_id, {"jsonrpc": "2.0", "method": "notifications/message", "params": {"text": "again"}})
        replay = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers={**stream_headers(session_id=session_id, include_json=False), "Last-Event-ID": replay_from},
        )
        replay_events = parse_sse_payload(replay.body)
        self.assertTrue(any('"again"' in event["data"] for event in replay_events))

    def test_concurrent_sessions_remain_isolated(self):
        first_session = self._initialize_session()
        second_session = self._initialize_session()

        self.app.queue_server_event(
            first_session,
            {"jsonrpc": "2.0", "method": "notifications/message", "params": {"text": "first-only"}},
        )
        self.app.queue_server_event(
            second_session,
            {"jsonrpc": "2.0", "method": "notifications/message", "params": {"text": "second-only"}},
        )

        first_response = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers=stream_headers(session_id=first_session, include_json=False),
        )
        second_response = execute_hosted_request(
            self.app,
            method="GET",
            path="/mcp",
            headers=stream_headers(session_id=second_session, include_json=False),
        )

        first_events = parse_sse_payload(first_response.body)
        second_events = parse_sse_payload(second_response.body)
        self.assertTrue(any('"first-only"' in event["data"] for event in first_events))
        self.assertFalse(any('"second-only"' in event["data"] for event in first_events))
        self.assertTrue(any('"second-only"' in event["data"] for event in second_events))
        self.assertFalse(any('"first-only"' in event["data"] for event in second_events))

    def test_shared_backed_instances_continue_same_session(self):
        shared_env = {
            "MCP_ENVIRONMENT": "dev",
            "MCP_SESSION_BACKEND": "memory",
            "MCP_SESSION_STORE_URL": "memory://integration-shared",
            "MCP_SESSION_DURABILITY_REQUIRED": "true",
        }
        first = create_app(env=shared_env)
        second = create_app(env=shared_env)
        init = execute_hosted_request(
            first,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers()},
            body=b'{"jsonrpc":"2.0","id":"req-init-shared","method":"initialize","params":{"clientInfo":{"name":"client","version":"1.0.0"}}}',
        )
        response = execute_hosted_request(
            second,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", **stream_headers(session_id=init.headers["MCP-Session-Id"])},
            body=b'{"jsonrpc":"2.0","id":"req-list-shared","method":"tools/list","params":{}}',
        )
        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.payload["result"]["tools"], list)


if __name__ == "__main__":
    unittest.main()
