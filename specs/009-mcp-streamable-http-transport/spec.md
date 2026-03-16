# Feature Specification: FND-009 MCP Streamable HTTP Transport

**Feature Branch**: `009-mcp-streamable-http-transport`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Read requirements/PRD.md to get an overview of the project. Then begin working on the requirements for FND-009 as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Establish a Compliant Hosted MCP Session (Priority: P1)

As an MCP consumer, I can connect to the hosted MCP endpoint using the expected streamable HTTP session behavior so I can start a standards-aligned session without relying on a server-specific request pattern.

**Why this priority**: Hosted session establishment is the entrypoint for every downstream MCP interaction, so the feature has no user value unless modern MCP clients can connect successfully.

**Independent Test**: Can be fully tested by exercising the hosted MCP endpoint with the required session-establishment requests and verifying that the service accepts the expected request patterns and returns the documented session behavior for both success and failure cases.

**Acceptance Scenarios**:

1. **Given** a hosted server that is ready to accept MCP traffic, **When** an MCP consumer initiates a session using the required streamable HTTP request flow, **Then** the server accepts the session and returns the expected transport-level response for a valid MCP session start.
2. **Given** a hosted server that is ready to accept MCP traffic, **When** an MCP consumer sends a transport request that does not match the required session-establishment shape, **Then** the server rejects the request with a stable client-visible failure response.
3. **Given** a hosted server that is temporarily not ready to serve MCP traffic, **When** an MCP consumer attempts to establish a session, **Then** the server returns a response that makes the temporary inability to serve traffic clear without implying a successful MCP session.

---

### User Story 2 - Receive Streamed MCP Responses and Server-Driven Events (Priority: P1)

As an MCP consumer, I can receive streamed responses and server-driven events over the hosted MCP connection so I can interact with the server using transport behavior expected by modern MCP clients.

**Why this priority**: Stream delivery is the core difference between the current hosted behavior and the target transport; without it, the feature would not satisfy the PRD transport requirement.

**Independent Test**: Can be fully tested by opening a valid hosted MCP session, triggering MCP operations that produce streamed output or event traffic, and confirming that the consumer receives ordered, well-formed streamed messages until the stream ends or the session closes.

**Acceptance Scenarios**:

1. **Given** an active hosted MCP session, **When** the server produces a streamed MCP response, **Then** the consumer receives the response through the stream in the documented format and order.
2. **Given** an active hosted MCP session, **When** the server needs to emit a server-driven event required by the transport contract, **Then** the event is delivered on the active stream without requiring the consumer to poll for it separately.
3. **Given** a streamed session is interrupted or closed, **When** the consumer attempts to continue reading from that stream, **Then** the transport behavior makes the session end visible and does not silently report incomplete data as a successful full response.

---

### User Story 3 - Verify Hosted Transport Compatibility Before Client Rollout (Priority: P2)

As a platform integrator, I can follow documented local and hosted verification steps for the streamable HTTP transport so I can confirm compatibility with OpenAI Agent Builder and similar MCP consumers before relying on the server in production workflows.

**Why this priority**: Verification guidance is slightly lower priority than transport correctness itself, but rollout risk stays high if integrators cannot prove that local and hosted behavior match the documented contract.

**Independent Test**: Can be fully tested by following the documented verification flow in a local environment and against a hosted deployment and confirming that both environments produce the same user-visible transport behavior for the same valid and invalid requests.

**Acceptance Scenarios**:

1. **Given** a local server instance that supports the streamable HTTP transport, **When** an integrator follows the documented verification steps, **Then** the integrator can confirm successful session establishment, streamed delivery behavior, and expected failure behavior.
2. **Given** a hosted deployment that supports the streamable HTTP transport, **When** an integrator follows the documented hosted verification steps, **Then** the integrator can confirm the same core transport behaviors without relying on undocumented request conventions.
3. **Given** the transport contract changes in a way that affects client-visible behavior, **When** verification guidance is updated, **Then** the documentation reflects the new valid request flow, streamed behavior, and failure expectations in one place.

### Edge Cases

- What happens when a client opens a valid streamable HTTP session but no MCP messages are immediately available to send?
- How does the transport behave when a client uses a valid session flow but attempts an unsupported HTTP method for that stage of the interaction?
- What happens when a client reconnects after a network interruption during an active streamed response?
- How does the server signal that a stream has ended normally versus ended because the request or session became invalid?
- What happens when a hosted deployment is healthy enough to answer probe requests but cannot maintain a valid streamed MCP session?
- How does the transport behave when multiple MCP consumers connect concurrently to the same hosted endpoint?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red:
  - Add failing contract tests that define the required session-establishment behavior for valid and invalid streamable HTTP `GET` and `POST` requests.
  - Add failing integration tests that prove streamed responses and required server-driven events are delivered through the hosted MCP transport rather than a request/response-only path.
  - Add failing end-to-end verification tests that compare local and hosted transport behavior for successful sessions, interrupted streams, and malformed client requests.
