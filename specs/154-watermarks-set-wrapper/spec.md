# Feature Specification: Layer 1 Watermarks Set Wrapper

**Feature Branch**: `154-watermarks-set-wrapper`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on YT-154, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set a Channel Watermark Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit authorized channel watermark placement details and supported media-upload content through a typed internal `watermarks.set` capability so higher layers can apply channel branding without hand-assembling the upstream upload request.

**Why this priority**: The core value of YT-154 is a dependable Layer 1 wrapper for the `watermarks.set` operation. Setting a watermark is write-oriented, upload-sensitive, authorization-sensitive, and quota-bearing, so downstream workflows need one shared contract that preserves required branding inputs, access expectations, and normalized outcomes.

**Independent Test**: Can be fully tested by submitting one valid authorized watermark-set request with supported channel context, placement metadata, and media-upload content, then confirming the wrapper returns a normalized successful watermark update result.

**Acceptance Scenarios**:

1. **Given** a caller provides an authorized request with supported channel context, watermark placement metadata, and upload content, **When** the caller invokes the `watermarks.set` capability, **Then** the system sets the channel watermark and returns a normalized successful outcome.
2. **Given** a valid watermark-set request succeeds, **When** the result is returned, **Then** the result preserves enough request context for downstream layers to identify the affected channel context and watermark placement that was acknowledged.

---

### User Story 2 - Review Quota, OAuth, and Upload Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `watermarks.set` wrapper contract and understand its quota cost, OAuth requirement, supported channel context, watermark placement metadata, and media-upload expectations before composing it into another workflow.

**Why this priority**: The seed explicitly requires the 50-unit quota cost plus media-upload and OAuth requirements to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly determine which branding inputs are mandatory, which upload shapes are supported, and what access mode is required.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required watermark metadata, required upload input, supported channel context, and unsupported-request boundaries in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `watermarks.set` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author evaluates whether the wrapper is safe to reuse, **When** the author reviews the same contract, **Then** the author can determine that OAuth-backed access is required, which watermark and upload inputs must be supplied, and which request shapes fall outside the supported boundary.

---

### User Story 3 - Reject Invalid or Under-Authorized Watermark Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid watermark-set requests from requests that omit required channel or watermark details, provide unsupported upload content, or lack required authorization so calling workflows can correct the request before treating the outcome as an upstream fault.

**Why this priority**: Watermark changes affect channel branding and consume quota. Higher layers need clear validation and authorization outcomes so malformed or under-authorized requests are not confused with successful watermark updates or ambiguous upstream failures.

