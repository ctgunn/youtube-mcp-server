# Feature Specification: Layer 2 Tool `comments_setModerationStatus`

**Feature Branch**: `219-comments-set-moderation-status`  
**Created**: 2026-06-19  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-219, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Moderate Existing Comments Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `comments_setModerationStatus` tool to set the moderation status for one or more existing YouTube comments while staying close to the upstream `comments.setModerationStatus` write behavior and returned moderation acknowledgment.

**Why this priority**: This is the core value of YT-219. Layer 2 must expose endpoint-backed comment moderation for direct moderation workflows, debugging, and later composition without turning the tool into comment listing, reply creation, comment editing, deletion, sentiment, ranking, summarization, or automated moderation advice.

**Independent Test**: Can be tested by invoking `comments_setModerationStatus` with eligible authorization, one or more valid comment identifiers, and a supported moderation outcome, then confirming the caller receives a clear moderation-status mutation result with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization and provides valid target comment identifiers plus a supported moderation status, **When** they call `comments_setModerationStatus`, **Then** the result confirms the requested moderation outcome and preserves the operation context.
2. **Given** a caller provides a supported optional moderation flag that is valid for the selected moderation status, **When** the moderation request succeeds, **Then** the result preserves that moderation intent without adding unrelated comment, thread, channel, video, deletion, or analysis data.
3. **Given** the upstream moderation operation succeeds with an acknowledgment-style result rather than a comment resource collection, **When** the caller inspects the result, **Then** the single moderation mutation outcome is clear and is not presented as listing, thread traversal, or higher-level review workflow output.
4. **Given** a caller wants direct access to comment moderation behavior, **When** they use `comments_setModerationStatus`, **Then** the tool performs only the moderation-status operation and is not presented as comment creation, comment editing, deletion, ranking, summarization, enrichment, or automated moderation recommendation.

---

### User Story 2 - Understand Cost, OAuth, and Moderation States Before Calling (Priority: P2)

As a client developer, I can inspect `comments_setModerationStatus` before invoking it and immediately understand that it maps to `comments.setModerationStatus`, costs 50 official quota units per call, requires eligible OAuth authorization, and supports only documented moderation-state transitions and optional moderation flags.

**Why this priority**: Comment moderation is quota-bearing, permission-sensitive, and can visibly change published or review-held content. Callers need quota, OAuth, target-comment, supported-status, optional-flag, transition-boundary, and unsupported-operation visibility in discovery, descriptions, and examples before they spend quota or change moderation state.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, supported moderation statuses, optional flag rules, and unsupported moderation shapes are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `comments_setModerationStatus`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported moderation boundary.
2. **Given** an example request is shown for `comments_setModerationStatus`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a supported moderation status are visible alongside the request shape.
3. **Given** a caller needs to reject or publish one or more comments, **When** they inspect the tool contract, **Then** the required relationship between comment identifiers, moderation status, optional moderation flags, and mutation outcome is clear before invocation.
4. **Given** a caller wants unsupported moderation transitions, moderation advice, bulk discovery, deletion, editing, or automated review decisions, **When** they inspect the tool contract, **Then** the boundary of `comments_setModerationStatus` is clear before invocation.

---

### User Story 3 - Reject Unsupported Moderation Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `comments_setModerationStatus` request lacks eligible OAuth authorization, omits required moderation inputs, uses unsupported statuses, combines incompatible optional flags, targets duplicate or invalid comments, or includes unsupported operations, so I can correct the request without guessing which moderation rule was violated.

**Why this priority**: `comments.setModerationStatus` combines write authorization, one-or-more target comments, supported moderation outcomes, optional flag constraints, and upstream moderation failures. Clear validation protects callers from ambiguous mutation failures while keeping the tool faithful to the endpoint instead of inventing fallback review, deletion, or analysis behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing identifiers, duplicate identifiers, missing moderation status, unsupported moderation status, incompatible optional flags, unsupported options, and inaccessible target comments, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `comments_setModerationStatus`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a target-comment or status-format failure.
2. **Given** a caller omits the required comment identifiers or moderation status, **When** they call `comments_setModerationStatus`, **Then** the request is rejected with guidance that both valid targets and a supported moderation outcome are required.
3. **Given** a caller uses an unsupported moderation status or combines an optional flag with an incompatible status, **When** they call `comments_setModerationStatus`, **Then** the request is rejected with guidance that the selected transition is outside the endpoint-backed moderation boundary.
4. **Given** a caller targets a missing, private, deleted, duplicate, locked, or otherwise ineligible comment, **When** they call `comments_setModerationStatus`, **Then** the response preserves the appropriate validation, access, missing-resource, or upstream failure meaning using the shared Layer 2 conventions.

### Edge Cases

