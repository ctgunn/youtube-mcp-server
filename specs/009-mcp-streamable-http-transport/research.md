# Research: FND-009 MCP Streamable HTTP Transport

## Phase 0 Research Summary

### Decision: Target the MCP Streamable HTTP transport defined in the official MCP specification version `2025-11-25`
Rationale: The current feature is explicitly about hosted transport
compatibility for modern MCP consumers. The official MCP transport
specification defines the required single-endpoint `GET` and `POST` behavior,
SSE streaming rules, optional resumability, session headers, and protocol
version header handling. Planning against the current official transport
contract avoids inventing a server-specific transport shape that would have to
be undone in FND-010 and FND-013.
Alternatives considered:
- Target the older `2025-03-26` transport revision: rejected because the latest
  official transport contract adds explicit security and session-management
  expectations that better match the PRD hosted-consumer goals.
- Keep the current custom `POST /mcp` request/response behavior and label it
  "streamable": rejected because it would not satisfy the official transport
  contract or the feature acceptance criteria.

### Decision: Keep one hosted MCP endpoint and add streamable `GET` plus `POST` semantics on `/mcp`
Rationale: The MCP transport specification requires a single MCP endpoint that
supports both `GET` and `POST`. The current service already exposes `/mcp`, so
retaining that endpoint minimizes deployment and client onboarding churn while
allowing the hosted entrypoint to evolve in place.
Alternatives considered:
- Introduce a second streaming endpoint alongside `/mcp`: rejected because it
  violates the single-endpoint transport model and would create migration debt.
- Replace `/mcp` with a new path and deprecate the old route immediately:
  rejected because it adds avoidable rollout complexity without user value.

### Decision: Use SSE as the streaming mechanism for hosted response streams and server-driven events
Rationale: The official transport contract allows a JSON response or an
`text/event-stream` response for `POST` requests carrying JSON-RPC requests,
and allows optional `GET` SSE streams for server-driven messages. SSE matches
the specification and can be introduced in the current Python hosted runtime
without requiring a full runtime migration in this slice.
Alternatives considered:
- Block on a runtime migration before adding any streaming support: rejected
  because FND-012 exists specifically to improve the runtime after transport
  semantics are established.
- Return only one-shot JSON responses from `POST`: rejected because the feature
  requires streamed responses and server-driven event support where the
  transport contract calls for it.

### Decision: Introduce in-memory session and stream state now, while keeping session termination and deeper auth hardening bounded
Rationale: The transport specification allows servers to assign a session ID at
initialization time and requires subsequent requests to carry it when the
server uses session management. FND-009 needs session-aware hosted behavior to
support concurrent streams, stream ownership, and resumability boundaries. This
can be handled with in-memory runtime state, which matches the project’s
foundation architecture and keeps scope contained.
Alternatives considered:
- Make the transport fully stateless: rejected because concurrent stream
  isolation, session headers, and resumability become ambiguous without some
  per-session state.
- Add persistent backing storage for sessions: rejected because the current
  foundation slices use in-memory state only and the feature does not require
  cross-instance session durability.

### Decision: Treat resumability as transport-compatible, optional server behavior with explicit event IDs and `Last-Event-ID` handling
Rationale: The official transport spec says servers may make streams resumable
by attaching unique SSE event IDs and accepting `Last-Event-ID` on reconnect.
Planning for resumability now avoids painting the transport into a corner, but
the implementation can remain minimal by limiting replay to in-memory
per-session/per-stream buffers and clearly documenting best-effort behavior.
Alternatives considered:
- Omit event IDs entirely: rejected because it would make reconnection behavior
  under-specified and weaken compatibility with streamable HTTP clients.
- Promise durable replay across process restarts: rejected because current
  runtime state is intentionally in-memory only.

