# Quickstart: FND-015 Hosted MCP Session Durability

## Objective

Verify durable hosted MCP session continuation locally first, then through the hosted Cloud Run verification path, using explicit Red-Green-Refactor steps.

## Prerequisites

- Python 3.11+
- Feature branch: `015-hosted-session-durability`
- Repository dependencies installed with `python3 -m pip install -e .`
- A reachable shared session backend for local multi-instance verification (`memory://...` for in-process shared tests or `redis://...` for a hosted-like flow)
- Hosted security inputs available for protected `/mcp` verification

## Execution Baseline

- Preserve the current MCP protocol, session headers, security checks, and tool invocation behavior.
- Add only the minimum shared durable-session layer needed to remove process-local fragility.
- Treat durable session continuity as a hosted transport concern, not a new client protocol.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests for durable session persistence, expiry handling, replay-window enforcement, and readiness failure when hosted durability is required but unavailable.
2. Add failing contract tests for initialize-plus-continuation, reconnect replay, expired-session, and replay-unavailable outcomes.
3. Add failing integration tests that initialize on one app instance and continue on another app instance sharing the same durable backend.
4. Add failing hosted verification expectations showing continuation and reconnect evidence are missing before implementation.
5. Run targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_streamable_http_transport.py \
  tests/unit/test_readiness_state.py \
  tests/contract/test_streamable_http_contract.py \
  tests/contract/test_readiness_contract.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_verification_flow.py
```

## Green Phase (minimal implementation)

1. Introduce the durable hosted session-store abstraction and the minimum runtime configuration needed to enable it.
2. Persist hosted session identity and replayable event state in the shared backend.
3. Update readiness and hosted verification so unsafe deployments are visible before operators rely on them.
4. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_streamable_http_transport.py \
  tests/unit/test_readiness_state.py \
  tests/unit/test_runtime_config_validation.py \
  tests/contract/test_streamable_http_contract.py \
  tests/contract/test_readiness_contract.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_verification_flow.py \
  tests/integration/test_hosted_http_routes.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate store access, session expiry, and replay lookup behind one transport-facing session durability layer.
2. Remove duplicate continuity decisions from request handling and verification code.
3. Re-run the full regression suite:

```bash
python3 -m pytest tests
```

## Local Runtime Setup

Export the shared session backend and hosted security settings:

```bash
export MCP_ENVIRONMENT=dev
export MCP_AUTH_TOKEN=local-dev-token
export MCP_ALLOWED_ORIGINS=http://localhost:3000
export MCP_ALLOW_ORIGINLESS_CLIENTS=true
export MCP_SESSION_BACKEND=memory
export MCP_SESSION_STORE_URL=memory://local-durable-session-demo
export MCP_SESSION_DURABILITY_REQUIRED=true
```

Start two local hosted runtimes that share the same durable session backend:

```bash
PYTHONPATH=src PORT=8080 python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

```bash
PYTHONPATH=src PORT=8081 python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8081
```

## Manual Local Validation Flow

1. Initialize a protected hosted session against the first runtime:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

2. Reuse the returned `MCP-Session-Id` against the second runtime to prove cross-instance `POST` continuation:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://127.0.0.1:8081/mcp
```

Expected result: successful MCP response rather than `Session not found`.

3. Queue or trigger a replayable event, then reconnect through the second runtime with `GET /mcp`:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  http://127.0.0.1:8081/mcp
```

4. Reconnect again with a valid `Last-Event-ID` cursor and confirm replay returns only later events:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -H 'Last-Event-ID: STREAM_CURSOR' \
  http://127.0.0.1:8080/mcp
```

5. Validate one expected failure path with an expired, unknown, or replay-unavailable session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: missing-session' \
  -d '{"jsonrpc":"2.0","id":"req-invalid","method":"tools/list","params":{}}' \
  http://127.0.0.1:8081/mcp
```

Expected result: stable session-state failure distinct from tool or security errors.

## Hosted Verification

Run the hosted verification flow against the deployed Cloud Run service with durable-session configuration enabled. Record evidence for:

- successful protected initialization
- successful follow-up `POST` continuation
- successful follow-up `GET` continuation
- successful reconnect with recent replay cursor
- expected invalid or expired session failure
- expected replay-unavailable failure when reconnect exceeds retained history
- correlatable hosted request identifiers for the verification run

For deployed Cloud Run validation, switch `MCP_SESSION_BACKEND` and
`MCP_SESSION_STORE_URL` to the shared Redis-compatible backend used by every
serving instance.

The hosted verifier should report these named checks:

- `liveness`
- `readiness`
- `initialize`
- `list-tools`
- `session-post-continuation`
- `session-get-continuation`
- `session-reconnect`
- `session-invalid`

## Success Evidence

- A session initialized on one runtime can continue on another runtime that shares the durable backend.
- Readiness blocks or clearly flags hosted deployments that cannot guarantee durable sessions.
- Reconnect succeeds within the documented replay window and fails cleanly outside it.
- Existing security, tool discovery, and invocation behavior remains intact outside the session durability changes.

## Latest Validation Snapshot

- `2026-03-18`: `python3 -m unittest` passed locally across the repository test suite (`210` tests), including the new durable-session config, readiness, cross-instance continuation, reconnect, and hosted verification coverage.
