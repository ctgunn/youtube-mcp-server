# Feature Specification: Layer 2 Tool `captions_insert`

**Feature Branch**: `205-captions-insert`  
**Created**: 2026-05-28  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-205, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Caption Tracks Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `captions_insert` tool to create a new caption track for an eligible YouTube video while staying close to the upstream `captions.insert` metadata, media-upload, and created-resource behavior.

**Why this priority**: This is the core value of YT-205. Layer 2 must expose the endpoint-backed caption creation operation for direct caption-management workflows, debugging, and later higher-level composition without hiding its upload-sensitive behavior.

**Independent Test**: Can be tested by invoking `captions_insert` with eligible authorization, required caption metadata, and supported caption media input, then confirming the caller receives a created caption resource and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for a target video, **When** they call `captions_insert` with valid caption metadata and supported caption media input, **Then** the result includes the created caption resource in a near-raw endpoint-backed shape.
2. **Given** a caller provides all required creation inputs and optional supported delegation context, **When** the caption track is created, **Then** the result preserves the requested operation context and the returned caption resource fields.
3. **Given** the upstream creation succeeds but returns only the created caption resource rather than a collection, **When** the caller inspects the result, **Then** the single-resource mutation outcome is clear and is not presented as a list or higher-level transcript workflow.

---

### User Story 2 - Understand Cost, Authorization, and Upload Rules Before Calling (Priority: P2)

As a client developer, I can inspect `captions_insert` before invoking it and immediately understand that it maps to `captions.insert`, costs 400 official quota units per call, requires eligible OAuth authorization, and requires caption media-upload input in addition to metadata.

**Why this priority**: Caption creation is quota-expensive, permission-sensitive, and upload-oriented. Callers need this information in discovery, descriptions, and examples so they do not accidentally spend quota, attempt API-key-only access, or submit metadata-only requests.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the upstream identity, quota cost of `400`, OAuth requirement, media-upload requirement, optional delegation context, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `captions_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `400`, OAuth-required access mode, upload requirement, and availability state.
2. **Given** an example request is shown for `captions_insert`, **When** a caller reads the example, **Then** the quota cost of `400` and the need for eligible authorization plus caption media input are visible alongside the request shape.
3. **Given** a caller needs to create captions in a delegated content-owner context, **When** they inspect the tool contract, **Then** the supported delegation fields and their authorization implications are clear before invocation.

---

### User Story 3 - Reject Unsupported Caption Creation Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `captions_insert` request is missing required metadata, missing media-upload input, lacks eligible authorization, or uses unsupported creation options, so I can correct the request without guessing which caption-creation rule was violated.

**Why this priority**: `captions.insert` combines mutation, authorization, and upload requirements. Clear validation protects callers from expensive failed attempts while keeping the tool faithful to the endpoint instead of inventing higher-level recovery behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including metadata-only creation attempts, media-only creation attempts, missing authorization, unsupported media input, conflicting delegation context, and unsupported optional fields, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides caption metadata but no caption media input, **When** they call `captions_insert`, **Then** the request is rejected with guidance that media-upload input is required.
2. **Given** a caller provides caption media input but omits required caption metadata, **When** they call `captions_insert`, **Then** the request is rejected with guidance that caption creation metadata is required.
3. **Given** a caller lacks eligible OAuth authorization for the target video or delegated content-owner context, **When** they call `captions_insert`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing video or caption resource.

### Edge Cases

- The caller provides metadata without caption media input; the request must be rejected before it is treated as a supported caption creation attempt.
- The caller provides caption media input without required caption metadata; the request must be rejected with clear missing-metadata guidance.
- The caller has OAuth authorization but lacks rights to create captions for the target video; the response must distinguish access failure from a missing video or unsupported media input.
- The caller supplies delegated content-owner context without the corresponding eligible authorization; the response must surface the delegation access requirement.
- The caller supplies unsupported media format, invalid media metadata, or upload-related fields outside the supported endpoint contract; the request must be rejected or clearly flagged as unsupported.
- The upstream service returns quota, authorization, invalid request, media upload, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The created caption resource is returned with a subset of expected fields; the result must preserve the returned resource without fabricating missing upstream fields.
- The caller expects transcript retrieval, caption download, translation, language ranking, or enrichment; the tool contract must keep those higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `captions_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `captions.insert` identity, official quota-unit cost of `400`, OAuth-required auth mode, media-upload requirement, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required caption metadata, required caption media input, optional supported delegation context, metadata-only rejection, media-only rejection, unsupported upload option rejection, and OAuth access guidance.
- **Red**: Add failing result-contract checks proving that created caption resources, requested operation context, mutation outcome details, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `captions_insert` tool contract and behavior needed for callers to make supported low-level `captions.insert` requests and receive near-raw created caption resource results.
- **Green**: Include representative examples for authorized caption creation, delegated content-owner creation context, metadata-only validation failure, media-only validation failure, and authorization-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `captions_insert` request, response, quota, auth, upload, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for metadata and media-upload validation, integration-style checks for representative successful and failed caption creation paths, and documentation checks for quota/auth/upload/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `captions_insert` responsibility, inputs, outputs, quota cost, auth behavior, media-upload constraints, mutation result, and delegation notes.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-205`, the dependency assumptions from YT-105/YT-201/YT-202, focused `captions_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `captions_insert`.
- **FR-002**: The `captions_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `captions` and method `insert`.
- **FR-003**: The `captions_insert` tool metadata MUST record the official quota-unit cost of `400` per call.
- **FR-004**: The `captions_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `400`.
- **FR-005**: The `captions_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present caption creation as an API-key-only capability.
- **FR-006**: The `captions_insert` input contract MUST preserve the upstream concepts of required caption metadata, required caption media input, supported upload-related options, and supported delegation context where those concepts are supported.
- **FR-007**: The `captions_insert` input contract MUST require both supported caption metadata and supported caption media input for each creation request.
- **FR-008**: The `captions_insert` tool MUST reject metadata-only creation attempts with clear caller-facing validation feedback.
- **FR-009**: The `captions_insert` tool MUST reject media-only creation attempts with clear caller-facing validation feedback.
- **FR-010**: The `captions_insert` tool MUST reject requests that require authorized or delegated access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-011**: The `captions_insert` result MUST preserve the created caption resource, mutation outcome details, relevant request context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-012**: The `captions_insert` tool MUST surface upstream quota, authorization, invalid request, upload, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-013**: The `captions_insert` contract MUST remain close to the upstream `captions.insert` endpoint and MUST NOT add higher-level transcript retrieval, caption downloading, translation, language ranking, enrichment, or heuristic interpretation.
- **FR-014**: The `captions_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation, media-upload, and example standards established by YT-201 and YT-202.
- **FR-015**: The `captions_insert` tool MUST rely on the existing Layer 1 `captions.insert` capability from YT-105 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-016**: The feature MUST include caller-facing examples for at least one authorized caption creation request, one delegated content-owner scenario, one metadata-only validation failure, one media-only validation failure, and one authorization-sensitive failure.
- **FR-017**: The feature MUST include validation evidence that clients can discover, call, understand upload and OAuth requirements, interpret created-resource results, and handle failures for `captions_insert` without consulting implementation-only artifacts.

