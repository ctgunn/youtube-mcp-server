# Research: FND-005 Health, Logging, Error Model, Metrics

## Phase 0 Research Summary

### Decision: Keep `/healthz` and `/readyz` as lightweight machine-readable operational endpoints
Rationale: Health and readiness checks are used by platform probes and operators and must remain deterministic, fast, and independent of MCP method routing complexity.
Alternatives considered:
- Route health checks through MCP method calls: rejected because it adds unnecessary protocol overhead and probe fragility.
- Merge liveness and readiness into a single endpoint: rejected because liveness and traffic-readiness are separate operational concerns.

### Decision: Implement request-scoped structured logging with stable required fields
Rationale: FND-005 and PRD observability requirements require request correlation and diagnosability for both MCP and operational endpoint traffic.
Alternatives considered:
- Log only failures: rejected because successful-path telemetry is needed for latency baselines and trace continuity.
- Free-form string logs: rejected because they are brittle for search, aggregation, and alerting.

### Decision: Preserve and enforce normalized error envelope shape `code/message/details` on all client-facing error paths
Rationale: Deterministic error contracts improve client integration resilience and satisfy contract-first principles.
Alternatives considered:
- Allow per-handler custom error payloads: rejected because it fragments the contract and complicates client handling.
- Return raw exception messages: rejected because this risks leaking internals and unstable semantics.

### Decision: Capture core metrics as request counters and latency distributions with endpoint/tool dimensions
Rationale: This directly satisfies the acceptance criteria for counts and p50/p95 latency visibility while keeping metrics narrowly scoped.
Alternatives considered:
- Track only aggregate server-wide counts: rejected because endpoint/tool breakdown is needed for actionable troubleshooting.
- Emit metrics without error/success outcome segmentation: rejected because operators need outcome split for reliability monitoring.

### Decision: Generate/propagate request IDs for correlation across logs, errors, and metrics
Rationale: Consistent request identity is required for traceability when clients omit IDs and for rapid failure triage.
Alternatives considered:
- Require client-provided request IDs only: rejected because traffic can arrive without IDs.
- Generate IDs only for MCP endpoints: rejected because operational endpoints also require traceability.

## Dependencies and Integration Patterns

- Dependency: Existing transport and method routing from FND-001/FND-003/FND-004.
  - Pattern: Add observability hooks at transport boundary so all paths (`/healthz`, `/readyz`, `/mcp`, invalid paths) are covered uniformly.
- Dependency: Existing envelope and error mapper behavior.
  - Pattern: Preserve success envelope and enforce normalized error fields without breaking existing contract tests.
- Integration target: Cloud Run operational observability requirements in PRD.
  - Pattern: Emit structured logs and metrics with stable machine-readable keys suited to centralized log/metric backends.

## Red-Green-Refactor Plan

### Red
- Add failing contract tests for health/readiness response expectations and normalized error shape consistency.
- Add failing integration tests validating structured log events with request ID, path/tool, status, and latency.
- Add failing integration/unit tests validating metrics for request totals, outcome counts, and latency percentile-ready distribution data.

### Green
- Implement transport-level instrumentation for request context, structured logging, and metric recording.
- Implement request ID generation/propagation for all request paths.
- Implement or harden normalized error envelope behavior across all error paths.
- Ensure health/readiness endpoints satisfy expected status behavior and remain observable.

### Refactor
- Consolidate instrumentation helpers (request context extraction, timing capture, status/outcome mapping).
- Reduce duplicated logging/metric emission logic across endpoint branches.
- Re-run full regression suite to verify contract compatibility and behavior stability.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. Technical decisions required for planning are resolved for FND-005.
