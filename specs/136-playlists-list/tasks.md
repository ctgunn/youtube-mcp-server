# Tasks: YT-136 Layer 1 Endpoint `playlists.list`

**Input**: Design documents from `/specs/136-playlists-list/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths in this task list follow the single-project structure captured in `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/plan.md`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the implementation seams, contract artifacts, and test surfaces before changing code

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/quickstart.md` to align scope
- [X] T002 Inspect the existing conditional-auth and playlist-family list-wrapper patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Inspect the relevant test seams in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared failing coverage and endpoint scaffolding that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing metadata and export coverage for `playlists.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T005 [P] Add failing transport dispatch coverage for `playlists.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Add failing higher-layer summary coverage for `playlists.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T007 Implement the shared `playlists.list` builder, export, and transport dispatch scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T008 Add or update reStructuredText docstrings for foundational `playlists.list` scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Refactor foundational `playlists.list` scaffolding while keeping foundational tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Retrieve Playlists Through Supported Filter Modes (Priority: P1) 🎯 MVP

**Goal**: Expose a typed internal `playlists.list` wrapper that supports successful channel-based, identifier-based, and owner-scoped retrieval without raw upstream request assembly

**Independent Test**: Submit valid `playlists.list` requests using `channelId`, `id`, and `mine` and verify the wrapper returns normalized successful results with stable selector context for each supported lookup mode

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing feature contract tests for channel-based, identifier-based, and owner-scoped `playlists.list` review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
- [X] T011 [P] [US1] Add failing integration tests for successful `channelId`, `id`, and `mine` retrieval flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T012 [P] [US1] Add failing transport tests for `playlists.list` query construction and selector-context preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement the `playlists.list` request shape, supported selector handling, and success-path wrapper execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `playlists.list` response normalization with `part`, `selectorName`, and `selectorValue` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Implement the higher-layer playlist retrieval summary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T016 [US1] Export the finished `playlists.list` builder and related integration surface in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T017 [US1] Add or update reStructuredText docstrings for successful retrieval behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T018 [US1] Refactor `playlists.list` success-path implementation while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 should now be independently functional and demoable as the MVP

---

## Phase 4: User Story 2 - Understand Paging and Access Expectations Before Reuse (Priority: P2)

**Goal**: Make quota, filter modes, paging rules, and selector-aware auth expectations reviewable through wrapper metadata, contracts, and higher-layer summary surfaces

**Independent Test**: Review the wrapper contract and consumer-facing summary surfaces and confirm they expose quota cost `1`, supported filter modes, filter-specific paging behavior, and public-versus-owner-scoped auth expectations without reading implementation details

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add failing metadata contract tests for quota, conditional-auth notes, and paging guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T020 [P] [US2] Add failing consumer summary contract tests for `selectorUsed`, `sourceOperation`, `sourceAuthMode`, `sourceAuthConditionNote`, and `sourceQuotaCost` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T021 [P] [US2] Add failing feature contract assertions for wrapper and filter-modes documentation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

### Implementation for User Story 2

- [X] T022 [US2] Update `playlists.list` metadata notes, auth-condition guidance, and filter-mode review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T023 [US2] Implement maintainer-facing playlist summary fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T024 [US2] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-filter-modes-contract.md` with the implemented review surfaces
- [X] T025 [US2] Add or update reStructuredText docstrings for review-surface behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Refactor `playlists.list` review-surface wording while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Stories 1 and 2 should both work independently, with US2 proving the wrapper is reviewable for reuse

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Unsupported Playlist Requests (Priority: P3)

**Goal**: Preserve distinct invalid-request, access-failure, and successful empty-result behavior for missing selectors, unsupported paging, conflicting filters, and incompatible auth usage

**Independent Test**: Submit requests with missing filters, conflicting filters, unsupported paging, unsupported modifiers, and incompatible auth modes and verify the wrapper returns distinct normalized outcomes from successful empty retrievals

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing unit tests for missing filters, conflicting filters, unsupported paging, and incompatible auth mode in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing integration tests for `invalid_request` versus `access_failure` versus empty-result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T029 [P] [US3] Add failing transport and feature-contract tests for invalid filter combinations and unsupported modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

