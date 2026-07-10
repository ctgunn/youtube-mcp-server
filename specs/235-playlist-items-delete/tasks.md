# Tasks: Layer 2 Tool `playlistItems_delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/data-model.md), [contracts/playlistItems_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/contracts/playlistItems_delete.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python changes require reStructuredText docstrings for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase because it touches different files or only adds independent test coverage
- **[Story]**: Maps a task to one user story from `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing extension points for the playlist-items Layer 2 resource family before adding YT-235 work.

- [X] T001 Inspect existing `playlistItems_list`, `playlistItems_insert`, and `playlistItems_update` patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T002 [P] Inspect public export and dispatcher registration patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T003 [P] Inspect existing playlist-items contract, unit, and registration coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared failing coverage and minimal public scaffolding that every user story depends on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T004 [P] Add failing public-symbol export assertions for `PLAYLIST_ITEMS_DELETE_TOOL_NAME`, `PLAYLIST_ITEMS_DELETE_INPUT_SCHEMA`, `PlaylistItemsDeleteToolError`, and `build_playlist_items_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- [X] T005 [P] Add failing default catalog assertions that `playlistItems_delete` is discoverable with operation key `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T006 [P] Add failing default dispatcher registration assertions for `playlistItems_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T007 [P] Add failing shared scaffolding assertions for the playlist-items delete resource family placement in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T008 Run foundational Red checks and confirm they fail for missing `playlistItems_delete` from `/Users/ctgunn/Projects/youtube-mcp-server` using `python3 -m pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 Add `playlistItems_delete` constants, input schema, and safe `PlaylistItemsDeleteToolError` scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T010 Export the new playlist-items delete public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T011 Add reStructuredText docstrings for the new `PlaylistItemsDeleteToolError` callable behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`

**Checkpoint**: Shared symbols and scaffolding are ready for story-specific Red-Green-Refactor work.

---

## Phase 3: User Story 1 - Delete Playlist Items Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can invoke `playlistItems_delete` with one playlist item identifier and OAuth-backed access, then receive a safe deletion acknowledgment.

**Independent Test**: Invoke `playlistItems_delete` through the descriptor or dispatcher with `{"id": "playlist-item-123"}` and confirm the result includes `endpoint`, `quotaCost`, `target.id`, `auth.mode`, `deleted`, and `acknowledged` without fabricated deleted resource fields.

### Tests for User Story 1 (Red)

- [X] T012 [P] [US1] Add failing unit tests for accepted `id` validation, deletion result mapping, no-body acknowledgment, and wrapper invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`
- [X] T013 [P] [US1] Add failing integration tests proving `playlistItems_delete` registers and executes through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py`
- [X] T014 [P] [US1] Add failing contract tests for the successful `playlistItems_delete` descriptor and result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- [X] T015 [US1] Run User Story 1 Red tests and confirm they fail for missing delete behavior from `/Users/ctgunn/Projects/youtube-mcp-server` using `python3 -m pytest tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_playlist_items_contract.py`

### Implementation for User Story 1 (Green)

- [X] T016 [US1] Implement `validate_playlist_items_delete_arguments`, target context mapping, and `map_playlist_items_delete_result` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T017 [US1] Implement OAuth auth-context builder, handler builder, default fake executor response, and `build_playlist_items_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T018 [US1] Register `build_playlist_items_delete_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T019 [US1] Add reStructuredText docstrings for every new or changed delete validator, mapper, auth helper, handler builder, descriptor builder, and fake wrapper method in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`

### Refactor and Validation for User Story 1

- [X] T020 [US1] Refactor `playlistItems_delete` implementation for consistency with existing playlist-items mutation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T021 [US1] Run focused US1 tests from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_playlist_items_contract.py` and fix failures in the touched files

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Delete Semantics Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, descriptions, usage notes, caveats, and examples to understand quota cost `50`, OAuth-required access, required `id`, destructive semantics, no-body acknowledgment behavior, and out-of-scope boundaries before invocation.

