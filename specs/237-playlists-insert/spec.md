# Feature Specification: Layer 2 Tool `playlists_insert`

**Feature Branch**: `237-playlists-insert`  
**Created**: 2026-07-10  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-237, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Playlists Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `playlists_insert` tool to create a playlist from supported writable playlist details while staying close to the upstream `playlists.insert` create behavior and returned playlist resource.

**Why this priority**: This is the core value of YT-237. Layer 2 must expose endpoint-backed playlist creation for direct owner workflows, debugging, and advanced automation without turning the tool into playlist update, deletion, playlist item insertion, playlist image handling, video curation, recommendation, ranking, summarization, analytics, or higher-level playlist-management behavior.

**Independent Test**: Can be tested by invoking `playlists_insert` with eligible user authorization, supported part selection, and required playlist creation details, then confirming the caller receives a near-raw created-playlist result with metadata identifying the mapped upstream operation, selected writable parts, creation context, access context, and quota cost.

**Acceptance Scenarios**:

1. **Given** a caller provides eligible user authorization, supported part selection, and required writable playlist details, **When** they call `playlists_insert`, **Then** the result identifies the created playlist and preserves the selected parts, creation inputs, access context, and quota cost.
2. **Given** a caller creates a playlist with supported optional writable playlist details, **When** the request succeeds, **Then** the result preserves returned playlist fields without fabricating playlist items, videos, images, transcripts, analytics, or derived recommendations.
3. **Given** a caller wants direct access to playlist creation behavior, **When** they use `playlists_insert`, **Then** the tool performs only the playlist insert operation and is not presented as playlist update, deletion, playlist item insertion, playlist image handling, video curation, ranking, summarization, analytics, or recommendation.

---

### User Story 2 - Understand Cost, OAuth, and Create Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `playlists_insert` before invoking it and immediately understand that it maps to `playlists.insert`, costs 50 official quota units per call, requires OAuth-backed user authorization, requires supported writable playlist details, and returns the created playlist resource.

