# Feature Specification: YT-103 Layer 1 Endpoint `activities.list`

**Feature Branch**: `103-activities-list`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-103, as outlined in requirements/spec-kit-seed.md. Use 103 as the next branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Channel Activity Through a Typed Wrapper (Priority: P1)

A maintainer can use a Layer 1 `activities.list` wrapper to retrieve recent activity for a channel through one typed integration method instead of assembling a raw upstream request by hand.

**Why this priority**: YT-103 is the first endpoint-specific Layer 1 slice for the activities resource. The core value is making `activities.list` available as a reusable internal capability that later layers can depend on safely and consistently.

**Independent Test**: Can be fully tested by invoking the `activities.list` wrapper with a supported channel-based filter and confirming the wrapper exposes a typed request contract, returns the upstream activity payload shape expected by internal consumers, and includes the required endpoint metadata.

**Acceptance Scenarios**:

1. **Given** a maintainer needs recent activity for a specific channel, **When** they call the Layer 1 `activities.list` wrapper with a supported channel-based filter, **Then** the wrapper retrieves activity through one typed method contract without requiring raw request assembly.
2. **Given** a reviewer inspects the wrapper contract for `activities.list`, **When** they read the wrapper-facing metadata and documentation, **Then** they can see the upstream endpoint identity, quota-unit cost, and the supported ways to filter requests.

---

### User Story 2 - Understand Authentication Rules Before Reuse (Priority: P2)

A Layer 2 or Layer 3 author can determine when `activities.list` is usable with standard public access and when it depends on authorized user context before composing the wrapper into a higher-level workflow.

**Why this priority**: This endpoint supports different access patterns depending on the selected filter. Reuse becomes risky if higher-layer authors cannot tell which requests are broadly accessible and which require user authorization.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it distinguishes publicly accessible channel-based access from authorized user activity views, with enough clarity for a higher-layer author to choose the correct usage path.

**Acceptance Scenarios**:

1. **Given** a higher-layer author wants channel activity for a public channel, **When** they review the `activities.list` wrapper contract, **Then** they can tell that channel-based retrieval is supported without relying on user-owned activity filters.
2. **Given** a higher-layer author wants an authenticated user's own or home activity feed, **When** they review the same wrapper contract, **Then** they can tell that those filters require authorized user context and are not interchangeable with public channel access.

---

### User Story 3 - Review Endpoint Readiness for Follow-on Tooling (Priority: P3)

A maintainer or reviewer can confirm the `activities.list` wrapper is ready to support follow-on Layer 2 and Layer 3 work because the wrapper contract captures quota, authentication behavior, and supported filter boundaries in one reviewable place.

**Why this priority**: Endpoint-specific Layer 1 slices need to be trustworthy building blocks. Reviewers need a fast way to confirm that this slice is complete enough for later activities-based tools.

**Independent Test**: Can be fully tested by reviewing the wrapper specification and representative artifacts for `activities.list` and confirming the endpoint contract is complete without referring back to external documentation.

**Acceptance Scenarios**:

1. **Given** a reviewer evaluates YT-103 for completeness, **When** they inspect the wrapper contract, **Then** they can confirm the quota-unit cost of `1` and the supported authentication modes from the feature artifacts alone.
2. **Given** a future tool author plans to reuse `activities.list`, **When** they inspect the wrapper contract, **Then** they can identify which request filters are supported in scope and which combinations are outside the intended contract.

---

### Edge Cases

