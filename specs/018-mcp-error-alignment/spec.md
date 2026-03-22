# Feature Specification: JSON-RPC / MCP Error Code Alignment

**Feature Branch**: `018-mcp-error-alignment`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Review the requirements/PRD.md to get an overview of the project and its goals for context. Then, begin working on the requirements for FND-018, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Protocol-Aligned Error Codes (Priority: P1)

An MCP client sends a malformed or otherwise invalid request and needs the returned error code to follow the expected JSON-RPC / MCP conventions so the client can classify and handle the failure without server-specific special cases.

**Why this priority**: FND-018 exists to remove ambiguous server-specific error-code behavior from the core protocol surface. If clients still need custom code-type handling, the compatibility goal is not met.

**Independent Test**: Can be fully tested by sending representative malformed request, unsupported method, and invalid argument cases to the service and confirming the returned error codes match the documented protocol-aligned categories.

**Acceptance Scenarios**:

1. **Given** an MCP client sends a malformed request, **When** the service rejects it, **Then** the client receives a structured error whose code follows the documented protocol-aligned malformed-request category.
2. **Given** an MCP client calls an unsupported method, **When** the service rejects the call, **Then** the returned error uses the documented protocol-aligned unsupported-method category instead of a server-specific code format.
3. **Given** an MCP client sends a tool request with invalid arguments, **When** the service rejects the request, **Then** the returned error uses the documented protocol-aligned invalid-argument category and remains safe for client consumption.

---

### User Story 2 - Trust Error Consistency Across Hosted and Local Flows (Priority: P2)

An integrator or release reviewer exercises the same failure path locally and against the hosted service and needs both environments to return the same client-visible error code behavior for equivalent requests.

**Why this priority**: Error-code alignment loses value if hosted and local environments drift. Consistent behavior across environments is required for dependable testing, support, and rollout validation.

**Independent Test**: Can be fully tested by running the same malformed request, invalid argument, authentication failure, and tool failure scenarios against local and hosted environments and confirming the client-visible error codes and categories remain aligned.

**Acceptance Scenarios**:

1. **Given** the same invalid request is sent to local and hosted environments, **When** both environments reject it, **Then** they return the same documented client-visible error code category.
2. **Given** authentication is required for a hosted request and equivalent access rules are exercised locally, **When** access is denied, **Then** the resulting client-visible error remains aligned with the documented authentication failure category.
3. **Given** a tool execution fails after the request is accepted, **When** the failure is reported in local and hosted environments, **Then** both environments return the same documented execution-failure category without leaking internal details.

---

### User Story 3 - Diagnose Failures Through One Documented Mapping (Priority: P3)

A developer or operator needs one documented error contract that explains how transport, protocol, validation, authentication, and tool failures are mapped so future features can reuse the same client-facing rules.

**Why this priority**: Without one documented mapping, later tool and transport work will reintroduce inconsistent error-code behavior and make regressions difficult to catch in review.

**Independent Test**: Can be fully tested by reviewing the published error mapping, exercising at least one representative failure from each covered category, and confirming the observed client-visible behavior matches the documented contract.

**Acceptance Scenarios**:

1. **Given** a reviewer reads the published error contract, **When** they compare it against representative failure-path results, **Then** they can map each covered failure category to one documented client-visible code behavior.
2. **Given** a new failure is added to an existing covered category, **When** the contract tests run, **Then** the failure is evaluated against the documented mapping rather than introducing a new server-specific code type by default.

### Edge Cases

