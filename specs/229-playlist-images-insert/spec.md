# Feature Specification: Layer 2 Tool `playlistImages_insert`

**Feature Branch**: `229-playlist-images-insert`  
**Created**: 2026-07-08  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-229, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Insert Playlist Images Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistImages_insert` tool to create a playlist image using playlist-image metadata and upload content while staying close to the upstream `playlistImages.insert` behavior.

**Why this priority**: This is the core value of YT-229. Layer 2 must expose endpoint-backed playlist-image insertion for direct mutation workflows, debugging, and later composition without turning the tool into thumbnail replacement, playlist management, media transformation, recommendation, ranking, summarization, or enrichment behavior.

**Independent Test**: Can be tested by invoking `playlistImages_insert` with supported part selection, required playlist-image metadata, upload content, and OAuth-backed access, then confirming the caller receives a near-raw created playlist-image result with metadata identifying the mapped operation, supplied parts, quota cost, upload context, and authorization boundary.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, required playlist-image metadata, supported upload content, and OAuth-backed access, **When** they call `playlistImages_insert`, **Then** the result identifies the created playlist image and preserves operation context for the insertion request.
2. **Given** a successful insertion returns optional or partial playlist-image fields based on selected parts, **When** the caller receives the result, **Then** returned fields are preserved without fabricated data.
3. **Given** a caller wants direct access to playlist-image insertion behavior, **When** they use `playlistImages_insert`, **Then** the tool performs only the playlist-image insert operation and is not presented as playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, or enrichment.

---

### User Story 2 - Understand Cost, Authorization, and Upload Requirements Before Calling (Priority: P2)

As a client developer, I can inspect `playlistImages_insert` before invoking it and immediately understand that it maps to `playlistImages.insert`, costs 50 official quota units per call, requires OAuth-backed access, requires part selection, requires playlist-image metadata, and requires supported media-upload content.

**Why this priority**: Playlist image insertion is quota-bearing, mutation-oriented, authorization-gated, and upload-sensitive. Callers need quota, auth mode, part selection, metadata, media-upload requirements, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that mutate playlist images.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required part selection, required metadata, supported upload content, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistImages_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required part selection, required metadata, supported media-upload requirement, and availability state.
2. **Given** an example request is shown for `playlistImages_insert`, **When** a caller reads the example, **Then** the quota cost of `50`, selected parts, metadata payload, upload content requirement, OAuth-backed access expectation, and expected created playlist-image outcome are visible alongside the request shape.
3. **Given** a caller needs playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, ranking, summarization, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-image insertion tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Image Insert Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistImages_insert` request omits required inputs, supplies invalid part selection, lacks metadata, lacks upload content, supplies unsupported upload content, lacks OAuth-backed access, or asks for behavior outside the playlist-image insert endpoint.

