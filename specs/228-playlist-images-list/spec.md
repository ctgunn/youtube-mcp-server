# Feature Specification: Layer 2 Tool `playlistImages_list`

**Feature Branch**: `228-playlist-images-list`  
**Created**: 2026-07-07  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-228, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlist Images Through a Public Tool (Priority: P1)

As a power user with OAuth-backed access, I can call the low-level `playlistImages_list` tool to retrieve playlist image resources while staying close to the upstream `playlistImages.list` behavior, selector rules, and returned image collection.

**Why this priority**: This is the core value of YT-228. Layer 2 must expose endpoint-backed playlist-image retrieval for direct inspection, debugging, and later composition without turning the tool into playlist management, thumbnail upload, media transformation, ranking, summarization, or enrichment behavior.

**Independent Test**: Can be tested by invoking `playlistImages_list` with supported part selection and one supported playlist-image lookup selector, then confirming the caller receives a near-raw playlist-image collection result with metadata identifying the mapped upstream operation, selected parts, selector context, and quota cost.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, OAuth-backed access, and one supported playlist-image selector, **When** they call `playlistImages_list`, **Then** the result includes matching playlist image records and preserves operation context for the selected lookup.
2. **Given** a valid request returns playlist image resources with optional or partial fields based on selected parts, **When** the caller receives the result, **Then** returned playlist image fields are preserved without fabricated data.
3. **Given** a caller wants direct access to playlist image listing behavior, **When** they use `playlistImages_list`, **Then** the tool performs only the playlist-image list operation and is not presented as playlist modification, image upload, thumbnail replacement, analytics, recommendation, ranking, summarization, or enrichment.

---

### User Story 2 - Understand Cost, Authorization, Selectors, and Parts Before Calling (Priority: P2)

As a client developer, I can inspect `playlistImages_list` before invoking it and immediately understand that it maps to `playlistImages.list`, costs 1 official quota unit per call, requires OAuth-backed access, requires part selection, supports playlist-scoped lookup by `playlistId` and direct image lookup by `id`, and has selector-specific paging and modifier boundaries.

