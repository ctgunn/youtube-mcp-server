import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.transport.session_store import create_session_store, reset_memory_session_store_registry


class DurableSessionStoreTests(unittest.TestCase):
    def tearDown(self):
        reset_memory_session_store_registry()

    def test_shared_memory_store_is_visible_across_instances(self):
        first = create_session_store(backend="memory", store_url="memory://shared-test")
        second = create_session_store(backend="memory", store_url="memory://shared-test")

        first.save_session("session-1", {"session_id": "session-1", "state": "active"})

        self.assertTrue(second.status().shared)
        self.assertEqual(second.load_session("session-1")["session_id"], "session-1")

    def test_local_memory_store_is_not_shared(self):
        first = create_session_store(backend="memory", store_url=None)
        second = create_session_store(backend="memory", store_url=None)

        first.save_session("session-1", {"session_id": "session-1", "state": "active"})

        self.assertIsNone(second.load_session("session-1"))
        self.assertFalse(first.status().shared)

    def test_redis_store_without_client_or_url_reports_unhealthy(self):
        store = create_session_store(backend="redis", store_url=None)
        status = store.status()
        self.assertEqual(status.backend, "redis")
        self.assertFalse(status.healthy)
        self.assertTrue(status.shared)


if __name__ == "__main__":
    unittest.main()
