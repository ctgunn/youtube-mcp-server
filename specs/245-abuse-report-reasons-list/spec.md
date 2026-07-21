# Feature Specification: Layer 2 Tool `videoAbuseReportReasons_list`

**Feature Branch**: `245-abuse-report-reasons-list`  
**Created**: 2026-07-20  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-245, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Abuse Report Reasons Through a Public Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `videoAbuseReportReasons_list` tool to retrieve the catalog of valid YouTube video abuse report reasons in a requested language view so later reporting workflows can present or validate reason choices without hard-coding them.

**Why this priority**: This is the core value of YT-245. Layer 2 must expose direct endpoint-backed abuse-reason lookup for direct inspection, debugging, and later composition without turning the tool into report submission, moderation, recommendation, ranking, summarization, or policy interpretation behavior.

**Independent Test**: Can be tested by invoking `videoAbuseReportReasons_list` with supported part selection and display-language input, then confirming the caller receives a near-raw abuse-report-reason list result with operation identity, quota context, access context, selected parts, localization context, and returned reason data preserved.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection and a supported display-language value, **When** they call `videoAbuseReportReasons_list`, **Then** the result includes the available abuse report reasons for that language view and preserves the mapped operation identity.
2. **Given** the lookup succeeds with localized reason labels or descriptions, **When** the caller inspects the result, **Then** they can identify the requested language context and returned reason fields without fabricated translations.
3. **Given** a caller wants direct reason-catalog lookup behavior, **When** they use `videoAbuseReportReasons_list`, **Then** the tool performs only the reason-list operation and is not presented as video abuse reporting, report submission, moderation action, policy adjudication, recommendation, ranking, summarization, or enrichment.

---

### User Story 2 - Understand Cost, Access, and Localization Before Calling (Priority: P2)

As a client developer, I can inspect `videoAbuseReportReasons_list` before invoking it and immediately understand that it maps to `videoAbuseReportReasons.list`, costs 1 official quota unit per call, uses API-key access expectations, requires part selection and display-language input, and returns localized reason metadata when available.

