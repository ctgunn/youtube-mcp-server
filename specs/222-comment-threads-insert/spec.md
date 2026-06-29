# Feature Specification: Layer 2 Tool `commentThreads_insert`

**Feature Branch**: `222-comment-threads-insert`  
**Created**: 2026-06-29  
**Status**: Draft  
**Input**: User description: "Review the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-222, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Top-Level Comment Threads Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `commentThreads_insert` tool to create a new top-level YouTube comment thread while staying close to the upstream `commentThreads.insert` write behavior and returned comment-thread resource.

**Why this priority**: This is the core value of YT-222. Layer 2 must expose endpoint-backed top-level comment-thread creation for direct write workflows, debugging, and later composition without turning the tool into reply creation, listing, moderation, ranking, summarization, or a higher-level conversation workflow.

**Independent Test**: Can be tested by invoking `commentThreads_insert` with eligible OAuth authorization, supported part selection, and a valid top-level comment-thread body for a comment-enabled video, then confirming the caller receives the created comment-thread resource in a near-raw endpoint-backed shape with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides a valid top-level comment-thread body for a comment-enabled video, **When** they call `commentThreads_insert` with supported part selection, **Then** the result includes the created comment-thread resource and preserves the requested operation context.
2. **Given** a caller provides all required top-level thread creation inputs and supported optional write context, **When** the thread is created, **Then** the result preserves the returned comment-thread fields without adding unrelated reply, listing, moderation, ranking, or analysis data.
3. **Given** the creation succeeds and returns a single comment-thread resource, **When** the caller inspects the result, **Then** the mutation outcome is clear and is not presented as a list, reply creation, thread traversal, or higher-level discussion workflow.
4. **Given** a caller wants direct access to top-level comment-thread creation behavior, **When** they use `commentThreads_insert`, **Then** the tool performs only the comment-thread insert operation and is not presented as comment reply creation, comment editing, comment deletion, moderation status change, enrichment, or automated response generation.

---

### User Story 2 - Understand Cost, OAuth, and Top-Level Comment Rules Before Calling (Priority: P2)

As a client developer, I can inspect `commentThreads_insert` before invoking it and immediately understand that it maps to `commentThreads.insert`, costs 50 official quota units per call, requires eligible OAuth authorization, and creates top-level comment threads rather than replies.

