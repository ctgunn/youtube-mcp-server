# Tasks: Layer 2 Tool `i18nLanguages_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/data-model.md), [contracts/i18nLanguages_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/contracts/i18nLanguages_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/quickstart.md)

**Tests**: Test tasks are required for every story and shared foundation. Red tests must fail before implementation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so `i18nLanguages_list` can be delivered first as a usable MVP, then expanded with metadata/examples, then hardened for invalid requests and safe errors.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or depends only on completed earlier phases
- **[Story]**: User story label for story phases only
- Every task includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature-local test files and confirm the plan artifacts used by implementation.

- [X] T001 Review YT-224 plan, contract, data model, and quickstart before implementation in /Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/plan.md
- [X] T002 [P] Create the focused contract test module with a module docstring in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py
- [X] T003 [P] Create the focused unit test module with a module docstring in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py
- [X] T004 [P] Create the focused integration test module with a module docstring in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_languages_registration.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add failing shared-contract, export, catalog, and registration coverage that blocks all user stories.

**Critical**: No user story implementation starts until these Red tests exist and fail for the missing `i18nLanguages_list` tool.

- [X] T005 [P] Add failing derived-name and localization resource-family placement coverage for `i18nLanguages_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T006 [P] Add failing shared contract coverage requiring safe public Layer 2 metadata for active API-key list tools in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T007 [P] Add failing representative catalog coverage requiring `i18nLanguages_list` in the shared example catalog in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 [P] Add failing default registry coverage requiring `i18nLanguages_list` to be listed and executable by default in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T009 Run the foundational Red tests and confirm they fail for missing `i18nLanguages_list` symbols or registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py

**Checkpoint**: Foundation Red coverage is in place; user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Localization Languages Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `i18nLanguages_list` with `part=snippet` and optional `hl`, receive a near-raw localization-language list result, and see endpoint/quota/context in the result.

**Independent Test**: Invoke `i18nLanguages_list` through its descriptor or dispatcher with `{"part": "snippet"}` and `{"part": "snippet", "hl": "es"}` and confirm both produce endpoint-backed list results with quota cost 1, requested parts, active availability, items, and display-language context when supplied.

### Tests for User Story 1 (REQUIRED)

> Write these tests first and verify they fail before implementation.

- [X] T010 [P] [US1] Add failing contract tests for public symbol exports, input schema, upstream identity, active availability, quota cost 1, and API-key auth in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py
- [X] T011 [P] [US1] Add failing unit tests for accepting default and display-language requests plus mapping populated and empty upstream list payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py
- [X] T012 [P] [US1] Add failing integration tests for descriptor registration and dispatcher invocation of default and display-language lookups in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_languages_registration.py
- [X] T013 [P] [US1] Add failing Layer 1 alignment tests showing `i18nLanguages.list` accepts omitted `hl` while preserving existing `part` plus `hl` behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T014 [US1] Implement `I18N_LANGUAGES_LIST_*` constants, input schema, description, usage notes, examples, and result-boundary constants in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T015 [US1] Implement `validate_i18n_languages_list_arguments()` for required `part=snippet` and optional `hl` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T016 [US1] Implement `map_i18n_languages_list_result()` preserving endpoint, quota cost, requested parts, active availability, localization context, items, kind, and etag in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T017 [US1] Implement `build_i18n_languages_list_contract()`, `build_i18n_languages_list_handler()`, and `build_i18n_languages_list_tool_descriptor()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T018 [US1] Align Layer 1 `i18nLanguages.list` metadata or validation so omitted `hl` is accepted while existing `part` plus `hl` requests still pass in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py
- [X] T019 [US1] Export `i18nLanguages_list` symbols and the `localization` module from the shared package in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T020 [US1] Register `build_i18n_languages_list_tool_descriptor()` in the default dispatcher registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T022 [US1] Run focused US1 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py
- [X] T023 [US1] Refactor US1 implementation for naming, helper reuse, and cohesion while keeping focused tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Auth, and Localization Usage Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, descriptions, usage notes, and examples to understand endpoint identity, quota cost, auth mode, required `part`, optional `hl`, active availability, and out-of-scope boundaries before invoking the tool.

**Independent Test**: Inspect the `i18nLanguages_list` descriptor and shared catalog entry and confirm quota cost 1, API-key auth, active availability, upstream `i18nLanguages.list`, `part=snippet`, optional `hl`, empty-result behavior, and non-translation/non-region scope are visible without calling the handler.

### Tests for User Story 2 (REQUIRED)

> Write these tests first and verify they fail before implementation.

- [X] T024 [P] [US2] Add failing contract tests for metadata, description, usage notes, caveats, response convention, response boundary, and required example names in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py
- [X] T025 [P] [US2] Add failing shared catalog tests proving `i18nLanguages_list` appears in representative examples with quota/auth/localization visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T026 [P] [US2] Add failing default registry metadata tests for public discovery of quota, auth, active availability, and examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py

### Implementation for User Story 2

- [X] T027 [US2] Populate caller-facing examples `default_language_listing`, `display_language_listing`, `empty_success`, `missing_part`, `invalid_part`, `invalid_display_language`, `unsupported_option`, and `out_of_scope_translation_or_region_request` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T028 [US2] Add `i18nLanguages_list` to the representative YouTube contract examples catalog in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T029 [US2] Update response convention and response boundary metadata for localization-language lookup in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T030 [US2] Add or update reStructuredText docstrings for every new or modified function touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T031 [US2] Run focused US2 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T032 [US2] Refactor US2 metadata and example text to avoid duplication while keeping focused tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py

**Checkpoint**: User Stories 1 and 2 work independently and the discovery surface is reviewable before invocation.

---