**Independent Test**: Build `playlistItems_delete` contract and descriptor, then verify metadata and examples expose `playlistItems.delete`, quota cost `50`, `oauth_required`, `id`, destructive deletion, no-body acknowledgment, safe errors, and out-of-scope workflows.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing metadata tests for quota, OAuth, required `id`, destructive caveats, response boundary, and usage notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- [X] T023 [US2] Add failing caller-example coverage for OAuth-backed deletion, no-body acknowledgment, missing `id`, invalid `id`, unsupported input, auth failure, quota or missing-resource failure, and out-of-scope request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- [X] T024 [P] [US2] Add failing default catalog metadata assertions for quota cost `50`, auth mode, and operation key in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T025 [US2] Run User Story 2 Red tests and confirm they fail for incomplete caller-facing metadata from `/Users/ctgunn/Projects/youtube-mcp-server` using `python3 -m pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2 (Green)

- [X] T026 [US2] Add `PLAYLIST_ITEMS_DELETE_DESCRIPTION`, `PLAYLIST_ITEMS_DELETE_USAGE_NOTES`, `PLAYLIST_ITEMS_DELETE_CAVEATS`, and `PLAYLIST_ITEMS_DELETE_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T027 [US2] Implement `build_playlist_items_delete_contract` with response convention, response boundary, error categories, availability state, quota metadata, and caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T028 [US2] Include `playlistItems_delete` contract metadata and examples in `build_playlist_items_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T029 [US2] Export `PLAYLIST_ITEMS_DELETE_DESCRIPTION`, `PLAYLIST_ITEMS_DELETE_USAGE_NOTES`, `PLAYLIST_ITEMS_DELETE_CAVEATS`, and `PLAYLIST_ITEMS_DELETE_CALLER_EXAMPLES` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T030 [US2] Add reStructuredText docstrings for delete contract builder and any changed metadata builder functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`

### Refactor and Validation for User Story 2

- [X] T031 [US2] Refactor delete metadata wording to avoid duplication while preserving endpoint-specific quota/auth/id/destructive guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T032 [US2] Run focused US2 tests from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py` and fix failures in the touched files

**Checkpoint**: User Story 2 is independently testable through discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Item Delete Requests Clearly (Priority: P3)

**Goal**: A caller receives safe, clear validation and access feedback for missing `id`, invalid `id`, unsupported inputs, missing OAuth, missing resources, quota failures, endpoint unavailability, deprecated endpoint behavior, and unexpected upstream failures.

**Independent Test**: Submit representative invalid or inaccessible `playlistItems_delete` requests and confirm each failure maps to a safe shared category with sanitized details and no successful deletion acknowledgment.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add failing parametrized unit tests for missing `id`, blank `id`, non-string `id`, unsupported `part`, unsupported `body`, unsupported playlist metadata, unsupported paging, and unsupported selector inputs in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`
- [X] T034 [P] [US3] Add failing contract tests for safe validation failures and sanitized upstream failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- [X] T035 [P] [US3] Add failing dispatcher integration tests for validation failure propagation and OAuth access failure propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py`
- [X] T036 [US3] Run User Story 3 Red tests and confirm they fail for incomplete validation/error behavior from `/Users/ctgunn/Projects/youtube-mcp-server` using `python3 -m pytest tests/unit/test_youtube_playlist_items.py tests/contract/test_youtube_playlist_items_contract.py tests/integration/test_youtube_playlist_items_registration.py`

### Implementation for User Story 3 (Green)

- [X] T037 [US3] Complete `validate_playlist_items_delete_arguments` unsupported-field and identifier validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T038 [US3] Implement `_map_playlist_items_delete_upstream_error` with shared safe categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T039 [US3] Wire delete handler failure paths for missing OAuth, `NormalizedUpstreamError`, and safe `PlaylistItemsDeleteToolError` propagation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T040 [US3] Add reStructuredText docstrings for changed delete validation, error-mapping, auth, and handler functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py`

### Refactor and Validation for User Story 3

