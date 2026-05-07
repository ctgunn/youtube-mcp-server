# Feature Specification: Layer 1 Thumbnails Set Wrapper

**Feature Branch**: `144-thumbnails-set`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-144, as outlined in requirements/spec-kit-seed.md. Use '144' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update a Video Thumbnail Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit a video identifier and thumbnail upload content through a typed internal `thumbnails.set` capability so higher layers can replace a video's custom thumbnail without assembling raw upstream upload behavior by hand.

**Why this priority**: The core value of YT-144 is providing a real Layer 1 thumbnail-update path. Without this wrapper, downstream workflows cannot reuse a stable contract for custom thumbnail changes on managed videos.

**Independent Test**: Can be fully tested by submitting a valid authorized `thumbnails.set` request with one supported video identifier and one supported upload payload, then confirming the wrapper returns a normalized thumbnail-update result.

**Acceptance Scenarios**:

1. **Given** a caller provides a valid video identifier and supported thumbnail upload content on an authorized request, **When** the caller invokes the `thumbnails.set` capability, **Then** the system updates the thumbnail and returns a normalized successful result.
2. **Given** a caller submits a valid thumbnail-update request that succeeds, **When** the result is returned, **Then** the successful outcome preserves enough request context for downstream layers to identify which video thumbnail was changed.

---

### User Story 2 - Review Quota, OAuth, and Upload Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `thumbnails.set` wrapper contract and understand its quota cost, OAuth requirement, and media-upload expectations before composing it into another workflow.

**Why this priority**: The seed explicitly requires the 50-unit quota cost plus media-upload and OAuth requirements to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly tell that this is an authorized upload operation or what a supported thumbnail-update request must contain.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required video identifier, required upload input, and unsupported-request boundaries in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `thumbnails.set` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author wants to compose thumbnail updates into another workflow, **When** the author reviews the same contract, **Then** the author can determine that authorized access is required and which identifier and upload inputs must be supplied for a supported request.

---

### User Story 3 - Reject Invalid or Under-Authorized Thumbnail Uploads Clearly (Priority: P3)

A downstream tool author can distinguish valid thumbnail-update requests from requests that omit the required video identifier, omit upload content, provide unsupported upload content, or lack authorization so calling workflows can correct the request instead of misinterpreting failures.

**Why this priority**: Thumbnail updates are write-oriented and upload-sensitive. Higher layers need clear failure boundaries so they can correct invalid inputs, supply the missing authorization context, or surface a true upstream rejection appropriately.

