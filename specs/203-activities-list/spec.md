# Feature Specification: Layer 2 Tool `activities_list`

**Feature Branch**: `203-activities-list`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Read the PRD to get an overview of the project and its goals for context. Then, work on the requirements for YT-203, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Channel Activity Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `activities_list` tool to retrieve recent activity for a YouTube channel while staying close to the upstream `activities.list` filter, part-selection, and pagination behavior.

**Why this priority**: This is the core value of YT-203. Layer 2 must expose direct endpoint-backed access for raw exploration, debugging, and advanced workflows before higher-level activities tools can compose it.

**Independent Test**: Can be tested by invoking `activities_list` with a supported channel-based request and confirming the caller receives activity items, requested resource parts, pagination details when present, and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has a valid channel-based activity request, **When** they call `activities_list`, **Then** the result includes the activity collection returned for that channel and preserves the requested resource parts.
2. **Given** the upstream result has additional pages, **When** the caller inspects the tool result, **Then** the next-page token or equivalent pagination information is visible for follow-up calls.
3. **Given** the channel has no recent activity items, **When** the caller makes a valid request, **Then** the tool returns a successful empty item collection rather than an error.

---

### User Story 2 - Understand Cost and Access Before Calling (Priority: P2)

As a client developer, I can inspect `activities_list` before invoking it and immediately understand that it maps to `activities.list`, costs 1 official quota unit per call, and may require different access depending on the selected activity filter.