- [X] T041 [US3] Refactor delete validation and safe error mapping to align with `comments_delete`, `channelSections_delete`, `captions_delete`, `playlistImages_delete`, and existing playlist-item tools in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- [X] T042 [US3] Run focused US3 tests from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_playlist_items.py tests/contract/test_youtube_playlist_items_contract.py tests/integration/test_youtube_playlist_items_registration.py` and fix failures in the touched files

**Checkpoint**: All user stories are independently functional and safely handle invalid or inaccessible deletion requests.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete feature across shared registry surfaces, documentation, code quality, and full test suite.

- [X] T043 [P] Review and update YT-235 implementation notes if discovered caveats affect `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/quickstart.md`
- [X] T044 [P] Review reStructuredText docstrings for all changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and changed playlist-items tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T045 Run the full focused feature suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` and fix failures in the touched files
- [X] T046 Run the full repository test suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest` and fix all failures before considering YT-235 complete
- [X] T047 Run repository lint from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m ruff check .` and fix all violations before considering YT-235 complete
- [X] T048 Verify git diff is scoped to YT-235 implementation, tests, and documentation before handoff in `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; delivers MVP behavior.
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run after or alongside US1 once shared descriptor scaffolding exists, but final metadata assertions depend on the descriptor being present.
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run after or alongside US1 once validator and handler surfaces exist, but final error-path assertions depend on handler wiring.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **User Story 2 (P2)**: Can be developed independently against the public contract metadata, but shares `build_playlist_items_delete_tool_descriptor` with US1.
- **User Story 3 (P3)**: Can be developed independently against the validator and safe error contract, but shares the handler surface with US1.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation tasks.
- Green implementation must be the smallest endpoint-backed change needed for that story.
- reStructuredText docstrings must be added or updated before story completion.
- Refactor tasks must preserve behavior and re-run the focused story tests.
- The full repository test suite must pass before the feature is considered complete.

---

## Parallel Opportunities

- Setup inspection tasks T002 and T003 can run in parallel after T001 starts.
- Foundational Red tasks T004, T005, T006, and T007 can run in parallel because they touch different test files.
- US1 Red tasks T012, T013, and T014 can run in parallel because they target unit, integration, and contract files.
- US2 Red tasks T022 and T024 can run in parallel because they touch separate contract and catalog files.
- US3 Red tasks T033, T034, and T035 can run in parallel because they cover unit, contract, and integration error behavior.
- Polish review tasks T043 and T044 can run in parallel after all story implementation is complete.

## Parallel Example: User Story 1

```bash
Task: "T012 [P] [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T013 [P] [US1] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
Task: "T014 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T024 [P] [US2] Add failing default catalog metadata assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T034 [P] [US3] Add failing safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T035 [P] [US3] Add failing dispatcher error propagation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup inspection.
2. Complete Phase 2 foundational export/scaffold work.
3. Complete Phase 3 User Story 1.
4. Stop and validate the MVP with `python3 -m pytest tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_playlist_items_contract.py`.

### Incremental Delivery

1. Add User Story 1 to expose an executable deletion tool and deletion acknowledgment.
2. Add User Story 2 to make quota, OAuth, destructive semantics, examples, and out-of-scope boundaries fully discoverable.
3. Add User Story 3 to harden invalid request and upstream failure behavior.
4. Run focused feature tests, full `python3 -m pytest`, and `python3 -m ruff check .`.

### Parallel Team Strategy

1. One contributor completes Setup and Foundational tasks.
2. After Foundational, separate contributors can add Red tests for US1, US2, and US3 in parallel.
3. Coordinate Green implementation through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py` to avoid conflicting edits.
4. Merge story increments only after focused tests pass and docstrings are complete.

---

## Notes

- [P] tasks indicate work that can proceed independently when no shared file conflict exists.
- [US1], [US2], and [US3] labels map directly to the prioritized user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md`.
- Every Python implementation task must preserve or add reStructuredText docstrings before the story is complete.
- Final completion requires passing focused feature tests, full repository tests, and Ruff.
