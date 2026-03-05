# Quickstart: FND-005 Health, Logging, Error Model, Metrics

## Objective
Implement operational observability foundations for liveness/readiness checks,
request-scoped structured logging, normalized client errors, and core request
metrics including latency percentile support.

## Prerequisites
- Python 3.11+
- Feature branch: `005-health-logging-metrics`
- Existing transport/protocol foundations from FND-001 through FND-004

## Red Phase (write failing tests first)

1. Add failing contract tests for:
   - `/healthz` and `/readyz` response status behavior.
   - Consistent error payload shape `code/message/details` on error responses.
2. Add failing integration tests for:
   - Structured logs containing `requestId`, `path`, `status`, `latencyMs`, and `toolName` for tool calls.
   - Request ID generation when missing from incoming payload.
3. Add failing unit/integration tests for:
   - Metric count increments by endpoint and outcome.
   - Latency observation capture suitable for p50/p95 calculations.
4. Run targeted suites and verify failing tests:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Add request instrumentation in transport handling so all endpoint paths are captured.
2. Add/propagate request ID context for logs, metrics, and error metadata.
3. Ensure normalized error envelope fields are present on all error responses.
4. Add structured logging output for request completion with required fields.
5. Add core metrics for request counts, outcomes, and latency observations.
6. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate duplicated request context extraction and endpoint classification helpers.
2. Normalize structured log and metric labeling logic for maintainability.
3. Re-run full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Validation Flow

1. Start the service with valid runtime configuration.
2. Call `/healthz` and `/readyz`; verify healthy/ready outputs and associated logs/metrics.
3. Send MCP requests for success and known failure paths.
4. Confirm responses preserve normalized error shape and response `requestId` correlation.
5. Inspect logs to verify required fields and tool attribution for `tools/call`.
6. Inspect metrics output to verify request counts and latency percentile inputs.

Success criteria:
- Health/readiness checks are accurate and fast.
- All errors are normalized and sanitized.
- Every handled request is traceable via request ID in logs and response metadata.
- Core request count/outcome/latency metrics are emitted for endpoint traffic.

## Implementation Execution Notes (2026-03-05)

- Added shared observability runtime in `src/mcp_server/observability.py`:
  request context extraction, request ID generation, structured event formatting,
  endpoint/tool metric counting, and latency percentile summaries.
- Integrated transport instrumentation in `src/mcp_server/transport/http.py` so
  `/healthz`, `/readyz`, `/mcp`, and unknown paths all emit logs and metrics.
- Added request ID fallback behavior for MCP payloads that omit `id`, and
  enforced response meta correlation for generated IDs.
- Added new test coverage in:
  - `tests/unit/test_request_context.py`
  - `tests/unit/test_metrics_state.py`
  - `tests/integration/test_request_observability.py`
  - `tests/contract/test_operational_observability_contract.py`
- Extended existing suites for request ID fallback, tool log field coverage, and
  normalized error field guarantees.

## Validation Evidence (2026-03-05)

- Unit suite: `python3 -m unittest discover -s tests/unit -p 'test_*.py'` -> 44 passed
- Integration suite: `python3 -m unittest discover -s tests/integration -p 'test_*.py'` -> 23 passed
- Contract suite: `python3 -m unittest discover -s tests/contract -p 'test_*.py'` -> 16 passed
- Full regression: `python3 -m unittest discover -s tests -p 'test_*.py'` -> 83 passed
