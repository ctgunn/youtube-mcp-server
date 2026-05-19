# Feature Specification: Layer 1 Watermarks Unset Wrapper

**Feature Branch**: `155-watermarks-unset-wrapper`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on YT-155, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remove a Channel Watermark Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can submit authorized channel context through a typed internal `watermarks.unset` capability so higher layers can remove channel branding without hand-assembling the upstream unset request.

**Why this priority**: The core value of YT-155 is a dependable Layer 1 wrapper for the `watermarks.unset` operation. Removing a watermark is write-oriented, authorization-sensitive, and quota-bearing, so downstream workflows need one shared contract that preserves required channel context, access expectations, and normalized outcomes.

**Independent Test**: Can be fully tested by submitting one valid authorized watermark-unset request with supported channel context, then confirming the wrapper returns a normalized successful watermark removal result.

**Acceptance Scenarios**:

1. **Given** a caller provides an authorized request with supported channel context, **When** the caller invokes the `watermarks.unset` capability, **Then** the system removes the channel watermark and returns a normalized successful outcome.
2. **Given** a valid watermark-unset request succeeds, **When** the result is returned, **Then** the result preserves enough request context for downstream layers to identify the affected channel context whose watermark was removed.

---

### User Story 2 - Review Quota and OAuth Expectations Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `watermarks.unset` wrapper contract and understand its quota cost, OAuth requirement, supported channel context, and unsupported-request boundaries before composing it into another workflow.

**Why this priority**: The seed explicitly requires the 50-unit quota cost and OAuth requirements to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly determine which channel inputs are mandatory, what access mode is required, and which request shapes are outside this slice.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, authorization requirement, required channel context, absence of upload input requirements, and unsupported-request boundaries in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `watermarks.unset` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 50 units is visible and consistent.
2. **Given** a higher-layer author evaluates whether the wrapper is safe to reuse, **When** the author reviews the same contract, **Then** the author can determine that OAuth-backed access is required, which channel context must be supplied, that no watermark media upload is required, and which request shapes fall outside the supported boundary.

---

### User Story 3 - Reject Invalid or Under-Authorized Removal Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid watermark-unset requests from requests that omit required channel details, include unsupported watermark-setting payloads, or lack required authorization so calling workflows can correct the request before treating the outcome as an upstream fault.

**Why this priority**: Watermark removal affects channel branding and consumes quota. Higher layers need clear validation and authorization outcomes so malformed or under-authorized requests are not confused with successful removals or ambiguous upstream failures.

