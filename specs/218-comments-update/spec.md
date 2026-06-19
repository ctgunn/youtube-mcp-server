# Feature Specification: Layer 2 Tool `comments_update`

**Feature Branch**: `218-comments-update`  
**Created**: 2026-06-18  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-218, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Existing Comments Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `comments_update` tool to edit an existing YouTube comment while staying close to the upstream `comments.update` write behavior and returned comment resource.

**Why this priority**: This is the core value of YT-218. Layer 2 must expose endpoint-backed comment editing for direct update workflows, debugging, and later composition without turning the tool into a higher-level moderation, conversation management, deletion, sentiment, ranking, or automated rewriting workflow.

**Independent Test**: Can be tested by invoking `comments_update` with eligible authorization, supported part selection, and a valid update body for an editable comment, then confirming the caller receives the updated comment resource in a near-raw endpoint-backed shape with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization and provides a valid update body for an editable comment, **When** they call `comments_update` with supported part selection, **Then** the result includes the updated comment and preserves the requested operation context.
2. **Given** a caller provides all required comment-edit inputs and supported optional update context, **When** the update succeeds, **Then** the result preserves the returned comment fields without adding unrelated thread, channel, video, moderation, deletion, or analysis data.
3. **Given** the upstream update succeeds but returns only the updated comment resource rather than a collection, **When** the caller inspects the result, **Then** the single-resource mutation outcome is clear and is not presented as a list, thread traversal, moderation workflow, or higher-level conversation workflow.
4. **Given** a caller wants direct access to comment edit behavior, **When** they use `comments_update`, **Then** the tool performs only the comment update operation and is not presented as reply creation, moderation status changes, deletion, ranking, summarization, enrichment, or automated response generation.

---

### User Story 2 - Understand Cost, OAuth, and Writable Fields Before Calling (Priority: P2)

As a client developer, I can inspect `comments_update` before invoking it and immediately understand that it maps to `comments.update`, costs 50 official quota units per call, requires eligible OAuth authorization, and only supports documented writable comment fields.

