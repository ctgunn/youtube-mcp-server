# Feature Specification: Layer 2 Tool `i18nRegions_list`

**Feature Branch**: `225-i18n-regions-list`  
**Created**: 2026-06-30  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-225, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Localization Regions Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `i18nRegions_list` tool to retrieve YouTube localization-region reference data while staying close to the upstream `i18nRegions.list` behavior and returned region collection.

**Why this priority**: This is the core value of YT-225. Layer 2 must expose the endpoint-backed localization-region lookup for direct inspection, debugging, and later composition without turning the tool into language lookup, country validation, geotargeting, search filtering, recommendation, ranking, or higher-level enrichment behavior.

**Independent Test**: Can be tested by invoking `i18nRegions_list` with supported part selection and, when desired, display-language context, then confirming the caller receives a near-raw localization-region list result with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller provides supported part selection, **When** they call `i18nRegions_list`, **Then** the result includes available localization regions and preserves operation context for region-reference retrieval.
2. **Given** a caller requests region names in a supported display-language context, **When** localization regions are returned, **Then** the result preserves the selected display-language context and returned localized fields without fabricating missing region names.
3. **Given** a caller wants direct localization-region reference behavior, **When** they use `i18nRegions_list`, **Then** the tool performs only the localization-region list operation and is not presented as language lookup, country validation, search filtering, geotargeting, ranking, or enrichment.

---

### User Story 2 - Understand Cost, Auth, and Region Lookup Usage Before Calling (Priority: P2)

As a client developer, I can inspect `i18nRegions_list` before invoking it and immediately understand that it maps to `i18nRegions.list`, costs 1 official quota unit per call, uses the supported read access mode for localization-region lookup, requires supported part selection, and accepts supported display-language input when provided.