**Independent Test**: Can be fully tested by submitting requests with missing channel context, unsupported extra watermark or upload payloads, missing OAuth-backed access, and validly shaped requests that receive upstream refusals, then verifying the outcomes remain distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `watermarks.unset` request without required channel context, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation outcome.
2. **Given** a caller submits a request that does not satisfy the documented OAuth requirement, targets channel context the caller cannot administer, or includes watermark-setting payloads outside the unset contract, **When** the request is evaluated or executed, **Then** the system clearly flags the outcome as unauthorized, invalid, unsupported, or upstream-rejected instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller omits channel context or provides ambiguous channel context?
- How does the system respond when the authorized caller cannot administer the targeted channel context?
- How does the system respond when a caller includes watermark metadata or upload content that belongs to setting a watermark rather than unsetting one?
- What happens when the target channel has no current watermark or the upstream service reports that no removal is possible?
- How does the system distinguish local validation failures, authorization failures, unsupported request payloads, channel-context failures, upstream watermark-removal refusals, and successful watermark removals?
- How does the system preserve enough result context for downstream layers to identify the removal outcome without exposing OAuth credentials, tokens, or other sensitive authorization material?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `watermarks.unset` behavior using a representative authorized request that includes supported channel context.
- **Red**: Add failing tests for missing channel context, ambiguous channel context, unsupported watermark-setting or upload payloads, missing OAuth-backed access, and authorized requests that receive an upstream watermark-removal refusal.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `watermarks.unset` wrapper to accept supported channel input, enforce the OAuth requirement, submit the watermark-unset request, and return a normalized successful result.
- **Green**: Add only the metadata and documentation support required to make endpoint identity, quota cost, OAuth expectations, required channel input, absence of upload input, and unsupported request shapes reviewable and testable.
- **Refactor**: Consolidate shared mutation result shaping, OAuth documentation patterns, and quota metadata patterns with neighboring Layer 1 wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, channel-context boundaries, OAuth enforcement, unsupported-payload handling, result shaping, credential-safe outcomes, and metadata completeness; integration tests for representative successful and failing `watermarks.unset` execution paths; and contract tests for quota visibility, OAuth guidance, and maintainer-facing request-boundary guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, authorization requirement, unsupported request payloads, and normalized outcome semantics for this wrapper.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete wrapper guidance, the passing targeted coverage for YT-155, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `watermarks.unset` operation.
- **FR-002**: System MUST identify the wrapper as representing the `watermarks` resource and the `unset` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /watermarks/unset` path shape and the official quota-unit cost of `50` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `50` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `watermarks.unset` request contract, including the channel context required for a watermark removal.
- **FR-006**: System MUST document the required channel context for watermark removal in maintainer-facing artifacts.
- **FR-007**: System MUST record that `watermarks.unset` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-008**: System MUST document that `watermarks.unset` does not require media-upload content and MUST identify watermark-setting payloads as outside the supported unset request contract.
- **FR-009**: System MUST reject or clearly flag `watermarks.unset` requests that omit required channel context when the request cannot otherwise identify an authorized target channel.
- **FR-010**: System MUST reject or clearly flag `watermarks.unset` requests whose channel context is ambiguous, malformed, or outside the documented supported contract.
- **FR-011**: System MUST reject or clearly flag requests that include watermark metadata or upload payloads outside the documented `watermarks.unset` contract.
- **FR-012**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `watermarks.unset`.
- **FR-013**: System MUST reject or clearly flag requests that target channel context whose watermark cannot be removed when that outcome is determinable from local validation or normalized upstream feedback.
- **FR-014**: System MUST return a normalized watermark-removal result for valid authorized requests so higher layers can consume successful outcomes without reverse-engineering upstream behavior.
- **FR-015**: System MUST preserve enough request context in successful results for downstream layers to identify which channel context had its watermark removed.
- **FR-016**: System MUST avoid exposing OAuth credentials, tokens, or other sensitive authorization material in successful or failed watermark outcomes.
- **FR-017**: System MUST preserve a clear distinction between validation failures, access-related failures, unsupported request payloads, channel-context failures, upstream watermark-removal refusals, no-removal-possible outcomes, and successful watermark-removal outcomes.
- **FR-018**: System MUST expose maintainer-facing contract detail describing the quota cost, OAuth requirement, required channel input, unsupported request boundaries, and absence of media-upload input for this wrapper.
- **FR-019**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-155.
- **FR-020**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-021**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, no-upload boundary, channel-context boundaries, and outcome classifications for `watermarks.unset`.

### Key Entities *(include if feature involves data)*

- **Watermarks Unset Wrapper Contract**: The maintainer-facing definition of the internal `watermarks.unset` wrapper, including endpoint identity, quota cost, OAuth requirement, supported channel context, no-upload boundary, unsupported-request boundaries, and expected outcome classifications.
- **Watermark Unset Request**: The typed input contract that carries channel context and any explicitly supported optional request context for one watermark-removal attempt.
- **Watermark Removal Result**: The normalized mutation outcome that confirms whether a supported authorized request removed the watermark and preserves enough request context for downstream interpretation.
- **Watermark Removal Outcome Classification**: The set of distinct outcome states that separate invalid requests, unsupported payloads, missing authorization, channel-context failures, upstream refusals, no-removal-possible outcomes, and successful watermark removals.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `watermarks.unset`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported behavior for this slice centers on one authorized watermark-unset attempt that includes enough channel context to identify the target channel.
- Watermark media upload content and watermark placement metadata are outside this unset wrapper's supported request contract.
- A validly shaped authorized request can still receive an upstream rejection based on channel ownership, permissions, branding eligibility, policy state, resource availability, or current watermark state, and that outcome should remain distinct from local validation failures.
- Successful watermark-unset behavior for this slice is represented as a normalized mutation outcome rather than as a requirement to fetch and return full channel branding state.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, access expectation, endpoint identity, and request-boundary guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `watermarks.unset` wrapper artifacts produced by this feature display the official quota-unit cost of `50` and the OAuth requirement in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which channel context, unsupported request boundaries, no-upload boundary, and access mode apply by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `watermarks.unset` request patterns for this slice are represented by at least one passing successful watermark-removal scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing required channel context, unsupported watermark-setting payloads, missing required access context, target channels that cannot be updated, or no-removal-possible outcomes fail or resolve with explicit normalized outcomes distinct from upstream refusal outcomes and successful watermark-removal results.
- **SC-005**: Reviewers can verify the endpoint identity, quota behavior, OAuth requirement, no-upload boundary, channel-context boundaries, request boundaries, and outcome classifications from feature artifacts without needing additional undocumented project knowledge.
