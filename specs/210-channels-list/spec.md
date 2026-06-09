# Feature Specification: Layer 2 Tool `channels_list`

**Feature Branch**: `210-channels-list`  
**Created**: 2026-06-08  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-210, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Channels Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `channels_list` tool to retrieve YouTube channel resources while staying close to the upstream `channels.list` filter, part-selection, and pagination behavior.

**Why this priority**: This is the core value of YT-210. Layer 2 must expose endpoint-backed channel lookup for raw exploration, debugging, channel identification, and later composition without turning the tool into higher-level channel analytics, ranking, or enrichment.

**Independent Test**: Can be tested by invoking `channels_list` with supported channel lookup filters and confirming the caller receives channel resources, requested resource parts, pagination details when present, and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller provides a valid channel identifier lookup, **When** they call `channels_list`, **Then** the result includes the matching channel resources and preserves the requested resource parts.
2. **Given** a caller provides a valid handle or username-style lookup supported by the endpoint contract, **When** they call `channels_list`, **Then** the result includes matching channel resources and identifies which lookup mode was used.
3. **Given** the upstream result includes additional pages, **When** the caller inspects the tool result, **Then** the next-page token or equivalent pagination information is visible for follow-up calls.
4. **Given** a valid lookup returns no matching channel resources, **When** the caller invokes `channels_list`, **Then** the tool returns a successful empty item collection rather than an error.

---

### User Story 2 - Understand Cost, Access, and Filter Rules Before Calling (Priority: P2)

As a client developer, I can inspect `channels_list` before invoking it and immediately understand that it maps to `channels.list`, costs 1 official quota unit per call, supports documented lookup filters such as `id`, `mine`, `forHandle`, and username-style lookup, and may require eligible authorization for owner-scoped retrieval.