- Green:
  - Implement the minimum hosted transport changes needed to accept the required streamable HTTP session flow and reject unsupported request shapes consistently.
  - Implement the minimum streamed delivery behavior required for server responses and transport-level events to reach connected clients.
  - Document a local and hosted verification path that proves transport compatibility without requiring tribal knowledge.
- Refactor:
  - Consolidate transport decision rules so session establishment, stream delivery, and failure handling follow one client-visible contract.
  - Remove any duplicated response-shaping or event-emission logic that could cause hosted and local streaming behavior to diverge.
  - Tighten regression coverage around interrupted streams, unsupported methods, malformed requests, and concurrent sessions.
- Required test levels: unit, contract, integration, end-to-end.
- Pull request evidence expectations:
  - Passing automated coverage for valid and invalid `GET` and `POST` transport flows, stream delivery, interrupted stream handling, and session closure behavior.
  - Captured local verification evidence showing successful session establishment and streamed response handling.
  - Captured hosted verification evidence showing the same transport behavior against the deployed Cloud Run endpoint.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose one hosted MCP endpoint that supports the streamable HTTP transport contract required for modern MCP consumers.
- **FR-002**: System MUST accept the `GET` request behavior required by the selected streamable HTTP transport contract.
- **FR-003**: System MUST accept the `POST` request behavior required by the selected streamable HTTP transport contract.
- **FR-004**: System MUST reject unsupported or malformed transport requests with stable client-visible failure behavior that does not imply a successful MCP session.
- **FR-005**: System MUST preserve a clear distinction between successful session establishment, temporarily unavailable service state, and client request errors.
- **FR-006**: System MUST deliver streamed MCP responses when the transport contract requires streaming rather than one-shot request/response behavior.
- **FR-007**: System MUST deliver server-driven events over the active hosted transport whenever the transport contract requires those events to be observable by the client.
- **FR-008**: System MUST preserve message ordering within a streamed response so connected clients can process output deterministically.
- **FR-009**: System MUST make stream completion or session termination visible to the client so incomplete streams are not mistaken for complete successful responses.
- **FR-010**: System MUST support multiple concurrent hosted MCP sessions without cross-delivering streamed messages between clients.
- **FR-011**: System MUST keep the hosted MCP entrypoint compatible with the existing Cloud Run deployment model so the service remains deployable through the project’s hosted workflow.
- **FR-012**: System MUST keep local verification behavior and hosted verification behavior aligned for the same valid and invalid transport interactions.
- **FR-013**: System MUST document the valid streamable HTTP request flows, expected success behavior, and expected failure behavior for MCP consumers and platform integrators.
- **FR-014**: System MUST document concrete local verification steps for session establishment, streamed response handling, and failure-path validation.
- **FR-015**: System MUST document concrete hosted verification steps for session establishment, streamed response handling, and failure-path validation against the deployed service URL.

### Key Entities *(include if feature involves data)*

- **Hosted MCP Session**: A client-visible connection context established through the hosted streamable HTTP endpoint and used for ongoing MCP interactions.
- **Transport Request Flow**: The sequence of allowed client requests and server responses needed to establish, use, and close a hosted streamable HTTP session.
- **Stream Event**: A unit of streamed server output delivered to an active client session, including response content or server-driven transport events.
- **Session Outcome**: The client-visible result of a hosted transport interaction, such as successful session establishment, normal stream completion, temporary service unavailability, or client request failure.

### Dependencies

- FND-008 must already provide the deploy-and-verify hosted workflow so this feature can be proven against an actual Cloud Run endpoint.
- FND-007 hosted HTTP semantics must remain compatible with the new transport rules so probe behavior and MCP route behavior stay coherent.
- Earlier MCP foundation work for initialization, tool discovery, and invocation must remain reachable through the transport once a compliant session is established.

### Assumptions

- The MCP specification chosen for this project defines a streamable HTTP contract that is sufficient for both OpenAI Agent Builder and comparable hosted MCP consumers.
- This feature is limited to transport behavior and verification guidance; protocol-native payload alignment remains in FND-010.
- The hosted MCP route remains the single externally documented entrypoint for MCP consumers.
- A temporary inability to serve a streamable session should be distinguishable from a permanent client-request failure.
- Integrators need one documented verification flow for local use and one for hosted use before treating the transport as rollout-ready.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid hosted transport verification runs successfully establish a streamable MCP session using the documented request flow.
- **SC-002**: 100% of required streamed response verification runs deliver ordered streamed output that reviewers can match to the initiating MCP interaction without ambiguity.
- **SC-003**: 100% of malformed or unsupported transport verification runs return the documented failure behavior without being misclassified as successful MCP sessions.
- **SC-004**: At least 95% of local-to-hosted verification comparisons show no client-visible difference for the same session-establishment, stream-delivery, and failure-path scenarios.
- **SC-005**: Integrators can complete the documented local verification and hosted verification flow for the transport in 20 minutes or less, excluding external deployment wait time.
