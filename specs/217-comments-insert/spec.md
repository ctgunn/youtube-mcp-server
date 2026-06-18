# Feature Specification: Layer 2 Tool `comments_insert`

**Feature Branch**: `217-comments-insert`  
**Created**: 2026-06-17  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-217, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Reply Comments Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `comments_insert` tool to create a reply to an existing YouTube comment while staying close to the upstream `comments.insert` write behavior and returned comment resource.

**Why this priority**: This is the core value of YT-217. Layer 2 must expose endpoint-backed reply creation for direct comment workflows, debugging, and later composition without turning the tool into a higher-level moderation, conversation management, sentiment, ranking, or automated response workflow.

**Independent Test**: Can be tested by invoking `comments_insert` with eligible authorization, supported part selection, and a valid reply body that references a parent comment, then confirming the caller receives the created comment resource in a near-raw endpoint-backed shape with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization and provides a valid reply body for an existing parent comment, **When** they call `comments_insert` with supported part selection, **Then** the result includes the created reply comment and preserves the requested operation context.
2. **Given** a caller provides all required reply-creation inputs and supported optional write context, **When** the reply is created, **Then** the result preserves the returned comment fields without adding unrelated thread, channel, video, moderation, or analysis data.
3. **Given** the upstream creation succeeds but returns only the created comment resource rather than a collection, **When** the caller inspects the result, **Then** the single-resource mutation outcome is clear and is not presented as a list, comment-thread traversal, or higher-level conversation workflow.
4. **Given** a caller wants direct access to comment reply creation behavior, **When** they use `comments_insert`, **Then** the tool performs only the reply creation operation and is not presented as top-level discussion creation, comment editing, moderation status changes, deletion, ranking, summarization, or enrichment.

---

### User Story 2 - Understand Cost, OAuth, and Reply Rules Before Calling (Priority: P2)

As a client developer, I can inspect `comments_insert` before invoking it and immediately understand that it maps to `comments.insert`, costs 50 official quota units per call, requires eligible OAuth authorization, and supports reply creation to an existing parent comment.

