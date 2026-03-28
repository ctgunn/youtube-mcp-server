import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.protocol.methods import route_mcp_request
from mcp_server.tools.dispatcher import InMemoryToolDispatcher


class RetrievalToolUnitTests(unittest.TestCase):
    def test_search_tool_is_registered_with_required_query_schema(self):
        dispatcher = InMemoryToolDispatcher()
        tools = {tool["name"]: tool for tool in dispatcher.list_tools()}
        self.assertIn("search", tools)
        self.assertEqual(tools["search"]["inputSchema"]["required"], ["query"])
        self.assertEqual(tools["search"]["inputSchema"]["properties"]["query"]["type"], "string")
        self.assertEqual(set(tools["search"]["inputSchema"]["properties"].keys()), {"query"})
        self.assertFalse(tools["search"]["inputSchema"]["additionalProperties"])

    def test_fetch_tool_is_registered_with_openai_identifier_input(self):
        dispatcher = InMemoryToolDispatcher()
        tools = {tool["name"]: tool for tool in dispatcher.list_tools()}
        self.assertIn("fetch", tools)
        self.assertEqual(tools["fetch"]["inputSchema"]["required"], ["id"])
        self.assertEqual(set(tools["fetch"]["inputSchema"]["properties"].keys()), {"id"})
        self.assertEqual(tools["fetch"]["inputSchema"]["properties"]["id"]["minLength"], 1)
        self.assertFalse(tools["fetch"]["inputSchema"]["additionalProperties"])

    def test_dispatcher_enforces_one_of_schema_combinations(self):
        dispatcher = InMemoryToolDispatcher(tools=[])
        dispatcher.register_tool(
            name="combo_tool",
            description="Validate oneOf combinations",
            input_schema={
                "type": "object",
                "properties": {
                    "left": {"type": "string", "minLength": 1},
                    "right": {"type": "string", "minLength": 1},
                },
                "oneOf": [
                    {"required": ["left"]},
                    {"required": ["right"]},
                    {"required": ["left", "right"]},
                ],
                "additionalProperties": False,
            },
            handler=lambda arguments: arguments,
        )
        with self.assertRaisesRegex(ValueError, "required"):
            dispatcher.call_tool("combo_tool", {})

    def test_search_rejects_blank_query(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-invalid",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": ""}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(response["error"]["data"]["category"], "invalid_argument")
        self.assertIn("query", response["error"]["message"].lower())

    def test_search_rejects_unsupported_field(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-extra",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "remote MCP research", "unsupported": True}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(response["error"]["data"]["category"], "invalid_argument")
        self.assertIn("unsupported field", response["error"]["message"].lower())

    def test_search_returns_empty_results_without_error(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-empty",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "no-match-sentinel"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(content["results"], [])

    def test_search_returns_openai_compatible_result_identifiers(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-success",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "remote MCP research"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]["structuredContent"]
        self.assertGreaterEqual(len(content["results"]), 1)
        first = content["results"][0]
        self.assertEqual(set(first.keys()), {"id", "title", "url"})

    def test_fetch_requires_id(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-invalid",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(response["error"]["data"]["category"], "invalid_argument")

    def test_fetch_rejects_legacy_resource_id_shape(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-legacy-id",
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"resourceId": "res_remote_mcp_001"},
            },
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(response["error"]["data"]["category"], "invalid_argument")

    def test_fetch_rejects_legacy_uri_shape(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-legacy-uri",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {"uri": "https://example.com/remote-mcp-research"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(response["error"]["data"]["category"], "invalid_argument")

    def test_fetch_returns_openai_compatible_content_for_known_id(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-success",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {"id": "doc-remote-mcp-001"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]
        structured = content["structuredContent"]
        parsed = json.loads(content["text"])
        self.assertEqual(structured["id"], "doc-remote-mcp-001")
        self.assertEqual(parsed["id"], "doc-remote-mcp-001")
        self.assertIn("text", structured)
        self.assertIn("url", structured)
        self.assertIn("metadata", structured)

    def test_fetch_unknown_resource_maps_to_not_found(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-missing",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {"id": "missing-resource"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["data"]["category"], "unavailable_source")


if __name__ == "__main__":
    unittest.main()
