import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.tools.dispatcher import InMemoryToolDispatcher, ToolRegistrationError


class ToolRegistryTests(unittest.TestCase):
    def test_register_tool_requires_description(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        with self.assertRaises(ToolRegistrationError):
            dispatcher.register_tool(
                name="alpha",
                description="",
                input_schema={"type": "object"},
                handler=lambda _: {},
            )

    def test_register_tool_requires_input_schema(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        with self.assertRaises(ToolRegistrationError):
            dispatcher.register_tool(
                name="alpha",
                description="Alpha",
                input_schema=None,
                handler=lambda _: {},
            )

    def test_register_tool_requires_callable_handler(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        with self.assertRaises(ToolRegistrationError):
            dispatcher.register_tool(
                name="alpha",
                description="Alpha",
                input_schema={"type": "object"},
                handler=None,
            )


if __name__ == "__main__":
    unittest.main()
