# Feature Specification: Layer 1 Comments Moderation Status Wrapper

**Feature Branch**: `119-comments-set-moderation-status`  
**Created**: 2026-04-15  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-119, as outlined in requirements/spec-kit-seed.md. Use '119' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Moderate Comments Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can invoke an internal `comments.setModerationStatus` capability with one or more valid comment targets, a supported moderation outcome, and eligible write access so downstream tools can apply comment moderation without assembling a raw upstream request.

**Why this priority**: The core value of YT-119 is enabling a real Layer 1 moderation path for existing comments. Without a dependable moderation-status wrapper, higher-layer moderation and workflow tools cannot consistently change comment review state through the shared integration layer.

**Independent Test**: Can be fully tested by submitting a valid moderation request with eligible write access and confirming the wrapper returns a normalized successful moderation result.

**Acceptance Scenarios**:

1. **Given** a caller provides one or more valid comment identifiers, a supported moderation outcome, and an eligible write access context, **When** the caller invokes the `comments.setModerationStatus` capability, **Then** the system applies the requested moderation outcome to the targeted comments and returns a normalized moderation-update result.
2. **Given** a caller provides a valid moderation request that includes a supported optional moderation flag, **When** the caller invokes the same capability, **Then** the system preserves that moderation intent in the successful result without obscuring which moderation outcome was requested.

---

### User Story 2 - Understand Moderation-State and OAuth Boundaries Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `comments.setModerationStatus` contract and understand its quota cost, OAuth requirement, and supported moderation-state transitions before reusing it in a workflow that moderates comment activity.

**Why this priority**: The seed explicitly requires moderation-state transitions and OAuth requirements to be documented in the wrapper contract. Reuse is risky if callers cannot tell that this is an authorized moderation write operation, which moderation outcomes are supported, or which request combinations fall outside the wrapper boundary.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, required authorization, and supported moderation-transition rules.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `comments.setModerationStatus` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose comment moderation into another workflow, **When** the author reviews the same contract, **Then** the author can determine that OAuth-backed write access is required and can identify the supported moderation states, transition boundaries, and optional moderation flags this wrapper accepts.

---

### User Story 3 - Fail Clearly for Invalid or Ineligible Moderation Requests (Priority: P3)

A downstream tool author can distinguish invalid moderation payloads from missing authorization, unsupported moderation transitions, incompatible moderation flags, or unavailable comment targets so calling workflows can guide users correctly instead of masking every moderation failure as the same error.

**Why this priority**: Moderation requests can fail because the caller omitted comment targets, selected an unsupported moderation outcome, combined incompatible moderation flags, or lacks the authorization needed to moderate the selected comments. Clear failure boundaries help higher layers decide whether to correct input, request authorization, or stop the workflow.

**Independent Test**: Can be fully tested by submitting requests with missing comment identifiers, unsupported moderation states, incompatible optional moderation flags, or ineligible access contexts and verifying the system returns distinct normalized failure categories.

**Acceptance Scenarios**:

1. **Given** a caller submits a `comments.setModerationStatus` request that omits the required comment identifiers or moderation outcome, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a `comments.setModerationStatus` request that uses unsupported moderation transitions, incompatible moderation flags, or lacks eligible OAuth-backed access, **When** the request is evaluated, **Then** the system returns a distinct normalized failure instead of attempting a partial moderation update.

### Edge Cases

