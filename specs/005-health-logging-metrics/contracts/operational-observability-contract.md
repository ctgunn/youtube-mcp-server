# Operational Health, Error, Logging, and Metrics Contract: FND-005

## Purpose
Define external and operator-visible behavior for liveness/readiness checks,
normalized error envelopes, request correlation, structured logs, and core metrics.

## Scope
- `GET /healthz` liveness contract
- `GET /readyz` readiness contract
- MCP and non-MCP error payload normalization
- Structured log field contract for handled requests
- Core metric dimensions and outcome/latency expectations

## Health Endpoint Contract (`GET /healthz`)

Success example:

```json
{
  "status": "ok"
}
```

Contract rules:
- Endpoint MUST be callable without MCP payload.
- Response MUST be machine-readable and indicate liveness health.
- Endpoint failures MUST still follow normalized error shape when applicable.

## Readiness Endpoint Contract (`GET /readyz`)

Ready example:

```json
{
  "status": "ready",
  "checks": {
    "configuration": "pass",
    "secrets": "pass"
  }
}
```

Not-ready example:

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

Contract rules:
- Readiness MUST represent startup validation state.
- Not-ready responses MUST include non-sensitive reason metadata.

## Error Model Contract

Error shape requirement:

```json
{
  "success": false,
  "data": null,
  "meta": { "requestId": "req-123" },
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "params must be an object",
    "details": null
  }
}
```

Contract rules:
- All client-visible error responses MUST include `error.code`, `error.message`, and `error.details`.
- `message` MUST be sanitized and MUST NOT expose stack traces or secret values.
- `requestId` in response metadata MUST match incoming request ID or generated correlation ID.

## Structured Logging Contract

Each handled request MUST emit structured log output with fields:
- `timestamp`
- `severity`
- `requestId`
- `path`
- `status`
- `latencyMs`

Conditional field:
- `toolName` for tool invocation requests.

Contract rules:
- Logs MUST support correlation across request lifecycle via `requestId`.
- Logs MUST exclude secret values and stack trace content in normal error paths.

## Core Metrics Contract

Minimum emitted metric dimensions:
- Request count by endpoint
- Success/error count by endpoint
- Request latency observations by endpoint
- Request latency observations by tool for `tools/call`

Contract rules:
- Metrics MUST support p50 and p95 latency reporting.
- Metrics MUST include both successful and failed requests.
- Metrics labels MUST use bounded values (endpoint classes and normalized tool identifiers).

## Test Coverage Mapping

- Unit tests: error envelope normalization and request ID propagation rules.
- Contract tests: `/healthz` and `/readyz` payload contracts plus error shape checks.
- Integration tests: structured log fields, request correlation behavior, and metrics emission for success/error paths.
- Regression tests: existing MCP initialize/list/call behavior remains compatible while observability is added.

## Implementation Notes (2026-03-05)

- Transport-level observability instrumentation was implemented to cover all
  handled endpoint classes (`/healthz`, `/readyz`, `/mcp`, and unknown paths).
- Generated request IDs now backfill MCP requests with missing `id` and are
  propagated into response metadata for correlation.
- Structured log events now include required fields plus `toolName` for
  `tools/call` requests.
- Metrics snapshot support includes endpoint success/error counts and
  percentile-ready latency summaries (`p50`, `p95`) by endpoint and tool.