- The caller omits one or more required comment identifiers; the request must be rejected before it is treated as a supported moderation attempt.
- The caller provides an empty identifier, malformed identifier, duplicate identifier, or target list that exceeds the supported request boundary; the response must identify the target-comment rule.
- The caller has no eligible OAuth authorization or lacks permission to moderate the targeted comments; the response must distinguish access failure from malformed moderation input.
- The caller omits `moderationStatus`, provides an empty value, uses unsupported casing, or requests an unsupported moderation status; the response must identify the supported moderation-status rule.
- The caller provides `banAuthor` or another optional moderation flag in a combination that is not valid for the selected moderation status; the request must be rejected or clearly flagged as outside the endpoint contract.
- The caller targets comments that are missing, deleted, held in an incompatible state, private, locked, unavailable, disabled for moderation, or inaccessible to the selected authorization context; the response must preserve the appropriate access, missing-resource, or upstream failure meaning.
- The upstream success response omits optional fields or returns acknowledgment-style content only; the result must preserve the mutation outcome without fabricating comment resource data.
- The upstream service returns quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects comment listing, reply creation, comment editing, deletion, sentiment analysis, ranking, summarization, enrichment, moderation recommendations, or heuristic interpretation; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `comments_setModerationStatus` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `comments.setModerationStatus` identity, official quota-unit cost of `50`, OAuth-required auth mode, supported moderation-state boundary, optional-flag guidance, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required target comment identifiers, required moderation status, duplicate or invalid identifiers, unsupported moderation statuses, incompatible optional flags, unsupported operation fields, unsupported optional parameters, and access-sensitive failures.
- **Red**: Add failing result-contract checks proving that moderation outcome, target context, optional moderation flag context, mutation acknowledgment, relevant authorization context, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `comments_setModerationStatus` tool contract and behavior needed for callers to make supported low-level `comments.setModerationStatus` moderation requests and receive near-raw moderation mutation results.
- **Green**: Include representative examples for authorized moderation status change, authorized rejection with a compatible optional flag, missing OAuth authorization, missing comment identifiers, duplicate identifiers, missing moderation status, unsupported moderation status, incompatible optional flag, unsupported option validation failure, and access-sensitive upstream failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `comments_setModerationStatus` request, response, quota, auth, target-comment, moderation-status, optional-flag, caveat, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for authorization, target-comment, moderation-status, optional-flag, duplicate-target, and unsupported-option validation, integration-style checks for representative successful and failed comment moderation paths, and documentation checks for quota/auth/moderation-state/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `comments_setModerationStatus` responsibility, inputs, outputs, quota cost, OAuth behavior, target-comment behavior, moderation-status boundary, optional-flag rules, mutation result, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-219`, the dependency assumptions from YT-119/YT-201/YT-202, focused `comments_setModerationStatus` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `comments_setModerationStatus`.
- **FR-002**: The `comments_setModerationStatus` tool definition MUST identify its mapped upstream operation as YouTube resource `comments` and method `setModerationStatus`.
- **FR-003**: The `comments_setModerationStatus` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `comments_setModerationStatus` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `comments_setModerationStatus` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present comment moderation as an API-key-only capability.
- **FR-006**: The `comments_setModerationStatus` input contract MUST preserve the upstream concepts of one or more target comment identifiers, required moderation status, supported optional moderation flags, and supported write context where those concepts are supported.
- **FR-007**: The `comments_setModerationStatus` input contract MUST require at least one valid target comment identifier for each moderation request.
- **FR-008**: The `comments_setModerationStatus` input contract MUST require a supported moderation status for each moderation request and MUST document the accepted moderation outcomes.
- **FR-009**: The `comments_setModerationStatus` input contract MUST document supported optional moderation flags and MUST reject incompatible flag and status combinations.
- **FR-010**: The `comments_setModerationStatus` tool MUST support valid authorized moderation requests when the caller's OAuth authorization is sufficient for the targeted comments.
- **FR-011**: The `comments_setModerationStatus` tool MUST reject requests that require OAuth access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-012**: The `comments_setModerationStatus` tool MUST reject missing, empty, malformed, duplicate, unsupported, or conflicting target comment identifiers with clear caller-facing validation feedback.
- **FR-013**: The `comments_setModerationStatus` tool MUST reject missing, empty, malformed, unsupported, or unavailable moderation status values with clear caller-facing validation feedback.
- **FR-014**: The `comments_setModerationStatus` tool MUST reject unsupported optional moderation flags, incompatible flag and status combinations, unsupported operation fields, listing fields, creation fields, update fields, deletion fields, search instructions, automated moderation advice, ranking instructions, summarization instructions, and unsupported moderation shapes with clear caller-facing validation feedback.
- **FR-015**: The `comments_setModerationStatus` result MUST preserve target comment context, requested moderation status, compatible optional flag context, mutation outcome details, relevant authorization context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-016**: The `comments_setModerationStatus` tool MUST distinguish successful moderation outcomes from validation failures, authorization failures, missing or inaccessible target comments, unsupported moderation transitions, incompatible optional flags, quota failures, disabled-comment failures, unavailable resources, and unexpected upstream failures.
- **FR-017**: The `comments_setModerationStatus` tool MUST surface upstream quota, authorization, invalid request, missing resource, disabled comments, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `comments_setModerationStatus` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, supported scopes or equivalent access expectations, target comment requirements, supported moderation statuses, optional flag rules, unsupported moderation shapes, availability state, and access-sensitive behavior.
- **FR-019**: The `comments_setModerationStatus` contract MUST remain close to the upstream `comments.setModerationStatus` endpoint and MUST NOT add higher-level comment listing, reply creation, comment editing, deletion, sentiment analysis, ranking, summarization, enrichment, automated moderation recommendation, or heuristic interpretation.
- **FR-020**: The `comments_setModerationStatus` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, request validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `comments_setModerationStatus` tool MUST rely on the existing Layer 1 `comments.setModerationStatus` capability from YT-119 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one authorized moderation status change, one authorized rejection with a compatible optional flag, one missing-OAuth failure, one missing-target failure, one duplicate-target failure, one missing-status failure, one unsupported-status failure, one incompatible optional-flag failure, one unsupported option failure, and one access-sensitive upstream failure.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand OAuth, quota, target-comment, moderation-status, optional-flag, and transition-boundary requirements, interpret moderation mutation results, and handle failures for `comments_setModerationStatus` without consulting implementation-only artifacts.

### Key Entities

- **Comments Moderation Status Tool**: The public Layer 2 MCP tool named `comments_setModerationStatus`, representing one low-level endpoint-backed comment moderation operation.
- **Comment Moderation Request**: The request shape that combines target comment identifiers, requested moderation status, any supported optional moderation flags, and eligible write context for one moderation attempt.
- **Target Comment Identifiers**: The caller-provided identifiers for one or more existing comments whose moderation status will be changed.
- **Moderation Status**: The caller-selected supported outcome to apply to the targeted comments.
- **Moderation Transition Policy**: The caller-facing rules that distinguish supported moderation statuses and optional flag combinations from unsupported moderation transitions or request shapes.
- **Optional Moderation Flag**: A supported additional moderation instruction, such as author-banning behavior where valid, that is only accepted with compatible moderation statuses.
- **Write Authorization Context**: The caller's eligible OAuth-backed permission state that determines whether comment moderation is allowed.
- **Moderation Mutation Result**: The returned moderation acknowledgment, requested outcome context, target context, optional flag context, and operation metadata produced by a successful `comments_setModerationStatus` call.
- **Quota Disclosure**: The caller-facing statement that each `comments_setModerationStatus` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that comment moderation requires eligible OAuth authorization and is not available through API-key-only access.
- **Moderation Boundary Disclosure**: The caller-facing explanation that this tool changes moderation status on existing comments and excludes listing, insertion, editing, deletion, advice, and higher-level analysis behavior.

### Assumptions

- YT-119 provides the Layer 1 `comments.setModerationStatus` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, request validation, error, example, and validation standards this feature must follow.
- `comments_setModerationStatus` is a low-level endpoint-backed tool for direct comment moderation, debugging, and power-user workflows; higher-level comment listing, reply creation, editing, deletion, ranking, sentiment analysis, summarization, analytics, moderation recommendation, or automated review workflows belong to separate endpoint or Layer 3 features.
- The tool supports one requested moderation status per call and applies that status to one or more targeted comments when the request is valid and authorized.
- Optional moderation flags are only in scope when they are documented as compatible with the selected moderation status; unsupported combinations are rejected or clearly documented as out of scope.
- The official YouTube Data API documentation and existing project inventory are the default sources for `comments.setModerationStatus` quota cost, OAuth behavior, target-comment rules, supported moderation statuses, optional flag rules, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized moderation, compatible optional flags, missing authorization, missing or duplicate targets, missing or unsupported moderation status, incompatible optional flags, unsupported options, access-sensitive failures, and moderation mutation results is sufficient for this slice.

### Dependencies

- `YT-119` Layer 1 `comments.setModerationStatus` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `comments_setModerationStatus` discovery metadata, descriptions, and examples produced by this feature display the mapped `comments.setModerationStatus` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `comments_setModerationStatus` requires eligible OAuth authorization and cannot be used with API-key-only access by reading the tool contract alone.
- **SC-003**: A client developer can identify the target-comment requirements, supported moderation statuses, optional flag rules, unsupported transition boundaries, and excluded higher-level behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `comments_setModerationStatus`, identify the OAuth requirement, prepare a valid moderation request, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `comments_setModerationStatus` requests return moderation mutation results with target context, requested moderation status, compatible optional flag context when supplied, relevant authorization context, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid moderation requests that omit OAuth, omit target identifiers, use duplicate targets, omit moderation status, use unsupported moderation status, combine incompatible optional flags, or include unsupported options are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative target-comment access, missing-resource, disabled-comment, unsupported-transition, incompatible-flag, quota, authorization, and unexpected upstream failures are distinguishable from successful moderation mutations and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `comments_setModerationStatus` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, request validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `comments_setModerationStatus` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