- What happens when a caller provides more than one mutually exclusive activity filter in the same request?
- How does the wrapper respond when a caller chooses a filter that requires authorized user context but no eligible user authorization is available?
- What happens when a caller requests activity for a channel that exists but has no recent activity items to return?
- How is the contract handled when a filter or usage mode is documented upstream but intentionally excluded from the supported wrapper scope for this slice?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests showing that `activities.list` is incomplete unless it exposes a typed wrapper contract, records the upstream endpoint identity, shows the quota-unit cost of `1`, and documents supported authentication and filter behavior.
- **Red**: Add failing tests that prove the wrapper must distinguish publicly accessible channel-based retrieval from authorized user activity views so higher-layer consumers cannot mistake one access mode for the other.
- **Green**: Implement the smallest endpoint-specific Layer 1 behavior needed for a representative `activities.list` wrapper to accept supported request inputs, surface the expected internal response shape, and expose maintainer-visible quota and auth guidance.
- **Green**: Add only the minimum validation and documentation support required to reject unsupported filter combinations and to make the supported filter boundary reviewable.
- **Refactor**: Simplify wrapper-facing naming, consolidate repeated request-shaping rules, and tighten maintainer documentation after the first passing tests while preserving the documented `activities.list` contract.
- **Refactor**: Run the full repository verification before review: `cd src && pytest` and `ruff check .`, with pull request evidence showing both commands completed successfully.
- Required test levels: unit tests for wrapper input and metadata rules, integration tests for representative authorized and non-authorized request paths, and contract tests for maintainer-visible filter and authentication guidance.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, and any authentication or filter constraints relevant to maintainers.
- Pull request evidence must show the initial failing coverage for missing wrapper metadata or unsupported filter handling, the passing targeted coverage for YT-103, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube Data API `activities.list` endpoint.
- **FR-002**: System MUST identify the wrapper as representing the `activities` resource and the `list` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `GET /activities` path shape and the official quota-unit cost of `1` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `1` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST document the supported request filters for this wrapper, including which filters are available for public channel-based retrieval and which filters require authorized user context.
- **FR-006**: System MUST distinguish between publicly accessible and authorized-user-only `activities.list` usage modes in the wrapper contract so higher-layer consumers can choose the correct access path.
- **FR-007**: System MUST reject or clearly flag request combinations that fall outside the supported filter rules for this wrapper.
- **FR-008**: System MUST surface empty-result outcomes for valid `activities.list` requests without treating the absence of activity items as a wrapper failure.
- **FR-009**: System MUST expose enough maintainer-facing contract detail for Layer 2 and Layer 3 authors to reuse `activities.list` without consulting raw upstream request semantics first.
- **FR-010**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-103.
- **FR-011**: System MUST preserve alignment with the shared Layer 1 metadata and signature standards established for earlier Layer 1 slices.
- **FR-012**: System MUST enable reviewers to verify, from feature artifacts alone, that `activities.list` has a complete wrapper contract covering endpoint identity, quota, authentication behavior, and supported filter boundaries.

### Key Entities *(include if feature involves data)*

- **Activity List Wrapper Contract**: The maintainer-facing definition of the internal `activities.list` wrapper, including endpoint identity, quota cost, authentication expectations, and supported filter behavior.
- **Activity Filter Mode**: A declared request-selection mode that determines whether activity retrieval is based on a public channel context or an authorized user context.
- **Authorization Expectation**: The rule that tells maintainers whether a given `activities.list` usage path is available through standard public access or requires an authorized user identity.
- **Activity Collection Result**: The returned set of activity items or empty-result outcome produced by a valid `activities.list` request.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `activities.list`; any public-facing Layer 2 exposure is addressed separately in YT-203.
- Representative coverage of the documented `activities.list` access patterns is sufficient for this slice as long as the wrapper clearly identifies which filter modes are supported and which are out of scope.
- The most important reuse decision for this endpoint is whether a caller needs public channel activity or an authorized user activity view, so the spec prioritizes those boundaries over exhaustive enumeration of every optional request field.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `activities.list` wrapper artifacts produced by this feature display the official quota-unit cost of `1` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute whether a planned `activities.list` call uses public channel access or requires authorized user context by reading the wrapper contract alone.
- **SC-003**: 100% of representative invalid filter combinations covered by this feature are rejected or clearly flagged before they can be treated as supported wrapper usage.
- **SC-004**: A reviewer can confirm the endpoint identity, quota behavior, authentication rules, and supported filter boundaries for `activities.list` in a single review pass without consulting external references.
