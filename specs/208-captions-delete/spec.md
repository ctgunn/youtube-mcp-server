# Feature Specification: Layer 2 Tool `captions_delete`

**Feature Branch**: `208-captions-delete`  
**Created**: 2026-06-06  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-208, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Caption Tracks Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `captions_delete` tool to delete an existing YouTube caption track while staying close to the upstream `captions.delete` caption-track identity and deletion acknowledgment behavior.

**Why this priority**: This is the core value of YT-208. Layer 2 must expose endpoint-backed caption deletion for direct caption management, debugging, and future caption-management composition without turning it into a higher-level caption workflow.

**Independent Test**: Can be tested by invoking `captions_delete` with eligible authorization and a valid caption-track identifier, then confirming the caller receives a deletion acknowledgment and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for an existing caption track, **When** they call `captions_delete` with the required caption-track identifier, **Then** the result acknowledges the deletion in a near-raw endpoint-backed shape.
2. **Given** the upstream deletion succeeds without returning a caption resource body, **When** the caller inspects the result, **Then** the mutation outcome is clear and includes operation context rather than fabricated caption data.
3. **Given** a caller wants to manage captions directly, **When** they use `captions_delete`, **Then** the tool performs only caption deletion and is not presented as caption listing, creation, update, download, transcript summarization, or recovery.

---

### User Story 2 - Understand Cost, Authorization, and Delegation Before Calling (Priority: P2)

As a client developer, I can inspect `captions_delete` before invoking it and immediately understand that it maps to `captions.delete`, costs 50 official quota units per call, requires eligible OAuth authorization, requires a caption-track identifier, and supports documented content-owner delegation context where applicable.

**Why this priority**: Caption deletion is destructive and authorization-sensitive. Callers need quota, permission, identifier, deletion, and delegation visibility in discovery, descriptions, and examples so they can avoid unauthorized attempts, accidental quota spend, and unintended deletion.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the upstream identity, quota cost of `50`, OAuth requirement, required caption-track identifier, deletion semantics, optional delegation context, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `captions_delete`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, required caption-track identifier, destructive deletion behavior, supported delegation context, and availability state.
2. **Given** an example request is shown for `captions_delete`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible authorization plus a valid caption-track identifier are visible alongside the request shape.
3. **Given** a caller needs to delete captions in a delegated content-owner context, **When** they inspect the tool contract, **Then** the supported delegation fields and their authorization implications are clear before invocation.

---

### User Story 3 - Reject Unsupported Caption Delete Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `captions_delete` request is missing the caption-track identifier, lacks eligible authorization, or includes unsupported delegation context, so I can correct the request without guessing which caption-delete rule was violated.

**Why this priority**: `captions.delete` is destructive and authorization-sensitive. Clear validation protects callers from confusing failed deletion attempts while keeping the tool faithful to the endpoint instead of inventing higher-level recovery or caption-selection behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing caption-track identifier, empty identifier, unsupported extra mutation options, missing authorization, and invalid delegated content-owner context, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required caption-track identifier, **When** they call `captions_delete`, **Then** the request is rejected with guidance that a valid caption-track identifier is required.
2. **Given** a caller includes unsupported deletion options or unsupported delegation context, **When** they call `captions_delete`, **Then** the request is rejected or clearly flagged with the supported endpoint rules.
3. **Given** a caller lacks eligible OAuth authorization for the target caption track or delegated content-owner context, **When** they call `captions_delete`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing caption resource.

### Edge Cases