**Why this priority**: `playlistImages.insert` creates resources and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported upload shapes, access failures, quota failures, upstream rejections, and successful insertions without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing metadata, malformed metadata, missing upload content, unsupported upload content, missing OAuth-backed access, and out-of-scope image-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, metadata, or upload content, **When** they call `playlistImages_insert`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed part selection, invalid metadata, unsupported upload content, unsupported optional inputs, or out-of-scope workflow requests, **When** they call `playlistImages_insert`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistImages_insert`, **Then** the response distinguishes access failure from malformed input and from upstream insertion failure.
4. **Given** a valid OAuth-backed insertion request is rejected by the upstream service for playlist ownership, media eligibility, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful insertion outcomes.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-image insertion.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides metadata without upload content, upload content without metadata, or neither required input; the response must identify the missing insertion input.
- The caller supplies metadata that lacks required playlist-image creation fields, includes unsupported fields, or conflicts with the selected parts; the response must identify invalid metadata input.
- The caller supplies upload content that is missing, empty, malformed, inaccessible to the request context, too large for the documented boundary, unsupported by media type, or otherwise outside the supported upload contract; the response must identify invalid upload input.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist; the response must identify access failure rather than reporting a successful insertion.
- The upstream success response omits optional fields or returns partial playlist image data according to selected parts; the result must preserve returned fields without fabricating missing playlist-image data.
- The upstream service returns quota, authorization, invalid request, media eligibility, missing resource, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistImages_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistImages.insert` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required part selection, required metadata, media-upload requirement, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing metadata, invalid metadata, missing upload content, unsupported upload content, unsupported optional inputs, missing or insufficient OAuth-backed access, upstream insertion failure categorization, and out-of-scope playlist-image or playlist-management requests.
- **Red**: Add failing result-contract checks proving that created playlist-image fields, selected part context, insertion metadata context, upload context, quota context, access failures, validation failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistImages_insert` tool contract and behavior needed for callers to make supported low-level `playlistImages.insert` requests and receive near-raw created playlist-image results.
- **Green**: Include representative examples for OAuth-backed playlist-image insertion, missing part validation failure, invalid part validation failure, missing metadata validation failure, missing upload validation failure, unsupported upload validation failure, authorization failure, quota or upstream insertion failure, and out-of-scope image-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistImages_insert` request, response, quota, auth, part-selection, metadata, upload, validation, error, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, metadata, upload, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist-image insertion paths, and documentation checks for quota/auth/upload/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `playlistImages_insert` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, metadata behavior, upload behavior, mutation result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-229`, the dependency assumptions from YT-129/YT-201/YT-202, focused `playlistImages_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistImages_insert`.
- **FR-002**: The `playlistImages_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistImages` and method `insert`.
- **FR-003**: The `playlistImages_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlistImages_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlistImages_insert` tool metadata MUST state the OAuth-backed authorization mode for playlist-image insertion and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistImages_insert` input contract MUST preserve the upstream concept of required part selection and MUST document that part selection determines which playlist image properties are returned in the creation result.
- **FR-007**: The `playlistImages_insert` input contract MUST require supported part selection for each insertion request.
- **FR-008**: The `playlistImages_insert` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-009**: The `playlistImages_insert` input contract MUST require playlist-image creation metadata for each supported insertion request.
- **FR-010**: The `playlistImages_insert` input contract MUST document the required playlist-image metadata needed to associate the new image with the intended playlist and insertion context.
- **FR-011**: The `playlistImages_insert` input contract MUST reject missing, empty, malformed, unsupported, or conflicting metadata with clear caller-facing validation feedback.
- **FR-012**: The `playlistImages_insert` input contract MUST require supported media-upload content for each insertion request.
- **FR-013**: The `playlistImages_insert` input contract MUST document the supported media-upload boundary, including required upload presence, accepted upload descriptors, media-type expectations, and unsupported upload shapes.
- **FR-014**: The `playlistImages_insert` input contract MUST reject missing, empty, malformed, inaccessible, oversized, unsupported, or conflicting upload content with clear caller-facing validation feedback.
- **FR-015**: The `playlistImages_insert` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-image insertion result.
- **FR-016**: The `playlistImages_insert` result MUST preserve created playlist image resources, selected part context, insertion metadata context, upload context, quota context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-017**: The `playlistImages_insert` tool MUST distinguish successful playlist-image insertions from validation failures, authorization failures, quota failures, media eligibility failures, missing-resource failures, unavailable service responses, and unexpected upstream failures.
- **FR-018**: The `playlistImages_insert` tool MUST surface upstream quota, authorization, invalid request, media eligibility, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `playlistImages_insert` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, required metadata, required media-upload behavior, unsupported modifier behavior, mutation semantics, and availability state.
- **FR-020**: The `playlistImages_insert` contract MUST remain close to the upstream `playlistImages.insert` endpoint and MUST NOT add playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-021**: The `playlistImages_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, upload, and example standards established by YT-201 and YT-202.
- **FR-022**: The `playlistImages_insert` tool MUST rely on the existing Layer 1 `playlistImages.insert` capability from YT-129 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-image insertion request, one missing-part validation failure, one invalid-part validation failure, one missing-metadata validation failure, one invalid-metadata validation failure, one missing-upload validation failure, one unsupported-upload validation failure, one authorization failure, one quota or upstream insertion failure, and one out-of-scope image-management request rejection.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, metadata, media-upload, failure, and mutation-result requirements, interpret created playlist-image results, and handle failures for `playlistImages_insert` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Images Insert Tool**: The public Layer 2 MCP tool named `playlistImages_insert`, representing one low-level endpoint-backed playlist-image insertion operation.
- **Playlist Images Insert Request**: The request shape centered on required part selection, required playlist-image metadata, required upload content, and any explicitly supported insertion modifiers.
- **Part Selection**: The caller-selected playlist image resource sections that determine which playlist image properties are returned in the creation result.
- **Playlist Image Creation Metadata**: The metadata payload that identifies the playlist-image insertion intent, including the target playlist association and other supported creation fields.
- **Playlist Image Upload Content**: The media-upload portion of the request that carries the image content needed to create the playlist image and whose supported shape must be documented and validated.
- **Authorization Context**: The caller access state required to insert playlist image resources without exposing credentials or sensitive authorization details.
- **Created Playlist Image Resource**: The playlist image record returned after a successful insertion for the selected parts.
- **Playlist Images Insert Result**: The created playlist image resource, selected parts, metadata context, upload context, quota context, and returned upstream fields produced by a successful `playlistImages_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistImages_insert` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, ranking, summarization, and enrichment are outside this low-level playlist-image insertion tool.

### Assumptions

- YT-129 provides the Layer 1 `playlistImages.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, upload, example, and validation standards this feature must follow.
- `playlistImages_insert` is a low-level endpoint-backed tool for direct playlist-image insertion, debugging, and power-user workflows; playlist image retrieval, update, deletion, playlist management, analytics, ranking, summarization, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-129 contract treats `part` as required, OAuth-backed access as required, playlist-image metadata as required, media-upload content as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, image eligibility, quota, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistImages.insert` quota cost, auth behavior, part-selection rules, metadata rules, media-upload behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-229 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist-image insertion, missing part selection, invalid part selection, missing metadata, invalid metadata, missing upload content, unsupported upload content, access failure, quota or upstream insertion failure, and returned created playlist-image results is sufficient for this slice.

### Dependencies

- `YT-129` Layer 1 `playlistImages.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, upload, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistImages_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistImages.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistImages_insert` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required metadata, required media-upload content, unsupported modifier boundaries, mutation semantics, and out-of-scope image-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistImages_insert`, choose valid inputs, understand the quota and access impact, and prepare a valid first insertion request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistImages_insert` requests return created playlist-image results with selected part context, metadata context, upload context, quota context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid insertion requests that omit part selection, use invalid part selection, omit metadata, use invalid metadata, omit upload content, use unsupported upload content, include unsupported modifiers, lack OAuth-backed access, or request out-of-scope image-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, media eligibility, missing-resource, unavailable-service, and unexpected upstream scenarios are distinguishable from successful insertion results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistImages_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, upload, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistImages_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
