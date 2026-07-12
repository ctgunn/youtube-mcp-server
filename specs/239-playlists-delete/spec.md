# Feature Specification: Layer 2 Tool `playlists_delete`

**Feature Branch**: `239-playlists-delete`  
**Created**: 2026-07-12  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-239, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Playlists Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlists_delete` tool to delete an existing playlist I am authorized to manage while staying close to the upstream `playlists.delete` behavior and deletion acknowledgment.

**Why this priority**: This is the core value of YT-239. Layer 2 must expose endpoint-backed playlist deletion for direct owner workflows, debugging, and advanced automation without turning the tool into playlist listing, creation, update, playlist item management, playlist image handling, video curation, recommendation, ranking, summarization, analytics, or higher-level playlist-management behavior.

**Independent Test**: Can be tested by invoking `playlists_delete` with required target playlist identity and OAuth-backed access, then confirming the caller receives a deletion acknowledgment with metadata identifying the mapped upstream operation, target identity context, quota cost, authorization boundary, and destructive mutation semantics.

**Acceptance Scenarios**:

1. **Given** a caller provides required target playlist identity and OAuth-backed access for a playlist they can manage, **When** they call `playlists_delete`, **Then** the result acknowledges deletion and preserves operation context for the delete request.
2. **Given** a deletion succeeds, **When** the caller receives the result, **Then** the result does not fabricate a playlist resource, playlist items, videos, images, transcripts, analytics, recommendations, or any higher-level curation output.
3. **Given** a caller wants direct access to playlist deletion behavior, **When** they use `playlists_delete`, **Then** the tool performs only the playlist delete operation and is not presented as playlist listing, creation, update, playlist item management, playlist image handling, video curation, ranking, summarization, analytics, or recommendation.

---

### User Story 2 - Understand Cost, OAuth, and Deletion Impact Before Calling (Priority: P2)

As a client developer, I can inspect `playlists_delete` before invoking it and immediately understand that it maps to `playlists.delete`, costs 50 official quota units per call, requires OAuth-backed user authorization, requires target playlist identity, and permanently removes a user-visible playlist within the authorized account or channel context.

**Why this priority**: Playlist deletion is quota-bearing, destructive, and authorization-gated. Callers need quota, OAuth, target identity, deletion impact, examples, and out-of-scope guidance in discovery and descriptions before they spend quota or remove user-visible playlists.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required target playlist identity, destructive deletion warning, expected deletion acknowledgment, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlists_delete`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed access requirement, required target playlist identity, deletion semantics, and availability state.
2. **Given** an example request is shown for `playlists_delete`, **When** a caller reads the example, **Then** the quota cost of `50`, target playlist identity, OAuth-backed access expectation, destructive deletion warning, and expected acknowledgment are visible alongside the request shape.
3. **Given** a caller needs playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, ranking, summarization, recommendation, or analytics, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist deletion tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid or Unauthorized Deletion Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlists_delete` request omits target playlist identity, supplies malformed or unsupported inputs, lacks OAuth-backed access, targets a playlist I cannot delete, or asks for behavior outside the playlist deletion endpoint.

**Why this priority**: `playlists.delete` removes user-visible resources and consumes significant quota. Clear boundaries help callers distinguish malformed requests, unsupported deletion shapes, access failures, quota failures, missing or unwritable playlists, upstream rejections, and successful deletion without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing target playlist identity, malformed identity, unsupported optional inputs, missing OAuth-backed access, insufficient authorization, upstream deletion rejection, repeat-delete scenarios, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits target playlist identity, **When** they call `playlists_delete`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed target identity, unsupported optional inputs, unsupported modifiers, or out-of-scope workflow requests, **When** they call `playlists_delete`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlists_delete`, **Then** the response distinguishes access failure from malformed input and from upstream deletion failure.
4. **Given** a valid OAuth-backed deletion request is rejected by the upstream service for playlist ownership, missing resource, quota, or service availability reasons, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful deletion acknowledgments.

### Edge Cases