**Why this priority**: Playlist image retrieval is quota-bearing and authorization-gated. Callers need quota, auth-mode, part-selection, selector, paging, example, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that depend on playlist image data.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, OAuth-backed access requirement, required part selection, `playlistId` and `id` selector behavior, selector-specific paging guidance, unsupported modifier boundary, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistImages_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, OAuth-backed access requirement, required part selection, `playlistId` and `id` lookup selectors, selector-specific paging guidance, and unsupported modifier boundary.
2. **Given** an example request is shown for `playlistImages_list`, **When** a caller reads the example, **Then** the quota cost of `1`, selected parts, selected lookup mode, OAuth-backed access expectation, and expected playlist-image list outcome are visible alongside the request shape.
3. **Given** a caller needs playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, ranking, summarization, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-image listing tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Image List Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistImages_list` request omits required inputs, supplies invalid part selection, combines conflicting selectors, uses unsupported modifiers, lacks OAuth-backed access, or asks for behavior outside the playlist-image list endpoint.

**Why this priority**: `playlistImages.list` depends on clear part and selector choices, and invalid lookup shapes can otherwise look like empty image collections. Clear boundaries help callers distinguish malformed requests, unsupported retrieval shapes, access failures, valid empty results, and upstream failures without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, malformed part selection, missing selectors, conflicting selectors, unsupported paging for a selector mode, unsupported modifiers, missing OAuth-backed access, and out-of-scope image-management requests, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, **When** they call `playlistImages_list`, **Then** the request is rejected with guidance that part selection is required.
2. **Given** a caller omits a supported lookup selector, combines conflicting selectors, or supplies unsupported selector-specific paging or modifiers, **When** they call `playlistImages_list`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without OAuth-backed access, **When** they call `playlistImages_list`, **Then** the response distinguishes access failure from malformed input and from successful empty playlist-image lists.
4. **Given** a valid OAuth-backed request returns no playlist image records, **When** the caller receives the result, **Then** the response identifies a successful empty collection rather than a validation, access, or upstream failure.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-image lookup.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller omits all supported playlist-image lookup selectors or provides only `part`; the request must identify the missing lookup selector.
- The caller combines direct image lookup and playlist-scoped lookup selectors in a way the contract does not support; the response must identify conflicting selector input.
- The caller provides paging controls with a selector mode where paging is unsupported, empty page tokens, out-of-range page sizes, or modifiers outside the Layer 1 contract; the response must identify unsupported or invalid modifier input.
- The request is validly shaped and has OAuth-backed access but returns an empty playlist-image collection; the result must distinguish an empty successful collection from invalid input, insufficient access, and upstream failure.
- The upstream success response omits optional fields or returns partial playlist image resources according to the selected parts; the result must preserve returned fields without fabricating missing playlist image data.
- The upstream service returns quota, authorization, invalid request, unavailable service, missing resource, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistImages_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistImages.list` identity, official quota-unit cost of `1`, OAuth-backed access disclosure, required part selection, supported playlist-image selector guidance, selector-specific paging guidance, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing lookup selectors, conflicting selectors, selector-incompatible paging, unsupported modifiers, missing or insufficient OAuth-backed access, empty result handling, and out-of-scope image-management or playlist-management requests.
- **Red**: Add failing result-contract checks proving that returned playlist image collection fields, selected part context, selected lookup context, successful empty outcomes, access failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistImages_list` tool contract and behavior needed for callers to make supported low-level `playlistImages.list` requests and receive near-raw playlist-image collection results.
- **Green**: Include representative examples for OAuth-backed playlist-scoped retrieval, OAuth-backed direct image lookup, empty successful results, missing part validation failure, invalid part validation failure, missing selector validation failure, conflicting selector validation failure, unsupported modifier validation failure, authorization failure, and out-of-scope image-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistImages_list` request, response, quota, auth, part-selection, selector, paging, unsupported modifier, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, selector, paging, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist-image retrieval paths, and documentation checks for quota/auth/selector/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `playlistImages_list` responsibility, inputs, outputs, quota cost, authorization behavior, part-selection behavior, selector behavior, paging boundary, empty-result behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-228`, the dependency assumptions from YT-128/YT-201/YT-202, focused `playlistImages_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistImages_list`.
- **FR-002**: The `playlistImages_list` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistImages` and method `list`.
- **FR-003**: The `playlistImages_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `playlistImages_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `playlistImages_list` tool metadata MUST state the OAuth-backed authorization mode for playlist-image retrieval and MUST make OAuth-backed access expectations visible to callers before invocation.
- **FR-006**: The `playlistImages_list` input contract MUST preserve the upstream concept of required part selection and MUST document that part selection determines which playlist image properties are returned.
- **FR-007**: The `playlistImages_list` input contract MUST require supported part selection for each retrieval request.
- **FR-008**: The `playlistImages_list` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-009**: The `playlistImages_list` input contract MUST document both supported playlist-image lookup selectors: playlist-scoped lookup by `playlistId` and direct image lookup by `id`.
- **FR-010**: The `playlistImages_list` input contract MUST require exactly one supported lookup selector per request.
- **FR-011**: The `playlistImages_list` input contract MUST reject requests that omit required lookup selector input, combine conflicting selectors, or provide unsupported selector combinations with clear caller-facing validation feedback.
- **FR-012**: The `playlistImages_list` input contract MUST document which paging inputs are supported for each lookup mode and MUST reject unsupported paging controls, empty page tokens, out-of-range page sizes, unsupported optional parameters, and unsupported modifiers with clear caller-facing validation feedback.
- **FR-013**: The `playlistImages_list` tool MUST reject or clearly categorize missing, invalid, or insufficient authorization as an access failure rather than a successful playlist-image list result.
- **FR-014**: The `playlistImages_list` result MUST preserve playlist image resources, selected part context, selected lookup context, paging context when applicable, quota context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-015**: The `playlistImages_list` result MUST distinguish successful populated collections from successful empty collections.
- **FR-016**: The `playlistImages_list` tool MUST distinguish successful empty playlist-image collections from validation failures, authorization failures, missing-resource failures, quota failures, unavailable service responses, and unexpected upstream failures.
- **FR-017**: The `playlistImages_list` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `playlistImages_list` contract MUST document applicable official limits and caveats, including quota cost, OAuth-backed access expectations, required part selection, `playlistId` and `id` selectors, selector-specific paging behavior, unsupported modifier behavior, empty-result behavior, and availability state.
- **FR-019**: The `playlistImages_list` contract MUST remain close to the upstream `playlistImages.list` endpoint and MUST NOT add playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-020**: The `playlistImages_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, selector-boundary, validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `playlistImages_list` tool MUST rely on the existing Layer 1 `playlistImages.list` capability from YT-128 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one OAuth-backed playlist-scoped retrieval request, one OAuth-backed direct image lookup request, one empty successful result, one missing-part validation failure, one invalid-part validation failure, one missing-selector validation failure, one conflicting-selector validation failure, one unsupported modifier validation failure, one authorization failure, and one out-of-scope image-management request rejection.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth-backed access, part-selection, selector, paging, unsupported modifier, failure, and empty-result requirements, interpret list results, and handle failures for `playlistImages_list` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Images List Tool**: The public Layer 2 MCP tool named `playlistImages_list`, representing one low-level endpoint-backed playlist-image retrieval operation.
- **Playlist Images List Request**: The request shape centered on required part selection, exactly one supported lookup selector, and any selector-compatible paging inputs.
- **Part Selection**: The caller-selected playlist image resource sections that determine which playlist image properties are returned.
- **Playlist Image Lookup Selector**: The supported retrieval mode, either playlist-scoped lookup by playlist identifier or direct lookup by playlist image identifier, including its validation and paging boundaries.
- **Authorization Context**: The caller access state required to retrieve playlist image resources without exposing credentials or sensitive authorization details.
- **Playlist Image Resource**: A returned playlist image record visible for the selected lookup and selected parts.
- **Playlist Images List Result**: The returned playlist image collection, selected parts, lookup selector, paging context when applicable, quota context, and upstream fields produced by a successful `playlistImages_list` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistImages_list` invocation costs 1 official quota unit.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, ranking, summarization, and enrichment are outside this low-level playlist-image listing tool.

