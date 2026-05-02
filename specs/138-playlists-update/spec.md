# Feature Specification: Layer 1 Playlists Update Wrapper

**Feature Branch**: `138-playlists-update`  
**Created**: 2026-05-02  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-138, as outlined in requirements/spec-kit-seed.md. Use '138' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update an Existing Playlist Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit authorized playlist update data through a typed internal `playlists.update` capability so higher layers can revise an existing playlist without assembling raw upstream update behavior by hand.

**Why this priority**: The core value of YT-138 is enabling playlist updates through a stable shared Layer 1 wrapper. Without a dependable update path, downstream curation and channel-management workflows cannot rely on a consistent contract for changing existing playlists.

**Independent Test**: Can be fully tested by submitting a valid authorized `playlists.update` request for an existing playlist, then confirming the wrapper returns a normalized updated-playlist result.

**Acceptance Scenarios**:

1. **Given** a caller provides the required playlist identifier, writable part selection, and supported update data on an authorized request, **When** the caller invokes the `playlists.update` capability, **Then** the system updates the playlist and returns the updated playlist data in the Layer 1 result shape.
2. **Given** a caller submits a valid playlist update request, **When** the request succeeds, **Then** the successful result preserves enough request context for downstream layers to identify the updated playlist and the update inputs that were applied.

---

### User Story 2 - Review Writable-Field and Authorization Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `playlists.update` wrapper contract and understand its quota cost, OAuth requirement, and writable-field expectations before composing it into another workflow.

**Why this priority**: The seed explicitly requires the 50-unit quota cost and writable-field expectations to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly tell what an authorized update request must contain or which playlist fields are supported by this slice.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required update inputs, writable-field boundaries, and unsupported-request guidance in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `playlists.update` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose playlist updates into another workflow, **When** the author reviews the same contract, **Then** the author can determine that authorized access is required, which update inputs are mandatory, and which writable playlist fields are supported for this slice.

---

### User Story 3 - Reject Invalid or Unauthorized Playlist-Update Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid playlist-update requests from requests that omit required update inputs, attempt unsupported writable changes, or lack authorization so calling workflows can correct the request instead of misinterpreting failures.

**Why this priority**: Playlist updates are mutation-oriented and can change the meaning and visibility of an existing playlist. Higher layers need clear failure boundaries so they can fix invalid requests, supply the missing authorization context, or surface a real upstream rejection appropriately.

**Independent Test**: Can be fully tested by submitting requests with missing identifiers, missing writable data, unsupported writable fields, missing OAuth-backed access, and authorized update requests that receive upstream rejection, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `playlists.update` request without the required identifier or writable update data, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement or relies on writable fields outside the supported contract, **When** the request is evaluated, **Then** the system clearly flags the request as unauthorized or unsupported instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller provides a playlist identifier but no writable fields that would change the existing playlist?
- How does the system respond when the request attempts to change playlist fields that the wrapper contract does not support for this slice?
- What happens when a caller submits a validly shaped authorized request for a playlist that no longer exists or is no longer writable by the caller?
- How does the system preserve enough update context in a successful result for downstream layers to identify which playlist changed and which writable inputs were applied?
- How does the system distinguish validation failures, authorization failures, unsupported writable-field requests, and upstream update failures from a successful playlist-update outcome?
- How does the system communicate the endpoint-wide OAuth requirement and writable-field boundary without forcing maintainers to inspect implementation details?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `playlists.update` behavior using a representative authorized request that includes the required playlist identifier, writable part selection, and supported update data.
- **Red**: Add failing tests for missing identifiers, missing writable update data, unsupported writable fields, inconsistent writable-part selections, missing OAuth-backed access, and authorized requests that receive an upstream update failure.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `playlists.update` wrapper to accept supported update inputs, enforce the OAuth requirement, and return normalized update results.
- **Green**: Add only the metadata and documentation support required to make quota cost, OAuth expectations, required update inputs, supported writable fields, and unsupported update boundaries reviewable and testable.
- **Refactor**: Consolidate shared mutation-wrapper writable-field validation and OAuth documentation patterns with neighboring Layer 1 insert and update wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, writable-field boundary enforcement, OAuth enforcement, and metadata completeness; integration tests for representative playlist updates and normalized mutation responses; and contract tests for quota, OAuth expectations, and maintainer-facing update guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, required identifier and update inputs, authorization requirement, and unsupported writable-field boundaries.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete update guidance, the passing targeted coverage for YT-138, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `playlists.update` update operation.
- **FR-002**: System MUST identify the wrapper as representing the `playlists` resource and the `update` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `PUT /playlists` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `playlists.update` request contract, including the required playlist identifier, writable part selection, and supported writable update data for a valid update request.
- **FR-006**: System MUST document the required update inputs, including the role of `part`, the required identifying information, and the supported writable playlist fields, in maintainer-facing artifacts.
- **FR-007**: System MUST record that `playlists.update` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document the supported writable-field boundary for `playlists.update`, including which update fields are accepted for this slice and which update requests fall outside the wrapper contract.
- **FR-009**: System MUST reject or clearly flag `playlists.update` requests that omit the required playlist identifier.
- **FR-010**: System MUST reject or clearly flag `playlists.update` requests that omit the required writable update data.
- **FR-011**: System MUST reject or clearly flag requests whose writable part selection or writable playlist fields do not satisfy the documented supported contract.
- **FR-012**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `playlists.update`.
- **FR-013**: System MUST return a normalized playlist update result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-014**: System MUST preserve enough request context in successful results for downstream layers to identify the updated playlist and the originating update inputs.
- **FR-015**: System MUST preserve a clear distinction between validation failures, access-related failures, unsupported writable-field failures, upstream update failures, and successful playlist-update outcomes.
- **FR-016**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required update inputs, supported writable fields, and unsupported update boundaries for this wrapper.
- **FR-017**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-138.
- **FR-018**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-019**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, required identifier and update inputs, and writable-field boundaries for `playlists.update`.

### Key Entities *(include if feature involves data)*

- **Playlists Update Wrapper Contract**: The maintainer-facing definition of the internal `playlists.update` wrapper, including endpoint identity, quota cost, OAuth requirement, required update inputs, and writable-field boundaries.
- **Playlist Update Request**: The input contract that combines the required playlist identifier, writable part selection, and supported playlist update data plus any explicitly supported optional update modifiers.
- **Writable Playlist Field Set**: The subset of playlist fields that this wrapper permits callers to update for this slice, along with the validation rules that govern supported combinations.
- **Playlist Update Result**: The normalized update outcome containing the updated playlist data and enough request context for downstream layers to interpret what changed.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `playlists.update`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported update behavior for this slice centers on a required playlist identifier, a required writable part selection, and a supported subset of writable playlist fields supplied on an authorized request.
- Optional update modifiers are in scope only when the wrapper explicitly documents them as supported; otherwise they remain outside the wrapper boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on playlist ownership, resource availability, visibility policy, metadata validity, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth expectations, endpoint identity, and writable-field guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlists.update` wrapper artifacts produced by this feature display the official quota-unit cost of `50` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `playlists.update` requires authorized access, which update inputs are mandatory, and what writable-field requests fall outside the wrapper contract by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `playlists.update` patterns for this slice are represented by at least one passing successful update scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing identifiers, missing writable update data, unsupported writable fields, inconsistent writable-part selections, or missing OAuth-backed access fail with explicit normalized outcomes distinct from upstream update failures and successful update results.
