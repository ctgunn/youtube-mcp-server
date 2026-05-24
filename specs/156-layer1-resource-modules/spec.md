# Feature Specification: Layer 1 Resource-Family Module Reorganization

**Feature Branch**: `156-layer1-resource-modules`  
**Created**: 2026-05-20  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-156, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Resource-Family Integration Code (Priority: P1)

As a maintainer, I can quickly find the Layer 1 integration responsibilities for a specific YouTube resource family, such as captions, channels, comments, playlists, videos, or watermarks, without searching through broad shared files.

**Why this priority**: The completed Layer 1 endpoint inventory is now large enough that maintainability is the primary blocker before more public tools are built on it.

**Independent Test**: Can be tested by selecting representative resource families and confirming that their endpoint wrappers, request validation expectations, metadata, and response handling responsibilities are discoverable from resource-family-specific organization while shared foundations remain separate.

**Acceptance Scenarios**:

1. **Given** a maintainer needs to inspect a specific YouTube resource family, **When** they look for that family in the Layer 1 integration area, **Then** they can identify the relevant endpoint wrappers, metadata, validation rules, and response handling responsibilities without reading unrelated resource families.
2. **Given** shared concerns such as authentication, request execution, retry policy, observability, and error normalization, **When** resource-family organization is reviewed, **Then** those shared concerns remain centralized rather than duplicated across families.
3. **Given** a resource family with multiple endpoints, **When** its Layer 1 responsibilities are inspected, **Then** the family-level organization shows how those endpoints relate without changing their individual contracts.

---

### User Story 2 - Compose Stable Layer 1 Capabilities (Priority: P2)

As a future Layer 2 or Layer 3 tool author, I can rely on stable resource-family integration surfaces while existing callers that use current integration imports continue to work.

**Why this priority**: Later public tool layers depend on Layer 1 as their foundation, so the refactor must improve composition without forcing unrelated migration work.

**Independent Test**: Can be tested by importing representative Layer 1 capabilities through both resource-family-oriented access points and existing compatibility import paths, then confirming each access path reaches the same documented behavior.

**Acceptance Scenarios**:

1. **Given** a future tool author needs a Layer 1 endpoint capability, **When** they locate it by YouTube resource family, **Then** they can compose it without depending on unrelated resource families.
2. **Given** downstream code uses existing integration import paths, **When** the refactor is complete, **Then** those imports continue to resolve and expose the expected capabilities.
3. **Given** the full set of completed Layer 1 endpoints from YT-103 through YT-155, **When** resource-family access points are reviewed, **Then** every endpoint remains reachable through a stable integration surface.

---

### User Story 3 - Verify Behavior Preservation (Priority: P3)

As a reviewer, I can verify that the reorganization preserves the already-complete Layer 1 endpoint contracts instead of introducing new endpoint behavior.

**Why this priority**: This feature is valuable only if it is a behavior-preserving reorganization; unintended contract drift would create risk for every later tool layer.

**Independent Test**: Can be tested by comparing pre-refactor and post-refactor contract evidence for the completed endpoint inventory, including request validation, credential behavior, quota metadata, auth metadata, response payload shape, and upstream error normalization.

**Acceptance Scenarios**:

1. **Given** an endpoint from YT-103 through YT-155, **When** its contract is exercised after the refactor, **Then** request validation, selector and filter behavior, credentials, quota metadata, auth metadata, response shape, and error handling match the established contract.
2. **Given** a reviewer examines the change, **When** they look for verification evidence, **Then** the evidence distinguishes behavior preservation from new endpoint implementation.
3. **Given** response handling for a YouTube operation, **When** the reviewer traces how it is selected, **Then** the mapping is explicit enough to audit without reading one long cross-resource conditional flow.

### Edge Cases

