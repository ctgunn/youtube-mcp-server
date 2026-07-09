# Feature Specification: Layer 2 Tool `playlistImages_update`

**Feature Branch**: `230-playlist-images-update`  
**Created**: 2026-07-08  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-230, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Playlist Images Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistImages_update` tool to update an existing playlist image using playlist-image metadata and replacement media content while staying close to the upstream `playlistImages.update` behavior.

**Why this priority**: This is the core value of YT-230. Layer 2 must expose endpoint-backed playlist-image update behavior for direct mutation workflows, debugging, and later composition without turning the tool into listing, insertion, deletion, thumbnail management, playlist management, media transformation, recommendation, ranking, summarization, or enrichment behavior.

**Independent Test**: Can be tested by invoking `playlistImages_update` with supported part selection, required playlist-image update metadata, supported replacement media content, and OAuth-backed access, then confirming the caller receives a near-raw updated playlist-image result with metadata identifying the mapped operation, supplied parts, quota cost, upload context, and authorization boundary.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, required playlist-image update metadata for an existing image, supported replacement media content, and OAuth-backed access, **When** they call `playlistImages_update`, **Then** the result identifies the updated playlist image and preserves operation context for the update request.
2. **Given** a successful update returns optional or partial playlist-image fields based on selected parts, **When** the caller receives the result, **Then** returned fields are preserved without fabricated data.
3. **Given** a caller wants direct access to playlist-image update behavior, **When** they use `playlistImages_update`, **Then** the tool performs only the playlist-image update operation and is not presented as playlist image listing, insertion, deletion, thumbnail management, playlist management, analytics, recommendation, ranking, summarization, or enrichment.

---

### User Story 2 - Understand Cost, Authorization, Update Semantics, and Upload Requirements Before Calling (Priority: P2)

As a client developer, I can inspect `playlistImages_update` before invoking it and immediately understand that it maps to `playlistImages.update`, costs 50 official quota units per call, requires OAuth-backed access, requires part selection, requires update metadata for the target playlist image, and requires supported media-upload content.

**Why this priority**: Playlist image update is quota-bearing, mutation-oriented, authorization-gated, and upload-sensitive. Callers need quota, auth mode, part selection, update semantics, required metadata, media-upload requirements, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that mutate playlist images.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required part selection, required update metadata, supported replacement media content, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistImages_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required part selection, required update metadata, supported media-upload requirement, update semantics, and availability state.
2. **Given** an example request is shown for `playlistImages_update`, **When** a caller reads the example, **Then** the quota cost of `50`, selected parts, update metadata payload, upload content requirement, OAuth-backed access expectation, and expected updated playlist-image outcome are visible alongside the request shape.
3. **Given** a caller needs playlist image listing, insertion, deletion, thumbnail management, playlist management, analytics, ranking, summarization, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-image update tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Image Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistImages_update` request omits required inputs, supplies invalid part selection, lacks target update metadata, lacks upload content, supplies unsupported upload content, lacks OAuth-backed access, or asks for behavior outside the playlist-image update endpoint.

