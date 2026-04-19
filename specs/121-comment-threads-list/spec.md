# Feature Specification: Layer 1 Comment Threads List Wrapper

**Feature Branch**: `121-comment-threads-list`  
**Created**: 2026-04-17  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-121, as outlined in requirements/spec-kit-seed.md. Use '121' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Comment Threads Through Supported Lookup Modes (Priority: P1)

A platform developer can invoke an internal `commentThreads.list` capability with a supported lookup mode so downstream tools can retrieve top-level discussion threads without assembling a raw upstream request by hand.

**Why this priority**: The core value of YT-121 is exposing a reusable Layer 1 retrieval path for comment threads. Without a dependable wrapper for supported thread lookups, later layers cannot safely compose thread-aware moderation, research, or audience-review workflows.

**Independent Test**: Can be fully tested by submitting valid `commentThreads.list` requests for the supported lookup modes and confirming the wrapper returns normalized successful results for matching threads.

**Acceptance Scenarios**:

1. **Given** a caller provides a video identifier with the required retrieval context, **When** the caller invokes the `commentThreads.list` capability, **Then** the system returns the matching comment threads in the Layer 1 result shape.
2. **Given** a caller provides a channel-related or thread-identifier-based lookup mode supported by the wrapper, **When** the caller invokes the same capability, **Then** the system returns the matching threads and preserves which lookup mode was used.

---

### User Story 2 - Understand Lookup and Access Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `commentThreads.list` contract and understand its quota cost, supported filter modes, and access expectations before reusing it in another workflow.

**Why this priority**: The seed explicitly calls out `videoId`, `allThreadsRelatedToChannelId`, and ID-based retrieval. Reuse is risky if callers cannot tell which thread selectors are supported, which optional filters are within scope, and whether any supported request combinations require a different access context.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, supported filter modes, and the access expectation attached to each supported mode.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `commentThreads.list` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 1 unit is visible and consistent.
2. **Given** a higher-layer author wants to compose comment-thread retrieval into another workflow, **When** the author reviews the same contract, **Then** the author can determine which supported filter modes are available, what access context each mode expects, and which request combinations are outside the wrapper boundary.

---

### User Story 3 - Fail Clearly for Invalid or Unsupported Thread Retrieval Requests (Priority: P3)

A downstream tool author can distinguish invalid comment-thread requests from unsupported selector combinations or access-related failures when retrieval cannot proceed, so calling workflows can respond correctly instead of masking every failure as the same error.

**Why this priority**: Comment-thread retrieval can fail because the caller omitted a required selector, mixed incompatible selectors, or used an otherwise supported lookup mode with an ineligible access context. Clear failure boundaries reduce ambiguous retries and help higher layers decide whether to correct input, change retrieval mode, or request different access.

**Independent Test**: Can be fully tested by submitting requests with missing selectors, conflicting selectors, unsupported modifiers, or an ineligible access context and verifying the system returns distinct normalized failure categories.

**Acceptance Scenarios**:

1. **Given** a caller submits a `commentThreads.list` request without any supported lookup selector, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a `commentThreads.list` request that combines incompatible selectors or relies on unsupported retrieval modifiers, **When** the request is evaluated, **Then** the system returns a distinct normalized error instead of attempting partial retrieval.

### Edge Cases

