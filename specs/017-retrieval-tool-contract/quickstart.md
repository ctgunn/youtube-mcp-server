# Quickstart: FND-017 Retrieval Tool Contract Completeness

## Objective

Verify that `search` and `fetch` can be called from MCP discovery output alone, locally first and then through the hosted `/mcp` route, using explicit Red-Green-Refactor steps.

## Prerequisites

- Python 3.11+
- Feature branch: `017-retrieval-tool-contract`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted MCP auth inputs available for protected `/mcp` verification

## Execution Baseline

- Keep the current retrieval-tool names, success-result shapes, and hosted access model intact.
- Add only the minimum schema, validation-alignment, and documentation changes needed to make the retrieval contract fully machine-readable.
- Treat `tools/list` discovery metadata as the source clients should use to construct valid requests.

## Implementation Targets

- `fetch` discovery metadata must describe the supported `resourceId`-only, `uri`-only, and matching combined-identifier request shapes.
- `search` discovery metadata must continue to describe the required query input and optional controls without relying on undocumented runtime-only rules.
- Hosted verification evidence must prove that the request examples were built from discovery output instead of separate ad hoc assumptions.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests proving the published `fetch` schema describes the supported identifier combinations and rejects unsupported shapes.
2. Add failing contract tests proving `tools/list` publishes the complete retrieval contract and that discovery-driven requests match runtime behavior.
3. Add failing integration tests proving valid `fetch` requests succeed for `resourceId`, `uri`, and matching combined identifiers, while invalid combinations fail predictably.
4. Add failing hosted documentation or verification checks proving the published examples are insufficient before the contract is completed.
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

1. Update retrieval discovery metadata so the valid `search` and `fetch` request shapes are fully machine-readable.
2. Align runtime validation with the published schemas so supported and unsupported request patterns behave exactly as discovery indicates.
3. Update hosted documentation and verification examples so every supported `fetch` pattern is demonstrably constructible from discovery output.
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

1. Consolidate retrieval schema and validation rules so discovery, runtime checks, and examples do not describe the same constraint in conflicting ways.
2. Remove duplicated retrieval-contract wording across code, contract tests, and hosted examples.
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

2. Verify discovery exposes the completed retrieval schemas:

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

- `search` publishes `query` as required.
- `fetch` publishes `resourceId`, `uri`, and the supported required-input combinations.

3. Verify one successful `search` call built from discovery:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-search","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research","pageSize":1}}}' \
  http://127.0.0.1:8080/mcp
```

4. Verify each supported valid `fetch` request pattern:

By `resourceId`:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-id","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_remote_mcp_001"}}}' \
  http://127.0.0.1:8080/mcp
```

By `uri`:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-uri","method":"tools/call","params":{"name":"fetch","arguments":{"uri":"https://example.com/remote-mcp-research"}}}' \
  http://127.0.0.1:8080/mcp
```

By matching `resourceId` and `uri`:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-both","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_remote_mcp_001","uri":"https://example.com/remote-mcp-research"}}}' \
  http://127.0.0.1:8080/mcp
```

5. Verify invalid request-shape failures:

Missing identifiers:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-missing","method":"tools/call","params":{"name":"fetch","arguments":{}}}' \
  http://127.0.0.1:8080/mcp
```

Conflicting identifiers:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-conflict","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_remote_mcp_001","uri":"https://example.com/not-the-same"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: stable MCP-safe `INVALID_ARGUMENT` failures with no internal details exposed.

## Hosted Verification

Repeat the same initialize, discovery, `search`, valid `fetch` by `resourceId`, valid `fetch` by `uri`, valid `fetch` by matching identifiers, and invalid `fetch` checks against the deployed Cloud Run service URL using the hosted MCP auth token.

Record evidence for:

- successful protected initialization
- discovery showing the completed retrieval schemas
- one successful `search` result
- one successful `fetch` call for each supported valid identifier pattern
- one invalid missing-identifier `fetch` outcome
- one invalid conflicting-identifier `fetch` outcome
- correlatable hosted request identifiers for the verification run

Expected named hosted checks:

- `search-tool-call`
- `fetch-tool-call-resource-id`
- `fetch-tool-call-uri`
- `fetch-tool-call-both`
- `fetch-tool-call-missing`
- `fetch-tool-call-conflict`

## Success Evidence

- `tools/list` exposes retrieval schemas that are sufficient to build valid `search` and `fetch` calls without undocumented assumptions.
- `search` still returns structured discovery output and distinguishes empty results from errors.
- `fetch` succeeds for every supported valid identifier pattern and rejects unsupported patterns predictably.
- Existing MCP transport, hosted security, and retrieval success behavior remain unchanged outside the contract-completeness updates.