### Assumptions

- YT-128 provides the Layer 1 `playlistImages.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, validation, error, example, and validation standards this feature must follow.
- `playlistImages_list` is a low-level endpoint-backed tool for direct playlist-image retrieval, debugging, and power-user workflows; playlist image mutation, media upload, playlist management, analytics, ranking, summarization, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-128 contract treats `part` as required, OAuth-backed access as required, supported lookup selectors as explicit contract detail, and unsupported modifiers as outside the supported contract for this slice.
- A valid OAuth-backed request may return an empty playlist-image list, and that outcome should remain distinguishable from invalid input, insufficient access, missing resources, and upstream failure.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistImages.list` quota cost, auth behavior, part-selection rules, selector behavior, paging behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-228 seed identifies the official quota-unit cost as `1` for this public Layer 2 contract.
- Representative coverage of playlist-scoped retrieval, direct image lookup, missing part selection, invalid part selection, missing selectors, conflicting selectors, unsupported modifiers, access failure, empty successful results, and returned playlist-image collection results is sufficient for this slice.

### Dependencies

- `YT-128` Layer 1 `playlistImages.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistImages_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistImages.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute that `playlistImages_list` requires OAuth-backed access by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, `playlistId` and `id` lookup selectors, selector-specific paging behavior, unsupported modifier boundaries, and out-of-scope image-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistImages_list`, choose valid inputs, understand the quota and access impact, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistImages_list` requests return playlist-image collection results with selected part context, lookup selector context, quota context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, use invalid part selection, omit lookup selectors, combine conflicting selectors, use unsupported paging, include unsupported modifiers, lack OAuth-backed access, or request out-of-scope image-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative empty-result, quota, authorization, missing-resource, unavailable-service, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistImages_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, list result, selector-boundary, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistImages_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
