# Quickstart: FND-004 Config + Secrets + Startup Validation

## Objective
Implement centralized configuration and secret validation that fails fast on
invalid startup input and drives accurate readiness status for traffic gating.

## Prerequisites
- Python 3.11+
- Feature branch: `004-config-secrets-startup-validation`
- Existing FND-001 through FND-003 foundations available

## Red Phase (write failing tests first)

1. Add failing unit tests for:
   - Missing required non-secret config keys.
   - Blank and malformed required config values.
   - Unsupported `MCP_ENVIRONMENT` profile values.
   - Secret redaction in validation errors.
2. Add failing integration tests for:
   - Startup refusal when required config/secret settings are invalid.
   - Successful startup when profile requirements are fully satisfied.
3. Add failing contract tests for:
   - `GET /readyz` returning `not_ready` with non-sensitive reason when validation fails.
   - `GET /readyz` returning `ready` only after successful validation.
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Introduce centralized configuration requirement definitions.
2. Add startup validation flow to block boot on invalid required settings.
3. Add deterministic profile rules for `dev`, `staging`, and `prod`.
4. Add readiness evaluation based on latest validation state.
5. Ensure all validation errors remain structured and non-sensitive.
6. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate shared validation and error formatting helpers.
2. Simplify profile requirement mapping for readability and maintainability.
3. Eliminate duplicated test setup fixtures for config matrices.
4. Re-run full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Validation Flow

1. Start service with a complete valid config set for each supported profile.
2. Verify startup succeeds and readiness reports `ready`.
3. Remove or corrupt one required setting and restart.
4. Verify startup fails fast or readiness reports `not_ready` with non-sensitive reason.
5. Inspect logs and confirm no secret values are emitted.

Success criteria:
- Invalid required startup config is always rejected.
- Readiness reflects config/secret validity accurately.
- Error payloads remain structured and safe.
- Existing MCP transport and baseline tool behavior remain stable when config is valid.

## Implementation Execution Notes (2026-03-03)

- Red phase completed by adding failing tests for startup validation, profile matrix validation, readiness contract behavior, and secret-redaction checks.
- Green phase completed by implementing centralized runtime config validation, strict profile handling, startup fail-fast behavior, and `/healthz` + `/readyz` transport paths.
- Refactor phase completed by consolidating validation and readiness helpers in `src/mcp_server/config.py` and `src/mcp_server/health.py` and keeping envelope sanitization centralized.

## Validation Evidence (2026-03-03)

- Unit suite: `python3 -m unittest discover -s tests/unit -p 'test_*.py'` -> 38 passed
- Integration suite: `python3 -m unittest discover -s tests/integration -p 'test_*.py'` -> 15 passed
- Contract suite: `python3 -m unittest discover -s tests/contract -p 'test_*.py'` -> 11 passed
- Full regression: `python3 -m unittest discover -s tests -p 'test_*.py'` -> 64 passed
