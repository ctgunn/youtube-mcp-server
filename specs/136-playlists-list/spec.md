# Feature Specification: Layer 1 Playlists List Wrapper

**Feature Branch**: `136-playlists-list`  
**Created**: 2026-05-01  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-136, as outlined in requirements/spec-kit-seed.md. Use '136' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlists Through Supported Filter Modes (Priority: P1)

A platform developer can invoke an internal `playlists.list` capability with a supported filter mode so downstream tools can retrieve playlists without assembling a raw upstream request by hand.

**Why this priority**: The core value of YT-136 is exposing a reusable Layer 1 retrieval path for playlists. Without a dependable wrapper for supported playlist lookups, later layers cannot safely compose channel, curation, or research workflows that depend on playlist discovery.

**Independent Test**: Can be fully tested by submitting valid `playlists.list` requests for the supported filter modes and confirming the wrapper returns normalized successful results for matching playlists.

**Acceptance Scenarios**:

1. **Given** a caller provides a supported playlist lookup filter and the required retrieval context, **When** the caller invokes the `playlists.list` capability, **Then** the system returns the matching playlists in the Layer 1 result shape.
2. **Given** a caller provides a supported filter mode with valid paging inputs, **When** the caller invokes the same capability, **Then** the system returns matching playlists and preserves the request context needed for downstream continuation.

---

### User Story 2 - Understand Paging and Access Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `playlists.list` contract and understand its quota cost, supported filter modes, pagination behavior, and access expectations before reusing it in another workflow.

**Why this priority**: The seed explicitly requires pagination and filter modes to be documented, and the tool catalog notes that auth can vary by filter mode. Reuse becomes risky if maintainers cannot tell which selectors are supported, which requests can page, or when an auth mode changes across supported retrieval paths.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, supported filter modes, per-mode paging behavior, and the access expectation attached to each supported mode.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `playlists.list` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 1 unit is visible and consistent.
2. **Given** a higher-layer author wants to compose playlist retrieval into another workflow, **When** the author reviews the same contract, **Then** the author can determine which supported filter modes are available, which modes support paging, and whether a mode is available with API-key access, authorized access, or both.

---

### User Story 3 - Fail Clearly for Invalid or Unsupported Playlist Requests (Priority: P3)

A downstream tool author can distinguish invalid playlist requests from unsupported filter combinations, paging misuse, or access-related failures when retrieval cannot proceed, so calling workflows can respond correctly instead of masking every failure as the same error.

**Why this priority**: Playlist retrieval can fail because the caller omitted a required selector, mixed incompatible filters, supplied paging inputs outside the supported contract, or attempted to use a different access mode than the selected filter supports. Clear failure boundaries reduce ambiguous retries and help higher layers decide whether to correct input or change retrieval mode.

**Independent Test**: Can be fully tested by submitting requests with missing filters, conflicting filters, unsupported paging or modifiers, or an incompatible access mode and verifying the system returns distinct normalized failure categories.

**Acceptance Scenarios**:

1. **Given** a caller submits a `playlists.list` request without any supported filter mode, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a `playlists.list` request that combines incompatible filters, relies on unsupported retrieval modifiers, or uses an ineligible access mode for the selected filter, **When** the request is evaluated, **Then** the system returns a distinct normalized error instead of attempting partial retrieval.

### Edge Cases

