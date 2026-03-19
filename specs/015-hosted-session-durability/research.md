# Research: FND-015 Hosted MCP Session Durability

## Phase 0 Research Summary

### Decision: Replace process-local hosted session storage with a shared Redis-compatible session backend for hosted runtimes
Rationale: The current `StreamManager` stores sessions and stream events in process memory, which guarantees `session not found` failures whenever Cloud Run routes a follow-up request to a different instance or the original instance restarts. A Redis-compatible backend is the smallest shared-state mechanism that fits ephemeral session data, low-latency lookups, TTL cleanup, and Cloud Run multi-instance access without introducing a heavier relational or document model.
Alternatives considered:
- Keep process-local memory and depend on single-instance deployment or sticky routing: rejected because FND-015 explicitly forbids undocumented single-instance assumptions.
- Persist sessions in a relational or document database: rejected because session metadata and replay cursors are short-lived operational state, and a general-purpose database adds more complexity and latency than the feature needs.

### Decision: Store session identity, last activity, and replayable event metadata separately from per-instance runtime objects
Rationale: Durable continuation needs shared session truth that any instance can read, but not every runtime concern needs persistence. Separating durable session records and replayable event data from transient per-request objects keeps the design small while still allowing follow-up `GET` and `POST` flows to recover on another instance.
Alternatives considered:
- Serialize entire in-memory stream objects into shared storage: rejected because it carries too much process-specific state and makes reconnect logic harder to evolve.
- Persist only session IDs and rebuild everything else heuristically: rejected because reconnect and replay require more than bare identity to remain protocol-correct.

### Decision: Bound replay durability with explicit TTL and recent-history guarantees instead of indefinite event retention
Rationale: Hosted reconnect needs enough retained history to resume after normal network interruptions and instance changes, but indefinite event retention would increase operational cost and complexity for marginal value. A TTL-backed replay window gives clients a documented continuation boundary and gives operators a clear expiration model.
Alternatives considered:
- Infinite retention for all stream events: rejected because it adds unbounded growth for operational state that is only needed for short-lived continuation.
- No replay retention at all: rejected because it would force reconnects to behave like fresh sessions and would not satisfy the reconnect requirements in FND-015.

### Decision: Treat durable session backing-state availability as a hosted readiness requirement
Rationale: If the service is deployed in a topology that promises durable hosted sessions but the shared backend is unavailable, the service should not advertise readiness for durable MCP traffic. Exposing a ready service that cannot honor the feature contract would recreate the current fragility under a different failure mode.
Alternatives considered:
- Fall back silently to process-local memory when the shared store is unavailable: rejected because it reintroduces hidden single-instance behavior and makes operator diagnosis harder.
- Allow traffic while logging warnings only: rejected because the feature spec requires operators to know when a deployment is unsafe for durable sessions.

### Decision: Define the supported Cloud Run topology as multi-instance capable only when every instance uses the same shared session backend
Rationale: The product goal is hosted reliability under real Cloud Run routing and scaling, not merely same-instance success. The simplest contract is to support multi-instance routing when shared session state is configured and healthy, and to document any topology lacking that backend as unsupported for durable sessions.
Alternatives considered:
- Support only min-instances=1 or max-instances=1 deployments: rejected because it trades reliability for an operational workaround and does not satisfy the spirit of FND-015.
- Claim support for all Cloud Run topologies regardless of backing state: rejected because the implementation cannot guarantee continuity without shared state.

### Decision: Preserve existing MCP session headers and protocol flow while refining session-state failure categories
Rationale: Earlier slices already established the hosted MCP protocol shape, session header usage, and security flow. FND-015 should strengthen continuity beneath that contract, not redesign the transport. Stable session-state failures should remain distinct from tool and security failures, but the outward protocol model should stay familiar to existing clients.
Alternatives considered:
- Introduce a new session negotiation protocol or alternate endpoint: rejected because it expands scope and creates unnecessary client churn.
- Collapse all session failures into generic `RESOURCE_NOT_FOUND`: rejected because operators and clients need to distinguish expired or replay-unavailable sessions from malformed requests and ordinary tool failures.

### Decision: Validate durability through cross-instance tests that share the same session backend and through hosted verification that exercises reconnect paths
Rationale: Existing tests prove same-process session behavior only. FND-015 must prove that independent app instances can resume the same session when they share durable state, and that hosted verification captures both successful continuation and expected expiration behavior.
Alternatives considered:
- Limit coverage to unit tests around the session store adapter: rejected because the public failure mode appears at the hosted MCP boundary.
- Rely only on manual Cloud Run checks: rejected because the constitution requires integration and regression coverage for cross-component behavior.

## Dependencies and Integration Patterns

- Dependency: Existing hosted request flow in `src/mcp_server/cloud_run_entrypoint.py`.
  - Pattern: Keep initialize and follow-up request handling on `/mcp`, but replace direct process-local session validation with a durable session-store abstraction used by every instance.
- Dependency: Existing HTTP transport wrapper in `src/mcp_server/transport/http.py`.
  - Pattern: Continue to route MCP requests through the current transport while moving session lookup and replay behavior behind a store-aware session manager.
- Dependency: Existing runtime configuration and readiness flow in `src/mcp_server/config.py` and `src/mcp_server/health.py`.
  - Pattern: Add durable-session backend configuration and readiness gating through the same centralized startup and readiness mechanisms already used for hosted security and environment validation.
- Dependency: Existing deployment and hosted verification tooling in `src/mcp_server/deploy.py` and `scripts/verify_cloud_run_foundation.py`.
  - Pattern: Extend the current verification record with continuity and reconnect checks rather than creating a separate verification tool.
- Dependency: Existing unit, integration, and contract suites under `tests/`.
  - Pattern: Simulate two app instances sharing one durable backend so regression coverage proves cross-instance survival rather than local happy paths alone.

## Red-Green-Refactor Plan

### Red

- Add failing unit tests for durable session-store read/write semantics, expiry handling, and replay-window enforcement.
- Add failing integration tests that initialize on one app instance and continue on another instance sharing the same durable backend.
- Add failing contract tests for invalid-session, expired-session, and replay-unavailable outcomes that remain distinct from transport and security failures.
- Add failing readiness and deployment-verification checks proving hosted durability is blocked or flagged when the shared backend is unavailable or unsupported.

### Green

- Add the minimum shared session store abstraction, hosted configuration, readiness checks, and reconnect/replay behavior needed to satisfy those failing tests.
- Update hosted verification and documentation with one successful initialize-plus-continuation flow, one successful reconnect flow, and one expected failure for expired or unrecoverable replay state.

### Refactor

- Consolidate store access, session expiry logic, and replay lookup into one transport-facing session durability layer.
- Remove duplicate continuity decisions from the entrypoint, transport, and verification code paths.
- Re-run the full regression suite to confirm earlier MCP transport, security, and retrieval behavior stays intact.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The durable session strategy, supported topology, readiness posture, and reconnect boundary are all defined strongly enough to proceed into design and task planning.