**Independent Test**: Can be fully tested by submitting requests with missing channel context, missing placement metadata, missing upload content, unsupported upload payloads, missing OAuth-backed access, and validly shaped requests that receive upstream refusals, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `watermarks.set` request without required watermark metadata or upload content, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation outcome.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement, targets channel context the caller cannot administer, or includes upload content outside the supported contract, **When** the request is evaluated or executed, **Then** the system clearly flags the outcome as unauthorized, invalid, unsupported, or upstream-rejected instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller provides watermark placement metadata without upload content, or upload content without watermark placement metadata?
- How does the system respond when channel context is omitted, ambiguous, unavailable, or not administrable by the authorized caller?
- How does the system respond when watermark timing, position, or display metadata is missing, internally inconsistent, deprecated, or outside the documented wrapper boundary?
- What happens when the upload payload is present but does not satisfy the documented watermark-upload contract?
- How does the system distinguish local validation failures, authorization failures, unsupported upload payloads, channel-context failures, upstream watermark-update refusals, and successful watermark updates?
- How does the system preserve enough result context for downstream layers to identify the watermark update without exposing OAuth credentials, tokens, or other sensitive authorization material?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `watermarks.set` behavior using a representative authorized request that includes supported channel context, watermark placement metadata, and media-upload payload.
- **Red**: Add failing tests for missing channel context where required, missing watermark placement metadata, missing upload payloads, malformed or unsupported upload content, missing OAuth-backed access, and authorized requests that receive an upstream watermark-update refusal.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `watermarks.set` wrapper to accept supported channel, watermark, and upload inputs, enforce the OAuth requirement, submit the watermark-set request, and return a normalized successful result.
- **Green**: Add only the metadata and documentation support required to make endpoint identity, quota cost, OAuth expectations, required watermark inputs, media-upload expectations, and unsupported request shapes reviewable and testable.
- **Refactor**: Consolidate shared media-upload validation, mutation result shaping, and OAuth documentation patterns with neighboring Layer 1 upload wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, watermark metadata boundaries, upload-contract enforcement, OAuth enforcement, result shaping, credential-safe outcomes, and metadata completeness; integration tests for representative successful and failing `watermarks.set` execution paths; and contract tests for quota visibility, OAuth guidance, and maintainer-facing media-upload guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, required watermark metadata, required upload content, authorization requirement, and normalized outcome semantics for this wrapper.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete wrapper guidance, the passing targeted coverage for YT-154, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `watermarks.set` operation.
- **FR-002**: System MUST identify the wrapper as representing the `watermarks` resource and the `set` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /watermarks/set` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `watermarks.set` request contract, including the channel context required for a watermark update, required watermark placement metadata, and required media-upload payload.
- **FR-006**: System MUST document the required watermark inputs, including channel context, placement and display metadata, and upload content, in maintainer-facing artifacts.
- **FR-007**: System MUST record that `watermarks.set` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document the supported media-upload boundary for `watermarks.set`, including which upload payload shape is expected and which watermark-update requests fall outside the wrapper contract.
- **FR-009**: System MUST reject or clearly flag `watermarks.set` requests that omit required channel context when the request cannot otherwise identify an authorized target channel.
- **FR-010**: System MUST reject or clearly flag `watermarks.set` requests that omit required watermark placement or display metadata.
- **FR-011**: System MUST reject or clearly flag `watermarks.set` requests that omit the required media-upload payload.
- **FR-012**: System MUST reject or clearly flag requests whose channel context, watermark metadata, or upload payload does not satisfy the documented supported contract.
- **FR-013**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `watermarks.set`.
- **FR-014**: System MUST reject or clearly flag requests that target channel context whose watermark cannot be updated when that outcome is determinable from local validation or normalized upstream feedback.
- **FR-015**: System MUST return a normalized watermark-update result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering upstream upload behavior.
- **FR-016**: System MUST preserve enough request context in successful results for downstream layers to identify which channel context and watermark placement were updated.
- **FR-017**: System MUST avoid exposing OAuth credentials, tokens, upload secrets, or other sensitive authorization material in successful or failed watermark outcomes.
- **FR-018**: System MUST preserve a clear distinction between validation failures, access-related failures, unsupported upload requests, channel-context failures, upstream watermark-update refusals, and successful watermark-update outcomes.
- **FR-019**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required watermark inputs, required upload input, and unsupported request boundaries for this wrapper.
- **FR-020**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-154.
- **FR-021**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-022**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, media-upload requirement, watermark metadata boundaries, and outcome classifications for `watermarks.set`.

### Key Entities *(include if feature involves data)*

- **Watermarks Set Wrapper Contract**: The maintainer-facing definition of the internal `watermarks.set` wrapper, including endpoint identity, quota cost, OAuth requirement, supported channel context, watermark metadata, media-upload boundary, unsupported-request boundaries, and expected outcome classifications.
- **Watermark Set Request**: The typed input contract that combines channel context, watermark placement and display metadata, upload content, and any explicitly supported optional request context for one watermark-set attempt.
- **Watermark Upload Payload**: The upload-specific portion of the request that carries the media content needed to set a channel watermark and whose supported shape must be documented and validated.
- **Watermark Update Result**: The normalized mutation outcome that confirms whether a supported authorized request set the watermark and preserves enough request context for downstream interpretation.
- **Watermark Outcome Classification**: The set of distinct outcome states that separate invalid requests, unsupported upload requests, missing authorization, channel-context failures, upstream refusals, and successful watermark updates.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `watermarks.set`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported behavior for this slice centers on one authorized watermark-set attempt that includes enough channel context to identify the target channel, one set of watermark placement metadata, and one media-upload payload.
- Optional watermark placement or upload modifiers are in scope only when the wrapper explicitly documents them as supported; otherwise they remain outside the wrapper boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on channel ownership, permissions, branding eligibility, upload eligibility, policy state, or resource availability, and that outcome should remain distinct from local validation failures.
- Successful watermark-set behavior for this slice is represented as a normalized mutation outcome rather than as a requirement to fetch and return full channel branding state.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, access expectation, endpoint identity, and upload guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `watermarks.set` wrapper artifacts produced by this feature display the official quota-unit cost of `50` and the OAuth requirement in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which channel context, watermark metadata, upload input, unsupported request boundaries, and access mode apply by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `watermarks.set` request patterns for this slice are represented by at least one passing successful watermark-update scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing required watermark inputs, unsupported upload payloads, missing required access context, or target channels that cannot be updated fail with explicit normalized outcomes distinct from upstream refusal outcomes and successful watermark-update results.
- **SC-005**: Reviewers can verify the endpoint identity, quota behavior, OAuth requirement, media-upload requirement, watermark metadata boundaries, request boundaries, and outcome classifications from feature artifacts without needing additional undocumented project knowledge.
