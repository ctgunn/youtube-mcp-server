# Tasks: Layer 2 Tool `guideCategories_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/data-model.md), [contracts/guideCategories_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/contracts/guideCategories_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository `pytest` run after final code changes plus `ruff check .`. Python code tasks include explicit reStructuredText docstring work.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches different files or has no dependency on incomplete tasks
- **[Story]**: Maps to a user story from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md)
- Every task includes at least one exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the feature-specific files and confirm the local target structure.

- [X] T001 Create the empty Layer 2 guide-categories module file at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T002 [P] Create the empty contract test file at `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`
- [X] T003 [P] Create the empty unit test file at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`
- [X] T004 [P] Create the empty integration test file at `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Resolve the Layer 1 dependency gap and shared export/registration prerequisites before user stories are implemented.

**Critical**: No user story Green implementation can begin until this phase is complete.

- [X] T005 [P] Add failing Layer 1 contract coverage for `guideCategories.list` supporting `part` plus `regionCode`, `id`, optional `hl`, quota cost `1`, API-key auth, and deprecated lifecycle metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_legacy_categories_contract.py`
- [X] T006 Update `build_guide_categories_list_wrapper()` metadata to support dependency-backed `id` lookup and optional `hl` localization while preserving API-key auth, quota cost `1`, and deprecated lifecycle state in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`
- [X] T007 Add or update reStructuredText docstrings for every changed Layer 1 guide-categories function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`
- [X] T008 Run the focused Layer 1 legacy category contract checks and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_legacy_categories_contract.py`

**Checkpoint**: Layer 1 dependency accepts the selector/localization surface that the Layer 2 public contract will expose.

---

## Phase 3: User Story 1 - Retrieve Guide Categories Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `guideCategories_list` with supported part selection and one supported selector, then receive a near-raw guide-category list result or a clear legacy-unavailable response.

**Independent Test**: Invoke the descriptor handler or registered dispatcher with `{"part": "snippet", "regionCode": "US"}` and `{"part": "snippet", "id": "GCQmVzdCBvZiBZb3VUdWJl"}` and verify endpoint, quota, selector, availability, and returned items are preserved.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add failing contract tests for `guideCategories_list` public identity, input schema with `part`, `regionCode`, `id`, `hl`, and list response convention in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`
- [X] T010 [P] [US1] Add failing unit tests for valid region lookup, valid ID lookup, optional localized lookup, wrapper invocation, selector context, requested parts, and near-raw item preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`
- [X] T011 [P] [US1] Add failing integration tests for manually registering `build_guide_categories_list_tool_descriptor()` and invoking region and ID lookups through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py`
- [X] T012 [US1] Run the focused US1 tests and confirm they fail for missing `guideCategories_list` implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Define `GUIDE_CATEGORIES_LIST_TOOL_NAME`, `GUIDE_CATEGORIES_LIST_QUOTA_COST`, selector constants, input schema, and result-shape constants in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T014 [US1] Implement `GuideCategoriesListToolError`, `validate_guide_categories_list_arguments()`, selector normalization, and localization validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T015 [US1] Implement `map_guide_categories_list_result()` to preserve endpoint, quota cost, requested parts, selector context, localization context, deprecated availability state, empty items, and returned upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T016 [US1] Implement `build_guide_categories_list_handler()` and `build_guide_categories_list_tool_descriptor()` using `build_guide_categories_list_wrapper()` and one Layer 1 wrapper call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T017 [US1] Add or update reStructuredText docstrings for all new US1 Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T018 [US1] Run the focused US1 contract, unit, and integration tests and fix retrieval-result failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`

### Refactor for User Story 1

- [X] T019 [US1] Refactor selector/result helper names and remove duplicated code while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Understand Cost, Auth, and Legacy Availability Before Calling (Priority: P2)

**Goal**: A client developer can discover `guideCategories_list` and understand upstream identity, quota cost, API-key auth, required part/selector rules, localization, and deprecated/unavailable platform behavior before invoking it.

**Independent Test**: Inspect tool metadata, description, usage notes, caveats, and examples and verify they expose `guideCategories.list`, quota cost `1`, auth mode `api_key`, availability `deprecated`, required selectors, localization caveat, and out-of-scope boundaries.

### Tests for User Story 2 (Red)

- [X] T020 [P] [US2] Add failing contract tests for metadata safety, quota/auth/availability disclosure, usage notes, caveats, and required examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`
- [X] T021 [P] [US2] Add failing representative catalog alignment tests for `guideCategories_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T022 [P] [US2] Add failing default registry metadata tests for `guideCategories_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T023 [US2] Run the focused US2 metadata tests and confirm they fail before metadata/export/registration implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2 (Green)

- [X] T024 [US2] Implement `GUIDE_CATEGORIES_LIST_DESCRIPTION`, `GUIDE_CATEGORIES_LIST_USAGE_NOTES`, `GUIDE_CATEGORIES_LIST_CAVEATS`, and `GUIDE_CATEGORIES_LIST_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T025 [US2] Implement `build_guide_categories_list_contract()` with `AuthMode.API_KEY`, `AvailabilityState.DEPRECATED`, safe metadata, response convention, response boundary, and shared error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T026 [US2] Export all `GUIDE_CATEGORIES_LIST_*`, validation, mapping, contract, handler, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T027 [US2] Add `guideCategories_list` to representative YouTube tool contracts in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T028 [US2] Register `build_guide_categories_list_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T029 [US2] Add or update reStructuredText docstrings for all new or changed US2 Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T030 [US2] Run the focused US2 contract and registry tests and fix metadata/example/export failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`

### Refactor for User Story 2

