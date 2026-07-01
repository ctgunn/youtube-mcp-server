# Tasks: Layer 2 Tool `i18nRegions_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/data-model.md), [contracts/i18nRegions_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/contracts/i18nRegions_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository `pytest` run after final code changes plus `ruff check .`. Python code tasks include explicit reStructuredText docstring work.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches different files or has no dependency on incomplete tasks
- **[Story]**: Maps to a user story from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/spec.md)
- Every task includes at least one exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature-specific test files and confirm the local target structure.

- [X] T001 Review YT-225 plan, contract, data model, and quickstart before implementation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/plan.md`
- [X] T002 [P] Create the focused contract test file with a module docstring at `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`
- [X] T003 [P] Create the focused unit test file with a module docstring at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`
- [X] T004 [P] Create the focused integration test file with a module docstring at `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Resolve the Layer 1 dependency gap and add shared Red coverage before user story implementation.

**Critical**: No user story Green implementation can begin until this phase is complete.

- [X] T005 [P] Add failing Layer 1 contract coverage proving `i18nRegions.list` accepts omitted `hl`, preserves `part` plus `hl`, exposes quota cost `1`, uses API-key auth, and remains active in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py`
- [X] T006 [P] Add failing Layer 1 unit coverage proving `build_i18n_regions_list_wrapper()` requires `part`, treats `hl` as optional, rejects unsupported fields, and preserves existing `part` plus `hl` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T007 Update `build_i18n_regions_list_wrapper()` metadata and validation to make `hl` optional while preserving API-key auth, quota cost `1`, active lifecycle state, and existing valid calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`
- [X] T008 Add or update reStructuredText docstrings for every changed Layer 1 localization function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`
- [X] T009 [P] Add failing shared scaffolding coverage requiring `i18nRegions_list` symbols in the localization resource family in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T010 Run foundational Red/Green checks and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py`

**Checkpoint**: Layer 1 accepts the endpoint-faithful `part` plus optional `hl` surface and shared Red coverage is in place.

---

## Phase 3: User Story 1 - Retrieve Localization Regions Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `i18nRegions_list` with `part=snippet` and optional `hl`, then receive a near-raw localization-region list result with endpoint, quota, requested part, active availability, and returned region fields preserved.

**Independent Test**: Invoke the descriptor handler or registered dispatcher with `{"part": "snippet"}` and `{"part": "snippet", "hl": "es"}` and verify both produce endpoint-backed list results with quota cost `1`, requested parts, active availability, items, and display-language context when supplied.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `i18nRegions_list` public exports, input schema with required `part` and optional `hl`, upstream identity, active availability, quota cost `1`, and API-key auth in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`
- [X] T012 [P] [US1] Add failing unit tests for accepting default and display-language region requests plus mapping populated and empty upstream list payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`
- [X] T013 [P] [US1] Add failing integration tests for manually registering `build_i18n_regions_list_tool_descriptor()` and invoking default and display-language lookups through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py`
- [X] T014 [US1] Run the focused US1 tests and confirm they fail for missing `i18nRegions_list` implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Define `I18N_REGIONS_LIST_TOOL_NAME`, `I18N_REGIONS_LIST_QUOTA_COST`, supported part constants, input schema, description, usage notes, caveats, examples, and result-boundary constants in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T016 [US1] Implement `I18nRegionsListToolError` and `validate_i18n_regions_list_arguments()` for required `part=snippet`, optional `hl`, and unsupported field rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T017 [US1] Implement `map_i18n_regions_list_result()` preserving endpoint, quota cost, requested parts, active availability, localization context, items, kind, and etag in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T018 [US1] Implement `build_i18n_regions_list_contract()`, `build_i18n_regions_list_handler()`, and `build_i18n_regions_list_tool_descriptor()` using `build_i18n_regions_list_wrapper()` and one Layer 1 wrapper call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T019 [US1] Export `i18nRegions_list` symbols from the shared package in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T020 [US1] Register `build_i18n_regions_list_tool_descriptor()` in the default dispatcher registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified function touched by US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T022 [US1] Run the focused US1 contract, unit, and integration tests and fix retrieval-result failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`

### Refactor for User Story 1

- [X] T023 [US1] Refactor US1 region constants, validator, result mapper, handler, and descriptor for naming consistency with `i18nLanguages_list` while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Auth, and Region Lookup Usage Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, descriptions, usage notes, and examples to understand endpoint identity, quota cost, auth mode, required `part`, optional `hl`, default display-language behavior, active availability, and out-of-scope boundaries before invoking the tool.

**Independent Test**: Inspect the `i18nRegions_list` descriptor and shared catalog entry and confirm quota cost `1`, API-key auth, active availability, upstream `i18nRegions.list`, `part=snippet`, optional `hl`, default display-language behavior, empty-result behavior, and non-geotargeting/non-language-lookup scope are visible without calling the handler.

### Tests for User Story 2 (Red)

- [X] T024 [P] [US2] Add failing contract tests for metadata safety, quota/auth/availability disclosure, usage notes, caveats, response convention, response boundary, and required example names in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`
- [X] T025 [P] [US2] Add failing representative catalog alignment tests for `i18nRegions_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T026 [P] [US2] Add failing shared contract coverage requiring safe public metadata for `i18nRegions_list` active API-key list behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T027 [P] [US2] Add failing default registry metadata tests for public discovery of `i18nRegions_list` quota, auth, active availability, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T028 [US2] Run the focused US2 metadata tests and confirm they fail before metadata/export/registration implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2 (Green)

- [X] T029 [US2] Populate caller-facing examples `default_region_listing`, `display_language_region_listing`, `empty_success`, `missing_part`, `invalid_part`, `invalid_display_language`, `unsupported_option`, and `out_of_scope_language_or_geotargeting_request` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T030 [US2] Add `i18nRegions_list` to the representative YouTube contract examples catalog in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Update `build_i18n_regions_list_contract()` response convention, response boundary, usage notes, caveats, and error categories for localization-region lookup in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T032 [US2] Ensure `i18nRegions_list` descriptor metadata includes examples and remains free of API keys, OAuth tokens, raw diagnostics, signed URLs, and stack traces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for every new or modified function touched by US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T034 [US2] Run the focused US2 contract, catalog, common-contract, and registry tests and fix metadata/example/export failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`

