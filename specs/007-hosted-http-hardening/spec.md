# Feature Specification: FND-007 Hosted Probe Semantics + HTTP Hardening

**Feature Branch**: `007-hosted-http-hardening`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "I need you to read the requirements/PRD.md document to get an overview of the project. Then, I need you to work on the requirements for FND-007 as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trust Hosted Readiness Signals (Priority: P1)

As an operator, I can rely on the hosted readiness endpoint to use transport-level success and failure semantics that accurately reflect whether the instance is ready to receive traffic.

**Why this priority**: Incorrect readiness semantics can cause unhealthy revisions to appear usable, which undermines deployment safety and platform probe behavior.

**Independent Test**: Can be fully tested by calling the hosted readiness endpoint in both ready and not-ready states and verifying that HTTP status and machine-readable body stay aligned with the actual service state.

**Acceptance Scenarios**:

1. **Given** a hosted instance with valid startup checks, **When** an operator or platform probe calls `/readyz`, **Then** the endpoint returns a success HTTP status and a machine-readable ready payload.
2. **Given** a hosted instance with failed startup checks, **When** an operator or platform probe calls `/readyz`, **Then** the endpoint returns a non-success HTTP status and a machine-readable not-ready payload that identifies the failing check class.
3. **Given** a hosted instance under normal operation, **When** an operator or platform probe calls `/healthz`, **Then** the endpoint returns a success HTTP status with a lightweight liveness payload.

---

### User Story 2 - Get Predictable Hosted MCP Route Behavior (Priority: P1)

As an MCP client integrator, I can send requests to the hosted MCP route and receive consistent content-type handling, status codes, and response envelopes so client behavior is deterministic.

**Why this priority**: The MCP endpoint is the primary product surface, so ambiguous hosted HTTP behavior would create avoidable client failures and support burden.

**Independent Test**: Can be fully tested by sending valid and malformed requests to `/mcp` and confirming that supported requests succeed while unsupported methods, bodies, or media types fail with stable transport semantics and structured errors.

**Acceptance Scenarios**:

1. **Given** a valid hosted MCP request, **When** a client sends it to `/mcp`, **Then** the service returns the expected success HTTP status, expected content type, and a standard success envelope.
2. **Given** a malformed hosted MCP request body, **When** a client sends it to `/mcp`, **Then** the service returns a client-error HTTP status with a structured error payload.
3. **Given** a request to `/mcp` that uses an unsupported content type or unsupported HTTP method, **When** the service receives it, **Then** it rejects the request with the correct transport-level status and does not present it as a protocol success.

---

### User Story 3 - Detect Unsupported Hosted Routes Quickly (Priority: P2)

As an operator or client integrator, I can distinguish unsupported hosted paths from valid service routes so misrouted traffic can be diagnosed without inspecting source code or logs first.

**Why this priority**: Clear behavior for unknown paths reduces confusion during rollout, smoke testing, and client onboarding, but it is secondary to the correctness of supported probes and MCP traffic.

**Independent Test**: Can be fully tested by calling unknown paths and unsupported route variations against the hosted service and confirming they return the correct not-found or method-related status behavior.

**Acceptance Scenarios**:

1. **Given** a request to an unsupported hosted path, **When** the service receives it, **Then** it returns the correct not-found HTTP status and a machine-readable error payload when the response body includes error details.
2. **Given** a request that uses a supported path with an unsupported HTTP method, **When** the service receives it, **Then** it returns the correct method-related HTTP status without implying the route itself is missing.

### Edge Cases

- What happens when `/readyz` is called during a transient not-ready startup window immediately after a new revision begins serving?
- How does the hosted surface respond when a request body is syntactically invalid and cannot be interpreted as a structured MCP request?
- What happens when a client sends a well-formed request body to the wrong hosted path?
- How does the service respond when an operator calls `/healthz` or `/readyz` with an unexpected content type or request body?
- What happens when the service can produce a machine-readable error body but the route semantics require a non-success HTTP status?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red:
  - Add failing contract tests for hosted `/readyz` that prove ready and not-ready states use different HTTP status classes while preserving machine-readable readiness details.
  - Add failing contract tests for `/healthz`, `/readyz`, and `/mcp` that prove response content-type and envelope behavior are consistent for their supported request shapes.
  - Add failing contract and integration tests for malformed hosted requests, unsupported media types, unsupported HTTP methods, and unknown paths.
- Green:
  - Define the hosted HTTP rules for liveness, readiness, MCP requests, and unsupported routes so each path returns the intended status code and machine-readable body.
  - Implement the smallest set of transport behavior changes needed to make probe semantics and hosted error handling deterministic.
  - Ensure hosted request validation failures and route failures produce structured error payloads wherever the route returns a body.
