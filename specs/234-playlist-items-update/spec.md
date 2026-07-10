# Feature Specification: Layer 2 Tool `playlistItems_update`

**Feature Branch**: `234-playlist-items-update`  
**Created**: 2026-07-09  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-234, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Playlist Items Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistItems_update` tool to update an existing playlist item using supported playlist-item update data while staying close to the upstream `playlistItems.update` behavior and returned playlist-item resource.

**Why this priority**: This is the core value of YT-234. Layer 2 must expose endpoint-backed playlist-item update behavior for direct playlist maintenance workflows, debugging, and later composition without turning the tool into playlist-item listing, insertion, deletion, playlist search, video enrichment, recommendation, ranking, summarization, or automated curation behavior.

**Independent Test**: Can be tested by invoking `playlistItems_update` with supported part selection, required target playlist-item identity, supported writable update data, and OAuth-backed access, then confirming the caller receives a near-raw updated playlist-item result with metadata identifying the mapped operation, supplied parts, quota cost, update context, and authorization boundary.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, required target playlist-item identity, supported writable update data, and OAuth-backed access, **When** they call `playlistItems_update`, **Then** the result identifies the updated playlist item and preserves operation context for the update request.
2. **Given** a caller updates supported playlist-item fields, **When** the update succeeds, **Then** the result preserves the returned playlist-item fields and update context without fabricating unrelated playlist, video, channel, transcript, or ranking data.
3. **Given** a successful update returns optional or partial playlist-item fields based on selected parts, **When** the caller receives the result, **Then** returned fields are preserved without fabricated data.
4. **Given** a caller wants direct access to playlist-item update behavior, **When** they use `playlistItems_update`, **Then** the tool performs only the playlist-item update operation and is not presented as playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, recommendation, ranking, summarization, or analytics.

---

### User Story 2 - Understand Cost, Authorization, and Update Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `playlistItems_update` before invoking it and immediately understand that it maps to `playlistItems.update`, costs 50 official quota units per call, requires OAuth-backed access, requires part selection, requires target playlist-item identity, and supports only clearly documented writable update inputs.

**Why this priority**: Playlist-item update is quota-bearing, mutation-oriented, and authorization-gated. Callers need quota, auth mode, part selection, writable-field expectations, update semantics, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that mutate playlists.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required part selection, required target identity, supported writable update data, mutation result shape, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistItems_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required part selection, required target playlist-item identity, writable-field expectations, update semantics, and availability state.
2. **Given** an example request is shown for `playlistItems_update`, **When** a caller reads the example, **Then** the quota cost of `50`, selected parts, target playlist-item identity, update payload, OAuth-backed access expectation, and expected updated playlist-item outcome are visible alongside the request shape.
3. **Given** a caller needs playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, ranking, summarization, recommendation, or analytics, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-item update tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Item Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistItems_update` request omits required inputs, supplies invalid part selection, lacks target playlist-item identity, lacks writable update data, includes unsupported resource fields, lacks OAuth-backed access, or asks for behavior outside the playlist-item update endpoint.

