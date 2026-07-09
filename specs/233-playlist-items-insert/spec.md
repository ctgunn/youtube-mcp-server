# Feature Specification: Layer 2 Tool `playlistItems_insert`

**Feature Branch**: `233-playlist-items-insert`  
**Created**: 2026-07-09  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-233, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Videos to Playlists Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistItems_insert` tool to add a video to a playlist using playlist-item creation data while staying close to the upstream `playlistItems.insert` behavior and returned playlist-item resource.

**Why this priority**: This is the core value of YT-233. Layer 2 must expose endpoint-backed playlist-item insertion for direct playlist mutation workflows, debugging, and later composition without turning the tool into playlist discovery, playlist traversal, video enrichment, recommendation, ranking, summarization, or curation automation.

**Independent Test**: Can be tested by invoking `playlistItems_insert` with supported part selection, required playlist/video assignment data, any supported placement details, and OAuth-backed access, then confirming the caller receives a near-raw created playlist-item result with metadata identifying the mapped operation, supplied parts, quota cost, mutation context, and authorization boundary.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, required playlist/video assignment data, and OAuth-backed access, **When** they call `playlistItems_insert`, **Then** the result identifies the created playlist item and preserves operation context for the insertion request.
2. **Given** a caller includes supported placement details for where the new item should appear in the playlist, **When** the insertion succeeds, **Then** the result preserves the returned playlist-item fields and insertion context without fabricating unrelated playlist, video, channel, transcript, or ranking data.
3. **Given** a successful insertion returns optional or partial playlist-item fields based on selected parts, **When** the caller receives the result, **Then** returned fields are preserved without fabricated data.
4. **Given** a caller wants direct access to playlist-item insertion behavior, **When** they use `playlistItems_insert`, **Then** the tool performs only the playlist-item insert operation and is not presented as playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, recommendation, ranking, summarization, or analytics.

---

### User Story 2 - Understand Cost, Authorization, and Insert Requirements Before Calling (Priority: P2)

As a client developer, I can inspect `playlistItems_insert` before invoking it and immediately understand that it maps to `playlistItems.insert`, costs 50 official quota units per call, requires OAuth-backed access, requires part selection, requires playlist/video assignment data, and supports only clearly documented insertion inputs.

**Why this priority**: Playlist-item insertion is quota-bearing, mutation-oriented, and authorization-gated. Callers need quota, auth mode, part selection, required creation data, placement semantics, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that mutate playlists.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required part selection, required playlist/video assignment data, supported placement behavior, mutation result shape, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistItems_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required part selection, required playlist/video assignment data, supported placement semantics, and availability state.
2. **Given** an example request is shown for `playlistItems_insert`, **When** a caller reads the example, **Then** the quota cost of `50`, selected parts, playlist/video assignment payload, OAuth-backed access expectation, supported placement context, and expected created playlist-item outcome are visible alongside the request shape.
3. **Given** a caller needs playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, ranking, summarization, recommendation, or analytics, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-item insertion tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Item Insert Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistItems_insert` request omits required inputs, supplies invalid part selection, lacks playlist/video assignment data, includes unsupported placement or resource fields, lacks OAuth-backed access, or asks for behavior outside the playlist-item insert endpoint.

