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

    def test_fetch_tool_is_registered_with_resource_identifier_inputs(self):
        dispatcher = InMemoryToolDispatcher()
        tools = {tool["name"]: tool for tool in dispatcher.list_tools()}
        self.assertIn("fetch", tools)
        self.assertIn("resourceId", tools["fetch"]["inputSchema"]["properties"])
        self.assertIn("uri", tools["fetch"]["inputSchema"]["properties"])

    def test_search_rejects_blank_query(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-invalid",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": ""}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")
        self.assertIn("query", response["error"]["message"].lower())

    def test_search_returns_empty_results_without_error(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-empty",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "no-match-sentinel", "pageSize": 3}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]["structuredContent"]
        self.assertEqual(content["results"], [])
        self.assertEqual(content["totalReturned"], 0)

    def test_search_returns_deterministic_result_order_and_identifiers(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-search-success",
            "method": "tools/call",
            "params": {"name": "search", "arguments": {"query": "remote MCP research", "pageSize": 2}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]["structuredContent"]
        self.assertGreaterEqual(len(content["results"]), 1)
        first = content["results"][0]
        self.assertIn("resourceId", first)
        self.assertIn("uri", first)
        self.assertEqual(first["position"], 1)

    def test_fetch_requires_resource_id_or_uri(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-invalid",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_fetch_rejects_conflicting_resource_id_and_uri(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-conflict",
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"resourceId": "res_remote_mcp_001", "uri": "https://example.com/not-the-same"},
            },
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], "INVALID_ARGUMENT")

    def test_fetch_returns_content_for_known_resource(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-success",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {"resourceId": "res_remote_mcp_001"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        content = response["result"]["content"][0]
        structured = content["structuredContent"]
        parsed = json.loads(content["text"])
        self.assertEqual(structured["resourceId"], "res_remote_mcp_001")
        self.assertEqual(parsed["resourceId"], "res_remote_mcp_001")
        self.assertIn("content", structured)
        self.assertIn("retrievalStatus", structured)

    def test_fetch_unknown_resource_maps_to_not_found(self):
        payload = {
            "jsonrpc": "2.0",
            "id": "req-fetch-missing",
            "method": "tools/call",
            "params": {"name": "fetch", "arguments": {"resourceId": "missing-resource"}},
        }
        response = route_mcp_request(payload, InMemoryToolDispatcher())
        self.assertEqual(response["error"]["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(response["error"]["data"]["category"], "unavailable_source")


if __name__ == "__main__":
    unittest.main()
