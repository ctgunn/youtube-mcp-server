import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class BaselineServerToolsTests(unittest.TestCase):
    def test_server_ping_payload_contains_status_and_timestamp(self):
        dispatcher = InMemoryToolDispatcher()
        result = dispatcher.call_tool("server_ping", {})
        self.assertEqual(result["status"], "ok")
        self.assertIsInstance(result["timestamp"], str)
        self.assertTrue(result["timestamp"])

    def test_server_info_uses_defaults_when_metadata_missing(self):
        dispatcher = InMemoryToolDispatcher(server_metadata={})
        result = dispatcher.call_tool("server_info", {})
        self.assertEqual(result["version"], "0.1.0")
        self.assertEqual(result["environment"], "dev")
        self.assertEqual(result["build"]["buildId"], "local")
        self.assertEqual(result["build"]["commit"], "unknown")
        self.assertEqual(result["build"]["buildTime"], "unknown")

    def test_server_info_allows_partial_metadata_overrides(self):
        dispatcher = InMemoryToolDispatcher(
            server_metadata={
                "version": "1.2.3",
                "build": {
                    "commit": "abc123",
                },
            }
        )
        result = dispatcher.call_tool("server_info", {})
        self.assertEqual(result["version"], "1.2.3")
        self.assertEqual(result["environment"], "dev")
        self.assertEqual(result["build"]["buildId"], "local")
        self.assertEqual(result["build"]["commit"], "abc123")
        self.assertEqual(result["build"]["buildTime"], "unknown")

    def test_server_list_tools_returns_complete_tool_descriptors(self):
        dispatcher = InMemoryToolDispatcher()
        result = dispatcher.call_tool("server_list_tools", {})
        self.assertGreaterEqual(len(result), 1)
        self.assertIn("name", result[0])
        self.assertIn("description", result[0])
        self.assertIn("inputSchema", result[0])


if __name__ == "__main__":
    unittest.main()