- The caller omits the caption-track identifier; the request must be rejected before it is treated as a supported caption deletion attempt.
- The caller provides an empty, malformed, or unsupported caption-track identifier value; the response must identify the invalid identifier input.
- The caller has OAuth authorization but lacks rights to delete the target caption track; the response must distinguish access failure from a missing caption resource.
- The caller supplies delegated content-owner context without the corresponding eligible authorization; the response must surface the delegation access requirement.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The upstream deletion succeeds with no resource body; the result must still provide a clear deletion acknowledgment and operation context without fabricating deleted caption fields.
- The caller repeats a deletion request for a caption track that was already deleted; the response must preserve the upstream missing-resource or idempotency-relevant signal in the shared error/result shape.
- The caller expects caption listing, caption creation, caption update, caption download, transcript summarization, deletion undo, language ranking, enrichment, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `captions_delete` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `captions.delete` identity, official quota-unit cost of `50`, OAuth-required auth mode, required caption-track identifier, destructive deletion behavior, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required caption-track identifier, supported deletion request, optional supported delegation context, missing-identifier rejection, invalid-identifier rejection, unsupported option rejection, and OAuth access guidance.
- **Red**: Add failing result-contract checks proving that deletion acknowledgment, requested operation context, mutation outcome details, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `captions_delete` tool contract and behavior needed for callers to make supported low-level `captions.delete` requests and receive near-raw deletion acknowledgment results.
- **Green**: Include representative examples for authorized caption deletion, delegated content-owner deletion context, missing-identifier validation failure, invalid-identifier validation failure, unsupported option validation failure, repeated deletion or missing-resource failure, and authorization-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `captions_delete` request, response, quota, auth, destructive mutation, delegation, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for caption-track identifier and delegation validation, integration-style checks for representative successful and failed caption deletion paths, and documentation checks for quota/auth/deletion/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `captions_delete` responsibility, inputs, outputs, quota cost, auth behavior, destructive deletion semantics, deletion acknowledgment result, and delegation notes.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-208`, the dependency assumptions from YT-108/YT-201/YT-202, focused `captions_delete` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `captions_delete`.
- **FR-002**: The `captions_delete` tool definition MUST identify its mapped upstream operation as YouTube resource `captions` and method `delete`.
- **FR-003**: The `captions_delete` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `captions_delete` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `captions_delete` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present caption deletion as an API-key-only capability.
- **FR-006**: The `captions_delete` input contract MUST preserve the upstream concepts of required caption-track identifier and supported delegated content-owner context where those concepts are supported.
- **FR-007**: The `captions_delete` input contract MUST require exactly one valid caption-track identifier for each deletion request.
- **FR-008**: The `captions_delete` tool MUST support valid caption deletion requests with no optional delegation context.
- **FR-009**: The `captions_delete` tool MUST support valid caption deletion requests that include supported delegated content-owner context.
- **FR-010**: The `captions_delete` tool MUST reject missing, empty, malformed, or unsupported caption-track identifiers with clear caller-facing validation feedback.
- **FR-011**: The `captions_delete` tool MUST reject unsupported deletion options or unsupported delegation context with clear caller-facing validation feedback.
- **FR-012**: The `captions_delete` tool MUST reject requests that require authorized or delegated access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-013**: The `captions_delete` result MUST preserve deletion acknowledgment, relevant request context, mutation outcome details, and returned upstream fields or no-body characteristics in a near-raw endpoint-backed shape.
- **FR-014**: The `captions_delete` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-015**: The `captions_delete` contract MUST remain close to the upstream `captions.delete` endpoint and MUST NOT add higher-level caption listing, caption creation, caption update, caption download, transcript summarization, deletion undo, language ranking, enrichment, or heuristic interpretation.
- **FR-016**: The `captions_delete` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation, deletion acknowledgment, delegation, error, and example standards established by YT-201 and YT-202.
- **FR-017**: The `captions_delete` tool MUST rely on the existing Layer 1 `captions.delete` capability from YT-108 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-018**: The feature MUST include caller-facing examples for at least one authorized caption deletion request, one delegated content-owner scenario, one missing-identifier validation failure, one invalid-identifier validation failure, one unsupported option validation failure, one repeated deletion or missing-resource failure, and one authorization-sensitive failure.
- **FR-019**: The feature MUST include validation evidence that clients can discover, call, understand deletion, quota, and OAuth requirements, interpret deletion acknowledgment results, and handle failures for `captions_delete` without consulting implementation-only artifacts.
- **FR-020**: The feature MUST make destructive deletion semantics visible in caller-facing descriptions and examples so users understand that successful calls remove the target caption track rather than returning or modifying it.

### Key Entities

- **Captions Delete Tool**: The public Layer 2 MCP tool named `captions_delete`, representing one low-level endpoint-backed caption deletion operation.
- **Caption Delete Request**: The request shape that combines a required caption-track identifier and any supported delegated content-owner context.
- **Caption Track Identifier**: The caller-provided identifier for the caption track being deleted.
- **Delegated Content-Owner Context**: Optional caller-provided context used when an authorized content-owner delegation flow is supported for the deletion request.
- **Deletion Acknowledgment Result**: The returned operation context, mutation outcome, and no-body or upstream payload characteristics produced by a successful `captions_delete` call.
- **Quota Disclosure**: The caller-facing statement that each `captions_delete` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that caption deletion requires eligible OAuth authorization and may require valid delegated content-owner context for some requests.
- **Destructive Mutation Disclosure**: The caller-facing indication that a successful request deletes the target caption track and does not provide undo, transcript retrieval, or higher-level recovery behavior.

### Assumptions

- YT-108 provides the Layer 1 `captions.delete` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation, deletion acknowledgment, delegation, error, example, and validation standards this feature must follow.
- `captions_delete` is a low-level endpoint-backed tool for direct caption management, debugging, and power-user workflows; higher-level transcript retrieval, caption recovery, summarization, enrichment, or research workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `captions.delete` quota cost, auth behavior, identifier behavior, availability state, delegation behavior, and deletion result behavior, with any discovered caveats recorded explicitly.
- Representative coverage of authorized deletion, delegated content-owner context, missing caption-track identifier, invalid caption-track identifier, unsupported options, repeated deletion or missing resource, authorization-sensitive failures, and deletion acknowledgment results is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions_delete` discovery metadata, descriptions, and examples produced by this feature display the mapped `captions.delete` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `captions_delete` requires eligible OAuth authorization and a valid caption-track identifier by reading the tool contract alone.
- **SC-003**: A client developer can determine in under 1 minute whether delegated content-owner context is supported and what authorization implication it has by reading the tool contract alone.
- **SC-004**: 100% of representative valid `captions_delete` requests return a deletion acknowledgment with relevant operation context and no fabricated caption resource data.
- **SC-005**: 100% of representative invalid caption delete requests that omit the caption-track identifier, provide invalid identifier input, use unsupported deletion options, or lack eligible permission are rejected with caller-facing feedback before being treated as supported endpoint requests.
- **SC-006**: Reviewers can verify in a single review pass that `captions_delete` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation response, deletion acknowledgment, delegation, error, and example standards.
- **SC-007**: A power user can discover `captions_delete`, identify the required caption-track identifier and destructive deletion behavior, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-008**: Final review evidence includes passing focused `captions_delete` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
