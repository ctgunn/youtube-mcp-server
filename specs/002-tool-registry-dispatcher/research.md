# Research: Tool Registry + Dispatcher (FND-002)

## Phase 0 Research Summary

### Decision: Keep a dedicated in-memory registry as the source of truth for tool definitions
Rationale: FND-002 scope is registration and dispatch lifecycle correctness, not persistence. In-memory state keeps design simple and supports deterministic test setup.
Alternatives considered:
- Persistent database-backed registry: rejected because it adds infrastructure outside foundation scope.
- Hard-coded tool map in router only: rejected because it violates transport-independence and extensibility requirements.

### Decision: Normalize tool names for uniqueness and lookup consistency
Rationale: Case-insensitive normalization avoids duplicate logical registrations and prevents ambiguous dispatch results.
Alternatives considered:
- Case-sensitive matching: rejected because it permits near-duplicate tools and inconsistent client behavior.
- Preserve raw input only: rejected because duplicate detection and lookup become unreliable.

### Decision: Validate invocation arguments before handler execution using declared input contracts
Rationale: Feature requirements mandate blocked execution on invalid input and structured validation errors.
Alternatives considered:
- Handler-only validation: rejected because behavior becomes inconsistent across tools.
- No validation in dispatcher: rejected because it violates FND-002 acceptance criteria.

### Decision: Return `RESOURCE_NOT_FOUND` for unknown tool dispatch attempts
Rationale: This is explicitly required in FND-002 and gives deterministic, client-actionable failure semantics.
Alternatives considered:
- Generic `INTERNAL_ERROR`: rejected because it masks caller errors.
- HTTP-only 404 without MCP error envelope: rejected because it breaks MCP response consistency.

### Decision: Preserve transport-layer independence via registry/dispatcher interface boundaries
Rationale: Developers must add tools without changing transport code. Registry and dispatcher boundaries isolate tool lifecycle concerns from request transport concerns.
Alternatives considered:
- Transport-layer direct handler wiring: rejected because every new tool would require transport edits.
- Single monolithic route function for registration and call logic: rejected because it increases coupling and regression risk.

## Red-Green-Refactor Execution Plan

### Red
- Add failing unit tests for:
  - required registration fields,
  - duplicate name rejection,
  - successful dispatch to registered handler,
  - input validation errors,
  - unknown tool mapping to `RESOURCE_NOT_FOUND`.
- Add/adjust integration tests for list and call flows against registered tools.
- Add/adjust contract tests for unknown-tool and validation error envelopes.

### Green
- Implement minimum registry lifecycle behavior for register/list/lookup.
- Implement dispatch path with pre-execution input validation.
- Map unknown tools and invalid inputs to structured MCP-safe errors.

### Refactor
- Extract shared normalization and validation helpers.
- Remove duplication between list and call lookup paths.
- Re-run full unit, integration, and contract suites for regression safety.

## Dependencies and Integration Patterns

- Dependency: FND-001 method routing and response envelope foundation.
  - Pattern: extend existing `tools/list` and `tools/call` flows without changing external request shape.
- Dependency: baseline tool definitions consumed by registry in FND-003.
  - Pattern: register baseline tools via registry API rather than transport-level branches.
- Dependency: centralized error model constraints from project constitution.
  - Pattern: always emit structured `code/message/details` errors and omit stack traces.

## Resolved Clarifications

No unresolved `NEEDS CLARIFICATION` items remain for FND-002 planning.