**Why this priority**: Playlist creation is quota-bearing and mutates an authorized user's channel state. Callers need quota, authorization, writable-part, create-input, result-shape, example, and out-of-scope guidance before they spend quota or create user-visible playlists.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth requirement, supported writable part selection, required creation fields, mutation semantics, expected created-playlist result, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlists_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth requirement, required writable playlist details, supported writable part selection, create semantics, and availability state.
2. **Given** an example request is shown for `playlists_insert`, **When** a caller reads the example, **Then** the quota cost of `50`, selected writable parts, required authorization, creation details, expected created-playlist outcome, and mutation warning are visible alongside the request shape.
3. **Given** a caller needs playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, or recommendation, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist creation tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid or Unauthorized Playlist Creation Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlists_insert` request omits required writable playlist details, supplies unsupported part selection, lacks eligible user authorization, includes unsupported creation modifiers, or asks for behavior outside the playlist insert endpoint.

**Why this priority**: `playlists.insert` is a mutation with explicit authorization and writable-input requirements. Clear boundaries help callers distinguish malformed requests, unsupported create shapes, access failures, upstream create failures, and successful playlist creation without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, invalid part selection, missing title, malformed writable details, unsupported modifiers, missing authorization, insufficient authorization, upstream creation rejection, and out-of-scope playlist-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection or required writable playlist details, **When** they call `playlists_insert`, **Then** the request is rejected with guidance identifying the missing create requirement.
2. **Given** a caller provides unsupported part selection, malformed writable details, unsupported modifiers, or out-of-scope playlist-management inputs, **When** they call `playlists_insert`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller lacks eligible user authorization for playlist creation, **When** they call `playlists_insert`, **Then** the response distinguishes access failure from malformed input and from upstream creation failure.
4. **Given** a validly shaped authorized creation request is rejected by the upstream service, **When** the caller receives the response, **Then** the failure is categorized as an upstream create failure rather than a local validation failure or successful creation.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist creation request.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid writable part-selection input.
- The caller omits the minimum writable playlist details needed to create a playlist, including the playlist title; the response must identify missing creation data.
- The caller provides empty, malformed, excessively long, conflicting, or unsupported playlist metadata; the response must identify invalid writable playlist details.
- The caller provides unsupported optional parameters, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, or higher-level curation instructions; the response must identify the unsupported workflow boundary.
- The caller attempts playlist creation without eligible user authorization or with insufficient authorization for the target channel; the response must identify the access requirement rather than returning a misleading success or validation failure.
- A validly shaped authorized request is rejected upstream because the channel cannot create the playlist, the playlist details violate upstream rules, quota is exhausted, the service is unavailable, or the endpoint behavior changes; the caller-facing error must follow the shared Layer 2 error conventions.
- The upstream success response omits optional fields or returns partial playlist resources according to selected parts; the result must preserve returned fields without fabricating playlist item, video, channel, image, transcript, analytics, or recommendation data.
- The caller repeats a creation request after a timeout or unclear upstream outcome; the tool contract must avoid promising idempotent creation unless the shared contract explicitly supports it.
- The caller expects playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlists_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlists.insert` identity, official quota-unit cost of `50`, OAuth requirement, supported writable part selection, required creation details, create-result semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing required playlist details, malformed writable details, unsupported optional inputs, unsupported modifiers, missing or insufficient authorization, upstream creation rejection, unclear duplicate-create expectations, and out-of-scope playlist-management requests.
- **Red**: Add failing result-contract checks proving that created playlist fields, selected part context, creation context, quota context, access context, successful mutation outcomes, authorization failures, local validation failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlists_insert` tool contract and behavior needed for callers to make supported low-level `playlists.insert` requests and receive near-raw created playlist results.
- **Green**: Include representative examples for successful playlist creation, creation with supported optional details, missing part validation failure, invalid part validation failure, missing title validation failure, malformed writable-detail validation failure, unsupported modifier rejection, missing authorization failure, upstream create failure, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlists_insert` request, response, quota, OAuth, writable-part, create-result, mutation-warning, unsupported modifier, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, writable-detail, unsupported-option, mutation-boundary, and access-boundary validation, integration-style checks for representative successful and failed playlist creation paths, and documentation checks for quota/OAuth/create-semantics/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlists_insert` responsibility, inputs, outputs, quota cost, OAuth behavior, writable-part behavior, mutation warning, created-resource result shape, unsupported workflow boundary, and error behavior.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-237`, the dependency assumptions from YT-137/YT-201/YT-202, focused `playlists_insert` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlists_insert`.
- **FR-002**: The `playlists_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `playlists` and method `insert`.
- **FR-003**: The `playlists_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `playlists_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `playlists_insert` tool metadata MUST state that eligible OAuth-backed user authorization is required for playlist creation and MUST make that access expectation visible to callers before invocation.
- **FR-006**: The `playlists_insert` input contract MUST preserve the upstream concepts of supported writable part selection, writable playlist details, and created playlist resource output where those concepts are supported by the Layer 1 dependency.
- **FR-007**: The `playlists_insert` input contract MUST require supported part selection for each creation request and MUST document that part selection determines which playlist properties are accepted and returned.
- **FR-008**: The `playlists_insert` input contract MUST require the minimum writable playlist details needed to create a playlist, including a playlist title.
- **FR-009**: The `playlists_insert` input contract MUST document supported optional writable playlist details and MUST reject unsupported writable fields or modifiers with clear caller-facing validation feedback.
- **FR-010**: The `playlists_insert` input contract MUST reject missing, empty, malformed, duplicate, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-011**: The `playlists_insert` input contract MUST reject missing, empty, malformed, conflicting, excessively long, or unsupported writable playlist details with clear caller-facing validation feedback.
- **FR-012**: The `playlists_insert` input contract MUST reject unsupported optional parameters, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-013**: The `playlists_insert` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist creation result.
- **FR-014**: The `playlists_insert` result MUST preserve the created playlist resource, selected part context, creation context, quota context, access context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-015**: The `playlists_insert` result MUST distinguish successful playlist creation from local validation failures, access failures, quota failures, upstream create failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-016**: The `playlists_insert` tool MUST surface upstream quota, authorization, invalid request, forbidden create, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-017**: The `playlists_insert` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, required writable part selection, required playlist details, supported optional writable details, mutation semantics, duplicate-create caveat, unsupported modifier behavior, created-resource result shape, and availability state.
- **FR-018**: The `playlists_insert` contract MUST warn callers that successful requests create user-visible playlists for the authorized account or channel represented by the access context.
- **FR-019**: The `playlists_insert` contract MUST remain close to the upstream `playlists.insert` endpoint and MUST NOT add playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-020**: The `playlists_insert` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `playlists_insert` tool MUST rely on the existing Layer 1 `playlists.insert` capability from YT-137 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one successful playlist creation request, one creation request with supported optional details, one missing-part validation failure, one invalid-part validation failure, one missing-title validation failure, one malformed writable-detail validation failure, one unsupported modifier rejection, one missing authorization failure, one upstream create failure, and one out-of-scope playlist-management request rejection.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, writable-part, create-input, mutation, unsupported modifier, result, and failure requirements, interpret created playlist results, and handle failures for `playlists_insert` without consulting implementation-only artifacts.

