# Feature Specification: YT-105 Layer 1 Endpoint `captions.insert`

**Feature Branch**: `105-captions-insert`  
**Created**: 2026-04-06  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and understand its goals for context. Then, work on the requirements for YT-105, as outlined in requirements/spec-kit-seed.md. Use 105 as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Caption Track Through a Typed Wrapper (Priority: P1)

A maintainer can create a new YouTube caption track through one typed Layer 1 `captions.insert` wrapper instead of assembling a raw caption-creation request and upload workflow by hand.

**Why this priority**: The core value of YT-105 is enabling an internal caption-creation capability that later Layer 2 and Layer 3 workflows can reuse safely. Without a typed creation path, follow-on caption-management work cannot rely on a consistent internal contract.

**Independent Test**: Can be fully tested by invoking the `captions.insert` wrapper with valid caption metadata and a supported caption media input, then confirming the wrapper exposes a typed request contract, creates the caption-track resource shape expected by internal consumers, and surfaces the required endpoint metadata.

**Acceptance Scenarios**:

1. **Given** a maintainer needs to add a new caption track to a video, **When** they call the Layer 1 `captions.insert` wrapper with the required caption metadata and media-upload input, **Then** the wrapper creates the caption track through one typed contract without requiring raw upstream request assembly.
2. **Given** a reviewer inspects the `captions.insert` wrapper contract, **When** they read the wrapper-facing metadata and documentation, **Then** they can see the endpoint identity, the upload-oriented request boundary, and the official quota-unit cost.

---

### User Story 2 - Understand Authorization and Upload Preconditions Before Reuse (Priority: P2)

A Layer 2 or Layer 3 author can tell that `captions.insert` requires authorized access and a media-upload-capable request, so they do not attempt to compose the wrapper into unsupported public or metadata-only flows.

**Why this priority**: Caption creation is both permission-sensitive and upload-sensitive. Reuse becomes risky if higher-layer authors mistake this endpoint for a lightweight metadata mutation or a publicly callable path.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it states the OAuth requirement, identifies the need for caption media-upload input, and makes any supported delegation context visible enough for a higher-layer author to choose the correct usage path.

**Acceptance Scenarios**:

1. **Given** a higher-layer author wants to automate caption creation, **When** they review the `captions.insert` wrapper contract, **Then** they can tell that the request requires authorized access rather than standard public endpoint use.
2. **Given** a higher-layer author reviews the same contract, **When** they assess the required inputs, **Then** they can determine that caption metadata alone is insufficient and that supported media-upload input is part of the valid request shape.

---

### User Story 3 - Review Caption-Creation Readiness for Follow-on Work (Priority: P3)

A maintainer or reviewer can confirm the `captions.insert` wrapper is ready to support later caption-management tooling because the wrapper contract captures creation boundaries, quota impact, authorization rules, and upload expectations in one reviewable place.

**Why this priority**: This endpoint has one of the highest quota costs in the planned YouTube integration surface and introduces upload semantics that future tools must respect. Reviewers need a fast way to confirm the slice is complete enough to serve as a trusted building block.

**Independent Test**: Can be fully tested by reviewing the wrapper specification and representative artifacts for `captions.insert` and confirming the endpoint contract is complete without referring back to external documentation.

**Acceptance Scenarios**:

1. **Given** a reviewer evaluates YT-105 for completeness, **When** they inspect the wrapper contract, **Then** they can confirm the quota-unit cost of `400`, the required authorization behavior, and the media-upload requirement from the feature artifacts alone.
2. **Given** a future tool author plans to reuse `captions.insert`, **When** they inspect the wrapper contract, **Then** they can identify the supported creation inputs, any supported delegation context, and the request boundaries that are out of scope for this slice.

### Edge Cases