**Why this priority**: Localization-region lookup is lightweight but still quota-bearing. Callers need quota, auth-mode, part-selection, display-language behavior, and region lookup guidance in discovery, descriptions, and examples before they spend quota or build workflows that depend on region reference data.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, auth-mode disclosure, required part selection, optional display-language input, default display-language behavior, and region-lookup purpose are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `i18nRegions_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, supported read auth mode, required part selection, optional display-language input, default display-language behavior, and region lookup purpose.
2. **Given** an example request is shown for `i18nRegions_list`, **When** a caller reads the example, **Then** the quota cost of `1`, selected parts, display-language input, and expected region-list outcome are visible alongside the request shape.
3. **Given** a caller needs language codes, translation, geographic targeting, region validation for another endpoint, video search by region, or audience analytics, **When** they inspect the tool contract, **Then** they can tell that `i18nRegions_list` is only a localization-region reference lookup and that those other workflows belong to separate tools or layers.

---

### User Story 3 - Reject Unsupported Localization-Region Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `i18nRegions_list` request omits required part selection, uses unsupported display-language input, or asks for behavior outside the localization-region endpoint, so I can correct the request without guessing which rule was violated.

**Why this priority**: The endpoint is simple, but callers still need predictable boundaries. Clear validation protects callers from ambiguous failures while keeping the tool faithful to the endpoint instead of inventing language lookup, country validation, geotargeting, search, or localization-enrichment behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing part selection, unsupported parts, malformed display-language values, unsupported options, and out-of-scope language, geotargeting, or search requests, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no supported part selection, **When** they call `i18nRegions_list`, **Then** the request is rejected with guidance that part selection is required.
2. **Given** a caller provides a malformed or unsupported display-language value, **When** they call `i18nRegions_list`, **Then** the request is rejected or categorized with guidance that the display-language input is invalid.
3. **Given** a caller requests language lookup, translation, region validation for another endpoint, search filtering, geotargeting, ranking, summarization, or enrichment, **When** they call `i18nRegions_list`, **Then** the request is rejected with guidance that those behaviors are outside this low-level localization-region lookup.
4. **Given** a valid request returns no region items or an upstream access, quota, or availability failure, **When** the caller receives the result, **Then** the response distinguishes empty successful collections from validation failures and upstream failures.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported localization-region lookup.
- The caller omits display-language context; the request must preserve the upstream default display-language behavior without fabricating region names.
- The caller provides an empty, malformed, unknown, or unsupported display-language value; the response must identify invalid localization input or preserve the upstream localization fallback without fabricating region names.
- The caller provides empty, malformed, duplicate, unsupported, or conflicting part selections; the response must identify invalid part-selection input.
- The caller submits unsupported optional parameters, lookup selectors, paging controls, country filters, language filters, search filters, geotargeting instructions, analytics instructions, or content-localization fields that do not belong to localization-region lookup; the response must identify the unsupported fields.
- The caller expects language lookup, translation, country validation, region-code conversion, search by region, audience analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.
- The request is validly shaped but returns an empty region collection; the result must distinguish an empty successful collection from a failed retrieval.
- The upstream success response omits optional fields or returns partial localization-region resources according to the selected parts; the result must preserve returned fields without fabricating missing region data.
- The upstream service returns quota, authorization, invalid request, unavailable service, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `i18nRegions_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `i18nRegions.list` identity, official quota-unit cost of `1`, supported read auth-mode disclosure, required part selection, optional display-language input, default display-language behavior, description-level quota visibility, example-level quota visibility, and region lookup usage guidance.
- **Red**: Add failing request-contract checks for required part selection, optional display-language input, unsupported option rejection, out-of-scope language lookup or geotargeting requests, empty result handling, and upstream error categorization.
- **Red**: Add failing result-contract checks proving that returned localization-region collection fields, selected part context, display-language context, empty successful outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `i18nRegions_list` tool contract and behavior needed for callers to make supported low-level `i18nRegions.list` requests and receive near-raw localization-region collection results.
- **Green**: Include representative examples for default region listing, alternate display-language region listing, empty successful results, missing part validation failure, invalid part validation failure, invalid display-language validation failure, unsupported option validation failure, and out-of-scope language lookup or geotargeting request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `i18nRegions_list` request, response, quota, auth, localization, region guidance, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, display-language, unsupported-option, and out-of-scope behavior, integration-style checks for representative successful and failed localization-region lookup paths, and documentation checks for quota/auth/region-guidance/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `i18nRegions_list` responsibility, inputs, outputs, quota cost, auth behavior, part-selection rules, display-language behavior, empty-result behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-225`, the dependency assumptions from YT-125/YT-201/YT-202, focused `i18nRegions_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `i18nRegions_list`.
- **FR-002**: The `i18nRegions_list` tool definition MUST identify its mapped upstream operation as YouTube resource `i18nRegions` and method `list`.
- **FR-003**: The `i18nRegions_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `i18nRegions_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `i18nRegions_list` tool metadata MUST state the supported read auth mode for localization-region retrieval and MUST make any API-key, OAuth, project-access, or availability limitations visible to callers before invocation.
- **FR-006**: The `i18nRegions_list` input contract MUST preserve the upstream concepts of required part selection and display-language context where those concepts are supported.
- **FR-007**: The `i18nRegions_list` input contract MUST require supported part selection for each retrieval request and MUST document that part selection determines which localization-region properties are returned.
- **FR-008**: The `i18nRegions_list` input contract MUST support display-language context when provided and MUST document default and fallback behavior when localized region names are unavailable.
- **FR-009**: The `i18nRegions_list` tool MUST reject missing, empty, malformed, unsupported, duplicate, or conflicting part selections with clear caller-facing validation feedback.
- **FR-010**: The `i18nRegions_list` tool MUST reject empty, malformed, or unsupported display-language input with clear caller-facing validation feedback and MUST preserve upstream default or fallback localization behavior when the request is otherwise valid.
- **FR-011**: The `i18nRegions_list` tool MUST reject unsupported optional parameters, unsupported lookup selectors, paging controls, country filters, language filters, search filters, geotargeting instructions, audience analytics instructions, translation instructions, language-lookup instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes with clear caller-facing validation feedback.
- **FR-012**: The `i18nRegions_list` result MUST preserve localization-region resources, selected part context, display-language context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-013**: The `i18nRegions_list` tool MUST distinguish successful empty localization-region collections from validation failures, authorization failures, no-match outcomes, quota failures, unavailable service responses, and unexpected upstream failures.
- **FR-014**: The `i18nRegions_list` tool MUST surface upstream quota, authorization, invalid request, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-015**: The `i18nRegions_list` contract MUST document applicable official limits and caveats, including quota cost, auth-mode expectations, required part selection, optional display-language context, default and fallback localization behavior, availability behavior, and unsupported-request boundaries.
- **FR-016**: The `i18nRegions_list` contract MUST remain close to the upstream `i18nRegions.list` endpoint and MUST NOT add language lookup, translation, country validation, region-code conversion, geotargeting, search filtering, recommendation, ranking, summarization, enrichment, analytics, or heuristic classification.
- **FR-017**: The `i18nRegions_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-018**: The `i18nRegions_list` tool MUST rely on the existing Layer 1 `i18nRegions.list` capability from YT-125 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-019**: The feature MUST include caller-facing examples for at least one default region-listing request, one alternate display-language request, one empty successful result, one missing-part validation failure, one invalid-part validation failure, one invalid display-language validation failure, one unsupported option validation failure, and one out-of-scope language lookup or geotargeting request rejection.
- **FR-020**: The feature MUST include validation evidence that clients can discover, call, understand quota, auth, part-selection, display-language, and region-lookup requirements, interpret list results, and handle failures for `i18nRegions_list` without consulting implementation-only artifacts.

### Key Entities

- **I18n Regions List Tool**: The public Layer 2 MCP tool named `i18nRegions_list`, representing one low-level endpoint-backed localization-region retrieval operation.
- **I18n Regions List Request**: The request shape that combines required part selection with optional display-language context.
- **Part Selection**: The caller-selected localization-region resource sections that determine which region properties are returned.
- **Display-Language Context**: The caller-provided language context used to request localized region names when supplied, plus the default display-language behavior used when omitted.
- **I18n Regions List Result**: The returned localization-region collection, selected parts, display-language context, and upstream fields produced by a successful `i18nRegions_list` call.
- **Quota Disclosure**: The caller-facing statement that each `i18nRegions_list` invocation costs 1 official quota unit.
- **Auth and Access Disclosure**: The caller-facing indication of supported read auth mode and access limitations for localization-region retrieval.
- **Region Lookup Guidance**: The caller-facing explanation that the tool returns supported YouTube localization regions for reference workflows and does not translate, validate countries, filter searches, rank, or enrich content.

### Assumptions

- YT-125 provides the Layer 1 `i18nRegions.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, validation, error, example, and validation standards this feature must follow.
- `i18nRegions_list` is a low-level endpoint-backed tool for direct localization-region retrieval, debugging, and compatibility workflows; higher-level language lookup, translation, country validation, region-code conversion, geotargeting, search filtering, recommendation, ranking, summarization, analytics, or enrichment workflows belong to separate endpoint or Layer 3 features.
- Current official YouTube documentation treats `part` as required and `hl` as optional with a default display-language behavior. If the existing Layer 1 YT-125 contract is stricter, this public Layer 2 tool will include a narrow dependency-alignment task so the caller contract remains endpoint-faithful.
- The official YouTube Data API documentation and existing project inventory are the default sources for `i18nRegions.list` quota cost, auth behavior, part-selection rules, display-language behavior, availability state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of default region listing, alternate display-language region listing, missing part selection, invalid part selection, invalid display-language input, unsupported options, empty successful results, out-of-scope language lookup or geotargeting requests, and returned localization-region collection results is sufficient for this slice.

### Dependencies

- `YT-125` Layer 1 `i18nRegions.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `i18nRegions_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `i18nRegions.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute which auth mode applies to `i18nRegions_list` and that it is intended for localization-region lookup by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, optional display-language behavior, default display-language behavior, unsupported-request boundaries, and localization fallback expectations in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `i18nRegions_list`, choose valid inputs, understand the quota impact, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `i18nRegions_list` requests return localization-region collection results with selected part context, display-language context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, use invalid part selection, use invalid display-language input, use unsupported options, or include out-of-scope operation fields are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative empty-result, quota, authorization, unavailable-service, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `i18nRegions_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, list result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `i18nRegions_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
