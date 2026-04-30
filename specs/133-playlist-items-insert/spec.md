# Feature Specification: Layer 1 Playlist Items Insert Wrapper

**Feature Branch**: `133-playlist-items-insert`  
**Created**: 2026-04-30  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-133, as outlined in requirements/spec-kit-seed.md. Use '133' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a Video to a Playlist Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit a typed internal `playlistItems.insert` request with the required playlist-assignment data so higher layers can add a video to a playlist without assembling raw upstream request behavior by hand.

**Why this priority**: The primary value of YT-133 is enabling playlist-item creation through a stable shared Layer 1 wrapper. Without it, downstream workflows cannot reliably add entries to playlists or compose playlist-curation actions.

**Independent Test**: Can be fully tested by submitting a valid authorized `playlistItems.insert` request that includes the required writable data, then confirming the wrapper returns a normalized created playlist-item result.

**Acceptance Scenarios**:

1. **Given** a caller provides the required writable playlist-assignment data on an authorized request, **When** the caller invokes the `playlistItems.insert` capability, **Then** the system creates the playlist item and returns the created playlist-item data in the Layer 1 result shape.
2. **Given** a caller submits a valid playlist-item creation request, **When** the request succeeds, **Then** the successful result preserves enough request context for downstream layers to identify the created playlist entry and the originating playlist/video association.

---

### User Story 2 - Review Quota, Authorization, and Writable-Part Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `playlistItems.insert` wrapper contract and understand its quota cost, OAuth requirement, and writable-part expectations before composing it into another workflow.

**Why this priority**: The seed requires the 50-unit quota cost plus OAuth and writable-part requirements to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly tell what an authorized create request must contain or which writable inputs are supported.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required writable part, required creation inputs, and unsupported-request boundaries in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `playlistItems.insert` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose playlist-item creation into another workflow, **When** the author reviews the same contract, **Then** the author can determine that authorized access is required, which writable part is supported, and which playlist-assignment inputs must be supplied for a supported request.

---

### User Story 3 - Reject Invalid or Unauthorized Insert Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid playlist-item creation requests from requests that omit required writable data, use unsupported writable parts, or lack authorization so calling workflows can correct the request instead of misinterpreting failures.

**Why this priority**: Playlist-item insertion is a mutation with explicit writable-boundary rules. Higher layers need clear failure boundaries so they can fix invalid inputs, supply the missing authorization context, or surface a real upstream rejection appropriately.

**Independent Test**: Can be fully tested by submitting requests with missing writable data, unsupported writable parts, missing OAuth-backed access, and authorized creation requests that receive upstream rejection, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `playlistItems.insert` request without the required writable playlist-assignment data, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement or uses writable parts outside the supported contract, **When** the request is evaluated, **Then** the system clearly flags the request as unauthorized or unsupported instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller provides the playlist identifier but omits the video reference required to create a playlist item?
- How does the system respond when the request uses a writable part outside the documented supported insert boundary?
- What happens when a caller provides duplicate or conflicting placement details for where the new playlist item should appear within the playlist?
- How does the system respond when a validly shaped authorized request is rejected upstream because the target playlist is not writable or the referenced video cannot be added?
- How does the system preserve enough creation context in a successful result for downstream layers to identify the created playlist item and the originating playlist/video relationship?
- How does the system distinguish validation failures, authorization failures, and upstream create failures from a successful playlist-item creation outcome?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `playlistItems.insert` creation using a representative authorized request that includes the required writable playlist-assignment data.
- **Red**: Add failing tests for missing writable data, unsupported writable parts, malformed placement data, missing OAuth-backed access, and authorized requests that receive an upstream create failure.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `playlistItems.insert` wrapper to accept supported writable inputs, enforce the OAuth requirement, and return normalized creation results.
- **Green**: Add only the metadata and documentation support required to make quota cost, OAuth expectations, writable-part boundaries, and required creation inputs reviewable and testable.
- **Refactor**: Consolidate shared mutation-wrapper writable-input validation and OAuth documentation patterns with neighboring Layer 1 insert/update wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, writable-part enforcement, OAuth enforcement, and metadata completeness; integration tests for representative playlist-item creation and normalized mutation responses; and contract tests for quota, OAuth expectations, and maintainer-facing writable-part guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, required writable data, authorization requirement, and unsupported writable-part boundaries.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete writable-part guidance, the passing targeted coverage for YT-133, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `playlistItems.insert` creation operation.
- **FR-002**: System MUST identify the wrapper as representing the `playlistItems` resource and the `insert` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /playlistItems` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `playlistItems.insert` request contract, including the writable part and the required playlist-assignment data for a supported create request.
- **FR-006**: System MUST document the required creation inputs, including the role of the writable part, the playlist identifier, the referenced video identifier, and any supported placement data, in maintainer-facing artifacts.
- **FR-007**: System MUST record that `playlistItems.insert` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document the supported writable-part boundary for `playlistItems.insert`, including which writable part values are accepted and which insert requests fall outside the wrapper contract.
- **FR-009**: System MUST reject or clearly flag `playlistItems.insert` requests that omit the required writable playlist-assignment data.
- **FR-010**: System MUST reject or clearly flag `playlistItems.insert` requests that omit either the target playlist identifier or the referenced video identifier.
- **FR-011**: System MUST reject or clearly flag requests whose writable part, placement data, or other mutation inputs do not satisfy the documented supported contract.
- **FR-012**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `playlistItems.insert`.
- **FR-013**: System MUST return a normalized playlist-item creation result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-014**: System MUST preserve enough request context in successful results for downstream layers to identify the created playlist item and the originating playlist/video relationship.
- **FR-015**: System MUST preserve a clear distinction between validation failures, access-related failures, upstream create failures, and successful playlist-item creation outcomes.
- **FR-016**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required create inputs, supported writable part, and unsupported insert boundaries for this wrapper.
- **FR-017**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-133.
- **FR-018**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-019**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, required writable inputs, and writable-part boundaries for `playlistItems.insert`.

### Key Entities *(include if feature involves data)*

- **Playlist Items Insert Wrapper Contract**: The maintainer-facing definition of the internal `playlistItems.insert` wrapper, including endpoint identity, quota cost, OAuth requirement, supported writable part, required create inputs, and unsupported-request boundaries.
- **Playlist Item Create Request**: The input contract that combines the required writable playlist-assignment data with any explicitly supported optional placement inputs for a playlist-item insertion request.
- **Writable Playlist Assignment**: The creation payload that identifies the target playlist, the video to add, and any supported placement detail required to create the playlist item.
- **Playlist Item Creation Result**: The normalized creation outcome containing the created playlist-item data and enough request context for downstream layers to interpret what was created.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `playlistItems.insert`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported creation behavior for this slice centers on the writable part required for playlist-item insertion and the playlist/video assignment needed to add a video to a playlist.
- Placement-related insert inputs are in scope only when the wrapper explicitly documents them as supported; otherwise they remain outside the wrapper boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, item duplication policy, video eligibility, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth expectations, endpoint identity, and writable-part guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistItems.insert` wrapper artifacts produced by this feature display the official quota-unit cost of `50` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `playlistItems.insert` requires authorized access, which writable part is supported, and which create inputs are mandatory by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `playlistItems.insert` creation patterns for this slice are represented by at least one passing successful creation scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing writable data, unsupported writable parts, malformed placement inputs, or missing OAuth-backed access fail with explicit normalized outcomes distinct from upstream create failures and successful creation results.