**Why this priority**: `playlistImages.update` mutates existing media and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported upload shapes, access failures, quota failures, missing or unwritable playlist images, upstream rejections, and successful updates without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing target image identity, missing update metadata, malformed metadata, missing upload content, unsupported upload content, missing OAuth-backed access, and out-of-scope image-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, target image identity, update metadata, or upload content, **When** they call `playlistImages_update`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed part selection, invalid metadata, unsupported upload content, unsupported optional inputs, or out-of-scope workflow requests, **When** they call `playlistImages_update`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistImages_update`, **Then** the response distinguishes access failure from malformed input and from upstream update failure.
4. **Given** a valid OAuth-backed update request is rejected by the upstream service for playlist ownership, missing resource, media eligibility, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful update outcomes.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-image update.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides update metadata without upload content, upload content without target image identity, upload content without update metadata, or none of the required update inputs; the response must identify the missing update input.
- The caller supplies metadata that lacks the playlist image identifier, lacks required update fields, includes unsupported fields, or conflicts with the selected parts; the response must identify invalid metadata input.
- The caller supplies upload content that is missing, empty, malformed, inaccessible to the request context, too large for the documented boundary, unsupported by media type, or otherwise outside the supported upload contract; the response must identify invalid upload input.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist image; the response must identify access failure rather than reporting a successful update.
- The target playlist image no longer exists, is not writable by the authorized caller, or belongs to a playlist outside the caller's access boundary; the response must distinguish missing-resource or authorization failure from malformed input.
- The upstream success response omits optional fields or returns partial playlist image data according to selected parts; the result must preserve returned fields without fabricating missing playlist-image data.
- The upstream service returns quota, authorization, invalid request, media eligibility, missing resource, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist image listing, insertion, deletion, thumbnail management, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistImages_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistImages.update` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required part selection, required update metadata, media-upload requirement, update semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing target image identity, missing update metadata, invalid metadata, missing upload content, unsupported upload content, unsupported optional inputs, missing or insufficient OAuth-backed access, upstream update failure categorization, and out-of-scope playlist-image or playlist-management requests.
- **Red**: Add failing result-contract checks proving that updated playlist-image fields, selected part context, update metadata context, upload context, quota context, access failures, validation failures, missing-resource failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistImages_update` tool contract and behavior needed for callers to make supported low-level `playlistImages.update` requests and receive near-raw updated playlist-image results.
- **Green**: Include representative examples for OAuth-backed playlist-image update, missing part validation failure, invalid part validation failure, missing target identity validation failure, missing metadata validation failure, missing upload validation failure, unsupported upload validation failure, authorization failure, missing-resource failure, quota or upstream update failure, and out-of-scope image-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistImages_update` request, response, quota, auth, part-selection, metadata, upload, update semantics, validation, error, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, metadata, upload, unsupported-option, target identity, and access-boundary validation, integration-style checks for representative successful and failed playlist-image update paths, and documentation checks for quota/auth/upload/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `playlistImages_update` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, metadata behavior, upload behavior, mutation result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-230`, the dependency assumptions from YT-130/YT-201/YT-202, focused `playlistImages_update` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistImages_update`.
- **FR-002**: The `playlistImages_update` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistImages` and method `update`.
- **FR-003**: The `playlistImages_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlistImages_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlistImages_update` tool metadata MUST state the OAuth-backed authorization mode for playlist-image update and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistImages_update` input contract MUST preserve the upstream concept of required part selection and MUST document that part selection determines which playlist image properties are returned in the update result.
- **FR-007**: The `playlistImages_update` input contract MUST require supported part selection for each update request.
- **FR-008**: The `playlistImages_update` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-009**: The `playlistImages_update` input contract MUST require playlist-image update metadata for each supported update request.
- **FR-010**: The `playlistImages_update` input contract MUST document the required playlist-image metadata needed to identify the playlist image being updated and describe the intended update.
- **FR-011**: The `playlistImages_update` input contract MUST reject missing, empty, malformed, unsupported, or conflicting metadata with clear caller-facing validation feedback.
- **FR-012**: The `playlistImages_update` input contract MUST require supported media-upload content for each update request.
- **FR-013**: The `playlistImages_update` input contract MUST document the supported media-upload boundary, including required upload presence, accepted upload descriptors, media-type expectations, and unsupported upload shapes.
- **FR-014**: The `playlistImages_update` input contract MUST reject missing, empty, malformed, inaccessible, oversized, unsupported, or conflicting upload content with clear caller-facing validation feedback.
- **FR-015**: The `playlistImages_update` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-image update result.
- **FR-016**: The `playlistImages_update` result MUST preserve updated playlist image resources, selected part context, update metadata context, upload context, quota context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-017**: The `playlistImages_update` tool MUST distinguish successful playlist-image updates from validation failures, authorization failures, missing-resource failures, quota failures, media eligibility failures, unavailable service responses, and unexpected upstream failures.
- **FR-018**: The `playlistImages_update` tool MUST surface upstream quota, authorization, invalid request, media eligibility, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `playlistImages_update` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, required update metadata, required media-upload behavior, unsupported modifier behavior, mutation semantics, and availability state.
- **FR-020**: The `playlistImages_update` contract MUST remain close to the upstream `playlistImages.update` endpoint and MUST NOT add playlist image listing, insertion, deletion, thumbnail management, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-021**: The `playlistImages_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, upload, and example standards established by YT-201 and YT-202.
- **FR-022**: The `playlistImages_update` tool MUST rely on the existing Layer 1 `playlistImages.update` capability from YT-130 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-image update request, one missing-part validation failure, one invalid-part validation failure, one missing-target-identity validation failure, one missing-metadata validation failure, one invalid-metadata validation failure, one missing-upload validation failure, one unsupported-upload validation failure, one authorization failure, one missing-resource or quota upstream failure, and one out-of-scope image-management request rejection.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, metadata, media-upload, update semantics, failure, and mutation-result requirements, interpret updated playlist-image results, and handle failures for `playlistImages_update` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Images Update Tool**: The public Layer 2 MCP tool named `playlistImages_update`, representing one low-level endpoint-backed playlist-image update operation.
- **Playlist Images Update Request**: The request shape centered on required part selection, required playlist-image update metadata, required upload content, and any explicitly supported update modifiers.
- **Part Selection**: The caller-selected playlist image resource sections that determine which playlist image properties are returned in the update result.
- **Playlist Image Update Metadata**: The metadata payload that identifies the playlist image to update and describes supported resource fields for the update.
- **Playlist Image Upload Content**: The media-upload portion of the request that carries the replacement image content needed to update the playlist image and whose supported shape must be documented and validated.
- **Authorization Context**: The caller access state required to update playlist image resources without exposing credentials or sensitive authorization details.
- **Updated Playlist Image Resource**: The playlist image record returned after a successful update for the selected parts.
- **Playlist Images Update Result**: The updated playlist image resource, selected parts, metadata context, upload context, quota context, and returned upstream fields produced by a successful `playlistImages_update` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistImages_update` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist image listing, insertion, deletion, thumbnail management, playlist management, analytics, ranking, summarization, and enrichment are outside this low-level playlist-image update tool.

