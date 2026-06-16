# Feature Specification: Layer 2 Tool `comments_list`

**Feature Branch**: `216-comments-list`  
**Created**: 2026-06-15  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-216, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Comments Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `comments_list` tool to retrieve comments by comment identifier or replies by parent-comment identifier while staying close to the upstream `comments.list` retrieval behavior and returned comment collection.

**Why this priority**: This is the core value of YT-216. Layer 2 must expose endpoint-backed comment retrieval for direct inspection, debugging, moderation support, and later composition without turning the tool into a higher-level discussion analysis, sentiment, ranking, thread summarization, or moderation workflow.

**Independent Test**: Can be tested by invoking `comments_list` with a valid part selection and either comment identifiers or a parent-comment identifier, then confirming the caller receives a near-raw comment list result with metadata identifying the mapped upstream operation and retrieval mode.

**Acceptance Scenarios**:

1. **Given** a caller provides one or more comment identifiers and a supported part selection, **When** they call `comments_list`, **Then** the result includes the matching comment resources and preserves operation context for direct ID-based retrieval.
2. **Given** a caller provides a parent-comment identifier and a supported part selection, **When** they call `comments_list`, **Then** the result includes the matching reply comments and preserves operation context for parent-comment retrieval.
3. **Given** a caller uses supported pagination or formatting options for comment retrieval, **When** the upstream operation returns a page of comments, **Then** the result preserves the returned comments, paging context, selected parts, and text-format behavior without adding unrelated thread, video, channel, or moderation analysis.
4. **Given** a caller wants direct access to comment retrieval behavior, **When** they use `comments_list`, **Then** the tool performs only the comment list operation and is not presented as comment-thread listing, reply creation, moderation status changes, comment editing, comment deletion, enrichment, or ranking.

---

### User Story 2 - Understand Cost, Auth, and Lookup Modes Before Calling (Priority: P2)

As a client developer, I can inspect `comments_list` before invoking it and immediately understand that it maps to `comments.list`, costs 1 official quota unit per call, supports ID-based and parent-comment retrieval modes, and has access expectations that depend on the selected retrieval context.

