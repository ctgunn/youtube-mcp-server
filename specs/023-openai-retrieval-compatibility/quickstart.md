# Quickstart: FND-023 OpenAI Retrieval Compatibility

## Objective

Verify that the existing retrieval tools now behave according to the OpenAI-compatible MCP retrieval contract, locally first and then through the hosted `/mcp` route, using explicit Red-Green-Refactor sequencing.

## Prerequisites

- Python 3.11+
- Feature branch: `023-openai-retrieval-compatibility`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted MCP auth inputs available for protected `/mcp` verification

## Execution Baseline

- Keep the tool names `search` and `fetch`.
- Keep the MCP-native `tools/list` and `tools/call` flow through protected `/mcp`.
- Treat the OpenAI-compatible retrieval contract as the primary public contract for this feature.
- Preserve empty `search` as a non-error path and unavailable `fetch` as a structured failure.

## Implementation Targets

- `tools/list` must publish the OpenAI-compatible retrieval schema.
- `search` must accept the supported OpenAI request shape and return `results` containing `id`, `title`, and `url`.
- `fetch` must accept the supported OpenAI request shape and return `id`, `title`, `text`, `url`, and optional `metadata`.
- Hosted verification must prove the OpenAI-specific flow and one representative unsupported legacy-shape failure.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests proving the current retrieval schema still exposes repo-specific inputs instead of the OpenAI-compatible shape.
2. Add failing contract tests proving `tools/list`, `search`, and `fetch` do not yet match the OpenAI-compatible payloads.
3. Add failing integration tests proving the documented OpenAI-specific examples cannot yet be executed end to end.
4. Add failing docs-example or hosted verification checks proving current examples still reflect the old contract.
5. Run targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_retrieval_tools.py \
  tests/contract/test_deep_research_tools_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_cloud_run_docs_examples.py
```

## Green Phase (minimal implementation)

1. Update retrieval discovery metadata to publish the OpenAI-compatible `search` and `fetch` contract.
2. Update runtime validation and handler behavior to accept the supported OpenAI-compatible inputs and emit the supported result payloads.
3. Update contract tests, docs examples, and hosted verification logic to the new retrieval flow.
4. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_retrieval_tools.py \
  tests/contract/test_deep_research_tools_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_cloud_run_docs_examples.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate retrieval schema and result-shaping rules so discovery, runtime behavior, tests, and docs derive from one coherent contract.
2. Remove duplicated compatibility-boundary wording across code, docs, and hosted verification artifacts.
3. Re-run the full repository verification flow:

```bash
python3 -m pytest
ruff check .
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

2. Verify discovery exposes the OpenAI-compatible retrieval schema:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- `search` publishes `query` as the required input.
- `fetch` publishes `id` as the required input.

3. Verify one successful OpenAI-compatible `search` call:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-search","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- success result with one text content item
- structured payload containing `results`
- each result includes `id`, `title`, and `url`

4. Verify one successful OpenAI-compatible `fetch` call:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch","method":"tools/call","params":{"name":"fetch","arguments":{"id":"doc-remote-mcp-001"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- success result with one text content item
- structured payload containing `id`, `title`, `text`, and `url`

5. Verify one empty-search success path:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-search-empty","method":"tools/call","params":{"name":"search","arguments":{"query":"no-match-sentinel"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: successful response with `results: []`.

6. Verify one unsupported legacy-shape request fails predictably:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-legacy","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_remote_mcp_001"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: stable MCP-safe invalid-argument failure unless a documented compatibility adapter explicitly supports this shape.

## Hosted Verification

Repeat the same initialize, discovery, OpenAI-compatible `search`, OpenAI-compatible `fetch`, empty-search, and unsupported-legacy-shape checks against the deployed Cloud Run service URL using the hosted MCP auth token.

Record evidence for:

- successful protected initialization
- discovery showing the OpenAI-compatible retrieval schemas
- one successful OpenAI-compatible `search` result
- one successful OpenAI-compatible `fetch` result
- one successful empty-search result
- one unsupported legacy-shape failure
- correlatable hosted request identifiers for the verification run

Expected named hosted checks:

- `search-tool-call-openai`
- `fetch-tool-call-openai`
- `search-tool-call-empty`
- `fetch-tool-call-legacy-shape`

## Success Evidence

- `tools/list` exposes the OpenAI-compatible retrieval contract without undocumented assumptions.
- `search` and `fetch` succeed for the documented OpenAI-compatible flow.
- Empty `search` remains a successful non-error outcome.
- Unsupported legacy shapes fail predictably or are documented explicitly through a compatibility boundary.
- Existing MCP transport, hosted security, and non-retrieval behaviors remain unchanged outside the intentional contract-alignment work.