**Independent Test**: Can be fully tested by submitting requests with missing video identifiers, missing upload content, malformed or unsupported upload payloads, missing OAuth-backed access, and authorized requests that receive an upstream update failure, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `thumbnails.set` request without the required video identifier or upload content, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation outcome.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement, targets a video whose thumbnail cannot be updated, or uses upload content outside the supported contract, **When** the request is evaluated or executed, **Then** the system clearly flags the outcome as unauthorized, invalid, unsupported, or upstream-rejected instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller provides a video identifier without thumbnail upload content, or upload content without a video identifier?
- How does the system respond when the upload payload is present but does not satisfy the documented thumbnail-upload contract?
- What happens when a caller provides an authorized request for a video whose thumbnail cannot be updated because the video is unavailable, not writable by the caller, or otherwise ineligible for the operation?
- How does the system preserve enough update context in a successful result for downstream layers to identify which video thumbnail changed?
- How does the system distinguish validation failures, authorization failures, unsupported upload payloads, target-video failures, and upstream thumbnail-update failures from a successful thumbnail update outcome?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `thumbnails.set` behavior using a representative authorized request that includes the required video identifier and thumbnail upload payload.
- **Red**: Add failing tests for missing video identifiers, missing upload payloads, malformed or unsupported upload content, missing OAuth-backed access, and authorized requests that receive an upstream thumbnail-update failure.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `thumbnails.set` wrapper to accept supported identifier and upload inputs, enforce the OAuth requirement, and return normalized thumbnail-update results.
- **Green**: Add only the metadata and documentation support required to make quota cost, OAuth expectations, required update inputs, and unsupported upload boundaries reviewable and testable.
- **Refactor**: Consolidate shared media-upload validation and OAuth documentation patterns with neighboring Layer 1 upload wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, upload-contract enforcement, OAuth enforcement, target-video eligibility handling, and metadata completeness; integration tests for representative thumbnail updates and normalized mutation responses; and contract tests for quota visibility and maintainer-facing upload guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, required video identifier, required upload content, authorization requirement, and unsupported upload boundaries.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete upload guidance, the passing targeted coverage for YT-144, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `thumbnails.set` update operation.
- **FR-002**: System MUST identify the wrapper as representing the `thumbnails` resource and the `set` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /thumbnails/set` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `thumbnails.set` request contract, including the required video identifier and required media-upload payload for a supported thumbnail update request.
- **FR-006**: System MUST document the required update inputs, including the role of the video identifier and the required thumbnail-upload payload, in maintainer-facing artifacts.
- **FR-007**: System MUST record that `thumbnails.set` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document the supported media-upload boundary for `thumbnails.set`, including which upload payload shape is expected and which thumbnail-update requests fall outside the wrapper contract.
- **FR-009**: System MUST reject or clearly flag `thumbnails.set` requests that omit the required video identifier.
- **FR-010**: System MUST reject or clearly flag `thumbnails.set` requests that omit the required media-upload payload.
- **FR-011**: System MUST reject or clearly flag requests whose video identifier or upload payload does not satisfy the documented supported contract.
- **FR-012**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `thumbnails.set`.
- **FR-013**: System MUST reject or clearly flag requests that target a video whose thumbnail cannot be updated when that outcome is determinable from local validation or normalized upstream feedback.
- **FR-014**: System MUST return a normalized thumbnail-update result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering the upstream response.
- **FR-015**: System MUST preserve enough request context in successful results for downstream layers to identify which video thumbnail was updated and which request inputs produced the change.
- **FR-016**: System MUST preserve a clear distinction between validation failures, access-related failures, unsupported upload requests, target-video failures, upstream thumbnail-update failures, and successful thumbnail-update outcomes.
- **FR-017**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required update inputs, and unsupported upload boundaries for this wrapper.
- **FR-018**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-144.
- **FR-019**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-020**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, required video identifier, required upload content, and unsupported upload boundaries for `thumbnails.set`.

### Key Entities *(include if feature involves data)*

- **Thumbnails Set Wrapper Contract**: The maintainer-facing definition of the internal `thumbnails.set` wrapper, including endpoint identity, quota cost, OAuth requirement, required update inputs, and upload-contract boundaries.
- **Thumbnail Update Request**: The input contract that combines the required video identifier with the required upload content and any explicitly supported optional request context for one thumbnail-update attempt.
- **Thumbnail Upload Payload**: The upload-specific portion of the request that carries the image content needed to update a video's thumbnail and whose supported shape must be documented and validated.
- **Thumbnail Update Result**: The normalized update outcome containing the thumbnail-change result and enough request context for downstream layers to interpret which video was updated.
- **Thumbnail Update Failure Classification**: The set of distinct failure outcomes that separate invalid requests, missing authorization, unsupported upload requests, target-video restrictions, upstream failures, and successful thumbnail updates.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `thumbnails.set`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported behavior for this slice centers on one required `videoId` plus one required media-upload payload supplied on an authorized request, because the seed specifically calls out media-upload and OAuth expectations rather than a broader optional-input surface.
- Optional upload modifiers are in scope only when the wrapper explicitly documents them as supported; otherwise they remain outside the wrapper boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on video ownership, video availability, thumbnail eligibility, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth expectations, endpoint identity, and upload guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `thumbnails.set` wrapper artifacts produced by this feature display the official quota-unit cost of `50` and the wrapper's OAuth expectation guidance in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `thumbnails.set` requires authorized access, which update inputs are mandatory, and what upload requests fall outside the wrapper contract by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `thumbnails.set` request patterns for this slice are represented by at least one passing successful thumbnail-update scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing video identifiers, missing upload content, unsupported payload shapes, missing OAuth-backed access, or target videos that cannot be updated fail with explicit normalized outcomes distinct from upstream thumbnail-update failures and successful update results.
