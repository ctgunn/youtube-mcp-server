# Tasks: YT-135 Layer 1 Endpoint `playlistItems.delete`

**Input**: Design documents from `/specs/135-playlist-items-delete/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths in this task list use the repository structure defined in `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/plan.md`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm implementation seams and test surfaces before changing code

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/research.md` to align the implementation scope
- [X] T002 Inspect existing playlist-item and delete-wrapper patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Inspect the relevant test seams in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared failing coverage that establishes the endpoint surface before any story-specific implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing metadata and export coverage for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T005 [P] Add failing transport and consumer-summary coverage for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T006 [P] Add failing playlist-item review-surface coverage for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Remove a Playlist Item Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed internal `playlistItems.delete` wrapper that accepts a valid authorized identifier-only request and returns a normalized successful deletion acknowledgment

**Independent Test**: Submit a valid authorized `playlistItems.delete` request for an existing playlist item through the representative wrapper and verify the result confirms deletion while preserving the deleted playlist-item identity

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing unit coverage for identifier validation and OAuth enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T008 [P] [US1] Add failing integration coverage for authorized `playlistItems.delete` execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T009 [US1] Implement the `playlistItems.delete` wrapper class, builder, and identifier validator in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T010 [US1] Export `build_playlist_items_delete_wrapper` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T011 [US1] Implement `playlistItems.delete` request construction and successful deletion payload normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T012 [US1] Add the higher-layer successful deletion summary for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T013 [US1] Add or update reStructuredText docstrings for `playlistItems.delete` changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T014 [US1] Refactor the `playlistItems.delete` happy-path implementation while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 1 should now be independently functional and demoable as the MVP

---

## Phase 4: User Story 2 - Review Quota and OAuth Expectations Before Reuse (Priority: P2)

**Goal**: Make quota cost, OAuth requirements, and delete-boundary guidance reviewable from wrapper metadata, higher-layer summaries, and contract-facing test surfaces

**Independent Test**: Review the maintainer-facing wrapper surface and higher-layer summary for `playlistItems.delete` and confirm the endpoint identity, quota cost `50`, auth mode, and required identifier input are visible without reading implementation details

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add failing metadata-contract coverage for `playlistItems.delete` quota, auth mode, and notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T016 [P] [US2] Add failing playlist-item and consumer-contract coverage for `playlistItems.delete` reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T017 [US2] Update `playlistItems.delete` wrapper metadata notes, quota visibility, and auth review fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T018 [US2] Update higher-layer summary fields for quota, auth, and delete guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T019 [US2] Add or update reStructuredText docstrings for review-surface changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T020 [US2] Refactor quota/auth review wording while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Stories 1 and 2 should both work independently, with US2 proving the wrapper is reviewable for reuse

---

## Phase 5: User Story 3 - Reject Invalid or Unauthorized Delete Requests Clearly (Priority: P3)

**Goal**: Preserve clear normalized distinctions between invalid requests, missing OAuth access, unavailable targets, and upstream delete failures

**Independent Test**: Submit malformed, unauthorized, not-found, and upstream-rejected `playlistItems.delete` requests and verify the wrapper surfaces distinct normalized outcomes instead of a generic failure

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T021 [P] [US3] Add failing unit and transport coverage for missing identifiers, unsupported fields, and normalized delete failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T022 [P] [US3] Add failing integration and playlist-item contract coverage for auth, target-state, and upstream failure distinctions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`

### Implementation for User Story 3

- [X] T023 [US3] Enforce unsupported-field and invalid-identifier rejection paths for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T024 [US3] Implement normalized auth, target-state, and upstream delete failure handling for `playlistItems.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T025 [US3] Surface failure-boundary context for higher-layer review in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US3] Add or update reStructuredText docstrings for failure-boundary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T027 [US3] Refactor failure-boundary implementation while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: All user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation alignment, and full validation

- [X] T028 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/contracts/layer1-playlist-items-delete-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/contracts/layer1-playlist-items-delete-auth-delete-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/quickstart.md` for final consistency with the implemented wrapper
- [X] T029 [P] Run the targeted playlist-item delete validation suite in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`
- [X] T030 Run the full repository test suite and resolve any failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`
- [X] T031 Run final lint validation for touched integration modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and delivers the MVP
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the `playlistItems.delete` wrapper surface introduced by US1
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the basic delete path introduced by US1

### Within Each User Story

- Red tests MUST be written and fail before implementation
- Wrapper validation and transport behavior come before higher-layer summary refinement
- reStructuredText docstrings MUST be updated before the story is complete
- Refactor only after story tests pass
- Before feature completion, run the full repository test suite and fix any failures

### Story Completion Order

- Foundational coverage → US1 → US2 and US3 → Polish
- **Suggested MVP scope**: Complete through US1 before taking on US2 or US3

---

## Parallel Examples

### Parallel Example: Foundational Phase

```bash
# Launch independent failing coverage additions together:
Task: "Add failing transport and consumer-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "Add failing playlist-item review-surface coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py"
```

### Parallel Example: User Story 1

```bash
# Launch US1 Red tests together:
Task: "Add failing unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

### Parallel Example: User Story 2

```bash
# Launch US2 contract checks together:
Task: "Add failing metadata-contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing playlist-item and consumer-contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

### Parallel Example: User Story 3

```bash
# Launch US3 failure-boundary tests together:
Task: "Add failing unit and transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration and playlist-item contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the authorized delete flow independently

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
- Each user story is independently testable per `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`
- Completion requires both targeted validation and a passing full repository test-suite run