- What happens when a caller provides more than one primary thread selector in the same request, such as `videoId` plus an ID-based lookup?
- How does the system respond when a lookup selector is syntactically valid but no comment threads match the request?
- What happens when a caller requests threads for a valid video or channel that currently has no retrievable comment threads?
- How does the system handle optional retrieval modifiers that fall outside the supported wrapper contract?
- What happens when the selected retrieval mode is valid but the caller supplies an access context that is not eligible for that mode or for an attached moderation-related filter?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `commentThreads.list` retrieval across the supported lookup modes, including video-based retrieval, channel-related retrieval, and thread-identifier-based retrieval.
- **Red**: Add failing tests for missing selectors, conflicting selector combinations, unsupported retrieval modifiers, and access-context mismatches for the selected lookup mode.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `commentThreads.list` wrapper to accept supported lookup selectors, enforce the relevant access expectations, and return normalized retrieval results.
- **Green**: Add only the metadata and documentation support required to make quota, filter-mode boundaries, and access expectations reviewable and testable.
- **Refactor**: Consolidate shared list-selector validation and maintainer-facing metadata patterns with neighboring Layer 1 list wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for selector validation, access expectation handling, and metadata exposure; integration tests for representative comment-thread retrieval and normalized responses; and contract tests for quota, access, and filter-mode guidance visibility.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any relevant lookup-mode or access constraints.
- Pull request evidence must show the initial failing coverage for missing selector validation or access handling, the passing targeted coverage for YT-121, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `commentThreads.list` retrieval operation.
- **FR-002**: System MUST identify the wrapper as representing the `commentThreads` resource and the `list` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `GET /commentThreads` path shape and the official quota-unit cost of `1` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `1` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `commentThreads.list` request contract, including the primary lookup modes this wrapper accepts for retrieval.
- **FR-006**: System MUST document video-based retrieval for this wrapper, including how callers provide a `videoId` selector for thread lookup.
- **FR-007**: System MUST document channel-related retrieval for this wrapper, including how callers provide an `allThreadsRelatedToChannelId` selector when retrieving threads associated with one channel.
- **FR-008**: System MUST document ID-based retrieval for this wrapper, including how callers provide one or more thread identifiers for direct thread lookup.
- **FR-009**: System MUST document the access expectation attached to each supported lookup mode and MUST clearly indicate when a mode is available with standard access versus when it depends on a different or elevated access context.
- **FR-010**: System MUST reject or clearly flag `commentThreads.list` requests that omit a required supported lookup selector.
- **FR-011**: System MUST reject or clearly flag requests that combine unsupported or mutually incompatible lookup selectors.
- **FR-012**: System MUST reject or clearly flag requests that rely on retrieval modifiers outside the supported wrapper contract.
- **FR-013**: System MUST return a normalized comment-thread retrieval result for valid requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-014**: System MUST preserve a clear distinction between validation failures, access-related failures, and successful no-match retrieval outcomes.
- **FR-015**: System MUST expose maintainer-facing contract detail describing the supported filter modes and unsupported request boundaries for this wrapper.
- **FR-016**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-121.
- **FR-017**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-018**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, supported filter modes, and access expectations for `commentThreads.list`.

### Key Entities *(include if feature involves data)*

- **Comment Threads List Wrapper Contract**: The maintainer-facing definition of the internal `commentThreads.list` wrapper, including endpoint identity, quota cost, supported filter modes, access expectations, and unsupported-request guidance.
- **Comment Threads List Request**: The input contract that combines one supported retrieval selector with any optional retrieval modifiers allowed by the wrapper.
- **Comment Thread Lookup Mode**: The selected retrieval method, such as video-based retrieval, channel-related retrieval, or identifier-based retrieval, with rules about valid combinations and access expectations.
- **Access Context**: The caller's authorization state that determines whether the selected `commentThreads.list` lookup mode is permitted.
- **Comment Threads List Result**: The normalized retrieval outcome containing the matched comment threads and enough context for downstream layers to understand the result.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `commentThreads.list`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported lookup behavior for this slice centers on the seed-required `videoId`, `allThreadsRelatedToChannelId`, and ID-based retrieval modes, and the wrapper contract will reject unsupported selector combinations outside that boundary.
- Representative coverage of supported lookup modes is sufficient for this slice as long as the wrapper clearly identifies accepted selectors, rejects unsupported combinations, and documents any access expectations that materially affect reuse.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth, and endpoint documentation remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `commentThreads.list` wrapper artifacts produced by this feature display the official quota-unit cost of `1` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which `commentThreads.list` filter modes are supported and what access expectation applies to each mode by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `commentThreads.list` lookup modes for this slice are represented by at least one passing successful retrieval scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing selectors, conflicting selector combinations, unsupported retrieval modifiers, or ineligible access context fail with explicit normalized outcomes distinct from successful no-match retrieval results.
