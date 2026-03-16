# Quickstart: FND-010 MCP Protocol Contract Alignment

## Objective

Replace the current wrapper-based MCP-like payloads with MCP-native protocol
request, result, and error behavior while preserving the existing `/mcp`
streamable HTTP transport and baseline tool availability.

## Prerequisites

- Python 3.11+
- Feature branch: `010-mcp-protocol-alignment`
- Existing foundation slices through FND-009 available in the current branch
- Local ability to run the Python test suites

## Execution Baseline

- Run foundational unit coverage before story-specific Red tests so shared
  protocol helpers fail first when the legacy wrapper remains in place.
- Keep `tests/unit/test_envelope_contract.py` and
  `tests/unit/test_method_routing.py` aligned with the same protocol-native
  request and response rules used by later contract and integration suites.
- Treat hosted JSON and SSE payload checks as part of the same contract
  migration rather than a separate transport rewrite.

## Red Phase (write failing tests and checks first)

1. Replace wrapper-based expectations in the existing tests with failing checks
   for:
   - initialize responses using `result` instead of `success/data/meta/error`
   - tool discovery responses using a protocol-native result shape
   - tool invocation responses using a protocol-native result shape
   - malformed-request, unsupported-method, invalid-argument, and unknown-tool
     failures using a protocol-native `error` shape
2. Add or update failing integration coverage for:
   - initialize -> list -> call flow in local execution
   - hosted `/mcp` JSON responses returning MCP-native bodies
   - hosted streamed tool-call responses carrying the same logical MCP result
3. Add or update failing unit coverage for protocol validation helpers, error
   sanitization, result construction, and legacy-wrapper removal.
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest tests.unit.test_envelope_contract
python3 -m unittest tests.unit.test_initialize_method
python3 -m unittest tests.unit.test_list_tools_method
python3 -m unittest tests.unit.test_invoke_error_mapping
python3 -m unittest tests.contract.test_mcp_transport_contract
python3 -m unittest tests.integration.test_mcp_request_flow
python3 -m unittest tests.integration.test_streamable_http_transport
```

## Green Phase (minimal implementation)

1. Introduce the minimum protocol-native response and error builders needed to
   support initialize, `tools/list`, and `tools/call`.
2. Update method routing so:
   - protocol validation happens before dispatch
   - unsupported methods map to protocol-native errors
   - tool lookup, argument validation, and execution failures map to stable
     protocol-native errors
3. Update hosted request handling so JSON and SSE flows preserve the current
   transport contract while returning the new protocol body shapes.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest tests.unit.test_envelope_contract
python3 -m unittest tests.unit.test_initialize_method
python3 -m unittest tests.unit.test_list_tools_method
python3 -m unittest tests.unit.test_invoke_error_mapping
python3 -m unittest tests.contract.test_mcp_transport_contract
python3 -m unittest tests.integration.test_mcp_request_flow
python3 -m unittest tests.integration.test_streamable_http_transport
```

## Refactor Phase (behavior-preserving cleanup)

1. Remove legacy wrapper helpers and obsolete assertions that no longer belong
   to the MCP-native contract.
2. Consolidate duplicated protocol result and error mapping logic across local
   and hosted paths.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Local Validation Flow

1. Start the hosted runtime locally:

```bash
PYTHONPATH=src python3 -m mcp_server.cloud_run_entrypoint
```

2. Verify initialize returns a protocol-native body:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://localhost:8080/mcp
```

3. Use the returned `MCP-Session-Id` to verify tool discovery:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://localhost:8080/mcp
```

4. Verify tool invocation returns MCP-native result content:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  http://localhost:8080/mcp
```

5. Verify unsupported-method error behavior:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-bad","method":"tools/remove","params":{}}' \
  http://localhost:8080/mcp
```

## Manual Hosted Validation Flow

1. Deploy using the established Cloud Run workflow.
2. Repeat the initialize, `tools/list`, `tools/call`, and unsupported-method
   checks against the hosted service URL.
3. Confirm local and hosted flows return the same protocol-native success and
   error body shapes for the same requests.
4. Validate the hosted verification workflow:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --evidence-file artifacts/cloud-run-verification.txt
```

## Success Evidence

- Contract, integration, and unit tests prove the legacy wrapper has been
  removed from covered MCP flows.
- Initialize, `tools/list`, and `tools/call` all return protocol-native
  results.
- Malformed requests, unsupported methods, invalid arguments, and unknown tools
  all return stable sanitized protocol-native errors.
- Local and hosted verification show matching protocol behavior for the same
  request flows.

## Validation Evidence (2026-03-15)

- Unit suites:
  - `python3 -m unittest tests.unit.test_envelope_contract tests.unit.test_method_routing tests.unit.test_initialize_method tests.unit.test_list_tools_method tests.unit.test_invoke_error_mapping`
  - `python3 -m unittest tests.unit.test_streamable_http_transport`
- Contract suites:
  - `python3 -m unittest tests.contract.test_mcp_transport_contract tests.contract.test_streamable_http_contract`
  - `python3 -m unittest tests.contract.test_cloud_run_foundation_contract tests.contract.test_operational_observability_contract`
- Integration suites:
  - `python3 -m unittest tests.integration.test_mcp_request_flow tests.integration.test_streamable_http_transport tests.integration.test_hosted_http_routes`
  - `python3 -m unittest tests.integration.test_request_observability tests.integration.test_cloud_run_verification_flow tests.integration.test_cloud_run_docs_examples`
- Full regression:
  - `python3 -m unittest discover -s tests -p 'test_*.py'`
  - Result: passing (`138` tests)
