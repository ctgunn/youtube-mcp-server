# Feature Specification: YT-106 Layer 1 Endpoint `captions.update`

**Feature Branch**: `106-captions-update`  
**Created**: 2026-04-06  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and understand its goals for context. Then, work on the requirements for YT-106, as outlined in requirements/spec-kit-seed.md. Use 106 as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update a Caption Track Through a Typed Wrapper (Priority: P1)

A maintainer can update an existing YouTube caption track through one typed Layer 1 `captions.update` wrapper instead of assembling a raw caption-update request and optional upload flow by hand.

**Why this priority**: The core value of YT-106 is enabling safe, reusable caption-track updates for later Layer 2 and Layer 3 tooling. Without a typed update path, higher-level caption-management work cannot rely on a consistent internal contract for changing existing caption resources.

**Independent Test**: Can be fully tested by invoking the `captions.update` wrapper with a valid caption resource update body and any required media-update input, then confirming the wrapper exposes a typed request contract, returns the updated caption resource shape expected by internal consumers, and surfaces the required endpoint metadata.

**Acceptance Scenarios**:

1. **Given** a maintainer needs to revise an existing caption track, **When** they call the Layer 1 `captions.update` wrapper with a valid caption resource update body, **Then** the wrapper updates the caption track through one typed method contract without requiring raw upstream request assembly.
2. **Given** a maintainer needs to replace caption content as part of the update, **When** they call the same wrapper with a valid update body and supported media-update input, **Then** the wrapper treats the request as a valid caption-update path and returns the updated caption resource.

---

### User Story 2 - Understand Authorization and Update Preconditions Before Reuse (Priority: P2)

A Layer 2 or Layer 3 author can tell that `captions.update` requires authorized access and can understand when media-update input is required or supported before composing the wrapper into a higher-level workflow.

**Why this priority**: Caption updates are permission-sensitive and more expensive than caption creation. Reuse becomes risky if higher-layer authors cannot distinguish metadata-only updates from updates that also change the caption file or cannot tell when authorized access is mandatory.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it states the OAuth requirement, identifies the supported update body, documents when media-update input is required or optional, and makes any supported delegation context visible enough for a higher-layer author to choose the correct usage path.

**Acceptance Scenarios**:

1. **Given** a higher-layer author wants to automate caption maintenance, **When** they review the `captions.update` wrapper contract, **Then** they can tell that the request requires authorized access rather than standard public endpoint use.
2. **Given** a higher-layer author needs to change caption metadata, content, or both, **When** they review the same contract, **Then** they can determine which update inputs are required for each supported update path and which request shapes are unsupported.

---

### User Story 3 - Review Caption-Update Readiness for Follow-on Work (Priority: P3)

A maintainer or reviewer can confirm the `captions.update` wrapper is ready to support later caption-management tooling because the wrapper contract captures update boundaries, quota impact, authorization rules, and media-update expectations in one reviewable place.

**Why this priority**: `captions.update` carries one of the highest quota costs in the planned Layer 1 inventory and introduces update-specific boundary decisions that future tools must respect. Reviewers need a fast way to confirm the slice is complete enough to serve as a trusted building block.

**Independent Test**: Can be fully tested by reviewing the wrapper specification and representative artifacts for `captions.update` and confirming the endpoint contract is complete without referring back to external documentation.

**Acceptance Scenarios**:

1. **Given** a reviewer evaluates YT-106 for completeness, **When** they inspect the wrapper contract, **Then** they can confirm the quota-unit cost of `450`, the required authorization behavior, and the supported update-body and media-update expectations from the feature artifacts alone.
2. **Given** a future tool author plans to reuse `captions.update`, **When** they inspect the wrapper contract, **Then** they can identify the supported update inputs, any supported delegation context, and the request boundaries that are out of scope for this slice.

### Edge Cases

