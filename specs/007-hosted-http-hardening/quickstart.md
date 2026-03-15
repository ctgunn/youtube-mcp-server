# Quickstart: FND-007 Hosted Probe Semantics + HTTP Hardening

## Objective

Implement hosted HTTP hardening so probe routes and the MCP route use
deterministic HTTP status codes, consistent JSON handling, and stable error
semantics in both local and deployed verification.

## Prerequisites

- Python 3.11+
- Feature branch: `007-hosted-http-hardening`
- Existing foundation slices from FND-005 and FND-006 available in the current
  branch
- Local ability to run the Python test suites

## Red Phase (write failing tests and checks first)

1. Add failing contract coverage for:
   - `/readyz` ready versus not-ready HTTP status behavior
   - `/healthz`, `/readyz`, and `/mcp` JSON content-type consistency
   - unknown-path and unsupported-method transport behavior
2. Add failing integration coverage for:
   - malformed JSON requests to hosted `/mcp`
   - malformed MCP payloads to hosted `/mcp`
   - unsupported media types on hosted routes
   - local-to-hosted parity for route classification and status mapping
3. Add failing unit coverage for shared helpers that classify hosted requests
   and choose status codes and error payloads.
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Add the minimum shared hosted request-classification and status-mapping
   behavior needed to satisfy the route contract.
2. Update the hosted entrypoint so:
   - `/healthz` always returns a success liveness response for a live process
   - `/readyz` returns `503` when the instance is not ready
   - `/mcp` rejects malformed, unsupported-method, and unsupported-media-type
     requests with structured JSON errors
   - unknown paths return `404` and supported paths with unsupported methods return `405`
3. Preserve the existing success payload shapes for liveness, readiness, and
   MCP success responses.
4. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate duplicated hosted response-writing and status-selection logic.
2. Remove special cases that classify the same request failure in more than one
   place.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Hosted Validation Flow

1. Start the service locally or deploy the current revision.
2. Verify liveness:

```bash
curl -i http://localhost:8080/healthz
```

3. Verify readiness for a ready instance:

```bash
curl -i http://localhost:8080/readyz
```

4. Verify MCP success behavior:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -d '{"id":"req-q1","method":"tools/list","params":{}}' \
  http://localhost:8080/mcp
```

5. Verify malformed JSON handling:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -d '{"id":"req-bad"' \
  http://localhost:8080/mcp
```

6. Verify unknown-path behavior:

```bash
curl -i http://localhost:8080/unknown
```

7. For deployed verification, repeat the same requests against the hosted
   service URL and confirm status-class parity with local verification.

Expected hosted statuses:
- `/healthz` success: `200`
- `/readyz` ready: `200`
- `/readyz` not ready: `503`
- `/mcp` success: `200`
- `/mcp` malformed payload: `400`
- `/mcp` unsupported media type: `415`
- Supported path with wrong HTTP method: `405`
- Unknown path: `404`

## Success Evidence

- Contract, integration, and unit tests prove hosted route semantics.
- `/readyz` ready and not-ready outcomes differ at the HTTP status layer.
- `/healthz`, `/readyz`, `/mcp`, and JSON error responses use the documented
  response media type policy.
- Malformed, unsupported-method, unsupported-media-type, and unknown-path
  scenarios produce deterministic, sanitized, machine-readable failures.
- Local and deployed verification produce matching route classifications and
  status behavior for equivalent requests.

## Validation Evidence (2026-03-15)

- Unit suite: `python3 -m unittest tests.unit.test_hosted_http_semantics` -> passing
- Integration suites:
  - `python3 -m unittest tests.integration.test_hosted_http_routes` -> passing
  - `python3 -m unittest tests.integration.test_readiness_flow` -> passing
  - `python3 -m unittest tests.integration.test_mcp_request_flow` -> passing
  - `python3 -m unittest tests.integration.test_cloud_run_verification_flow` -> passing
- Contract suites:
  - `python3 -m unittest tests.contract.test_readiness_contract` -> passing
  - `python3 -m unittest tests.contract.test_operational_observability_contract` -> passing
  - `python3 -m unittest tests.contract.test_mcp_transport_contract` -> passing
