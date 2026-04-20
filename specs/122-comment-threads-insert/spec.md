# Feature Specification: Layer 1 Comment Threads Insert Wrapper

**Feature Branch**: `122-comment-threads-insert`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-122, as outlined in requirements/spec-kit-seed.md. Use '122' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Top-Level Comment Thread Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit an authorized top-level comment creation request through a typed internal capability so downstream tools can publish a new discussion thread without assembling a raw upstream write request.

**Why this priority**: The core value of YT-122 is enabling a real Layer 1 creation path for `commentThreads.insert`. Without a dependable wrapper for top-level thread creation, higher-layer engagement and moderation workflows cannot safely start new public discussion threads through the shared integration layer.

**Independent Test**: Can be fully tested by submitting one valid authorized top-level comment creation request for an eligible discussion target and confirming the wrapper returns a normalized successful creation outcome.

**Acceptance Scenarios**:

1. **Given** a caller provides an eligible write access context, a supported target for the new discussion thread, and the required top-level comment content, **When** the caller invokes the `commentThreads.insert` capability, **Then** the system creates the top-level comment thread and returns a normalized successful creation outcome.
2. **Given** a caller provides a valid top-level comment creation request that includes supported owner-delegation context, **When** the caller invokes the same capability, **Then** the system preserves that context in the create attempt without requiring raw upstream request assembly.

---

### User Story 2 - Understand Top-Level Comment and OAuth Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `commentThreads.insert` contract and understand its quota cost, OAuth requirement, and top-level-comment-only behavior before reusing it in a workflow that creates public discussion content.

**Why this priority**: The seed explicitly requires documentation of the 50-unit quota cost, top-level-comment creation behavior, and OAuth requirements. Reuse is risky if callers cannot tell that this wrapper starts a new thread, what authorization it requires, or what minimum request shape is needed before creation can proceed.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, OAuth requirement, top-level-comment-only boundary, and the minimum request shape needed for a valid creation attempt.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `commentThreads.insert` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose thread creation into another workflow, **When** the author reviews the same contract, **Then** the author can determine that OAuth-backed authorization is required and that the wrapper is limited to creating top-level comments rather than replies.

---

### User Story 3 - Fail Clearly for Invalid or Ineligible Thread-Creation Requests (Priority: P3)

A downstream tool author can distinguish invalid top-level comment creation requests from missing authorization or ineligible targets when creation cannot proceed, so calling workflows can guide remediation correctly instead of masking every failure as a generic error.

**Why this priority**: Thread-creation operations are public write actions and can fail for missing required content, missing authorization, unsupported thread shape, or attempts to create content in a context that the caller cannot use. Clear failure boundaries help higher layers decide whether to correct input, request authorization, change target context, or stop the workflow.

**Independent Test**: Can be fully tested by submitting requests with missing authorization, missing required top-level comment content, unsupported thread shapes, or invalid or unavailable creation targets and verifying the system returns distinct normalized failure categories.

**Acceptance Scenarios**:

1. **Given** a caller submits a `commentThreads.insert` request without eligible OAuth-backed authorization, **When** the request is evaluated, **Then** the system returns a distinct normalized authorization failure instead of attempting creation.
2. **Given** a caller submits a `commentThreads.insert` request that omits required top-level comment content, targets an unsupported creation context, or attempts to create a reply-style thread shape, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation or target-eligibility failure.

### Edge Cases

