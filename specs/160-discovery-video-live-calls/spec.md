# Feature Specification: Layer 1 Live Calls for Discovery, Video, and Branding Resources

**Feature Branch**: `160-discovery-video-live-calls`  
**Created**: 2026-08-02  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-160, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Live Discovery and Video Results (Priority: P1)

As an agent developer, I can use a supported search or video lookup operation through its configured default path and receive current data from YouTube rather than a representative response.

**Why this priority**: Trustworthy discovery and video data is the foundation for the public search, video-detail, and video-statistics workflows.

**Independent Test**: Configure the required access, invoke each supported read operation without a test-only override, and verify that it produces the established live result or established live failure outcome.

**Acceptance Scenarios**:

1. **Given** a configured, authorized default invocation of a supported search, category, abuse-reason, or video lookup operation, **When** an agent developer supplies valid input, **Then** the operation uses live YouTube data rather than a static or representative successful result.
2. **Given** a successful live response from a supported read operation, **When** the response is returned, **Then** it retains that operation's established result shape and metadata.
3. **Given** invalid input to a supported operation, **When** it is invoked, **Then** its established validation outcome is returned before a live request is made.

---

### User Story 2 - Perform Authorized Video and Subscription Changes (Priority: P2)

As an authorized channel operator, I can manage subscriptions, videos, ratings, abuse reports, thumbnails, and watermarks through supported operations, with each request applying its declared access rules and returning a reliable outcome.

**Why this priority**: Incorrect authorization or request handling can prevent a legitimate change or cause a sensitive channel action to be reported inaccurately.

**Independent Test**: Exercise a subscription change, video mutation, rating or abuse report, thumbnail upload, and watermark change with controlled live-operation results, and verify the declared access requirement, request details, success mapping, and safe failure behavior.

**Acceptance Scenarios**:

1. **Given** an operation declared as API-key eligible, OAuth-required, or conditionally authorized, **When** it is invoked with configured access, **Then** it applies the operation's established authorization rule.
2. **Given** a valid, authorized request to create, update, rate, report, delete, subscribe, unsubscribe, set a thumbnail, or set or remove a watermark, **When** the operation completes, **Then** the caller receives the established normalized confirmation or result from the live action.
3. **Given** missing, invalid, expired, or insufficient access, **When** a supported operation is invoked, **Then** the caller receives the established safe configuration or authorization failure and no representative data.

---

### User Story 3 - Reach Live Wrappers Through Existing Public Tools (Priority: P3)

As an agent developer, I can use the existing low-level search and video tools and the higher-level video-detail tool knowing that their configured calls reach the live wrapper path.

**Why this priority**: Live wrappers deliver user value only when the public tools that depend on them use those wrappers instead of an alternate or representative path.

**Independent Test**: Invoke each named public-tool flow with controlled live-operation results and verify that it reaches the corresponding supported wrapper and returns a normalized live result or normalized live upstream failure.

**Acceptance Scenarios**:

1. **Given** a configured low-level search tool, **When** it is invoked with valid input, **Then** it reaches the live search wrapper path.
2. **Given** a configured low-level video tool or higher-level video-detail tool, **When** it is invoked with valid input, **Then** it reaches the live video wrapper path.
3. **Given** a live upstream failure in one of these public-tool flows, **When** the failure is returned, **Then** it uses the established normalized failure behavior without exposing credentials or substituting representative data.

### Edge Cases

