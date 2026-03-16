# Research: FND-010 MCP Protocol Contract Alignment

## Phase 0 Research Summary

### Decision: Replace the legacy `success/data/meta/error` wrapper with MCP-native success and error payloads across all covered MCP flows
Rationale: The current code in `src/mcp_server/protocol/envelope.py` and
`src/mcp_server/protocol/methods.py` still returns a server-specific envelope
that contradicts the feature goal, FND-010 acceptance criteria, and the need
for downstream MCP clients to treat the service as a true MCP server. The
contract migration must therefore be explicit and complete for initialize,
tool discovery, tool invocation, malformed requests, and unsupported methods.
Alternatives considered:
- Keep the wrapper and add MCP-like fields inside `data`: rejected because it
  would preserve the non-standard boundary clients must special-case.
- Defer the wrapper change until after FND-011: rejected because FND-011
  depends on FND-010 and assumes protocol-native behavior already exists.

### Decision: Keep the FND-009 hosted streamable HTTP transport surface and change only the protocol payloads and lifecycle semantics in this slice
Rationale: FND-009 already established the single `/mcp` endpoint, session
headers, SSE behavior, and hosted request negotiation. FND-010 should migrate
the payload contract beneath that transport rather than reopen transport design.
This keeps scope bounded and makes test failures easier to interpret.
Alternatives considered:
- Merge transport and protocol changes into one new contract layer: rejected
  because transport behavior is already covered in FND-009 and would create
  avoidable regression risk.
- Introduce a second endpoint for MCP-native traffic: rejected because the PRD
  and prior slices center the design on one hosted MCP endpoint.

### Decision: Treat JSON-RPC request validation and MCP lifecycle rules as the first protocol boundary to enforce
Rationale: The current router accepts a minimal payload shape but does not
fully separate protocol validation from tool dispatch semantics. FND-010 must
make it clear which failures happen before routing, which failures map to
method-level protocol errors, and which failures originate from tool execution.
That separation is required for deterministic client behavior and stable
contract tests.
Alternatives considered:
- Focus only on output-shape migration: rejected because lifecycle and failure
  behavior would remain ambiguous.
- Push all validation down into tool dispatch: rejected because malformed or
  unsupported protocol requests must fail before tool-level logic runs.

### Decision: Preserve baseline tool availability while remapping tool discovery and invocation into MCP-native result structures
Rationale: The feature does not add or remove tools, but it changes how clients
discover and consume them. Baseline tools must continue working so FND-010
proves the protocol migration without masking regressions behind tool churn.
Alternatives considered:
- Limit the migration to `initialize` only: rejected because acceptance
  criteria require initialize, list, call, and unsupported-method handling.
- Redesign full tool metadata richness now: rejected because FND-011 is the
  slice reserved for tool metadata expansion and invocation result alignment.

### Decision: Use stable protocol error categories with sanitized details and map the current internal failures into those categories consistently
Rationale: Current tests already verify sanitized errors and a small set of
error codes such as `INVALID_ARGUMENT`, `RESOURCE_NOT_FOUND`, and
`INTERNAL_ERROR`. FND-010 should preserve the security posture while expressing
those failures through MCP-native error payloads and documented mapping rules.
Alternatives considered:
- Return raw exceptions for debugging: rejected because it violates the
  constitution’s security and observability constraints.
- Keep transport-level HTTP status codes as the primary error contract:
  rejected because MCP clients need stable protocol-level errors in the body.

### Decision: Rewrite existing contract, integration, and unit tests from wrapper assertions to protocol-native assertions before implementation
Rationale: The current suite, including `tests/unit/test_envelope_contract.py`
and `tests/contract/test_mcp_transport_contract.py`, codifies the legacy
wrapper. FND-010 must start by making those expectations fail so the migration
is driven by visible contract changes rather than by ad hoc code edits.
Alternatives considered:
- Add a second set of tests while leaving the old ones in place: rejected
  because the old suite would continue to defend the behavior this feature is
  meant to remove.
- Implement first and update tests later: rejected by the constitution’s
  mandatory Red-Green-Refactor workflow.

## Dependencies and Integration Patterns

- Dependency: Existing request routing in `src/mcp_server/protocol/methods.py`.
  - Pattern: Replace wrapper-oriented routing helpers with protocol-native
    request validation, result shaping, and error mapping while preserving the
    current method entrypoints.
- Dependency: Existing hosted entrypoint in `src/mcp_server/cloud_run_entrypoint.py`.
  - Pattern: Keep session, Accept-header, and streaming behavior from FND-009,
    but ensure hosted JSON and SSE payloads carry MCP-native protocol bodies.
- Dependency: Existing baseline tools in `src/mcp_server/tools/dispatcher.py`.
  - Pattern: Reuse the dispatcher and current tool handlers, changing only the
    invocation boundary contract.
- Integration target: Local and Cloud Run verification flows.
  - Pattern: Run the same initialize, list, call, malformed request, and
    unsupported-method scenarios against both environments and compare results.

## Red-Green-Refactor Plan

### Red
- Replace wrapper-based contract assertions with failing tests for:
  - initialize success payload shape
  - tool discovery result shape
  - tool invocation result shape
  - malformed request validation failures
  - unsupported-method failures
  - tool execution error mapping
- Add failing integration tests for:
  - initialize -> list -> call flow using MCP-native payloads
  - hosted and local parity for success and failure cases
  - session-aware hosted behavior carrying protocol-native responses over JSON
    and SSE
- Add failing unit tests for protocol request validation, result construction,
  error sanitization, and legacy-wrapper removal.

### Green
- Introduce the minimum protocol result and error builders required to satisfy
  MCP-native response expectations for initialize, list, and call flows.
- Update method routing so unsupported methods, invalid parameters, and tool
  failures map to stable MCP-native errors.
- Update hosted request handling to preserve current transport behavior while
  returning MCP-native payloads for JSON responses and streamed tool results.
- Keep baseline tools and health/readiness routes working without changing the
  deployment entrypoint or Cloud Run verification flow shape.

### Refactor
- Remove obsolete wrapper-specific helpers and duplicated response shaping
  logic.
- Consolidate protocol validation and error mapping behind shared helpers so
  local and hosted entrypoints cannot drift.
- Re-run the full regression suite to confirm transport, observability,
  readiness, and deployment verification continue to pass after the contract
  migration.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The repository state, FND-009
artifacts, constitution, and FND-010 spec provide enough context to resolve the
technical planning decisions for this feature.