**Why this priority**: `playlistItems.insert` mutates playlists and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported mutation shapes, access failures, quota failures, upstream rejections, and successful insertions without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing playlist identifier, missing video reference, malformed assignment data, conflicting placement details, unsupported resource fields, missing OAuth-backed access, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, target playlist identity, or referenced video identity, **When** they call `playlistItems_insert`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed part selection, invalid assignment data, conflicting placement details, unsupported resource fields, unsupported optional inputs, or out-of-scope workflow requests, **When** they call `playlistItems_insert`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistItems_insert`, **Then** the response distinguishes access failure from malformed input and from upstream insertion failure.
4. **Given** a valid OAuth-backed insertion request is rejected by the upstream service for playlist ownership, duplicate or ineligible video, missing resource, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful insertion outcomes.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-item insertion.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides the target playlist identifier without the referenced video identifier, the referenced video identifier without the target playlist identifier, or neither required assignment input; the response must identify the missing playlist/video assignment input.
- The caller supplies assignment data that lacks required creation fields, includes read-only or unsupported fields, conflicts with selected parts, or does not identify a playlist/video relationship; the response must identify invalid assignment input.
- The caller supplies placement details that are empty, malformed, duplicate, conflicting, unsupported, or outside the documented insert boundary; the response must identify invalid placement input.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist; the response must identify access failure rather than reporting a successful insertion.
- The target playlist is missing, private to another account, not writable by the authorized caller, or otherwise unavailable; the response must distinguish missing-resource or authorization failure from malformed input.
- The referenced video is missing, unavailable, already restricted from playlist addition, or otherwise rejected by the upstream service; the response must preserve the appropriate invalid request, eligibility, or upstream failure meaning.
- The upstream success response omits optional fields or returns partial playlist item data according to selected parts; the result must preserve returned fields without fabricating missing playlist-item, video, playlist, or channel data.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistItems_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistItems.insert` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required part selection, required playlist/video assignment data, supported placement semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing playlist identifier, missing video reference, invalid assignment data, unsupported or conflicting placement details, unsupported resource fields, unsupported optional inputs, missing or insufficient OAuth-backed access, upstream insertion failure categorization, and out-of-scope playlist-item or playlist-management requests.
- **Red**: Add failing result-contract checks proving that created playlist-item fields, selected part context, playlist/video assignment context, placement context when applicable, quota context, access failures, validation failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistItems_insert` tool contract and behavior needed for callers to make supported low-level `playlistItems.insert` requests and receive near-raw created playlist-item results.
- **Green**: Include representative examples for OAuth-backed playlist-item insertion, supported placement, missing part validation failure, invalid part validation failure, missing playlist identifier validation failure, missing video reference validation failure, invalid assignment validation failure, unsupported placement validation failure, authorization failure, quota or upstream insertion failure, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistItems_insert` request, response, quota, auth, part-selection, assignment data, placement semantics, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository test-suite run, and a passing repository code-quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, assignment data, placement, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist-item insertion paths, and documentation checks for quota/auth/assignment/placement/example visibility.
- **Docstring work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlistItems_insert` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, assignment data behavior, placement behavior, mutation result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-233`, the dependency assumptions from YT-133/YT-201/YT-202, focused `playlistItems_insert` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistItems_insert`.
- **FR-002**: The `playlistItems_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistItems` and method `insert`.
- **FR-003**: The `playlistItems_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlistItems_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlistItems_insert` tool metadata MUST state the OAuth-backed authorization mode for playlist-item insertion and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistItems_insert` input contract MUST preserve the upstream concept of required part selection and MUST document that part selection determines which playlist item properties are returned in the creation result.
- **FR-007**: The `playlistItems_insert` input contract MUST require supported part selection for each insertion request.
- **FR-008**: The `playlistItems_insert` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-009**: The `playlistItems_insert` input contract MUST require playlist-item creation data that identifies the target playlist and the referenced video for each supported insertion request.
- **FR-010**: The `playlistItems_insert` input contract MUST document the required playlist/video assignment data needed to add a video to a playlist and interpret the created playlist item.
- **FR-011**: The `playlistItems_insert` input contract MUST reject missing, empty, malformed, unsupported, read-only, or conflicting playlist-item creation data with clear caller-facing validation feedback.
- **FR-012**: The `playlistItems_insert` input contract MUST document any supported placement behavior for the created playlist item and MUST distinguish supported placement details from unsupported mutation modifiers.
- **FR-013**: The `playlistItems_insert` input contract MUST reject missing, malformed, duplicate, conflicting, unsupported, or out-of-bound placement details when placement inputs are supplied.
- **FR-014**: The `playlistItems_insert` tool MUST support valid OAuth-backed insertion requests when the caller is authorized to modify the target playlist.
- **FR-015**: The `playlistItems_insert` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-item insertion result.
- **FR-016**: The `playlistItems_insert` result MUST preserve created playlist item resources, selected part context, playlist/video assignment context, placement context when applicable, quota context, authorization context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-017**: The `playlistItems_insert` tool MUST distinguish successful playlist-item insertions from validation failures, authorization failures, quota failures, duplicate or ineligible video failures, missing-resource failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-018**: The `playlistItems_insert` tool MUST surface upstream quota, authorization, invalid request, duplicate or ineligible resource, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `playlistItems_insert` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, required playlist/video assignment data, supported placement behavior, unsupported modifier behavior, mutation semantics, and availability state.
- **FR-020**: The `playlistItems_insert` contract MUST remain close to the upstream `playlistItems.insert` endpoint and MUST NOT add playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or heuristic classification.
- **FR-021**: The `playlistItems_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-022**: The `playlistItems_insert` tool MUST rely on the existing Layer 1 `playlistItems.insert` capability from YT-133 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-item insertion request, one insertion request with supported placement context, one missing-part validation failure, one invalid-part validation failure, one missing-playlist validation failure, one missing-video-reference validation failure, one invalid-assignment validation failure, one unsupported-placement validation failure, one authorization failure, one quota or upstream insertion failure, and one out-of-scope playlist-management request rejection.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, playlist/video assignment, supported placement, failure, and mutation-result requirements, interpret created playlist-item results, and handle failures for `playlistItems_insert` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Items Insert Tool**: The public Layer 2 MCP tool named `playlistItems_insert`, representing one low-level endpoint-backed playlist-item insertion operation.
- **Playlist Items Insert Request**: The request shape centered on required part selection, required playlist/video assignment data, and any explicitly supported placement context.
- **Part Selection**: The caller-selected playlist item resource sections that determine which playlist item properties are returned in the creation result.
- **Playlist/Video Assignment Data**: The creation payload that identifies the target playlist, the video to add, and other supported playlist-item creation fields.
- **Placement Context**: Optional caller-provided information, when supported, describing where the new playlist item should appear relative to the target playlist.
- **Authorization Context**: The caller access state required to insert playlist item resources without exposing credentials or sensitive authorization details.
- **Created Playlist Item Resource**: The playlist item record returned after a successful insertion for the selected parts.
- **Playlist Items Insert Result**: The created playlist item resource, selected parts, playlist/video assignment context, placement context when applicable, quota context, authorization context, and returned upstream fields produced by a successful `playlistItems_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistItems_insert` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, and automated curation are outside this low-level playlist-item insertion tool.

### Assumptions

- YT-133 provides the Layer 1 `playlistItems.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and validation standards this feature must follow.
- `playlistItems_insert` is a low-level endpoint-backed tool for direct playlist-item insertion, debugging, and power-user workflows; playlist item retrieval, update, deletion, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, automated curation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-133 contract treats `part` as required, OAuth-backed access as required, playlist/video assignment data as required, placement inputs as supported only when explicitly documented, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, duplicate insertion policy, video eligibility, quota, missing resources, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistItems.insert` quota cost, auth behavior, part-selection rules, playlist/video assignment rules, placement behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-233 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist-item insertion, supported placement, missing part selection, invalid part selection, missing playlist identifier, missing video reference, invalid assignment data, unsupported placement, access failure, quota or upstream insertion failure, and returned created playlist-item results is sufficient for this slice.

### Dependencies

- `YT-133` Layer 1 `playlistItems.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistItems.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistItems_insert` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required playlist/video assignment data, supported placement behavior, unsupported modifier boundaries, mutation semantics, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistItems_insert`, choose valid inputs, understand the quota and access impact, and prepare a valid first insertion request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistItems_insert` requests return created playlist-item results with selected part context, playlist/video assignment context, placement context when applicable, quota context, authorization context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid insertion requests that omit part selection, use invalid part selection, omit playlist identity, omit video reference, use invalid assignment data, include unsupported placement or modifiers, lack OAuth-backed access, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, duplicate or ineligible video, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful insertion results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistItems_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistItems_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
