# Contract: FND-007 Hosted Probe Semantics + HTTP Hardening

## Purpose

Define the externally visible hosted HTTP behavior for the foundation service
so Cloud Run probes, operators, and MCP clients can rely on transport-level
status codes and consistent JSON response handling.

## Scope

- Hosted liveness contract for `GET /healthz`
- Hosted readiness contract for `GET /readyz`
- Hosted MCP contract for supported requests to `/mcp`
- Hosted failure semantics for malformed requests, unsupported media types,
  unsupported methods, and unknown paths

## Hosted Route Contract

### `GET /healthz`

Success contract:
- Returns a success HTTP status.
- Returns a JSON liveness payload:

```json
{
  "status": "ok"
}
```

Behavior rules:
- The route is probe-safe and does not require an MCP request body.
- A request body, if present, does not change successful liveness semantics.
- Unsupported methods on this path MUST return a method-related non-success
  status and MUST NOT be misclassified as not-found.
- Hosted success status: `200`.
- Hosted unsupported-method status: `405`.

### `GET /readyz`

Ready contract:
- Returns a success HTTP status.
- Returns a JSON readiness payload:

```json
{
  "status": "ready",
  "checks": {
    "configuration": "pass",
    "secrets": "pass"
  }
}
```

Not-ready contract:
- Returns a non-success HTTP status.
- Returns a JSON readiness payload with failing checks:

```json
{
  "status": "not_ready",
  "checks": {
    "configuration": "fail",
    "secrets": "fail"
  },
  "reason": {
    "code": "CONFIG_VALIDATION_ERROR",
    "message": "Required configuration is invalid or incomplete."
  }
}
```

Behavior rules:
- Readiness status is authoritative for whether the instance should receive
  traffic.
- Ready and not-ready outcomes MUST differ at both the HTTP status layer and
  the JSON body layer.
- Unsupported methods on this path MUST return a method-related non-success
  status.
- Hosted ready status: `200`.
- Hosted not-ready status: `503`.

### `/mcp`

Supported request contract:
- The route accepts only supported HTTP methods for MCP traffic.
- The route accepts only the documented JSON request format.
- Valid hosted MCP requests return a success HTTP status, JSON content type,
  and the standard MCP success envelope.

Malformed request contract:
- Syntactically invalid JSON returns a client-error HTTP status and a
  structured error payload.
- Structurally invalid MCP payloads return a client-error HTTP status and a
  structured error payload.
- Unsupported media types return the appropriate client-error HTTP status.
- Hosted success status: `200`.
- Hosted malformed-payload status: `400`.
- Hosted unsupported-media-type status: `415`.
- Hosted unsupported-method status: `405`.

Behavior rules:
- Error payloads MUST include normalized `code`, `message`, and `details`
  fields when a body is returned.
- Hosted MCP failures MUST remain sanitized and MUST NOT expose stack traces or
  secret values.

## Unsupported Hosted Requests

### Unsupported Methods

- Supported routes with unsupported methods MUST return the correct
  method-related non-success status.
- Unsupported-method responses MUST remain distinguishable from unknown-path
  responses.

### Unknown Paths

- Unsupported hosted paths MUST return the correct not-found HTTP status.
- When a response body is returned, it MUST use a machine-readable JSON error
  payload.
- Hosted unknown-path status: `404`.

## Content-Type Contract

- Hosted responses that include a body MUST use one consistent JSON response
  media type across `/healthz`, `/readyz`, `/mcp`, and JSON error responses.
- Content-type behavior for malformed or unsupported requests MUST remain
  deterministic for both local and deployed verification.

## Local and Hosted Parity

- The same request conditions MUST produce the same status classification and
  response-body class in local verification and deployed verification.
- Deployment hardening MUST NOT change the success body shape of existing MCP,
  liveness, or readiness responses beyond the status-code semantics defined
  above.

## Testable Assertions

- Contract tests can prove that hosted `/readyz` returns success only when the
  instance is ready.
- Contract tests can prove that malformed JSON, malformed MCP payloads,
  unsupported media types, unsupported methods, and unknown paths map to the
  expected status classes.
- Integration tests can prove that JSON content-type and structured error
  payload rules remain consistent across supported and unsupported hosted
  request scenarios.
- Deployed verification can prove that local route semantics match the hosted
  Cloud Run revision.
