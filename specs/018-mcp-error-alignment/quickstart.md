# Quickstart: FND-018 JSON-RPC / MCP Error Code Alignment

## Objective

Verify that covered local and hosted MCP failures return the aligned numeric error-code contract, locally first and then through the hosted `/mcp` route, using explicit Red-Green-Refactor steps.

## Prerequisites

- Python 3.11+
- Feature branch: `018-mcp-error-alignment`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted MCP auth inputs available for protected `/mcp` verification

## Execution Baseline

- Keep the current MCP success payloads, tool names, route footprint, auth model, and hosted status-code behavior intact.
- Replace only the covered client-visible error-code contract from string-style enums to the documented numeric mapping.
- Treat `error.data.category` as the stable carrier for the detailed failure reason previously embedded in the string code.

## Implementation Targets

- Local MCP routing must return numeric codes for malformed request, unsupported method, invalid argument, resource-missing, and unexpected tool-failure cases.
- Hosted `/mcp` handling must return the same numeric code and category for equivalent covered failures while preserving existing HTTP statuses.
- Deployment verification and contract examples must stop asserting string-style codes such as `INVALID_ARGUMENT`, `METHOD_NOT_SUPPORTED`, `UNAUTHENTICATED`, and `ORIGIN_DENIED`.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests proving `error.code` is numeric for local protocol-routing and tool-failure responses.
2. Add failing contract tests proving the published MCP error contract and hosted security contract still contain retired string-style codes.
3. Add failing integration tests proving local and hosted representative failure scenarios currently diverge from the new numeric mapping.
4. Add failing deployment-verification checks proving Cloud Run evidence still expects string-style codes.
5. Run targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_envelope_contract.py \
  tests/unit/test_method_routing.py \
  tests/unit/test_invoke_error_mapping.py \
  tests/unit/test_retrieval_tools.py \
  tests/contract/test_mcp_transport_contract.py \
  tests/contract/test_operational_observability_contract.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/contract/test_deep_research_tools_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_hosted_mcp_security_flows.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_docs_examples.py
```

## Green Phase (minimal implementation)

1. Introduce one shared numeric error-code mapping and category-detail strategy.
2. Update local protocol-routing and tool-failure paths to emit the mapped numeric codes.
3. Update hosted `/mcp` denial, session, and invalid-request paths to reuse the same numeric mapping while preserving current HTTP statuses.
4. Update contracts, deploy verification, and examples so all covered error assertions use numeric codes and stable categories.
5. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_envelope_contract.py \
  tests/unit/test_method_routing.py \
  tests/unit/test_invoke_error_mapping.py \
  tests/unit/test_retrieval_tools.py \
  tests/contract/test_mcp_transport_contract.py \
  tests/contract/test_operational_observability_contract.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/contract/test_deep_research_tools_contract.py \
  tests/integration/test_mcp_request_flow.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_hosted_mcp_security_flows.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_docs_examples.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate duplicate error construction paths so local router, hosted entrypoint, and tool dispatch share one mapping approach.
2. Remove stale string-code references from tests, deployment verification helpers, and contracts.
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

1. Send an unsupported method and expect a numeric unsupported-method code:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"req-unsupported","method":"unknown/method","params":{}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- HTTP status remains consistent with the current hosted route behavior for MCP POST handling.
- `error.code` is numeric.
- `error.data.category` is `unsupported_method`.

2. Initialize a protected MCP session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

3. Send an invalid-argument tool call and expect the numeric invalid-argument code:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-invalid-args","method":"tools/call","params":{"name":"server_ping","arguments":"bad"}}' \
  http://127.0.0.1:8080/mcp
```

4. Send an unknown-tool call and expect the numeric resource-missing code:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-missing-tool","method":"tools/call","params":{"name":"missing_tool","arguments":{}}}' \
  http://127.0.0.1:8080/mcp
```

5. Omit authentication and expect a numeric unauthenticated code while preserving the denial status:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-no-auth","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- Hosted denial status remains `401`.
- `error.code` is numeric.
- `error.data.category` is `unauthenticated`.

## Hosted Verification

Repeat the same representative unsupported-method, invalid-argument, missing-tool, and unauthenticated checks against the deployed Cloud Run service URL and record:

- the HTTP status for each hosted failure
- the numeric `error.code`
- the stable `error.data.category`
- the request identifier or equivalent correlatable evidence for each check
- the verifier summary field `errorCodeContract: "numeric"` when using `scripts/verify_cloud_run_foundation.py`

Also verify one representative missing-session or expired-session case to confirm the numeric resource-missing mapping is preserved through hosted stream/session behavior.

## Success Evidence

- Covered MCP failures no longer use string-style top-level error codes.
- Local and hosted representative failures expose the same numeric code and category detail for equivalent scenarios.
- Hosted security and browser-access denials keep their established HTTP status behavior.
- Contracts, tests, and deployment verification no longer rely on retired string-style codes for covered paths.
