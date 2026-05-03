# Tasks: YT-139 Layer 1 Endpoint `playlists.delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the implementation seam, contract scope, and test targets before code changes begin

- [X] T001 Review feature scope and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/spec.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/plan.md
- [X] T002 [P] Review delete-boundary decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/data-model.md
- [X] T003 [P] Review contract and quickstart expectations in /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-auth-delete-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared `playlists.delete` wiring that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Add failing shared registration and transport coverage for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T005 Add minimal `playlists.delete` scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T006 Refactor shared `playlists.delete` scaffolding and add reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready, `playlists.delete` seams exist, and user story work can begin

---

## Phase 3: User Story 1 - Delete a Playlist Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a callable internal `playlists.delete` wrapper that executes an authorized playlist deletion and returns a normalized delete acknowledgment

**Independent Test**: Submit a valid authorized `playlists.delete` request with `id` for an existing playlist and confirm the wrapper returns a normalized result containing the deleted playlist identity and delete acknowledgment state

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing wrapper success-path tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T008 [P] [US1] Add failing transport success-path tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T009 [P] [US1] Add failing integration success-path tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T010 [US1] Implement the `PlaylistsDeleteWrapper` class, `build_playlists_delete_wrapper` factory, and request validator in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T011 [US1] Implement `playlists.delete` request construction and success payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T012 [US1] Export the `playlists.delete` builder and delete-summary entry points in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T013 [US1] Add or update reStructuredText docstrings for the `playlists.delete` success-path code in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T014 [US1] Refactor the `playlists.delete` success path while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: User Story 1 is independently functional and can delete a playlist through the internal Layer 1 wrapper

---

## Phase 4: User Story 2 - Review Quota and OAuth Expectations Before Reuse (Priority: P2)

**Goal**: Make the wrapper’s quota, OAuth requirement, required fields, and delete-boundary notes reviewable without reading transport internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output and confirm they expose quota cost `50`, OAuth-only access, required `id`, and unsupported delete-shape guidance for `playlists.delete`

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add failing metadata review-surface tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T016 [P] [US2] Add failing consumer-summary tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T017 [P] [US2] Add failing feature-contract review tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlists_contract.py

### Implementation for User Story 2

- [X] T018 [US2] Implement `playlists.delete` review-surface metadata and delete-boundary notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T019 [US2] Implement the higher-layer playlist delete summary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US2] Update /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-wrapper-contract.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-auth-delete-contract.md to match the implemented review surface and delete guidance
- [X] T021 [US2] Add or update reStructuredText docstrings for review-surface and summary changes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T022 [US2] Refactor review-surface and summary wording while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlists_contract.py green

**Checkpoint**: User Story 2 is independently testable through metadata, contract, and consumer review surfaces

---

## Phase 5: User Story 3 - Reject Invalid or Unauthorized Delete Requests Clearly (Priority: P3)

**Goal**: Distinguish malformed requests, unsupported delete shapes, missing OAuth access, and upstream delete failures from successful delete outcomes

**Independent Test**: Submit requests missing `id`, using unsupported delete fields, lacking OAuth access, and receiving an upstream target failure, then confirm the outcomes remain explicitly distinct from one another and from successful deletion acknowledgments

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add failing invalid-request and auth-boundary tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T024 [P] [US3] Add failing transport error-normalization tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T025 [P] [US3] Add failing integration failure-boundary tests for `playlists.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T026 [US3] Implement `playlists.delete` request validation for required identifier and unsupported-field boundaries in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T027 [US3] Implement `playlists.delete` error-category handling and failure-path payload fallbacks in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T028 [US3] Update the delete-failure interpretation guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/layer1-playlists-delete-auth-delete-contract.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/quickstart.md
- [X] T029 [US3] Add or update reStructuredText docstrings for `playlists.delete` validation and failure-path logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T030 [US3] Refactor `playlists.delete` failure handling while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: All user stories are independently functional and their failure boundaries are reviewable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation-aligned validation and full-suite proof

- [X] T031 [P] Run quickstart validation steps from /Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/quickstart.md
- [X] T032 [P] Review touched reStructuredText docstrings across /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T033 Run the full repository test suite and resolve any failing tests with `python3 -m pytest` and `python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server

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
Task: "T023 Add failing invalid-request and auth-boundary tests in tests/unit/test_layer1_foundation.py"
Task: "T024 Add failing transport error-normalization tests in tests/unit/test_youtube_transport.py"
Task: "T025 Add failing integration failure-boundary tests in tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational
3. Complete Phase 3 User Story 1
4. Stop and validate the internal `playlists.delete` success path independently

### Incremental Delivery

1. Complete Setup and Foundational work to expose the shared `playlists.delete` seam
2. Deliver User Story 1 for the callable delete wrapper
3. Deliver User Story 2 for reviewable quota, OAuth, and delete-boundary guidance
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