- A configured default invocation lacks a usable required credential or does not have live operation configured; it returns the established safe failure and never a static successful result.
- An upstream request times out, is unavailable, returns malformed content, or returns an authorization, validation, quota, or service failure; the established normalized failure is returned without credential values or sensitive upstream details.
- A request contains invalid selectors, query values, a structured change request, or invalid media content; the operation's established validation rules remain in force and prevent the live action.
- A test explicitly injects a fake executor or representative response; it remains available for deterministic isolated tests only and is never selected for a configured default invocation.
- A public tool invokes a supported wrapper after the retrofit; it must not bypass that wrapper with a separate direct upstream request path.
- An authorized read produces no matching data or a mutation targets an unavailable resource; the caller receives the operation's established empty-result or normalized not-found outcome rather than representative data.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing request-level tests for all 16 in-scope operations that prove a configured default invocation reaches live execution and covers the operation's target, method, parameters, authorization mode, structured content or media form where applicable, success mapping, and normalized upstream failure. Add failing configured-flow tests for the existing low-level search and video tools and the higher-level video-detail tool.
- **Green**: Make the smallest changes needed to connect each existing wrapper to the shared live operation capability while preserving its public contract, validation, metadata, quota documentation, authorization behavior, and result and error normalization.
- **Refactor**: Remove repeated resource-family execution behavior by reusing the shared capability without altering externally observable wrapper behavior. Run focused checks during development and the full repository test suite with `pytest` plus code-quality checks with `ruff check .` before review; both commands must pass.
- **Required test levels**: Unit tests for request construction and authorization selection; integration tests with controlled live-operation results; contract tests for preserved wrapper results and normalized failures; and configured public-tool flow tests for the low-level search and video tools and higher-level video-detail tool.
- **Docstring work**: Every new or changed Python function in scope must have a reStructuredText docstring describing its responsibility, accepted request context, result, and safe failure behavior without exposing credential values.
- **Pull request evidence**: Include request-level results for all 16 operations, the three public-tool flow results, evidence that configured defaults do not return representative data, success and normalized-failure mapping evidence, and passing `pytest` and `ruff check .` output.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST make the configured default invocation of every in-scope wrapper use live YouTube data and MUST NOT return a representative default result or static successful result.
- **FR-002**: The feature scope MUST include exactly these existing operations: `search.list`; `subscriptions.list`, `subscriptions.insert`, and `subscriptions.delete`; `thumbnails.set`; `videoAbuseReportReasons.list`; `videoCategories.list`; `videos.list`, `videos.insert`, `videos.update`, `videos.rate`, `videos.getRating`, `videos.reportAbuse`, and `videos.delete`; and `watermarks.set` and `watermarks.unset`.
- **FR-003**: Each in-scope operation MUST preserve its existing public contract, endpoint metadata, input validation, quota documentation, authorization requirement, and result and error normalization when it accesses live YouTube data.
- **FR-004**: Each in-scope operation MUST perform the established YouTube action with its established request method, target, parameters, structured content, and media form where applicable.
- **FR-005**: Each in-scope operation MUST apply API-key, OAuth, or conditional authorization according to its existing endpoint metadata.
- **FR-006**: Operations that transfer thumbnails, videos, or watermarks MUST use the shared supported media-transfer capability and MUST NOT introduce a separate resource-specific live-request path.
- **FR-007**: When live configuration or required authorization is unavailable or unusable, each in-scope operation MUST return the established normalized configuration or authorization failure and MUST NOT return representative data.
- **FR-008**: Each in-scope operation MUST map successful live responses and upstream failures through its established result and error-normalization behavior.
- **FR-009**: The system MUST provide request-level automated coverage for every in-scope operation's request target, method, parameters, authorization mode, structured content or media form where applicable, successful-result mapping, and normalized upstream failure behavior.
- **FR-010**: The system MUST demonstrate that configured calls through the existing low-level search and video tools and the higher-level video-detail tool reach the live wrapper path.
- **FR-011**: The feature MUST retrofit existing wrappers only and MUST NOT add new endpoint inventory, change existing wrapper contracts, or create a separate direct upstream path for affected public tools.

### Key Entities

- **Configured Default Invocation**: A normal operation request made using the runtime configuration selected for an environment and without a test-only execution override.
- **Discovery, Video, Subscription, and Branding Operation**: An existing supported operation that retrieves, changes, reports on, uploads, or removes YouTube discovery, subscription, video, thumbnail, category, abuse-reason, or watermark data.
- **Authorization Rule**: The declared access requirement identifying whether an operation can use an API key, requires OAuth, or conditionally supports either.
- **Live Request**: The validated operation details sent to YouTube, including its target, method, parameters, optional structured content, and optional media content.
- **Normalized Outcome**: The established caller-facing successful result or safe failure returned after a live request.
- **Public-tool Flow**: A configured caller journey through an existing low-level search or video tool or the higher-level video-detail tool that reaches an affected wrapper.

### Assumptions

- The existing contracts, metadata, validation, quota documentation, authorization rules, and normalizers delivered by YT-140 through YT-156 are the compatibility baseline for this feature.
- YT-157 supplies the shared live-operation capability required by configured default invocations.
- The existing low-level search and video tools and the higher-level video-detail tool supply the public flows covered by this feature; the public tool catalog is not expanded.
- Explicitly injected fake executors and representative responses remain valid for deterministic isolated tests, but never represent configured default behavior.
- The project's established safe failure model determines the caller-facing format for unavailable configuration, authorization failures, and upstream failures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 16 of 16 in-scope operations demonstrate in automated configured-default tests that they use live operation and do not return a representative or static successful result.
- **SC-002**: 16 of 16 in-scope operations have request-level automated coverage for applicable request targets, methods, parameters, authorization modes, structured content or media forms, successful-result mapping, and normalized upstream failures.
- **SC-003**: 100% of affected compatibility tests continue to pass for public contracts, metadata, input validation, quota documentation, authorization rules, and normalized outcomes.
- **SC-004**: 3 of 3 named public-tool flows—the low-level search tool, low-level video tool, and higher-level video-detail tool—demonstrate that configured calls reach the live wrapper path and return a normalized live result or normalized live upstream failure.
- **SC-005**: 100% of tested missing, invalid, expired, or insufficient authorization cases return a safe normalized failure with no representative successful result or credential value.
- **SC-006**: Review of the automated test evidence finds zero configured-default paths among the 16 in-scope operations that use a resource-specific direct live-request path or a representative default result.