- Refactor:
  - Consolidate duplicated hosted response-shaping and status-selection logic so probe routes and MCP routes follow one consistent decision model.
  - Tighten regression coverage around route classification, malformed request handling, and transport-level error mapping.
  - Remove any response-shaping inconsistencies that could cause hosted and local test behavior to diverge.
- Required test levels: unit, contract, integration, end-to-end.
- Pull request evidence expectations:
  - Passing automated tests covering ready, not-ready, malformed, unsupported-method, unsupported-content-type, and unknown-path scenarios.
  - Captured hosted verification evidence showing `/healthz`, `/readyz`, and `/mcp` behavior against a deployed revision.
  - Reviewer-visible mapping of each functional requirement to at least one automated test.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST return a success HTTP status from hosted `/healthz` when the service process is alive enough to answer liveness checks.
- **FR-002**: System MUST return a success HTTP status from hosted `/readyz` only when required startup validation checks have passed.
- **FR-003**: System MUST return a non-success HTTP status from hosted `/readyz` whenever the instance is not ready to serve traffic.
- **FR-004**: System MUST include a machine-readable readiness body on hosted `/readyz` responses for both ready and not-ready states.
- **FR-005**: System MUST identify which readiness check categories are passing or failing when hosted `/readyz` reports a not-ready state.
- **FR-006**: System MUST preserve a lightweight machine-readable liveness body for hosted `/healthz`.
- **FR-007**: System MUST apply one consistent response media type policy across hosted `/healthz`, `/readyz`, and `/mcp` so operators and clients can predict how successful and failed responses are encoded.
- **FR-008**: System MUST accept supported hosted MCP requests at `/mcp` only when the request uses the expected transport shape and supported media type.
- **FR-009**: System MUST return the standard MCP success envelope for valid hosted `/mcp` requests.
- **FR-010**: System MUST reject malformed hosted `/mcp` requests with a client-error HTTP status and a structured error payload that identifies the request problem without exposing internal stack traces.
- **FR-011**: System MUST reject unsupported media types on hosted routes with the correct client-error HTTP status.
- **FR-012**: System MUST reject unsupported HTTP methods on hosted `/healthz`, `/readyz`, and `/mcp` with the correct method-related HTTP status.
- **FR-013**: System MUST return the correct not-found HTTP status for unsupported hosted paths.
- **FR-014**: System MUST return a machine-readable error payload for unsupported hosted requests whenever the route returns a response body.
- **FR-015**: System MUST keep hosted transport behavior consistent between local verification and deployed verification for the same request conditions.
- **FR-016**: System MUST ensure hosted probe and route semantics are documented clearly enough for operators and MCP client integrators to know which statuses indicate retryable readiness issues, client request issues, or unsupported routes.

### Key Entities *(include if feature involves data)*

- **Hosted Route Contract**: The externally visible behavior for a hosted path, including allowed methods, expected request shape, response status classes, and body rules.
- **Readiness Check Result**: A machine-readable summary of whether each readiness check category passed or failed for the current instance.
- **Hosted Error Payload**: The structured client-visible error body returned for malformed, unsupported, or unknown hosted requests.
- **Probe Outcome**: The transport-level result observed by a platform probe or operator when checking liveness or readiness.

### Dependencies

- FND-005 health, logging, error model, and metrics behavior must already exist so this feature can harden the hosted surface without redefining foundational payloads.
- FND-006 hosted deployment verification must already exist so the hardened HTTP semantics can be validated against a deployed revision.
- MCP initialize, tool discovery, and baseline tool invocation behavior from earlier foundation work must remain compatible with the hardened hosted transport rules.

### Assumptions

- `/healthz` remains a lightweight liveness route and is not repurposed to expose deep dependency validation.
- `/readyz` remains the authoritative hosted signal for whether a revision should receive traffic.
- A structured error payload is required for client-facing hosted failures when the route returns a body, but an empty-body response remains acceptable for statuses where no body is expected.
- Supported hosted routes for this slice are limited to `/healthz`, `/readyz`, and `/mcp`.
- Operators and client integrators need deterministic status semantics more than expanded payload detail in this phase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of hosted not-ready verification runs observe a non-success HTTP status from `/readyz`.
- **SC-002**: 100% of hosted ready verification runs observe a success HTTP status from `/readyz` and a machine-readable body that reports ready state.
- **SC-003**: At least 95% of malformed or unsupported hosted request tests are diagnosed correctly by reviewers on first inspection using only the returned HTTP status and response body.
- **SC-004**: 100% of supported hosted MCP smoke requests return the documented success envelope and expected response media type in both local and deployed verification.
- **SC-005**: 100% of unknown-path verification checks return the documented not-found status without being misclassified as MCP or probe successes.
