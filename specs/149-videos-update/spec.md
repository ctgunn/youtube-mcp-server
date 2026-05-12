# Feature Specification: Layer 1 Videos Update Wrapper

**Feature Branch**: `149-videos-update`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-149, as outlined in requirements/spec-kit-seed.md. Use '149' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update an Existing Video Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit an authorized video-update request through a typed internal `videos.update` capability so downstream workflows can change supported video metadata without assembling raw upstream update behavior by hand.

**Why this priority**: The core value of YT-149 is a dependable Layer 1 wrapper for `videos.update`. Without a reusable update path, later moderation, publishing, and curation workflows cannot build on a shared contract for changing existing video resources.

**Independent Test**: Can be fully tested by submitting one valid authorized `videos.update` request with the required video identifier, writable part selection, and supported writable video data, then confirming the wrapper returns a normalized updated-video result.

**Acceptance Scenarios**:

1. **Given** a caller provides an authorized request with the required video identifier, writable part selection, and supported writable video data, **When** the caller invokes the `videos.update` capability, **Then** the system updates the video and returns the updated video resource in the Layer 1 result shape.
2. **Given** a caller submits a valid video update request for supported writable metadata only, **When** the request succeeds, **Then** the successful result preserves enough request context for downstream layers to identify the updated video and the update inputs that were applied.

---

### User Story 2 - Review Writable-Part and Authorization Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `videos.update` wrapper contract and understand its quota cost, OAuth requirement, and writable-part expectations before composing it into another workflow.

**Why this priority**: The seed explicitly requires the 50-unit quota cost and writable-part requirements to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly tell what an authorized update request must contain or which video resource parts are writable in this slice.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required update inputs, writable-part boundaries, and unsupported-request guidance in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `videos.update` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose video updates into another workflow, **When** the author reviews the same contract, **Then** the author can determine that authorized access is required, which update inputs are mandatory, and which writable video parts are supported for this slice.

---

### User Story 3 - Reject Invalid or Unauthorized Video-Update Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid video-update requests from requests that omit required update inputs, attempt unsupported writable changes, or lack authorization so calling workflows can correct the request instead of misinterpreting failures.

**Why this priority**: Video updates are mutation-oriented and can change live metadata on an existing resource. Higher layers need clear failure boundaries so they can fix invalid requests, supply the missing authorization context, or surface a true upstream rejection appropriately.

**Independent Test**: Can be fully tested by submitting requests with missing identifiers, missing writable update data, unsupported writable parts, missing OAuth-backed access, and authorized update requests that receive upstream rejection, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `videos.update` request without the required video identifier or writable update data, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement or relies on writable parts outside the supported contract, **When** the request is evaluated, **Then** the system clearly flags the request as unauthorized or unsupported instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller provides a video identifier but no writable fields that would change the existing video?
- How does the system respond when the request attempts to update video fields that the wrapper contract does not support for this slice?
- What happens when a caller selects writable parts that do not align with the fields present in the provided video-update body?
- What happens when a caller submits a validly shaped authorized request for a video that no longer exists or is no longer writable by the caller?
- How does the system preserve enough update context in a successful result for downstream layers to identify which video changed and which writable inputs were applied?
- How does the system distinguish validation failures, authorization failures, unsupported writable-part requests, upstream update failures, and successful video-update outcomes?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `videos.update` behavior using a representative authorized request that includes the required video identifier, writable part selection, and supported update data.
- **Red**: Add failing tests for missing identifiers, missing writable update data, unsupported writable parts, inconsistent writable-part selections, missing OAuth-backed access, and authorized requests that receive an upstream update failure.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `videos.update` wrapper to accept supported update inputs, enforce the OAuth requirement, and return normalized update results.
- **Green**: Add only the metadata and documentation support required to make quota cost, OAuth expectations, required update inputs, supported writable parts, and unsupported update boundaries reviewable and testable.
- **Refactor**: Consolidate shared mutation-wrapper writable-part validation and OAuth documentation patterns with neighboring Layer 1 insert and update wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, writable-part boundary enforcement, OAuth enforcement, and metadata completeness; integration tests for representative video updates and normalized mutation responses; and contract tests for quota, OAuth expectations, and maintainer-facing update guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, required identifier and update inputs, authorization requirement, and unsupported writable-part boundaries.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete update guidance, the passing targeted coverage for YT-149, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `videos.update` update operation.
- **FR-002**: System MUST identify the wrapper as representing the `videos` resource and the `update` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `PUT /videos` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `videos.update` request contract, including the required video identifier, writable part selection, and supported writable video data for a valid update request.
- **FR-006**: System MUST document the required update inputs, including the role of `part`, the required identifying information, and the supported writable video fields, in maintainer-facing artifacts.
- **FR-007**: System MUST record that `videos.update` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document the supported writable-part boundary for `videos.update`, including which video resource parts are accepted for this slice and which update requests fall outside the wrapper contract.
- **FR-009**: System MUST reject or clearly flag `videos.update` requests that omit the required video identifier.
- **FR-010**: System MUST reject or clearly flag `videos.update` requests that omit the required writable update data.
- **FR-011**: System MUST reject or clearly flag requests whose writable part selection or writable video fields do not satisfy the documented supported contract.
- **FR-012**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `videos.update`.
- **FR-013**: System MUST return a normalized video update result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-014**: System MUST preserve enough request context in successful results for downstream layers to identify the updated video and the originating update inputs.
- **FR-015**: System MUST preserve a clear distinction between validation failures, access-related failures, unsupported writable-part failures, upstream update failures, and successful video-update outcomes.
- **FR-016**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required update inputs, supported writable parts, and unsupported update boundaries for this wrapper.
- **FR-017**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-149.
- **FR-018**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-019**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, required identifier and update inputs, and writable-part boundaries for `videos.update`.

### Key Entities *(include if feature involves data)*

- **Videos Update Wrapper Contract**: The maintainer-facing definition of the internal `videos.update` wrapper, including endpoint identity, quota cost, OAuth requirement, required update inputs, and writable-part boundaries.
- **Video Update Request**: The input contract that combines the required video identifier, writable part selection, and supported video update data plus any explicitly supported optional update modifiers.
- **Writable Video Part Set**: The subset of video resource parts that this wrapper permits callers to update for this slice, along with the validation rules that govern supported combinations.
- **Video Update Result**: The normalized update outcome containing the updated video data and enough request context for downstream layers to interpret what changed.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `videos.update`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported update behavior for this slice centers on a required video identifier, a required writable part selection, and a supported subset of writable video fields supplied on an authorized request.
- Optional update modifiers are in scope only when the wrapper explicitly documents them as supported; otherwise they remain outside the wrapper boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on ownership, resource availability, policy, metadata validity, or other video-specific constraints, and that outcome should remain distinct from local validation failures.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth expectations, endpoint identity, and writable-part guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `videos.update` wrapper artifacts produced by this feature display the official quota-unit cost of `50` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `videos.update` requires authorized access, which update inputs are mandatory, and what writable-part requests fall outside the wrapper contract by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `videos.update` patterns for this slice are represented by at least one passing successful update scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing identifiers, missing writable update data, unsupported writable parts, inconsistent writable-part selections, or missing OAuth-backed access fail with explicit normalized outcomes distinct from upstream update failures and successful update results.
