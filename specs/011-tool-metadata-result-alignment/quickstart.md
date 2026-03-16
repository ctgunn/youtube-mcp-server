# Quickstart: FND-011 Tool Metadata + Invocation Result Alignment

## Objective

Expand tool discovery to expose complete MCP-facing metadata and align
successful tool invocation results so MCP clients can discover and consume
baseline tools without relying on simplified wrappers or out-of-band
documentation.

## Prerequisites

- Python 3.11+
- Feature branch: `011-tool-metadata-result-alignment`
- Existing foundation slices through FND-010 available in the current branch
- Local ability to run the Python test suites

## Execution Baseline

- Keep FND-010 request and error behavior intact while changing only tool
  discovery metadata and successful tool result content.
- Use the existing baseline tools as the minimum regression set for the new
  discovery and invocation contract.
- Treat `tools/list` and `server_list_tools` as one shared discovery contract,
  not two separate registry views.

## Red Phase (write failing tests and checks first)

1. Replace discovery assertions in existing tests with failing checks that each
   listed tool includes `name`, `description`, and `inputSchema`.
2. Add or update failing unit tests that prove `server_list_tools` matches the
   richer descriptors returned by `tools/list`.
3. Add or update failing unit and integration tests that prove successful
   baseline tool invocations return aligned MCP content preserving structured
   output rather than only one JSON text blob.
4. Add or update failing hosted and contract checks for richer `tools/list`
   results and aligned `tools/call` success content.
5. Run targeted suites and confirm failures:

```bash
python3 -m unittest tests.unit.test_tool_registry
python3 -m unittest tests.unit.test_tool_registry_duplicates
python3 -m unittest tests.unit.test_baseline_server_tools
python3 -m unittest tests.unit.test_list_tools_method
python3 -m unittest tests.unit.test_invoke_error_mapping
python3 -m unittest tests.contract.test_mcp_transport_contract
python3 -m unittest tests.integration.test_mcp_request_flow
python3 -m unittest tests.integration.test_hosted_http_routes
```

## Green Phase (minimal implementation)

1. Update the tool registry so discovery exposes complete MCP-facing tool
   descriptors sourced from one registry definition path.
2. Update baseline tool discovery behavior so `server_list_tools` returns the
   same richer descriptors as `tools/list`.
3. Update successful tool-result shaping to emit the minimum aligned MCP
   content structure needed to preserve baseline-tool meaning.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest tests.unit.test_tool_registry
python3 -m unittest tests.unit.test_tool_registry_duplicates
python3 -m unittest tests.unit.test_baseline_server_tools
python3 -m unittest tests.unit.test_list_tools_method
python3 -m unittest tests.unit.test_invoke_error_mapping
python3 -m unittest tests.contract.test_mcp_transport_contract
python3 -m unittest tests.integration.test_mcp_request_flow
python3 -m unittest tests.integration.test_hosted_http_routes
python3 -m unittest tests.contract.test_streamable_http_contract
python3 -m unittest tests.contract.test_cloud_run_foundation_contract
```

## Refactor Phase (behavior-preserving cleanup)

1. Remove duplicated tool-descriptor assembly and success-result shaping logic.
2. Consolidate registry-to-protocol mapping helpers so local and hosted
   discovery/invocation flows cannot drift.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Local Validation Flow

1. Start the hosted runtime locally:

```bash
PYTHONPATH=src python3 -m mcp_server.cloud_run_entrypoint
```

2. Initialize a session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://localhost:8080/mcp
```

3. Verify `tools/list` returns complete metadata:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://localhost:8080/mcp
```

Expected discovery result fields per tool:

```json
{
  "name": "server_ping",
  "description": "Return service status and timestamp",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

4. Verify `server_list_tools` returns the same richer descriptors through tool
   invocation:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call-list","method":"tools/call","params":{"name":"server_list_tools","arguments":{}}}' \
  http://localhost:8080/mcp
```

5. Verify `server_ping` returns aligned MCP content with preserved structured
   output:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call-ping","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  http://localhost:8080/mcp
```

Expected success content shape:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"status\":\"ok\",\"timestamp\":\"...\"}",
      "structuredContent": {
        "status": "ok",
        "timestamp": "..."
      }
    }
  ],
  "isError": false
}
```

## Success Evidence

- Discovery shows complete tool descriptors for all baseline tools.
- `server_list_tools` matches the richer `tools/list` output.
- Successful baseline tool invocations return aligned MCP content preserving
  structured meaning.
- Existing initialize, readiness, error, and hosted transport behavior remain
  unchanged outside the new discovery/success-result contract.

## Validation Evidence (2026-03-16)

- Focused Red-to-Green suites:
  - `python3 -m unittest tests.unit.test_tool_registry tests.unit.test_tool_registry_duplicates tests.unit.test_list_tools_method tests.unit.test_invoke_error_mapping tests.unit.test_baseline_server_tools tests.contract.test_mcp_transport_contract tests.integration.test_mcp_request_flow tests.integration.test_hosted_http_routes`
- Full regression:
  - `python3 -m unittest discover -s tests -p 'test_*.py'`
  - Result: passing (`144` tests)
