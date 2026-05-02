# Tasks: YT-138 Layer 1 Endpoint `playlists.update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/contracts)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the implementation seam, contract scope, and test targets before code changes begin

- [X] T001 Review feature scope and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/spec.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/plan.md
- [X] T002 [P] Review update-boundary decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/data-model.md
- [X] T003 [P] Review contract and quickstart expectations in /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/contracts/layer1-playlists-update-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/contracts/layer1-playlists-update-auth-write-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared `playlists.update` wiring that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Add failing shared registration and transport coverage for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T005 Add minimal `playlists.update` scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T006 Refactor shared `playlists.update` scaffolding and add reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready, `playlists.update` seams exist, and user story work can begin

---

## Phase 3: User Story 1 - Update an Existing Playlist Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a callable internal `playlists.update` wrapper that executes an authorized playlist update and returns a normalized updated-playlist result

**Independent Test**: Submit a valid authorized `playlists.update` request with `part=snippet`, `body.id`, and `body.snippet.title`, then confirm the wrapper updates the playlist and returns normalized playlist identity and title data

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing wrapper success-path tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T008 [P] [US1] Add failing transport success-path tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T009 [P] [US1] Add failing integration success-path tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T010 [US1] Implement the `PlaylistsUpdateWrapper` class and `build_playlists_update_wrapper` factory in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T011 [US1] Implement `playlists.update` request construction and success payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T012 [US1] Export the `playlists.update` builder and summary entry points in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T013 [US1] Add or update reStructuredText docstrings for the `playlists.update` success-path code in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T014 [US1] Refactor the `playlists.update` success path while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: User Story 1 is independently functional and can update a playlist through the internal Layer 1 wrapper

---

## Phase 4: User Story 2 - Review Writable-Field and Authorization Expectations Before Reuse (Priority: P2)

**Goal**: Make the wrapper’s quota, OAuth requirement, required fields, and writable-boundary notes reviewable without reading transport internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output and confirm they expose quota cost `50`, OAuth-only access, `part=snippet`, `body.id`, and `body.snippet.title` as the required update boundary

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add failing metadata review-surface tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T016 [P] [US2] Add failing consumer-summary tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T017 [P] [US2] Add failing feature-contract review tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlists_contract.py

### Implementation for User Story 2

- [X] T018 [US2] Implement `playlists.update` review-surface metadata and writable-boundary notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T019 [US2] Implement the higher-layer playlist update summary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US2] Add or update reStructuredText docstrings for review-surface and summary changes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T021 [US2] Refactor review-surface and summary wording while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlists_contract.py green

**Checkpoint**: User Story 2 is independently testable through metadata, contract, and consumer review surfaces

---

## Phase 5: User Story 3 - Reject Invalid or Unauthorized Playlist-Update Requests Clearly (Priority: P3)

**Goal**: Distinguish malformed requests, unsupported writable fields, missing OAuth access, and upstream update failures from successful update outcomes

**Independent Test**: Submit requests missing `body.id`, missing `body.snippet.title`, using unsupported writable fields or parts, lacking OAuth access, and receiving an upstream target failure, then confirm the outcomes remain explicitly distinct

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T022 [P] [US3] Add failing invalid-request and auth-boundary tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T023 [P] [US3] Add failing transport error-normalization tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T024 [P] [US3] Add failing integration failure-boundary tests for `playlists.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T025 [US3] Implement `playlists.update` request validation for required identifier and writable-field boundaries in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T026 [US3] Implement `playlists.update` error-category handling and failure-path payload fallbacks in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T027 [US3] Add or update reStructuredText docstrings for `playlists.update` validation and failure-path logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T028 [US3] Refactor `playlists.update` failure handling while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: All user stories are independently functional and their failure boundaries are reviewable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation-aligned validation and full-suite proof

- [X] T029 [P] Run quickstart validation steps from /Users/ctgunn/Projects/youtube-mcp-server/specs/138-playlists-update/quickstart.md
- [X] T030 [P] Review touched reStructuredText docstrings across /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T031 Run the full repository test suite and resolve any failing tests with `python3 -m pytest` and `python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2 and is the MVP slice
- **User Story 2 (P2)**: Starts after Phase 2 and depends on the US1 wrapper path existing, but remains independently testable through review surfaces
- **User Story 3 (P3)**: Starts after Phase 2 and depends on the US1 execution path existing, but remains independently testable through explicit failure-boundary scenarios

### Within Each User Story

- Red tests MUST be written and fail before implementation
- Wrapper and transport behavior before consumer or contract-surface refinement
- Core implementation before refactor
- ReStructuredText docstrings before closing the story
- Full repository validation before the feature is complete

### Story Completion Order

1. Phase 1 Setup
2. Phase 2 Foundational
3. User Story 1 (MVP)
4. User Story 2
5. User Story 3
6. Phase 6 Polish

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests for User Story 1 together:
Task: "T007 Add failing wrapper success-path tests in tests/unit/test_layer1_foundation.py"
Task: "T008 Add failing transport success-path tests in tests/unit/test_youtube_transport.py"
Task: "T009 Add failing integration success-path tests in tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch the review-surface Red tests for User Story 2 together:
Task: "T015 Add failing metadata review-surface tests in tests/contract/test_layer1_metadata_contract.py"
Task: "T016 Add failing consumer-summary tests in tests/contract/test_layer1_consumer_contract.py"
Task: "T017 Add failing feature-contract review tests in tests/contract/test_layer1_playlists_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch the failure-boundary Red tests for User Story 3 together:
Task: "T022 Add failing invalid-request and auth-boundary tests in tests/unit/test_layer1_foundation.py"
Task: "T023 Add failing transport error-normalization tests in tests/unit/test_youtube_transport.py"
Task: "T024 Add failing integration failure-boundary tests in tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational
3. Complete Phase 3 User Story 1
4. Stop and validate the internal `playlists.update` success path independently

### Incremental Delivery

1. Complete Setup and Foundational work to expose the shared `playlists.update` seam
2. Deliver User Story 1 for the callable update wrapper
3. Deliver User Story 2 for reviewable quota, OAuth, and writable-boundary guidance
4. Deliver User Story 3 for explicit invalid-request, auth, and upstream-failure boundaries
5. Finish with quickstart validation and full-suite proof

### Parallel Team Strategy

1. One engineer completes Setup and Foundational work
2. After Phase 2:
   - Engineer A can drive US1 success-path implementation
   - Engineer B can prepare US2 contract and consumer Red tests
   - Engineer C can prepare US3 failure-boundary Red tests
3. Merge story work in priority order with full-suite validation at the end

---

## Notes

- All task lines use the required checklist format
- `[P]` tasks are limited to work that can proceed in parallel without incomplete-task dependencies
- User story labels appear only on user story phase tasks
- Each user story remains independently testable based on the criteria listed above
