# Feature Specification: Layer 2 Tool `playlistItems_delete`

**Feature Branch**: `235-playlist-items-delete`  
**Created**: 2026-07-10  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-235, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Playlist Items Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistItems_delete` tool to remove an existing item from a playlist by its playlist item identifier while staying close to the upstream `playlistItems.delete` behavior.

**Why this priority**: This is the core value of YT-235. Layer 2 must expose endpoint-backed playlist-item deletion for direct playlist maintenance workflows, debugging, and later composition without turning the tool into playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, recommendation, ranking, summarization, or analytics behavior.

**Independent Test**: Can be tested by invoking `playlistItems_delete` with a valid playlist item identifier and OAuth-backed access, then confirming the caller receives a deletion acknowledgment with metadata identifying the mapped operation, supplied identifier, quota cost, authorization boundary, and successful mutation outcome.

**Acceptance Scenarios**:

1. **Given** a caller provides a valid playlist item identifier and OAuth-backed access, **When** they call `playlistItems_delete`, **Then** the result acknowledges deletion of the targeted playlist item and preserves operation context for the deletion request.
2. **Given** the deletion succeeds and the upstream operation returns no resource body, **When** the caller receives the result, **Then** the response still provides a clear deletion acknowledgment without fabricating deleted playlist-item data.
3. **Given** a caller wants direct access to playlist-item deletion behavior, **When** they use `playlistItems_delete`, **Then** the tool performs only the playlist-item delete operation and is not presented as playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, recommendation, ranking, summarization, or analytics.

---

### User Story 2 - Understand Cost, Authorization, and Delete Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `playlistItems_delete` before invoking it and immediately understand that it maps to `playlistItems.delete`, costs 50 official quota units per call, requires OAuth-backed access, requires a playlist item identifier, and performs a destructive removal from a playlist.

**Why this priority**: Playlist-item deletion is quota-bearing, destructive, and authorization-gated. Callers need quota, auth mode, required identifier, delete semantics, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that remove playlist items.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required playlist item identifier, destructive delete semantics, acknowledgment result, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistItems_delete`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required playlist item identifier, destructive delete semantics, and availability state.
2. **Given** an example request is shown for `playlistItems_delete`, **When** a caller reads the example, **Then** the quota cost of `50`, target playlist item identifier, OAuth-backed access expectation, destructive outcome, and expected deletion acknowledgment are visible alongside the request shape.
3. **Given** a caller needs playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, ranking, summarization, recommendation, or analytics, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-item deletion tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Item Delete Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistItems_delete` request omits the playlist item identifier, supplies an invalid identifier, lacks OAuth-backed access, targets a missing or unwritable playlist item, or asks for behavior outside the playlist-item delete endpoint.

**Why this priority**: `playlistItems.delete` removes playlist entries and consumes significant quota. Clear boundaries help callers distinguish malformed requests, access failures, missing resources, quota failures, upstream rejections, and successful deletion acknowledgments without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing identifier, malformed identifier, unsupported optional inputs, missing OAuth-backed access, insufficient access to the target playlist item, missing target item, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the playlist item identifier, **When** they call `playlistItems_delete`, **Then** the request is rejected with guidance identifying the missing required identifier.
2. **Given** a caller supplies a malformed identifier, unsupported optional inputs, or out-of-scope workflow request, **When** they call `playlistItems_delete`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistItems_delete`, **Then** the response distinguishes access failure from malformed input and from upstream deletion failure.
4. **Given** a valid OAuth-backed deletion request is rejected because the target playlist item is missing, unavailable, or not writable by the caller, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful deletion outcomes.

### Edge Cases

