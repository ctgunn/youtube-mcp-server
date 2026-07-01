# Feature Specification: Layer 2 Tool `members_list`

**Feature Branch**: `226-members-list`  
**Created**: 2026-07-01  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-226, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Channel Members Through a Public Tool (Priority: P1)

As a power user with eligible channel-owner authorization, I can call the low-level `members_list` tool to retrieve channel membership records while staying close to the upstream `members.list` behavior and returned member collection.

**Why this priority**: This is the core value of YT-226. Layer 2 must expose endpoint-backed membership retrieval for direct inspection, debugging, and later composition without turning the tool into a public subscriber lookup, membership administration flow, audience analytics report, ranking workflow, or higher-level enrichment behavior.

**Independent Test**: Can be tested by invoking `members_list` with supported part selection, one supported membership retrieval mode, eligible OAuth-backed owner access, and optional paging input, then confirming the caller receives a near-raw member list result with metadata identifying the mapped upstream operation and selected membership view.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, one supported membership retrieval mode, and eligible owner authorization, **When** they call `members_list`, **Then** the result includes matching member records and preserves operation context for owner-scoped membership retrieval.
2. **Given** a caller provides supported paging input for an eligible membership request, **When** the upstream operation returns a page of members, **Then** the result preserves returned members, selected part context, selected membership mode, and paging context.
3. **Given** a caller wants direct access to membership listing behavior, **When** they use `members_list`, **Then** the tool performs only the member list operation and is not presented as subscriber lookup, membership level lookup, membership management, analytics, recommendation, ranking, or enrichment.

---

### User Story 2 - Understand Cost, OAuth, and Membership Access Before Calling (Priority: P2)

As a client developer, I can inspect `members_list` before invoking it and immediately understand that it maps to `members.list`, costs 2 official quota units per call, requires OAuth-backed owner access, supports part plus mode membership retrieval, and is constrained to channel-membership visibility rules.

