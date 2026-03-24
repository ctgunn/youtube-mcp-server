import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.deploy import HostedRevisionRecord, run_hosted_verification, serialize_verification_run


class CloudRunFoundationContractTests(unittest.TestCase):
    def setUp(self):
        self.revision = HostedRevisionRecord(
            revision_name="rev-001",
            service_name="youtube-mcp-server",
            deployment_timestamp="2026-03-13T00:00:00Z",
            endpoint_url="https://example.com",
            runtime_identity="svc@example.iam.gserviceaccount.com",
            scaling_settings={"minInstances": 0, "maxInstances": 1, "concurrency": 80},
            timeout_seconds=300,
            status="created",
        )

    def test_verification_records_required_check_order(self):
        app_payloads = {
            "/health": {"status": "ok", "statusCode": 200},
            "/ready": {"status": "ready", "checks": {"configuration": "pass"}, "statusCode": 200},
            "initialize": {
                "jsonrpc": "2.0",
                "id": "verify-init",
                "result": {"capabilities": {"tools": {"listChanged": False}}},
                "statusCode": 200,
            },
            "tools/list": {
                "jsonrpc": "2.0",
                "id": "verify-list",
                "result": {
                    "tools": [
                        {
                            "name": "search",
                            "description": "Discover relevant sources for deep research workflows.",
                            "inputSchema": {
                                "type": "object",
                                "required": ["query"],
                                "properties": {"query": {"type": "string", "minLength": 1}},
                                "additionalProperties": False,
                            },
                        },
                        {
                            "name": "fetch",
                            "description": "Retrieve a selected source in consumable content form.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "resourceId": {"type": "string", "minLength": 1},
                                    "uri": {"type": "string", "minLength": 1},
                                },
                                "oneOf": [
                                    {"required": ["resourceId"]},
                                    {"required": ["uri"]},
                                    {"required": ["resourceId", "uri"]},
                                ],
                                "additionalProperties": False,
                            },
                        }
                    ]
                },
                "statusCode": 200,
            },
            "search-tool-call": {
                "jsonrpc": "2.0",
                "id": "verify-search-tool-call",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"results\":[{\"resourceId\":\"res_remote_mcp_001\",\"uri\":\"https://example.com/remote-mcp-research\",\"title\":\"Remote MCP Research Workflows\",\"position\":1}],\"totalReturned\":1}",
                            "structuredContent": {
                                "results": [
                                    {
                                        "resourceId": "res_remote_mcp_001",
                                        "uri": "https://example.com/remote-mcp-research",
                                        "title": "Remote MCP Research Workflows",
                                        "position": 1,
                                    }
                                ],
                                "totalReturned": 1,
                            },
                        }
                    ],
                    "isError": False,
                },
                "statusCode": 200,
            },
            "fetch-tool-call-resource-id": {
                "jsonrpc": "2.0",
                "id": "verify-fetch-by-id",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"resourceId\":\"res_remote_mcp_001\",\"uri\":\"https://example.com/remote-mcp-research\",\"retrievalStatus\":\"complete\"}",
                            "structuredContent": {
                                "resourceId": "res_remote_mcp_001",
                                "uri": "https://example.com/remote-mcp-research",
                                "retrievalStatus": "complete",
                            },
                        }
                    ],
                    "isError": False,
                },
                "statusCode": 200,
            },
            "fetch-tool-call-uri": {
                "jsonrpc": "2.0",
                "id": "verify-fetch-by-uri",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"resourceId\":\"res_remote_mcp_001\",\"uri\":\"https://example.com/remote-mcp-research\",\"retrievalStatus\":\"complete\"}",
                            "structuredContent": {
                                "resourceId": "res_remote_mcp_001",
                                "uri": "https://example.com/remote-mcp-research",
                                "retrievalStatus": "complete",
                            },
                        }
                    ],
                    "isError": False,
                },
                "statusCode": 200,
            },
            "fetch-tool-call-both": {
                "jsonrpc": "2.0",
                "id": "verify-fetch-by-both",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"resourceId\":\"res_remote_mcp_001\",\"uri\":\"https://example.com/remote-mcp-research\",\"retrievalStatus\":\"complete\"}",
                            "structuredContent": {
                                "resourceId": "res_remote_mcp_001",
                                "uri": "https://example.com/remote-mcp-research",
                                "retrievalStatus": "complete",
                            },
                        }
                    ],
                    "isError": False,
                },
                "statusCode": 200,
            },
            "fetch-tool-call-missing": {
                "jsonrpc": "2.0",
                "id": "verify-fetch-missing",
                "error": {"code": -32602, "message": "resourceId or uri is required", "data": {"category": "invalid_argument"}},
                "statusCode": 200,
            },
            "fetch-tool-call-conflict": {
                "jsonrpc": "2.0",
                "id": "verify-fetch-conflict",
                "error": {"code": -32602, "message": "resourceId and uri must identify the same source", "data": {"category": "invalid_argument"}},
                "statusCode": 200,
            },
            "server-ping-call": {
                "jsonrpc": "2.0",
                "id": "verify-replay-seed",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"status\":\"ok\",\"timestamp\":\"2026-03-18T00:00:00Z\"}",
                            "structuredContent": {
                                "status": "ok",
                                "timestamp": "2026-03-18T00:00:00Z",
                            },
                        }
                    ],
                    "isError": False,
                },
                "statusCode": 200,
                "_sseEvents": [
                    {"id": "stream-1:1", "data": ""},
                    {"id": "stream-1:2", "data": "{\"jsonrpc\":\"2.0\",\"id\":\"verify-replay-seed\",\"result\":{\"content\":[{\"type\":\"text\",\"structuredContent\":{\"status\":\"ok\"}}],\"isError\":false}}"},
                ],
            },
            "get-continuation": {"statusCode": 200, "_sseEvents": [{"id": "stream-2:1", "data": ""}]},
            "reconnect": {
                "statusCode": 200,
                "_sseEvents": [
                    {"id": "stream-1:2", "data": "{\"jsonrpc\":\"2.0\",\"id\":\"verify-replay-seed\",\"result\":{\"content\":[{\"type\":\"text\",\"structuredContent\":{\"status\":\"ok\"}}],\"isError\":false}}"}
                ],
            },
            "invalid-session": {
                "statusCode": 404,
                "error": {"code": -32001, "data": {"category": "session_not_found"}},
            },
        }

        def requester(path, payload):
            if path != "/mcp":
                if path == "/":
                    return {"statusCode": 404}
                return app_payloads[path]
            if payload.get("__httpMethod") == "GET" and payload.get("__sessionId") == "missing-session":
                return app_payloads["invalid-session"]
            if payload.get("__httpMethod") == "GET" and payload.get("__lastEventId"):
                return app_payloads["reconnect"]
            if payload.get("__httpMethod") == "GET":
                return app_payloads["get-continuation"]
            if payload["method"] == "tools/call" and payload["params"]["name"] == "server_ping":
                return app_payloads["server-ping-call"]
            if payload["method"] == "tools/call" and payload["params"]["name"] == "search":
                return app_payloads["search-tool-call"]
            if payload["method"] == "tools/call" and payload["params"]["name"] == "fetch":
                arguments = payload["params"]["arguments"]
                if not arguments:
                    return app_payloads["fetch-tool-call-missing"]
                if arguments == {"resourceId": "res_remote_mcp_001"}:
                    return app_payloads["fetch-tool-call-resource-id"]
                if arguments == {"uri": "https://example.com/remote-mcp-research"}:
                    return app_payloads["fetch-tool-call-uri"]
                if arguments == {
                    "resourceId": "res_remote_mcp_001",
                    "uri": "https://example.com/remote-mcp-research",
                }:
                    return app_payloads["fetch-tool-call-both"]
                return app_payloads["fetch-tool-call-conflict"]
            return app_payloads[payload["method"]]

        run = run_hosted_verification(self.revision, requester, evidence_path="artifacts/verify.txt")
        self.assertEqual(
            [check.check_name for check in run.checks],
            [
                "reachability",
                "liveness",
                "readiness",
                "initialize",
                "list-tools",
                "search-tool-call",
                "fetch-tool-call-resource-id",
                "fetch-tool-call-uri",
                "fetch-tool-call-both",
                "fetch-tool-call-missing",
                "fetch-tool-call-conflict",
                "session-post-continuation",
                "session-get-continuation",
                "session-reconnect",
                "session-invalid",
            ],
        )
        self.assertEqual(run.overall_result, "pass")
        self.assertIn("inputSchema", app_payloads["tools/list"]["result"]["tools"][0])
        self.assertEqual(app_payloads["server-ping-call"]["result"]["content"][0]["structuredContent"]["status"], "ok")

        serialized = serialize_verification_run(run)
        self.assertEqual(
            serialized["checks"][0].keys(),
            {
                "checkName",
                "endpointUrl",
                "executedAt",
                "result",
                "summary",
                "statusCode",
                "evidenceLocation",
                "failureLayer",
                "requestReachedApplication",
                "remediation",
            },
        )

    def test_verification_stops_after_failed_readiness(self):
        def requester(path, payload):
            if path == "/":
                return {"statusCode": 404}
            if path == "/health":
                return {"status": "ok", "statusCode": 200}
            if path == "/ready":
                return {
                    "status": "not_ready",
                    "checks": {"configuration": "fail"},
                    "reason": {"code": "CONFIG_VALIDATION_ERROR"},
                    "statusCode": 503,
                }
            self.fail("MCP verification should not execute after readiness failure")

        run = run_hosted_verification(self.revision, requester)
        self.assertEqual([check.check_name for check in run.checks], ["reachability", "liveness", "readiness"])
        self.assertEqual(run.overall_result, "fail")

    def test_contract_document_lists_required_deployment_settings(self):
        contract_path = Path("specs/006-cloud-run-foundation/contracts/cloud-run-foundation-contract.md")
        content = contract_path.read_text()
        for expected in (
            "execution identity",
            "environment profile",
            "secret references",
            "request concurrency",
            "request timeout",
            "baseline-tool-call",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
