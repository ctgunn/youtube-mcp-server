# Feature Specification: Layer 2 Tool `videos_insert`

**Feature Branch**: `248-videos-insert`  
**Created**: 2026-07-21  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-248, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Videos Through a Public Endpoint Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `videos_insert` tool to create a YouTube video resource with supported metadata and media-upload input while staying close to the upstream `videos.insert` creation behavior.

**Why this priority**: This is the core value of YT-248. Layer 2 must expose direct endpoint-backed `videos.insert` behavior for raw endpoint access, debugging, and controlled upload workflows without turning the tool into a higher-level publishing assistant.

**Independent Test**: Can be tested by invoking `videos_insert` with eligible OAuth authorization, supported video metadata, required part selection, and supported media-upload input, then confirming the caller receives a created video result with mapped operation identity, quota context, access context, upload context, requested parts, and returned video resource data preserved.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides valid video metadata, required part selection, and supported media-upload input, **When** they call `videos_insert`, **Then** the result includes the created video resource in a near-raw endpoint-backed shape.
2. **Given** a caller provides all required creation inputs plus optional supported upload or delegation context, **When** video creation succeeds, **Then** the result preserves the requested operation context, upload context, quota context, access context, and returned video fields.
3. **Given** the upstream creation succeeds but returns only the created video resource rather than a collection, **When** the caller inspects the result, **Then** the single-resource creation outcome is clear and is not presented as a list, search, ranking, recommendation, analytics, or publishing workflow.
4. **Given** product or platform policy constrains upload availability for a release channel, **When** a caller discovers or invokes `videos_insert`, **Then** the tool contract and response make the availability boundary clear instead of implying unrestricted publishing support.

---

### User Story 2 - Understand Cost, OAuth, Upload, and Availability Before Calling (Priority: P2)

As a client developer, I can inspect `videos_insert` before invoking it and immediately understand that it maps to `videos.insert`, costs 1600 official quota units per call, requires eligible OAuth authorization, requires media-upload input, and may carry upload visibility or availability caveats.

