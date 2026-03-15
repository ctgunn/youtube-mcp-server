# Research: FND-007 Hosted Probe Semantics + HTTP Hardening

## Phase 0 Research Summary

### Decision: Treat hosted HTTP status selection as a first-class contract at the entrypoint boundary
Rationale: The current in-memory transport returns payloads but does not model
transport-level status codes. FND-007 is specifically about hosted probe and
route semantics, so status selection must be defined where hosted requests are
translated into HTTP responses.
Alternatives considered:
- Encode HTTP status intent inside every payload helper: rejected because it
  couples route semantics to payload shape and spreads hosted behavior across
  unrelated modules.
- Leave status mapping implicit in the Cloud Run handler: rejected because the
  current entrypoint already hard-codes `200` for `/readyz` and lacks a shared
  decision model for error cases.

### Decision: Return non-success readiness status for not-ready hosted revisions
Rationale: Operators and Cloud Run probes need transport-level failure when the
instance is not ready for traffic. A machine-readable body should remain
available so the failing check categories are still diagnosable.
Alternatives considered:
- Keep `/readyz` at `200` and rely only on body contents: rejected because it
  weakens probe semantics and contradicts FND-007 acceptance criteria.
- Fail both `/healthz` and `/readyz` during startup validation issues: rejected
  because liveness and readiness serve different operational purposes.

### Decision: Use explicit client-error status classes for malformed or unsupported hosted requests
Rationale: MCP clients and operators need deterministic transport behavior.
Malformed JSON or malformed MCP request shapes should be treated as bad client
input, unsupported media types should be rejected clearly, unsupported methods
should be distinguished from missing routes, and unknown paths should remain
not-found.
Alternatives considered:
- Collapse all hosted request failures into one generic bad-request response:
  rejected because method, media type, and path errors have different operator
  and client remediation paths.
- Return success HTTP status with an internal error envelope for malformed
  requests: rejected because transport-level semantics would become misleading.

### Decision: Keep response bodies JSON and preserve normalized error payloads wherever a body is returned
Rationale: Existing MCP and non-MCP error behavior is already machine-readable.
FND-007 should tighten hosted semantics without fragmenting payload formats
across routes.
Alternatives considered:
- Use plain-text probe responses and JSON only for MCP: rejected because it
  would reduce consistency for hosted diagnostics.
- Introduce route-specific error body shapes: rejected because it increases
  client complexity without adding value.

### Decision: Preserve local-to-hosted parity by centralizing route classification and response mapping
Rationale: FND-007 requires hosted behavior to remain consistent between local
verification and deployed verification. Shared helpers for route classification,
status selection, and error mapping reduce the risk of test-only semantics that
drift from Cloud Run behavior.
Alternatives considered:
- Keep local `app.handle()` behavior separate from hosted entrypoint mapping:
  rejected because deployed semantics would be harder to prove through local
  automation.
- Reimplement hosted route semantics only in end-to-end verification scripts:
  rejected because contract behavior should live in the product, not in tests.

## Dependencies and Integration Patterns

- Dependency: Existing readiness payload contract from FND-005.
  - Pattern: Preserve the current ready and not-ready body shapes while adding
    explicit hosted status mapping for ready versus not-ready outcomes.
- Dependency: Existing MCP envelope and error normalization.
  - Pattern: Reuse the standard `code/message/details` error model for hosted
    request failures whenever a JSON body is returned.
- Dependency: Existing hosted entrypoint in `cloud_run_entrypoint.py`.
  - Pattern: Introduce shared route/status handling there or in a helper used by
    both the entrypoint and local verification paths.
- Integration target: Cloud Run liveness/readiness probing and operator smoke tests.
  - Pattern: Make `/healthz` probe-safe, `/readyz` readiness-authoritative, and
    `/mcp` deterministic for supported and unsupported requests.

## Red-Green-Refactor Plan

### Red
- Add failing contract tests that prove hosted `/readyz` returns success only
  when ready and returns non-success when not ready.
- Add failing contract and integration tests for unsupported HTTP methods,
  unsupported media types, malformed JSON bodies, malformed MCP payloads, and
  unknown hosted paths.
- Add failing tests that verify consistent JSON content-type and structured
  error payload behavior across `/healthz`, `/readyz`, `/mcp`, and unknown
  paths where a body is returned.

### Green
- Add the minimum shared route-classification and status-selection behavior
  needed to satisfy hosted readiness and error semantics.
- Add the minimum hosted request validation needed to distinguish malformed
  JSON, malformed MCP payloads, unsupported media types, unsupported methods,
  and unknown paths.
- Preserve existing MCP success behavior and current readiness/liveness body
  shapes while tightening hosted status behavior.

### Refactor
- Consolidate response-writing, content-type, and status-mapping logic into a
  shared helper path rather than duplicating per-method rules.
- Remove any branching that classifies the same hosted failure in multiple
  places.
- Re-run full regression coverage to confirm existing initialize, tools/list,
  tools/call, health, readiness, logging, and deployment verification behavior
  remains compatible.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. Technical planning decisions for
FND-007 are resolved within the current repository context and constitution.