**Why this priority**: Comment creation is quota-bearing, permission-sensitive, and publicly visible. Callers need quota, OAuth, part-selection, reply-body, parent-comment, and write-boundary visibility in discovery, descriptions, and examples before they spend quota or publish a reply.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required part selection, required reply body, parent-comment requirement, and unsupported create shapes are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `comments_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported reply-creation boundary.
2. **Given** an example request is shown for `comments_insert`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a valid parent-comment reply body are visible alongside the request shape.
3. **Given** a caller needs to publish a reply under a specific parent comment, **When** they inspect the tool contract, **Then** the required relationship between parent-comment reference, reply text, selected response parts, and returned created-comment fields is clear before invocation.
4. **Given** a caller wants to create a top-level comment thread or perform another unsupported comment write shape, **When** they inspect the tool contract, **Then** the boundary of `comments_insert` is clear before invocation.

---

### User Story 3 - Reject Unsupported Reply Creation Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `comments_insert` request lacks eligible OAuth authorization, omits required reply fields, references an invalid parent comment, or includes unsupported write options, so I can correct the request without guessing which comment-create rule was violated.

**Why this priority**: `comments.insert` combines write authorization, part selection, parent-comment targeting, body validation, and upstream write failures. Clear validation protects callers from ambiguous publish failures while keeping the tool faithful to the endpoint instead of inventing fallback comment repair or moderation behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing part selection, missing parent-comment reference, empty reply text, unsupported top-level create shapes, unsupported fields, and inaccessible parent comments, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `comments_insert`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a comment-format failure.
2. **Given** a caller omits the required parent-comment reference, **When** they call `comments_insert`, **Then** the request is rejected with guidance that reply creation requires a parent comment.
3. **Given** a caller omits reply text or provides reply text that is empty after validation, **When** they call `comments_insert`, **Then** the request is rejected with guidance that publishable reply content is required.
4. **Given** a caller includes top-level comment-thread creation fields, moderation instructions, update fields, deletion instructions, or unsupported optional parameters, **When** they call `comments_insert`, **Then** the request is rejected or clearly flagged as outside the endpoint-backed tool contract.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported create attempt.
- The caller has no eligible OAuth authorization or lacks permission to reply in the target context; the response must distinguish access failure from malformed reply content.
- The caller omits the parent-comment reference, provides an empty parent-comment reference, or references a malformed parent-comment identifier; the response must identify the parent-comment rule.
- The caller provides reply text that is missing, empty after validation, too long, malformed, or otherwise unpublishable; the response must identify the reply-content rule.
- The caller references a parent comment that is missing, deleted, held for review, private, disabled for replies, locked, unavailable, or inaccessible to the selected authorization context; the response must preserve the appropriate access, missing-resource, or upstream failure meaning.
- The caller supplies unsupported part names, unsupported body fields, read-only fields, unsupported optional parameters, top-level thread creation fields, update fields, moderation fields, deletion fields, search instructions, or automated reply instructions; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream success response omits optional fields or returns partial comment resources according to the selected parts; the result must preserve returned fields without fabricating missing comment data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects comment listing, top-level thread creation, comment editing, moderation status changes, deletion, sentiment analysis, ranking, summarization, enrichment, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `comments_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `comments.insert` identity, official quota-unit cost of `50`, OAuth-required auth mode, required part selection, reply-creation boundary, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required part selection, required parent-comment reference, required reply content, unsupported top-level create shapes, unsupported body fields, unsupported optional parameters, invalid parent-comment identifiers, and access-sensitive failures.
- **Red**: Add failing result-contract checks proving that created comment resource fields, selected part context, mutation outcome details, relevant authorization context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `comments_insert` tool contract and behavior needed for callers to make supported low-level `comments.insert` reply-creation requests and receive near-raw created comment results.
- **Green**: Include representative examples for authorized reply creation, missing OAuth authorization, missing part selection, missing parent-comment reference, missing reply content, invalid parent-comment target, unsupported top-level create shape, unsupported option validation failure, and access-sensitive upstream failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `comments_insert` request, response, quota, auth, part-selection, reply-body, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for reply-body, part-selection, authorization, parent-comment, and unsupported-field validation, integration-style checks for representative successful and failed reply-creation paths, and documentation checks for quota/auth/reply-rule/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `comments_insert` responsibility, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, parent-comment rule, reply-content rule, mutation result, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-217`, the dependency assumptions from YT-117/YT-201/YT-202, focused `comments_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `comments_insert`.
- **FR-002**: The `comments_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `comments` and method `insert`.
- **FR-003**: The `comments_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `comments_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `comments_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present comment creation as an API-key-only capability.
- **FR-006**: The `comments_insert` input contract MUST preserve the upstream concepts of required part selection, comment reply body, parent-comment reference, and supported optional write context where those concepts are supported.
- **FR-007**: The `comments_insert` input contract MUST require supported part selection for each create request and MUST document that part selection determines which created-comment properties are returned.
- **FR-008**: The `comments_insert` input contract MUST require a reply body that identifies the parent comment being answered and the reply content to publish.
- **FR-009**: The `comments_insert` tool MUST support valid authorized reply-creation requests when the caller's OAuth authorization is sufficient for the parent-comment context.
- **FR-010**: The `comments_insert` tool MUST reject requests that require OAuth access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-011**: The `comments_insert` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-012**: The `comments_insert` tool MUST reject missing, empty, malformed, or inaccessible parent-comment references with clear caller-facing validation feedback or upstream failure categorization.
- **FR-013**: The `comments_insert` tool MUST reject missing, empty, malformed, unsupported, or unpublishable reply content with clear caller-facing validation feedback.
- **FR-014**: The `comments_insert` tool MUST reject unsupported body fields, read-only fields, unsupported optional parameters, top-level comment-thread creation fields, update fields, moderation fields, deletion fields, search instructions, automated response instructions, and unsupported create shapes with clear caller-facing validation feedback.
- **FR-015**: The `comments_insert` result MUST preserve created comment resource fields, selected part context, mutation outcome details, relevant authorization context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-016**: The `comments_insert` tool MUST distinguish successful created-comment outcomes from validation failures, authorization failures, missing or inaccessible parent comments, quota failures, disabled-comment failures, unavailable resources, and unexpected upstream failures.
- **FR-017**: The `comments_insert` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `comments_insert` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, supported scopes or equivalent access expectations, required part selection, required parent-comment reference, reply-content requirements, unsupported create shapes, availability state, and access-sensitive behavior.
- **FR-019**: The `comments_insert` contract MUST remain close to the upstream `comments.insert` endpoint and MUST NOT add higher-level comment listing, top-level thread creation, comment editing, moderation status change, deletion, sentiment analysis, ranking, summarization, enrichment, automated response generation, or heuristic interpretation.
- **FR-020**: The `comments_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, request validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `comments_insert` tool MUST rely on the existing Layer 1 `comments.insert` capability from YT-117 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one authorized reply-creation request, one missing-OAuth failure, one missing-part failure, one missing-parent-comment failure, one missing-reply-content failure, one invalid-parent-comment failure, one unsupported top-level create shape, one unsupported option failure, and one access-sensitive upstream failure.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand OAuth, quota, part-selection, parent-comment, and reply-content requirements, interpret created-comment results, and handle failures for `comments_insert` without consulting implementation-only artifacts.

### Key Entities

- **Comments Insert Tool**: The public Layer 2 MCP tool named `comments_insert`, representing one low-level endpoint-backed comment reply creation operation.
- **Comment Reply Create Request**: The request shape that combines required part selection, a reply body, parent-comment reference, and any supported optional write context for one create attempt.
- **Part Selection**: The caller-selected comment resource sections that determine which created-comment properties are returned.
- **Reply Body**: The caller-provided comment resource content that identifies the parent comment being answered and the text content to publish.
- **Parent Comment Reference**: The caller-provided identifier for the existing comment that will receive the reply.
- **Write Authorization Context**: The caller's eligible OAuth-backed permission state that determines whether reply creation is allowed.
- **Created Comment Result**: The returned comment resource fields and operation context produced by a successful `comments_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `comments_insert` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that comment reply creation requires eligible OAuth authorization and is not available through API-key-only access.
- **Reply-Creation Boundary Disclosure**: The caller-facing explanation that this tool creates replies to existing comments and excludes top-level thread creation and other comment-management operations.

