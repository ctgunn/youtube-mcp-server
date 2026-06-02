# Feature Specification: Layer 2 Tool `captions_update`

**Feature Branch**: `206-captions-update`  
**Created**: 2026-06-01  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-206, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Caption Tracks Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `captions_update` tool to update an existing YouTube caption track while staying close to the upstream `captions.update` body, optional media-replacement, and updated-resource behavior.

**Why this priority**: This is the core value of YT-206. Layer 2 must expose the endpoint-backed caption update operation for direct caption maintenance, debugging, and future caption-management composition without hiding its mutation and upload-sensitive behavior.

**Independent Test**: Can be tested by invoking `captions_update` with eligible authorization and a valid caption update body, with and without supported replacement media, then confirming the caller receives an updated caption resource and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for an existing caption track, **When** they call `captions_update` with a valid update body and no replacement media, **Then** the result includes the updated caption resource in a near-raw endpoint-backed shape.
2. **Given** a caller has eligible authorization and provides a valid update body plus supported replacement caption media, **When** they call `captions_update`, **Then** the result reflects a caption update that includes the media-replacement path and preserves the returned caption resource fields.
3. **Given** the upstream update succeeds and returns a single updated caption resource, **When** the caller inspects the result, **Then** the mutation outcome is clear and is not presented as a list, transcript download, translation, or higher-level caption workflow.

---

### User Story 2 - Understand Cost, Authorization, and Update Rules Before Calling (Priority: P2)

As a client developer, I can inspect `captions_update` before invoking it and immediately understand that it maps to `captions.update`, costs 450 official quota units per call, requires eligible OAuth authorization, requires an update body, and may include supported caption media replacement.

**Why this priority**: Caption update is one of the highest-cost planned endpoint operations and can alter user-managed caption data. Callers need quota, authorization, update-body, delegation, and media-replacement rules visible before invocation so they can avoid accidental quota spend, unauthorized attempts, or unintended caption content changes.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the upstream identity, quota cost of `450`, OAuth requirement, required update body, optional supported media-replacement behavior, optional delegation context, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `captions_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `450`, OAuth-required access mode, update-body requirement, media-replacement behavior, and availability state.
2. **Given** an example request is shown for `captions_update`, **When** a caller reads the example, **Then** the quota cost of `450` and the need for eligible authorization plus a valid update body are visible alongside the request shape.
3. **Given** a caller needs to update captions in a delegated content-owner context, **When** they inspect the tool contract, **Then** the supported delegation fields and their authorization implications are clear before invocation.

---

### User Story 3 - Reject Unsupported Caption Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `captions_update` request is missing a required update body, has incomplete caption identity, lacks eligible authorization, or uses unsupported media/update options, so I can correct the request without guessing which caption-update rule was violated.

**Why this priority**: `captions.update` combines mutation, authorization, high quota cost, and optional media replacement. Clear validation protects callers from expensive failed attempts while keeping the tool faithful to the endpoint instead of inventing higher-level recovery behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing update body, incomplete caption identity, replacement media without a valid update body, unsupported media input, conflicting delegation context, missing authorization, and unsupported optional fields, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required caption update body, **When** they call `captions_update`, **Then** the request is rejected with guidance that a supported update body is required.
2. **Given** a caller provides replacement caption media but no valid caption update body, **When** they call `captions_update`, **Then** the request is rejected with guidance that media replacement must be paired with a valid caption update request.
3. **Given** a caller lacks eligible OAuth authorization for the target caption track or delegated content-owner context, **When** they call `captions_update`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing caption resource.

### Edge Cases

- The caller provides no caption update body; the request must be rejected before it is treated as a supported caption update attempt.
- The caller provides an update body that does not identify the caption track or omits required writable caption fields; the response must identify the missing or incomplete update input.
- The caller provides replacement caption media without a valid update body; the request must be rejected with clear body-plus-media guidance.
- The caller has OAuth authorization but lacks rights to update the target caption track; the response must distinguish access failure from a missing caption resource or unsupported media input.
- The caller supplies delegated content-owner context without the corresponding eligible authorization; the response must surface the delegation access requirement.
- The caller supplies unsupported media format, invalid media metadata, conflicting update options, or fields outside the supported endpoint contract; the request must be rejected or clearly flagged as unsupported.
- The upstream service returns quota, authorization, invalid request, media upload, unavailable service, missing resource, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The updated caption resource is returned with a subset of expected fields; the result must preserve the returned resource without fabricating missing upstream fields.
- The caller expects transcript retrieval, caption creation, caption download, translation, language ranking, enrichment, or heuristic interpretation; the tool contract must keep those higher-level or separate endpoint behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `captions_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `captions.update` identity, official quota-unit cost of `450`, OAuth-required auth mode, update-body requirement, optional media-replacement behavior, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required caption update body, caption-track identity, supported body-only update, supported body-plus-media update, optional supported delegation context, missing-body rejection, media-without-body rejection, unsupported update option rejection, and OAuth access guidance.
- **Red**: Add failing result-contract checks proving that updated caption resources, requested operation context, mutation outcome details, media-replacement indicators when applicable, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `captions_update` tool contract and behavior needed for callers to make supported low-level `captions.update` requests and receive near-raw updated caption resource results.
- **Green**: Include representative examples for authorized body-only caption update, authorized body-plus-media caption update, delegated content-owner update context, missing-body validation failure, media-without-body validation failure, and authorization-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `captions_update` request, response, quota, auth, media-update, mutation, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for update-body and optional media validation, integration-style checks for representative successful and failed caption update paths, and documentation checks for quota/auth/update/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `captions_update` responsibility, inputs, outputs, quota cost, auth behavior, update-body constraints, optional media-replacement behavior, mutation result, and delegation notes.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-206`, the dependency assumptions from YT-106/YT-201/YT-202, focused `captions_update` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `captions_update`.
- **FR-002**: The `captions_update` tool definition MUST identify its mapped upstream operation as YouTube resource `captions` and method `update`.
- **FR-003**: The `captions_update` tool metadata MUST record the official quota-unit cost of `450` per call.
- **FR-004**: The `captions_update` tool description and usage examples MUST visibly state the official quota-unit cost of `450`.
- **FR-005**: The `captions_update` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present caption update as an API-key-only capability.
- **FR-006**: The `captions_update` input contract MUST preserve the upstream concepts of required caption update body, caption-track identity, supported body-only update, optional supported media replacement, and supported delegation context where those concepts are supported.
- **FR-007**: The `captions_update` input contract MUST require a valid caption update body for each update request.
- **FR-008**: The `captions_update` tool MUST support valid body-only caption update requests.
- **FR-009**: The `captions_update` tool MUST support valid caption update requests that include supported replacement caption media.
- **FR-010**: The `captions_update` tool MUST reject missing-body update attempts with clear caller-facing validation feedback.
- **FR-011**: The `captions_update` tool MUST reject replacement-media attempts that are not paired with a valid caption update body.
- **FR-012**: The `captions_update` tool MUST reject requests that require authorized or delegated access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-013**: The `captions_update` result MUST preserve the updated caption resource, mutation outcome details, relevant request context, media-replacement indication when applicable, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-014**: The `captions_update` tool MUST surface upstream quota, authorization, invalid request, media upload, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-015**: The `captions_update` contract MUST remain close to the upstream `captions.update` endpoint and MUST NOT add higher-level transcript retrieval, caption creation, caption downloading, translation, language ranking, enrichment, or heuristic interpretation.
- **FR-016**: The `captions_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation, media-update, and example standards established by YT-201 and YT-202.
- **FR-017**: The `captions_update` tool MUST rely on the existing Layer 1 `captions.update` capability from YT-106 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-018**: The feature MUST include caller-facing examples for at least one authorized body-only caption update request, one authorized body-plus-media update request, one delegated content-owner scenario, one missing-body validation failure, one media-without-body validation failure, and one authorization-sensitive failure.
- **FR-019**: The feature MUST include validation evidence that clients can discover, call, understand update body, media, quota, and OAuth requirements, interpret updated-resource results, and handle failures for `captions_update` without consulting implementation-only artifacts.

