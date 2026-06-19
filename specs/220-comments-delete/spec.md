# Feature Specification: Layer 2 Tool `comments_delete`

**Feature Branch**: `220-comments-delete`  
**Created**: 2026-06-19  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-220, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Existing Comments Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `comments_delete` tool to delete an existing YouTube comment while staying close to the upstream `comments.delete` write behavior and receiving a clear deletion acknowledgment.

**Why this priority**: This is the core value of YT-220. Layer 2 must expose endpoint-backed comment deletion for direct cleanup, moderation support, debugging, and later composition without turning the tool into comment listing, reply creation, comment editing, moderation-state changes, sentiment, ranking, summarization, or automated review workflow.

**Independent Test**: Can be tested by invoking `comments_delete` with eligible authorization and a valid deletable comment identifier, then confirming the caller receives a clear deletion mutation result with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization and provides a valid deletable comment identifier, **When** they call `comments_delete`, **Then** the result confirms the deletion request succeeded and preserves the operation context.
2. **Given** the upstream deletion succeeds with an acknowledgment-style result rather than a comment resource, **When** the caller inspects the result, **Then** the single deletion mutation outcome is clear and is not presented as listing, update, moderation, or higher-level conversation output.
3. **Given** a caller provides supported optional write context that is valid for deleting a comment, **When** the deletion request succeeds, **Then** the result preserves that context without adding unrelated thread, channel, video, update, moderation, or analysis data.
4. **Given** a caller wants direct access to comment deletion behavior, **When** they use `comments_delete`, **Then** the tool performs only the deletion operation and is not presented as comment discovery, reply creation, comment editing, moderation status change, ranking, summarization, enrichment, or automated review.

---

### User Story 2 - Understand Cost and OAuth Before Deleting (Priority: P2)

As a client developer, I can inspect `comments_delete` before invoking it and immediately understand that it maps to `comments.delete`, costs 50 official quota units per call, requires eligible OAuth authorization, and permanently removes the targeted comment when the caller is allowed to delete it.

**Why this priority**: Comment deletion is quota-bearing, permission-sensitive, and destructive. Callers need quota, OAuth, target-comment, deletion acknowledgment, access boundary, and unsupported-operation visibility in discovery, descriptions, and examples before they spend quota or remove content.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, target-comment requirement, deletion result behavior, and unsupported operation shapes are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `comments_delete`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported deletion boundary.
2. **Given** an example request is shown for `comments_delete`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a valid target comment are visible alongside the request shape.
3. **Given** a caller needs to delete a comment, **When** they inspect the tool contract, **Then** the required relationship between the target comment identifier, authorization context, destructive deletion behavior, and acknowledgment result is clear before invocation.
4. **Given** a caller wants listing, editing, moderation-state change, comment-thread traversal, soft-delete recovery, or automated moderation advice, **When** they inspect the tool contract, **Then** the boundary of `comments_delete` is clear before invocation.

---

### User Story 3 - Reject Unsupported Comment Delete Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `comments_delete` request lacks eligible OAuth authorization, omits the target comment, targets an ineligible comment, or includes unsupported deletion options, so I can correct the request without guessing which deletion rule was violated.

**Why this priority**: `comments.delete` combines write authorization, target-comment identity, destructive mutation semantics, and upstream deletion failures. Clear validation protects callers from ambiguous mutation failures while keeping the tool faithful to the endpoint instead of inventing fallback listing, moderation, update, or recovery behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing comment identifier, empty or malformed identifier, unsupported optional parameters, deletion of inaccessible comments, deletion of already deleted comments, and upstream write failures, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `comments_delete`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a comment-identifier failure.
2. **Given** a caller omits the required comment identifier or provides an empty identifier, **When** they call `comments_delete`, **Then** the request is rejected with guidance that one valid target comment is required.
3. **Given** a caller includes unsupported delete options, listing filters, update fields, moderation instructions, or recovery instructions, **When** they call `comments_delete`, **Then** the request is rejected with guidance that the requested shape is outside the endpoint-backed deletion boundary.
4. **Given** a caller targets a missing, private, already deleted, locked, or otherwise ineligible comment, **When** they call `comments_delete`, **Then** the response preserves the appropriate access, missing-resource, deletion-state, or upstream failure meaning using the shared Layer 2 conventions.

### Edge Cases

