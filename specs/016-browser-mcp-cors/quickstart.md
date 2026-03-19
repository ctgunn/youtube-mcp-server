# Quickstart: FND-016 Browser-Originated MCP Access + CORS Support

## Objective

Verify explicit browser-originated hosted MCP access locally first, then through the hosted verification path, using Red-Green-Refactor execution.

## Prerequisites

- Python 3.11+
- Feature branch: `016-browser-mcp-cors`
- Repository dependencies installed with `python3 -m pip install -e .`
- Hosted security inputs available for protected `/mcp` verification
- One allowed browser origin for local validation, such as `http://localhost:3000`

## Execution Baseline

- Preserve the current MCP protocol, auth behavior, session behavior, and origin-aware security model.
- Add only the minimum browser preflight and response-header behavior needed to make approved and denied browser access explicit.
- Treat browser-origin support as a hosted transport concern, not a change to tool behavior or MCP message semantics.
- Keep browser support scoped to `/mcp`; `/health` and `/ready` remain non-browser-accessible operational routes in this feature slice.

## Red Phase (write failing tests and checks first)

1. Add failing unit tests for browser origin evaluation, preflight request classification, supported-request-header handling, and response-header selection.
2. Add failing contract tests for approved-origin preflight, approved-origin actual response headers, denied-origin behavior, and unsupported browser request patterns.
3. Add failing integration tests that exercise browser-style `OPTIONS`, approved browser `POST /mcp`, and denied browser flows through the hosted request entrypoint.
4. Add failing hosted verification expectations proving browser-approved and browser-denied scenarios are not yet covered.
5. Run targeted suites and confirm failures:

```bash
python3 -m pytest \
  tests/unit/test_hosted_security_policy.py \
  tests/unit/test_hosted_http_semantics.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/integration/test_hosted_mcp_security_flows.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_cloud_run_verification_flow.py
```

## Green Phase (minimal implementation)

1. Add the minimum hosted route handling for browser preflight requests.
2. Add the minimum response-header shaping for approved browser-originated hosted responses.
3. Add the minimum denial-path shaping for disallowed origins and unsupported browser request patterns.
4. Update hosted verification and documentation to reflect the explicit browser contract.
5. Re-run the targeted suites until they pass:

```bash
python3 -m pytest \
  tests/unit/test_hosted_security_policy.py \
  tests/unit/test_hosted_http_semantics.py \
  tests/unit/test_cloud_run_security_gate.py \
  tests/contract/test_hosted_mcp_security_contract.py \
  tests/integration/test_hosted_mcp_security_flows.py \
  tests/integration/test_hosted_http_routes.py \
  tests/integration/test_cloud_run_verification_flow.py
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate browser preflight, header generation, and denial mapping behind shared hosted transport helpers.
2. Remove duplicate browser decision logic from request handling and verification code.
3. Re-run the full regression suite:

```bash
python3 -m pytest tests
```

## Local Runtime Setup

Export the hosted security settings used by the browser flow:

```bash
export MCP_ENVIRONMENT=dev
export MCP_AUTH_TOKEN=local-dev-token
export MCP_ALLOWED_ORIGINS=http://localhost:3000
export MCP_ALLOW_ORIGINLESS_CLIENTS=true
```

Start the local hosted runtime:

```bash
PYTHONPATH=src PORT=8080 python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

## Manual Local Validation Flow

1. Verify approved browser preflight for `POST /mcp`:

```bash
curl -i -X OPTIONS \
  -H 'Origin: http://localhost:3000' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization, content-type' \
  http://127.0.0.1:8080/mcp
```

Expected result: a successful preflight response with the documented browser allow headers.
Required headers: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`.

2. Verify an approved browser-originated hosted initialize request:

```bash
curl -i \
  -H 'Origin: http://localhost:3000' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-browser-init","method":"initialize","params":{"clientInfo":{"name":"browser","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: normal hosted MCP initialize behavior plus the documented cross-origin response headers.
Required headers: `Access-Control-Allow-Origin` and `Access-Control-Expose-Headers` exposing `MCP-Session-Id`, `MCP-Protocol-Version`, and `X-Stream-Id` when present.

3. Verify denied-origin preflight behavior:

```bash
curl -i -X OPTIONS \
  -H 'Origin: https://evil.example' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization, content-type' \
  http://127.0.0.1:8080/mcp
```

Expected result: the documented denial behavior, without a successful browser grant.

4. Verify denied-origin actual request behavior:

```bash
curl -i \
  -H 'Origin: https://evil.example' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-browser-denied","method":"initialize","params":{"clientInfo":{"name":"browser","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: a stable denial response that is distinct from successful browser access.

5. Verify originless non-browser behavior remains unchanged:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-originless","method":"initialize","params":{"clientInfo":{"name":"cli","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: the existing non-browser hosted flow continues to work according to the current security policy.

## Hosted Verification

Run the hosted verification flow against the deployed Cloud Run service and record evidence for:

- successful approved-origin browser preflight
- successful approved-origin authenticated hosted MCP request with browser response headers
- expected denied-origin browser failure
- expected unsupported browser request-pattern failure
- preserved non-browser hosted MCP access where configured

The hosted verifier should report browser-specific evidence alongside the existing hosted checks so operators can confirm browser support is deliberate and bounded.

When verifying a deployed service, provide the approved browser origin to the verifier so it can exercise both approved and denied browser scenarios:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --auth-token "$MCP_AUTH_TOKEN" \
  --origin http://localhost:3000 \
  --evidence-file artifacts/cloud-run-verification.txt
```

Expected browser-specific hosted verification checks:

- `browser-preflight-approved`
- `browser-request-approved`
- `browser-origin-denied`
- `browser-request-unsupported`

## Success Evidence

- Approved browser origins can complete preflight and actual hosted requests for documented supported paths.
- Disallowed origins and unsupported browser patterns fail with stable documented behavior.
- Existing auth, session, and non-browser hosted behavior remain intact outside the intentional browser-access changes.

## Latest Validation Snapshot

- `2026-03-19`: `python3 -m pytest tests` passed locally across the repository test suite (`224` tests), including browser preflight, approved-origin response headers, denied-origin handling, hosted verification browser checks, and existing session/security regressions.
