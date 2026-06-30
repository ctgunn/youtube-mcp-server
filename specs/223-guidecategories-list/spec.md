# Feature Specification: Layer 2 Tool `guideCategories_list`

**Feature Branch**: `223-guidecategories-list`  
**Created**: 2026-06-29  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-223, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Guide Categories Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `guideCategories_list` tool to retrieve YouTube guide category information while staying close to the upstream `guideCategories.list` behavior and returned guide-category collection when that legacy capability is available.

**Why this priority**: This is the core value of YT-223. Layer 2 must expose the endpoint-backed guide-category lookup for direct inspection, compatibility with older category-based workflows, debugging, and later composition without turning the tool into channel lookup, video-category lookup, recommendation, ranking, or higher-level classification.

**Independent Test**: Can be tested by invoking `guideCategories_list` with supported part selection and one supported lookup selector, then confirming the caller receives a near-raw guide-category list result or a clearly categorized legacy-unavailable response with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller provides a supported region selector and supported part selection, **When** they call `guideCategories_list` and the legacy lookup is available, **Then** the result includes guide categories available for that region and preserves operation context for region-based retrieval.
2. **Given** a caller provides one or more guide category identifiers and supported part selection, **When** they call `guideCategories_list` and matching categories are available, **Then** the result includes matching guide-category resources and preserves operation context for ID-based retrieval.
3. **Given** a caller requests localized category text with a supported language preference, **When** guide categories are returned, **Then** the result preserves the selected language context and returned localized fields without fabricating missing translations.
4. **Given** the platform reports that guide-category lookup is deprecated, unavailable, removed from current reference documentation, or otherwise unsupported for the caller's project, **When** the caller invokes `guideCategories_list`, **Then** the response clearly distinguishes legacy platform unavailability from local validation failure, empty successful results, quota failure, and unexpected upstream failure.
5. **Given** a caller wants direct guide-category lookup behavior, **When** they use `guideCategories_list`, **Then** the tool performs only the guide-category list operation and is not presented as channel listing, channel categorization, video-category listing, recommendation, search, ranking, or taxonomy enrichment.

---

### User Story 2 - Understand Cost, Auth, and Legacy Availability Before Calling (Priority: P2)

As a client developer, I can inspect `guideCategories_list` before invoking it and immediately understand that it maps to `guideCategories.list`, costs 1 official quota unit per call, uses the supported read authorization modes for this legacy lookup, and may be deprecated or unavailable on the current YouTube platform.

**Why this priority**: Guide-category lookup is quota-bearing and legacy-sensitive. Callers need quota, auth-mode, part-selection, selector, localization, and availability visibility in discovery, descriptions, and examples before they spend quota or build workflows against a category surface that may not behave like currently active endpoints.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `1`, auth-mode disclosure, required part selection, supported lookup selectors, localization behavior, and deprecation or unavailable-platform caveats are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `guideCategories_list`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `1`, supported read auth mode, required part selection, supported selectors, and current availability caveat.
2. **Given** an example request is shown for `guideCategories_list`, **When** a caller reads the example, **Then** the quota cost of `1`, selected parts, selector choice, optional localization input, and expected list or legacy-unavailable outcome are visible alongside the request shape.
3. **Given** the official platform documents `guideCategories.list` as deprecated or omits it from current endpoint reference navigation, **When** a caller inspects the tool contract, **Then** that caveat is plainly documented without implying the endpoint is a recommended current taxonomy source.
4. **Given** a caller needs active channel or video category data, **When** they inspect the tool contract, **Then** they can tell that `guideCategories_list` is a legacy guide-category lookup and that active channel, video-category, search, or recommendation workflows belong to separate tools.

---

### User Story 3 - Reject Unsupported Guide Category Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `guideCategories_list` request omits required part selection, omits lookup selectors, mixes incompatible selectors, uses unsupported localization input, or requests behavior outside the legacy guide-category endpoint, so I can correct the request without guessing which rule was violated.

