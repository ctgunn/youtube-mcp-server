# Feature Specification: MCP Transport + Handshake

**Feature Branch**: `001-mcp-transport-handshake`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Can you read requirements/PRD.md to understand the scope of the project. Then, can you read requirements/spec-kit-seed.md and start on FND-001?"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Initialize MCP Session (Priority: P1)

As an MCP client, I can initialize a session with the server and receive
declared capabilities so I can safely proceed with tool operations.

**Why this priority**: Initialization is the first required handshake and
blocks all other MCP operations.

**Independent Test**: Send an initialize request to the MCP transport and
verify a successful response containing server identity and capabilities.

**Acceptance Scenarios**:

1. **Given** a running server, **When** a client sends a valid initialize
   request, **Then** the server returns success with capabilities and protocol
   metadata.
2. **Given** a malformed initialize request, **When** the request is processed,
   **Then** the server returns a structured error with `code`, `message`, and
   optional `details`.

---

### User Story 2 - Discover Registered Tools (Priority: P2)

As an MCP client, I can list currently available tools so I can decide what
operations to invoke.

**Why this priority**: Tool discovery is essential for dynamic clients and
validates that the transport supports core MCP discovery flow.

**Independent Test**: Send a list-tools request and verify that the response
contains registered tool metadata in a stable shape.

**Acceptance Scenarios**:

1. **Given** the server has one or more registered tools, **When** a client
   requests tool listing, **Then** the server returns a deterministic list of
   tool names and descriptions.

---

### User Story 3 - Invoke Tool via MCP Path (Priority: P3)

As an MCP client, I can invoke a tool through the MCP invocation path and
receive structured success or failure responses.

**Why this priority**: Invocation completes the minimum FND-001 capability and
proves the transport can process MCP tool execution lifecycle requests.

**Independent Test**: Invoke a baseline stub tool and verify success envelope;
invoke an unknown tool and verify structured not-found error envelope.

**Acceptance Scenarios**:

1. **Given** a registered tool and valid input, **When** a client invokes it,
   **Then** the server returns a stable success response envelope.
2. **Given** a tool name that is not registered, **When** invocation is
   requested, **Then** the server returns a structured `RESOURCE_NOT_FOUND`
   error response.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Unsupported or unknown MCP method name.
- Missing required request fields in initialize/list/invoke payloads.
- Invalid or non-object tool arguments.
- Empty tool registry at list time.
- Duplicate request IDs from clients.
- Unexpected internal exception during invocation.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red: Write failing tests for initialize success/error handling, tool discovery,
  and tool invocation success/failure envelopes before implementation.
- Green: Implement only the minimum transport and method routing needed to make
  those tests pass for FND-001 scope.
- Refactor: Improve request parsing, envelope shaping, and method dispatch
  structure while keeping all FND-001 tests green after each change.
- Required test levels: unit tests for request/method handling and contract tests
  for initialize/list/invoke response envelopes.
- Pull request evidence: include test output showing initial failures, final
  pass results, and a note of refactor changes performed post-green.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST expose an HTTP MCP transport compatible with Cloud Run.
- **FR-002**: System MUST support MCP initialize request handling and capability
  declaration in the response.
- **FR-003**: System MUST support tool discovery/listing through MCP flow.
- **FR-004**: System MUST support tool invocation through MCP flow using a stable
  success/error response envelope.
- **FR-005**: System MUST return structured errors containing `code`, `message`,
  and optional `details` for invalid requests and invocation failures.
- **FR-006**: System MUST include request correlation metadata (at minimum
  `requestId`) in MCP responses where available from the incoming request.
- **FR-007**: System MUST prevent stack trace leakage in client-visible error
  payloads.

### Key Entities *(include if feature involves data)*

- **MCP Request**: Client message containing method, request identifier, and
  optional params/payload.
- **MCP Response Envelope**: Standard server response containing success state,
  data payload, metadata, and structured error.
- **Server Capability Descriptor**: Declares supported MCP operations and basic
  server identity/version details.
- **Tool Descriptor**: Advertised tool metadata including name and description.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of initialize contract tests pass, including success and
  malformed request scenarios.
- **SC-002**: 100% of tool discovery contract tests pass for both populated and
  empty registry scenarios.
- **SC-003**: 100% of invocation contract tests pass for success and
  `RESOURCE_NOT_FOUND` failure scenarios.
- **SC-004**: A new MCP client can complete initialize, list tools, and invoke
  one baseline tool in a single session without protocol-shape errors.