- The caller omits the required playlist item identifier; the request must be rejected before it is treated as a supported playlist-item deletion.
- The caller provides an empty, malformed, duplicate, or conflicting playlist item identifier; the response must identify invalid target input.
- The caller supplies part selection, playlist-item metadata payloads, playlist/video assignment data, placement controls, paging controls, listing selectors, or other optional inputs that do not belong to deletion; the response must identify unsupported input rather than silently ignoring destructive-request ambiguity.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target playlist item; the response must identify access failure rather than reporting a successful deletion.
- The target playlist item no longer exists, is not writable by the authorized caller, or belongs to a playlist outside the caller's access boundary; the response must distinguish missing-resource or authorization failure from malformed input.
- The deletion succeeds with no returned playlist item resource; the result must provide a clear deletion acknowledgment without fabricating deleted resource fields.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistItems_delete` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistItems.delete` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required playlist item identifier, destructive delete semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing identifier, invalid identifier, unsupported optional inputs, missing or insufficient OAuth-backed access, missing target playlist item, upstream deletion failure categorization, and out-of-scope playlist-item or playlist-management requests.
- **Red**: Add failing result-contract checks proving that deletion acknowledgment, target identifier context, quota context, access failures, validation failures, missing-resource failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistItems_delete` tool contract and behavior needed for callers to make supported low-level `playlistItems.delete` requests and receive deletion acknowledgments.
- **Green**: Include representative examples for OAuth-backed playlist-item deletion, successful no-body deletion acknowledgment, missing identifier validation failure, invalid identifier validation failure, unsupported input validation failure, authorization failure, missing-resource failure, quota or upstream deletion failure, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistItems_delete` request, response, quota, auth, destructive semantics, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for identifier, unsupported-option, destructive-boundary, and access-boundary validation, integration-style checks for representative successful and failed playlist-item deletion paths, and documentation checks for quota/auth/delete/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlistItems_delete` responsibility, inputs, outputs, quota cost, authorization behavior, target identifier behavior, destructive mutation result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-235`, the dependency assumptions from YT-135/YT-201/YT-202, focused `playlistItems_delete` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistItems_delete`.
- **FR-002**: The `playlistItems_delete` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistItems` and method `delete`.
- **FR-003**: The `playlistItems_delete` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlistItems_delete` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlistItems_delete` tool metadata MUST state the OAuth-backed authorization mode for playlist-item deletion and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistItems_delete` input contract MUST require a playlist item identifier for each deletion request.
- **FR-007**: The `playlistItems_delete` input contract MUST document that the identifier selects the playlist item to delete and that deletion is destructive.
- **FR-008**: The `playlistItems_delete` input contract MUST reject missing, empty, malformed, duplicate, unsupported, or conflicting playlist item identifiers with clear caller-facing validation feedback.
- **FR-009**: The `playlistItems_delete` input contract MUST reject part selection, playlist-item metadata payloads, playlist/video assignment data, placement controls, paging controls, listing selectors, unsupported optional parameters, and unsupported modifiers with clear caller-facing validation feedback.
- **FR-010**: The `playlistItems_delete` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-item deletion result.
- **FR-011**: The `playlistItems_delete` result MUST preserve target identifier context, quota context, authorization context, mapped operation identity, and deletion acknowledgment in a near-raw endpoint-backed shape.
- **FR-012**: The `playlistItems_delete` result MUST support successful deletion acknowledgment when no deleted playlist-item resource body is returned.
- **FR-013**: The `playlistItems_delete` tool MUST distinguish successful playlist-item deletions from validation failures, authorization failures, missing-resource failures, quota failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-014**: The `playlistItems_delete` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-015**: The `playlistItems_delete` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required identifier input, destructive mutation semantics, unsupported modifier behavior, no-body acknowledgment behavior, and availability state.
- **FR-016**: The `playlistItems_delete` contract MUST remain close to the upstream `playlistItems.delete` endpoint and MUST NOT add playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or heuristic classification.
- **FR-017**: The `playlistItems_delete` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation acknowledgment, validation, error, and example standards established by YT-201 and YT-202.
- **FR-018**: The `playlistItems_delete` tool MUST rely on the existing Layer 1 `playlistItems.delete` capability from YT-135 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-019**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-item deletion request, one successful no-body deletion acknowledgment, one missing-identifier validation failure, one invalid-identifier validation failure, one unsupported-input validation failure, one authorization failure, one missing-resource or quota upstream failure, and one out-of-scope playlist-management request rejection.
- **FR-020**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, required identifier, destructive delete semantics, failure, and acknowledgment-result requirements, interpret deletion acknowledgments, and handle failures for `playlistItems_delete` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Items Delete Tool**: The public Layer 2 MCP tool named `playlistItems_delete`, representing one low-level endpoint-backed playlist-item deletion operation.
- **Playlist Items Delete Request**: The request shape centered on the required playlist item identifier and any explicitly supported deletion context.
- **Playlist Item Identifier**: The caller-supplied target identifier that selects the playlist item to delete.
- **Authorization Context**: The caller access state required to delete playlist item resources without exposing credentials or sensitive authorization details.
- **Deleted Playlist Item Target**: The existing playlist item selected for deletion by the request identifier.
- **Playlist Items Delete Result**: The deletion acknowledgment, target identifier context, quota context, mapped operation identity, and any returned upstream context produced by a successful `playlistItems_delete` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistItems_delete` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, and enrichment are outside this low-level playlist-item deletion tool.

### Assumptions

- YT-135 provides the Layer 1 `playlistItems.delete` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation acknowledgment, validation, error, example, and validation standards this feature must follow.
- `playlistItems_delete` is a low-level endpoint-backed tool for direct playlist-item deletion, debugging, and power-user workflows; playlist item retrieval, insertion, update, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, automated curation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-135 contract treats a playlist item identifier as required, OAuth-backed access as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, playlist item writability, quota, missing resource, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistItems.delete` quota cost, auth behavior, identifier rules, destructive semantics, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-235 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist-item deletion, no-body deletion acknowledgment, missing identifier, invalid identifier, unsupported inputs, access failure, missing-resource or upstream deletion failure, and out-of-scope playlist-management requests is sufficient for this slice.

### Dependencies

- `YT-135` Layer 1 `playlistItems.delete` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems_delete` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistItems.delete` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistItems_delete` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify the required playlist item identifier, destructive delete semantics, unsupported modifier boundaries, no-body acknowledgment behavior, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistItems_delete`, choose valid inputs, understand the quota and access impact, and prepare a valid first deletion request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistItems_delete` requests return deletion acknowledgments with target identifier context, quota context, mapped operation identity, and mutation outcome preserved.
- **SC-006**: 100% of representative invalid deletion requests that omit the identifier, use an invalid identifier, include unsupported optional inputs, lack OAuth-backed access, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful deletion acknowledgments and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistItems_delete` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation acknowledgment, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistItems_delete` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