### Assumptions

- YT-130 provides the Layer 1 `playlistImages.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, upload, example, and validation standards this feature must follow.
- `playlistImages_update` is a low-level endpoint-backed tool for direct playlist-image update, debugging, and power-user workflows; playlist image retrieval, insertion, deletion, playlist management, analytics, ranking, summarization, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-130 contract treats `part` as required, OAuth-backed access as required, playlist-image update metadata as required, media-upload content as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, image writability, image eligibility, quota, missing resource, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistImages.update` quota cost, auth behavior, part-selection rules, metadata rules, media-upload behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-230 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist-image update, missing part selection, invalid part selection, missing target identity, missing metadata, invalid metadata, missing upload content, unsupported upload content, access failure, missing-resource or upstream update failure, and returned updated playlist-image results is sufficient for this slice.

### Dependencies

- `YT-130` Layer 1 `playlistImages.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, upload, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistImages_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistImages.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistImages_update` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required update metadata, required media-upload content, unsupported modifier boundaries, mutation semantics, and out-of-scope image-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistImages_update`, choose valid inputs, understand the quota and access impact, and prepare a valid first update request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistImages_update` requests return updated playlist-image results with selected part context, metadata context, upload context, quota context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid update requests that omit part selection, use invalid part selection, omit target identity, omit metadata, use invalid metadata, omit upload content, use unsupported upload content, include unsupported modifiers, lack OAuth-backed access, or request out-of-scope image-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, media eligibility, missing-resource, unavailable-service, and unexpected upstream scenarios are distinguishable from successful update results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistImages_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, upload, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistImages_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