**Why this priority**: `playlistItems.update` mutates playlists and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported mutation shapes, access failures, quota failures, missing or unwritable playlist items, upstream rejections, and successful updates without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing target playlist-item identity, missing writable update data, malformed update data, unsupported resource fields, missing OAuth-backed access, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, target playlist-item identity, or writable update data, **When** they call `playlistItems_update`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed part selection, invalid update data, unsupported resource fields, unsupported optional inputs, or out-of-scope workflow requests, **When** they call `playlistItems_update`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistItems_update`, **Then** the response distinguishes access failure from malformed input and from upstream update failure.
4. **Given** a valid OAuth-backed update request is rejected by the upstream service for playlist ownership, missing resource, invalid writable fields, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful update outcomes.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-item update.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides writable update data without target playlist-item identity, target identity without writable update data, or neither required update input; the response must identify the missing update input.
- The caller supplies update data that lacks required writable fields, includes read-only or unsupported fields, conflicts with selected parts, or does not identify a playlist-item update; the response must identify invalid update input.
- The caller attempts to change playlist-item properties outside the documented writable boundary; the response must identify unsupported update behavior rather than silently accepting or ignoring it.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist item; the response must identify access failure rather than reporting a successful update.
- The target playlist item no longer exists, is not writable by the authorized caller, or belongs to a playlist outside the caller's access boundary; the response must distinguish missing-resource or authorization failure from malformed input.
- The upstream success response omits optional fields or returns partial playlist item data according to selected parts; the result must preserve returned fields without fabricating missing playlist-item, video, playlist, or channel data.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistItems_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistItems.update` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required part selection, required target playlist-item identity, supported writable update data, update semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing target playlist-item identity, missing writable update data, invalid update data, unsupported resource fields, unsupported optional inputs, missing or insufficient OAuth-backed access, upstream update failure categorization, and out-of-scope playlist-item or playlist-management requests.
- **Red**: Add failing result-contract checks proving that updated playlist-item fields, selected part context, target identity context, writable update context, quota context, access failures, validation failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistItems_update` tool contract and behavior needed for callers to make supported low-level `playlistItems.update` requests and receive near-raw updated playlist-item results.
- **Green**: Include representative examples for OAuth-backed playlist-item update, missing part validation failure, invalid part validation failure, missing target identity validation failure, missing writable update data validation failure, invalid update data validation failure, unsupported field validation failure, authorization failure, quota or upstream update failure, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistItems_update` request, response, quota, auth, part-selection, target identity, writable update data, update semantics, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, target identity, writable update data, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist-item update paths, and documentation checks for quota/auth/update/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlistItems_update` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, target identity behavior, writable update boundary, mutation result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-234`, the dependency assumptions from YT-134/YT-201/YT-202, focused `playlistItems_update` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistItems_update`.
- **FR-002**: The `playlistItems_update` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistItems` and method `update`.
- **FR-003**: The `playlistItems_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlistItems_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlistItems_update` tool metadata MUST state the OAuth-backed authorization mode for playlist-item update and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistItems_update` input contract MUST preserve the upstream concept of required part selection and MUST document that part selection determines which playlist item properties are returned in the update result.
- **FR-007**: The `playlistItems_update` input contract MUST require supported part selection for each update request.
- **FR-008**: The `playlistItems_update` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-009**: The `playlistItems_update` input contract MUST require target playlist-item identity for each supported update request.
- **FR-010**: The `playlistItems_update` input contract MUST document the required target identity needed to identify the playlist item being updated.
- **FR-011**: The `playlistItems_update` input contract MUST require supported writable update data for each update request.
- **FR-012**: The `playlistItems_update` input contract MUST document the writable-field boundary for playlist-item updates, including which update fields are accepted for this slice and which fields are read-only or unsupported.
- **FR-013**: The `playlistItems_update` input contract MUST reject missing, empty, malformed, read-only, unsupported, or conflicting update data with clear caller-facing validation feedback.
- **FR-014**: The `playlistItems_update` tool MUST support valid OAuth-backed update requests when the caller is authorized to modify the target playlist item.
- **FR-015**: The `playlistItems_update` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-item update result.
- **FR-016**: The `playlistItems_update` result MUST preserve updated playlist item resources, selected part context, target identity context, writable update context, quota context, authorization context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-017**: The `playlistItems_update` tool MUST distinguish successful playlist-item updates from validation failures, authorization failures, quota failures, missing-resource failures, invalid writable-field failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-018**: The `playlistItems_update` tool MUST surface upstream quota, authorization, invalid request, unsupported or invalid writable-field, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `playlistItems_update` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, required target identity, writable update data, unsupported modifier behavior, mutation semantics, and availability state.
- **FR-020**: The `playlistItems_update` contract MUST remain close to the upstream `playlistItems.update` endpoint and MUST NOT add playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or heuristic classification.
- **FR-021**: The `playlistItems_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-022**: The `playlistItems_update` tool MUST rely on the existing Layer 1 `playlistItems.update` capability from YT-134 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-item update request, one missing-part validation failure, one invalid-part validation failure, one missing-target-identity validation failure, one missing-writable-data validation failure, one invalid-update-data validation failure, one unsupported-field validation failure, one authorization failure, one quota or upstream update failure, and one out-of-scope playlist-management request rejection.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, target identity, writable update data, update semantics, failure, and mutation-result requirements, interpret updated playlist-item results, and handle failures for `playlistItems_update` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Items Update Tool**: The public Layer 2 MCP tool named `playlistItems_update`, representing one low-level endpoint-backed playlist-item update operation.
- **Playlist Items Update Request**: The request shape centered on required part selection, required target playlist-item identity, supported writable update data, and any explicitly supported update modifiers.
- **Part Selection**: The caller-selected playlist item resource sections that determine which playlist item properties are returned in the update result.
- **Target Playlist Item Identity**: The identifier and associated context needed to select the existing playlist item being updated.
- **Writable Update Data**: The mutation payload that describes supported playlist-item fields the caller wants to update while excluding read-only or unsupported fields.
- **Authorization Context**: The caller access state required to update playlist item resources without exposing credentials or sensitive authorization details.
- **Updated Playlist Item Resource**: The playlist item record returned after a successful update for the selected parts.
- **Playlist Items Update Result**: The updated playlist item resource, selected parts, target identity context, writable update context, quota context, authorization context, and returned upstream fields produced by a successful `playlistItems_update` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistItems_update` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, and automated curation are outside this low-level playlist-item update tool.

### Assumptions

- YT-134 provides the Layer 1 `playlistItems.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and validation standards this feature must follow.
- `playlistItems_update` is a low-level endpoint-backed tool for direct playlist-item updates, debugging, and power-user workflows; playlist item retrieval, insertion, deletion, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, automated curation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-134 contract treats `part` as required, OAuth-backed access as required, target playlist-item identity as required, writable update data as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, playlist item writability, invalid writable fields, quota, missing resources, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistItems.update` quota cost, auth behavior, part-selection rules, writable-field expectations, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-234 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist-item update, missing part selection, invalid part selection, missing target identity, missing writable update data, invalid update data, unsupported fields, access failure, quota or upstream update failure, and returned updated playlist-item results is sufficient for this slice.

### Dependencies

- `YT-134` Layer 1 `playlistItems.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistItems.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistItems_update` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required target playlist-item identity, writable update data, unsupported modifier boundaries, mutation semantics, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistItems_update`, choose valid inputs, understand the quota and access impact, and prepare a valid first update request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistItems_update` requests return updated playlist-item results with selected part context, target identity context, writable update context, quota context, authorization context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid update requests that omit part selection, use invalid part selection, omit target identity, omit writable update data, use invalid update data, include unsupported fields or modifiers, lack OAuth-backed access, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, invalid writable-field, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful update results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistItems_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistItems_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
