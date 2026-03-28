# Quickstart: FND-024 Initialize Session Correctness

## Objective

Verify that hosted initialize/session behavior issues `MCP-Session-Id` only after successful initialize completion and never leaves usable continuation state behind for rejected initialize requests, locally first and then through the hosted `/mcp` route using explicit Red-Green-Refactor sequencing.

## Prerequisites

- Python 3.11+
- Feature branch: `024-initialize-session-correctness`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted MCP auth inputs available for protected `/mcp` verification when security is enabled

## Execution Baseline

- Keep the existing `/mcp` route, streamable transport behavior, and MCP-native initialize flow.
- Keep the existing authentication, origin, and session-state failure categories.
- Treat rejected initialize requests as sessionless outcomes.
- Treat successful initialize requests as the only path that may create hosted continuation state.

## Implementation Targets

- Invalid or malformed initialize must return no `MCP-Session-Id`.
- Successful initialize must return exactly one `MCP-Session-Id`.
- Continuation must succeed only for session identifiers issued from successful initialize responses.
- Hosted verification must prove both the no-session failure path and the session-created success path.

## Red Phase (write failing tests and checks first)

1. Add failing contract tests proving rejected initialize paths still issue `MCP-Session-Id` today or otherwise allow invalid continuation behavior.
2. Add failing integration tests proving malformed or invalid initialize requests can still leave behind usable hosted session state.
3. Add failing verification-flow checks proving hosted verification does not yet assert “no session on failed initialize.”
4. Run the targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_method_routing.py \
  tests/contract/test_streamable_http_contract.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_verification_flow.py
```

## Green Phase (minimal implementation)

1. Move session creation behind successful initialize completion in the hosted request executor.
2. Add or reuse the smallest helper needed to determine whether initialize succeeded before issuing headers or creating session state.
3. Update contract tests, integration tests, and hosted verification checks to the corrected lifecycle.
4. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_method_routing.py \
  tests/contract/test_streamable_http_contract.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_streamable_http_transport.py \
  tests/integration/test_cloud_run_verification_flow.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate initialize success detection so session issuance, logs, tests, and verifier expectations all derive from one lifecycle rule.
2. Remove duplicated lifecycle wording across code, contracts, quickstart, and verifier artifacts.
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

1. Verify an invalid initialize request returns no session header:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init-invalid","method":"initialize","params":{}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- error response for invalid initialize
- no `MCP-Session-Id` header

2. Verify a successful initialize request returns a session header:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init-success","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- success response for initialize
- exactly one `MCP-Session-Id` header
- one usable session identifier captured as `SESSION_ID`

3. Verify continuation succeeds only for the issued successful session:

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

- successful continuation response
- tool list returned through the existing MCP contract

4. Verify continuation with a non-issued session identifier fails:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: missing-session' \
  -d '{"jsonrpc":"2.0","id":"req-list-missing","method":"tools/list","params":{}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- stable session-state failure
- no tool success result

5. Verify retry after failure creates valid state only on the later success:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init-retry-1","method":"initialize","params":{}}' \
  http://127.0.0.1:8080/mcp

curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init-retry-2","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected logical evidence:

- first response has no session header
- second response creates the first usable session for that retry sequence

## Hosted Verification

Repeat the same invalid initialize, successful initialize, continuation, invalid-session continuation, and retry-after-failure checks against the deployed Cloud Run service URL using the hosted MCP auth token.

Record evidence for:

- rejected initialize with no `MCP-Session-Id`
- successful initialize with `MCP-Session-Id`
- successful post-initialize continuation
- invalid continuation using a non-issued session identifier
- later successful retry after an earlier rejected initialize
- correlatable hosted request identifiers for the verification run

Expected hosted verification checks:

- `initialize-invalid-no-session`
- `initialize-success-session-created`
- `session-post-continuation`
- `session-invalid`
- `initialize-retry-success`

## Success Evidence

- Rejected initialize requests never expose `MCP-Session-Id`.
- Rejected initialize requests leave no usable continuation state.
- Successful initialize still produces one reusable session identifier.
- Continuation remains valid only for session identifiers issued from successful initialize responses.
- Existing MCP transport, hosted security, and durable-session behavior remain unchanged outside the intentional initialize/session correction.