**Why this priority**: Channel lookup is a common dependency for research, direct endpoint use, and later composed workflows. Callers need quota, filter, and auth visibility up front so they can choose the right lookup mode, avoid invalid selector combinations, and understand when user-owned channel access is required.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the upstream identity, quota cost of `1`, auth mode, supported filter modes, pagination behavior, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `channels_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, auth mode, availability state, and supported filter modes.
2. **Given** an example request is shown for `channels_list`, **When** a caller reads the example, **Then** the quota cost of `1` and the selected lookup mode are visible alongside the request shape.
3. **Given** a caller wants to retrieve the authorized user's own channel using `mine`, **When** they inspect the tool contract, **Then** the need for eligible user authorization is clear before invocation.

---

### User Story 3 - Reject Unsupported Channel Lookup Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `channels_list` request uses missing, conflicting, or unsupported lookup filters, so I can correct the request without guessing which channel lookup rule was violated.

**Why this priority**: `channels.list` uses selector-style filters whose combinations matter. Clear validation protects low-level users while keeping the tool faithful to the endpoint rather than inventing fallback lookup behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing filters, conflicting lookup modes, unsupported optional fields, invalid pagination inputs, and missing authorization for `mine`, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits a supported channel lookup filter, **When** they call `channels_list`, **Then** the request is rejected with guidance that one supported lookup mode is required.
2. **Given** a caller provides mutually exclusive channel lookup filters in one request, **When** they call `channels_list`, **Then** the request is rejected with guidance that only one supported lookup mode may be used.
3. **Given** a caller uses `mine` without eligible user authorization, **When** they call `channels_list`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing public channel.

### Edge Cases

- A valid lookup returns no matching channel resources; the result must remain successful and include an empty item collection.
- The upstream response includes a page token; the tool result must preserve the token so the caller can continue listing channel resources.
- The caller provides multiple mutually exclusive channel lookup filters, such as `id` with `mine` or `forHandle` with username-style lookup; the request must be rejected before it is treated as valid endpoint usage.
- The caller uses `mine` without eligible user authorization; the response must surface an access requirement.
- The caller has eligible authorization but lacks access to the owner-scoped channel view requested; the response must distinguish access failure from a no-match public lookup.
- The caller supplies unsupported optional fields, unsupported lookup aliases, malformed handles, empty identifiers, or page-size values outside the supported endpoint contract; the request must be rejected or clearly flagged as unsupported.
- The upstream service returns quota, authorization, missing resource, invalid request, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects channel analytics, channel search ranking, video expansion, playlist expansion, branding updates, or heuristic enrichment; the tool contract must keep those higher-level or separate endpoint behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `channels_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `channels.list` identity, official quota-unit cost of `1`, auth mode, availability state, supported filter modes, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for supported lookup filters including `id`, `mine`, `forHandle`, and username-style lookup; required part selection; pagination inputs; missing filter handling; mutually exclusive filter handling; malformed lookup values; unsupported optional fields; and authorization guidance for owner-scoped retrieval.
- **Red**: Add failing result-contract checks proving that channel resource items, requested parts, successful empty collections, pagination tokens, selected lookup mode, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `channels_list` tool contract and behavior needed for callers to make supported low-level `channels.list` requests and receive near-raw channel collection results.
- **Green**: Include representative examples for channel ID lookup, handle lookup, username-style lookup, authorized `mine` lookup, paginated continuation, empty results, conflicting filters, and missing authorization for owner-scoped retrieval.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `channels_list` request, response, quota, auth, filters, pagination, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for filter and pagination validation, integration-style checks for representative successful and failed channel listing paths, and documentation checks for quota/auth/filter/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `channels_list` responsibility, inputs, outputs, quota cost, auth behavior, lookup-filter constraints, pagination behavior, and no-match behavior.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-210`, the dependency assumptions from YT-110/YT-201/YT-202, focused `channels_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `channels_list`.
- **FR-002**: The `channels_list` tool definition MUST identify its mapped upstream operation as YouTube resource `channels` and method `list`.
- **FR-003**: The `channels_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `channels_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `channels_list` tool metadata MUST state the auth mode and distinguish public lookup modes from owner-scoped lookup modes that require eligible user authorization.
- **FR-006**: The `channels_list` input contract MUST preserve the upstream concepts of channel lookup filters, part selection, pagination tokens, page-size limits, and supported owner-scoped context where those concepts are supported.
- **FR-007**: The `channels_list` input contract MUST document supported lookup modes including `id`, `mine`, `forHandle`, and username-style lookup.
- **FR-008**: The `channels_list` input contract MUST require exactly one supported channel lookup mode for each request.
- **FR-009**: The `channels_list` tool MUST reject missing, empty, unsupported, malformed, or mutually exclusive channel lookup filters with clear caller-facing validation feedback.
- **FR-010**: The `channels_list` tool MUST reject requests that require authorized user context when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-011**: The `channels_list` result MUST preserve returned channel items, requested resource parts, pagination details, selected lookup mode, and relevant request context in a near-raw endpoint-backed shape.
- **FR-012**: The `channels_list` result MUST treat a valid no-match channel lookup as a successful empty collection.
- **FR-013**: The `channels_list` tool MUST surface upstream quota, authorization, missing resource, invalid request, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-014**: The `channels_list` contract MUST remain close to the upstream `channels.list` endpoint and MUST NOT add higher-level channel analytics, ranking, enrichment, video expansion, playlist expansion, branding updates, or heuristic interpretation.
- **FR-015**: The `channels_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, error, and example standards established by YT-201 and YT-202.
- **FR-016**: The `channels_list` tool MUST rely on the existing Layer 1 `channels.list` capability from YT-110 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-017**: The feature MUST include caller-facing examples for at least one channel ID lookup, one handle lookup, one username-style lookup, one authorized `mine` lookup, one paginated request, one empty-result outcome, one conflicting-filter validation failure, and one authorization-sensitive failure.
- **FR-018**: The feature MUST include validation evidence that clients can discover, call, paginate, understand filter and auth requirements, interpret empty results, and handle failures for `channels_list` without consulting implementation-only artifacts.

### Key Entities

- **Channels List Tool**: The public Layer 2 MCP tool named `channels_list`, representing one low-level endpoint-backed channel listing operation.
- **Channel Lookup Filter**: The request selector that determines how channel resources are retrieved, including `id`, `mine`, `forHandle`, and username-style lookup where supported.
- **Part Selection**: The caller-selected resource sections requested for returned channel items.
- **Pagination Cursor**: The token or continuation value that lets callers request subsequent channel result pages.
- **Channel Collection Result**: The returned channel item collection, including successful empty collections and any pagination details.
- **Quota Disclosure**: The caller-facing statement that each `channels_list` invocation costs 1 official quota unit.
- **Auth Requirement Disclosure**: The caller-facing indication of which lookup modes are public and which require eligible user authorization.
- **Availability Caveat**: Any caller-facing note about supported, deprecated, constrained, or documentation-sensitive lookup behavior for channel filters such as username-style lookup.

### Assumptions

- YT-110 provides the Layer 1 `channels.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, error, example, and validation standards this feature must follow.
- `channels_list` is a low-level endpoint-backed tool for direct access, debugging, channel identification, and power-user workflows; higher-level channel analytics, search ranking, enrichment, related-video lookup, playlist expansion, or branding workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `channels.list` quota cost, auth behavior, filter rules, availability state, pagination behavior, and username-style lookup caveats, with any discovered caveats recorded explicitly.
- Representative coverage of channel ID lookup, handle lookup, username-style lookup, authorized `mine` lookup, pagination, empty results, invalid filters, and authorization-sensitive failures is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `channels_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `channels.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can identify all supported `channels_list` lookup modes and determine whether each requires public access or eligible user authorization in under 1 minute by reading the tool contract alone.
- **SC-003**: 100% of representative valid `channels_list` requests return channel items or a successful empty collection with requested parts, selected lookup mode, and pagination details preserved when present.
- **SC-004**: 100% of representative invalid channel lookup requests with missing, malformed, unsupported, or conflicting filters are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-005**: Reviewers can verify in a single review pass that `channels_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example standards.
- **SC-006**: A power user can discover `channels_list`, choose a valid lookup filter, identify required authorization, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-007**: Final review evidence includes passing focused `channels_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