- The caller omits required target playlist identity; the request must be rejected before it is treated as a supported playlist deletion.
- The caller provides empty, malformed, duplicated, conflicting, or unsupported target playlist identity input; the response must identify invalid target identity.
- The caller provides unsupported optional parameters, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, or higher-level curation instructions; the response must identify the unsupported workflow boundary.
- The caller attempts deletion without OAuth-backed access or with insufficient authorization for the target playlist; the response must identify access failure rather than returning a misleading success or local validation failure.
- The target playlist no longer exists, was already deleted, is not manageable by the authorized caller, or belongs to a channel outside the caller's access boundary; the response must distinguish missing-resource or authorization failure from malformed input.
- The upstream success response has no playlist resource body; the result must provide a deletion acknowledgment and operation context without fabricating deleted playlist details.
- A caller repeats a deletion request after a timeout or unclear upstream outcome; the tool contract must avoid promising rollback, restore, or idempotent success unless the shared contract explicitly supports it.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist listing, creation, update, playlist item insertion, playlist item update, playlist item deletion, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlists_delete` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlists.delete` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required target playlist identity, destructive deletion semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing target playlist identity, malformed target playlist identity, unsupported optional inputs, unsupported modifiers, missing or insufficient OAuth-backed access, upstream deletion failure categorization, repeat-delete caveat visibility, and out-of-scope playlist-management requests.
- **Red**: Add failing result-contract checks proving that deletion acknowledgments, target identity context, quota context, authorization context, successful deletion outcomes, access failures, validation failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlists_delete` tool contract and behavior needed for callers to make supported low-level `playlists.delete` requests and receive clear deletion acknowledgments.
- **Green**: Include representative examples for OAuth-backed playlist deletion, missing target identity validation failure, malformed target identity validation failure, unsupported modifier rejection, missing authorization failure, insufficient authorization failure, missing-resource or already-deleted upstream failure, quota or upstream service failure, repeat-delete caveat, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlists_delete` request, response, quota, OAuth, target identity, destructive deletion, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for target identity, unsupported-option, destructive-boundary, and access-boundary validation, integration-style checks for representative successful and failed playlist deletion paths, and documentation checks for quota/OAuth/deletion/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlists_delete` responsibility, inputs, outputs, quota cost, OAuth behavior, target identity behavior, destructive deletion warning, acknowledgment result shape, unsupported workflow boundary, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-239`, the dependency assumptions from YT-139/YT-201/YT-202, focused `playlists_delete` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlists_delete`.
- **FR-002**: The `playlists_delete` tool definition MUST identify its mapped upstream operation as YouTube resource `playlists` and method `delete`.
- **FR-003**: The `playlists_delete` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlists_delete` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlists_delete` tool metadata MUST state the OAuth-backed authorization mode for playlist deletion and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlists_delete` input contract MUST preserve the upstream concepts of required target playlist identity and deletion acknowledgment where those concepts are supported by the Layer 1 dependency.
- **FR-007**: The `playlists_delete` input contract MUST require target playlist identity for each supported deletion request.
- **FR-008**: The `playlists_delete` input contract MUST document the target identity needed to identify the playlist being deleted.
- **FR-009**: The `playlists_delete` input contract MUST reject missing, empty, malformed, duplicated, conflicting, or unsupported target playlist identity with clear caller-facing validation feedback.
- **FR-010**: The `playlists_delete` input contract MUST reject unsupported optional parameters, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-011**: The `playlists_delete` tool MUST support valid OAuth-backed deletion requests when the caller is authorized to delete the target playlist.
- **FR-012**: The `playlists_delete` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist deletion result.
- **FR-013**: The `playlists_delete` result MUST preserve deletion acknowledgment, target identity context, quota context, authorization context, and returned upstream context in a near-raw endpoint-backed shape.
- **FR-014**: The `playlists_delete` result MUST NOT fabricate a deleted playlist resource or imply retrieval of playlist items, videos, playlist images, transcripts, analytics, or recommendations.
- **FR-015**: The `playlists_delete` tool MUST distinguish successful playlist deletions from local validation failures, authorization failures, quota failures, missing-resource failures, invalid request failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-016**: The `playlists_delete` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-017**: The `playlists_delete` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required target identity, destructive mutation semantics, repeat-delete caveat, unsupported modifier behavior, acknowledgment result shape, and availability state.
- **FR-018**: The `playlists_delete` contract MUST warn callers that successful requests delete user-visible playlists for the authorized account or channel represented by the access context.
- **FR-019**: The `playlists_delete` contract MUST remain close to the upstream `playlists.delete` endpoint and MUST NOT add playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, restore, rollback, or heuristic classification.
- **FR-020**: The `playlists_delete` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `playlists_delete` tool MUST rely on the existing Layer 1 `playlists.delete` capability from YT-139 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist deletion request, one missing-target-identity validation failure, one malformed-target-identity validation failure, one unsupported modifier rejection, one missing authorization failure, one insufficient authorization failure, one missing-resource or already-deleted failure, one quota or upstream service failure, one repeat-delete caveat, and one out-of-scope playlist-management request rejection.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, target identity, destructive deletion semantics, failure, and acknowledgment requirements, interpret deletion results, and handle failures for `playlists_delete` without consulting implementation-only artifacts.

