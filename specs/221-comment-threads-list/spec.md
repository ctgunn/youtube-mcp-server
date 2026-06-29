# Feature Specification: Layer 2 Tool `commentThreads_list`

**Feature Branch**: `221-comment-threads-list`  
**Created**: 2026-06-19  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-221, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Comment Threads Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `commentThreads_list` tool to retrieve top-level YouTube comment threads by video, channel-related thread association, or thread identifier while staying close to the upstream `commentThreads.list` retrieval behavior and returned thread collection.

**Why this priority**: This is the core value of YT-221. Layer 2 must expose endpoint-backed comment-thread retrieval for direct inspection, debugging, moderation support, and later composition without turning the tool into reply listing, comment insertion, thread creation, moderation workflow, sentiment analysis, ranking, summarization, or higher-level discussion analysis.

**Independent Test**: Can be tested by invoking `commentThreads_list` with a valid part selection and one supported retrieval selector, then confirming the caller receives a near-raw comment-thread list result with metadata identifying the mapped upstream operation and retrieval mode.

**Acceptance Scenarios**:

1. **Given** a caller provides a video identifier and supported part selection, **When** they call `commentThreads_list`, **Then** the result includes matching comment threads for that video and preserves operation context for video-based retrieval.
2. **Given** a caller provides an `allThreadsRelatedToChannelId` selector and supported part selection, **When** they call `commentThreads_list`, **Then** the result includes matching threads associated with that channel and preserves operation context for channel-related retrieval.
3. **Given** a caller provides one or more thread identifiers and supported part selection, **When** they call `commentThreads_list`, **Then** the result includes matching thread resources and preserves operation context for ID-based retrieval.
4. **Given** a caller uses supported pagination, ordering, search, or text-format options for thread retrieval, **When** the upstream operation returns a page of threads, **Then** the result preserves returned threads, paging context, selected parts, selector context, and supported option behavior without adding unrelated reply-list, mutation, moderation, ranking, or analysis data.
5. **Given** a caller wants direct access to comment-thread retrieval behavior, **When** they use `commentThreads_list`, **Then** the tool performs only the comment-thread list operation and is not presented as reply creation, thread insertion, comment editing, comment deletion, moderation status change, enrichment, or ranking.

---

### User Story 2 - Understand Cost, Auth, and Filter Modes Before Calling (Priority: P2)

As a client developer, I can inspect `commentThreads_list` before invoking it and immediately understand that it maps to `commentThreads.list`, costs 1 official quota unit per call, supports `videoId`, `allThreadsRelatedToChannelId`, and ID-based retrieval modes, and has access expectations that depend on the selected retrieval context.