**Why this priority**: Abuse-reason lookup is lightweight but still quota-bearing and localization-sensitive. Callers need cost, access, required input, localization behavior, examples, and out-of-scope guidance before they spend quota or build video-reporting workflows around the reason catalog.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, API-key access expectation, required part selection, required display-language input, expected list result shape, empty-result behavior, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `videoAbuseReportReasons_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, API-key access expectation, required part selection, required display-language input, and availability state.
2. **Given** an example request is shown for `videoAbuseReportReasons_list`, **When** a caller reads the example, **Then** the quota cost of `1`, selected parts, display-language input, API-key access expectation, and expected abuse-reason list result are visible alongside the request shape.
3. **Given** a caller needs to submit an abuse report, evaluate whether content violates policy, moderate content, rank reasons, or summarize policy guidance, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level lookup tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid or Unsupported Lookup Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `videoAbuseReportReasons_list` request omits required inputs, uses unsupported localization values, includes unsupported modifiers, lacks valid API-key access, or receives an empty or failed upstream lookup.

**Why this priority**: Reason-catalog lookup is often used to prepare later reporting workflows, so ambiguous failures can cause callers to present stale choices or misclassify reporting errors. Clear boundaries help callers distinguish malformed requests, access failures, empty successful lookups, quota failures, upstream failures, and unsupported report-submission requests.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including missing part selection, missing display-language input, invalid localization input, unsupported optional fields, missing access context, empty successful results, quota failures, and out-of-scope video-reporting requests, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits part selection or display-language input, **When** they call `videoAbuseReportReasons_list`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed, empty, unsupported, ambiguous, or conflicting part or localization input, **When** they call `videoAbuseReportReasons_list`, **Then** the request is rejected with guidance identifying the invalid input.
3. **Given** a validly shaped request returns no abuse report reason items for the requested language view, **When** the caller receives the response, **Then** the result is distinguishable from local validation failure, access failure, quota failure, and unexpected upstream failure.
4. **Given** a caller submits inputs intended to report a video or perform moderation, **When** they call `videoAbuseReportReasons_list`, **Then** the request is rejected as outside the reason-lookup boundary rather than being treated as a supported lookup.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported abuse-reason lookup.
- The caller omits required display-language input; the response must identify the missing localization input.
- The caller provides empty, malformed, duplicate, conflicting, unknown, or unsupported part selections; the response must identify invalid part input.
- The caller provides empty, malformed, unknown, unsupported, or conflicting display-language input; the response must identify invalid localization input or preserve upstream localization fallback when the request is otherwise valid.
- The caller supplies paging controls, selectors, report reason identifiers, video identifiers, report text, moderation instructions, policy evaluation instructions, or other optional inputs that do not belong to reason-catalog lookup; the response must identify unsupported input rather than silently ignoring request ambiguity.
- The upstream success response contains zero reason items for the requested language view; the result must distinguish an empty successful collection from a failed retrieval.
- The upstream success response omits optional fields or returns partial reason resources according to selected parts; the result must preserve returned fields without fabricating missing labels, descriptions, or policy details.
- The upstream service returns quota, authorization, invalid request, unavailable service, deprecated behavior, or unexpected failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects video abuse report submission, report-status lookup, moderation action, policy adjudication, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `videoAbuseReportReasons_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `videoAbuseReportReasons.list` identity, official quota-unit cost of `1`, API-key access disclosure, required part selection, required display-language input, description-level quota visibility, example-level quota visibility, and localization guidance.
- **Red**: Add failing request-contract checks for missing part selection, missing display-language input, invalid part selection, invalid localization input, unsupported option rejection, out-of-scope report-submission or moderation requests, empty successful result handling, and API-key access failure categorization.
- **Red**: Add failing result-contract checks proving that returned abuse-reason resources, selected part context, localization context, quota context, access context, empty successful outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `videoAbuseReportReasons_list` tool contract and behavior needed for callers to make supported low-level `videoAbuseReportReasons.list` requests and receive near-raw abuse-reason collection results.
- **Green**: Include representative examples for localized reason lookup, successful empty results, missing part validation failure, missing display-language validation failure, invalid part validation failure, invalid localization validation failure, missing or invalid access failure, quota or upstream failure, and out-of-scope report-submission request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `videoAbuseReportReasons_list` request, response, quota, access, localization, empty-result, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, display-language, unsupported-option, access-boundary, empty-result, and out-of-scope behavior validation, integration-style checks for representative successful and failed abuse-reason lookup paths, and documentation checks for quota/access/localization/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `videoAbuseReportReasons_list` responsibility, inputs, outputs, quota cost, access behavior, localization behavior, empty-result behavior, unsupported behavior, failure categories, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-245`, the dependency assumptions from YT-145/YT-201/YT-202, focused `videoAbuseReportReasons_list` test output, full-suite command output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `videoAbuseReportReasons_list`.
- **FR-002**: The `videoAbuseReportReasons_list` tool definition MUST identify its mapped upstream operation as YouTube resource `videoAbuseReportReasons` and method `list`.
- **FR-003**: The `videoAbuseReportReasons_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `videoAbuseReportReasons_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `videoAbuseReportReasons_list` tool metadata MUST state the API-key access expectation and MUST make that access expectation visible to callers before invocation.
- **FR-006**: The `videoAbuseReportReasons_list` input contract MUST preserve the upstream concepts of required part selection and required display-language input for localized abuse-reason lookup.
- **FR-007**: The `videoAbuseReportReasons_list` input contract MUST require supported part selection for each lookup request and MUST document that part selection determines which abuse-reason properties are returned.
- **FR-008**: The `videoAbuseReportReasons_list` input contract MUST require a supported display-language value for each lookup request and MUST document how localization affects returned reason labels and descriptions.
- **FR-009**: The `videoAbuseReportReasons_list` input contract MUST reject missing, empty, malformed, duplicate, unsupported, ambiguous, or conflicting part selections with clear caller-facing validation feedback.
- **FR-010**: The `videoAbuseReportReasons_list` input contract MUST reject missing, empty, malformed, unsupported, ambiguous, or conflicting display-language inputs with clear caller-facing validation feedback.
- **FR-011**: The `videoAbuseReportReasons_list` input contract MUST reject unsupported optional parameters, paging controls, lookup selectors, video identifiers, report-submission payloads, moderation instructions, policy evaluation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes with clear caller-facing validation feedback.
- **FR-012**: The `videoAbuseReportReasons_list` tool MUST reject or clearly categorize missing, invalid, or unavailable API-key access as an access failure rather than a successful lookup result.
- **FR-013**: The `videoAbuseReportReasons_list` result MUST preserve abuse-report-reason resources, selected part context, localization context, quota context, access context, mapped operation identity, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-014**: The `videoAbuseReportReasons_list` result MUST preserve enough request and result context for callers to identify which language view and part selection produced the returned reason catalog.
- **FR-015**: The `videoAbuseReportReasons_list` result MUST NOT fabricate reason labels, reason descriptions, policy interpretations, moderation outcomes, report-submission status, recommendations, rankings, summaries, or enrichment details that are not returned by the reason-list operation.
- **FR-016**: The `videoAbuseReportReasons_list` tool MUST distinguish successful populated reason collections from successful empty reason collections, validation failures, access failures, quota failures, invalid request failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-017**: The `videoAbuseReportReasons_list` tool MUST surface upstream quota, authorization, invalid request, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-018**: The `videoAbuseReportReasons_list` contract MUST document applicable official limits and caveats, including quota cost, API-key access expectation, required part selection, required display-language input, localization behavior, empty-result behavior, unsupported modifier behavior, and availability state.
- **FR-019**: The `videoAbuseReportReasons_list` contract MUST remain close to the upstream `videoAbuseReportReasons.list` endpoint and MUST NOT add video abuse report submission, report status lookup, moderation action, policy adjudication, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-020**: The `videoAbuseReportReasons_list` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, list result, localization, validation, error, and example standards established by YT-201 and YT-202.
- **FR-021**: The `videoAbuseReportReasons_list` tool MUST rely on the existing Layer 1 `videoAbuseReportReasons.list` capability from YT-145 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-022**: The feature MUST include caller-facing examples for localized reason lookup, successful populated results, successful empty results, missing part validation failure, missing display-language validation failure, invalid part validation failure, invalid localization validation failure, missing access failure, quota or upstream failure, and out-of-scope report-submission request rejection.
- **FR-023**: The feature MUST include validation evidence that clients can discover, call, understand quota, access, part-selection, localization, empty-result, unsupported behavior, failure behavior, and reason-list results for `videoAbuseReportReasons_list` without consulting implementation-only artifacts.

### Key Entities

- **Video Abuse Report Reasons List Tool**: The public Layer 2 MCP tool named `videoAbuseReportReasons_list`, representing one low-level endpoint-backed abuse-reason retrieval operation.
- **Video Abuse Report Reasons List Request**: The request shape that combines required part selection, required display-language input, and any explicitly supported lookup context.
- **Part Selection**: The caller-selected abuse-reason resource sections that determine which reason properties are returned.
- **Display-Language Input**: The caller-provided language preference used to request localized abuse-reason labels and descriptions.
- **Localization Context**: The caller-facing record of the requested language view and any returned localization behavior.
- **Abuse Report Reason Resource**: A returned reason item that callers may present or validate before separate video-reporting workflows.
- **Video Abuse Report Reasons List Result**: The returned reason collection, selected part context, localization context, quota context, access context, mapped operation identity, and returned upstream fields produced by a successful `videoAbuseReportReasons_list` call.
- **Quota Disclosure**: The caller-facing statement that each `videoAbuseReportReasons_list` invocation costs 1 official quota unit.
- **Access Disclosure**: The caller-facing indication that the reason lookup uses API-key access expectations.
- **Unsupported Boundary Guidance**: The caller-facing explanation that abuse-report submission, moderation action, policy adjudication, ranking, summarization, and enrichment are outside this low-level lookup tool.

### Assumptions

- YT-145 provides the Layer 1 `videoAbuseReportReasons.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, access, response-shaping, list result, localization, validation, error, example, and documentation standards this feature must follow.
- `videoAbuseReportReasons_list` is a low-level endpoint-backed tool for direct abuse-reason catalog lookup, debugging, and later workflow composition; abuse-report submission, moderation action, policy interpretation, recommendation, ranking, summarization, analytics, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- Supported behavior for this slice centers on one required part selection plus one required display-language input, matching the existing project-local Layer 1 wrapper boundary.
- A validly shaped request can return an empty reason collection for a language view, and that outcome should remain distinct from validation failures and upstream failures.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, part-selection rules, localization behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-245 seed identifies the official quota-unit cost as `1` for this public Layer 2 contract.

### Dependencies

- `YT-145` Layer 1 `videoAbuseReportReasons.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, localization, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `videoAbuseReportReasons_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `videoAbuseReportReasons.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute that `videoAbuseReportReasons_list` uses API-key access expectations by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, required display-language input, localization behavior, empty-result behavior, and out-of-scope behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `videoAbuseReportReasons_list`, choose valid inputs, understand quota and access impact, and prepare a valid first reason-lookup request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `videoAbuseReportReasons_list` requests return reason-list results with selected part context, localization context, quota context, access context, mapped operation identity, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid reason-lookup requests that omit part selection, omit display-language input, use invalid part selection, use invalid localization input, include unsupported optional inputs, lack valid API-key access, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative empty-result, quota, authorization, invalid-request, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful populated reason-list results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `videoAbuseReportReasons_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, access, availability, list result, localization, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `videoAbuseReportReasons_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