- What happens when a caller provides a caption update body that does not identify an existing caption track to update?
- How does the wrapper respond when a caller attempts `captions.update` without eligible authorized access for the target caption track?
- What happens when a caller provides media-update input without the minimum caption resource update body needed to identify the caption being changed?
- What happens when a caller provides an update body that is valid for metadata changes but incompatible with the requested media-update path?
- How is the contract handled when a caller supplies delegated content-owner context that does not match the authorized update context?
- What happens when the target caption track no longer exists or cannot be updated in its current state?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests showing that `captions.update` is incomplete unless it exposes a typed wrapper contract, records the upstream endpoint identity, shows the quota-unit cost of `450`, and documents the required OAuth and media-update expectations.
- **Red**: Add failing tests that prove the wrapper must define valid update boundaries, including the minimum caption resource update body, the supported role of media-update input, and the handling of unsupported or ambiguous update combinations.
- **Green**: Implement the smallest endpoint-specific Layer 1 behavior needed for a representative `captions.update` wrapper to accept supported update inputs, surface the expected updated-caption resource shape, and expose maintainer-visible quota, auth, and update guidance.
- **Green**: Add only the minimum validation and documentation support required to make the supported update-body rules, authorization requirement, and media-update expectations reviewable.
- **Refactor**: Simplify wrapper-facing naming, consolidate repeated update-validation rules, and tighten maintainer documentation after the first passing tests while preserving the documented `captions.update` contract.
- **Refactor**: Run the full repository verification before review: `cd src && pytest` and `ruff check .`, with pull request evidence showing both commands completed successfully.
- Required test levels: unit tests for wrapper input and metadata rules, integration tests for representative authorized caption-update request paths, and contract tests for maintainer-visible authorization, update-boundary, and media-update guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any authorization, media-update, or delegation constraints relevant to maintainers.
- Pull request evidence must show the initial failing coverage for missing wrapper metadata or unsupported update handling, the passing targeted coverage for YT-106, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube Data API `captions.update` endpoint.
- **FR-002**: System MUST identify the wrapper as representing the `captions` resource and the `update` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `PUT /captions` path shape and the official quota-unit cost of `450` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `450` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the minimum supported caption-update request contract, including the caption resource update body needed to identify and change an existing caption track.
- **FR-006**: System MUST document when media-update input is required, optional, or unsupported for the update paths covered by this wrapper contract.
- **FR-007**: System MUST state that `captions.update` requires authorized access and MUST make that authorization expectation visible to higher-layer consumers before they reuse the wrapper.
- **FR-008**: System MUST reject or clearly flag update requests that omit the minimum caption resource body needed to identify the caption track being changed.
- **FR-009**: System MUST reject or clearly flag update requests whose combination of caption resource body and media-update input falls outside the supported update rules for this wrapper.
- **FR-010**: System MUST document any supported content-owner delegation context for `captions.update` so maintainers can tell when delegated access may be applied.
- **FR-011**: System MUST return an updated caption-resource result shape for valid `captions.update` requests so higher layers can consume the outcome without reverse-engineering the update response.
- **FR-012**: System MUST expose enough maintainer-facing contract detail for Layer 2 and Layer 3 authors to reuse `captions.update` without consulting raw upstream update semantics first.
- **FR-013**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-106.
- **FR-014**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-015**: System MUST enable reviewers to verify, from feature artifacts alone, that `captions.update` has a complete wrapper contract covering endpoint identity, quota, authorization behavior, supported update boundaries, media-update expectations, and delegation notes.

### Key Entities *(include if feature involves data)*

- **Caption Update Wrapper Contract**: The maintainer-facing definition of the internal `captions.update` wrapper, including endpoint identity, quota cost, authorization expectations, supported update-body rules, media-update expectations, and delegation notes.
- **Caption Update Request**: The input contract that combines the caption resource update body with any supported media-update content needed to change an existing caption track.
- **Authorization Expectation**: The rule that tells maintainers that `captions.update` requires authorized access and whether delegated content-owner context is supported.
- **Updated Caption Resource**: The returned caption-track resource produced by a valid `captions.update` request.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `captions.update`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Representative coverage of the documented caption-update path is sufficient for this slice as long as the wrapper clearly identifies the supported caption resource body, documents the role of media-update input, and flags unsupported update shapes.
- The most important reuse decisions for this endpoint are whether the caller has the authorized access needed to update the caption track and whether the requested update requires caption media replacement, so the spec prioritizes explicit authorization and update-boundary guidance over exhaustive enumeration of every optional request field.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions.update` wrapper artifacts produced by this feature display the official quota-unit cost of `450` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute that `captions.update` requires authorized access and can identify the supported update path by reading the wrapper contract alone.
- **SC-003**: 100% of representative invalid update requests covered by this feature that omit the minimum caption resource body or use unsupported media-update combinations are rejected or clearly flagged before they can be treated as supported wrapper usage.
- **SC-004**: A reviewer can confirm the endpoint identity, quota behavior, authorization rules, update boundaries, media-update expectations, and delegation guidance for `captions.update` in a single review pass without consulting external references.