**Why this priority**: `guideCategories.list` combines required part selection, lookup selector rules, optional localization, quota-bearing execution, and legacy platform caveats. Clear validation protects callers from ambiguous failures while keeping the tool faithful to the endpoint instead of inventing fallback taxonomy, channel lookup, or category-enrichment behavior.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing part selection, missing selector, conflicting selectors, malformed identifiers, invalid region codes, unsupported language values, unsupported options, and out-of-scope channel or video category requests, then confirming each failure or empty-success case is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits all supported lookup selectors, **When** they call `guideCategories_list`, **Then** the request is rejected with guidance that one supported guide-category lookup selector is required.
2. **Given** a caller combines region-based and ID-based selectors in one request when the contract requires a single lookup mode, **When** they call `guideCategories_list`, **Then** the request is rejected with guidance that lookup modes cannot be combined.
3. **Given** a caller provides no supported part selection, **When** they call `guideCategories_list`, **Then** the request is rejected with guidance that part selection is required.
4. **Given** a caller requests guide categories that are not found, unavailable for the requested region, removed, deprecated, or inaccessible to the selected access context, **When** they call `guideCategories_list`, **Then** the response preserves the appropriate no-match, legacy-unavailable, access, or upstream failure signal using the shared Layer 2 result and error conventions.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported guide-category lookup.
- The caller omits all supported lookup selectors; the response must identify that region-based or ID-based retrieval is required.
- The caller supplies more than one primary lookup selector, such as category identifiers plus a region selector, when the public contract requires a single lookup mode; the response must identify the mutually exclusive selector rule.
- The caller provides empty, malformed, duplicate, excessive, unknown, deprecated, removed, or otherwise unsupported guide category identifiers; the response must identify invalid or unavailable identifier input.
- The caller provides an empty, malformed, unknown, deprecated, or unsupported region code; the response must identify invalid or unavailable region input.
- The caller provides an empty, malformed, unknown, or unsupported language preference for localized text; the response must identify invalid localization input or preserve the upstream localization fallback without fabricating translations.
- The caller requests guide categories for a region that exists but currently has no retrievable guide categories; the result must distinguish an empty successful collection from a failed retrieval.
- The platform returns a deprecation, removed-resource, unsupported-method, unavailable endpoint, or current-reference omission signal; the caller-facing response must distinguish legacy platform unavailability from local validation failures and unexpected errors.
- The upstream success response omits optional fields or returns partial guide-category resources according to the selected parts; the result must preserve returned fields without fabricating missing guide-category data.
- The upstream service returns quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, removed-resource behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects channel listing, channel category assignment, video-category lookup, search, recommendation, ranking, taxonomy migration advice, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `guideCategories_list` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `guideCategories.list` identity, official quota-unit cost of `1`, supported read auth-mode disclosure, required part selection, supported lookup selectors, description-level quota visibility, example-level quota visibility, and legacy availability caveats.
- **Red**: Add failing request-contract checks for required part selection, exactly one supported lookup selector, guide category identifier validation, region-code validation, localization validation, unsupported option rejection, out-of-scope channel or video category requests, empty result handling, no-match handling, and deprecated or unavailable platform behavior.
- **Red**: Add failing result-contract checks proving that returned guide-category collection fields, selected part context, lookup mode, localization context, no-match outcomes, legacy-unavailable outcomes, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `guideCategories_list` tool contract and behavior needed for callers to make supported low-level `guideCategories.list` requests and receive near-raw guide-category collection results or clearly categorized legacy-unavailable responses.
- **Green**: Include representative examples for region-based retrieval, ID-based retrieval, localized retrieval, empty successful results, missing part validation failure, missing selector validation failure, conflicting selector validation failure, invalid identifier validation failure, invalid region validation failure, unsupported option validation failure, and legacy-unavailable platform behavior.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `guideCategories_list` request, response, quota, auth, selector, localization, availability caveat, and example surfaces easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for part-selection, selector, identifier, region, localization, unsupported-option, out-of-scope behavior, and unavailable-platform validation, integration-style checks for representative successful and failed guide-category lookup paths, and documentation checks for quota/auth/availability/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `guideCategories_list` responsibility, inputs, outputs, quota cost, auth behavior, selector rules, localization behavior, legacy availability behavior, no-match behavior, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-223`, the dependency assumptions from YT-123/YT-201/YT-202, focused `guideCategories_list` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `guideCategories_list`.
- **FR-002**: The `guideCategories_list` tool definition MUST identify its mapped upstream operation as YouTube resource `guideCategories` and method `list`.
- **FR-003**: The `guideCategories_list` tool metadata MUST record the official quota-unit cost of `1` per call.
- **FR-004**: The `guideCategories_list` tool description and usage examples MUST visibly state the official quota-unit cost of `1`.
- **FR-005**: The `guideCategories_list` tool metadata MUST state the supported read auth mode for guide-category retrieval and MUST make any API-key, OAuth, project-access, or legacy availability limitations visible to callers before invocation.
- **FR-006**: The `guideCategories_list` input contract MUST preserve the upstream concepts of required part selection, region-based lookup, ID-based lookup, optional localized text preference, and any documented legacy availability caveats where those concepts are supported.
- **FR-007**: The `guideCategories_list` input contract MUST require a supported part selection for each retrieval request and MUST document that part selection determines which guide-category properties are returned.
- **FR-008**: The `guideCategories_list` input contract MUST support region-based retrieval for one supported region code when the legacy endpoint behavior is available.
- **FR-009**: The `guideCategories_list` input contract MUST support ID-based retrieval for one or more guide category identifiers when the legacy endpoint behavior is available.
- **FR-010**: The `guideCategories_list` input contract MUST support localized text preference where the legacy endpoint behavior accepts a language preference and MUST document fallback behavior when localized text is unavailable.
- **FR-011**: The `guideCategories_list` input contract MUST require exactly one supported lookup selector for each request and MUST reject requests that omit selectors or combine mutually exclusive selectors.
- **FR-012**: The `guideCategories_list` tool MUST reject missing, empty, malformed, duplicate, excessive, deprecated, removed, unknown, or unsupported guide category identifier input with clear caller-facing validation feedback or no-match categorization.
- **FR-013**: The `guideCategories_list` tool MUST reject missing, empty, malformed, unknown, deprecated, or unsupported region selector input with clear caller-facing validation feedback or no-match categorization.
- **FR-014**: The `guideCategories_list` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-015**: The `guideCategories_list` tool MUST reject malformed or unsupported localization input with clear caller-facing validation feedback and MUST preserve upstream localization fallback behavior when the request is otherwise valid.
- **FR-016**: The `guideCategories_list` tool MUST reject unsupported optional parameters, unsupported selector combinations, channel-listing filters, channel category assignment requests, video-category lookup requests, search instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes with clear caller-facing validation feedback.
- **FR-017**: The `guideCategories_list` result MUST preserve guide-category resources, selected part context, lookup mode, localization context, relevant availability context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-018**: The `guideCategories_list` tool MUST distinguish successful empty guide-category collections from validation failures, authorization failures, unavailable legacy platform behavior, removed-resource behavior, no-match outcomes, quota failures, and unexpected upstream failures.
- **FR-019**: The `guideCategories_list` tool MUST surface upstream quota, authorization, invalid request, missing resource, unavailable service, deprecated behavior, removed-resource behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-020**: The `guideCategories_list` contract MUST document applicable official limits and caveats, including quota cost, auth-mode expectations, required part selection, mutually exclusive selectors, supported region behavior, supported ID lookup behavior, localization behavior, unavailable or deprecated platform behavior, removed-resource behavior, and current availability state.
- **FR-021**: The `guideCategories_list` contract MUST remain close to the upstream `guideCategories.list` endpoint and MUST NOT add higher-level channel listing, channel category assignment, video-category lookup, search, recommendation, ranking, summarization, enrichment, taxonomy migration, or heuristic classification.
- **FR-022**: The `guideCategories_list` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, list result, selector validation, error, and example standards established by YT-201 and YT-202.
- **FR-023**: The `guideCategories_list` tool MUST rely on the existing Layer 1 `guideCategories.list` capability from YT-123 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-024**: The feature MUST include caller-facing examples for at least one region-based retrieval request, one ID-based retrieval request, one localized retrieval request, one empty successful result, one missing-part validation failure, one missing-selector validation failure, one conflicting-selector validation failure, one invalid-identifier validation failure, one invalid-region validation failure, one unsupported option validation failure, and one legacy-unavailable platform response.
- **FR-025**: The feature MUST include validation evidence that clients can discover, call, understand quota, auth, part-selection, selector, localization, and availability requirements, interpret list results, and handle failures for `guideCategories_list` without consulting implementation-only artifacts.

### Key Entities

- **Guide Categories List Tool**: The public Layer 2 MCP tool named `guideCategories_list`, representing one low-level endpoint-backed guide-category retrieval operation.
- **Guide Categories List Request**: The request shape that combines required part selection, exactly one supported lookup selector, and any supported localization input.
- **Part Selection**: The caller-selected guide-category resource sections that determine which category properties are returned.
- **Region Selector**: The caller-provided region code for retrieving guide categories associated with one supported country or region.
- **Guide Category Identifier Selector**: The caller-provided selector for direct retrieval of one or more guide categories by identifier.
- **Localization Context**: The caller-provided language preference and any returned localization behavior for guide-category text fields.
- **Guide Categories List Result**: The returned guide-category collection, lookup mode, selected parts, localization context, availability context, and upstream fields produced by a successful `guideCategories_list` call.
- **Quota Disclosure**: The caller-facing statement that each `guideCategories_list` invocation costs 1 official quota unit.
- **Auth and Access Disclosure**: The caller-facing indication of supported read auth mode and access limitations for guide-category retrieval.
- **Legacy Availability Disclosure**: The caller-facing explanation that guide-category lookup is a deprecated or legacy platform capability and may be unavailable or removed in current YouTube Data API behavior.

### Assumptions

- YT-123 provides the Layer 1 `guideCategories.list` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, list result, selector validation, error, example, and validation standards this feature must follow.
- `guideCategories_list` is a low-level endpoint-backed tool for direct legacy guide-category retrieval, debugging, and compatibility workflows; higher-level channel lookup, channel classification, video-category lookup, recommendation, ranking, summarization, analytics, enrichment, or taxonomy migration workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation and existing project inventory are the default sources for `guideCategories.list` quota cost, auth behavior, part-selection rules, selector behavior, localization behavior, availability state, deprecation state, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of region-based retrieval, ID-based retrieval, localized retrieval, missing part selection, missing selectors, conflicting selectors, invalid identifiers, invalid regions, invalid localization, unsupported options, empty successful results, legacy-unavailable behavior, and returned guide-category collection results is sufficient for this slice.

### Dependencies

- `YT-123` Layer 1 `guideCategories.list` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `guideCategories_list` discovery metadata, descriptions, and examples produced by this feature display the mapped `guideCategories.list` identity and official quota-unit cost of `1`.
- **SC-002**: A client developer can determine in under 1 minute which auth mode and legacy availability limitations apply to `guideCategories_list` by reading the tool contract alone.
- **SC-003**: A client developer can identify the required part selection, supported region-based lookup, supported ID-based lookup, optional localization behavior, and mutually exclusive selector rule in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `guideCategories_list`, choose a valid lookup mode, understand the legacy caveat, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `guideCategories_list` requests return guide-category collection results or legacy-unavailable outcomes with lookup mode, selected part context, localization context, availability context, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid list requests that omit part selection, omit selectors, combine selectors, use invalid identifiers, use invalid regions, use invalid localization, use unsupported options, or include out-of-scope operation fields are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative no-match, empty-result, deprecated, removed-resource, unavailable-platform, quota, authorization, unavailable-service, and unexpected upstream scenarios are distinguishable from successful populated results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `guideCategories_list` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, availability, list result, selector validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `guideCategories_list` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