**Why this priority**: Comment-thread creation is quota-bearing, permission-sensitive, and publicly visible. Callers need quota, OAuth, part-selection, target video, top-level comment body, and write-boundary visibility in discovery, descriptions, and examples before they spend quota or publish content.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required part selection, required top-level comment-thread body, target-video relationship, and unsupported write shapes are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `commentThreads_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported top-level thread creation boundary.
2. **Given** an example request is shown for `commentThreads_insert`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a valid top-level comment body are visible alongside the request shape.
3. **Given** a caller needs to publish a top-level comment on a specific video, **When** they inspect the tool contract, **Then** the required relationship between target video, top-level comment content, selected response parts, and returned created-thread fields is clear before invocation.
4. **Given** a caller wants to create a reply, list threads, moderate comments, edit comments, or delete comments, **When** they inspect the tool contract, **Then** those separate endpoint or higher-level behaviors are clearly outside the `commentThreads_insert` boundary.

---

### User Story 3 - Reject Unsupported Thread Creation Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `commentThreads_insert` request lacks eligible OAuth authorization, omits required top-level comment-thread fields, references an invalid or unavailable target, or includes unsupported write options, so I can correct the request without guessing which thread-create rule was violated.

**Why this priority**: `commentThreads.insert` combines write authorization, part selection, target context, top-level comment content, and upstream write failures. Clear validation protects callers from ambiguous publish failures while keeping the tool faithful to the endpoint instead of inventing fallback repair, reply creation, or moderation behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing part selection, missing target video, missing top-level comment content, unsupported reply shapes, unsupported fields, and inaccessible or comment-disabled targets, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `commentThreads_insert`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a comment-format failure.
2. **Given** a caller omits the required target context for top-level thread creation, **When** they call `commentThreads_insert`, **Then** the request is rejected with guidance that a valid target video context is required.
3. **Given** a caller omits top-level comment content or provides content that is empty after validation, **When** they call `commentThreads_insert`, **Then** the request is rejected with guidance that publishable top-level comment content is required.
4. **Given** a caller includes reply creation fields, listing filters, moderation instructions, update fields, deletion instructions, or unsupported optional parameters, **When** they call `commentThreads_insert`, **Then** the request is rejected or clearly flagged as outside the endpoint-backed tool contract.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported create attempt.
- The caller has no eligible OAuth authorization or lacks permission to publish in the target context; the response must distinguish access failure from malformed comment-thread content.
- The caller omits the target video context, provides an empty target reference, or references a malformed target; the response must identify the target-context rule.
- The caller provides top-level comment text that is missing, empty after validation, too long, malformed, or otherwise unpublishable; the response must identify the publishable-content rule.
- The caller targets a video that is missing, private, unavailable, disabled for comments, restricted, locked, or inaccessible to the selected authorization context; the response must preserve the appropriate access, disabled-comment, missing-resource, or upstream failure meaning.
- The caller supplies unsupported part names, unsupported body fields, read-only fields, unsupported optional parameters, reply creation fields, listing filters, update fields, moderation fields, deletion fields, search instructions, or automated response instructions; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream success response omits optional fields or returns partial comment-thread resources according to the selected parts; the result must preserve returned fields without fabricating missing comment-thread data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects thread listing, reply creation, comment editing, moderation status changes, deletion, sentiment analysis, ranking, summarization, enrichment, analytics, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `commentThreads_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `commentThreads.insert` identity, official quota-unit cost of `50`, OAuth-required auth mode, required part selection, top-level thread creation boundary, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required part selection, required target video context, required top-level comment content, unsupported reply creation shapes, unsupported body fields, unsupported optional parameters, invalid target identifiers, disabled-comment targets, and access-sensitive failures.
- **Red**: Add failing result-contract checks proving that created comment-thread resource fields, selected part context, mutation outcome details, relevant authorization context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `commentThreads_insert` tool contract and behavior needed for callers to make supported low-level `commentThreads.insert` top-level comment-thread creation requests and receive near-raw created thread results.
- **Green**: Include representative examples for authorized top-level thread creation, missing OAuth authorization, missing part selection, missing target video context, missing top-level comment content, invalid target context, unsupported reply creation shape, unsupported option validation failure, disabled-comment target failure, and access-sensitive upstream failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `commentThreads_insert` request, response, quota, auth, part-selection, top-level comment body, target context, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for top-level thread body, part-selection, authorization, target context, unsupported-field validation, and failure categorization, integration-style checks for representative successful and failed thread-creation paths, and documentation checks for quota/auth/top-level-comment-rule/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `commentThreads_insert` responsibility, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, target-context rule, top-level comment-content rule, mutation result, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-222`, the dependency assumptions from YT-122/YT-201/YT-202, focused `commentThreads_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `commentThreads_insert`.
- **FR-002**: The `commentThreads_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `commentThreads` and method `insert`.
- **FR-003**: The `commentThreads_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `commentThreads_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `commentThreads_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present comment-thread creation as an API-key-only capability.
- **FR-006**: The `commentThreads_insert` input contract MUST preserve the upstream concepts of required part selection, target video context, top-level comment-thread body, and supported optional write context where those concepts are supported.
- **FR-007**: The `commentThreads_insert` input contract MUST require supported part selection for each create request and MUST document that part selection determines which created-thread properties are returned.
- **FR-008**: The `commentThreads_insert` input contract MUST require a top-level comment-thread body that identifies the target video context and the comment content to publish.
- **FR-009**: The `commentThreads_insert` tool MUST support valid authorized top-level thread creation requests when the caller's OAuth authorization is sufficient for the target video context.
- **FR-010**: The `commentThreads_insert` tool MUST reject requests that require OAuth access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-011**: The `commentThreads_insert` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-012**: The `commentThreads_insert` tool MUST reject missing, empty, malformed, unavailable, comment-disabled, or inaccessible target video context with clear caller-facing validation feedback or upstream failure categorization.
- **FR-013**: The `commentThreads_insert` tool MUST reject missing, empty, malformed, unsupported, or unpublishable top-level comment content with clear caller-facing validation feedback.
- **FR-014**: The `commentThreads_insert` tool MUST reject unsupported body fields, read-only fields, unsupported optional parameters, reply creation fields, listing filters, update fields, moderation fields, deletion fields, search instructions, automated response instructions, and unsupported create shapes with clear caller-facing validation feedback.
- **FR-015**: The `commentThreads_insert` result MUST preserve created comment-thread resource fields, selected part context, mutation outcome details, relevant authorization context, target context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-016**: The `commentThreads_insert` tool MUST distinguish successful created-thread outcomes from validation failures, authorization failures, missing or inaccessible targets, disabled-comment failures, quota failures, unavailable resources, and unexpected upstream failures.
- **FR-017**: The `commentThreads_insert` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `commentThreads_insert` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, supported scopes or equivalent access expectations, required part selection, required target video context, top-level comment-content requirements, unsupported create shapes, availability state, and access-sensitive behavior.
- **FR-019**: The `commentThreads_insert` contract MUST remain close to the upstream `commentThreads.insert` endpoint and MUST NOT add higher-level thread listing, reply creation, comment editing, moderation status change, deletion, sentiment analysis, ranking, summarization, enrichment, automated response generation, or heuristic interpretation.
- **FR-020**: The `commentThreads_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, request validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `commentThreads_insert` tool MUST rely on the existing Layer 1 `commentThreads.insert` capability from YT-122 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one authorized top-level thread creation request, one missing-OAuth failure, one missing-part failure, one missing-target-context failure, one missing-top-level-comment-content failure, one invalid-target-context failure, one unsupported reply creation shape, one unsupported option failure, one disabled-comment target failure, and one access-sensitive upstream failure.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand OAuth, quota, part-selection, target-context, and top-level-comment-content requirements, interpret created-thread results, and handle failures for `commentThreads_insert` without consulting implementation-only artifacts.

### Key Entities

- **Comment Threads Insert Tool**: The public Layer 2 MCP tool named `commentThreads_insert`, representing one low-level endpoint-backed top-level comment-thread creation operation.
- **Comment Thread Create Request**: The request shape that combines required part selection, target video context, top-level comment body, and any supported optional write context for one create attempt.
- **Part Selection**: The caller-selected comment-thread resource sections that determine which created-thread properties are returned.
- **Target Video Context**: The caller-provided video context where the top-level comment thread will be created.
- **Top-Level Comment Body**: The caller-provided comment-thread content that identifies the target context and the text content to publish as a new top-level comment.
- **Write Authorization Context**: The caller's eligible OAuth-backed permission state that determines whether top-level comment-thread creation is allowed.
- **Created Comment Thread Result**: The returned comment-thread resource fields and operation context produced by a successful `commentThreads_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `commentThreads_insert` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that top-level comment-thread creation requires eligible OAuth authorization and is not available through API-key-only access.
- **Top-Level Creation Boundary Disclosure**: The caller-facing explanation that this tool creates top-level comment threads and excludes reply creation, listing, moderation, updates, deletion, and higher-level discussion workflows.

