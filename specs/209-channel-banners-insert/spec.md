# Feature Specification: Layer 2 Tool `channelBanners_insert`

**Feature Branch**: `209-channel-banners-insert`  
**Created**: 2026-06-07  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-209, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Channel Banner Assets Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `channelBanners_insert` tool to upload a channel banner asset while staying close to the upstream `channelBanners.insert` media-upload and returned-resource behavior.

**Why this priority**: This is the core value of YT-209. Layer 2 must expose endpoint-backed channel banner upload for direct branding workflows, debugging, and later composition without turning it into a higher-level image editing or full channel branding flow.

**Independent Test**: Can be tested by invoking `channelBanners_insert` with eligible authorization and supported banner media input, then confirming the caller receives a near-raw upload result and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for channel branding operations, **When** they call `channelBanners_insert` with supported banner media input, **Then** the result includes the uploaded channel banner resource or upload outcome in a near-raw endpoint-backed shape.
2. **Given** the upstream upload succeeds and returns banner resource fields or upload-location details, **When** the caller inspects the result, **Then** the returned fields and requested operation context are preserved without fabricating additional channel branding state.
3. **Given** a caller wants direct access to channel banner upload behavior, **When** they use `channelBanners_insert`, **Then** the tool performs only the banner upload operation and is not presented as channel profile editing, image resizing, banner previewing, or full branding publication.

---

### User Story 2 - Understand Cost, Authorization, and Upload Rules Before Calling (Priority: P2)

As a client developer, I can inspect `channelBanners_insert` before invoking it and immediately understand that it maps to `channelBanners.insert`, costs 50 official quota units per call, requires eligible OAuth authorization, and requires supported banner media-upload input.

