# Feature Specification: Layer 2 Tool `playlistItems_list`

**Feature Branch**: `232-playlist-items-list`  
**Created**: 2026-07-09  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-232, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlist Items Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `playlistItems_list` tool to retrieve playlist entries by playlist identifier or playlist-item identifier while staying close to the upstream `playlistItems.list` behavior, pagination model, and returned playlist-item collection.

**Why this priority**: This is the core value of YT-232. Layer 2 must expose endpoint-backed playlist-item retrieval for direct inspection, debugging, playlist traversal, and later composition without turning the tool into playlist mutation, playlist search, ranking, transcript lookup, video enrichment, summarization, or recommendation behavior.

**Independent Test**: Can be tested by invoking `playlistItems_list` with supported part selection and one supported lookup selector, then confirming the caller receives a near-raw playlist-item collection result with metadata identifying the mapped upstream operation, selected parts, lookup mode, pagination context when applicable, and quota cost.

**Acceptance Scenarios**:

1. **Given** a caller provides a playlist identifier, supported part selection, and any supported pagination inputs, **When** they call `playlistItems_list`, **Then** the result includes matching playlist item records and preserves operation context for playlist-scoped retrieval.
2. **Given** a caller provides one or more playlist-item identifiers and supported part selection, **When** they call `playlistItems_list`, **Then** the result includes matching playlist item records and preserves operation context for identifier-based retrieval.
3. **Given** a valid request returns playlist item resources with optional or partial fields based on selected parts, **When** the caller receives the result, **Then** returned playlist item fields are preserved without fabricated video, playlist, or channel data.
4. **Given** a caller wants direct access to playlist-item listing behavior, **When** they use `playlistItems_list`, **Then** the tool performs only the playlist-item list operation and is not presented as playlist insertion, playlist-item mutation, playlist search, ranking, transcript retrieval, video enrichment, summarization, or recommendation.

---

### User Story 2 - Understand Cost, Selectors, Access, and Pagination Before Calling (Priority: P2)

As a client developer, I can inspect `playlistItems_list` before invoking it and immediately understand that it maps to `playlistItems.list`, costs 1 official quota unit per call, supports playlist-scoped and identifier-based lookup modes, uses the documented API-key access path for the supported selector set, requires part selection, and preserves endpoint pagination behavior where supported.

