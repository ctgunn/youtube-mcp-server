# Feature Specification: Layer 2 Tool `playlists_update`

**Feature Branch**: `238-playlists-update`  
**Created**: 2026-07-11  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-238, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Playlists Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlists_update` tool to update an existing playlist using supported playlist update data while staying close to the upstream `playlists.update` behavior and returned playlist resource.

**Why this priority**: This is the core value of YT-238. Layer 2 must expose endpoint-backed playlist update behavior for direct playlist maintenance workflows, debugging, and advanced automation without turning the tool into playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, recommendation, ranking, summarization, analytics, or higher-level playlist-management behavior.

**Independent Test**: Can be tested by invoking `playlists_update` with supported part selection, required target playlist identity, supported writable playlist details, and OAuth-backed access, then confirming the caller receives a near-raw updated-playlist result with metadata identifying the mapped upstream operation, selected parts, quota cost, update context, and authorization boundary.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, required target playlist identity, supported writable playlist details, and OAuth-backed access, **When** they call `playlists_update`, **Then** the result identifies the updated playlist and preserves operation context for the update request.
2. **Given** a caller updates supported playlist fields, **When** the update succeeds, **Then** the result preserves returned playlist fields and update context without fabricating playlist items, videos, images, transcripts, analytics, or recommendations.
3. **Given** a successful update returns optional or partial playlist fields based on selected parts, **When** the caller receives the result, **Then** returned fields are preserved without fabricated data.
4. **Given** a caller wants direct access to playlist update behavior, **When** they use `playlists_update`, **Then** the tool performs only the playlist update operation and is not presented as playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, ranking, summarization, analytics, or recommendation.

---

### User Story 2 - Understand Cost, Authorization, and Update Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `playlists_update` before invoking it and immediately understand that it maps to `playlists.update`, costs 50 official quota units per call, requires OAuth-backed user authorization, requires part selection, requires target playlist identity, and supports only clearly documented writable update inputs.

**Why this priority**: Playlist update is quota-bearing, mutation-oriented, and authorization-gated. Callers need quota, auth mode, part selection, writable-field expectations, update semantics, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or mutate user-visible playlists.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required part selection, required target playlist identity, supported writable update data, mutation result shape, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlists_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required part selection, required target playlist identity, writable-field expectations, update semantics, and availability state.
2. **Given** an example request is shown for `playlists_update`, **When** a caller reads the example, **Then** the quota cost of `50`, selected parts, target playlist identity, update payload, OAuth-backed access expectation, mutation warning, and expected updated-playlist outcome are visible alongside the request shape.
3. **Given** a caller needs playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, transcript retrieval, ranking, summarization, recommendation, or analytics, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist update tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlists_update` request omits required inputs, supplies invalid part selection, lacks target playlist identity, lacks writable update data, includes unsupported resource fields, lacks OAuth-backed access, or asks for behavior outside the playlist update endpoint.