**Why this priority**: Comment editing is quota-bearing, permission-sensitive, and can visibly change published content. Callers need quota, OAuth, part-selection, update-body, writable-field, read-only-field, and replacement-boundary visibility in discovery, descriptions, and examples before they spend quota or revise a comment.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required part selection, supported writable fields, read-only field boundaries, and unsupported update shapes are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `comments_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported comment-edit boundary.
2. **Given** an example request is shown for `comments_update`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a valid update body are visible alongside the request shape.
3. **Given** a caller needs to revise comment text, **When** they inspect the tool contract, **Then** the required relationship between selected part, comment identifier, writable text field, and returned updated-comment fields is clear before invocation.
4. **Given** a caller wants to change read-only comment metadata, parent relationships, moderation state, deletion state, or another unsupported update target, **When** they inspect the tool contract, **Then** the boundary of `comments_update` is clear before invocation.

---

### User Story 3 - Reject Unsupported Comment Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `comments_update` request lacks eligible OAuth authorization, omits required update fields, attempts to change read-only fields, targets an ineligible comment, or includes unsupported write options, so I can correct the request without guessing which comment-edit rule was violated.

**Why this priority**: `comments.update` combines write authorization, part selection, comment identity, writable-field limits, and upstream edit failures. Clear validation protects callers from ambiguous mutation failures while keeping the tool faithful to the endpoint instead of inventing fallback repair, moderation, deletion, or rewrite behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing part selection, missing comment identifier, missing updated text, empty updated text, unsupported part selections, read-only field updates, unsupported optional parameters, inaccessible comments, and upstream write failures, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `comments_update`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a comment-format failure.
2. **Given** a caller omits the required comment identifier or updated text field, **When** they call `comments_update`, **Then** the request is rejected with guidance that both the target comment and writable text are required.
3. **Given** a caller attempts to update read-only fields or unsupported writable parts, **When** they call `comments_update`, **Then** the request is rejected with guidance that the requested change is outside the endpoint-backed update boundary.
4. **Given** a caller targets a missing, private, deleted, locked, or otherwise ineligible comment, **When** they call `comments_update`, **Then** the response preserves the appropriate access, missing-resource, or upstream failure meaning using the shared Layer 2 conventions.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported update attempt.
- The caller provides unsupported, empty, duplicate, or conflicting part selections; the response must identify the supported writable part rule.
- The caller provides no eligible OAuth authorization or lacks permission to edit the targeted comment; the response must distinguish access failure from malformed update content.
- The caller omits the comment identifier, provides an empty identifier, or provides a malformed comment identifier; the response must identify the target-comment rule.
- The caller provides updated comment text that is missing, empty after validation, too long, malformed, or otherwise unpublishable; the response must identify the updated-text rule.
- The caller includes read-only fields, immutable parent relationships, moderation instructions, deletion instructions, insert-only fields, listing/search fields, derived metrics, ranking instructions, summarization instructions, or unsupported optional parameters; the request must be rejected or clearly flagged as outside the endpoint contract.
- The caller targets a comment that is missing, deleted, held for review, private, locked, unavailable, disabled for editing, or inaccessible to the selected authorization context; the response must preserve the appropriate access, missing-resource, or upstream failure meaning.
- The upstream success response omits optional fields or returns partial comment resources according to the selected parts; the result must preserve returned fields without fabricating missing comment data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects comment listing, reply creation, moderation status changes, deletion, sentiment analysis, ranking, summarization, enrichment, automated rewriting, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `comments_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `comments.update` identity, official quota-unit cost of `50`, OAuth-required auth mode, required part selection, writable-field boundary, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required part selection, required comment identifier, required updated text, unsupported writable parts, read-only field rejection, unsupported body fields, unsupported optional parameters, invalid comment identifiers, empty updated text, and access-sensitive failures.
- **Red**: Add failing result-contract checks proving that updated comment resource fields, selected part context, mutation outcome details, relevant authorization context, writable-field context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `comments_update` tool contract and behavior needed for callers to make supported low-level `comments.update` edit requests and receive near-raw updated comment results.
- **Green**: Include representative examples for authorized comment update, missing OAuth authorization, missing part selection, missing comment identifier, missing updated text, unsupported writable part, read-only field validation failure, unsupported option validation failure, inaccessible target comment, and access-sensitive upstream failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `comments_update` request, response, quota, auth, part-selection, writable-field, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for update-body, part-selection, authorization, comment-identifier, writable-field, read-only-field, and unsupported-option validation, integration-style checks for representative successful and failed comment update paths, and documentation checks for quota/auth/writable-field/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `comments_update` responsibility, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, writable-field boundary, mutation result, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-218`, the dependency assumptions from YT-118/YT-201/YT-202, focused `comments_update` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `comments_update`.
- **FR-002**: The `comments_update` tool definition MUST identify its mapped upstream operation as YouTube resource `comments` and method `update`.
- **FR-003**: The `comments_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `comments_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `comments_update` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present comment editing as an API-key-only capability.
- **FR-006**: The `comments_update` input contract MUST preserve the upstream concepts of required part selection, target comment identity, update body, writable text field, and supported optional update context where those concepts are supported.
- **FR-007**: The `comments_update` input contract MUST require supported part selection for each update request and MUST document that part selection determines which updated-comment properties are returned.
- **FR-008**: The `comments_update` input contract MUST document that the supported writable part for this slice is the comment `snippet` content and MUST reject unsupported writable parts.
- **FR-009**: The `comments_update` input contract MUST require an update body that identifies the existing comment being edited and provides the revised comment text.
- **FR-010**: The `comments_update` tool MUST support valid authorized comment-edit requests when the caller's OAuth authorization is sufficient for the target comment.
- **FR-011**: The `comments_update` tool MUST reject requests that require OAuth access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-012**: The `comments_update` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-013**: The `comments_update` tool MUST reject missing, empty, malformed, or inaccessible target comment identifiers with clear caller-facing validation feedback or upstream failure categorization.
- **FR-014**: The `comments_update` tool MUST reject missing, empty, malformed, unsupported, or unpublishable updated comment text with clear caller-facing validation feedback.
- **FR-015**: The `comments_update` tool MUST reject unsupported body fields, read-only fields, immutable parent relationships, unsupported optional parameters, insert-only fields, listing fields, moderation fields, deletion fields, search instructions, automated rewriting instructions, and unsupported update shapes with clear caller-facing validation feedback.
- **FR-016**: The `comments_update` result MUST preserve updated comment resource fields, selected part context, mutation outcome details, relevant authorization context, writable-field context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-017**: The `comments_update` tool MUST distinguish successful updated-comment outcomes from validation failures, authorization failures, missing or inaccessible target comments, immutable-field violations, quota failures, disabled-comment failures, unavailable resources, and unexpected upstream failures.
- **FR-018**: The `comments_update` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `comments_update` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, supported scopes or equivalent access expectations, required part selection, target comment identity, writable text requirements, read-only field boundaries, unsupported update shapes, availability state, and access-sensitive behavior.
- **FR-020**: The `comments_update` contract MUST remain close to the upstream `comments.update` endpoint and MUST NOT add higher-level comment listing, reply creation, moderation status change, deletion, sentiment analysis, ranking, summarization, enrichment, automated rewriting, or heuristic interpretation.
- **FR-021**: The `comments_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, request validation, error, and example standards established by YT-201 and YT-202.
- **FR-022**: The `comments_update` tool MUST rely on the existing Layer 1 `comments.update` capability from YT-118 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one authorized comment update request, one missing-OAuth failure, one missing-part failure, one missing-comment-identifier failure, one missing-updated-text failure, one unsupported writable-part failure, one read-only-field failure, one unsupported option failure, and one access-sensitive upstream failure.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand OAuth, quota, part-selection, target-comment, writable-field, and updated-text requirements, interpret updated-comment results, and handle failures for `comments_update` without consulting implementation-only artifacts.