### Decision: Preserve current health/readiness behavior and defer full protocol-native payload alignment to FND-010
Rationale: FND-009 is about transport semantics. The current server still uses
custom MCP-like envelopes and method routing; FND-010 is the slice dedicated to
native MCP protocol alignment. The transport plan should therefore wrap the
existing request lifecycle in streamable HTTP semantics without expanding scope
into a full response-model rewrite.
Alternatives considered:
- Combine transport migration and payload-contract migration in one slice:
  rejected because it would materially widen scope and obscure test failure
  causes.
- Freeze all transport changes until protocol-native payloads exist: rejected
  because FND-010 explicitly depends on FND-009.

### Decision: Add transport-level request validation for `Accept`, protocol version, and session headers, and carry forward origin validation as a required transport concern
Rationale: The official transport contract requires client `Accept` headers for
`GET` and `POST`, defines `MCP-Protocol-Version` behavior, and requires origin
validation to mitigate DNS rebinding. These are transport-layer concerns and
must be modeled in the plan so FND-009 produces a standards-aligned boundary
instead of a raw SSE wrapper.
Alternatives considered:
- Ignore header validation until the later security slice: rejected because the
  transport spec already makes some of these behaviors normative.
- Validate only JSON body shape and not transport headers: rejected because
  clients rely on header-level negotiation to determine supported behaviors.

## Dependencies and Integration Patterns

- Dependency: Existing hosted entrypoint in `cloud_run_entrypoint.py`.
  - Pattern: Extend the entrypoint from one-shot JSON responses to dual-mode
    JSON-or-SSE transport behavior while keeping `/health` and `/ready`
    unchanged.
- Dependency: Existing MCP request router in `transport/http.py` and
  `protocol/methods.py`.
  - Pattern: Reuse current request routing behind a new streamable transport
    adapter so request lifecycle behavior remains testable while transport
    semantics evolve first.
- Dependency: Existing hosted deployment flow from FND-008.
  - Pattern: Preserve the same Cloud Run entrypoint path and verification
    workflow, then extend verification to cover `GET`, `POST`, session, and
    stream behavior.
- Integration target: OpenAI Agent Builder and other hosted MCP clients.
  - Pattern: Align hosted transport negotiation, header handling, and SSE
    behavior with the official MCP streamable HTTP contract.

## Red-Green-Refactor Plan

### Red
- Add failing contract tests for:
  - `POST /mcp` Accept-header negotiation and JSON-vs-SSE response selection
  - `GET /mcp` SSE stream negotiation, including `405` when the stream is not
    offered for a given condition
  - session header issuance at initialization and required reuse on subsequent
    requests when sessions are active
  - protocol-version and invalid-session failures
- Add failing integration tests for:
  - streamed response delivery over SSE for valid MCP requests
  - server-driven event delivery on an active `GET` stream
  - concurrent session isolation and non-broadcast delivery
  - reconnect behavior using `Last-Event-ID`
- Add failing unit tests for session-state helpers, stream-event buffering,
  event ordering, Accept/header validation, and hosted transport
  classification.

### Green
- Add the minimum hosted session registry and stream-state helpers required to
  support one active session lifecycle, concurrent stream isolation, and
  best-effort reconnection.
- Update the hosted MCP entrypoint so `POST /mcp` can return either JSON or SSE
  according to the transport contract and `GET /mcp` can establish an SSE
  stream.
- Add minimal validation for `Accept`, `MCP-Protocol-Version`,
  `MCP-Session-Id`, and origin headers at the hosted transport boundary.
- Preserve current health/readiness behavior and current request router behavior
  behind the new transport surface.

### Refactor
- Consolidate session lookup, event formatting, and stream lifecycle management
  into shared transport helpers rather than per-request branching.
- Remove duplicated hosted header-validation logic across `GET`, `POST`, and
  reconnect flows.
- Re-run full regression coverage to confirm initialize, tools/list, tools/call,
  health, readiness, logging, and deployment verification remain compatible
  under the new transport boundary.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. Technical planning decisions for
FND-009 are resolved from the current repository state, constitution, and the
official MCP transport specification.