**Why this priority**: `playlists.update` mutates user-visible playlists and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported mutation shapes, access failures, quota failures, missing or unwritable playlists, upstream rejections, and successful updates without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing target playlist identity, missing writable update data, malformed update data, unsupported resource fields, missing OAuth-backed access, upstream update rejection, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, target playlist identity, or writable update data, **When** they call `playlists_update`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed part selection, invalid update data, read-only fields, unsupported resource fields, unsupported optional inputs, or out-of-scope workflow requests, **When** they call `playlists_update`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlists_update`, **Then** the response distinguishes access failure from malformed input and from upstream update failure.
4. **Given** a valid OAuth-backed update request is rejected by the upstream service for playlist ownership, missing resource, invalid writable fields, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful update outcomes.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist update.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides writable update data without target playlist identity, target identity without writable update data, or neither required update input; the response must identify the missing update input.
- The caller supplies update data that lacks required writable fields, includes read-only or unsupported fields, conflicts with selected parts, or does not identify a playlist update; the response must identify invalid update input.
- The caller attempts to change playlist properties outside the documented writable boundary; the response must identify unsupported update behavior rather than silently accepting or ignoring it.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist; the response must identify access failure rather than reporting a successful update.
- The target playlist no longer exists, is not writable by the authorized caller, or belongs to a channel outside the caller's access boundary; the response must distinguish missing-resource or authorization failure from malformed input.
- The upstream success response omits optional fields or returns partial playlist data according to selected parts; the result must preserve returned fields without fabricating missing playlist, playlist item, video, channel, image, transcript, analytics, or recommendation data.
- A caller repeats an update request after a timeout or unclear upstream outcome; the tool contract must avoid promising conflict detection or rollback unless the shared contract explicitly supports it.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist listing, creation, deletion, playlist item insertion, playlist item update, playlist item deletion, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlists_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlists.update` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required part selection, required target playlist identity, supported writable update data, update semantics, mutation warning, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing target playlist identity, missing writable update data, invalid update data, read-only or unsupported resource fields, unsupported optional inputs, missing or insufficient OAuth-backed access, upstream update failure categorization, repeat-request caveat visibility, and out-of-scope playlist-management requests.
- **Red**: Add failing result-contract checks proving that updated playlist fields, selected part context, target identity context, writable update context, quota context, access failures, validation failures, mutation outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlists_update` tool contract and behavior needed for callers to make supported low-level `playlists.update` requests and receive near-raw updated playlist results.
- **Green**: Include representative examples for OAuth-backed playlist update, update with supported optional playlist details, missing part validation failure, invalid part validation failure, missing target identity validation failure, missing writable data validation failure, invalid update data validation failure, unsupported field validation failure, authorization failure, quota or upstream update failure, repeat-request caveat, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlists_update` request, response, quota, auth, part-selection, target identity, writable update data, update semantics, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, target identity, writable update data, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist update paths, and documentation checks for quota/auth/update/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlists_update` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, target identity behavior, writable update boundary, mutation result shape, unsupported workflow boundary, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-238`, the dependency assumptions from YT-138/YT-201/YT-202, focused `playlists_update` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlists_update`.
- **FR-002**: The `playlists_update` tool definition MUST identify its mapped upstream operation as YouTube resource `playlists` and method `update`.
- **FR-003**: The `playlists_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlists_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlists_update` tool metadata MUST state the OAuth-backed authorization mode for playlist update and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlists_update` input contract MUST preserve the upstream concepts of required part selection, target playlist identity, writable playlist details, and updated playlist resource output where those concepts are supported by the Layer 1 dependency.
- **FR-007**: The `playlists_update` input contract MUST require supported part selection for each update request and MUST document that part selection determines which playlist properties are accepted and returned.
- **FR-008**: The `playlists_update` input contract MUST require target playlist identity for each supported update request.
- **FR-009**: The `playlists_update` input contract MUST document the required target identity needed to identify the playlist being updated.
- **FR-010**: The `playlists_update` input contract MUST require supported writable playlist details for each update request.
- **FR-011**: The `playlists_update` input contract MUST document the writable-field boundary for playlist updates, including which update fields are accepted for this slice and which fields are read-only or unsupported.
- **FR-012**: The `playlists_update` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-013**: The `playlists_update` input contract MUST reject missing, empty, malformed, read-only, unsupported, conflicting, or insufficient writable update data with clear caller-facing validation feedback.
- **FR-014**: The `playlists_update` input contract MUST reject unsupported optional parameters, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-015**: The `playlists_update` tool MUST support valid OAuth-backed update requests when the caller is authorized to modify the target playlist.
- **FR-016**: The `playlists_update` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist update result.
- **FR-017**: The `playlists_update` result MUST preserve updated playlist resources, selected part context, target identity context, writable update context, quota context, authorization context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-018**: The `playlists_update` tool MUST distinguish successful playlist updates from local validation failures, authorization failures, quota failures, missing-resource failures, invalid writable-field failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-019**: The `playlists_update` tool MUST surface upstream quota, authorization, invalid request, unsupported or invalid writable-field, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-020**: The `playlists_update` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, required target identity, writable playlist details, unsupported modifier behavior, mutation semantics, repeat-request caveat, and availability state.
- **FR-021**: The `playlists_update` contract MUST warn callers that successful requests mutate user-visible playlist details for the authorized account or channel represented by the access context.
- **FR-022**: The `playlists_update` contract MUST remain close to the upstream `playlists.update` endpoint and MUST NOT add playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or heuristic classification.
- **FR-023**: The `playlists_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-024**: The `playlists_update` tool MUST rely on the existing Layer 1 `playlists.update` capability from YT-138 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-025**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist update request, one update request with supported optional details, one missing-part validation failure, one invalid-part validation failure, one missing-target-identity validation failure, one missing-writable-data validation failure, one invalid update-data validation failure, one unsupported-field validation failure, one authorization failure, one quota or upstream update failure, one repeat-request caveat, and one out-of-scope playlist-management request rejection.
- **FR-026**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, target identity, writable update data, update semantics, mutation warning, failure, and mutation-result requirements, interpret updated playlist results, and handle failures for `playlists_update` without consulting implementation-only artifacts.

### Key Entities

- **Playlists Update Tool**: The public Layer 2 MCP tool named `playlists_update`, representing one low-level endpoint-backed playlist update operation.
- **Playlists Update Request**: The request shape centered on required part selection, required target playlist identity, supported writable playlist details, and any explicitly supported update modifiers.
- **Part Selection**: The caller-selected playlist resource sections that determine which playlist properties are accepted and returned in the update result.
- **Target Playlist Identity**: The identifier and associated context needed to select the existing playlist being updated.
- **Writable Playlist Details**: The mutation payload that describes supported playlist fields the caller wants to update while excluding read-only or unsupported fields.
- **Authorization Context**: The caller access state required to update playlist resources without exposing credentials or sensitive authorization details.
- **Updated Playlist Resource**: The playlist record returned after a successful update for the selected parts.
- **Playlists Update Result**: The updated playlist resource, selected parts, target identity context, writable update context, quota context, authorization context, and returned upstream fields produced by a successful `playlists_update` call.
- **Quota Disclosure**: The caller-facing statement that each `playlists_update` invocation costs 50 official quota units.
- **Mutation Boundary Guidance**: The caller-facing explanation that successful calls mutate user-visible playlist details and that listing, creation, deletion, playlist item management, playlist image handling, video curation, transcripts, analytics, ranking, summarization, and recommendation are outside this low-level playlist update tool.

### Assumptions

- YT-138 provides the Layer 1 `playlists.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and validation standards this feature must follow.
- `playlists_update` is a low-level endpoint-backed tool for direct playlist updates, debugging, and power-user workflows; playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-138 contract treats `part` as required, OAuth-backed access as required, target playlist identity as required, writable playlist update data as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, playlist writability, invalid writable fields, quota, missing resources, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- Repeated update requests after timeout or unclear upstream outcome may reapply the same requested playlist state; this feature documents the caveat but does not add a higher-level conflict-detection, rollback, or playlist-versioning workflow.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlists.update` quota cost, auth behavior, part-selection rules, writable-field expectations, availability state, mutation behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-238 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist update, update with supported optional details, missing part selection, invalid part selection, missing target identity, missing writable update data, invalid update data, unsupported fields, access failure, quota or upstream update failure, repeat-request caveat, and returned updated playlist results is sufficient for this slice.

### Dependencies

- `YT-138` Layer 1 `playlists.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, mutation-result, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlists_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlists.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlists_update` requires OAuth-backed access and mutates user-visible playlist details by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required target playlist identity, writable update data, unsupported modifier boundaries, mutation semantics, repeat-request caveat, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlists_update`, choose valid inputs, understand the quota and access impact, and prepare a valid first update request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlists_update` requests return updated playlist results with selected part context, target identity context, writable update context, quota context, authorization context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid update requests that omit part selection, use invalid part selection, omit target identity, omit writable update data, use invalid update data, include unsupported fields or modifiers, lack OAuth-backed access, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, invalid writable-field, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful update results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlists_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlists_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