**Why this priority**: Membership data is access-sensitive and quota-bearing. Callers need quota, auth-mode, owner-visibility, membership-mode, paging, and unsupported-delegation guidance in discovery, descriptions, and examples before they spend quota or build workflows that depend on channel member data.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `2`, OAuth-required access, owner-only visibility, channel-membership eligibility constraints, required part selection, required mode selection, optional paging inputs, and unsupported delegation boundary are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `members_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `2`, OAuth-required access, owner-only visibility, required part selection, required mode selection, optional paging inputs, and channel-membership eligibility constraints.
2. **Given** an example request is shown for `members_list`, **When** a caller reads the example, **Then** the quota cost of `2`, selected parts, selected membership mode, owner-auth requirement, and expected member-list outcome are visible alongside the request shape.
3. **Given** a caller needs public subscribers, membership levels, membership management, delegated owner context, analytics, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level member listing tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Unsupported or Ineligible Member List Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `members_list` request omits required inputs, uses unsupported membership modes or modifiers, supplies invalid paging input, lacks eligible owner authorization, or asks for behavior outside the membership-list endpoint.

**Why this priority**: `members.list` has a narrower access model than public list endpoints. Clear boundaries help callers distinguish malformed requests, unsupported membership views, ineligible access, valid empty member lists, and upstream failures without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing part selection, missing mode, unsupported mode, unsupported optional fields, invalid paging values, delegation-related inputs, API-key-only access, non-owner OAuth access, and out-of-scope subscriber or analytics requests, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits supported part selection or membership mode, **When** they call `members_list`, **Then** the request is rejected with guidance that both part selection and one supported membership mode are required.
2. **Given** a caller supplies unsupported fields, delegation-related inputs, unsupported membership modes, or invalid paging values, **When** they call `members_list`, **Then** the request is rejected with guidance identifying the unsupported or invalid input.
3. **Given** a caller submits a validly shaped request without eligible OAuth-backed owner access or channel-membership visibility, **When** they call `members_list`, **Then** the response distinguishes access or eligibility failure from malformed input and from successful empty member lists.
4. **Given** a valid owner-authorized request returns no member records for the selected membership mode, **When** the caller receives the result, **Then** the response identifies a successful empty collection rather than a validation, access, or upstream failure.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported membership lookup.
- The caller omits the required membership mode or provides multiple, empty, malformed, unknown, or unsupported mode values; the response must identify invalid membership-mode input.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller provides invalid page tokens, unsupported page sizes, or paging controls outside the documented member-list boundary; the response must identify invalid paging input.
- The caller supplies unsupported optional parameters, delegated owner-context inputs, public subscriber lookup fields, membership-level selectors, management actions, analytics instructions, ranking instructions, summarization instructions, or enrichment instructions; the request must be rejected or clearly flagged as outside this low-level endpoint contract.
- The caller attempts API-key-only access, has OAuth credentials for a non-owner context, lacks channel-membership program eligibility, or lacks the visibility required for member data; the response must preserve access or eligibility meaning without exposing sensitive member details.
- The request is validly shaped and owner-authorized but returns an empty member collection; the result must distinguish an empty successful collection from a failed retrieval.
- The upstream success response omits optional fields or returns partial member resources according to the selected parts; the result must preserve returned fields without fabricating missing membership data.
- The upstream service returns quota, authorization, invalid request, unavailable service, channel-membership eligibility, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects subscriber lookup, membership-level listing, member administration, channel analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `members_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `members.list` identity, official quota-unit cost of `2`, OAuth-required auth disclosure, owner-only and channel-membership access constraints, required part selection, required membership mode, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required part selection, required membership mode, unsupported mode rejection, optional paging boundaries, unsupported option rejection, unsupported delegation inputs, API-key-only access, non-owner OAuth access, channel-membership eligibility failures, empty result handling, and out-of-scope subscriber or analytics requests.
- **Red**: Add failing result-contract checks proving that returned member collection fields, selected part context, selected membership mode, paging context, successful empty outcomes, access or eligibility failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `members_list` tool contract and behavior needed for callers to make supported low-level `members.list` requests and receive near-raw member collection results.
- **Green**: Include representative examples for owner-authorized member retrieval, paged member retrieval, empty successful results, missing part validation failure, missing mode validation failure, unsupported mode validation failure, unsupported option validation failure, ineligible owner or membership access failure, and out-of-scope subscriber or analytics request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `members_list` request, response, quota, auth, owner-visibility, channel-membership constraints, paging, unsupported delegation boundary, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, membership-mode, paging, unsupported-option, unsupported-delegation, and access-boundary validation, integration-style checks for representative successful and failed membership retrieval paths, and documentation checks for quota/auth/access-constraint/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `members_list` responsibility, inputs, outputs, quota cost, OAuth-required behavior, owner-only visibility, channel-membership constraints, membership-mode rules, paging behavior, empty-result behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-226`, the dependency assumptions from YT-126/YT-201/YT-202, focused `members_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `members_list`.
- **FR-002**: The `members_list` tool definition MUST identify its mapped upstream operation as YouTube resource `members` and method `list`.
- **FR-003**: The `members_list` tool metadata MUST record the official quota-unit cost of `2` per call.
- **FR-004**: The `members_list` tool description and usage examples MUST visibly state the official quota-unit cost of `2`.
- **FR-005**: The `members_list` tool metadata MUST state that membership retrieval requires OAuth-backed owner access and MUST make owner-only and channel-membership access constraints visible to callers before invocation.
- **FR-006**: The `members_list` input contract MUST preserve the upstream concepts of required part selection, required membership retrieval mode, optional page token, and optional maximum result count where those concepts are supported.
- **FR-007**: The `members_list` input contract MUST require supported part selection for each retrieval request and MUST document that part selection determines which member properties are returned.
- **FR-008**: The `members_list` input contract MUST require exactly one supported membership retrieval mode for each request and MUST document how the selected mode affects returned membership records.
- **FR-009**: The `members_list` tool MUST support valid owner-authorized requests with no paging token and MUST preserve returned page context when additional pages are available.
- **FR-010**: The `members_list` tool MUST support valid owner-authorized requests that include supported paging inputs, including page token and maximum result count within documented limits.
- **FR-011**: The `members_list` tool MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-012**: The `members_list` tool MUST reject missing, empty, malformed, unknown, multiple, or unsupported membership-mode input with clear caller-facing validation feedback.
- **FR-013**: The `members_list` tool MUST reject unsupported optional parameters, unsupported delegation-related inputs, public subscriber lookup fields, membership-level selectors, invalid page tokens, unsupported maximum result counts, management actions, analytics instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes with clear caller-facing validation feedback.
- **FR-014**: The `members_list` tool MUST reject or clearly categorize API-key-only access, missing OAuth access, non-owner OAuth access, channel-membership ineligibility, and unavailable membership visibility as access or eligibility failures rather than successful member-list results.
- **FR-015**: The `members_list` result MUST preserve member resources, selected part context, selected membership mode, pagination context, relevant owner-access context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-016**: The `members_list` tool MUST distinguish successful empty member collections from validation failures, authorization failures, membership eligibility failures, quota failures, unavailable service responses, and unexpected upstream failures.
- **FR-017**: The `members_list` tool MUST surface upstream quota, authorization, invalid request, membership eligibility, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `members_list` contract MUST document applicable official limits and caveats, including quota cost, OAuth-required access, owner-only visibility, channel-membership access constraints, required part selection, required membership mode, optional paging behavior, unsupported delegation boundary, empty-result behavior, and availability state.
- **FR-019**: The `members_list` contract MUST remain close to the upstream `members.list` endpoint and MUST NOT add public subscriber lookup, membership-level listing, membership administration, delegated owner management, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-020**: The `members_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, pagination, access-boundary, validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `members_list` tool MUST rely on the existing Layer 1 `members.list` capability from YT-126 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for at least one owner-authorized member retrieval request, one paged retrieval request, one empty successful result, one missing-part validation failure, one missing-mode validation failure, one unsupported-mode validation failure, one unsupported option validation failure, one access or membership-eligibility failure, and one out-of-scope subscriber or analytics request rejection.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, owner-only access, channel-membership constraints, part-selection, membership-mode, paging, unsupported-delegation, and failure requirements, interpret list results, and handle failures for `members_list` without consulting implementation-only artifacts.

### Key Entities

- **Members List Tool**: The public Layer 2 MCP tool named `members_list`, representing one low-level endpoint-backed channel membership retrieval operation.
- **Members List Request**: The request shape that combines required part selection, one required membership retrieval mode, and any supported paging inputs.
- **Part Selection**: The caller-selected member resource sections that determine which member properties are returned.
- **Membership Retrieval Mode**: The caller-selected membership view used to retrieve one supported category of member records for an eligible owner context.
- **Pagination Context**: The caller-provided and returned page information that allows clients to traverse supported member result pages.
- **Owner Access Context**: The OAuth-backed channel-owner authorization and channel-membership eligibility context required to access membership records.
- **Members List Result**: The returned member collection, selected parts, membership mode, paging context, access context, and upstream fields produced by a successful `members_list` call.
- **Quota Disclosure**: The caller-facing statement that each `members_list` invocation costs 2 official quota units.
- **Auth and Access Disclosure**: The caller-facing indication that `members_list` requires OAuth-backed owner access and is subject to channel-membership visibility constraints.
- **Unsupported Boundary Guidance**: The caller-facing explanation that subscriber lookup, membership-level lookup, delegation-related inputs, management actions, analytics, ranking, summarization, and enrichment are outside this low-level member listing tool.

### Assumptions

- YT-126 provides the Layer 1 `members.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, pagination, validation, error, example, and validation standards this feature must follow.
- `members_list` is a low-level endpoint-backed tool for direct channel member retrieval, debugging, and power-user workflows; public subscriber lookup, membership-level listing, member administration, analytics, ranking, summarization, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- The existing Layer 1 YT-126 contract treats `part` and `mode` as required, `pageToken` and `maxResults` as optional paging fields, OAuth-backed owner access as required, and delegation-related inputs as unsupported for this slice.
- A valid owner-authorized request may return an empty member list, and that outcome should remain distinguishable from invalid input, ineligible access, and upstream failure.
- The official YouTube Data API documentation and existing project inventory are the default sources for `members.list` quota cost, auth behavior, owner-only visibility, channel-membership eligibility, part-selection rules, mode rules, paging behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. Phase 0 planning research found the current official documentation lists 2 quota units per call, superseding the earlier seed/local inventory value of 1 for this public Layer 2 contract.
- Representative coverage of owner-authorized retrieval, paged retrieval, missing part selection, missing mode, unsupported mode, invalid paging input, unsupported options, unsupported delegation inputs, access or eligibility failure, empty successful results, and returned member collection results is sufficient for this slice.

### Dependencies

- `YT-126` Layer 1 `members.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `members_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `members.list` identity and official quota-unit cost of `2`.
- **SC-002**: A client developer can determine in under 1 minute that `members_list` requires OAuth-backed owner access and channel-membership visibility by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, required membership mode, supported paging inputs, unsupported delegation boundary, and out-of-scope subscriber or analytics behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `members_list`, choose valid inputs, understand the quota and access impact, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `members_list` requests return member collection results with selected part context, selected membership mode, pagination context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, omit mode, use unsupported mode, use invalid paging input, use unsupported options, include unsupported delegation inputs, lack eligible owner access, or request out-of-scope subscriber or analytics behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative empty-result, quota, authorization, channel-membership eligibility, unavailable-service, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `members_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, list result, pagination, access-boundary, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `members_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