- [X] T031 [US2] Refactor metadata/caveat/example wording to avoid drift while preserving quota, auth, deprecated availability, and out-of-scope disclosures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Reject Unsupported Guide Category Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation or safe upstream-error feedback for missing inputs, conflicting selectors, unsupported options, no-match outcomes, deprecated/unavailable behavior, quota issues, and unexpected upstream failures.

**Independent Test**: Submit invalid requests and fake upstream failures to the descriptor handler and verify each response maps to the expected shared Layer 2 category without exposing unsafe diagnostics.

### Tests for User Story 3 (Red)

- [X] T032 [P] [US3] Add failing unit tests for missing `part`, missing selector, conflicting selectors, blank `regionCode`, blank `id`, invalid `hl`, unsupported option fields, and out-of-scope channel/video/search/ranking/enrichment fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`
- [X] T033 [P] [US3] Add failing unit tests for upstream guide category not found, quota exhausted, authorization failure, deprecated endpoint, endpoint unavailable, removed-resource behavior, unexpected upstream failure, and unsafe detail sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`
- [X] T034 [P] [US3] Add failing integration tests for dispatcher-visible validation failures and safe error payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py`
- [X] T035 [US3] Run the focused US3 validation tests and confirm they fail before validation/error mapping implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`

### Implementation for User Story 3 (Green)

- [X] T036 [US3] Complete `validate_guide_categories_list_arguments()` to reject missing `part`, missing selector, conflicting selectors, invalid selector values, invalid localization, unsupported options, and out-of-scope request fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T037 [US3] Complete upstream error mapping for `resource_not_found`, `quota_exhausted`, `authentication_failed`, `authorization_failed`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T038 [US3] Ensure safe error detail sanitization removes API keys, OAuth tokens, raw diagnostics, stack traces, signed URLs, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T039 [US3] Add or update reStructuredText docstrings for all new or changed US3 Python functions and fake wrapper methods in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py`
- [X] T040 [US3] Run the focused US3 unit and integration tests and fix validation/error-mapping failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`

### Refactor for User Story 3

- [X] T041 [US3] Refactor validation and safe-error helpers while keeping US1, US2, and US3 focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and documentation checks across all stories.

- [X] T042 [P] Update YT-223 review notes and any implementation caveats in `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/quickstart.md`
- [X] T043 [P] Review all changed Python files for reStructuredText docstrings on every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py`
- [X] T044 Run the full focused feature verification command from quickstart and fix any failures in `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/quickstart.md`
- [X] T045 Run `pytest` for the full repository and fix any failing tests before completion in `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T046 Run `ruff check .` and fix any lint failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks user story Green implementation because Layer 2 must stay backed by Layer 1.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; delivers MVP retrieval.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can run in parallel with US1 after shared file coordination, but registry/export work is easier after US1 descriptor names exist.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can run in parallel with US1/US2 tests, but its implementation depends on the validator/error-mapper introduced by US1.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP. No dependency on US2 or US3 after Foundational phase.
- **User Story 2 (P2)**: Can be tested independently through metadata and registry inspection; practically depends on the contract/descriptor symbols from US1.
- **User Story 3 (P3)**: Can be tested independently through invalid requests and fake upstream failures; practically depends on the handler/validator surface from US1.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation should be the smallest code needed to pass that story's tests.
- reStructuredText docstrings must be added or updated before each story is marked complete.
- Refactor only after focused tests pass; rerun focused tests after refactor.
- Full repository `pytest` and `ruff check .` are required before feature completion.

---

## Parallel Opportunities

- T002, T003, and T004 can run in parallel because they create separate test files.
- T005 can run in parallel with later test drafting as long as T006 waits for the failing Layer 1 test.
- T009, T010, and T011 can run in parallel because they target separate test files.
- T020, T021, and T022 can run in parallel because they target separate metadata/registry test files.
- T032, T033, and T034 can run in parallel because they target distinct validation/error scenarios.
- T042 and T043 can run in parallel during polish because one updates docs and one reviews Python docstrings.

---

## Parallel Example: User Story 1

```bash
# Launch Red test drafting together:
Task: "T009 [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py"
Task: "T010 [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py"
Task: "T011 [US1] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch metadata and registry Red test drafting together:
Task: "T020 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py"
Task: "T021 [US2] Add representative catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T022 [US2] Add default registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
# Launch validation and safe-error Red test drafting together:
Task: "T032 [US3] Add invalid request validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py"
Task: "T033 [US3] Add upstream error mapping tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_guide_categories.py"
Task: "T034 [US3] Add dispatcher safe-error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_guide_categories_registration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational Layer 1 dependency alignment.
3. Complete Phase 3 User Story 1.
4. Stop and validate `guideCategories_list` retrieval independently with the focused US1 tests.

### Incremental Delivery

1. Add User Story 1 retrieval and result mapping for MVP value.
2. Add User Story 2 metadata, examples, exports, representative catalog, and default registry visibility.
3. Add User Story 3 validation and safe error clarity.
4. Finish with full `pytest`, `ruff check .`, and docstring review.

### Parallel Team Strategy

1. One contributor handles foundational Layer 1 dependency alignment.
2. After foundation, one contributor can implement US1 while another drafts US2 metadata/registry tests.
3. US3 tests can be drafted in parallel, then wired to the validator and error mapper after US1 introduces those functions.

## Notes

- [P] tasks use different files or can be performed without depending on incomplete implementation tasks.
- [US1], [US2], and [US3] labels map directly to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md).
- Tests must fail before implementation begins for the corresponding story.
- Each story has its own independent test criteria and docstring task.
- The feature is not complete until focused tests, full `pytest`, and `ruff check .` pass.