### Implementation for User Story 3

- [X] T030 [US3] Implement selector-specific validation and incompatible auth failures for `playlists.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T031 [US3] Implement normalized empty-result and failure-boundary handling for `playlists.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T032 [US3] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/data-model.md` with the final validation and result-boundary behavior
- [X] T033 [US3] Add or update reStructuredText docstrings for validation and failure-path behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T034 [US3] Refactor `playlists.list` validation and failure wording while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, quickstart alignment, and full validation

- [X] T035 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/contracts/layer1-playlists-list-wrapper-contract.md` for final consistency with the implemented wrapper
- [X] T036 [P] Run the quickstart validation steps and update any stale commands or file references in `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/quickstart.md`
- [X] T037 Review reStructuredText docstrings across touched Python modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T038 Run the targeted `playlists.list` validation suite in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
- [X] T039 Run the full repository test suite and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`
- [X] T040 Run final lint validation for touched integration modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and delivers the MVP
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the `playlists.list` wrapper surface introduced by US1
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the basic retrieval path introduced by US1

### Within Each User Story

- Red tests MUST be written and fail before implementation
- Wrapper validation and transport behavior come before higher-layer summary refinement
- reStructuredText docstrings MUST be updated before the story is complete
- Refactor only after story tests pass
- Before feature completion, run the full repository test suite and fix any failures

### Story Completion Order

- Foundational coverage → US1 → US2 and US3 → Polish
- **Suggested MVP scope**: Complete through US1 before taking on US2 or US3

### Dependency Graph

- Phase 1 → Phase 2 → US1 → US2
- Phase 1 → Phase 2 → US1 → US3
- US2 and US3 → Phase 6

### Parallel Opportunities

- T003 can run in parallel with T001-T002 during Setup
- T005 and T006 can run in parallel during Foundational Red work
- T010, T011, and T012 can run in parallel for US1 Red work
- T019, T020, and T021 can run in parallel for US2 Red work
- T027, T028, and T029 can run in parallel for US3 Red work
- T035 and T036 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "Add failing feature contract tests for channel-based, identifier-based, and owner-scoped playlists.list review surfaces in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py"
Task: "Add failing integration tests for successful channelId, id, and mine retrieval flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing transport tests for playlists.list query construction and selector-context preservation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "Add failing metadata contract tests for quota, conditional-auth notes, and paging guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing consumer summary contract tests for selectorUsed, sourceOperation, sourceAuthMode, sourceAuthConditionNote, and sourceQuotaCost in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "Add failing feature contract assertions for wrapper and filter-modes documentation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "Add failing unit tests for missing filters, conflicting filters, unsupported paging, and incompatible auth mode in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing integration tests for invalid_request versus access_failure versus empty-result boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing transport and feature-contract tests for invalid filter combinations and unsupported modifiers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported `channelId`, `id`, and `mine` retrieval flows independently

### Incremental Delivery

1. Finish Setup and Foundational coverage
2. Deliver US1 as the first usable internal wrapper increment
3. Add US2 review-surface completeness
4. Add US3 failure-boundary hardening
5. Finish with targeted and full-suite validation

### Parallel Team Strategy

1. One contributor handles failing coverage in Phase 2 while another prepares wrapper and transport implementation notes from the design docs
2. After US1 lands, US2 and US3 can proceed in parallel because one focuses on review surfaces and the other on failure-boundary handling
3. Rejoin for Phase 6 full-suite validation and final documentation alignment

---

## Notes

- All tasks follow the required checklist format with task ID, optional `[P]`, optional story label, and exact file paths
- `[P]` tasks are limited to work that can proceed on different files or independent test surfaces
- Each user story is independently testable per `/Users/ctgunn/Projects/youtube-mcp-server/specs/136-playlists-list/spec.md`
- Completion requires both targeted validation and a passing full repository test-suite run