### Key Entities

- **Captions Insert Tool**: The public Layer 2 MCP tool named `captions_insert`, representing one low-level endpoint-backed caption creation operation.
- **Caption Creation Request**: The request shape that combines required caption metadata, target video context, supported caption media input, and any supported delegated content-owner context.
- **Caption Metadata**: The caller-provided caption-track attributes required to create a caption resource, such as video association and language or naming information when required by the supported contract.
- **Caption Media Input**: The uploaded caption content and related media information required for a valid caption creation request.
- **Created Caption Resource Result**: The returned caption-track resource and operation context produced by a successful `captions_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `captions_insert` invocation costs 400 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that caption creation requires eligible OAuth authorization and may require valid delegated content-owner context for some requests.
- **Upload Requirement Disclosure**: The caller-facing indication that caption metadata alone is insufficient and supported caption media input is required.

### Assumptions

- YT-105 provides the Layer 1 `captions.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation, media-upload, error, example, and validation standards this feature must follow.
- `captions_insert` is a low-level endpoint-backed tool for direct caption creation, debugging, and power-user workflows; higher-level transcript retrieval, caption download, translation, language ranking, enrichment, or research workflows belong to later Layer 3 features.
- The official YouTube Data API documentation is the default source for `captions.insert` quota cost, auth behavior, upload behavior, availability state, delegation behavior, and mutation result behavior, with any discovered caveats recorded explicitly.
- Representative coverage of authorized caption creation, delegated content-owner context, missing metadata, missing media input, unsupported upload options, authorization-sensitive failures, and created-resource results is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `captions.insert` identity and official quota-unit cost of `400`.
- **SC-002**: A client developer can determine in under 1 minute that `captions_insert` requires eligible OAuth authorization and supported caption media input by reading the tool contract alone.
- **SC-003**: 100% of representative valid `captions_insert` requests return a created caption resource with relevant operation context and returned upstream fields preserved.
- **SC-004**: 100% of representative invalid caption creation requests that omit required metadata, omit media input, or use unsupported upload options are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-005**: Reviewers can verify in a single review pass that `captions_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, media-upload, mutation response, error, and example standards.
- **SC-006**: A power user can discover `captions_insert`, identify the required metadata and media-upload inputs, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-007**: Final review evidence includes passing focused `captions_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