**Why this priority**: Channel banner upload is quota-bearing, permission-sensitive, and upload-oriented. Callers need quota, OAuth, media, and endpoint identity visibility in discovery, descriptions, and examples so they can avoid unauthorized attempts, accidental quota spend, and metadata-only requests.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the upstream identity, quota cost of `50`, OAuth requirement, media-upload requirement, optional management context, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `channelBanners_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, media-upload requirement, and availability state.
2. **Given** an example request is shown for `channelBanners_insert`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible authorization plus supported banner media input are visible alongside the request shape.
3. **Given** a caller needs to upload a banner in a managed or delegated channel context, **When** they inspect the tool contract, **Then** the supported management context and authorization implications are clear before invocation.

---

### User Story 3 - Reject Unsupported Banner Upload Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `channelBanners_insert` request is missing banner media input, lacks eligible authorization, or uses unsupported upload or management context, so I can correct the request without guessing which banner-upload rule was violated.

**Why this priority**: `channelBanners.insert` combines mutation-like upload behavior, OAuth authorization, and media constraints. Clear validation protects callers from confusing failed upload attempts while keeping the tool faithful to the endpoint instead of inventing higher-level image repair or channel update behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing media input, unsupported media shape, unsupported upload options, missing authorization, and invalid delegated management context, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no banner media input, **When** they call `channelBanners_insert`, **Then** the request is rejected with guidance that supported banner media input is required.
2. **Given** a caller provides unsupported media input or upload options, **When** they call `channelBanners_insert`, **Then** the request is rejected or clearly flagged with the supported endpoint rules.
3. **Given** a caller lacks eligible OAuth authorization for the target management context, **When** they call `channelBanners_insert`, **Then** the response clearly identifies the access requirement rather than presenting the request as an upload-format failure.

### Edge Cases

- The caller omits banner media input; the request must be rejected before it is treated as a supported banner upload attempt.
- The caller provides empty, unreadable, malformed, unsupported, or conflicting banner media input; the response must identify the invalid media input.
- The caller has OAuth authorization but lacks rights for the requested channel or management context; the response must distinguish access failure from invalid media input.
- The caller supplies delegated or managed-channel context without corresponding eligible authorization; the response must surface the management-context access requirement.
- The caller supplies unsupported upload options, channel update fields, profile image fields, or image-editing instructions; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream service returns quota, authorization, invalid request, upload, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The upstream upload result omits optional fields; the result must preserve the returned fields without fabricating missing banner resource data.
- The caller expects the uploaded banner to be resized, previewed, selected as the channel's active banner, combined with channel metadata updates, or applied to multiple channels; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `channelBanners_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `channelBanners.insert` identity, official quota-unit cost of `50`, OAuth-required auth mode, media-upload requirement, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required banner media input, optional supported management context, missing-media rejection, invalid-media rejection, unsupported upload option rejection, and OAuth access guidance.
- **Red**: Add failing result-contract checks proving that uploaded banner resource fields or upload outcome details, requested operation context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `channelBanners_insert` tool contract and behavior needed for callers to make supported low-level `channelBanners.insert` requests and receive near-raw banner upload results.
- **Green**: Include representative examples for authorized banner upload, managed or delegated channel context where supported, missing-media validation failure, invalid-media validation failure, unsupported option validation failure, and authorization-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `channelBanners_insert` request, response, quota, auth, upload, management-context, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for banner media and management-context validation, integration-style checks for representative successful and failed banner upload paths, and documentation checks for quota/auth/upload/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `channelBanners_insert` responsibility, inputs, outputs, quota cost, auth behavior, media-upload constraints, upload result, and management-context notes.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-209`, the dependency assumptions from YT-109/YT-201/YT-202, focused `channelBanners_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `channelBanners_insert`.
- **FR-002**: The `channelBanners_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `channelBanners` and method `insert`.
- **FR-003**: The `channelBanners_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `channelBanners_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `channelBanners_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present channel banner upload as an API-key-only capability.
- **FR-006**: The `channelBanners_insert` input contract MUST preserve the upstream concepts of required banner media input, supported upload-related options, and supported channel or management context where those concepts are supported.
- **FR-007**: The `channelBanners_insert` input contract MUST require supported banner media input for each upload request.
- **FR-008**: The `channelBanners_insert` tool MUST support valid banner upload requests with no optional management context when the caller's authorization is sufficient.
- **FR-009**: The `channelBanners_insert` tool MUST support valid banner upload requests that include supported managed or delegated channel context.
- **FR-010**: The `channelBanners_insert` tool MUST reject missing, empty, malformed, unsupported, or conflicting banner media input with clear caller-facing validation feedback.
- **FR-011**: The `channelBanners_insert` tool MUST reject unsupported upload options, unsupported channel update fields, unsupported profile image fields, image-editing instructions, or unsupported management context with clear caller-facing validation feedback.
- **FR-012**: The `channelBanners_insert` tool MUST reject requests that require authorized or delegated access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-013**: The `channelBanners_insert` result MUST preserve uploaded banner resource fields or upload outcome details, relevant request context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-014**: The `channelBanners_insert` tool MUST surface upstream quota, authorization, invalid request, upload, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-015**: The `channelBanners_insert` contract MUST remain close to the upstream `channelBanners.insert` endpoint and MUST NOT add higher-level channel profile editing, banner resizing, banner preview generation, full branding publication, bulk channel updates, enrichment, or heuristic interpretation.
- **FR-016**: The `channelBanners_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation or upload result, media-upload, management-context, error, and example standards established by YT-201 and YT-202.
- **FR-017**: The `channelBanners_insert` tool MUST rely on the existing Layer 1 `channelBanners.insert` capability from YT-109 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-018**: The feature MUST include caller-facing examples for at least one authorized banner upload request, one supported managed or delegated channel scenario, one missing-media validation failure, one invalid-media validation failure, one unsupported option validation failure, and one authorization-sensitive failure.
- **FR-019**: The feature MUST include validation evidence that clients can discover, call, understand upload and OAuth requirements, interpret banner upload results, and handle failures for `channelBanners_insert` without consulting implementation-only artifacts.

### Key Entities

- **Channel Banners Insert Tool**: The public Layer 2 MCP tool named `channelBanners_insert`, representing one low-level endpoint-backed channel banner upload operation.
- **Channel Banner Upload Request**: The request shape that combines required banner media input, supported upload-related options, and any supported channel or management context.
- **Banner Media Input**: The caller-provided channel banner asset and related media information required for a valid upload request.
- **Channel or Management Context**: Optional caller-provided context used when an authorized managed-channel or delegated flow is supported for the upload request.
- **Banner Upload Result**: The returned banner resource fields, upload outcome details, and operation context produced by a successful `channelBanners_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `channelBanners_insert` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that channel banner upload requires eligible OAuth authorization and may require valid management context for some requests.
- **Upload Requirement Disclosure**: The caller-facing indication that a supported banner media input is required and that metadata-only or channel-update-only requests are outside this tool's scope.

### Assumptions

- YT-109 provides the Layer 1 `channelBanners.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation or upload result, media-upload, error, example, and validation standards this feature must follow.
- `channelBanners_insert` is a low-level endpoint-backed tool for direct banner upload, debugging, and power-user workflows; higher-level branding publication, image transformation, preview generation, enrichment, or research workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `channelBanners.insert` quota cost, auth behavior, upload behavior, availability state, management-context behavior, and upload result behavior, with any discovered caveats recorded explicitly.
- Representative coverage of authorized banner upload, supported managed or delegated channel context, missing media input, invalid media input, unsupported upload options, authorization-sensitive failures, and banner upload results is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `channelBanners_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `channelBanners.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `channelBanners_insert` requires eligible OAuth authorization and supported banner media input by reading the tool contract alone.
- **SC-003**: A client developer can determine in under 1 minute which managed or delegated channel context is supported, if any, and what authorization implication it has by reading the tool contract alone.
- **SC-004**: 100% of representative valid `channelBanners_insert` requests return banner upload results with relevant operation context and returned upstream fields preserved.
- **SC-005**: 100% of representative invalid banner upload requests that omit media input, provide invalid media input, use unsupported upload options, or lack eligible permission are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-006**: Reviewers can verify in a single review pass that `channelBanners_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, media-upload, upload result, management-context, error, and example standards.
- **SC-007**: A power user can discover `channelBanners_insert`, identify the required banner media input and OAuth requirement, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-008**: Final review evidence includes passing focused `channelBanners_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
