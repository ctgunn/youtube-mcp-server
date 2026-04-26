# Feature Specification: Layer 1 Playlist Images List Wrapper

**Feature Branch**: `128-playlist-images-list`  
**Created**: 2026-04-24  
**Status**: Draft  
**Input**: User description: "Read the PRD in requirements/PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-128, as outlined in requirements/spec-kit-seed.md. Use '128' as the next feature branch number."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlist Images Through a Reusable Layer 1 Contract (Priority: P1)

A platform developer can request playlist image records through a typed internal `playlistImages.list` capability so downstream tools can inspect playlist image data without assembling a raw upstream request by hand.

**Why this priority**: The core value of YT-128 is exposing a dependable Layer 1 retrieval path for playlist image data. Without this wrapper, later layers have no shared and reviewable way to retrieve playlist images by supported filter mode.

**Independent Test**: Can be fully tested by submitting a valid playlist-image lookup request with one supported filter mode and confirming the wrapper returns a normalized successful result that preserves the selected lookup context.

**Acceptance Scenarios**:

1. **Given** a caller provides the required lookup inputs for one supported playlist-image request, **When** the caller invokes the `playlistImages.list` capability, **Then** the system returns the matching playlist-image data in the Layer 1 result shape.
2. **Given** a caller provides a valid playlist-image request that uses a supported filter mode, **When** the caller invokes the same capability, **Then** the successful result preserves enough request context for downstream layers to understand which playlist-image filter mode was used.

---

### User Story 2 - Review Quota, OAuth Expectations, and Filter Modes Before Reuse (Priority: P2)

A maintainer or higher-layer author can review the `playlistImages.list` contract and understand its quota cost, OAuth requirements, and supported playlist-image filter modes before reusing it in another workflow.

**Why this priority**: The seed requires the 1-unit quota cost plus OAuth and playlist-image filter-mode guidance to be documented in the wrapper contract. Reuse becomes risky if maintainers cannot quickly tell that this endpoint is authorization-gated or which lookup paths the wrapper supports.

**Independent Test**: Can be fully tested by reviewing the wrapper contract and confirming it clearly exposes the quota cost, OAuth requirement, supported lookup inputs, selector-specific paging behavior, and unsupported-request boundaries in maintainer-facing artifacts.

**Acceptance Scenarios**:

1. **Given** a maintainer reviews the `playlistImages.list` wrapper contract, **When** the maintainer inspects the capability metadata and adjacent documentation, **Then** the official quota cost of 1 unit is visible and consistent.
2. **Given** a higher-layer author wants to compose playlist-image retrieval into another workflow, **When** the author reviews the same contract, **Then** the author can determine which supported filter modes are available, that OAuth-backed access is required, and when paging is supported for the selected mode.

---

### User Story 3 - Reject Invalid or Conflicting Playlist Image Requests Clearly (Priority: P3)

A downstream tool author can distinguish valid playlist-image lookups from requests that are missing required filters, combine conflicting filter modes, or rely on unsupported modifiers so calling workflows can correct the request instead of misinterpreting failures.

**Why this priority**: Playlist image retrieval depends on choosing valid filter inputs and understanding which modes are supported by the wrapper. Higher layers need clear failure boundaries so they can fix invalid inputs, remove unsupported modifiers, or treat a valid empty result as a success.

**Independent Test**: Can be fully tested by submitting requests with missing required filters, conflicting filter modes, unsupported paging or modifiers, missing OAuth-backed access, and validly shaped requests that return no playlist images, then verifying the outcomes stay distinct.

**Acceptance Scenarios**:

1. **Given** a caller submits a `playlistImages.list` request without a required supported filter input, **When** the request is evaluated, **Then** the system rejects the request with a clear normalized validation error.
2. **Given** a caller submits a request that combines conflicting filter modes or relies on unsupported modifiers outside the wrapper boundary, **When** the request is evaluated, **Then** the system clearly flags the request as outside the supported contract instead of returning a misleading successful result.

### Edge Cases

