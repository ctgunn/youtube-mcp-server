import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.transport.streaming import StreamManager, encode_sse, normalize_accept_header
from tests.unit.conftest import parse_sse_payload


class StreamableHTTPTransportUnitTests(unittest.TestCase):
    def test_session_registry_lifecycle(self):
        manager = StreamManager()
        session = manager.create_session(protocol_version="2025-11-25", client_metadata={"name": "client"})
        self.assertEqual(session.state, "active")
        touched = manager.touch_session(session.session_id)
        self.assertEqual(touched.session_id, session.session_id)
        self.assertGreaterEqual(len(manager.sessions), 1)

    def test_post_response_stream_has_primer_and_response_event(self):
        manager = StreamManager()
        session = manager.create_session(protocol_version="2025-11-25")
        stream, events = manager.build_post_response_stream(
            session.session_id,
            "req-1",
            {"success": True, "data": {"toolName": "server_ping"}, "meta": {"requestId": "req-1"}, "error": None},
        )
        self.assertEqual(stream.origin_method, "POST")
        self.assertEqual(len(events), 2)
        encoded = parse_sse_payload(encode_sse(events))
        self.assertEqual(encoded[0]["data"], "")
        self.assertIn('"toolName": "server_ping"', encoded[1]["data"])

    def test_replay_cursor_returns_only_events_after_last_event_id(self):
        manager = StreamManager()
        session = manager.create_session(protocol_version="2025-11-25")
        stream = manager.open_stream(session.session_id, origin_method="GET")
        first = manager.enqueue_event(session_id=session.session_id, payload={"event": 1}, stream_id=stream.stream_id)
        second = manager.enqueue_event(session_id=session.session_id, payload={"event": 2}, stream_id=stream.stream_id)
        _, replay = manager.events_after(session.session_id, first.event_id)
        self.assertEqual([item.event_id for item in replay], [second.event_id])
        self.assertEqual(replay[0].delivery_state, "replayed")

    def test_accept_header_normalization(self):
        normalized = normalize_accept_header("application/json; charset=utf-8, text/event-stream")
        self.assertEqual(normalized, {"application/json", "text/event-stream"})


if __name__ == "__main__":
    unittest.main()