### Key Entities

- **Captions Update Tool**: The public Layer 2 MCP tool named `captions_update`, representing one low-level endpoint-backed caption update operation.
- **Caption Update Request**: The request shape that combines a required caption update body, target caption-track identity, optional supported replacement media, and any supported delegated content-owner context.
- **Caption Update Body**: The caller-provided caption-track resource information required to update an existing caption track.
- **Replacement Caption Media**: Optional uploaded caption content and related media information used when the update replaces caption content as part of the request.
- **Updated Caption Resource Result**: The returned caption-track resource and operation context produced by a successful `captions_update` call.
- **Quota Disclosure**: The caller-facing statement that each `captions_update` invocation costs 450 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that caption update requires eligible OAuth authorization and may require valid delegated content-owner context for some requests.
- **Media Replacement Disclosure**: The caller-facing indication that caption media replacement is supported only as part of a valid caption update request.

### Assumptions

- YT-106 provides the Layer 1 `captions.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation, media-update, error, example, and validation standards this feature must follow.
- `captions_update` is a low-level endpoint-backed tool for direct caption maintenance, debugging, and power-user workflows; higher-level transcript retrieval, caption creation, caption download, translation, language ranking, enrichment, or research workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `captions.update` quota cost, auth behavior, update-body behavior, media-replacement behavior, availability state, delegation behavior, and mutation result behavior, with any discovered caveats recorded explicitly.
- Representative coverage of authorized body-only update, authorized body-plus-media update, delegated content-owner context, missing update body, media-without-body, unsupported update options, authorization-sensitive failures, and updated-resource results is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `captions.update` identity and official quota-unit cost of `450`.
- **SC-002**: A client developer can determine in under 1 minute that `captions_update` requires eligible OAuth authorization and a valid caption update body by reading the tool contract alone.
- **SC-003**: A client developer can determine in under 1 minute whether replacement caption media is supported and how it relates to the required update body by reading the tool contract alone.
- **SC-004**: 100% of representative valid `captions_update` requests return an updated caption resource with relevant operation context and returned upstream fields preserved.
- **SC-005**: 100% of representative invalid caption update requests that omit the update body, omit required caption identity, pair media with an invalid update body, or use unsupported update options are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-006**: Reviewers can verify in a single review pass that `captions_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, media-update, mutation response, error, and example standards.
- **SC-007**: A power user can discover `captions_update`, identify the required update body and optional replacement-media inputs, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-008**: Final review evidence includes passing focused `captions_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
