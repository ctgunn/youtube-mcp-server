# Quickstart: FND-009 MCP Streamable HTTP Transport

## Objective

Implement hosted MCP streamable HTTP behavior on `/mcp` so modern MCP consumers
can use one endpoint for request submission, optional SSE streams, and
session-aware reconnect behavior while the current Cloud Run deployment path
remains intact.

## Prerequisites

- Python 3.11+
- Feature branch: `009-mcp-streamable-http-transport`
- Existing foundation slices through FND-008 available in the current branch
- Local ability to run the Python test suites

## Red Phase (write failing tests and checks first)

1. Add failing contract coverage for:
   - `POST /mcp` Accept-header negotiation and JSON-vs-SSE response behavior
   - `GET /mcp` SSE stream negotiation
   - session ID issuance during initialization and required reuse afterward
   - invalid protocol-version, invalid-session, unsupported-method, and invalid-origin failures
2. Add failing integration coverage for:
   - streamed response delivery from a `POST` request
   - server-driven event delivery on an active `GET` stream
   - reconnect behavior using `Last-Event-ID`
   - concurrent session and stream isolation
3. Add failing unit coverage for session registry helpers, stream-event
   ordering, reconnect cursor handling, and hosted transport header validation.
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Add the minimum in-memory session and stream state needed for:
   - session ID issuance and lookup
   - one or more active SSE streams per session
   - ordered stream-event delivery
   - best-effort reconnect from `Last-Event-ID`
2. Update the hosted entrypoint so:
   - `POST /mcp` accepts the required transport headers and can return JSON,
     SSE, or `202` with no body depending on the posted MCP message type
   - `GET /mcp` can establish an SSE stream or return `405` when appropriate
   - `MCP-Protocol-Version`, `MCP-Session-Id`, and origin validation failures
     are rejected at the transport layer
3. Preserve `/health` and `/ready` behavior from earlier slices.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate session lookup, stream lifecycle, and SSE event formatting into
   shared transport helpers.
2. Remove duplicated header-validation and reconnect logic across `GET`, `POST`,
   and session-termination paths.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Local Validation Flow

1. Start the hosted runtime locally.
2. Verify stream-capable `POST` request negotiation:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"id":"req-q1","method":"initialize","params":{"clientInfo":{"name":"test","version":"1.0.0"}}}' \
  http://localhost:8080/mcp
```

3. Verify `GET` stream negotiation:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  http://localhost:8080/mcp
```

4. Verify protocol-version failure behavior:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: invalid-version' \
  -d '{"id":"req-q2","method":"tools/list","params":{}}' \
  http://localhost:8080/mcp
```

5. Verify malformed-session behavior after a session is established:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: missing-session' \
  -d '{"id":"req-q3","method":"tools/list","params":{}}' \
  http://localhost:8080/mcp
```

6. Verify reconnect behavior with `Last-Event-ID` once SSE event IDs are
   implemented:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -H 'Last-Event-ID: example-stream-event-id' \
  http://localhost:8080/mcp
```

## Manual Hosted Validation Flow

1. Deploy the current revision using the established FND-008 workflow.
2. Repeat the same `POST /mcp`, `GET /mcp`, invalid protocol-version,
   invalid-session, and reconnect checks against the hosted service URL.
3. Confirm local and hosted behavior match for:
   - session-establishment success
   - JSON-vs-SSE response negotiation
   - invalid header failures
   - concurrent stream isolation
   - reconnect behavior
4. Validate the automated hosted flow:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --evidence-file artifacts/cloud-run-verification.txt
```

## Success Evidence

- Contract, integration, and unit tests prove streamable `GET` and `POST`
  transport behavior.
- Session IDs are issued, reused, and rejected deterministically.
- Stream events remain ordered and isolated to the correct session/stream.
- Invalid protocol-version, origin, and session conditions fail at the
  transport layer rather than inside tool dispatch.
- Local and hosted verification produce matching transport outcomes for the
  same request flows.

## Validation Evidence (2026-03-15)

- Unit suite: `python3 -m unittest tests.unit.test_streamable_http_transport` -> passing
- Integration suites:
  - `python3 -m unittest tests.integration.test_streamable_http_transport` -> passing
  - `python3 -m unittest tests.integration.test_hosted_http_routes` -> passing
  - `python3 -m unittest tests.integration.test_mcp_request_flow` -> passing
  - `python3 -m unittest tests.integration.test_cloud_run_verification_flow` -> passing
  - `python3 -m unittest tests.integration.test_cloud_run_docs_examples` -> passing
  - `python3 -m unittest tests.integration.test_request_observability` -> passing
- Contract suites:
  - `python3 -m unittest tests.contract.test_streamable_http_contract` -> passing
  - `python3 -m unittest tests.contract.test_mcp_transport_contract` -> passing
  - `python3 -m unittest tests.contract.test_operational_observability_contract` -> passing
- Full regression: `python3 -m unittest discover -s tests -p 'test_*.py'` -> passing