- Existing callers may import integration capabilities through current package-level or compatibility paths; those paths must continue to work.
- Some resource families contain only one endpoint while others contain many; both cases must remain easy to inspect.
- Some endpoint behavior is shared across resource families, such as common request construction and error normalization; shared behavior must not be duplicated or forked.
- Some endpoints have conditional auth, quota, selector, filter, or availability details; those details must survive the reorganization unchanged.
- Response handling may involve closely related resources or names that differ from public resource labels; the final organization must still make the operation-to-family mapping auditable.
- Existing tests may be concentrated in broad files; verification must still cover resource-family behavior without depending only on monolithic test coverage.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing or characterization tests that expose the expected resource-family organization and compatibility import behavior before moving each group of Layer 1 responsibilities. For behavior preservation, use existing endpoint contract tests as the baseline and add focused coverage where resource-family discoverability or compatibility paths are not already protected.
- **Green**: Move the minimum necessary Layer 1 responsibilities for each resource family while keeping existing endpoint behavior, public compatibility imports, metadata, validation rules, response shapes, and error normalization passing for that family.
- **Refactor**: After each completed family or practical group of families, remove duplicate transitional paths, keep shared concerns centralized, and run focused tests before the full repository check. The final review evidence must include a full `pytest` run with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Unit tests for resource-family organization and compatibility imports, contract tests for endpoint behavior preservation, integration tests for representative Layer 1 flows, and focused regression tests for response handling selection.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that clearly describes its Layer 1 responsibility without claiming behavior changes.
- **Pull request evidence**: Review materials must show the matched seed slice, the endpoint inventory covered by the reorganization, focused test commands for representative families, full-suite command output, lint output, and any intentionally preserved compatibility shims.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST organize resource-specific Layer 1 wrappers, builder functions, request validation responsibilities, endpoint metadata, and response handling responsibilities by YouTube resource family.
- **FR-002**: The system MUST preserve established behavior for every completed Layer 1 endpoint from YT-103 through YT-155.
- **FR-003**: The system MUST preserve request validation rules, selector and filter behavior, credential attachment behavior, quota-cost metadata, auth-mode metadata, response payload shape, and upstream error normalization behavior for all affected endpoints.
- **FR-004**: The system MUST keep shared Layer 1 foundations centralized and reusable across resource families, including authentication, request execution, retry policy, observability hooks, contracts, error normalization, and generic YouTube request construction.
- **FR-005**: The system MUST provide stable access to Layer 1 capabilities through resource-family-oriented organization for activities, captions, channel banners, channels, channel sections, comments, comment threads, guide categories, localization, members, membership levels, playlist images, playlist items, playlists, search, subscriptions, thumbnails, video abuse report reasons, video categories, videos, and watermarks.
- **FR-006**: The system MUST preserve compatibility for existing public integration import paths used by downstream code and tests.
- **FR-007**: The system MUST make the mapping between YouTube operations and endpoint-specific response handling explicit and auditable.
- **FR-008**: The system MUST support verification by resource family so reviewers can validate behavior without relying only on broad Layer 1 test files.
- **FR-009**: The system MUST avoid intentional endpoint contract changes, new endpoint semantics, or second implementations of completed Layer 1 endpoint behavior as part of this feature.
- **FR-010**: The system MUST provide review evidence that all completed Layer 1 endpoint families remain covered by automated tests after the reorganization.

### Key Entities

- **Resource Family**: A YouTube capability group, such as captions, channels, playlists, videos, or watermarks, used to organize related Layer 1 endpoint responsibilities.
- **Layer 1 Endpoint Capability**: A completed integration capability from YT-103 through YT-155, including its request expectations, metadata, result shape, and error behavior.
- **Endpoint Contract**: The observable behavior that callers rely on for validation, credentials, quota and auth metadata, request shape, response shape, and normalized errors.
- **Compatibility Import Surface**: Existing integration access paths that downstream code and tests already use and that must continue to expose the same capabilities.
- **Verification Evidence**: Automated test and lint results that demonstrate the reorganization preserved established Layer 1 behavior.

### Assumptions

- YT-103 through YT-155 represent the completed Layer 1 endpoint inventory that must be preserved by this refactor.
- The primary goal is maintainability and future composition, not new YouTube endpoint capability.
- Existing Layer 1 tests define the baseline behavior and may be reorganized or supplemented when coverage is too broad to verify a resource family clearly.
- Compatibility import paths remain supported for this feature so downstream code does not need to migrate in the same change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can identify the Layer 1 responsibilities for any supported YouTube resource family in under 2 minutes during review.
- **SC-002**: 100% of completed Layer 1 endpoint capabilities from YT-103 through YT-155 remain covered by passing automated behavior checks after the reorganization.
- **SC-003**: Existing compatibility import paths used by current downstream code and tests continue to work with zero known import regressions.
- **SC-004**: Reviewers can trace each supported YouTube operation to its response handling responsibility without following a single cross-resource conditional flow.
- **SC-005**: The final review package includes passing focused resource-family checks, passing full repository behavior checks, and passing code-quality checks.
- **SC-006**: No intentional changes are introduced to request validation, selector behavior, credentials, quota metadata, auth metadata, response shapes, or normalized error behavior for any completed Layer 1 endpoint.
