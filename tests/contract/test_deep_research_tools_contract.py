import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.cloud_run_entrypoint import execute_hosted_request
from mcp_server.deploy import _normalize_request_result


class DeepResearchToolsContractTests(unittest.TestCase):
    def setUp(self):
        os.environ["MCP_ENVIRONMENT"] = "dev"
        self.app = create_app()

    def _initialize_hosted_session(self):
        result = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            body=b'{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"contract","version":"1.0.0"}}}',
        )
        self.assertEqual(result.status, 200)
        return result.headers["MCP-Session-Id"]

    def test_tools_list_includes_search_and_fetch_contract_metadata(self):
        response = self.app.handle("/mcp", {"jsonrpc": "2.0", "id": "req-list", "method": "tools/list", "params": {}})
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}
        self.assertIn("search", tools)
        self.assertIn("fetch", tools)
        self.assertEqual(tools["search"]["inputSchema"]["required"], ["query"])
        self.assertFalse(tools["search"]["inputSchema"]["additionalProperties"])
        self.assertFalse(tools["fetch"]["inputSchema"]["additionalProperties"])
        self.assertEqual(tools["fetch"]["inputSchema"]["required"], ["id"])
        self.assertEqual(set(tools["fetch"]["inputSchema"]["properties"].keys()), {"id"})

    def test_search_result_contract_uses_mcp_aligned_content(self):
        response = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "remote MCP research"}},
            },
        )
        content = response["result"]["content"][0]
        self.assertEqual(content["type"], "text")
        structured = content["structuredContent"]
        self.assertIn("results", structured)
        if structured["results"]:
            self.assertEqual(set(structured["results"][0].keys()), {"id", "title", "url"})

    def test_fetch_result_contract_uses_mcp_aligned_content(self):
        by_id = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-id",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": "doc-remote-mcp-001"}},
            },
        )
        missing_legacy = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-legacy-uri",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"uri": "https://example.com/remote-mcp-research"}},
            },
        )
        content = by_id["result"]["content"][0]
        structured = content["structuredContent"]
        parsed = json.loads(content["text"])
        self.assertEqual(structured["id"], parsed["id"])
        self.assertIn("url", structured)
        self.assertIn("text", structured)
        self.assertEqual(missing_legacy["error"]["code"], -32602)

    def test_invalid_search_and_missing_fetch_use_stable_error_codes(self):
        invalid_search = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-search-invalid",
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": ""}},
            },
        )
        self.assertEqual(invalid_search["error"]["code"], -32602)
        self.assertEqual(invalid_search["error"]["data"]["category"], "invalid_argument")

        missing_fetch = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-missing",
                "method": "tools/call",
                "params": {"name": "fetch", "arguments": {"id": "missing-resource"}},
            },
        )
        self.assertEqual(missing_fetch["error"]["code"], -32001)
        self.assertEqual(missing_fetch["error"]["data"]["category"], "unavailable_source")

        legacy_fetch = self.app.handle(
            "/mcp",
            {
                "jsonrpc": "2.0",
                "id": "req-fetch-legacy",
                "method": "tools/call",
                "params": {
                    "name": "fetch",
                    "arguments": {"resourceId": "res_remote_mcp_001"},
                },
            },
        )
        self.assertEqual(legacy_fetch["error"]["code"], -32602)
        self.assertEqual(legacy_fetch["error"]["data"]["category"], "invalid_argument")

    def test_hosted_contract_exposes_search_and_fetch_on_protected_mcp_route(self):
        session_id = self._initialize_hosted_session()
        response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-list-hosted","method":"tools/list","params":{}}',
        )
        self.assertEqual(response.status, 200)
        tools = {tool["name"]: tool for tool in response.payload["result"]["tools"]}
        self.assertIn("search", tools)
        self.assertIn("fetch", tools)
        self.assertEqual(tools["fetch"]["inputSchema"]["required"], ["id"])

        search_response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-search-hosted","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research"}}}',
        )
        self.assertEqual(search_response.status, 200)
        normalized = _normalize_request_result(search_response)
        self.assertEqual(normalized["result"]["content"][0]["structuredContent"]["results"][0]["id"], "doc-remote-mcp-001")

        fetch_response = execute_hosted_request(
            self.app,
            method="POST",
            path="/mcp",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Session-Id": session_id,
            },
            body=b'{"jsonrpc":"2.0","id":"req-fetch-hosted","method":"tools/call","params":{"name":"fetch","arguments":{"id":"doc-remote-mcp-001"}}}',
        )
        self.assertEqual(fetch_response.status, 200)
        hosted_fetch = _normalize_request_result(fetch_response)
        self.assertEqual(hosted_fetch["result"]["content"][0]["structuredContent"]["id"], "doc-remote-mcp-001")


if __name__ == "__main__":
    unittest.main()