- What happens when a caller omits both supported playlist-image filter inputs and submits only `part`?
- How does the system respond when a caller provides both `playlistId` and `id` in the same request if the wrapper supports only one filter mode per request?
- What happens when a caller supplies paging inputs with a selector mode that does not support paging or adds other modifiers that are not explicitly supported by the wrapper contract?
- How does the system preserve the caller's selected playlist-image filter mode in a successful retrieval result?
- What happens when a validly shaped playlist-image request returns no items for the requested filter mode?
- How does the system communicate the endpoint-wide OAuth requirement without forcing maintainers to inspect implementation details?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and integration tests for successful `playlistImages.list` retrieval using each supported filter mode, including one representative `playlistId` lookup and one representative `id` lookup when both modes are in scope.
- **Red**: Add failing tests for missing required filter inputs, conflicting filter modes, unsupported paging or request modifiers, missing OAuth-backed access, and validly shaped requests that return an empty playlist-image result.
- **Green**: Implement the minimum endpoint-specific behavior needed for a representative `playlistImages.list` wrapper to accept supported filter inputs, enforce the OAuth requirement, apply selector-specific paging rules, and return normalized retrieval results.
- **Green**: Add only the metadata and documentation support required to make quota cost, supported filter modes, OAuth expectations, and unsupported-request boundaries reviewable and testable.
- **Refactor**: Consolidate shared list-wrapper filter validation and mixed-access documentation patterns with neighboring Layer 1 wrappers, then run the full repository verification before review: `cd src && pytest` and `ruff check .`.
- Required test levels: unit tests for request validation, filter-mode enforcement, paging rules, and metadata completeness; integration tests for representative playlist-image retrieval and normalized responses; and contract tests for quota, OAuth expectations, and supported-input documentation.
- Every new or changed Python function in scope must include a reStructuredText docstring that explains purpose, inputs, outputs, quota cost, supported playlist-image filter modes, selector-specific paging behavior, and any relevant OAuth constraints.
- Pull request evidence must show the initial failing coverage for missing validation or incomplete filter-mode guidance, the passing targeted coverage for YT-128, and the final full-suite passing result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a typed internal Layer 1 wrapper for the YouTube `playlistImages.list` retrieval operation.
- **FR-002**: System MUST identify the wrapper as representing the `playlistImages` resource and the `list` method in maintainer-visible wrapper metadata.
- **FR-003**: System MUST record the `GET /playlistImages` path shape and the official quota-unit cost of `1` for this wrapper.
- **FR-004**: System MUST make the quota-unit cost of `1` visible in the wrapper's docstring, signature-adjacent documentation, or equivalent maintainer-facing artifact.
- **FR-005**: System MUST define the supported `playlistImages.list` request contract, including the required lookup inputs for at least one supported playlist-image filter mode.
- **FR-006**: System MUST document the supported use of `part` and the playlist-image filter inputs supported by this wrapper in maintainer-facing artifacts.
- **FR-007**: System MUST document whether `playlistId`, `id`, or both are supported filter modes for this wrapper and MUST describe the request boundary associated with each supported mode.
- **FR-008**: System MUST record that `playlistImages.list` requires OAuth-backed access and MUST make that requirement reviewable in maintainer-facing wrapper artifacts.
- **FR-009**: System MUST document which optional paging inputs are supported for each supported filter mode and MUST clearly indicate which request modifiers fall outside the wrapper boundary.
- **FR-010**: System MUST reject or clearly flag `playlistImages.list` requests that omit the required supported filter input for the selected lookup mode.
- **FR-011**: System MUST reject or clearly flag requests that combine conflicting playlist-image filter modes when the wrapper contract does not allow that combination.
- **FR-012**: System MUST reject or clearly flag requests that rely on unsupported or incompatible request modifiers outside the supported wrapper contract.
- **FR-013**: System MUST reject or clearly flag requests that do not satisfy the documented OAuth requirement for `playlistImages.list`.
- **FR-014**: System MUST return a normalized playlist-image retrieval result for valid requests so higher layers can consume successful outcomes without reverse-engineering the response.
- **FR-015**: System MUST preserve enough request context in successful results for downstream layers to understand the selected playlist-image filter mode and lookup value that produced the result.
- **FR-016**: System MUST preserve a clear distinction between validation failures, access-related failures, successful empty results, and successful retrieval outcomes containing playlist-image data.
- **FR-017**: System MUST expose maintainer-facing contract detail describing supported filter modes, OAuth expectations, supported paging behavior, and unsupported-request boundaries for this wrapper.
- **FR-018**: System MUST keep this feature internal to Layer 1 and MUST NOT define a public MCP tool as part of YT-128.
- **FR-019**: System MUST preserve alignment with the shared Layer 1 metadata standards established for earlier Layer 1 slices.
- **FR-020**: System MUST enable reviewers to verify, from feature artifacts alone, the endpoint identity, quota behavior, OAuth requirement, supported filter modes, selector-specific paging behavior, and unsupported-request boundaries for `playlistImages.list`.

### Key Entities *(include if feature involves data)*

- **Playlist Images List Wrapper Contract**: The maintainer-facing definition of the internal `playlistImages.list` wrapper, including endpoint identity, quota cost, supported filter modes, OAuth requirement, selector-specific paging behavior, and unsupported-request guidance.
- **Playlist Images List Request**: The input contract that combines the required playlist-image lookup fields with any optional paging fields allowed by the wrapper.
- **Playlist Image Filter Mode**: The supported selection path used to retrieve playlist images, such as a playlist-scoped lookup or a direct image lookup, together with its paging and validation boundaries.
- **Playlist Image Retrieval Result**: The normalized retrieval outcome containing returned playlist-image data and enough request context for downstream layers to interpret the selected lookup mode.

### Assumptions

- YT-101 and YT-102 already provide the shared Layer 1 request foundation and metadata standards that this endpoint-specific slice extends.
- This feature defines the internal Layer 1 contract for `playlistImages.list`; any public-facing Layer 2 exposure is addressed separately in the Layer 2 tool workstream.
- Supported retrieval behavior for this slice centers on the documented `part` input plus playlist-image filter inputs such as `playlistId`, `id`, or both when explicitly supported by the wrapper contract.
- Paging inputs are in scope only when the wrapper explicitly documents them as supported for the selected filter mode.
- Official endpoint documentation is the source of truth for auth behavior, so this slice treats `playlistImages.list` as OAuth-required even if an older in-repo inventory summary suggests broader access.
- A valid request may return an empty list of playlist images, and that outcome should remain distinguishable from invalid input or access-related failure.

### Dependencies

- `YT-101` Layer 1 client foundation is available for shared request execution behavior.
- `YT-102` Layer 1 metadata standards are available so quota, auth expectations, endpoint identity, and filter-mode guidance remain consistent across wrappers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `playlistImages.list` wrapper artifacts produced by this feature display the official quota-unit cost of `1` in maintainer-visible metadata or documentation.
- **SC-002**: A maintainer can determine in under 1 minute which playlist-image filter modes the wrapper supports, whether `playlistId`, `id`, or both are accepted, which selector modes allow paging, and that OAuth-backed access is required by reading the wrapper contract alone.
- **SC-003**: In verification coverage, 100% of supported `playlistImages.list` retrieval patterns for this slice are represented by at least one passing successful retrieval scenario.
- **SC-004**: In verification coverage, 100% of tested requests with missing required filters, conflicting filter modes, unsupported modifiers, or missing OAuth-backed access fail with explicit normalized outcomes distinct from successful empty retrieval results.
