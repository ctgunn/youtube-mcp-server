# Tasks: Layer 2 Tool `playlists_delete`

**Input**: Design documents from /Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/data-model.md), [contracts/playlists_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/contracts/playlists_delete.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before story completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the existing playlists Layer 2 family and test files for delete work without adding user-facing behavior.

- [X] T001 [P] Review the existing `playlists_list`, `playlists_insert`, and `playlists_update` implementation patterns and reserve a delete section in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T002 [P] Reserve delete-focused contract test sections below the existing list, insert, and update tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py
- [X] T003 [P] Reserve delete-focused unit test sections below the existing list, insert, and update tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T004 [P] Reserve delete-focused registration test sections below the existing list, insert, and update tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add failing shared-surface checks that block all stories until the public delete tool can be exported and registered consistently.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add a failing shared package export test for `PLAYLISTS_DELETE_TOOL_NAME` and `build_playlists_delete_tool_descriptor()` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T006 [P] Add a failing scaffold test proving the existing playlists resource family remains the owner for `playlists_delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T007 [P] Add a failing default catalog test proving `playlists_delete` is expected in the YouTube tool catalog in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 Implement minimal public placeholders for delete constants and descriptor exports without executable behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T009 Export the minimal delete placeholders from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T010 Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm only intended delete behavior remains red in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Delete Playlists Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `playlists_delete` with OAuth-backed access and target playlist identity, then receive a deletion acknowledgment with endpoint, quota, target, access, and mutation context.

**Independent Test**: Invoke `playlists_delete` through its descriptor or dispatcher with valid `id`, then confirm the handler calls the Layer 1 delete wrapper once and returns a no-body-compatible deletion acknowledgment without fabricated playlist data or out-of-scope enrichment.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `PLAYLISTS_DELETE_TOOL_NAME`, quota cost `50`, OAuth auth mode, input schema, `build_playlists_delete_contract()`, and deletion response convention in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py
- [X] T012 [P] [US1] Add failing unit tests for `validate_playlists_delete_arguments()` accepting a valid non-empty `id` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T013 [US1] Add failing unit tests for `map_playlists_delete_result()` preserving endpoint, quota, deleted marker, acknowledged marker, OAuth context, and target playlist identity in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T014 [US1] Add failing unit tests proving `build_playlists_delete_handler()` forwards OAuth context to `build_playlists_delete_wrapper()` and never leaks the OAuth token in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T015 [P] [US1] Add failing integration tests proving `build_playlists_delete_tool_descriptor()` registers and executes through `InMemoryToolDispatcher` for a valid delete request in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py
- [X] T016 [P] [US1] Add failing default registry tests proving `playlists_delete` appears in `InMemoryToolDispatcher().list_tools()` and can be called for a valid delete request in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py

### Implementation for User Story 1 (Green)

- [X] T017 [US1] Define `PLAYLISTS_DELETE_*` constants, unsafe detail keys, and input schema requiring `id` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T018 [US1] Implement `PlaylistsDeleteToolError`, delete error sanitization, and shared safe details for playlist delete failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T019 [US1] Implement `build_playlists_delete_contract()` with `playlists.delete` identity, OAuth-required auth mode, quota cost `50`, mutation acknowledgment convention, and no-body response boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T020 [US1] Implement `validate_playlists_delete_arguments()` for required non-empty string `id` and one-target-per-request behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T021 [US1] Implement OAuth access-context selection for `playlists_delete` with safe missing-token failure behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T022 [US1] Implement `map_playlists_delete_result()` to preserve endpoint, quota, deleted marker, acknowledged marker, OAuth context, and target playlist identity without fabricated playlist data in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T023 [US1] Implement `_default_playlists_delete_executor()` returning deterministic representative no-body deletion acknowledgment data in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T024 [US1] Implement `build_playlists_delete_handler()` using `build_playlists_delete_wrapper()` and one Layer 1 wrapper call per valid request in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T025 [US1] Implement `build_playlists_delete_tool_descriptor()` with callable handler, input schema, and metadata wiring in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T026 [US1] Export `PLAYLISTS_DELETE_*`, `PlaylistsDeleteToolError`, `build_playlists_delete_contract()`, `build_playlists_delete_handler()`, `build_playlists_delete_tool_descriptor()`, `map_playlists_delete_result()`, and `validate_playlists_delete_arguments()` from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T027 [US1] Register `build_playlists_delete_tool_descriptor()` in the default dispatcher tool list in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T028 [US1] Add reStructuredText docstrings for every new or modified production and fake test helper function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py

### Refactor and Validation for User Story 1

- [X] T029 [US1] Refactor US1 implementation for naming, helper reuse, and narrow endpoint scope while preserving existing `playlists_list`, `playlists_insert`, and `playlists_update` behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T030 [US1] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US1 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Deletion Impact Before Calling (Priority: P2)

**Goal**: A client developer can inspect `playlists_delete` discovery metadata, descriptions, usage notes, caveats, and examples and understand quota, OAuth, target identity, destructive deletion behavior, acknowledgment shape, repeat-delete caveat, safe failures, and out-of-scope boundaries before invocation.

**Independent Test**: Review `playlists_delete` metadata and examples from its descriptor and catalog entries, then confirm the mapped endpoint, quota cost, OAuth requirement, required `id`, destructive warning, repeat-delete caveat, deletion acknowledgment result shape, safe failures, and out-of-scope workflows are visible without reading implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T031 [P] [US2] Add failing metadata tests for description, usage notes, caveats, examples, quota cost `50`, OAuth requirement, destructive deletion warning, repeat-delete caveat, no-body acknowledgment shape, and out-of-scope workflows in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py
- [X] T032 [US2] Add failing example coverage tests for successful deletion, no-body acknowledgment, missing target identity, malformed target identity, unsupported field, missing authorization, insufficient authorization, missing-resource or already-deleted failure, quota or upstream failure, repeat-delete caveat, and out-of-scope management request in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py
- [X] T033 [P] [US2] Add failing shared catalog tests proving `playlists_delete` appears with concrete contract metadata and representative examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T034 [P] [US2] Add failing common contract tests for `playlists_delete` public exports and catalog participation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T035 [US2] Add `PLAYLISTS_DELETE_DESCRIPTION`, `PLAYLISTS_DELETE_USAGE_NOTES`, `PLAYLISTS_DELETE_CAVEATS`, and `PLAYLISTS_DELETE_CALLER_EXAMPLES` covering all quickstart examples in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T036 [US2] Wire delete examples, usage notes, caveats, auth mode, availability state, response convention, and response boundary into `build_playlists_delete_contract()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T037 [US2] Add `build_playlists_delete_contract()` to the shared YouTube example/catalog contract list in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T038 [US2] Ensure `playlists_delete` metadata and examples are exposed consistently through public package exports in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T039 [US2] Add reStructuredText docstrings for every new or modified metadata/catalog helper function touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py

### Refactor and Validation for User Story 2

- [X] T040 [US2] Refactor metadata text to remove duplicated shared wording while preserving quota, OAuth, target identity, destructive warning, no-body acknowledgment, repeat-delete caveat, and scope guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T041 [US2] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US2 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid or Unauthorized Deletion Requests Clearly (Priority: P3)

**Goal**: Callers receive clear validation, access, and upstream failure feedback for malformed inputs, unsupported fields, missing OAuth, insufficient authorization, missing or already-deleted playlist outcomes, quota failures, unavailable service, deprecated endpoint behavior, and out-of-scope requests.

**Independent Test**: Submit representative invalid and ineligible `playlists_delete` requests through validator, handler, descriptor, and dispatcher paths, then confirm each failure uses safe categories and sanitized details while successful deletion remains distinct.

### Tests for User Story 3 (Red)

- [X] T042 [P] [US3] Add failing unit validation tests for missing `id`, blank `id`, non-string `id`, unsupported `part`, unsupported `body`, unsupported selector fields, unsupported paging fields, unsupported playlist item fields, unsupported playlist image fields, unsupported analytics fields, and unsupported top-level fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T043 [US3] Add failing unit tests for missing OAuth, invalid OAuth, quota failure, authorization failure, missing playlist failure, already-deleted playlist failure, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized unsafe upstream details in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py
- [X] T044 [P] [US3] Add failing integration tests for invalid dispatcher requests, missing OAuth failures, safe upstream failures, and successful deletion staying distinct from failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py
- [X] T045 [P] [US3] Add failing contract tests proving failure examples cover missing target identity, malformed target identity, unsupported field, missing authorization, insufficient authorization, missing-resource or already-deleted failure, quota or upstream failure, repeat-delete caveat, and out-of-scope workflow rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py

### Implementation for User Story 3 (Green)

- [X] T046 [US3] Expand `validate_playlists_delete_arguments()` to reject all malformed target identity and unsupported field inputs with safe field details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T047 [US3] Implement safe OAuth authentication and authorization failure handling for delete requests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T048 [US3] Implement upstream error mapping for quota, invalid request, authorization, missing resource, already-deleted target, unavailable service, deprecated behavior, unexpected upstream failure, and sanitized details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T049 [US3] Ensure descriptor and dispatcher handlers surface `PlaylistsDeleteToolError` without leaking API keys, OAuth tokens, authorization headers, stack traces, raw upstream bodies, or unsafe request context in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T050 [US3] Add or update failure examples and contract metadata for all safe delete error categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T051 [US3] Add reStructuredText docstrings for every new or modified validation, access, and error-mapping function touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py

### Refactor and Validation for User Story 3

- [X] T052 [US3] Refactor safe error helpers and invalid-request branches while preserving clear field-level feedback in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T053 [US3] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US3 failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, verification, documentation, and full-suite confidence.

- [X] T054 [P] Review the implemented contract against /Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/contracts/playlists_delete.md and update mismatches in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T055 [P] Review quickstart examples against /Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/quickstart.md and update mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py
- [X] T056 [P] Review every new or modified Python function for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py
- [X] T057 Run focused quickstart verification command from /Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/quickstart.md and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T058 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any repository test failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T059 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any code-quality failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py
- [X] T060 Record final focused, full-suite, lint, and docstring evidence for YT-239 in /Users/ctgunn/Projects/youtube-mcp-server/specs/239-playlists-delete/tasks.md

### Final Verification Evidence

- Matched seed slice: YT-239 (`239-playlists-delete`)
- Focused quickstart verification: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/integration/test_youtube_tool_registration.py` -> 351 passed
- Full repository test suite: `PYTHONPATH=src python3 -m pytest` -> 3137 passed
- Lint: `python3 -m ruff check .` -> All checks passed
- Python docstring audit for new/modified Python functions -> `missing_count 0`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001-T004 can start immediately.
- **Phase 2 Foundational**: Depends on setup context from Phase 1; blocks user story work.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP executable delete tool.
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
- Implementation tasks that touch /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py should be sequenced to avoid conflicting edits.
- Docstring tasks must complete before the story checkpoint is considered done.
- Refactor tasks must preserve focused test success before moving to the next story or final polish.

---

## Parallel Execution Examples

### User Story 1

```text
Task: "T011 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
Task: "T012 [P] [US1] Add failing unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py"
Task: "T015 [P] [US1] Add failing integration descriptor tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py"
Task: "T016 [P] [US1] Add failing default registry tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T031 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
Task: "T033 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T034 [P] [US2] Add failing common contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

### User Story 3

```text
Task: "T042 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py"
Task: "T044 [P] [US3] Add failing dispatcher invalid-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py"
Task: "T045 [P] [US3] Add failing failure-example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup tasks T001-T004.
2. Complete Phase 2 foundational tasks T005-T010.
3. Complete Phase 3 US1 tasks T011-T030.
4. Validate `playlists_delete` independently with descriptor and dispatcher calls for valid deletion.
5. Stop for MVP review before metadata enrichment and invalid-request hardening if incremental delivery is desired.

### Incremental Delivery

1. Setup and foundation establish the playlists delete public surface.
2. US1 adds executable playlist deletion and default registration.
3. US2 makes the tool self-explanatory through discovery, examples, catalog metadata, destructive warning, no-body acknowledgment shape, repeat-delete caveat, and caveats.
4. US3 hardens invalid input, access failures, upstream failures, and safe sanitization.
5. Polish runs focused quickstart checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person can prepare setup sections while another adds scaffold/export tests.
2. After Phase 2, separate contributors can write US1, US2, and US3 Red tests in parallel.
3. Coordinate implementation edits to /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py because most Green tasks converge there.
4. Keep final validation serialized so full-suite and lint evidence reflect the final combined state.

---

## Task Summary

- **Total tasks**: 60
- **Setup tasks**: 4
- **Foundational tasks**: 6
- **US1 tasks**: 20
- **US2 tasks**: 11
- **US3 tasks**: 12
- **Polish tasks**: 7
- **Suggested MVP scope**: Complete through US1, tasks T001-T030.
