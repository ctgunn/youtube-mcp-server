# Feature Specification: Layer 1 Live Calls for Catalog, Membership, and Playlist Resources

**Feature Branch**: `159-catalog-playlist-live-calls`  
**Created**: 2026-08-02  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-159, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Live Catalog, Membership, and Playlist Results (Priority: P1)

As an agent developer, I can invoke any supported catalog, membership, or playlist operation through its configured default path and receive a result from the live YouTube service instead of a representative response.

**Why this priority**: Trustworthy live data is necessary before public tools can support discovery, membership, and playlist workflows.

**Independent Test**: For each supported operation, configure its required access, invoke the existing wrapper without a test-only override, and verify that it performs the established live request and returns its normalized success or failure outcome.

**Acceptance Scenarios**:

1. **Given** a configured, authorized default invocation for any supported operation, **When** an agent developer invokes it with valid input, **Then** it uses the live execution path rather than a static or representative successful result.
2. **Given** a successful live response for a supported operation, **When** the response is returned, **Then** it retains that operation's existing normalized result shape and metadata.
3. **Given** an invalid request input, **When** the operation is invoked, **Then** its existing validation outcome is returned before a live request is made.

---

### User Story 2 - Apply the Correct Authorization and Request Form (Priority: P2)

As an operator, I can rely on each catalog, membership, and playlist operation to use the authorization rule and request details already declared for that operation when it accesses live data.

**Why this priority**: The operations span reads, creation, updates, deletion, and playlist-image uploads, so an incorrect authorization choice or request form can block a workflow or change the wrong resource.

**Independent Test**: Exercise a read operation, a playlist mutation, and a playlist-image upload with controlled live-runtime requests, and verify the declared authorization mode, request method, target, parameters, body, or upload form for each.

**Acceptance Scenarios**:

1. **Given** an operation declared as API-key eligible, OAuth-required, or conditionally authorized, **When** it is invoked with configured access, **Then** it applies the corresponding existing authorization rule.
2. **Given** an operation that creates, updates, deletes, or uploads a playlist image, **When** it is invoked, **Then** its established request details are passed to the live execution path without changing the public wrapper contract.
3. **Given** missing, invalid, expired, or insufficient access, **When** an operation is invoked, **Then** the caller receives the established normalized authorization or configuration failure and no representative data.

---

### User Story 3 - Use Live Wrappers Through Public Tools (Priority: P3)

As an agent developer, I can use at least one configured public tool in every affected resource family and know it reaches the same live wrapper path.

**Why this priority**: A completed internal wrapper is valuable only when callers that depend on it actually receive live behavior.

**Independent Test**: Configure one public-tool flow for each affected resource family, invoke it with controlled live execution, and verify that the call reaches its resource-family wrapper and produces a normalized live result or normalized live upstream failure.

**Acceptance Scenarios**:

1. **Given** a configured public-tool flow for guide categories, localization, members, membership levels, playlist images, playlist items, or playlists, **When** it is invoked, **Then** it reaches the corresponding live wrapper path.
2. **Given** a live upstream failure in one of those flows, **When** the failure is returned to the caller, **Then** it uses the established normalized failure behavior and does not expose credentials or substitute representative data.

### Edge Cases

