# Feature Specification: Tool Registry + Dispatcher

**Feature Branch**: `002-tool-registry-dispatcher`  
**Created**: 2026-03-01  
**Status**: Draft  
**Input**: User description: "Can you read requirements/PRD.md to get an overview of the project. Then, can you read the requirements in requirements/spec-kit-seed.md for FND-002 and begin working on it?"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register MCP Tools (Priority: P1)

As a server developer, I can register each tool with its name, description, input contract, and executable behavior so that tools are discoverable and callable through one consistent lifecycle.

**Why this priority**: Without registration, no tools can be exposed through MCP discovery or invocation, so this is the minimum value slice.

**Independent Test**: Register a sample tool and verify it appears as a complete entry in the server's internal tool list and can be referenced by name.

**Acceptance Scenarios**:

1. **Given** a tool definition with required fields, **When** the tool is registered, **Then** the registry stores it as an active callable tool entry.
2. **Given** a tool definition missing a required field, **When** registration is attempted, **Then** registration is rejected with a structured validation error.
3. **Given** an already-registered tool name, **When** a second registration attempts to use the same name, **Then** the registry rejects the duplicate and preserves the original active binding.

---

### User Story 2 - Dispatch Valid Tool Calls (Priority: P2)

As an MCP client, I can invoke a registered tool by name with valid input so that the request is routed to the correct behavior and returns structured output.

**Why this priority**: Dispatch turns registration into usable runtime behavior and enables real tool execution value.

**Independent Test**: Invoke a known registered tool with valid input and verify the matching tool behavior is executed and a structured result is returned.

**Acceptance Scenarios**:

1. **Given** a registered tool and valid input, **When** dispatch is requested for that tool name, **Then** the dispatcher executes the bound tool behavior and returns a structured success response.
2. **Given** a registered tool and invalid input, **When** dispatch is requested, **Then** execution is blocked and a structured input-validation error is returned.

---

### User Story 3 - Handle Unknown Tool Calls Safely (Priority: P3)

As an MCP client, I receive a predictable error when I call an unknown tool so that integration logic can handle missing tools safely.

**Why this priority**: Unknown-tool handling protects clients from ambiguous failures and is explicitly required by the feature acceptance criteria.

**Independent Test**: Dispatch a tool name that is not registered and verify the response contains the structured `RESOURCE_NOT_FOUND` error.

**Acceptance Scenarios**:

1. **Given** no tool exists for the requested name, **When** dispatch is requested, **Then** the response returns a structured `RESOURCE_NOT_FOUND` error without executing any tool behavior.
2. **Given** an unknown tool request, **When** error details are returned, **Then** the message identifies that the tool name is not available and supports client-side troubleshooting.

### Edge Cases

- What happens when a tool is registered with a name that differs only by case from an existing tool name?
- How does the system handle dispatch requests with missing, null, or non-object input payloads?
- What happens when a registered tool behavior fails unexpectedly during execution?
- How does the dispatcher behave if the registry is empty and receives a dispatch request?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- Red: Add failing unit tests for tool registration validation, duplicate-name rejection, successful dispatch, dispatch input validation, and unknown tool error mapping.
- Green: Implement only the minimum registry and dispatcher behavior required for those tests to pass, including structured unknown-tool errors.
- Refactor: Consolidate shared validation/error creation paths, remove duplication between registration and dispatch guards, and re-run full automated tests to confirm no regressions.
- Required test levels: unit (registry and dispatcher behavior), integration (MCP request flow through list and invoke paths), contract (error envelope and discovery behavior).
- Pull request evidence: failing-to-passing test progression for the new cases and final passing output for lint and test commands.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow developers to register tools with exactly these required attributes: tool name, human-readable description, input contract, and executable behavior binding.
- **FR-002**: System MUST reject registration attempts that omit required attributes or provide invalid attribute formats.
- **FR-003**: System MUST prevent duplicate tool registrations for the same normalized tool name and return a structured error when duplication is attempted.
- **FR-004**: System MUST provide a registry lookup capability that returns a tool definition by name for invocation workflows.
- **FR-005**: System MUST dispatch invocation requests by matching requested tool name to a registered tool definition.
- **FR-006**: System MUST validate invocation input against the tool's declared input contract before executing tool behavior.
- **FR-007**: System MUST not execute tool behavior when input validation fails and MUST return a structured validation error.
- **FR-008**: System MUST return a structured `RESOURCE_NOT_FOUND` error when dispatch is requested for an unregistered tool name.
- **FR-009**: System MUST return tool execution results in the standard MCP response envelope used by the server foundation.
- **FR-010**: System MUST preserve transport-layer independence so tools can be added or updated without requiring transport workflow changes.

### Key Entities *(include if feature involves data)*

- **Tool Definition**: A registered capability containing name, description, input contract, and executable behavior binding.
- **Tool Registry Entry**: The active stored representation of a tool definition used for listing and lookup during invocation.
- **Dispatch Request**: An invocation request containing target tool name and input payload.
- **Dispatch Result**: A structured success or error outcome returned from dispatch processing.

### Assumptions

- Tool names are treated as case-insensitive for uniqueness and lookup consistency.
- Only one active binding per normalized tool name is allowed at a time.
- Input contracts are complete enough to determine whether a dispatch request is valid before execution.
- Structured errors follow the existing foundation error shape (`code`, `message`, optional `details`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of attempted tool registrations with missing required attributes are rejected with structured validation errors.
- **SC-002**: 100% of dispatch requests to unknown tool names return `RESOURCE_NOT_FOUND` errors with no tool execution side effects.
- **SC-003**: At least 95% of valid dispatch requests for registered tools return successful structured results on first attempt in automated integration testing.
- **SC-004**: Developers can add a new tool definition and make it available for discovery and invocation without modifying transport behavior in 100% of sampled onboarding checks.