### Refactor for User Story 2

- [X] T035 [US2] Refactor region metadata, caveat, response-boundary, and example wording to avoid drift while preserving quota, auth, active availability, optional `hl`, and out-of-scope disclosures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`

**Checkpoint**: User Story 2 is independently functional and the discovery surface is reviewable before invocation.

---

## Phase 5: User Story 3 - Reject Unsupported Localization-Region Requests Clearly (Priority: P3)

**Goal**: Invalid `i18nRegions_list` requests and upstream failures produce clear safe categories without exposing secrets or implying unsupported language lookup, translation, country validation, geotargeting, search filtering, ranking, summarization, enrichment, or analytics behavior.

**Independent Test**: Submit invalid requests directly to the validator and through the dispatcher, then confirm missing/invalid `part`, invalid `hl`, unsupported fields, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and unexpected failures are categorized distinctly and safely.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Add failing unit tests for missing `part`, invalid `part`, invalid `hl`, unsupported selectors, language filters, country validation fields, geotargeting fields, search fields, ranking fields, summarization fields, enrichment fields, and analytics fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`
- [X] T037 [P] [US3] Add failing unit tests for upstream invalid request, authentication failure, authorization failure, quota exhausted, resource not found, endpoint unavailable, unexpected upstream failure, and unsafe detail sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`
- [X] T038 [P] [US3] Add failing integration tests for dispatcher-visible validation failures and safe upstream error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py`
- [X] T039 [P] [US3] Add failing contract tests proving public metadata, examples, results, and errors contain no API keys, OAuth tokens, stack traces, signed URLs, raw bodies, or raw upstream diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`
- [X] T040 [US3] Run the focused US3 validation tests and confirm they fail before validation/error mapping implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`

