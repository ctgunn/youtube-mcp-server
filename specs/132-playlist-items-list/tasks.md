# Tasks: YT-132 Layer 1 Endpoint `playlistItems.list`

**Input**: Design documents from `/specs/132-playlist-items-list/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths in this task list follow the single-project structure captured in `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature-specific test and contract scaffolding before shared implementation work begins

- [X] T001 Create the new feature contract test module for playlist item behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`
- [X] T002 [P] Add a dedicated `playlistItems.list` unit-test section scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T003 [P] Add a dedicated `playlistItems.list` transport-test section scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T004 [P] Add a dedicated `playlistItems.list` integration-test section scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared endpoint plumbing that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Add failing metadata review-surface coverage for `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T006 [P] Add failing package export and builder metadata coverage for `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T007 [P] Add failing transport dispatch coverage for `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T008 Implement the shared `playlistItems.list` builder, export, and transport dispatch scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Add or update reStructuredText docstrings for foundational `playlistItems.list` scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T010 Refactor foundational `playlistItems.list` scaffolding while keeping foundational tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Retrieve Playlist Items Through Supported Lookup Modes (Priority: P1) 🎯 MVP

**Goal**: Expose a typed internal `playlistItems.list` wrapper that supports successful playlist-based and identifier-based retrieval without raw upstream request assembly

**Independent Test**: Submit valid `playlistItems.list` requests using `playlistId` and `id` and verify the wrapper returns normalized successful results with stable selector context for each lookup mode

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Add failing feature contract tests for playlist-based and identifier-based `playlistItems.list` review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`
- [X] T012 [P] [US1] Add failing integration tests for successful `playlistId` and `id` retrieval flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T013 [P] [US1] Add failing transport tests for `playlistItems.list` query construction and selector-context preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement the `playlistItems.list` request shape, selector handling, and success-path wrapper execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T015 [US1] Implement `playlistItems.list` response normalization with `part`, `selectorName`, and `selectorValue` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T016 [US1] Implement the higher-layer playlist item retrieval summary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T017 [US1] Export the finished `playlistItems.list` builder and related integration surface in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T018 [US1] Add or update reStructuredText docstrings for successful retrieval behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T019 [US1] Refactor `playlistItems.list` success-path implementation while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Understand Selector, Paging, and Access Expectations Before Reuse (Priority: P2)

**Goal**: Make quota, selector modes, paging rules, and API-key access expectations reviewable through wrapper metadata, contracts, and higher-layer summary surfaces

**Independent Test**: Review the wrapper contract and consumer-facing summary surfaces and confirm they expose quota cost `1`, supported selectors, selector-specific paging behavior, and API-key access expectations without reading implementation details

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T020 [P] [US2] Add failing metadata contract tests for quota, API-key notes, and paging guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T021 [P] [US2] Add failing consumer summary contract tests for `selectorUsed`, `sourceOperation`, `sourceAuthMode`, and `sourceQuotaCost` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T022 [P] [US2] Add failing feature contract assertions for wrapper and selector-modes documentation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`

### Implementation for User Story 2

- [X] T023 [US2] Update `playlistItems.list` metadata notes and selector-mode review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T024 [US2] Implement maintainer-facing playlist item summary fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T025 [US2] Add or update reStructuredText docstrings for review-surface behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Refactor `playlistItems.list` review-surface wording while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Unsupported Playlist Item Requests (Priority: P3)

**Goal**: Preserve distinct invalid-request, access-failure, and successful empty-result behavior for malformed selectors, unsupported paging, and incompatible auth usage

**Independent Test**: Submit requests with missing selectors, conflicting selectors, unsupported paging, unsupported modifiers, and incompatible auth modes and verify the wrapper returns distinct normalized outcomes from successful empty retrievals

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing unit tests for missing selectors, conflicting selectors, unsupported paging, and incompatible auth mode in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing integration tests for `invalid_request` versus `access_failure` versus empty-result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T029 [P] [US3] Add failing transport and feature-contract tests for invalid selector combinations and unsupported modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`

### Implementation for User Story 3

- [X] T030 [US3] Implement selector-specific validation and incompatible auth failures for `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T031 [US3] Implement normalized empty-result and failure-boundary handling for `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T032 [US3] Add or update reStructuredText docstrings for validation and failure-path behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T033 [US3] Refactor `playlistItems.list` validation and failure wording while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T034 [P] Validate documentation consistency across `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/contracts/layer1-playlist-items-list-wrapper-contract.md`
- [X] T035 [P] Run the quickstart validation steps and update any stale commands or file references in `/Users/ctgunn/Projects/youtube-mcp-server/specs/132-playlist-items-list/quickstart.md`
- [X] T036 Review reStructuredText docstrings across touched Python modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T037 Run the full repository test suite and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`, and any additional failing files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - **US1** should be completed first because it establishes the working retrieval path
  - **US2** depends on the completed success-path review surfaces from **US1**
  - **US3** depends on the completed request-shape and response seams from **US1** and can follow **US2** or run after **US1** if review-surface work is already stable
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - MVP and base retrieval contract
- **User Story 2 (P2)**: Depends on User Story 1 success-path metadata and summary surfaces
- **User Story 3 (P3)**: Depends on User Story 1 request and response seams; may reuse User Story 2 review-surface wording but remains independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Shared builders and exports before story-specific summary and validation refinements
- Core wrapper and transport implementation before consumer summary integration (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the story or feature complete, run the full repository test suite and fix any failures

### Dependency Graph

- Phase 1 → Phase 2 → US1 → US2
- Phase 1 → Phase 2 → US1 → US3
- US2 and US3 → Phase 6

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during Setup
- T005, T006, and T007 can run in parallel during Foundational Red work
- T011, T012, and T013 can run in parallel for US1 Red work
- T020, T021, and T022 can run in parallel for US2 Red work
- T027, T028, and T029 can run in parallel for US3 Red work
- T034 and T035 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "Add failing feature contract tests for playlist-based and identifier-based playlistItems.list review surfaces in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py"
Task: "Add failing integration tests for successful playlistId and id retrieval flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing transport tests for playlistItems.list query construction and selector-context preservation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "Add failing metadata contract tests for quota, API-key notes, and paging guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing consumer summary contract tests for selectorUsed, sourceOperation, sourceAuthMode, and sourceQuotaCost in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "Add failing feature contract assertions for wrapper and selector-modes documentation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "Add failing unit tests for missing selectors, conflicting selectors, unsupported paging, and incompatible auth mode in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing integration tests for invalid_request versus access_failure versus empty-result boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing transport and feature-contract tests for invalid selector combinations and unsupported modifiers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the US1 test set independently and confirm playlist-based plus identifier-based retrieval works end to end
5. Demo the internal wrapper as the MVP increment

### Incremental Delivery

1. Complete Setup + Foundational → shared `playlistItems.list` seam is ready
2. Add User Story 1 → test independently → MVP ready
3. Add User Story 2 → test independently → maintainer review surfaces are ready
4. Add User Story 3 → test independently → failure boundaries are ready
5. Finish Polish → run quickstart and full-suite validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. One developer completes US1 to establish the base retrieval path
3. Once US1 is stable:
   - Developer A: User Story 2 review surfaces
   - Developer B: User Story 3 validation and failure boundaries
4. Team reconverges for Polish and full-suite validation

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] labels map tasks to specific user stories for traceability
- Each user story remains independently completable and testable
- Verify tests fail before implementing
- Verify refactor tasks preserve behavior and keep tests passing