- What happens when a request violates both protocol shape rules and tool-specific validation rules at the same time?
- How does the service classify a request that reaches a protected route without valid authentication and also includes malformed input?
- What happens when a tool failure includes internal exception details that must not be exposed to clients?
- How does the service behave when a legacy server-specific error code is still emitted from an older path?
- What happens when a client retries the same invalid request repeatedly and expects identical error classification each time?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit, integration, and contract tests for malformed requests, unsupported methods, invalid arguments, authentication failures, and tool execution failures that currently return non-aligned or inconsistent client-visible code behavior.
- **Green**: Implement the minimal error-mapping and documentation changes required so covered failure paths return the documented protocol-aligned code categories in both local and hosted flows.
- **Refactor**: Consolidate duplicated error classification paths, remove remaining server-specific code typing from covered client-visible responses, and rerun the broader MCP regression suite to confirm no accepted success-path behavior regresses.
- Required test levels: unit tests for error categorization rules; integration tests for request handling across covered failure types; contract tests for client-visible error payload structure and code alignment; end-to-end verification for representative local and hosted failure scenarios.
- Pull request evidence must include failing-to-passing error-path coverage, one documented mapping of covered failure categories to client-visible codes, and proof that local and hosted verification produce aligned results for the representative scenarios.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The service MUST return client-visible error codes that follow the documented JSON-RPC / MCP conventions for covered protocol and tool failure scenarios.
- **FR-002**: The service MUST define one documented mapping for transport, protocol, validation, authentication, authorization, and tool execution failure categories.
- **FR-003**: The service MUST use the documented malformed-request error category when a request cannot be processed because its protocol shape is invalid.
- **FR-004**: The service MUST use the documented unsupported-method error category when a client requests an operation the service does not support.
- **FR-005**: The service MUST use the documented invalid-argument error category when a request reaches a supported operation but fails input validation.
- **FR-006**: The service MUST use the documented authentication or authorization error category when access is denied by the hosted access rules established by prior security requirements.
- **FR-007**: The service MUST use the documented tool-execution failure category when a tool fails after the request is otherwise accepted for execution.
- **FR-008**: Hosted and local environments MUST return the same client-visible error category and code for equivalent covered failure scenarios.
- **FR-009**: Covered client-visible error payloads MUST remain structured and safe, including a code and message and optional additional details only when those details do not expose internal diagnostics or secrets.
- **FR-010**: The service MUST prevent legacy server-specific error-code typing from appearing in covered client-visible responses once an equivalent documented protocol-aligned category exists.
- **FR-011**: The documented error mapping MUST identify category precedence rules for requests that could match more than one failure category.
- **FR-012**: Automated verification MUST cover representative malformed request, unsupported method, invalid argument, authentication or authorization denial, and tool execution failure scenarios.
- **FR-013**: The release evidence MUST demonstrate that the documented error mapping matches observed client-visible behavior for both local and hosted verification flows.

### Key Entities *(include if feature involves data)*

- **Error Mapping Contract**: The documented rules that map covered failure categories to the client-visible JSON-RPC / MCP error-code behavior the service promises to return.
- **Failure Category**: A class of request failure, such as malformed request, unsupported method, invalid argument, authentication or authorization denial, or tool execution failure.
- **Client-Visible Error Payload**: The structured failure response returned to a caller, including its code, message, and any safe optional details.
- **Verification Scenario**: A documented failing request used to prove that observed client-visible error behavior matches the published mapping in both local and hosted environments.

## Assumptions

- FND-010 already established MCP-native response structure, and this feature narrows the remaining gap in how error codes are typed and classified.
- FND-013 already established the hosted security model, and this feature aligns the client-visible authentication and authorization failure codes with the shared protocol contract.
- This feature changes client-visible error classification for covered scenarios, not the set of supported tools, routes, or authentication requirements.
- Equivalent local and hosted requests are expected to produce the same client-visible error categorization even if their internal diagnostics differ.

## Dependencies

- `FND-010` MCP protocol contract alignment
- `FND-013` Remote MCP security and transport hardening

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated contract verification, 100% of covered malformed request, unsupported method, invalid argument, authentication or authorization denial, and tool execution failure scenarios return the documented client-visible error code category.
- **SC-002**: In local-versus-hosted verification, 100% of representative equivalent failure scenarios return matching client-visible error codes and failure categories.
- **SC-003**: 0 covered client-visible error responses use retired server-specific error-code typing after the feature is released.
- **SC-004**: A reviewer can use the published error mapping and verification evidence to classify each covered failure scenario in 20 minutes or less without consulting implementation code.
- **SC-005**: In failure-path verification, 100% of covered client-visible error payloads omit internal stack traces, raw exception objects, and secret-bearing diagnostic details.