### Assumptions

- YT-117 provides the Layer 1 `comments.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, request validation, error, example, and validation standards this feature must follow.
- `comments_insert` is a low-level endpoint-backed tool for direct reply creation, debugging, and power-user workflows; higher-level comment listing, top-level thread creation, moderation, editing, deletion, ranking, sentiment analysis, summarization, analytics, or automated response workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation and existing project inventory are the default sources for `comments.insert` quota cost, OAuth behavior, part-selection rules, reply body requirements, parent-comment behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized reply creation, missing authorization, missing part selection, missing parent-comment reference, missing reply content, invalid or inaccessible parent comments, unsupported create shapes, unsupported options, access-sensitive failures, and created-comment results is sufficient for this slice.

### Dependencies

- `YT-117` Layer 1 `comments.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `comments.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `comments_insert` requires eligible OAuth authorization and cannot be used with API-key-only access by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, parent-comment reference, reply-content requirements, and reply-only creation boundary in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `comments_insert`, identify the OAuth requirement, prepare a valid reply body, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `comments_insert` requests return created-comment results with selected part context, relevant authorization context, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid create requests that omit OAuth, omit part selection, omit parent-comment reference, omit reply content, use invalid parent-comment identifiers, use unsupported fields, or request unsupported create shapes are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative parent-comment access, missing-resource, disabled-comment, quota, authorization, and unexpected upstream failures are distinguishable from successful reply creation and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `comments_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, request validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `comments_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
