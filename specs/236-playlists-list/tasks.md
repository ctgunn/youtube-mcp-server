# Tasks: Layer 2 Tool `playlists_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/data-model.md), [contracts/playlists_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/contracts/playlists_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before story completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature's empty implementation and test surfaces without adding user-facing behavior.

- [X] T001 [P] Create the new Layer 2 playlists module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T002 [P] Create the playlists contract test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`
- [X] T003 [P] Create the playlists unit test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`
- [X] T004 [P] Create the playlists registration test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm shared resource-family placement before story work begins.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add a failing scaffold test for `get_resource_family("playlists")` placement paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 [P] Add a failing shared contract test proving `mcp_server.tools.youtube_common.playlists` is importable as the playlists family module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T007 Implement the minimal playlists family import scaffold needed for T005 and T006 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T008 Run foundational tests `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Playlists Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `playlists_list` with valid `part` plus exactly one supported selector and receive a near-raw playlist collection result with endpoint, quota, selector, access, pagination, and item context.

**Independent Test**: Invoke `playlists_list` through its descriptor or dispatcher with channel-scoped, identifier-based, owner-scoped, paginated, and empty-result requests and confirm successful list results preserve context without adding out-of-scope enrichment.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add failing contract tests for `PLAYLISTS_LIST_TOOL_NAME`, quota cost `1`, input schema, `build_playlists_list_contract()`, and list response convention in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`
- [X] T010 [P] [US1] Add failing unit tests for `validate_playlists_list_arguments()`, `map_playlists_list_result()`, and successful handler calls for `channelId`, `id`, `mine`, paginated, and empty playlist results in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`
- [X] T011 [P] [US1] Add failing integration tests proving `build_playlists_list_tool_descriptor()` registers and executes through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py`
- [X] T012 [P] [US1] Add failing default registry tests proving `playlists_list` appears in `InMemoryToolDispatcher().list_tools()` and can be called for a valid channel-scoped request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Define `PLAYLISTS_LIST_*` constants, supported parts, selectors, maximum result limit, and input schema in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T014 [US1] Implement `PlaylistsListToolError`, `build_playlists_list_contract()`, response convention metadata, and response boundary metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T015 [US1] Implement `validate_playlists_list_arguments()` with required `part`, exactly-one selector, selector shape, and selector-compatible pagination validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T016 [US1] Implement access-context selection for public `channelId` and `id` requests and OAuth-backed `mine` requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T017 [US1] Implement `map_playlists_list_result()` to preserve endpoint, quota, requested parts, selector, auth, pagination, returned playlist items, and empty collection context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T018 [US1] Implement `build_playlists_list_handler()` using `build_playlists_list_wrapper()` and one Layer 1 wrapper call per valid request in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T019 [US1] Implement `build_playlists_list_tool_descriptor()` and descriptor input schema wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T020 [US1] Export `PLAYLISTS_LIST_*`, `PlaylistsListToolError`, `build_playlists_list_contract()`, `build_playlists_list_handler()`, and `build_playlists_list_tool_descriptor()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_playlists_list_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add reStructuredText docstrings for every new or modified production and test helper function touched by US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py`

### Refactor and Validation for User Story 1

- [X] T023 [US1] Refactor US1 implementation for naming, helper reuse, and narrow endpoint scope while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T024 [US1] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and fix US1 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Selectors, Access, and Pagination Before Calling (Priority: P2)

**Goal**: A client developer can inspect `playlists_list` discovery metadata, descriptions, usage notes, caveats, and examples and understand quota, access, selectors, pagination, empty-result behavior, and out-of-scope boundaries before invocation.

**Independent Test**: Review `playlists_list` metadata and examples from its descriptor and catalog entries, then confirm the mapped endpoint, quota cost, conditional access behavior, required `part`, selectors, pagination, empty success, safe failures, and out-of-scope workflows are visible without reading implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing metadata tests for description, usage notes, caveats, examples, quota cost `1`, conditional access, selector names, pagination guidance, empty success, and out-of-scope workflows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`
- [X] T026 [P] [US2] Add failing shared catalog tests proving `playlists_list` appears with concrete contract metadata and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T027 [P] [US2] Add failing shared common contract tests for `playlists_list` export and catalog participation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`

### Implementation for User Story 2 (Green)

- [X] T028 [US2] Add `PLAYLISTS_LIST_DESCRIPTION`, `PLAYLISTS_LIST_USAGE_NOTES`, `PLAYLISTS_LIST_CAVEATS`, and `PLAYLISTS_LIST_CALLER_EXAMPLES` covering all quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T029 [US2] Wire `playlists_list` examples, usage notes, caveats, auth mode, availability state, response convention, and response boundary into `build_playlists_list_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T030 [US2] Add `build_playlists_list_contract()` to the shared YouTube example/catalog contract list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Ensure `playlists_list` metadata is exposed consistently through public package exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T032 [US2] Add reStructuredText docstrings for every new or modified metadata/catalog helper function touched by US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor and Validation for User Story 2

- [X] T033 [US2] Refactor metadata text to remove duplicated shared wording while preserving endpoint-specific quota, access, selector, pagination, and scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T034 [US2] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` and fix US2 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid Playlist List Requests Clearly (Priority: P3)

**Goal**: Callers receive clear validation, access, and upstream failure feedback for malformed inputs, selector conflicts, selector-incompatible paging, missing owner-scoped access, quota failures, missing resources, unavailable service, and out-of-scope requests.

**Independent Test**: Submit representative invalid and ineligible `playlists_list` requests through validator, handler, descriptor, and dispatcher paths, then confirm each failure uses safe categories and sanitized details while empty successful collections remain successful results.