### Key Entities

- **Playlists Delete Tool**: The public Layer 2 MCP tool named `playlists_delete`, representing one low-level endpoint-backed playlist deletion operation.
- **Playlists Delete Request**: The request shape centered on required target playlist identity and any explicitly supported deletion context.
- **Target Playlist Identity**: The identifier and associated context needed to select the existing playlist being deleted.
- **Authorization Context**: The caller access state required to delete playlist resources without exposing credentials or sensitive authorization details.
- **Deletion Acknowledgment**: The successful result that confirms the delete operation was accepted without inventing a deleted playlist resource body.
- **Playlists Delete Result**: The deletion acknowledgment, target identity context, quota context, authorization context, and returned upstream context produced by a successful `playlists_delete` call.
- **Quota Disclosure**: The caller-facing statement that each `playlists_delete` invocation costs 50 official quota units.
- **Destructive Mutation Boundary Guidance**: The caller-facing explanation that successful calls delete user-visible playlists and that listing, creation, update, playlist item management, playlist image handling, video curation, transcripts, analytics, ranking, summarization, recommendation, restore, and rollback are outside this low-level playlist deletion tool.

### Assumptions

- YT-139 provides the Layer 1 `playlists.delete` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and validation standards this feature must follow.
- `playlists_delete` is a low-level endpoint-backed tool for direct playlist deletion, debugging, and power-user workflows; playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore, rollback, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-139 contract treats target playlist identity as required, OAuth-backed access as required, and unsupported modifiers as outside the supported contract for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, playlist existence, playlist writability, quota, missing resources, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- Repeated deletion requests after timeout or unclear upstream outcome may encounter a missing-resource response if the first request succeeded; this feature documents the caveat but does not add restore, rollback, idempotency, or playlist-versioning behavior.
- The official YouTube endpoint documentation and existing project inventory are the default sources for `playlists.delete` quota cost, auth behavior, target identity rules, availability state, destructive deletion behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-239 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful playlist deletion, missing target identity, malformed target identity, unsupported modifiers, missing authorization, insufficient authorization, missing-resource or already-deleted failures, quota or upstream service failures, repeat-delete caveat, out-of-scope workflow requests, and deletion acknowledgments is sufficient for this slice.

### Dependencies

- `YT-139` Layer 1 `playlists.delete` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, mutation-result, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlists_delete` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlists.delete` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlists_delete` requires OAuth-backed access and deletes a user-visible playlist by reading the tool contract alone.
- **SC-003**: A client developer can identify required target playlist identity, destructive deletion semantics, repeat-delete caveat, unsupported modifier boundaries, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlists_delete`, choose valid inputs, understand the quota and deletion impact, and prepare a valid first deletion request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlists_delete` requests return deletion acknowledgments with target identity context, quota context, authorization context, and returned upstream context preserved.
- **SC-006**: 100% of representative invalid deletion requests that omit target identity, use malformed target identity, include unsupported fields or modifiers, lack OAuth-backed access, lack sufficient authorization, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, invalid request, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful deletion acknowledgments and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlists_delete` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlists_delete` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