**Why this priority**: Playlist-item retrieval is quota-bearing and selector-sensitive. Callers need quota, access-mode, part-selection, lookup-mode, pagination, example, and out-of-scope guidance in discovery and descriptions before they spend quota or build workflows that depend on playlist entries.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, API-key access expectation, required part selection, supported `playlistId` and `id` lookup selectors, selector-specific pagination guidance, and out-of-scope behaviors are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `playlistItems_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, API-key access expectation, required part selection, supported lookup selectors, pagination behavior, and availability state.
2. **Given** an example request is shown for `playlistItems_list`, **When** a caller reads the example, **Then** the quota cost of `1`, selected parts, selected lookup mode, access expectation, paging context when applicable, and expected playlist-item list outcome are visible alongside the request shape.
3. **Given** a caller needs to traverse a playlist across pages, **When** they inspect the tool contract, **Then** the supported page-size and page-token behavior for playlist-scoped retrieval is clear before invocation.
4. **Given** a caller needs playlist search, playlist-item insertion, update, deletion, video enrichment, transcript retrieval, ranking, summarization, or recommendation, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level playlist-item listing tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid Playlist Item List Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `playlistItems_list` request omits required inputs, supplies invalid part selection, combines conflicting selectors, uses paging where the selected lookup mode does not support it, lacks eligible access, or asks for behavior outside the playlist-item list endpoint.

**Why this priority**: `playlistItems.list` depends on clear part, selector, and paging choices, and invalid lookup shapes can otherwise look like empty playlist results. Clear boundaries help callers distinguish malformed requests, unsupported retrieval shapes, access failures, valid empty results, and upstream failures without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, invalid part selection, missing selectors, conflicting selectors, malformed identifiers, selector-incompatible paging, unsupported modifiers, ineligible access context, and out-of-scope playlist-management requests, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection, **When** they call `playlistItems_list`, **Then** the request is rejected with guidance that part selection is required.
2. **Given** a caller omits a supported lookup selector or combines playlist-scoped and identifier-based selectors, **When** they call `playlistItems_list`, **Then** the request is rejected with guidance identifying the missing or conflicting selector input.
3. **Given** a caller supplies unsupported paging controls, unsupported modifiers, or malformed selector values, **When** they call `playlistItems_list`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
4. **Given** a valid request returns no playlist item records, **When** the caller receives the result, **Then** the response identifies a successful empty collection rather than a validation, access, or upstream failure.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported playlist-item lookup.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller omits all supported playlist-item lookup selectors or provides only `part`; the request must identify the missing lookup selector.
- The caller combines playlist-scoped lookup by `playlistId` with identifier-based lookup by `id`; the response must identify conflicting selector input.
- The caller provides empty, malformed, duplicate, excessive, or unsupported playlist identifiers or playlist-item identifiers; the response must identify invalid selector input.
- The caller provides page tokens, page-size values, or other paging controls for a selector mode where the public contract does not support paging; the response must identify selector-incompatible paging input.
- The request is validly shaped and eligible for access but returns an empty playlist-item collection; the result must distinguish an empty successful collection from invalid input, insufficient access, missing resources, and upstream failure.
- The upstream success response omits optional fields or returns partial playlist item resources according to the selected parts; the result must preserve returned fields without fabricating missing playlist item, video, playlist, or channel data.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects playlist item insertion, update, deletion, playlist search, playlist mutation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `playlistItems_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `playlistItems.list` identity, official quota-unit cost of `1`, API-key access disclosure for the supported selector set, required part selection, supported `playlistId` lookup, supported `id` lookup, selector-specific pagination guidance, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing part selection, invalid part selection, missing lookup selectors, conflicting selectors, invalid identifiers, unsupported or selector-incompatible paging, unsupported modifiers, ineligible access context, empty result handling, and out-of-scope playlist-item or playlist-management requests.
- **Red**: Add failing result-contract checks proving that returned playlist item collection fields, selected part context, lookup mode, paging context when applicable, quota context, successful empty outcomes, access failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `playlistItems_list` tool contract and behavior needed for callers to make supported low-level `playlistItems.list` requests and receive near-raw playlist-item collection results.
- **Green**: Include representative examples for playlist-scoped retrieval, identifier-based retrieval, paginated playlist traversal, empty successful results, missing part validation failure, invalid part validation failure, missing selector validation failure, conflicting selector validation failure, unsupported paging or modifier validation failure, access failure, and out-of-scope playlist-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `playlistItems_list` request, response, quota, access, part-selection, selector, pagination, unsupported modifier, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository test-suite run, and a passing repository code-quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, selector, paging, unsupported-option, and access-boundary validation, integration-style checks for representative successful and failed playlist-item retrieval paths, and documentation checks for quota/access/selector/pagination/example visibility.
- **Docstring work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `playlistItems_list` responsibility, inputs, outputs, quota cost, access behavior, part-selection behavior, selector behavior, paging boundary, empty-result behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-232`, the dependency assumptions from YT-132/YT-201/YT-202, focused `playlistItems_list` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `playlistItems_list`.
- **FR-002**: The `playlistItems_list` tool definition MUST identify its mapped upstream operation as YouTube resource `playlistItems` and method `list`.
- **FR-003**: The `playlistItems_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `playlistItems_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `playlistItems_list` tool metadata MUST state the documented API-key access mode for the supported selector set and MUST make access expectations visible to callers before invocation.
- **FR-006**: The `playlistItems_list` input contract MUST preserve the upstream concepts of required part selection, playlist-scoped retrieval, identifier-based retrieval, pagination, page tokens, and maximum result count where those concepts are supported.
- **FR-007**: The `playlistItems_list` input contract MUST require supported part selection for each retrieval request and MUST document that part selection determines which playlist item properties are returned.
- **FR-008**: The `playlistItems_list` input contract MUST support playlist-scoped retrieval through a `playlistId` selector.
- **FR-009**: The `playlistItems_list` input contract MUST support identifier-based retrieval through one or more playlist-item `id` values.
- **FR-010**: The `playlistItems_list` input contract MUST require exactly one supported lookup selector for each request and MUST reject requests that omit selectors or combine mutually exclusive selectors.
- **FR-011**: The `playlistItems_list` tool MUST support valid playlist-scoped retrieval requests with no pagination token and MUST preserve returned page context when additional pages are available.
- **FR-012**: The `playlistItems_list` tool MUST support valid playlist-scoped retrieval requests that include supported pagination inputs, including page token and maximum result count within official limits.
- **FR-013**: The `playlistItems_list` input contract MUST document which supported lookup modes accept page tokens, maximum result count, or both, and MUST reject selector-incompatible paging inputs with clear caller-facing validation feedback.
- **FR-014**: The `playlistItems_list` input contract MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-015**: The `playlistItems_list` input contract MUST reject missing, empty, malformed, duplicate, excessive, unsupported, or conflicting playlist identifiers and playlist-item identifiers with clear caller-facing validation feedback.
- **FR-016**: The `playlistItems_list` input contract MUST reject unsupported optional parameters, unsupported modifiers, invalid page tokens, out-of-range maximum result counts, unsupported selector combinations, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-017**: The `playlistItems_list` tool MUST reject or clearly categorize missing, invalid, or insufficient access as an access failure rather than a successful playlist-item list result.
- **FR-018**: The `playlistItems_list` result MUST preserve playlist item resources, selected part context, lookup selector context, pagination context when applicable, quota context, access context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-019**: The `playlistItems_list` result MUST distinguish successful populated collections from successful empty collections.
- **FR-020**: The `playlistItems_list` tool MUST distinguish successful empty playlist-item collections from validation failures, access failures, missing-resource failures, quota failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-021**: The `playlistItems_list` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-022**: The `playlistItems_list` contract MUST document applicable official limits and caveats, including quota cost, access expectations, required part selection, `playlistId` and `id` selectors, selector-specific paging behavior, unsupported modifier behavior, empty-result behavior, and availability state.
- **FR-023**: The `playlistItems_list` contract MUST remain close to the upstream `playlistItems.list` endpoint and MUST NOT add playlist-item insertion, update, deletion, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-024**: The `playlistItems_list` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, list result, pagination, selector-boundary, validation, error, and example standards established by YT-201 and YT-202.
- **FR-025**: The `playlistItems_list` tool MUST rely on the existing Layer 1 `playlistItems.list` capability from YT-132 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-026**: The feature MUST include caller-facing examples for at least one playlist-scoped retrieval request, one identifier-based retrieval request, one paginated playlist traversal request, one empty successful result, one missing-part validation failure, one invalid-part validation failure, one missing-selector validation failure, one conflicting-selector validation failure, one unsupported paging or modifier validation failure, one access failure, and one out-of-scope playlist-management request rejection.
- **FR-027**: The feature MUST include validation evidence that clients can discover, call, understand quota, access, part-selection, selector, pagination, unsupported modifier, failure, and empty-result requirements, interpret list results, and handle failures for `playlistItems_list` without consulting implementation-only artifacts.

### Key Entities

- **Playlist Items List Tool**: The public Layer 2 MCP tool named `playlistItems_list`, representing one low-level endpoint-backed playlist-item retrieval operation.
- **Playlist Items List Request**: The request shape centered on required part selection, exactly one supported lookup selector, and any selector-compatible pagination inputs.
- **Part Selection**: The caller-selected playlist item resource sections that determine which playlist item properties are returned.
- **Playlist Item Lookup Selector**: The supported retrieval mode, either playlist-scoped lookup by playlist identifier or direct lookup by playlist-item identifier, including its validation and paging boundaries.
- **Pagination Context**: The caller-provided and returned page information that allows clients to traverse supported playlist-scoped result pages.
- **Access Context**: The caller access state required to retrieve playlist item resources without exposing credentials or sensitive access details.
- **Playlist Item Resource**: A returned playlist entry visible for the selected lookup and selected parts.
- **Playlist Items List Result**: The returned playlist item collection, selected parts, lookup selector, paging context when applicable, quota context, access context, and upstream fields produced by a successful `playlistItems_list` call.
- **Quota Disclosure**: The caller-facing statement that each `playlistItems_list` invocation costs 1 official quota unit.
- **Unsupported Boundary Guidance**: The caller-facing explanation that playlist item insertion, update, deletion, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, and recommendation are outside this low-level playlist-item listing tool.

### Assumptions

- YT-132 provides the Layer 1 `playlistItems.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, access, response-shaping, list result, pagination, selector validation, error, example, and validation standards this feature must follow.
- `playlistItems_list` is a low-level endpoint-backed tool for direct playlist-item retrieval, debugging, playlist traversal, and power-user workflows; playlist item mutation, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-132 contract treats `part` as required, `playlistId` and `id` as the supported lookup selectors, the supported selector set as API-key accessible, and unsupported selector combinations or modifiers as outside the supported contract for this slice.
- Pagination is expected for playlist-scoped traversal, while identifier-based retrieval only supports pagination if the shared contract explicitly allows it; unsupported selector-specific paging must be rejected rather than silently ignored.
- A valid accessible request may return an empty playlist-item list, and that outcome should remain distinguishable from invalid input, insufficient access, missing resources, and upstream failure.
- The official YouTube Data API documentation and existing project inventory are the default sources for `playlistItems.list` quota cost, access behavior, part-selection rules, selector behavior, pagination behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-232 seed identifies the official quota-unit cost as `1` for this public Layer 2 contract.
- Representative coverage of playlist-scoped retrieval, identifier-based retrieval, pagination, missing part selection, invalid part selection, missing selectors, conflicting selectors, unsupported paging or modifiers, access failure, empty successful results, and returned playlist-item collection results is sufficient for this slice.

### Dependencies

- `YT-132` Layer 1 `playlistItems.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `playlistItems.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute which access mode applies to the supported `playlistItems_list` selector set by reading the tool contract alone.
- **SC-003**: A client developer can identify required part selection, `playlistId` and `id` lookup selectors, selector-specific pagination behavior, unsupported modifier boundaries, and out-of-scope playlist-management behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `playlistItems_list`, choose valid inputs, understand the quota and access impact, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `playlistItems_list` requests return playlist-item collection results with selected part context, lookup selector context, pagination context when applicable, quota context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, use invalid part selection, omit lookup selectors, combine conflicting selectors, use invalid identifiers, use unsupported paging, include unsupported modifiers, lack eligible access, or request out-of-scope playlist-management behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative empty-result, quota, authorization, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `playlistItems_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, access, availability, list result, pagination, selector-boundary, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `playlistItems_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