### Tests for User Story 3 (Red)

- [X] T035 [P] [US3] Add failing unit validation tests for missing `part`, invalid `part`, missing selector, conflicting selectors, invalid `channelId`, invalid `id`, invalid `mine`, invalid `pageToken`, out-of-range `maxResults`, selector-incompatible paging, and unsupported fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`
- [X] T036 [P] [US3] Add failing unit tests for owner-scoped missing OAuth access, quota failure, missing resource, upstream unavailable, deprecated behavior, unexpected upstream failure, and sanitized unsafe upstream details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`
- [X] T037 [P] [US3] Add failing integration tests for invalid dispatcher requests, safe access failures, safe upstream failures, and empty successful collections in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py`
- [X] T038 [P] [US3] Add failing contract tests proving failure examples cover missing part, invalid part, missing selector, conflicting selector, unsupported paging, access failure, quota/upstream failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`

### Implementation for User Story 3 (Green)

- [X] T039 [US3] Expand `validate_playlists_list_arguments()` to reject all US3 malformed inputs with safe field details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T040 [US3] Implement safe owner-scoped authentication and authorization failure handling for `mine` requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T041 [US3] Implement upstream error mapping for quota, invalid request, missing resource, unavailable service, deprecated behavior, unexpected upstream failure, and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T042 [US3] Ensure descriptor and dispatcher handlers surface `PlaylistsListToolError` without leaking API keys, OAuth tokens, authorization headers, stack traces, raw upstream bodies, or unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T043 [US3] Add or update failure examples and contract metadata for all safe error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T044 [US3] Add reStructuredText docstrings for every new or modified validation, access, and error-mapping function touched by US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`

### Refactor and Validation for User Story 3

- [X] T045 [US3] Refactor safe error helpers and invalid-request branches while preserving clear field-level feedback in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T046 [US3] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py` and fix US3 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, verification, documentation, and full-suite confidence.

- [X] T047 [P] Review and update feature-facing implementation notes against `/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/quickstart.md`
- [X] T048 [P] Review every new or modified Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py`
- [X] T049 Run focused quickstart verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/quickstart.md` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T050 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any repository test failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T051 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any code-quality failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T052 Record final focused, full-suite, and lint evidence for YT-236 in `/Users/ctgunn/Projects/youtube-mcp-server/specs/236-playlists-list/tasks.md`

## Final Verification Evidence

- Matched seed slice: `YT-236`
- Focused quickstart verification: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` -> 225 passed
- Full repository verification: `PYTHONPATH=src python3 -m pytest` -> 3011 passed
- Lint verification: `python3 -m ruff check .` -> All checks passed
- Docstring review: every new or modified Python class, helper, handler, nested fake, and test function in the YT-236 production and test files has a reStructuredText-style docstring where parameters, returns, or raised errors need caller context

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001-T004 can start immediately.
- **Phase 2 Foundational**: Depends on setup files from Phase 1; blocks user story work.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP executable retrieval tool.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 if descriptor/contract ownership is coordinated, but final metadata validation expects US1 contract builders to exist.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 if validator/error-helper ownership is coordinated, but final invalid-request validation expects US1 handler scaffolding to exist.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Start after Phase 2; no dependency on US2 or US3; recommended MVP scope.
- **US2 (P2)**: Start after Phase 2; depends on the same public contract surface as US1 but remains independently testable through metadata and catalog assertions.
- **US3 (P3)**: Start after Phase 2; depends on the same validator/handler surface as US1 but remains independently testable through invalid input and safe error assertions.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation tasks begin.
- Contract and unit tests marked `[P]` can be written in parallel because they target different files or independent sections.
- Implementation tasks that touch `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` should be sequenced to avoid conflicting edits.
- Docstring tasks must complete before the story checkpoint is considered done.
- Refactor tasks must preserve focused test success before moving to the next story or final polish.

---

## Parallel Execution Examples

### User Story 1

```text
Task: "T009 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
Task: "T010 [P] [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py"
Task: "T011 [P] [US1] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py"
Task: "T012 [P] [US1] Add failing default registry tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T025 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
Task: "T026 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T027 [P] [US2] Add failing common contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

### User Story 3

```text
Task: "T035 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py"
Task: "T037 [P] [US3] Add failing dispatcher invalid-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py"
Task: "T038 [P] [US3] Add failing failure-example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup tasks T001-T004.
2. Complete Phase 2 foundational tasks T005-T008.
3. Complete Phase 3 US1 tasks T009-T024.
4. Validate `playlists_list` independently with descriptor and dispatcher calls for valid retrieval paths.
5. Stop for MVP review before metadata enrichment and invalid-request hardening if incremental delivery is desired.

### Incremental Delivery

1. Setup and foundation establish the playlists family surface.
2. US1 adds executable playlist retrieval and default registration.
3. US2 makes the tool self-explanatory through discovery, examples, catalog metadata, and caveats.
4. US3 hardens invalid input, access failures, upstream failures, and safe sanitization.
5. Polish runs focused quickstart checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person can create setup files while another adds scaffold tests.
2. After Phase 2, separate contributors can write US1, US2, and US3 Red tests in parallel.
3. Coordinate implementation edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` because most Green tasks converge there.
4. Keep final validation serialized so full-suite and lint evidence reflect the final combined state.

---

## Task Summary

- **Total tasks**: 52
- **Setup tasks**: 4
- **Foundational tasks**: 4
- **US1 tasks**: 16
- **US2 tasks**: 10
- **US3 tasks**: 12
- **Polish tasks**: 6
- **Suggested MVP scope**: Complete through US1, tasks T001-T024.