### Implementation for User Story 3 (Green)

- [X] T041 [US3] Complete `validate_i18n_regions_list_arguments()` to reject missing `part`, invalid part selections, invalid display-language input, unsupported options, and out-of-scope request fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T042 [US3] Implement upstream error mapping for invalid request, authentication, authorization, quota, endpoint unavailable, resource not found, and upstream failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T043 [US3] Harden handler error paths so dispatcher calls expose safe caller-facing failures without leaking credentials or raw diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T044 [US3] Add or update reStructuredText docstrings for every new or modified function and fake wrapper method touched by US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py`
- [X] T045 [US3] Run the focused US3 unit and integration tests and fix validation/error-mapping failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`

### Refactor for User Story 3

- [X] T046 [US3] Refactor validation and safe-error helpers while keeping US1, US2, and US3 focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`

**Checkpoint**: All user stories are independently functional and safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature, update review evidence, and ensure no cross-story regressions remain.

- [X] T047 [P] Update YT-225 review evidence notes after implementation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/quickstart.md`
- [X] T048 [P] Review all changed Python files for reStructuredText docstrings on every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py`
- [X] T049 Run the full focused feature verification command from quickstart and fix any failures in `/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/quickstart.md`
- [X] T050 Run `pytest` for the full repository and fix any failing tests before completion in `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T051 Run `ruff check .` and fix any lint failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T052 Confirm `i18nRegions_list` scope excludes language lookup, translation, country validation, region-code conversion, geotargeting, search filtering, ranking, summarization, enrichment, analytics, and aggregation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks user story Green implementation because the public Layer 2 contract must stay backed by the Layer 1 wrapper.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; delivers MVP retrieval.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can run after US1 descriptor shape exists; Red tests can be drafted earlier with file coordination.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can run after US1 validator/handler shape exists; Red tests can be drafted earlier with file coordination.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP. No dependency on US2 or US3 after Foundational phase.
- **User Story 2 (P2)**: Can be tested independently through metadata and registry inspection; practically depends on the contract/descriptor symbols from US1.
- **User Story 3 (P3)**: Can be tested independently through invalid requests and fake upstream failures; practically depends on the validator and handler surface from US1.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation should be the smallest code needed to pass that story's tests.
- reStructuredText docstrings must be added or updated before each story is marked complete.
- Refactor only after focused tests pass; rerun focused tests after refactor.
- Full repository `pytest` and `ruff check .` are required before feature completion.

---

## Parallel Opportunities

- T002, T003, and T004 can run in parallel because they create separate test files.
- T005, T006, and T009 can run in parallel because they target separate foundational test files.
- T011, T012, and T013 can run in parallel because they target separate US1 test files.
- T024, T025, T026, and T027 can run in parallel because they target separate metadata/catalog/common/registry test files.
- T036, T038, and T039 can run in parallel because they target different US3 test files; T037 shares `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py` with T036 and should be coordinated.
- T047 and T048 can run in parallel during polish because one updates docs and one reviews Python docstrings.

---

## Parallel Example: User Story 1

```bash
Task: "T011 [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py"
Task: "T012 [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py"
Task: "T013 [US1] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T024 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py"
Task: "T025 [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T026 [US2] Add failing common-contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T027 [US2] Add failing default registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T036 [US3] Add invalid request validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_regions.py"
Task: "T038 [US3] Add dispatcher safe-error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_regions_registration.py"
Task: "T039 [US3] Add safe metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational Layer 1 dependency alignment and shared Red coverage.
3. Complete Phase 3 User Story 1.
4. Stop and validate `i18nRegions_list` retrieval independently with the focused US1 tests.

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
- [US1], [US2], and [US3] labels map directly to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/spec.md).
- Tests must fail before implementation begins for the corresponding story.
- Each story has its own independent test criteria and docstring task.
- The suggested MVP scope is User Story 1 only.
- The feature is not complete until focused tests, full `pytest`, and `ruff check .` pass.