**Why this priority**: Layer 2 tools are intended for direct endpoint access. Callers need quota and auth visibility up front so they can decide whether a request is appropriate and avoid surprising failures or unnecessary cost.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, and examples to confirm the upstream identity, quota cost of `1`, auth mode, and filter-dependent access expectations are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `activities_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, auth mode, and availability state.
2. **Given** an example request is shown for `activities_list`, **When** a caller reads the example, **Then** the quota cost of `1` is visible alongside the request shape.
3. **Given** a caller chooses an authorized-user-only activity filter, **When** they inspect the tool contract, **Then** the need for eligible user authorization is clear before invocation.

---

### User Story 3 - Reject Unsupported Activity Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `activities_list` request uses missing, conflicting, or unsupported filters, so I can correct the request without guessing which upstream rule was violated.

**Why this priority**: `activities.list` supports selector-style filters whose combinations matter. Clear validation protects low-level users while keeping the tool faithful to the endpoint.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing selectors and conflicting selectors, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required activity selector, **When** they call `activities_list`, **Then** the request is rejected with guidance that a supported selector is required.
2. **Given** a caller provides mutually exclusive activity selectors in one request, **When** they call `activities_list`, **Then** the request is rejected with guidance that only one selector mode may be used.
3. **Given** a caller requests a private activity view without eligible authorization, **When** they call `activities_list`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing public resource.

### Edge Cases

- A valid channel activity request returns no items; the result must remain successful and include an empty item collection.
- The upstream response includes a page token; the tool result must preserve the token so the caller can continue listing activity.
- The caller provides multiple activity selector filters that are mutually exclusive; the request must be rejected before it is treated as valid endpoint usage.
- The caller chooses an activity filter that requires authorized user context but no eligible authorization is available; the response must surface an access requirement.
- The caller supplies optional fields or page-size values outside the supported endpoint contract; the request must be rejected or clearly flagged as unsupported.
- The upstream service returns a quota, authorization, invalid-request, or unavailable-service failure; the caller-facing error must follow the shared Layer 2 error conventions.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `activities_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `activities.list` identity, official quota-unit cost of `1`, auth mode, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for supported activity selectors, required part selection, pagination inputs, missing selector handling, mutually exclusive selector handling, and filter-dependent authorization guidance.
- **Red**: Add failing result-contract checks proving that activity items, requested parts, empty collections, pagination tokens, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `activities_list` tool contract and behavior needed for callers to make supported low-level `activities.list` requests and receive near-raw activity collection results.
- **Green**: Include representative examples for public channel activity retrieval, paginated continuation, empty results, and authorized-user-only filter behavior.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `activities_list` request, response, quota, auth, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for selector and pagination validation, integration-style checks for representative successful and failed activity listing paths, and documentation checks for quota/auth/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `activities_list` responsibility, inputs, outputs, quota cost, auth behavior, and selector or pagination constraints.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-203`, the dependency assumptions from YT-103/YT-201/YT-202, focused `activities_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `activities_list`.
- **FR-002**: The `activities_list` tool definition MUST identify its mapped upstream operation as YouTube resource `activities` and method `list`.
- **FR-003**: The `activities_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `activities_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `activities_list` tool metadata MUST state the auth mode and distinguish public channel-based access from activity filters that require eligible user authorization.
- **FR-006**: The `activities_list` input contract MUST preserve the upstream concepts of activity selector filters, part selection, pagination tokens, and page-size limits where those concepts are supported.
- **FR-007**: The `activities_list` input contract MUST require exactly one supported activity selector mode for each request.
- **FR-008**: The `activities_list` tool MUST reject mutually exclusive activity selector combinations with clear caller-facing validation feedback.
- **FR-009**: The `activities_list` tool MUST reject requests that require authorized user context when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-010**: The `activities_list` result MUST preserve returned activity items, requested resource parts, pagination details, and relevant request context in a near-raw endpoint-backed shape.
- **FR-011**: The `activities_list` result MUST treat a valid no-item activity response as a successful empty collection.
- **FR-012**: The `activities_list` tool MUST surface upstream quota, authorization, missing resource, invalid request, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-013**: The `activities_list` contract MUST remain close to the upstream `activities.list` endpoint and MUST NOT add higher-level enrichment, ranking, transcript lookup, channel expansion, or heuristic interpretation.
- **FR-014**: The `activities_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, and example standards established by YT-201 and YT-202.
- **FR-015**: The `activities_list` tool MUST rely on the existing Layer 1 `activities.list` capability from YT-103 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-016**: The feature MUST include caller-facing examples for at least one public channel activity request, one paginated request, one empty-result outcome, and one authorization-sensitive filter scenario.
- **FR-017**: The feature MUST include validation evidence that clients can discover, call, paginate, and handle failures for `activities_list` without consulting implementation-only artifacts.

### Key Entities

- **Activities List Tool**: The public Layer 2 MCP tool named `activities_list`, representing one low-level endpoint-backed activity listing operation.
- **Activity Selector**: The request filter mode that determines which activity feed is listed, including public channel-based access and authorization-sensitive user activity views.
- **Part Selection**: The caller-selected resource sections requested for returned activity items.
- **Pagination Cursor**: The token or continuation value that lets callers request subsequent activity result pages.
- **Activity Collection Result**: The returned activity item collection, including successful empty collections and any pagination details.
- **Quota Disclosure**: The caller-facing statement that each `activities_list` invocation costs 1 official quota unit.
- **Auth Requirement Disclosure**: The caller-facing indication of which activity selector modes are public and which require eligible user authorization.

### Assumptions

- YT-103 provides the Layer 1 `activities.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, error, example, and validation standards this feature must follow.
- `activities_list` is a low-level endpoint-backed tool for direct access, debugging, and power-user workflows; higher-level discovery, ranking, enrichment, or research workflows belong to later Layer 3 features.
- The official YouTube Data API documentation is the default source for `activities.list` quota cost, auth behavior, selector rules, availability state, and pagination behavior, with any discovered caveats recorded explicitly.
- Representative coverage of channel-based access, pagination, empty results, invalid selectors, and authorization-sensitive filters is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `activities_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `activities.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute whether a planned `activities_list` request uses public channel access or requires eligible user authorization by reading the tool contract alone.
- **SC-003**: 100% of representative valid `activities_list` requests return activity items or a successful empty collection with requested parts and pagination details preserved when present.
- **SC-004**: 100% of representative invalid selector combinations are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-005**: Reviewers can verify in a single review pass that `activities_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example standards.
- **SC-006**: A power user can discover `activities_list`, identify the required selector and pagination inputs, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-007**: Final review evidence includes passing focused `activities_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
