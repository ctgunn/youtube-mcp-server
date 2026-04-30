# Feature Specification: Layer 1 Playlist Items List Wrapper

**Feature Branch**: `132-playlist-items-list`  
**Created**: 2026-04-28  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-132, as outlined in requirements/spec-kit-seed.md. Use '132' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlist Items Through Supported Lookup Modes (Priority: P1)

A platform developer can invoke an internal `playlistItems.list` capability with a supported lookup mode so downstream tools can retrieve playlist entries without assembling a raw upstream request by hand.

**Why this priority**: The core value of YT-132 is exposing a reusable Layer 1 retrieval path for playlist items. Without a dependable wrapper for supported playlist-item lookups, later layers cannot safely compose playlist inspection, curation, or research workflows.

**Independent Test**: Can be fully tested by submitting valid `playlistItems.list` requests for the supported lookup modes and confirming the wrapper returns normalized successful results for matching playlist items.

**Acceptance Scenarios**:

1. **Given** a caller provides a playlist identifier with the required retrieval context, **When** the caller invokes the `playlistItems.list` capability, **Then** the system returns the matching playlist items in the Layer 1 result shape.
2. **Given** a caller provides a supported identifier-based lookup mode, **When** the caller invokes the same capability, **Then** the system returns the matching playlist items and preserves which lookup mode was used.

---

### User Story 2 - Understand Selector, Paging, and Access Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `playlistItems.list` contract and understand its quota cost, supported selector modes, pagination behavior, and access expectations before reusing it in another workflow.

**Why this priority**: The seed explicitly calls out playlist and ID filter modes, and later layers need a reviewable contract for when paging is valid and how authorized access should be chosen. Reuse is risky if callers cannot tell which selectors are supported or when paging is allowed.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, supported selector modes, per-mode paging behavior, and the access expectation attached to the supported modes.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `playlistItems.list` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 1 unit is visible and consistent.
2. **Given** a higher-layer author wants to compose playlist-item retrieval into another workflow, **When** the author reviews the same contract, **Then** the author can determine which supported selector modes are available, which modes support paging, and that the supported retrieval paths use the documented API-key access mode for this slice.

---

### User Story 3 - Fail Clearly for Invalid or Unsupported Playlist Item Requests (Priority: P3)

A downstream tool author can distinguish invalid playlist-item requests from unsupported selector combinations or access-related failures when retrieval cannot proceed, so calling workflows can respond correctly instead of masking every failure as the same error.

**Why this priority**: Playlist-item retrieval can fail because the caller omitted a required selector, mixed incompatible selectors, supplied paging inputs outside the supported contract, or attempted to use a different access mode than the wrapper supports. Clear failure boundaries reduce ambiguous retries and help higher layers decide whether to correct input or change retrieval mode.

**Independent Test**: Can be fully tested by submitting requests with missing selectors, conflicting selectors, unsupported paging or modifiers, or an incompatible access mode and verifying the system returns distinct normalized failure categories.

**Acceptance Scenarios**:

1. **Given** a caller submits a `playlistItems.list` request without any supported lookup selector, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a `playlistItems.list` request that combines incompatible selectors or relies on unsupported retrieval modifiers, **When** the request is evaluated, **Then** the system returns a distinct normalized error instead of attempting partial retrieval.

### Edge Cases