**Why this priority**: `videos.insert` is high-cost, permission-sensitive, and upload-oriented. Callers need quota, OAuth, media-upload, examples, availability, and out-of-scope guidance before they spend quota or build workflows around video creation.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1600`, OAuth-required access mode, media-upload requirement, supported creation inputs, availability state, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `videos_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1600`, OAuth requirement, media-upload requirement, and availability state.
2. **Given** an example request is shown for `videos_insert`, **When** a caller reads the example, **Then** the quota cost of `1600`, required OAuth authorization, required media input, requested parts, and expected created-video result are visible alongside the request shape.
3. **Given** a caller needs to use a supported upload mode or delegated content-owner context, **When** they inspect the tool contract, **Then** the supported inputs and their authorization implications are clear before invocation.
4. **Given** a caller expects automatic publishing, video editing, search discovery, transcript extraction, analytics, recommendations, ranking, summarization, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level video creation tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Unsupported Video Creation Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `videos_insert` request omits required metadata, omits media-upload input, lacks eligible OAuth authorization, uses unsupported upload options, or requests behavior outside the video creation endpoint.

**Why this priority**: Video upload is one of the highest-cost YouTube operations in this tool catalog. Clear request boundaries help callers correct invalid inputs before execution and distinguish malformed input, insufficient access, quota failure, policy or availability refusal, upload failure, and successful creation.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including metadata-only creation attempts, media-only creation attempts, missing OAuth authorization, malformed upload input, unsupported upload options, incompatible delegation context, unsupported optional fields, quota failures, and out-of-scope publishing or enrichment requests, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides video metadata but no supported media-upload input, **When** they call `videos_insert`, **Then** the request is rejected with guidance that media-upload input is required.
2. **Given** a caller provides media-upload input but omits required metadata or part selection, **When** they call `videos_insert`, **Then** the request is rejected with guidance identifying the missing creation inputs.
3. **Given** a caller lacks eligible OAuth authorization for the target account or delegated content-owner context, **When** they call `videos_insert`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing resource or successful upload.
4. **Given** a caller requests unsupported upload modes, unsupported optional inputs, automatic publishing, editing, analytics, ranking, recommendation, transcript, or enrichment behavior, **When** they call `videos_insert`, **Then** the request is rejected or clearly categorized as outside the low-level endpoint boundary.

### Edge Cases

- The caller provides video metadata without media-upload input; the request must be rejected before it is treated as a supported video creation attempt.
- The caller provides media-upload input without required video metadata or required part selection; the response must identify the missing creation input.
- The caller supplies empty, malformed, duplicate, conflicting, unknown, or unsupported part selections; the response must identify invalid part input.
- The caller supplies unsupported media format, invalid media descriptors, missing upload size or type information when required, unsupported upload mode, or incompatible upload options; the request must be rejected or clearly flagged as unsupported.
- The caller provides delegated content-owner context without eligible authorization; the response must surface the delegation access requirement.
- The caller has OAuth authorization but lacks permission to create videos for the selected account, channel, or delegated owner; the response must distinguish access failure from missing media input and invalid metadata.
- The caller attempts API-key-only access; the response must make clear that video creation requires OAuth authorization.
- The caller requests automatic public publishing, post-upload editing, thumbnails, captions, playlists, ratings, comments, analytics, transcript retrieval, recommendation, ranking, summarization, or research enrichment; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.
- The upstream service returns quota, authorization, policy, invalid request, upload, unavailable service, deprecated behavior, availability constraint, or unexpected failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The created video resource is returned with only a subset of requested or expected fields; the result must preserve returned fields without fabricating missing video metadata.
- A release or deployment channel does not allow public video upload behavior even though the low-level contract exists; discovery and invocation outcomes must clearly surface that availability boundary.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `videos_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `videos.insert` identity, official quota-unit cost of `1600`, OAuth-required access mode, media-upload requirement, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required part selection, required video metadata, required media-upload input, metadata-only rejection, media-only rejection, missing OAuth authorization, unsupported upload modes, incompatible delegation context, unsupported optional inputs, policy or availability refusal, and out-of-scope workflow requests.
- **Red**: Add failing result-contract checks proving that created video resources, requested operation context, upload context, quota context, access context, availability context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `videos_insert` tool contract and behavior needed for callers to make supported low-level `videos.insert` requests and receive near-raw created video resource results.
- **Green**: Include representative examples for authorized video creation, supported media upload, delegated content-owner context where supported, metadata-only validation failure, media-only validation failure, missing OAuth failure, unsupported upload option failure, quota or upstream failure, availability-constrained behavior, and out-of-scope workflow rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `videos_insert` request, response, quota, access, upload, availability, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, metadata, media-upload, OAuth, delegation, unsupported-option, availability, and out-of-scope behavior validation, integration-style checks for representative successful and failed video creation paths, and documentation checks for quota/OAuth/upload/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `videos_insert` responsibility, inputs, outputs, quota cost, OAuth behavior, media-upload constraints, availability state, mutation result, unsupported behavior, failure categories, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-248`, the dependency assumptions from YT-148/YT-201/YT-202, focused `videos_insert` test output, full-suite output, code-quality output, and any official-documentation or product-availability caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `videos_insert`.
- **FR-002**: The `videos_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `videos` and method `insert`.
- **FR-003**: The `videos_insert` tool metadata MUST record the official quota-unit cost of `1600` per call.
- **FR-004**: The `videos_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `1600` and make the high-cost nature of the operation clear before invocation.
- **FR-005**: The `videos_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present video creation as an API-key-only capability.
- **FR-006**: The `videos_insert` input contract MUST preserve the upstream concepts of required part selection, supported video metadata, supported media-upload input, supported upload modes, supported creation options, and supported delegation context where those concepts are available through the Layer 1 dependency.
- **FR-007**: The `videos_insert` input contract MUST require supported video metadata, required part selection, and supported media-upload input for each creation request.
- **FR-008**: The `videos_insert` input contract MUST document which video metadata fields, requested parts, media inputs, upload modes, and optional creation settings are supported for this low-level tool.
- **FR-009**: The `videos_insert` input contract MUST reject metadata-only creation attempts with clear caller-facing validation feedback.
- **FR-010**: The `videos_insert` input contract MUST reject media-only creation attempts with clear caller-facing validation feedback.
- **FR-011**: The `videos_insert` input contract MUST reject missing, empty, malformed, duplicate, unsupported, ambiguous, or conflicting part selections with clear caller-facing validation feedback.
- **FR-012**: The `videos_insert` input contract MUST reject unsupported media-upload descriptors, unsupported upload modes, unsupported optional parameters, unsupported modifiers, incompatible delegation context, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-013**: The `videos_insert` tool MUST reject or clearly categorize missing, invalid, or insufficient OAuth authorization as an access failure rather than a successful or public video creation result.
- **FR-014**: The `videos_insert` tool MUST document media-upload requirements clearly, including the requirement that upload content is present and compatible with the supported creation contract.
- **FR-015**: The `videos_insert` tool MUST document OAuth requirements clearly, including any supported account, channel, or delegated content-owner access expectations.
- **FR-016**: The `videos_insert` contract MUST document applicable availability and policy caveats, including quota cost, OAuth expectations, upload requirements, supported upload modes, release availability, initial visibility or audit-related caveats where applicable, unsupported option behavior, and failure categories.
- **FR-017**: The `videos_insert` result MUST preserve the created video resource, requested part context, upload context, quota context, access context, availability context where applicable, mapped operation identity, mutation outcome details, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-018**: The `videos_insert` result MUST preserve enough request and result context for callers to identify which metadata, part selection, upload input, upload mode, authorization context, and optional supported settings produced the creation outcome.
- **FR-019**: The `videos_insert` result MUST NOT fabricate video metadata, upload state, publication state, thumbnails, captions, playlists, transcript text, analytics, recommendations, ranking, summaries, enrichment details, or fields that are not returned by the video creation operation.
- **FR-020**: The `videos_insert` tool MUST distinguish successful video creation from validation failures, access failures, quota failures, policy or availability refusals, invalid request failures, upload failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-021**: The `videos_insert` tool MUST surface upstream quota, authorization, policy, invalid request, upload, unavailable service, deprecated behavior, availability constraint, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-022**: The `videos_insert` contract MUST remain close to the upstream `videos.insert` endpoint and MUST NOT add automatic publishing, video metadata update, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated research synthesis, or heuristic classification.
- **FR-023**: The `videos_insert` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, media-upload, validation, error, and example standards established by YT-201 and YT-202.
- **FR-024**: The `videos_insert` tool MUST rely on the existing Layer 1 `videos.insert` capability from YT-148 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-025**: The feature MUST include caller-facing examples for authorized video creation, supported media upload, delegated content-owner context where supported, metadata-only validation failure, media-only validation failure, missing OAuth failure, unsupported upload option failure, quota or upstream failure, availability-constrained behavior, and out-of-scope workflow request rejection.
- **FR-026**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, media-upload requirements, availability boundaries, created-resource results, unsupported behavior, and failure behavior for `videos_insert` without consulting implementation-only artifacts.