- The caller omits the required comment identifier; the request must be rejected before it is treated as a supported deletion attempt.
- The caller provides an empty, malformed, duplicate, conflicting, or multi-target identifier shape when the contract supports a single target comment per deletion request; the response must identify the target-comment rule.
- The caller has no eligible OAuth authorization or lacks permission to delete the targeted comment; the response must distinguish access failure from malformed deletion input.
- The caller targets a comment that is missing, already deleted, private, locked, unavailable, disabled for deletion, or inaccessible to the selected authorization context; the response must preserve the appropriate access, missing-resource, deletion-state, or upstream failure meaning.
- The caller includes read-only fields, update body fields, listing filters, moderation status changes, reply-creation fields, recovery instructions, ranking instructions, summarization instructions, or unsupported optional parameters; the request must be rejected or clearly flagged as outside the endpoint contract.
- The upstream success response returns no comment resource or only acknowledgment-style content; the result must preserve the deletion outcome without fabricating deleted comment data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects comment listing, reply creation, comment editing, moderation status changes, deletion recovery, sentiment analysis, ranking, summarization, enrichment, automated moderation advice, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `comments_delete` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `comments.delete` identity, official quota-unit cost of `50`, OAuth-required auth mode, target-comment requirement, deletion acknowledgment behavior, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required target comment identifier, empty or malformed identifiers, duplicate or conflicting target shapes, unsupported optional parameters, unsupported operation fields, unsupported recovery instructions, and access-sensitive failures.
- **Red**: Add failing result-contract checks proving that deletion outcome, target context, mutation acknowledgment, relevant authorization context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `comments_delete` tool contract and behavior needed for callers to make supported low-level `comments.delete` deletion requests and receive clear deletion mutation results.
- **Green**: Include representative examples for authorized deletion, missing OAuth authorization, missing comment identifier, empty or malformed identifier, duplicate or conflicting target shape, unsupported option validation failure, inaccessible target comment, already deleted target comment, and access-sensitive upstream failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `comments_delete` request, response, quota, auth, target-comment, deletion acknowledgment, caveat, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for authorization, target-comment, duplicate-target, unsupported-option, unsupported-operation, and deletion acknowledgment validation, integration-style checks for representative successful and failed comment deletion paths, and documentation checks for quota/auth/deletion/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `comments_delete` responsibility, inputs, outputs, quota cost, OAuth behavior, target-comment behavior, deletion acknowledgment result, destructive behavior, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-220`, the dependency assumptions from YT-120/YT-201/YT-202, focused `comments_delete` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `comments_delete`.
- **FR-002**: The `comments_delete` tool definition MUST identify its mapped upstream operation as YouTube resource `comments` and method `delete`.
- **FR-003**: The `comments_delete` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `comments_delete` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `comments_delete` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present comment deletion as an API-key-only capability.
- **FR-006**: The `comments_delete` input contract MUST preserve the upstream concepts of target comment identity, eligible write authorization, destructive deletion intent, and supported optional write context where those concepts are supported.
- **FR-007**: The `comments_delete` input contract MUST require exactly one valid target comment identifier for each deletion request unless the shared Layer 2 contract explicitly defines a supported single-call multi-target pattern for this endpoint.
- **FR-008**: The `comments_delete` input contract MUST document that successful deletion is an acknowledgment-style mutation result and MUST NOT promise a returned deleted-comment resource.
- **FR-009**: The `comments_delete` tool MUST support valid authorized deletion requests when the caller's OAuth authorization is sufficient for the targeted comment.
- **FR-010**: The `comments_delete` tool MUST reject requests that require OAuth access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-011**: The `comments_delete` tool MUST reject missing, empty, malformed, duplicate, conflicting, unsupported, or inaccessible target comment identifiers with clear caller-facing validation feedback or upstream failure categorization.
- **FR-012**: The `comments_delete` tool MUST reject unsupported optional parameters, read-only fields, update body fields, listing filters, moderation fields, reply-creation fields, recovery instructions, search instructions, automated moderation advice, ranking instructions, summarization instructions, and unsupported deletion shapes with clear caller-facing validation feedback.
- **FR-013**: The `comments_delete` result MUST preserve target comment context, deletion outcome details, relevant authorization context, mutation acknowledgment, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-014**: The `comments_delete` tool MUST distinguish successful deletion outcomes from validation failures, authorization failures, missing or inaccessible target comments, already deleted targets, quota failures, disabled-comment failures, unavailable resources, and unexpected upstream failures.
- **FR-015**: The `comments_delete` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-016**: The `comments_delete` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, supported scopes or equivalent access expectations, target comment requirements, destructive deletion behavior, acknowledgment-style result behavior, unsupported deletion shapes, availability state, and access-sensitive behavior.
- **FR-017**: The `comments_delete` contract MUST remain close to the upstream `comments.delete` endpoint and MUST NOT add higher-level comment listing, reply creation, comment editing, moderation status change, deletion recovery, sentiment analysis, ranking, summarization, enrichment, automated moderation recommendation, or heuristic interpretation.
- **FR-018**: The `comments_delete` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, request validation, error, and example standards established by YT-201 and YT-202.
- **FR-019**: The `comments_delete` tool MUST rely on the existing Layer 1 `comments.delete` capability from YT-120 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-020**: The feature MUST include caller-facing examples for at least one authorized deletion request, one missing-OAuth failure, one missing-target failure, one empty or malformed target failure, one duplicate or conflicting target failure, one unsupported option failure, one inaccessible-target failure, one already-deleted target failure, and one access-sensitive upstream failure.
- **FR-021**: The feature MUST include validation evidence that clients can discover, call, understand OAuth, quota, target-comment, destructive deletion, and acknowledgment-result requirements, interpret deletion mutation results, and handle failures for `comments_delete` without consulting implementation-only artifacts.

### Key Entities

- **Comments Delete Tool**: The public Layer 2 MCP tool named `comments_delete`, representing one low-level endpoint-backed comment deletion operation.
- **Comment Delete Request**: The request shape that combines target comment identity, destructive deletion intent, eligible write authorization context, and any supported optional write context for one deletion attempt.
- **Target Comment Identifier**: The caller-provided identifier for the existing comment that will be deleted.
- **Deletion Boundary Policy**: The caller-facing rules that distinguish supported comment deletion from unsupported listing, editing, moderation, recovery, analysis, or multi-operation request shapes.
- **Write Authorization Context**: The caller's eligible OAuth-backed permission state that determines whether comment deletion is allowed.
- **Deletion Mutation Result**: The returned deletion acknowledgment, target context, authorization context, outcome details, and operation metadata produced by a successful `comments_delete` call.
- **Quota Disclosure**: The caller-facing statement that each `comments_delete` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that comment deletion requires eligible OAuth authorization and is not available through API-key-only access.
- **Deletion Boundary Disclosure**: The caller-facing explanation that this tool deletes an existing comment and excludes listing, insertion, editing, moderation, recovery, and higher-level analysis behavior.

### Assumptions

- YT-120 provides the Layer 1 `comments.delete` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, request validation, error, example, and validation standards this feature must follow.
- `comments_delete` is a low-level endpoint-backed tool for direct comment deletion, debugging, and power-user workflows; higher-level comment listing, reply creation, editing, moderation, recovery, ranking, sentiment analysis, summarization, analytics, enrichment, or automated review workflows belong to separate endpoint or Layer 3 features.
- The supported deletion behavior for this slice centers on deleting one target comment per request and returning an acknowledgment-style mutation result rather than a deleted comment resource.
- The official YouTube Data API documentation and existing project inventory are the default sources for `comments.delete` quota cost, OAuth behavior, target-comment rules, availability state, destructive deletion caveats, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized deletion, missing authorization, missing or malformed target comment identifier, duplicate or conflicting target shapes, unsupported options, inaccessible targets, already deleted targets, access-sensitive failures, and deletion acknowledgment results is sufficient for this slice.

### Dependencies

- `YT-120` Layer 1 `comments.delete` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments_delete` discovery metadata, descriptions, and examples produced by this feature display the mapped `comments.delete` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `comments_delete` requires eligible OAuth authorization and cannot be used with API-key-only access by reading the tool contract alone.
- **SC-003**: A client developer can identify the target-comment requirement, destructive deletion behavior, acknowledgment-style result behavior, and unsupported deletion shapes in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `comments_delete`, identify the OAuth requirement, prepare a valid deletion request, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `comments_delete` requests return deletion mutation results with target context, relevant authorization context, deletion outcome details, mutation acknowledgment, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid deletion requests that omit OAuth, omit target identity, use malformed target identity, provide duplicate or conflicting target shapes, or include unsupported options are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative target-comment access, missing-resource, already-deleted, disabled-comment, quota, authorization, and unexpected upstream failures are distinguishable from successful comment deletions and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `comments_delete` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, request validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `comments_delete` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
