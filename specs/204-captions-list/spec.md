# Feature Specification: Layer 2 Tool `captions_list`

**Feature Branch**: `204-captions-list`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-204, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Caption Tracks Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `captions_list` tool to retrieve the caption tracks associated with a YouTube video while staying close to the upstream `captions.list` selector, part-selection, and pagination behavior.

**Why this priority**: This is the core value of YT-204. Layer 2 must expose endpoint-backed caption-track lookup for raw exploration, debugging, transcript preparation, and advanced workflows before higher-level caption and transcript tools can compose it.

**Independent Test**: Can be tested by invoking `captions_list` with an authorized video-based request and confirming the caller receives caption-track items, requested resource parts, pagination details when present, and endpoint metadata that identifies the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for a target video, **When** they call `captions_list` with a valid caption-track lookup request, **Then** the result includes the available caption tracks for that video and preserves the requested resource parts.
2. **Given** the upstream result includes additional caption-track pages, **When** the caller inspects the tool result, **Then** the next-page token or equivalent pagination information is visible for follow-up calls.
3. **Given** a valid authorized request targets a video with no available caption tracks, **When** the caller invokes `captions_list`, **Then** the tool returns a successful empty item collection rather than an error.

---

### User Story 2 - Understand Cost, Authorization, and Lookup Rules Before Calling (Priority: P2)

As a client developer, I can inspect `captions_list` before invoking it and immediately understand that it maps to `captions.list`, costs 50 official quota units per call, requires OAuth-authorized caption access, and supports clearly documented caption-track lookup inputs.