**Why this priority**: Comment retrieval is quota-bearing and selector-sensitive. Callers need quota, auth-mode, selector, part-selection, pagination, and text-format visibility in discovery, descriptions, and examples before they spend quota or build workflows against the public tool.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, auth-mode disclosure, required part selection, supported ID and parent-comment selectors, supported pagination and text-format options, and no-match behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `comments_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, auth-mode expectations, required part selection, and supported retrieval modes.
2. **Given** an example request is shown for `comments_list`, **When** a caller reads the example, **Then** the quota cost of `1`, part selection, selector choice, and expected list result are visible alongside the request shape.
3. **Given** a caller needs to retrieve comments across pages, **When** they inspect the tool contract, **Then** the supported pagination inputs and returned page context are clear before invocation.
4. **Given** a caller needs comment text in a supported format, **When** they inspect the tool contract, **Then** the supported text-format behavior is visible without implying higher-level text normalization or analysis.

---

### User Story 3 - Reject Unsupported Comment List Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `comments_list` request omits required selectors, mixes incompatible selectors, omits part selection, uses unsupported options, or requests inaccessible comments, so I can correct the request without guessing which comment-list rule was violated.

**Why this priority**: `comments.list` combines required part selection, mutually exclusive lookup selectors, optional pagination, optional formatting, and access-sensitive results. Clear validation protects callers from ambiguous retrieval failures while keeping the tool faithful to the endpoint instead of inventing fallback lookup, thread traversal, moderation, or search behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing part selection, missing selector, conflicting selectors, malformed identifiers, unsupported options, invalid pagination values, unsupported formatting, inaccessible comments, and no-match outcomes, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits both comment identifiers and parent-comment identifier, **When** they call `comments_list`, **Then** the request is rejected with guidance that exactly one supported retrieval selector is required.
2. **Given** a caller provides both comment identifiers and parent-comment identifier, **When** they call `comments_list`, **Then** the request is rejected with guidance that retrieval modes cannot be combined.
3. **Given** a caller provides no supported part selection, **When** they call `comments_list`, **Then** the request is rejected with guidance that part selection is required.
4. **Given** a caller requests comments that are inaccessible, unavailable, or not found, **When** they call `comments_list`, **Then** the response preserves the appropriate no-match, access, or upstream failure signal using the shared Layer 2 result and error conventions.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported retrieval attempt.
- The caller omits both supported selectors; the response must identify that ID-based or parent-comment retrieval is required.
- The caller supplies both `id` and `parentId` selectors in the same request; the response must identify the mutually exclusive selector rule.
- The caller provides empty, malformed, duplicate, too many, or otherwise unsupported comment identifiers; the response must identify invalid identifier input.
- The caller provides an empty, malformed, or unsupported parent-comment identifier; the response must identify invalid parent-comment selector input.
- The caller requests replies for a parent comment that exists but has no reply comments; the result must distinguish an empty successful collection from a failed retrieval.
- The caller requests comments that do not exist, are private, deleted, held for review, unavailable, or inaccessible to the selected access context; the response must preserve no-match, access, or upstream failure meaning.
- The caller supplies unsupported part names, unsupported optional parameters, invalid page tokens, unsupported page sizes, unsupported text-format values, or unsupported sorting, search, moderation, or thread traversal options; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream success response omits optional fields or returns partial comment resources according to the selected parts; the result must preserve returned fields without fabricating missing comment data.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects comment-thread listing, top-level thread discovery, reply creation, comment updates, moderation status changes, deletion, sentiment analysis, ranking, summarization, enrichment, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `comments_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `comments.list` identity, official quota-unit cost of `1`, auth-mode disclosure, required part selection, supported ID-based retrieval, supported parent-comment retrieval, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required part selection, exactly one supported selector, comment identifier validation, parent-comment identifier validation, pagination limits, supported text-format options, unsupported option rejection, no-match behavior, access-sensitive failures, and discovery examples for both retrieval modes.
- **Red**: Add failing result-contract checks proving that returned comment collection fields, selected part context, retrieval mode, paging context, text-format context, no-match outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `comments_list` tool contract and behavior needed for callers to make supported low-level `comments.list` requests and receive near-raw comment collection results.
- **Green**: Include representative examples for ID-based retrieval, parent-comment reply retrieval, paginated retrieval, supported text-format selection, empty successful results, missing selector validation failure, conflicting selector validation failure, invalid identifier validation failure, unsupported option validation failure, and access-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `comments_list` request, response, quota, auth, selector, pagination, formatting, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for selector, pagination, text-format, and access-context validation, integration-style checks for representative successful and failed comment retrieval paths, and documentation checks for quota/auth/retrieval-mode/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `comments_list` responsibility, inputs, outputs, quota cost, auth behavior, selector rules, pagination behavior, text-format behavior, no-match behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-216`, the dependency assumptions from YT-116/YT-201/YT-202, focused `comments_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `comments_list`.
- **FR-002**: The `comments_list` tool definition MUST identify its mapped upstream operation as YouTube resource `comments` and method `list`.
- **FR-003**: The `comments_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `comments_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `comments_list` tool metadata MUST state the supported auth mode for comment retrieval and MUST make access-sensitive retrieval limitations visible to callers before invocation.
- **FR-006**: The `comments_list` input contract MUST preserve the upstream concepts of required part selection, ID-based comment retrieval, parent-comment-based reply retrieval, pagination, maximum result count, and text-format selection where those concepts are supported.
- **FR-007**: The `comments_list` input contract MUST require a supported part selection for each retrieval request and MUST document that part selection determines which comment properties are returned.
- **FR-008**: The `comments_list` input contract MUST support ID-based retrieval for one or more comment identifiers.
- **FR-009**: The `comments_list` input contract MUST support parent-comment-based retrieval for reply comments under one parent comment.
- **FR-010**: The `comments_list` input contract MUST require exactly one supported retrieval selector for each request and MUST reject requests that omit selectors or combine mutually exclusive selectors.
- **FR-011**: The `comments_list` tool MUST support valid retrieval requests with no pagination token and MUST preserve returned page context when additional pages are available.
- **FR-012**: The `comments_list` tool MUST support valid retrieval requests that include supported pagination inputs, including page token and maximum result count within official limits.
- **FR-013**: The `comments_list` tool MUST support valid retrieval requests that include supported text-format selection and MUST preserve the resulting comment text behavior in the response context.
- **FR-014**: The `comments_list` tool MUST reject missing, empty, malformed, duplicate, excessive, or unsupported comment identifier input with clear caller-facing validation feedback.
- **FR-015**: The `comments_list` tool MUST reject missing, empty, malformed, or unsupported parent-comment identifier input with clear caller-facing validation feedback.
- **FR-016**: The `comments_list` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-017**: The `comments_list` tool MUST reject unsupported optional parameters, unsupported sort/search/thread traversal/moderation options, invalid page tokens, unsupported maximum result counts, unsupported text-format values, and unsupported selector combinations with clear caller-facing validation feedback.
- **FR-018**: The `comments_list` result MUST preserve comment resources, selected part context, retrieval mode, pagination context, text-format context, relevant access context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-019**: The `comments_list` tool MUST distinguish successful empty comment collections from validation failures, authorization failures, unavailable resources, quota failures, and unexpected upstream failures.
- **FR-020**: The `comments_list` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-021**: The `comments_list` contract MUST document applicable official limits and caveats, including quota cost, auth-mode expectations, required part selection, mutually exclusive selectors, supported pagination behavior, maximum result behavior, text-format behavior, unavailable or inaccessible comment behavior, and availability state.
- **FR-022**: The `comments_list` contract MUST remain close to the upstream `comments.list` endpoint and MUST NOT add higher-level comment-thread discovery, comment search, reply creation, comment update, moderation status change, deletion, sentiment analysis, ranking, summarization, enrichment, or heuristic interpretation.
- **FR-023**: The `comments_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, pagination, selector validation, error, and example standards established by YT-201 and YT-202.
- **FR-024**: The `comments_list` tool MUST rely on the existing Layer 1 `comments.list` capability from YT-116 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-025**: The feature MUST include caller-facing examples for at least one ID-based retrieval request, one parent-comment reply retrieval request, one paginated retrieval request, one text-format request, one empty successful result, one missing-selector validation failure, one conflicting-selector validation failure, one invalid-identifier validation failure, one unsupported option validation failure, and one access-sensitive failure.
- **FR-026**: The feature MUST include validation evidence that clients can discover, call, understand quota, auth, part-selection, selector, pagination, and text-format requirements, interpret list results, and handle failures for `comments_list` without consulting implementation-only artifacts.

### Key Entities

- **Comments List Tool**: The public Layer 2 MCP tool named `comments_list`, representing one low-level endpoint-backed comment retrieval operation.
- **Comments List Request**: The request shape that combines required part selection, exactly one supported retrieval selector, and any supported pagination or text-format options.
- **Part Selection**: The caller-selected comment resource sections that determine which comment properties are returned.
- **Comment Identifier Selector**: The caller-provided selector for direct retrieval of one or more comments by identifier.
- **Parent Comment Selector**: The caller-provided selector for retrieving reply comments under one parent comment.
- **Pagination Context**: The caller-provided and returned page information that allows clients to traverse supported comment result pages.
- **Text Format Selection**: The caller-selected comment text representation where supported by the underlying operation.
- **Comments List Result**: The returned comment collection, paging context, retrieval mode, selected parts, text-format context, and upstream fields produced by a successful `comments_list` call.
- **Quota Disclosure**: The caller-facing statement that each `comments_list` invocation costs 1 official quota unit.
- **Auth and Access Disclosure**: The caller-facing indication of supported auth mode and access-sensitive limitations for comment retrieval.
- **Retrieval Mode Disclosure**: The caller-facing explanation that ID-based retrieval and parent-comment-based reply retrieval are supported and mutually exclusive within a single request.

### Assumptions

- YT-116 provides the Layer 1 `comments.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, pagination, selector validation, error, example, and validation standards this feature must follow.
- `comments_list` is a low-level endpoint-backed tool for direct comment retrieval, debugging, and power-user workflows; higher-level thread discovery, moderation, reply creation, editing, deletion, ranking, sentiment analysis, summarization, analytics, or enrichment workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation and existing project inventory are the default sources for `comments.list` quota cost, auth behavior, part-selection rules, ID selector behavior, parent-comment selector behavior, pagination limits, text-format behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of ID-based retrieval, parent-comment reply retrieval, pagination, text-format handling, missing selector, conflicting selectors, invalid identifiers, unsupported options, access-sensitive failures, empty successful results, and returned comment collection results is sufficient for this slice.

### Dependencies

- `YT-116` Layer 1 `comments.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `comments.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute which auth mode and access-sensitive limitations apply to `comments_list` by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, supported ID-based retrieval mode, supported parent-comment retrieval mode, and mutually exclusive selector rule in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `comments_list`, choose a valid retrieval mode, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `comments_list` requests return comment collection results with retrieval mode, selected part context, pagination context, text-format context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, omit selectors, combine selectors, use invalid identifiers, use invalid pagination, use unsupported text formatting, request unavailable comments, or include unsupported options are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative no-match or empty-reply scenarios are distinguishable from validation, authorization, quota, unavailable-resource, and unexpected upstream failures.
- **SC-008**: Reviewers can verify in a single review pass that `comments_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, list result, pagination, selector validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `comments_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