### Key Entities

- **Playlists Insert Tool**: The public Layer 2 MCP tool named `playlists_insert`, representing one low-level endpoint-backed playlist creation operation.
- **Playlists Insert Request**: The request shape centered on required part selection, required writable playlist details, and any explicitly supported optional creation fields.
- **Part Selection**: The caller-selected writable playlist resource sections that determine which playlist properties are accepted and returned.
- **Writable Playlist Details**: The caller-provided playlist metadata used to create the playlist, including the required title and any supported optional details.
- **Access Context**: The eligible user authorization state required to create a playlist without exposing credentials or sensitive access details.
- **Created Playlist Resource**: The playlist resource returned after successful creation, limited to fields available for the selected parts.
- **Playlists Insert Result**: The successful mutation outcome containing the created playlist resource, selected parts, creation context, quota context, access context, and returned upstream fields.
- **Quota Disclosure**: The caller-facing statement that each `playlists_insert` invocation costs 50 official quota units.
- **Mutation Boundary Guidance**: The caller-facing explanation that successful calls create user-visible playlists and that update, delete, playlist item insertion, playlist image handling, video curation, transcripts, analytics, ranking, summarization, and recommendation are outside this low-level playlist creation tool.

### Assumptions

- YT-137 provides the Layer 1 `playlists.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, access, response-shaping, mutation result, validation, error, example, and validation standards this feature must follow.
- `playlists_insert` is a low-level endpoint-backed tool for direct playlist creation, debugging, and power-user workflows; playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-137 contract treats supported writable part selection, required playlist title, supported optional writable playlist details, and OAuth-backed access as the authoritative create boundary for this Layer 2 slice.
- A validly shaped authorized request may still receive an upstream rejection based on channel permissions, playlist policy, invalid supplied metadata, quota state, or service availability, and that outcome should remain distinct from local validation failures and successful playlist creation.
- Repeated creation requests may create multiple playlists unless the shared contract explicitly provides an idempotency guarantee; this feature documents the caveat but does not add a higher-level duplicate-prevention workflow.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlists.insert` quota cost, access behavior, part-selection rules, writable detail rules, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-237 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.
- Representative coverage of successful creation, supported optional details, missing part selection, invalid part selection, missing title, malformed writable details, unsupported modifiers, missing authorization, upstream create failure, out-of-scope workflow requests, and returned created playlist results is sufficient for this slice.

### Dependencies

- `YT-137` Layer 1 `playlists.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, mutation-result, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlists_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlists.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `playlists_insert` requires OAuth-backed user authorization and creates a user-visible playlist by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, required playlist title, supported optional writable details, duplicate-create caveat, unsupported modifier boundaries, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlists_insert`, choose valid inputs, understand the quota and access impact, and prepare a valid first creation request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlists_insert` requests return created playlist results with selected part context, creation context, quota context, access context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid insert requests that omit part selection, use invalid part selection, omit required playlist details, provide malformed writable details, use unsupported modifiers, lack eligible authorization, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful creation requests.
- **SC-007**: 100% of representative quota, authorization, forbidden-create, invalid-request, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful created playlist results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlists_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, access, availability, mutation-result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlists_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