### Assumptions

- YT-122 provides the Layer 1 `commentThreads.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, request validation, error, example, and validation standards this feature must follow.
- `commentThreads_insert` is a low-level endpoint-backed tool for direct top-level comment-thread creation, debugging, and power-user workflows; higher-level thread listing, reply creation, moderation, editing, deletion, ranking, sentiment analysis, summarization, analytics, or automated response workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation and existing project inventory are the default sources for `commentThreads.insert` quota cost, OAuth behavior, part-selection rules, top-level comment body requirements, target video behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized top-level thread creation, missing authorization, missing part selection, missing target video context, missing top-level comment content, invalid or inaccessible targets, disabled-comment targets, unsupported create shapes, unsupported options, access-sensitive failures, and created-thread results is sufficient for this slice.

### Dependencies

- `YT-122` Layer 1 `commentThreads.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `commentThreads_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `commentThreads.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `commentThreads_insert` requires eligible OAuth authorization and cannot be used with API-key-only access by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, target video context, top-level comment-content requirements, and top-level-only creation boundary in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `commentThreads_insert`, identify the OAuth requirement, prepare a valid top-level comment-thread body, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `commentThreads_insert` requests return created-thread results with selected part context, relevant authorization context, target context, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid create requests that omit OAuth, omit part selection, omit target video context, omit top-level comment content, use invalid target identifiers, use unsupported fields, or request unsupported create shapes are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative target access, disabled-comment, missing-resource, quota, authorization, and unexpected upstream failures are distinguishable from successful thread creation and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `commentThreads_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, request validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `commentThreads_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