- A default invocation lacks a usable required credential, contains credentials that do not satisfy the operation's declared authorization rule, or is not configured for live execution; it returns the existing safe normalized failure and never a static success.
- An upstream request times out, returns a malformed response, or returns an authorization, validation, or service failure; the existing normalized failure behavior is preserved without exposing credential values or sensitive upstream details.
- An operation includes selectors, query parameters, a structured body, or a playlist-image upload; the existing request validation and shaping rules remain in force for that operation.
- A test injects a fake executor or representative response; it remains available only when explicitly requested by the test and is never selected by a configured default invocation.
- A public tool calls a supported wrapper after the retrofit; it must not bypass the wrapper with a separate direct request path.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing request-level tests for all 17 listed operations that prove a configured default invocation reaches live execution and covers the operation's request target, method, parameters, authorization mode, body or upload form where applicable, success mapping, and normalized upstream failure. Add one failing configured public-tool flow for each of the seven affected resource families.
- **Green**: Make the smallest changes needed to connect each existing wrapper to the shared live runtime while preserving its public contract, validation, metadata, quota documentation, authorization behavior, and response normalization.
- **Refactor**: Remove any repeated resource-family execution behavior by reusing the shared runtime, without altering externally observable wrapper behavior. Run focused checks throughout and the full repository test suite with `pytest` plus code-quality checks with `ruff check .` before review; both must pass.
- **Required test levels**: Unit tests for wrapper request construction and authorization selection; integration tests with controlled live-runtime responses; contract tests for preserved wrapper results and normalized failures; and configured public-tool flow tests for guide categories, localization, members, membership levels, playlist images, playlist items, and playlists.
- **Docstring work**: Every new or changed Python function in scope must have a reStructuredText docstring that describes its responsibility, accepted request context, result, and safe failure behavior without exposing credential values.
- **Pull request evidence**: Include the request-level results for all listed operations, the seven public-tool flow results, evidence that configured defaults do not return representative data, success and normalized-failure mapping evidence, and passing `pytest` and `ruff check .` output.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST make the configured default invocation of each listed catalog, membership, and playlist wrapper use the shared live execution path and MUST NOT return a representative default executor result or static successful result.
- **FR-002**: The scope of this feature MUST include exactly these existing operations: `guideCategories.list`; `i18nLanguages.list` and `i18nRegions.list`; `members.list`; `membershipsLevels.list`; `playlistImages.list`, `playlistImages.insert`, `playlistImages.update`, and `playlistImages.delete`; `playlistItems.list`, `playlistItems.insert`, `playlistItems.update`, and `playlistItems.delete`; and `playlists.list`, `playlists.insert`, `playlists.update`, and `playlists.delete`.
- **FR-003**: Each in-scope wrapper MUST preserve its existing public contract, endpoint metadata, request validation, quota documentation, authorization requirement, and response normalization when it uses live execution.
- **FR-004**: Each in-scope wrapper MUST send the established upstream request method, target, parameters, body, and media-upload form when applicable, using the shared live execution capability rather than a resource-specific execution path.
- **FR-005**: Each in-scope wrapper MUST apply API-key, OAuth, or conditional authorization according to its existing endpoint metadata.
- **FR-006**: Playlist-image operations that send media MUST build and submit their required upload form through the shared live execution capability and MUST NOT add a separate resource-specific transport path.
- **FR-007**: When live configuration or the required authorization is unavailable or unusable, each in-scope wrapper MUST return the established normalized configuration or authorization failure and MUST NOT return representative data.
- **FR-008**: Each in-scope wrapper MUST map successful live responses and upstream failures through its existing response-normalization and error-normalization behavior.
- **FR-009**: The system MUST provide request-level automated coverage for every in-scope operation's request target, method, parameters, authorization mode, body or upload form where applicable, successful-result mapping, and normalized upstream failure behavior.
- **FR-010**: The system MUST demonstrate at least one configured public-tool flow reaches the live wrapper path for each affected resource family: guide categories, localization, members, membership levels, playlist images, playlist items, and playlists.
- **FR-011**: The feature MUST retrofit existing wrappers only and MUST NOT add new endpoint inventory, change existing wrapper contracts, or create a separate direct upstream path for affected public tools.

### Key Entities

- **Configured Default Invocation**: A normal wrapper call made with the runtime configuration selected for an environment and without a test-only execution override.
- **Catalog, Membership, and Playlist Wrapper**: An existing operation that retrieves or changes guide-category, localization, membership, playlist-image, playlist-item, or playlist data.
- **Authorization Rule**: The declared access requirement that identifies whether an operation can use an API key, requires OAuth, or conditionally supports either.
- **Live Request**: The validated operation details sent to the upstream YouTube service, including its target, method, parameters, optional structured content, and optional media content.
- **Normalized Outcome**: The existing caller-facing successful result or safe failure returned after a live request.
- **Public-tool Flow**: A configured caller journey that reaches an affected wrapper through the supported public tool surface.

### Assumptions

- The existing wrapper contracts, metadata, validation, quota documentation, authorization rules, and normalizers delivered by YT-123 through YT-139 are the compatibility baseline for this feature.
- YT-157 supplies the shared live execution capability required by the configured default path.
- Existing public tools provide at least one callable flow for each of the seven affected resource families; this feature verifies their use of the wrapper rather than expanding the public tool catalog.
- Explicitly injected fake executors and representative responses remain valid for deterministic isolated tests, but never represent the configured default behavior.
- The project's existing safe failure model determines the caller-facing format for unavailable configuration, authorization failures, and upstream failures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 17 of 17 in-scope wrapper operations demonstrate in automated configured-default tests that they select the live execution path and do not return a representative or static successful result.
- **SC-002**: 17 of 17 in-scope operations have request-level automated coverage for the applicable request target, method, parameters, authorization mode, body or upload form, successful-result mapping, and normalized upstream failure.
- **SC-003**: 100% of affected wrapper compatibility tests continue to pass for public contracts, metadata, request validation, quota documentation, authorization rules, and normalized outcomes.
- **SC-004**: 7 of 7 affected resource families demonstrate at least one configured public-tool flow that reaches the live wrapper path and returns a normalized live result or normalized live upstream failure.
- **SC-005**: 100% of tested missing, invalid, expired, or insufficient authorization cases return a safe normalized failure with no representative successful result or credential value.
- **SC-006**: A review of automated test evidence finds zero configured-default paths among the 17 in-scope operations that use a resource-specific direct execution path or a representative default result.