### Key Entities

- **Videos Insert Tool**: The public Layer 2 MCP tool named `videos_insert`, representing one low-level endpoint-backed video creation operation.
- **Video Creation Request**: The request shape that combines required part selection, supported video metadata, supported media-upload input, supported upload mode, and any compatible optional creation or delegation settings.
- **Video Metadata**: The caller-provided video resource details accepted by the creation contract, such as title, description, category, tags, status-related fields, or other supported metadata fields.
- **Media Upload Input**: The uploaded video content and related media information required for a valid creation request.
- **Upload Context**: The caller-facing record of which supported media-upload path and compatible upload inputs shaped the creation attempt.
- **Access Context**: The caller access state required for OAuth-only video creation without exposing credentials or sensitive access details.
- **Availability Context**: The caller-facing indication of whether the low-level video creation operation is available, constrained, release-gated, policy-limited, deprecated, or otherwise caveated.
- **Created Video Resource Result**: The returned video resource and operation context produced by a successful `videos_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `videos_insert` invocation costs 1600 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that video creation requires eligible OAuth authorization and may require valid delegated content-owner context for some requests.
- **Upload Requirement Disclosure**: The caller-facing indication that video metadata alone is insufficient and supported media-upload input is required.
- **Unsupported Boundary Guidance**: The caller-facing explanation that automatic publishing, editing, thumbnails, captions, playlists, comments, ratings, transcripts, analytics, ranking, summarization, recommendations, and enrichment are outside this low-level video creation tool.

### Assumptions

- YT-148 provides the Layer 1 `videos.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, media-upload, error, example, and validation standards this feature must follow.
- `videos_insert` is a low-level endpoint-backed tool for direct video creation, debugging, and power-user workflows; higher-level publishing, editing, enrichment, analytics, transcript, recommendation, or research workflows belong to separate endpoint or Layer 3 features.
- OAuth-based access is required for every supported `videos_insert` request, with requests outside that access mode rejected or categorized rather than silently downgraded.
- The public contract should surface any release availability, audit-related, policy, or private-default caveats that affect caller expectations without obscuring the successful created-video outcome when creation is allowed.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, upload behavior, availability state, mutation result behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-248 seed identifies the official quota-unit cost as `1600` for this public Layer 2 contract.

### Dependencies

- `YT-148` Layer 1 `videos.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, validation, mutation, and media-upload conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `videos_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `videos.insert` identity and official quota-unit cost of `1600`.
- **SC-002**: A client developer can determine in under 1 minute that `videos_insert` requires eligible OAuth authorization and supported media-upload input by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, supported metadata inputs, supported upload requirements, availability boundaries, unsupported behavior, and failure categories in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `videos_insert`, understand quota and access impact, identify required creation inputs, and prepare a valid first video creation request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `videos_insert` requests return created-video results with requested part context, upload context, quota context, access context, mapped operation identity, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid video creation requests that omit metadata, omit media-upload input, omit part selection, use invalid part selection, lack eligible OAuth authorization, use unsupported upload options, include incompatible delegation context, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, policy, invalid-request, upload, unavailable-service, deprecated-behavior, availability-constrained, and unexpected upstream scenarios are distinguishable from successful video creation and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `videos_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, OAuth, availability, mutation result, media-upload, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `videos_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
