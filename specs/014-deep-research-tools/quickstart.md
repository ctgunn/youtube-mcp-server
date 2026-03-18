# Quickstart: FND-014 Deep Research Tool Foundation

## Objective

Verify the `search` and `fetch` MCP tool contract locally first, then through the hosted `/mcp` endpoint, using explicit Red-Green-Refactor steps.

## Prerequisites

- Python 3.11+
- Feature branch: `014-deep-research-tools`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted security inputs available for protected `/mcp` verification

## Execution Baseline

- Keep existing initialize, baseline tool, readiness, and hosted security behavior intact.
- Add only the minimal retrieval contract needed for deep research discovery and follow-up fetch.
- Treat `search` and `fetch` as MCP tools first, not standalone HTTP endpoints.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests for registration, schema validation, stateless retrieval-reference handling, and retrieval failure mapping.
2. Add failing contract tests for `tools/list` discovery metadata and `tools/call` success-result shapes for `search` and `fetch`.
3. Add failing integration tests for successful `search`, empty-result `search`, successful `fetch`, and unavailable-source `fetch`.
4. Add failing hosted verification expectations showing the new tools are absent or undocumented before implementation.
5. Run targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_tool_registry.py \
  tests/unit/test_list_tools_method.py \
  tests/unit/test_invoke_error_mapping.py \
  tests/contract/test_mcp_transport_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py
```

## Green Phase (minimal implementation)

1. Register `search` and `fetch` with complete input schemas and descriptions.
2. Implement the minimum discovery and retrieval result shaping needed to satisfy the failing tests.
3. Update hosted verification guidance and examples to include the new tools.
4. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_tool_registry.py \
  tests/unit/test_list_tools_method.py \
  tests/unit/test_invoke_error_mapping.py \
  tests/contract/test_mcp_transport_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_hosted_mcp_security_flows.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate shared retrieval validation and content-shaping helpers.
2. Remove duplicated documentation or contract wording for the same `search` and `fetch` flows.
3. Re-run the full regression suite:

```bash
python3 -m pytest tests
```

## Local Runtime Setup

Start the hosted runtime locally with the protected MCP route enabled:

```bash
PYTHONPATH=src \
MCP_ENVIRONMENT=dev \
MCP_AUTH_TOKEN=local-dev-token \
MCP_ALLOWED_ORIGINS=http://localhost:3000 \
MCP_ALLOW_ORIGINLESS_CLIENTS=true \
python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

## Manual Local Validation Flow

1. Initialize a protected MCP session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

2. Verify discovery exposes `search` and `fetch`:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://127.0.0.1:8080/mcp
```

3. Verify one successful `search` call:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-search","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research","pageSize":3}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical result shape:

```json
{
  "content": [
    {
      "type": "text",
      "structuredContent": {
        "results": [
          {
            "resourceId": "res_001",
            "uri": "https://example.com/article",
            "title": "Example Article",
            "snippet": "Example summary",
            "position": 1
          }
        ],
        "totalReturned": 1
      }
    }
  ],
  "isError": false
}
```

4. Verify one successful `fetch` call for a selected result:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_001","uri":"https://example.com/article"}}}' \
  http://127.0.0.1:8080/mcp
```

5. Verify one failing retrieval case:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-missing","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"missing-resource"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: stable MCP-safe retrieval failure with no internal details exposed.

## Hosted Verification

Repeat the same initialize, discovery, successful `search`, successful `fetch`, and failing `fetch` checks against the deployed Cloud Run service URL using the hosted MCP auth token.

Record evidence for:

- successful protected initialization
- discovery showing `search` and `fetch`
- one successful `search` result set
- one successful `fetch` content response
- one empty or invalid `search` outcome
- one invalid or unavailable `fetch` outcome
- correlatable hosted request identifiers for the verification run

The hosted verifier should report these named checks:

- `liveness`
- `readiness`
- `initialize`
- `list-tools`
- `search-tool-call`
- `fetch-tool-call`

## Success Evidence

- `tools/list` exposes both deep research tools with complete schemas.
- `search` returns structured discovery output and distinguishes empty results from errors.
- `fetch` returns structured content for a selected result and stable failures for bad retrieval targets.
- Existing hosted security and MCP transport behavior remains unchanged outside the addition of the new tools.