**Why this priority**: Caption access is permission-sensitive and quota-expensive relative to many read endpoints. Callers need cost, auth, and lookup visibility up front so they can avoid surprising failures, unnecessary quota use, or invalid assumptions that captions are public.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, and examples to confirm the upstream identity, quota cost of `50`, OAuth requirement, supported lookup modes, optional delegation context, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `captions_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and availability state.
2. **Given** an example request is shown for `captions_list`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible authorization are visible alongside the request shape.
3. **Given** a caller needs to list captions in a delegated content-owner context, **When** they inspect the tool contract, **Then** the supported delegation fields and their authorization implications are clear before invocation.

---

### User Story 3 - Reject Unsupported Caption Lookup Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `captions_list` request uses missing, conflicting, or unsupported lookup inputs, so I can correct the request without guessing which caption-track rule was violated.

**Why this priority**: `captions.list` uses selector-style lookup and authorization-sensitive behavior. Clear validation protects low-level users while keeping the tool faithful to the endpoint rather than inventing higher-level recovery behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing video context, conflicting selector inputs, unsupported optional fields, and missing authorization, and confirming the tool rejects them with stable caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required caption-track lookup context, **When** they call `captions_list`, **Then** the request is rejected with guidance that a supported video-based or explicitly supported selector is required.
2. **Given** a caller provides mutually exclusive caption lookup selectors in one request, **When** they call `captions_list`, **Then** the request is rejected with guidance that only one supported lookup mode may be used.
3. **Given** a caller lacks eligible OAuth authorization for the target video or delegated content-owner context, **When** they call `captions_list`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing caption resource.

### Edge Cases

- A valid authorized caption-track lookup returns no items; the result must remain successful and include an empty item collection.
- The upstream response includes a page token; the tool result must preserve the token so the caller can continue listing caption tracks.
- The caller provides multiple mutually exclusive caption lookup selectors; the request must be rejected before it is treated as valid endpoint usage.
- The caller has OAuth authorization but lacks access to the requested video's captions; the response must distinguish access failure from true absence of caption tracks.
- The caller supplies delegated content-owner context without the corresponding eligible authorization; the response must surface the delegation access requirement.
- The caller supplies optional fields or page-size values outside the supported endpoint contract; the request must be rejected or clearly flagged as unsupported.
- The upstream service returns a quota, authorization, invalid-request, unavailable-service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `captions_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `captions.list` identity, official quota-unit cost of `50`, OAuth-required auth mode, availability state, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for supported caption-track lookup inputs, required part selection, pagination inputs, optional delegation context, missing selector handling, mutually exclusive selector handling, and OAuth access guidance.
- **Red**: Add failing result-contract checks proving that caption-track items, requested parts, successful empty collections, pagination tokens, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `captions_list` tool contract and behavior needed for callers to make supported low-level `captions.list` requests and receive near-raw caption-track collection results.
- **Green**: Include representative examples for authorized video caption lookup, paginated continuation, empty caption-track results, and delegated content-owner context.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `captions_list` request, response, quota, auth, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for lookup and pagination validation, integration-style checks for representative successful and failed caption listing paths, and documentation checks for quota/auth/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `captions_list` responsibility, inputs, outputs, quota cost, auth behavior, lookup constraints, pagination behavior, and delegation notes.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-204`, the dependency assumptions from YT-104/YT-201/YT-202, focused `captions_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `captions_list`.
- **FR-002**: The `captions_list` tool definition MUST identify its mapped upstream operation as YouTube resource `captions` and method `list`.
- **FR-003**: The `captions_list` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `captions_list` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `captions_list` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present caption listing as a public API-key-only capability.
- **FR-006**: The `captions_list` input contract MUST preserve the upstream concepts of caption-track lookup context, part selection, pagination tokens, page-size limits, and supported delegation context where those concepts are supported.
- **FR-007**: The `captions_list` input contract MUST require exactly one supported caption-track lookup mode for each request.
- **FR-008**: The `captions_list` tool MUST reject mutually exclusive caption-track lookup combinations with clear caller-facing validation feedback.
- **FR-009**: The `captions_list` tool MUST reject requests that require authorized or delegated access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-010**: The `captions_list` result MUST preserve returned caption-track items, requested resource parts, pagination details, and relevant request context in a near-raw endpoint-backed shape.
- **FR-011**: The `captions_list` result MUST treat a valid no-caption-track response as a successful empty collection.
- **FR-012**: The `captions_list` tool MUST surface upstream quota, authorization, missing resource, invalid request, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-013**: The `captions_list` contract MUST remain close to the upstream `captions.list` endpoint and MUST NOT add higher-level transcript retrieval, caption downloading, language ranking, enrichment, or heuristic interpretation.
- **FR-014**: The `captions_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, and example standards established by YT-201 and YT-202.
- **FR-015**: The `captions_list` tool MUST rely on the existing Layer 1 `captions.list` capability from YT-104 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-016**: The feature MUST include caller-facing examples for at least one authorized video caption lookup, one paginated request, one empty-result outcome, and one delegated content-owner scenario.
- **FR-017**: The feature MUST include validation evidence that clients can discover, call, paginate, understand OAuth requirements, and handle failures for `captions_list` without consulting implementation-only artifacts.

### Key Entities

- **Captions List Tool**: The public Layer 2 MCP tool named `captions_list`, representing one low-level endpoint-backed caption listing operation.
- **Caption Track Lookup**: The request selector that determines which video's caption tracks are listed and whether any delegated content-owner context applies.
- **Part Selection**: The caller-selected resource sections requested for returned caption-track items.
- **Pagination Cursor**: The token or continuation value that lets callers request subsequent caption-track result pages.
- **Caption Track Collection Result**: The returned caption-track item collection, including successful empty collections and any pagination details.
- **Quota Disclosure**: The caller-facing statement that each `captions_list` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that caption listing requires eligible OAuth authorization and may require valid delegated content-owner context for some requests.

### Assumptions

- YT-104 provides the Layer 1 `captions.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, error, example, and validation standards this feature must follow.
- `captions_list` is a low-level endpoint-backed tool for direct access, debugging, transcript preparation, and power-user workflows; higher-level transcript discovery, caption download, ranking, enrichment, or research workflows belong to later Layer 3 features.
- The official YouTube Data API documentation is the default source for `captions.list` quota cost, auth behavior, selector rules, availability state, delegation behavior, and pagination behavior, with any discovered caveats recorded explicitly.
- Representative coverage of authorized video-based lookup, pagination, empty results, invalid selectors, delegated content-owner context, and authorization-sensitive failures is sufficient for this slice.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `captions_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `captions.list` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `captions_list` requires eligible OAuth authorization and can identify whether delegated content-owner context applies by reading the tool contract alone.
- **SC-003**: 100% of representative valid `captions_list` requests return caption-track items or a successful empty collection with requested parts and pagination details preserved when present.
- **SC-004**: 100% of representative invalid caption-track lookup combinations are rejected with caller-facing validation feedback before being treated as supported endpoint requests.
- **SC-005**: Reviewers can verify in a single review pass that `captions_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example standards.
- **SC-006**: A power user can discover `captions_list`, identify the required lookup and pagination inputs, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-007**: Final review evidence includes passing focused `captions_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