## Phase 5: User Story 3 - Reject Unsupported Localization-Language Requests Clearly (Priority: P3)

**Goal**: Invalid `i18nLanguages_list` requests and upstream failures produce clear safe categories without exposing secrets or implying unsupported translation, region, caption, search, ranking, summarization, or enrichment behavior.

**Independent Test**: Submit invalid requests directly to the validator and through the dispatcher, then confirm missing/invalid `part`, invalid `hl`, unsupported fields, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and unexpected failures are categorized distinctly and safely.

### Tests for User Story 3 (REQUIRED)

> Write these tests first and verify they fail before implementation.

- [X] T033 [P] [US3] Add failing unit tests for missing `part`, invalid `part`, invalid `hl`, unsupported selectors, unsupported region/caption/translation/search fields, and empty successful results in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py
- [X] T034 [P] [US3] Add failing unit tests for mapping upstream invalid request, auth, quota, endpoint unavailable, and unexpected errors to safe categories in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py
- [X] T035 [P] [US3] Add failing integration tests for dispatcher validation failures and safe error detail sanitization in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_languages_registration.py
- [X] T036 [P] [US3] Add failing contract tests proving public metadata, examples, results, and errors contain no API keys, OAuth tokens, stack traces, signed URLs, or raw upstream diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py

### Implementation for User Story 3

- [X] T037 [US3] Implement `I18nLanguagesListToolError` and safe validation failure details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T038 [US3] Implement upstream error mapping for invalid request, authentication, authorization, quota, endpoint unavailable, resource not found, and upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T039 [US3] Harden handler error paths so dispatcher calls expose safe caller-facing failures without leaking credentials or raw diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T040 [US3] Add or update reStructuredText docstrings for every new or modified function touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T041 [US3] Run focused US3 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py
- [X] T042 [US3] Refactor US3 validation and error mapping to reuse shared safe metadata helpers while keeping focused tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py

**Checkpoint**: All user stories are independently functional and safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature, update review evidence, and ensure no cross-story regressions remain.

- [X] T043 [P] Update quickstart review evidence notes after implementation in /Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/quickstart.md
- [X] T044 [P] Review and update reStructuredText docstrings for all Python functions changed by the feature in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py
- [X] T045 Run the focused YT-224 verification command and fix any failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py
- [X] T046 Run `pytest` for the full repository and fix any failures before completion in /Users/ctgunn/Projects/youtube-mcp-server
- [X] T047 Run `ruff check .` and fix any lint failures before completion in /Users/ctgunn/Projects/youtube-mcp-server
- [X] T048 Confirm `i18nLanguages_list` scope excludes translation, language detection, region lookup, caption-language availability, search, ranking, summarization, enrichment, and aggregation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can run after US1 constants/descriptor shape exists or in parallel with careful coordination on `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`.
- **User Story 3 (Phase 5)**: Depends on Foundational; can run after US1 validator/handler shape exists or in parallel with careful coordination on `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP; no dependency on US2 or US3 after Foundational.
- **User Story 2 (P2)**: Independent discovery/metadata value; depends on the descriptor shape created by US1 for lowest-conflict implementation.
- **User Story 3 (P3)**: Independent validation/error value; depends on the validator and handler shape created by US1 for lowest-conflict implementation.

### Within Each User Story

- Red tests must be written and observed failing before implementation tasks begin.
- Green implementation should be the smallest code needed to pass that story's tests.
- reStructuredText docstrings must be added or preserved before marking the story complete.
- Refactor tasks run only after story tests pass and must keep focused tests green.
- Final completion requires full `pytest` and `ruff check .`, not only focused tests.

---

## Parallel Opportunities

- T002, T003, and T004 can run in parallel because they create different focused test files.
- T005, T006, T007, and T008 can run in parallel because they touch different shared test files.
- T010, T011, T012, and T013 can run in parallel during US1 Red because they target different test files.
- T024, T025, and T026 can run in parallel during US2 Red because they target different metadata/catalog/registry tests.
- T033, T035, and T036 can run in parallel during US3 Red; T034 shares `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py` with T033 and should be coordinated.
- T043 and T044 can run in parallel during Polish because they touch documentation and source docstrings separately.

---

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py"
Task: "T011 [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py"
Task: "T012 [US1] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_languages_registration.py"
Task: "T013 [US1] Add failing Layer 1 alignment tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T024 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py"
Task: "T025 [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T026 [US2] Add failing default registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_i18n_languages.py"
Task: "T035 [US3] Add failing dispatcher error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_i18n_languages_registration.py"
Task: "T036 [US3] Add failing safe metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational Red tests.
3. Complete Phase 3 User Story 1.
4. Validate with focused US1 tests and a dispatcher call for `i18nLanguages_list`.
5. Stop for demo or review if only the MVP is needed.

### Incremental Delivery

1. Complete Setup and Foundational phases.
2. Deliver US1 for callable localization-language lookup.
3. Deliver US2 for complete discovery metadata and examples.
4. Deliver US3 for robust validation and safe error handling.
5. Complete Polish with focused tests, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person owns `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py` during Green implementation to reduce merge conflicts.
2. Other contributors can independently add Red tests in contract, unit, integration, shared catalog, and registry files.
3. After the US1 module skeleton exists, US2 metadata/example work and US3 validation/error work can proceed in coordinated branches or sequenced patches.

## Notes

- The suggested MVP scope is User Story 1 only.
- The current Layer 1 `i18nLanguages.list` wrapper may need a narrow optional-`hl` alignment update in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`.
- Keep `i18nLanguages_list` in the localization resource family; do not add translation, language detection, region, caption, search, ranking, summarization, enrichment, or aggregation behavior.
- Every Python function added or changed by these tasks must have a reStructuredText docstring before the relevant story is marked complete.