- What happens when a caller attempts to create a comment thread without the required top-level comment content?
- How does the system respond when a creation request is syntactically valid but targets a discussion context that is unavailable, disabled, or otherwise not eligible for new top-level comments?
- What happens when a caller attempts to use this wrapper to create a reply instead of a new top-level thread?
- How does the system handle optional owner-delegation context that is incomplete or incompatible with the requested creation?
- What happens when a creation request is validly shaped but the resulting thread cannot be published because of an upstream restriction or access limitation?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `commentThreads.insert` execution with an eligible write access context, including a representative top-level comment creation request for one supported discussion target.
- **Red**: Add failing tests for missing OAuth-backed authorization, missing required top-level comment content, unsupported thread shapes, invalid or unavailable creation targets, and incompatible optional owner-delegation context.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `commentThreads.insert` wrapper to accept a valid top-level comment creation request, enforce OAuth-backed write access, and return a normalized successful creation outcome.
- **Green**: Add only the metadata and documentation support required to make quota cost, OAuth expectations, top-level-comment-only behavior, and supported request boundaries reviewable and testable.
- **Refactor**: Consolidate shared write-operation validation and documentation patterns with neighboring Layer 1 comment write wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for create-request validation, authorization enforcement, and metadata exposure; integration tests for representative top-level comment creation and normalized responses; and contract tests for quota, OAuth expectations, and top-level-comment boundary guidance visibility.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any relevant authorization or top-level-comment constraints.
- Pull request evidence must show the initial failing coverage for missing validation or authorization handling, the passing targeted coverage for YT-122, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `commentThreads.insert` create operation.
- **FR-002**: System MUST identify the wrapper as representing the `commentThreads` resource and the `insert` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /commentThreads` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `commentThreads.insert` request contract, including the required discussion target and the required top-level comment content used for one create attempt.
- **FR-006**: System MUST require the create request to represent a top-level comment thread creation attempt rather than a reply-style or otherwise unsupported thread shape.
- **FR-007**: System MUST require an OAuth-backed authorization context before a `commentThreads.insert` request can proceed.
- **FR-008**: System MUST document that `commentThreads.insert` creates top-level comment threads, requires OAuth-backed authorization, and may include supported owner-delegation context where applicable.
- **FR-009**: System MUST reject or clearly flag create requests that omit the required discussion target or required top-level comment content.
- **FR-010**: System MUST reject or clearly flag create requests that attempt to create unsupported thread shapes, including reply-style content outside the wrapper boundary.
- **FR-011**: System MUST reject or clearly flag create requests that include unsupported inputs outside the supported wrapper contract.
- **FR-012**: System MUST preserve a clear distinction between validation failures, authorization failures, target-eligibility failures, upstream create failures, and successful create outcomes.
- **FR-013**: System MUST return a normalized comment-thread creation result for valid requests so higher layers can recognize the create outcome without reverse-engineering the response.
- **FR-014**: System MUST expose maintainer-facing contract detail describing the OAuth requirement, top-level-comment-only behavior, and the minimum creation preconditions for this wrapper.
- **FR-015**: System MUST clearly indicate how callers should interpret creation attempts when the requested discussion target is unavailable, disallows new comments, or is otherwise ineligible in the current authorization context.
- **FR-016**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-122.
- **FR-017**: System MUST preserve alignment with the shared Layer 1 metadata and write-operation standards established for earlier Layer 1 slices.
- **FR-018**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, top-level-comment boundary, create preconditions, and failure boundaries for `commentThreads.insert`.

### Key Entities *(include if feature involves data)*

- **Comment Threads Insert Wrapper Contract**: The maintainer-facing definition of the internal `commentThreads.insert` wrapper, including endpoint identity, quota cost, OAuth rules, top-level-comment boundaries, creation preconditions, and failure-boundary guidance.
- **Comment Thread Create Request**: The input contract that combines the discussion target, the top-level comment content, and any supported owner-delegation context for one create attempt.
- **Authorization Context**: The caller's access state that determines whether a top-level comment thread creation operation is permitted.
- **Creation Target State**: The reviewable status of the targeted discussion context at create time, such as eligible for new comments, unavailable, disabled, or inaccessible to the current authorization context.
- **Comment Thread Create Result**: The normalized successful outcome indicating that the requested top-level comment thread was accepted and created for the targeted discussion context.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `commentThreads.insert`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- The wrapper contract will support the currently documented create pattern for one new top-level comment thread at a time and will reject reply-style or otherwise unsupported thread shapes outside that boundary.
- Representative coverage of supported create patterns is sufficient for this slice as long as the wrapper clearly identifies required authorization, required creation inputs, top-level-comment boundaries, and the boundaries for unsupported or ineligible create attempts.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth, and endpoint documentation remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `commentThreads.insert` wrapper artifacts produced by this feature display the official quota-unit cost of `50` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `commentThreads.insert` requires OAuth-backed authorization and is limited to top-level comment creation by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of representative supported top-level comment creation patterns for this slice are represented by at least one passing successful creation scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing authorization, missing required creation inputs, unsupported thread shapes, or ineligible target states fail with explicit normalized outcomes distinct from successful creation results.