- What happens when a caller provides caption metadata but omits the media-upload input needed to create the caption track?
- How does the wrapper respond when a caller attempts `captions.insert` without eligible authorized access for the target video?
- What happens when the caption media input is present but the request is missing required caption-creation metadata?
- How is the contract handled when a caller supplies delegated content-owner context that does not match the authorized creation context?
- What happens when a valid creation request targets a video or caption state that cannot accept the submitted caption track?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests showing that `captions.insert` is incomplete unless it exposes a typed wrapper contract, records the upstream endpoint identity, shows the quota-unit cost of `400`, and documents the required OAuth and media-upload expectations.
- **Red**: Add failing tests that prove the wrapper must define a valid creation request boundary, including the minimum caption metadata and media-upload inputs, and must not allow unsupported metadata-only or unauthorized creation flows to be treated as supported usage.
- **Green**: Implement the smallest endpoint-specific Layer 1 behavior needed for a representative `captions.insert` wrapper to accept supported creation inputs, surface the expected created-caption resource shape, and expose maintainer-visible quota, auth, and upload guidance.
- **Green**: Add only the minimum validation and documentation support required to make the supported creation inputs, authorization requirement, and delegation notes reviewable.
- **Refactor**: Simplify wrapper-facing naming, consolidate repeated upload-validation rules, and tighten maintainer documentation after the first passing tests while preserving the documented `captions.insert` contract.
- **Refactor**: Run the full repository verification before review: `cd src && pytest` and `ruff check .`, with pull request evidence showing both commands completed successfully.
- Required test levels: unit tests for wrapper input and metadata rules, integration tests for representative authorized caption-creation request paths, and contract tests for maintainer-visible authorization, upload, and request-boundary guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any authorization, media-upload, or delegation constraints relevant to maintainers.
- Pull request evidence must show the initial failing coverage for missing wrapper metadata or unsupported creation handling, the passing targeted coverage for YT-105, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube Data API `captions.insert` endpoint.
- **FR-002**: System MUST identify the wrapper as representing the `captions` resource and the `insert` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `POST /captions` path shape and the official quota-unit cost of `400` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `400` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the minimum supported caption-creation request contract, including the required caption metadata and the required media-upload input for a valid `captions.insert` request.
- **FR-006**: System MUST state that `captions.insert` requires authorized access and MUST make that authorization expectation visible to higher-layer consumers before they reuse the wrapper.
- **FR-007**: System MUST reject or clearly flag caption-creation requests that provide metadata without the required media-upload input.
- **FR-008**: System MUST reject or clearly flag caption-creation requests that provide media-upload input without the required caption metadata.
- **FR-009**: System MUST document any supported content-owner delegation context for `captions.insert` so maintainers can tell when delegated access may be applied.
- **FR-010**: System MUST return a created caption-resource result shape for valid `captions.insert` requests so higher layers can consume the outcome without reverse-engineering the creation response.
- **FR-011**: System MUST expose enough maintainer-facing contract detail for Layer 2 and Layer 3 authors to reuse `captions.insert` without consulting raw upstream creation semantics first.
- **FR-012**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-105.
- **FR-013**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-014**: System MUST enable reviewers to verify, from feature artifacts alone, that `captions.insert` has a complete wrapper contract covering endpoint identity, quota, authorization behavior, media-upload requirements, supported request boundaries, and delegation notes.

### Key Entities *(include if feature involves data)*

- **Caption Insert Wrapper Contract**: The maintainer-facing definition of the internal `captions.insert` wrapper, including endpoint identity, quota cost, authorization expectations, upload requirements, supported request boundaries, and delegation notes.
- **Caption Creation Request**: The input contract that combines the minimum caption metadata and media-upload content needed to create a caption track.
- **Authorization Expectation**: The rule that tells maintainers that `captions.insert` requires authorized access and whether delegated content-owner context is supported.
- **Created Caption Resource**: The returned caption-track resource produced by a valid `captions.insert` request.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `captions.insert`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Representative coverage of the documented caption-creation path is sufficient for this slice as long as the wrapper clearly identifies the supported metadata and media-upload inputs and flags unsupported creation shapes.
- The most important reuse decisions for this endpoint are whether the caller has the authorized access needed to create the caption track and whether they can supply the required upload input, so the spec prioritizes explicit authorization and upload guidance over exhaustive enumeration of every optional request field.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions.insert` wrapper artifacts produced by this feature display the official quota-unit cost of `400` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `captions.insert` requires authorized access and media-upload-capable input by reading the wrapper contract alone.
- **SC-003**: 100% of representative invalid creation requests covered by this feature that omit required metadata or media-upload input are rejected or clearly flagged before they can be treated as supported wrapper usage.
- **SC-004**: A reviewer can confirm the endpoint identity, quota behavior, authorization rules, upload requirements, supported request boundaries, and delegation guidance for `captions.insert` in a single review pass without consulting external references.
