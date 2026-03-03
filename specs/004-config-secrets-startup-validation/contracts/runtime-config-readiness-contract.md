# Runtime Config and Readiness Contract: FND-004

## Purpose
Define external runtime behavior for startup configuration validation,
secret-backed setting requirements, and readiness reporting.

## Scope
- Startup acceptance/rejection behavior based on config validity.
- Supported runtime environment profiles.
- Readiness endpoint behavior for config/secret validation state.
- Error-shape and redaction expectations.

## Runtime Profile Contract

Supported profile values:
- `dev`
- `staging`
- `prod`

Contract rules:
- Unsupported profile values MUST fail startup validation.
- Profile-specific required settings MUST be deterministic and documented.

## Startup Validation Contract

Startup succeeds only when all required non-secret and secret-backed
requirements for the active profile are valid and available.

Failure behavior contract:
- Startup MUST fail before the instance is considered ready for traffic.
- Validation failure output MUST identify failing keys and rule categories.
- Validation failure output MUST NOT include raw secret values.

Failure example (shape only):

```json
{
  "code": "CONFIG_VALIDATION_ERROR",
  "message": "Required runtime configuration is invalid.",
  "details": {
    "profile": "staging",
    "failures": [
      { "key": "MCP_ENVIRONMENT", "reason": "unsupported value" },
      { "key": "YOUTUBE_API_KEY", "reason": "missing required secret" }
    ]
  }
}
```

## Readiness Endpoint Contract (`GET /readyz`)

Success example:

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
- `status=ready` only after successful startup validation.
- `status=not_ready` when required config or required secret checks fail.
- `reason` content MUST remain non-sensitive and must not expose secret values.

## Observability and Security Contract

- Configuration/readiness validation logs MUST be structured and include a
  correlation identifier when available.
- Logs and client-facing error payloads MUST NOT contain secret values.
- Error shape MUST remain machine-readable with `code`, `message`, and optional
  `details`.

## Test Coverage Mapping

- Unit tests: validation rules (missing/blank/malformed/unsupported profile),
  secret redaction guarantees.
- Integration tests: startup pass/fail behavior under profile-specific config sets.
- Contract tests: `/readyz` success and not-ready response shape and redaction.
- Regression tests: existing MCP request/response behavior remains unchanged when
  startup validation is satisfied.
