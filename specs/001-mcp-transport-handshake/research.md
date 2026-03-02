# Research: MCP Transport + Handshake (FND-001)

## Phase 0 Research Summary

### Decision: Use HTTP JSON request handling with explicit MCP method routing
Rationale: Cloud Run requires HTTP-first operation, and the feature scope only
needs initialize/list/invoke flow for MCP clients.
Alternatives considered:
- WebSocket-first transport: rejected for higher setup complexity in foundation.
- gRPC transport: rejected because it is outside MCP baseline requirements.

### Decision: Use Python 3.11 + FastAPI + Pydantic for transport and schema safety
Rationale: Matches project constitution default, provides straightforward request
validation and deterministic JSON response shaping.
Alternatives considered:
- Flask + marshmallow: rejected due to less integrated typed modeling workflow.
- Node.js runtime: rejected for cross-slice consistency with constitution.

### Decision: Contract tests and method unit tests are mandatory in Red phase
Rationale: Constitution mandates Red-Green-Refactor in planning and execution,
so failing tests must exist before implementation.
Alternatives considered:
- Integration-only tests: rejected because method-level error behavior would be
  underspecified and regressions harder to isolate.
- Manual validation only: rejected as non-repeatable and non-compliant.

### Decision: Standard MCP response envelope includes success/data/meta/error
Rationale: PRD and tool specs require stable structured responses and consistent
error shapes for agent clients.
Alternatives considered:
- Method-specific response shapes without envelope: rejected because it breaks
  consistency and increases client-side complexity.

### Decision: Return structured `RESOURCE_NOT_FOUND` for unknown tool invocation
Rationale: Required by feature seed for subsequent registry/dispatcher behavior,
and gives deterministic failure semantics to clients.
Alternatives considered:
- Generic `INTERNAL_ERROR`: rejected because it masks user-correctable errors.
- HTTP 404 without MCP envelope: rejected as protocol-inconsistent.

## Red-Green-Refactor Execution Plan

### Red
- Add failing contract tests for `initialize`, `tools/list`, and `tools/call`
  envelope behavior.
- Add failing unit tests for method validation and unknown-method/tool errors.

### Green
- Implement minimal HTTP entrypoint and method router.
- Implement minimal initialize/list/invoke handlers returning valid envelopes.
- Implement minimal error mapper producing `code/message/details`.

### Refactor
- Isolate protocol envelope builders and dispatcher mapping into small modules.
- Remove duplication in validation and error-path code.
- Re-run full test suite and preserve behavior.

## Dependencies and Integration Patterns

- Dependency: Cloud Run runtime model (single HTTP service endpoint).
  - Pattern: stateless request handling per call.
- Dependency: Future registry/dispatcher slice (FND-002).
  - Pattern: provide temporary in-memory stub registry contract in FND-001.
- Dependency: Observability slice (FND-005).
  - Pattern: include requestId/meta placeholders in response shape now.

## Resolved Clarifications

No unresolved `NEEDS CLARIFICATION` items remain for FND-001 planning.