- What happens when a caller provides more than one primary selector in the same request, such as `playlistId` plus `id`?
- How does the system respond when a selector is syntactically valid but no playlist items match the request?
- What happens when a caller supplies `pageToken` or `maxResults` for a selector mode that does not support paging within this wrapper contract?
- What happens when a caller supplies an OAuth-backed or conditional auth context to a wrapper contract that documents one API-key access path for the supported selector set?
- How does the system preserve enough context in a successful retrieval result for downstream layers to understand whether the result came from playlist-based or identifier-based lookup?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `playlistItems.list` retrieval across the supported lookup modes, including playlist-based retrieval and identifier-based retrieval.
- **Red**: Add failing tests for missing selectors, conflicting selector combinations, unsupported paging inputs, unsupported retrieval modifiers, and incompatible auth-mode usage for the supported selector set.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `playlistItems.list` wrapper to accept supported lookup selectors, enforce the documented API-key access expectation, apply selector-specific paging rules, and return normalized retrieval results.
- **Green**: Add only the metadata and documentation support required to make quota, selector-mode boundaries, paging rules, and access expectations reviewable and testable.
- **Refactor**: Consolidate shared list-selector validation, paging-rule enforcement, and maintainer-facing metadata patterns with neighboring Layer 1 list wrappers, then run the full repository verification before review: `python3 -m pytest` and `python3 -m ruff check .`.
- Required test levels: unit tests for selector validation, paging-rule handling, access expectation handling, and metadata exposure; integration tests for representative playlist-item retrieval and normalized responses; and contract tests for quota, access, selector-mode, and paging guidance visibility.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any relevant selector-mode, paging, or access constraints.
- Pull request evidence must show the initial failing coverage for missing selector validation or paging/access handling, the passing targeted coverage for YT-132, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `playlistItems.list` retrieval operation.
- **FR-002**: System MUST identify the wrapper as representing the `playlistItems` resource and the `list` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `GET /playlistItems` path shape and the official quota-unit cost of `1` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `1` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `playlistItems.list` request contract, including the primary lookup modes this wrapper accepts for retrieval.
- **FR-006**: System MUST document playlist-based retrieval for this wrapper, including how callers provide a `playlistId` selector for playlist entry lookup.
- **FR-007**: System MUST document ID-based retrieval for this wrapper, including how callers provide one or more playlist-item identifiers for direct lookup.
- **FR-008**: System MUST document that the supported `playlistItems.list` selector set for this slice is limited to playlist-based retrieval through `playlistId` and identifier-based retrieval through `id`.
- **FR-009**: System MUST document that the supported `playlistItems.list` selector set uses API-key access for this slice and MUST clearly indicate that unsupported or future selector modes are outside the wrapper boundary.
- **FR-010**: System MUST document which supported lookup modes accept `pageToken`, `maxResults`, or both, and MUST clearly indicate when paging inputs fall outside the supported wrapper contract.
- **FR-011**: System MUST reject or clearly flag `playlistItems.list` requests that omit a required supported lookup selector.
- **FR-012**: System MUST reject or clearly flag requests that combine unsupported or mutually incompatible lookup selectors.
- **FR-013**: System MUST reject or clearly flag requests that rely on paging inputs or retrieval modifiers outside the supported wrapper contract.
- **FR-014**: System MUST reject or clearly flag requests that use an auth mode outside the documented API-key contract for the supported selector set.
- **FR-015**: System MUST return a normalized playlist-item retrieval result for valid requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-016**: System MUST preserve enough request context in successful results for downstream layers to identify which lookup mode and selector value produced the returned playlist items.
- **FR-017**: System MUST preserve a clear distinction between validation failures, access-related failures, and successful no-match retrieval outcomes.
- **FR-018**: System MUST expose maintainer-facing contract detail describing the supported selector modes, paging behavior, access expectations, and unsupported request boundaries for this wrapper.
- **FR-019**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-132.
- **FR-020**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-021**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, supported selector modes, paging rules, and access expectations for `playlistItems.list`.

### Key Entities *(include if feature involves data)*

- **Playlist Items List Wrapper Contract**: The maintainer-facing definition of the internal `playlistItems.list` wrapper, including endpoint identity, quota cost, supported selector modes, paging behavior, access expectations, and unsupported-request guidance.
- **Playlist Items List Request**: The input contract that combines one supported retrieval selector with any optional paging or retrieval modifiers allowed by the wrapper.
- **Playlist Item Lookup Mode**: The selected retrieval method, such as playlist-based retrieval or identifier-based retrieval, with rules about valid combinations, paging support, and access expectations.
- **Access Context**: The caller's authorization state that determines whether the selected `playlistItems.list` lookup mode is permitted.
- **Playlist Items List Result**: The normalized retrieval outcome containing the matched playlist items and enough context for downstream layers to understand the result.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `playlistItems.list`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported lookup behavior for this slice centers on the seed-required selectors `playlistId` and `id`, and the wrapper contract will reject unsupported selector combinations outside that boundary.
- Paging inputs are in scope only for selector modes that the wrapper contract explicitly marks as pageable; otherwise `pageToken` and `maxResults` remain outside the supported request boundary for this slice.
- Representative coverage of supported lookup modes is sufficient for this slice as long as the wrapper clearly identifies accepted selectors, rejects unsupported combinations, and documents any access expectations that materially affect reuse.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth, and endpoint documentation remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems.list` wrapper artifacts produced by this feature display the official quota-unit cost of `1` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which `playlistItems.list` selector modes are supported, which of those modes allow paging, and that the supported selector set uses the documented API-key access mode by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `playlistItems.list` lookup modes for this slice are represented by at least one passing successful retrieval scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing selectors, conflicting selector combinations, unsupported paging or retrieval modifiers, or ineligible access context fail with explicit normalized outcomes distinct from successful no-match retrieval results.
