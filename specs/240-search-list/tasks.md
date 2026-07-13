# Tasks: Layer 2 Tool `search_list`

**Input**: Design documents from /Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/data-model.md), [contracts/search_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/contracts/search_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before story completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the new search Layer 2 family and test files without adding user-facing behavior.

- [X] T001 [P] Create the empty concrete search Layer 2 family module with module-level documentation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T002 [P] Create the search contract test file for public metadata and examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py
- [X] T003 [P] Create the search unit test file for validation, result mapping, and error behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T004 [P] Create the search registration test file for descriptor and dispatcher execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add failing shared-surface checks and minimal placeholders that block story work until the public search tool can be exported and registered consistently.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add a failing shared package export test for `SEARCH_LIST_TOOL_NAME` and `build_search_list_tool_descriptor()` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T006 [P] Add a failing scaffold test proving the `search` resource family owns `search_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T007 [P] Add a failing default catalog test proving `search_list` is expected as a concrete endpoint-backed tool in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 Implement minimal public placeholders for search constants and descriptor exports without executable behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T009 Export the minimal search placeholders from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T010 Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py` from /Users/ctgunn/Projects/youtube-mcp-server and confirm only intended search behavior remains red in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Search YouTube Resources Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `search_list` with supported search inputs and receive a near-raw search result collection with endpoint, quota, query, filter, access, paging, and empty-result context.

**Independent Test**: Invoke `search_list` through its descriptor or dispatcher with valid public and restricted search requests, then confirm the handler calls the Layer 1 search wrapper once and returns search result references without fabricated resource hydration or higher-level enrichment.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `SEARCH_LIST_TOOL_NAME`, quota cost `100`, conditional auth mode, input schema, `build_search_list_contract()`, and list response convention in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py
- [X] T012 [P] [US1] Add failing unit tests for `validate_search_list_arguments()` accepting valid keyword, type-filtered, channel-scoped, date-filtered, locale-refined, restricted, and paginated search requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T013 [US1] Add failing unit tests for `map_search_list_result()` preserving endpoint, quota, items, empty marker, query context, filter context, access context, and pagination tokens in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T014 [US1] Add failing unit tests proving `build_search_list_handler()` selects API-key auth for public search, OAuth auth for restricted search, calls `build_search_list_wrapper()` once, and never leaks credentials in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T015 [P] [US1] Add failing integration tests proving `build_search_list_tool_descriptor()` registers and executes through `InMemoryToolDispatcher` for valid public and restricted search requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py
- [X] T016 [P] [US1] Add failing default registry tests proving `search_list` appears in `InMemoryToolDispatcher().list_tools()` and can be called for a valid public search request in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py

### Implementation for User Story 1 (Green)

- [X] T017 [US1] Define `SEARCH_LIST_*` constants, supported filter sets, unsafe detail keys, and input schema requiring `part` and `q` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T018 [US1] Implement `SearchListToolError`, search error sanitization, and shared safe details for search list failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T019 [US1] Implement `build_search_list_contract()` with `search.list` identity, conditional auth mode, quota cost `100`, list response convention, and near-raw response boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T020 [US1] Implement `validate_search_list_arguments()` for required non-empty `part` and `q`, supported optional filters, restricted filter exclusivity, video-only filter compatibility, and pagination shape in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T021 [US1] Implement conditional access-context selection for `search_list` with API-key public search and OAuth-backed restricted search paths in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T022 [US1] Implement `map_search_list_result()` to preserve endpoint, quota, items, empty marker, query context, filter context, access context, and pagination context without fabricated hydrated resource data in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T023 [US1] Implement `_default_search_list_executor()` returning deterministic representative search result and empty result data in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T024 [US1] Implement `build_search_list_handler()` using `build_search_list_wrapper()` and one Layer 1 wrapper call per valid request in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T025 [US1] Implement `build_search_list_tool_descriptor()` with callable handler, input schema, and metadata wiring in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T026 [US1] Export `SEARCH_LIST_*`, `SearchListToolError`, `build_search_list_contract()`, `build_search_list_handler()`, `build_search_list_tool_descriptor()`, `map_search_list_result()`, and `validate_search_list_arguments()` from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T027 [US1] Register `build_search_list_tool_descriptor()` in the default dispatcher tool list in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T028 [US1] Add reStructuredText docstrings for every new or modified production and fake test helper function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py

### Refactor and Validation for User Story 1

- [X] T029 [US1] Refactor US1 implementation for naming, helper reuse, narrow endpoint scope, and no-hydration result boundaries in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T030 [US1] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from /Users/ctgunn/Projects/youtube-mcp-server and fix US1 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Search Cost, Filters, Access, and Pagination Before Calling (Priority: P2)

**Goal**: A client developer can inspect `search_list` discovery metadata, descriptions, usage notes, caveats, and examples and understand quota, conditional auth, required inputs, supported filters, pagination, empty-result behavior, no-hydration boundaries, safe failures, and out-of-scope workflows before invocation.

**Independent Test**: Review `search_list` metadata and examples from its descriptor and catalog entries, then confirm mapped endpoint, quota cost, auth paths, required `part` and `q`, filter compatibility, paging rules, no-hydration boundary, safe failures, and out-of-scope workflows are visible without reading implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T031 [P] [US2] Add failing metadata tests for description, usage notes, caveats, examples, quota cost `100`, conditional auth disclosure, required `part` and `q`, supported filters, pagination, empty-result behavior, no-hydration boundary, and out-of-scope workflows in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py
- [X] T032 [US2] Add failing example coverage tests for public keyword search, type-filtered search, channel-scoped search, date and locale refinement, restricted OAuth search, paginated search, missing input, incompatible filter, restricted filter conflict, quota or upstream failure, and out-of-scope enrichment request in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py
- [X] T033 [P] [US2] Add failing shared catalog tests proving `search_list` uses concrete contract metadata and no duplicate representative placeholder in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T034 [P] [US2] Add failing common contract tests for `search_list` public exports, examples, and catalog participation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T035 [US2] Add `SEARCH_LIST_DESCRIPTION`, `SEARCH_LIST_USAGE_NOTES`, `SEARCH_LIST_CAVEATS`, and `SEARCH_LIST_CALLER_EXAMPLES` covering all quickstart examples in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T036 [US2] Wire search examples, usage notes, caveats, auth mode, availability state, response convention, response boundary, and quota caveat into `build_search_list_contract()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T037 [US2] Replace or supersede the representative `_contract` for `search.list` with `build_search_list_contract()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T038 [US2] Ensure `search_list` metadata and examples are exposed consistently through public package exports in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T039 [US2] Add reStructuredText docstrings for every new or modified metadata/catalog helper function touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py

### Refactor and Validation for User Story 2

- [X] T040 [US2] Refactor metadata text to remove duplicated shared wording while preserving quota, conditional auth, required inputs, filter compatibility, pagination, empty-result, no-hydration, and scope guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T041 [US2] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` from /Users/ctgunn/Projects/youtube-mcp-server and fix US2 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid or Restricted Search Requests Clearly (Priority: P3)

**Goal**: Callers receive clear validation, access, and upstream failure feedback for missing inputs, malformed or incompatible filters, invalid pagination, restricted filters without OAuth, quota failures, unavailable service, deprecated endpoint behavior, unexpected upstream failure, and out-of-scope enrichment requests.

**Independent Test**: Submit representative invalid and ineligible `search_list` requests through validator, handler, descriptor, and dispatcher paths, then confirm each failure uses safe categories and sanitized details while successful populated and empty search results remain distinct.

### Tests for User Story 3 (Red)

- [X] T042 [P] [US3] Add failing unit validation tests for missing `part`, missing `q`, blank `part`, blank `q`, non-string inputs, unsupported fields, out-of-scope enrichment fields, invalid page token, and out-of-range `maxResults` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T043 [US3] Add failing unit tests for restricted filter conflicts, restricted filters without OAuth, video-only refinements without `type=video`, malformed date/language/region/location inputs where locally validated, and successful empty result classification in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T044 [US3] Add failing unit tests for missing credentials, invalid credentials, quota failure, authorization failure, upstream invalid request, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized unsafe upstream details in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py
- [X] T045 [P] [US3] Add failing integration tests for invalid dispatcher requests, restricted access failures, safe upstream failures, empty successful results, and populated search results staying distinct from failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py
- [X] T046 [P] [US3] Add failing contract tests proving failure examples cover missing input, incompatible filter, invalid pagination, restricted access, quota or upstream failure, and out-of-scope enrichment request rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py

### Implementation for User Story 3 (Green)

- [X] T047 [US3] Expand `validate_search_list_arguments()` to reject malformed required inputs, unsupported fields, invalid pagination, out-of-scope enrichment fields, and incompatible search filters with safe field details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T048 [US3] Implement safe API-key and OAuth authentication and authorization failure handling for search requests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T049 [US3] Implement upstream error mapping for quota, invalid request, authorization, unavailable service, deprecated behavior, unexpected upstream failure, and sanitized details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T050 [US3] Ensure descriptor and dispatcher handlers surface `SearchListToolError` without leaking API keys, OAuth tokens, authorization headers, stack traces, raw upstream bodies, or unsafe request context in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T051 [US3] Preserve successful empty search collections as `empty: true` results distinct from validation, access, quota, and upstream failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T052 [US3] Add or update failure examples and contract metadata for all safe search error categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T053 [US3] Add reStructuredText docstrings for every new or modified validation, access, result, and error-mapping function touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py

### Refactor and Validation for User Story 3

- [X] T054 [US3] Refactor safe error helpers and invalid-request branches while preserving clear field-level feedback in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T055 [US3] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py` from /Users/ctgunn/Projects/youtube-mcp-server and fix US3 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, verification, documentation, and full-suite confidence.

- [X] T056 [P] Review the implemented contract against /Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/contracts/search_list.md and update mismatches in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T057 [P] Review quickstart examples against /Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/quickstart.md and update mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py
- [X] T058 [P] Review every new or modified Python function for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py
- [X] T059 Run focused quickstart verification command from /Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/quickstart.md and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T060 Run `pytest` from /Users/ctgunn/Projects/youtube-mcp-server and fix any repository test failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T061 Run `ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server and fix any code-quality failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py
- [X] T062 Record final focused, full-suite, lint, and docstring evidence for YT-240 in /Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/tasks.md

### Final Verification Evidence

- Matched seed slice: YT-240 (`240-search-list`)
- Focused quickstart verification: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_search_contract.py tests/unit/test_youtube_search.py tests/integration/test_youtube_search_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` -> 235 passed
- Full repository test suite: `PYTHONPATH=src python3 -m pytest` -> 3173 passed
- Lint: `python3 -m ruff check .` -> All checks passed
- Python docstring audit for new/modified Python functions -> `missing_count 0`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001-T004 can start immediately.
- **Phase 2 Foundational**: Depends on setup context from Phase 1; blocks user story work.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP executable search tool.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 if descriptor/contract ownership is coordinated, but final metadata validation expects US1 contract builders to exist.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 if validator/error-helper ownership is coordinated, but final invalid-request validation expects US1 handler scaffolding to exist.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Start after Phase 2; no dependency on US2 or US3; recommended MVP scope.
- **US2 (P2)**: Start after Phase 2; depends on the same public contract surface as US1 but remains independently testable through metadata and catalog assertions.
- **US3 (P3)**: Start after Phase 2; depends on the same validator/handler surface as US1 but remains independently testable through invalid input and safe error assertions.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation tasks begin.
- Contract, unit, and integration tests marked `[P]` can be written in parallel when they target different files or independent sections.
- Implementation tasks that touch /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py should be sequenced to avoid conflicting edits.
- Docstring tasks must complete before the story checkpoint is considered done.
- Refactor tasks must preserve focused test success before moving to the next story or final polish.

---

## Parallel Execution Examples

### User Story 1

```text
Task: "T011 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py"
Task: "T012 [P] [US1] Add failing unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py"
Task: "T015 [P] [US1] Add failing integration descriptor tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py"
Task: "T016 [P] [US1] Add failing default registry tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T031 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py"
Task: "T033 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T034 [P] [US2] Add failing common contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

### User Story 3

```text
Task: "T042 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py"
Task: "T045 [P] [US3] Add failing dispatcher invalid-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py"
Task: "T046 [P] [US3] Add failing failure-example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup tasks T001-T004.
2. Complete Phase 2 foundational tasks T005-T010.
3. Complete Phase 3 US1 tasks T011-T030.
4. Validate `search_list` independently with descriptor and dispatcher calls for valid public and restricted search.
5. Stop for MVP review before metadata enrichment and invalid-request hardening if incremental delivery is desired.

### Incremental Delivery

1. Setup and foundation establish the search public surface.
2. US1 adds executable search listing and default registration.
3. US2 makes the tool self-explanatory through discovery, examples, catalog metadata, conditional auth guidance, filter compatibility, pagination, empty-result behavior, and caveats.
4. US3 hardens invalid input, access failures, upstream failures, empty-result distinction, and safe sanitization.
5. Polish runs focused quickstart checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person can prepare setup files while another adds scaffold/export tests.
2. After Phase 2, separate contributors can write US1, US2, and US3 Red tests in parallel.
3. Coordinate implementation edits to /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py because most Green tasks converge there.
4. Keep final validation serialized so full-suite and lint evidence reflect the final combined state.

---

## Task Summary

- **Total tasks**: 62
- **Setup tasks**: 4
- **Foundational tasks**: 6
- **US1 tasks**: 20
- **US2 tasks**: 11
- **US3 tasks**: 14
- **Polish tasks**: 7
- **Suggested MVP scope**: Complete through US1, tasks T001-T030.
