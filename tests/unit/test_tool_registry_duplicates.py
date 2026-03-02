import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.tools.dispatcher import DuplicateToolError, InMemoryToolDispatcher


class ToolRegistryDuplicateTests(unittest.TestCase):
    def test_duplicate_name_rejected_with_normalized_match(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="Server_Ping",
            description="Primary",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
            handler=lambda _: {"ok": True},
        )

        with self.assertRaises(DuplicateToolError):
            dispatcher.register_tool(
                name="server_ping",
                description="Duplicate",
                input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                handler=lambda _: {"ok": True},
            )


if __name__ == "__main__":
    unittest.main()