### Key Entities

- **Comments Update Tool**: The public Layer 2 MCP tool named `comments_update`, representing one low-level endpoint-backed comment edit operation.
- **Comment Update Request**: The request shape that combines required part selection, target comment identity, update body, writable revised text, and any supported optional update context for one edit attempt.
- **Part Selection**: The caller-selected comment resource section that determines which updated-comment properties are returned.
- **Target Comment Identifier**: The caller-provided identifier for the existing comment that will be edited.
- **Writable Field Policy**: The caller-facing rules that distinguish the supported writable comment text field from read-only fields, immutable relationships, unsupported writable parts, and unrelated operations.
- **Updated Comment Text**: The caller-provided revised comment content to apply to the targeted comment.
- **Write Authorization Context**: The caller's eligible OAuth-backed permission state that determines whether comment editing is allowed.
- **Updated Comment Result**: The returned comment resource fields and operation context produced by a successful `comments_update` call.
- **Quota Disclosure**: The caller-facing statement that each `comments_update` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that comment editing requires eligible OAuth authorization and is not available through API-key-only access.
- **Update Boundary Disclosure**: The caller-facing explanation that this tool edits supported fields on an existing comment and excludes listing, insertion, moderation, deletion, and higher-level analysis behavior.

### Assumptions

- YT-118 provides the Layer 1 `comments.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, request validation, error, example, and validation standards this feature must follow.
- `comments_update` is a low-level endpoint-backed tool for direct comment editing, debugging, and power-user workflows; higher-level comment listing, reply creation, moderation, deletion, ranking, sentiment analysis, summarization, analytics, enrichment, or automated rewriting workflows belong to separate endpoint or Layer 3 features.
- The supported update behavior for this slice centers on revising existing comment text while clearly rejecting attempts to edit fields outside the documented writable boundary.
- The official YouTube Data API documentation and existing project inventory are the default sources for `comments.update` quota cost, OAuth behavior, part-selection rules, writable field rules, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized comment update, missing authorization, missing part selection, missing target comment identifier, missing updated text, unsupported writable parts, read-only field attempts, unsupported options, access-sensitive failures, and updated-comment results is sufficient for this slice.

### Dependencies

- `YT-118` Layer 1 `comments.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `comments.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `comments_update` requires eligible OAuth authorization and cannot be used with API-key-only access by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, target comment identifier, updated text requirement, supported writable field boundary, and unsupported update shapes in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `comments_update`, identify the OAuth requirement, prepare a valid update body, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `comments_update` requests return updated-comment results with selected part context, relevant authorization context, writable-field context, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid update requests that omit OAuth, omit part selection, omit target comment identity, omit updated text, use unsupported writable parts, attempt read-only field changes, or include unsupported options are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative target-comment access, missing-resource, disabled-comment, immutable-field, quota, authorization, and unexpected upstream failures are distinguishable from successful comment updates and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `comments_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, request validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `comments_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