- What happens when a caller provides multiple comment identifiers and one or more targets are missing, deleted, or no longer eligible for moderation?
- How does the system respond when a caller supplies duplicate comment identifiers in the same moderation request?
- What happens when a caller provides a syntactically valid moderation outcome that is outside the wrapper's supported moderation-transition boundary?
- How does the system handle optional moderation flags that conflict with the selected moderation outcome?
- What happens when the caller has OAuth-backed access but lacks the authority needed to moderate the targeted comments?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `comments.setModerationStatus` execution with eligible OAuth-backed write access, including a representative request that moderates one or more comments to a supported outcome.
- **Red**: Add failing tests for missing authorization, missing comment identifiers, missing moderation outcome, unsupported moderation states, incompatible optional moderation flags, duplicate or invalid comment targets, and unavailable moderation targets.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `comments.setModerationStatus` wrapper to accept a valid moderation request, enforce OAuth-backed moderation access, and return a normalized moderation-update result.
- **Green**: Add only the metadata and documentation support required to make quota cost, moderation-transition boundaries, optional moderation-flag rules, and authorization expectations reviewable and testable.
- **Refactor**: Consolidate shared moderation-write validation and documentation patterns with neighboring Layer 1 write wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, authorization handling, moderation-state enforcement, and metadata exposure; integration tests for representative comment moderation flows and normalized responses; and contract tests for quota, OAuth, moderation-transition, and optional-flag guidance visibility.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any relevant moderation-state or authorization constraints.
- Pull request evidence must show the initial failing coverage for missing validation, unsupported moderation-state handling, or authorization handling, the passing targeted coverage for YT-119, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `comments.setModerationStatus` moderation operation.
- **FR-002**: System MUST identify the wrapper as representing the `comments` resource and the `setModerationStatus` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /comments/setModerationStatus` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `comments.setModerationStatus` request contract, including one or more comment identifiers and the requested moderation outcome.
- **FR-006**: System MUST require an OAuth-backed write access context before a `comments.setModerationStatus` request can proceed.
- **FR-007**: System MUST document that this wrapper is a moderation write operation that requires OAuth-backed authorization.
- **FR-008**: System MUST document the supported moderation-state transitions for this wrapper, including which moderation outcomes are accepted and which transition combinations or states are outside the wrapper boundary.
- **FR-009**: System MUST document any supported optional moderation flags that may accompany the moderation request and MUST clearly indicate which moderation outcomes they can validly accompany.
- **FR-010**: System MUST reject or clearly flag moderation requests that omit the required comment identifiers or requested moderation outcome.
- **FR-011**: System MUST reject or clearly flag moderation requests that use unsupported moderation states, unsupported moderation transitions, or incompatible optional moderation flags.
- **FR-012**: System MUST reject or clearly flag moderation requests that include invalid, duplicate, or otherwise unusable comment targets when those targets prevent the request from being treated as a supported moderation call.
- **FR-013**: System MUST preserve a clear distinction between validation failures, authorization failures, unsupported moderation-transition failures, upstream moderation failures, and successful moderation outcomes.
- **FR-014**: System MUST return a normalized moderation-update result for valid requests so higher layers can consume the moderation outcome without reverse-engineering the response.
- **FR-015**: System MUST expose maintainer-facing contract detail describing the supported moderation states, optional moderation-flag rules, OAuth requirement, and unsupported request shapes for this wrapper.
- **FR-016**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-119.
- **FR-017**: System MUST preserve alignment with the shared Layer 1 metadata and write-operation standards established for earlier Layer 1 slices.
- **FR-018**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, moderation-transition rules, optional moderation-flag boundaries, and OAuth requirement for `comments.setModerationStatus`.

### Key Entities *(include if feature involves data)*

- **Comments Moderation Wrapper Contract**: The maintainer-facing definition of the internal `comments.setModerationStatus` wrapper, including endpoint identity, quota cost, authorization rules, moderation-transition guidance, optional moderation-flag behavior, and unsupported-request boundaries.
- **Comment Moderation Request**: The input contract that combines the targeted comment identifiers, requested moderation outcome, and any supported optional moderation flags for one moderation attempt.
- **Moderation Transition Policy**: The rules that define which moderation outcomes are supported, which optional moderation flags may accompany them, and which state combinations are rejected.
- **Write Access Context**: The caller's authorization state that determines whether the moderation operation is permitted.
- **Moderation Update Result**: The normalized successful outcome containing the applied moderation outcome and enough context for downstream layers to understand what moderation action completed.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `comments.setModerationStatus`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- The wrapper supports one requested moderation outcome per call and applies that outcome to one or more targeted comments in the same moderation request.
- Optional moderation flags are only in scope when they are explicitly documented as compatible with the selected moderation outcome; unsupported combinations are rejected or clearly documented as out of scope.
- Representative moderation coverage is sufficient for this slice as long as the wrapper clearly identifies required authorization, accepted moderation states, and the boundaries for unsupported moderation transitions or optional-flag combinations.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth, and endpoint documentation remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments.setModerationStatus` wrapper artifacts produced by this feature display the official quota-unit cost of `50` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `comments.setModerationStatus` is an OAuth-backed moderation write operation and identify its supported moderation-state transitions by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `comments.setModerationStatus` moderation patterns for this slice are represented by at least one passing successful moderation scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing authorization, missing required moderation inputs, unsupported moderation transitions, incompatible optional moderation flags, or unusable moderation targets fail with explicit normalized outcomes distinct from successful moderation results.