- What happens when a caller provides more than one primary filter in the same request, such as `channelId` plus `id`, or `mine` plus `id`?
- How does the system respond when a filter is syntactically valid but no playlists match the request?
- What happens when a caller supplies `pageToken` or `maxResults` for a supported filter mode but the combination is not valid for that mode?
- How does the system distinguish filter modes that are available with API-key access from those that require authorized access?
- What happens when a caller supplies authorized context for a mode that works with API-key access, or API-key-only context for a mode that depends on user-owned playlists?
- How does the system preserve enough context in a successful retrieval result for downstream layers to understand which filter mode produced the returned playlists and whether more results can be requested?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `playlists.list` retrieval across the supported filter modes, including channel-based retrieval, identifier-based retrieval, and authorized self-playlist retrieval when that mode is in scope.
- **Red**: Add failing tests for missing filters, conflicting filter combinations, unsupported paging inputs, unsupported retrieval modifiers, and incompatible auth-mode usage for the selected filter mode.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `playlists.list` wrapper to accept supported filter modes, enforce the documented access expectation for each mode, apply paging rules, and return normalized retrieval results.
- **Green**: Add only the metadata and documentation support required to make quota, filter-mode boundaries, paging rules, and access expectations reviewable and testable.
- **Refactor**: Consolidate shared list-filter validation, paging-rule enforcement, and maintainer-facing metadata patterns with neighboring Layer 1 list wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for filter validation, paging-rule handling, access expectation handling, and metadata exposure; integration tests for representative playlist retrieval and normalized responses; and contract tests for quota, access, filter-mode, and paging guidance visibility.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any relevant filter-mode, paging, or access constraints.
- Pull request evidence must show the initial failing coverage for missing filter validation or paging/access handling, the passing targeted coverage for YT-136, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `playlists.list` retrieval operation.
- **FR-002**: System MUST identify the wrapper as representing the `playlists` resource and the `list` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `GET /playlists` path shape and the official quota-unit cost of `1` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `1` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `playlists.list` request contract, including the primary filter modes this wrapper accepts for retrieval.
- **FR-006**: System MUST document channel-based retrieval for this wrapper, including how callers provide a `channelId` filter to retrieve playlists associated with a channel.
- **FR-007**: System MUST document identifier-based retrieval for this wrapper, including how callers provide one or more playlist identifiers through `id` for direct lookup.
- **FR-008**: System MUST document whether self-owned playlist retrieval through `mine` is supported in this slice and, if supported, which authorization context it requires.
- **FR-009**: System MUST document that the supported `playlists.list` filter set for this slice is limited to the explicitly supported modes and MUST clearly indicate that unsupported or future filter modes are outside the wrapper boundary.
- **FR-010**: System MUST document which supported filter modes accept `pageToken`, `maxResults`, or both, and MUST clearly indicate when paging inputs fall outside the supported wrapper contract.
- **FR-011**: System MUST document the access expectation for each supported filter mode, including whether the mode is available with API-key access, authorized access, or both.
- **FR-012**: System MUST reject or clearly flag `playlists.list` requests that omit a required supported filter mode.
- **FR-013**: System MUST reject or clearly flag requests that combine unsupported or mutually incompatible filters.
- **FR-014**: System MUST reject or clearly flag requests that rely on paging inputs or retrieval modifiers outside the supported wrapper contract.
- **FR-015**: System MUST reject or clearly flag requests that use an auth mode outside the documented access contract for the selected filter mode.
- **FR-016**: System MUST return a normalized playlist retrieval result for valid requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-017**: System MUST preserve enough request context in successful results for downstream layers to identify which filter mode and selector value produced the returned playlists, along with any continuation state needed for a follow-on request.
- **FR-018**: System MUST preserve a clear distinction between validation failures, access-related failures, and successful no-match retrieval outcomes.
- **FR-019**: System MUST expose maintainer-facing contract detail describing the supported filter modes, paging behavior, access expectations, and unsupported request boundaries for this wrapper.
- **FR-020**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-136.
- **FR-021**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-022**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, supported filter modes, paging rules, and access expectations for `playlists.list`.

### Key Entities *(include if feature involves data)*

- **Playlists List Wrapper Contract**: The maintainer-facing definition of the internal `playlists.list` wrapper, including endpoint identity, quota cost, supported filter modes, paging behavior, access expectations, and unsupported-request guidance.
- **Playlists List Request**: The input contract that combines one supported retrieval filter with any optional paging or retrieval modifiers allowed by the wrapper.
- **Playlist Filter Mode**: The selected retrieval method, such as channel-based retrieval, identifier-based retrieval, or self-owned playlist retrieval, with rules about valid combinations, paging support, and access expectations.
- **Access Context**: The caller's authorization state that determines whether the selected `playlists.list` filter mode is permitted.
- **Playlists List Result**: The normalized retrieval outcome containing the matched playlists and enough context for downstream layers to understand the result.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `playlists.list`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported lookup behavior for this slice centers on the seed-aligned filters `channelId`, `id`, and the documented possibility of `mine`, because those are the filter modes called out by the current tool catalog for `playlists.list`.
- Authorized self-playlist retrieval is only in scope if the wrapper explicitly documents it as supported for this slice; otherwise requests that depend on `mine` remain outside the supported wrapper boundary.
- Paging inputs are in scope only for filter modes that the wrapper contract explicitly marks as pageable; otherwise `pageToken` and `maxResults` remain outside the supported request boundary for this slice.
- Representative coverage of supported filter modes is sufficient for this slice as long as the wrapper clearly identifies accepted filters, rejects unsupported combinations, and documents any access expectations that materially affect reuse.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth, and endpoint documentation remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlists.list` wrapper artifacts produced by this feature display the official quota-unit cost of `1` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which `playlists.list` filter modes are supported, which of those modes allow paging, and what access expectation applies to each supported mode by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `playlists.list` filter modes for this slice are represented by at least one passing successful retrieval scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing filters, conflicting filter combinations, unsupported paging or retrieval modifiers, or ineligible access context fail with explicit normalized outcomes distinct from successful no-match retrieval results.