**Why this priority**: Comment-thread retrieval is quota-bearing and selector-sensitive. Callers need quota, auth-mode, selector, part-selection, pagination, ordering, search, text-format, and access-limitation visibility in discovery, descriptions, and examples before they spend quota or build workflows against the public tool.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, auth-mode disclosure, required part selection, supported selectors, supported pagination and formatting options, and no-match behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `commentThreads_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, auth-mode expectations, required part selection, and supported retrieval modes.
2. **Given** an example request is shown for `commentThreads_list`, **When** a caller reads the example, **Then** the quota cost of `1`, part selection, selector choice, and expected list result are visible alongside the request shape.
3. **Given** a caller needs to retrieve comment threads across pages, **When** they inspect the tool contract, **Then** the supported pagination inputs and returned page context are clear before invocation.
4. **Given** a caller needs ordered, searched, formatted, or access-sensitive thread results where those options are supported, **When** they inspect the tool contract, **Then** the supported behavior and access caveats are visible without implying higher-level text normalization, moderation automation, or analysis.

---

### User Story 3 - Reject Unsupported Comment Thread List Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `commentThreads_list` request omits required selectors, mixes incompatible selectors, omits part selection, uses unsupported options, or requests inaccessible thread data, so I can correct the request without guessing which comment-thread rule was violated.

**Why this priority**: `commentThreads.list` combines required part selection, mutually exclusive lookup selectors, optional pagination, optional ordering, optional search and formatting controls, and access-sensitive results. Clear validation protects callers from ambiguous retrieval failures while keeping the tool faithful to the endpoint instead of inventing fallback lookup, reply traversal, mutation, moderation, or search behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing part selection, missing selector, conflicting selectors, malformed identifiers, unsupported options, invalid pagination values, unsupported formatting, access-sensitive moderation options without eligible authorization, inaccessible threads, and no-match outcomes, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits all supported retrieval selectors, **When** they call `commentThreads_list`, **Then** the request is rejected with guidance that exactly one supported retrieval selector is required.
2. **Given** a caller combines `videoId`, `allThreadsRelatedToChannelId`, or ID-based selectors in one request, **When** they call `commentThreads_list`, **Then** the request is rejected with guidance that retrieval modes cannot be combined.
3. **Given** a caller provides no supported part selection, **When** they call `commentThreads_list`, **Then** the request is rejected with guidance that part selection is required.
4. **Given** a caller requests threads that are inaccessible, unavailable, hidden, disabled, or not found, **When** they call `commentThreads_list`, **Then** the response preserves the appropriate no-match, access, or upstream failure signal using the shared Layer 2 result and error conventions.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported retrieval attempt.
- The caller omits all supported selectors; the response must identify that video-based, channel-related, or ID-based retrieval is required.
- The caller supplies more than one primary selector, such as `videoId` plus `allThreadsRelatedToChannelId`, `videoId` plus thread identifiers, or channel-related lookup plus thread identifiers; the response must identify the mutually exclusive selector rule.
- The caller provides empty, malformed, duplicate, excessive, or otherwise unsupported thread identifiers; the response must identify invalid identifier input.
- The caller provides an empty, malformed, or unsupported `videoId` or `allThreadsRelatedToChannelId` selector; the response must identify invalid selector input.
- The caller requests threads for a video or channel that exists but currently has no retrievable comment threads; the result must distinguish an empty successful collection from a failed retrieval.
- The caller requests comment threads that do not exist, are private, deleted, hidden, held for review, unavailable, disabled by comment settings, or inaccessible to the selected access context; the response must preserve no-match, access, disabled-comment, or upstream failure meaning.
- The caller supplies unsupported part names, unsupported optional parameters, invalid page tokens, unsupported page sizes, unsupported order values, unsupported search values, unsupported text-format values, moderation-related filters without eligible authorization, or unsupported reply traversal, mutation, or analysis options; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream success response omits optional fields or returns partial thread resources according to the selected parts; the result must preserve returned fields without fabricating missing comment-thread data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects reply listing, thread creation, comment insertion, comment editing, comment deletion, moderation status changes, sentiment analysis, ranking, summarization, enrichment, automated moderation advice, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `commentThreads_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `commentThreads.list` identity, official quota-unit cost of `1`, auth-mode disclosure, required part selection, supported video-based retrieval, supported channel-related retrieval, supported ID-based retrieval, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required part selection, exactly one supported selector, thread identifier validation, video identifier validation, channel-related identifier validation, pagination limits, supported order behavior, supported search behavior, supported text-format options, access-sensitive moderation filters, unsupported option rejection, no-match behavior, and discovery examples for each retrieval mode.
- **Red**: Add failing result-contract checks proving that returned comment-thread collection fields, selected part context, retrieval mode, paging context, supported option context, no-match outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `commentThreads_list` tool contract and behavior needed for callers to make supported low-level `commentThreads.list` requests and receive near-raw comment-thread collection results.
- **Green**: Include representative examples for video-based retrieval, channel-related retrieval, ID-based retrieval, paginated retrieval, supported ordering, supported search, supported text-format selection, empty successful results, missing selector validation failure, conflicting selector validation failure, invalid identifier validation failure, unsupported option validation failure, and access-sensitive failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `commentThreads_list` request, response, quota, auth, selector, pagination, option, caveat, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for selector, pagination, ordering, search, text-format, access-context, and unsupported-option validation, integration-style checks for representative successful and failed comment-thread retrieval paths, and documentation checks for quota/auth/filter-mode/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `commentThreads_list` responsibility, inputs, outputs, quota cost, auth behavior, selector rules, pagination behavior, supported option behavior, no-match behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-221`, the dependency assumptions from YT-121/YT-201/YT-202, focused `commentThreads_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `commentThreads_list`.
- **FR-002**: The `commentThreads_list` tool definition MUST identify its mapped upstream operation as YouTube resource `commentThreads` and method `list`.
- **FR-003**: The `commentThreads_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `commentThreads_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `commentThreads_list` tool metadata MUST state the supported auth mode for comment-thread retrieval and MUST make access-sensitive retrieval limitations visible to callers before invocation.
- **FR-006**: The `commentThreads_list` input contract MUST preserve the upstream concepts of required part selection, video-based retrieval, channel-related retrieval through `allThreadsRelatedToChannelId`, ID-based thread retrieval, pagination, maximum result count, ordering, search terms, text-format selection, and access-sensitive filters where those concepts are supported.
- **FR-007**: The `commentThreads_list` input contract MUST require a supported part selection for each retrieval request and MUST document that part selection determines which comment-thread properties are returned.
- **FR-008**: The `commentThreads_list` input contract MUST support video-based retrieval for one video identifier.
- **FR-009**: The `commentThreads_list` input contract MUST support channel-related retrieval for one `allThreadsRelatedToChannelId` selector.
- **FR-010**: The `commentThreads_list` input contract MUST support ID-based retrieval for one or more comment-thread identifiers.
- **FR-011**: The `commentThreads_list` input contract MUST require exactly one supported retrieval selector for each request and MUST reject requests that omit selectors or combine mutually exclusive selectors.
- **FR-012**: The `commentThreads_list` tool MUST support valid retrieval requests with no pagination token and MUST preserve returned page context when additional pages are available.
- **FR-013**: The `commentThreads_list` tool MUST support valid retrieval requests that include supported pagination inputs, including page token and maximum result count within official limits.
- **FR-014**: The `commentThreads_list` tool MUST support valid retrieval requests that include supported ordering, search-term, text-format, and access-sensitive filter inputs where those inputs are valid for the selected retrieval mode and authorization context.
- **FR-015**: The `commentThreads_list` tool MUST reject missing, empty, malformed, duplicate, excessive, or unsupported thread identifier input with clear caller-facing validation feedback.
- **FR-016**: The `commentThreads_list` tool MUST reject missing, empty, malformed, or unsupported video identifier input with clear caller-facing validation feedback.
- **FR-017**: The `commentThreads_list` tool MUST reject missing, empty, malformed, or unsupported `allThreadsRelatedToChannelId` input with clear caller-facing validation feedback.
- **FR-018**: The `commentThreads_list` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-019**: The `commentThreads_list` tool MUST reject unsupported optional parameters, unsupported selector combinations, invalid page tokens, unsupported maximum result counts, unsupported order values, unsupported search values, unsupported text-format values, access-sensitive filters without eligible authorization, reply-listing fields, mutation fields, moderation-action fields, ranking instructions, summarization instructions, and unsupported retrieval shapes with clear caller-facing validation feedback.
- **FR-020**: The `commentThreads_list` result MUST preserve comment-thread resources, selected part context, retrieval mode, pagination context, supported option context, relevant access context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-021**: The `commentThreads_list` tool MUST distinguish successful empty comment-thread collections from validation failures, authorization failures, unavailable resources, disabled-comment states, quota failures, and unexpected upstream failures.
- **FR-022**: The `commentThreads_list` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-023**: The `commentThreads_list` contract MUST document applicable official limits and caveats, including quota cost, auth-mode expectations, required part selection, mutually exclusive selectors, supported pagination behavior, maximum result behavior, ordering behavior, search behavior, text-format behavior, access-sensitive filter behavior, unavailable or inaccessible thread behavior, disabled-comment behavior, and availability state.
- **FR-024**: The `commentThreads_list` contract MUST remain close to the upstream `commentThreads.list` endpoint and MUST NOT add higher-level reply listing, thread creation, comment insertion, comment editing, comment deletion, moderation status change, sentiment analysis, ranking, summarization, enrichment, automated moderation recommendation, or heuristic interpretation.
- **FR-025**: The `commentThreads_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, pagination, selector validation, error, and example standards established by YT-201 and YT-202.
- **FR-026**: The `commentThreads_list` tool MUST rely on the existing Layer 1 `commentThreads.list` capability from YT-121 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-027**: The feature MUST include caller-facing examples for at least one video-based retrieval request, one channel-related retrieval request, one ID-based retrieval request, one paginated retrieval request, one supported order request, one supported search request, one text-format request, one empty successful result, one missing-selector validation failure, one conflicting-selector validation failure, one invalid-identifier validation failure, one unsupported option validation failure, and one access-sensitive failure.
- **FR-028**: The feature MUST include validation evidence that clients can discover, call, understand quota, auth, part-selection, selector, pagination, supported option, and access-sensitive requirements, interpret list results, and handle failures for `commentThreads_list` without consulting implementation-only artifacts.

### Key Entities

- **Comment Threads List Tool**: The public Layer 2 MCP tool named `commentThreads_list`, representing one low-level endpoint-backed comment-thread retrieval operation.
- **Comment Threads List Request**: The request shape that combines required part selection, exactly one supported retrieval selector, and any supported pagination, ordering, search, text-format, or access-sensitive filter options.
- **Part Selection**: The caller-selected comment-thread resource sections that determine which thread properties are returned.
- **Video Identifier Selector**: The caller-provided selector for retrieving comment threads associated with one video.
- **Channel-Related Selector**: The caller-provided `allThreadsRelatedToChannelId` selector for retrieving comment threads associated with one channel.
- **Thread Identifier Selector**: The caller-provided selector for direct retrieval of one or more comment threads by identifier.
- **Pagination Context**: The caller-provided and returned page information that allows clients to traverse supported comment-thread result pages.
- **Supported Option Context**: The caller-provided ordering, search, text-format, or access-sensitive filter choices that shape valid thread retrieval.
- **Comment Threads List Result**: The returned comment-thread collection, paging context, retrieval mode, selected parts, supported option context, and upstream fields produced by a successful `commentThreads_list` call.
- **Quota Disclosure**: The caller-facing statement that each `commentThreads_list` invocation costs 1 official quota unit.
- **Auth and Access Disclosure**: The caller-facing indication of supported auth mode and access-sensitive limitations for comment-thread retrieval.
- **Retrieval Mode Disclosure**: The caller-facing explanation that video-based, channel-related, and ID-based retrieval are supported and mutually exclusive within a single request.

### Assumptions

- YT-121 provides the Layer 1 `commentThreads.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, pagination, selector validation, error, example, and validation standards this feature must follow.
- `commentThreads_list` is a low-level endpoint-backed tool for direct comment-thread retrieval, debugging, and power-user workflows; higher-level reply listing, thread insertion, comment mutation, moderation workflows, ranking, sentiment analysis, summarization, analytics, or enrichment workflows belong to separate endpoint or Layer 3 features.
- The seed-required retrieval modes for this slice are `videoId`, `allThreadsRelatedToChannelId`, and ID-based retrieval. Other upstream options may be exposed only when they preserve the endpoint-backed boundary and are clearly documented in the public contract.
- The official YouTube Data API documentation and existing project inventory are the default sources for `commentThreads.list` quota cost, auth behavior, part-selection rules, selector behavior, pagination limits, ordering behavior, search behavior, text-format behavior, moderation-filter access caveats, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of video-based retrieval, channel-related retrieval, ID-based retrieval, pagination, ordering, search, text-format handling, missing selector, conflicting selectors, invalid identifiers, unsupported options, access-sensitive failures, empty successful results, and returned comment-thread collection results is sufficient for this slice.

### Dependencies

- `YT-121` Layer 1 `commentThreads.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `commentThreads_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `commentThreads.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute which auth mode and access-sensitive limitations apply to `commentThreads_list` by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, supported video-based retrieval mode, supported channel-related retrieval mode, supported ID-based retrieval mode, and mutually exclusive selector rule in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `commentThreads_list`, choose a valid retrieval mode, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `commentThreads_list` requests return comment-thread collection results with retrieval mode, selected part context, pagination context, supported option context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, omit selectors, combine selectors, use invalid identifiers, use invalid pagination, use unsupported options, request unavailable threads, include access-sensitive filters without eligible authorization, or include unsupported operation fields are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative no-match, empty-thread, disabled-comment, inaccessible-thread, quota, authorization, unavailable-resource, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `commentThreads_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, list result, pagination, selector validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `commentThreads_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
