# Tasks: YT-106 Layer 1 Endpoint `captions.update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align the feature-local implementation guide and design artifacts before code changes begin

- [X] T001 Sync implementation targets and verification commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/quickstart.md
- [X] T002 [P] Sync update-boundary terminology in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/data-model.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core transport and contract groundwork that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add shared validator support for body-required caption-update rules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py
- [X] T004 [P] Add `PUT` request-construction coverage for body-only and body-plus-media caption updates in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T005 [P] Export the planned `captions.update` wrapper builder in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T006 Add foundational transport regression coverage for caption-update request construction in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Update a Caption Track Through a Typed Wrapper (Priority: P1) 🎯 MVP

**Goal**: Add a typed internal `captions.update` wrapper that can execute valid metadata-only and content-replacement update requests and return an updated caption resource through the existing Layer 1 executor flow

**Independent Test**: Invoke `captions.update` with a valid caption resource update body and optionally `media`, then confirm the wrapper exposes the expected metadata and returns an updated caption resource shape through the shared executor path

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing wrapper metadata and update-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T008 [P] [US1] Add failing executor success-path tests for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
- [X] T009 [P] [US1] Add failing transport tests for `captions.update` request serialization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py

### Implementation for User Story 1

- [X] T010 [US1] Implement `CaptionsUpdateWrapper` and `build_captions_update_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T011 [US1] Wire the `captions.update` wrapper export into /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T012 [US1] Implement `captions.update` request execution and updated-resource parsing in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T013 [US1] Add or update reStructuredText docstrings for `captions.update` wrapper and request-building functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T014 [US1] Refactor `captions.update` success-path naming and request-shape handling while keeping US1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: User Story 1 should now be independently functional and testable

---

## Phase 4: User Story 2 - Understand Authorization and Update Preconditions Before Reuse (Priority: P2)

**Goal**: Make OAuth-only behavior, body-required update preconditions, optional media replacement, and optional delegation context explicit enough that higher-layer authors cannot mistake `captions.update` for a public or loosely shaped path

**Independent Test**: Review the wrapper contract and exercise validation failures to confirm that missing-body, media-only, and unauthorized requests are rejected before execution and that optional delegation guidance remains visible

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add failing contract checks for OAuth, media-update, and delegation guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py
- [X] T016 [P] [US2] Add failing validation tests for media-only, invalid-body, and wrong-auth requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T017 [P] [US2] Add failing delegated-update integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 2

- [X] T018 [US2] Implement OAuth-only and body-required validation for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T019 [US2] Implement body-only versus body-plus-media request serialization and delegation-field handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T020 [US2] Update auth and media contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/contracts/layer1-captions-update-auth-media-contract.md
- [X] T021 [US2] Add or update reStructuredText docstrings for changed validation and request-building functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T022 [US2] Refactor auth, media, and delegation validation while keeping US2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Review Caption-Update Readiness for Follow-on Work (Priority: P3)

**Goal**: Make the `captions.update` wrapper reviewable for downstream caption-management work by surfacing quota, request boundaries, auth, media guidance, and updated-resource visibility in contracts and higher-layer summaries

**Independent Test**: Review the feature-local contracts and higher-layer summary behavior to confirm a reviewer can verify quota cost `450`, OAuth-required access, body-required updates, optional media replacement, and delegation guidance without external docs

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add failing higher-layer summary coverage for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T024 [P] [US3] Add failing contract-artifact checks for quota and update-boundary visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py

### Implementation for User Story 3

- [X] T025 [US3] Extend higher-layer summary support for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US3] Finalize `captions.update` review-surface notes for quota, media, and delegation visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T027 [US3] Sync wrapper-contract language with the final review surface in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/contracts/layer1-captions-update-wrapper-contract.md
- [X] T028 [US3] Add or update reStructuredText docstrings for changed higher-layer summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T029 [US3] Refactor `captions.update` review-surface wording and story-3 assertions while keeping US3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, regression coverage, and repository-wide validation

- [X] T030 [P] Validate the implementation flow and command list against /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/quickstart.md
- [X] T031 [P] Review shared caption regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T032 Review final reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T033 Run the targeted YT-106 validation commands documented in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/quickstart.md
- [X] T034 Run the full repository test suite and lint commands documented in /Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/quickstart.md and fix any failures across /Users/ctgunn/Projects/youtube-mcp-server/src/ and /Users/ctgunn/Projects/youtube-mcp-server/tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and delivers the MVP caption-update wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the US1 wrapper seam to enforce auth and update preconditions
- **User Story 3 (P3)**: Starts after US1 and US2 because the final review surface depends on the completed wrapper behavior and validation rules

### Within Each User Story

- Write tests first and confirm they fail before implementation
- Implement the minimum code needed to satisfy the failing tests
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass and keep the story-specific tests green
- Before marking the feature complete, run the full repository test suite and fix any failures

### Dependency Graph

- **T001-T002** → **T003-T006** → **T007-T014** → **T015-T022** → **T023-T029** → **T030-T034**
- **US1** depends on Foundational only
- **US2** depends on Foundational and the completed US1 wrapper seam
- **US3** depends on US1 and US2

### Parallel Opportunities

- **Setup**: T002 can run alongside T001 once the quickstart scope is known
- **Foundational**: T004 and T005 can run in parallel after T003; T006 follows the foundational transport seam
- **US1**: T007, T008, and T009 can run in parallel
- **US2**: T015, T016, and T017 can run in parallel
- **US3**: T023 and T024 can run in parallel
- **Polish**: T030 and T031 can run in parallel before the final validation tasks

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests together for User Story 1:
Task: "T007 [US1] Add failing wrapper metadata and update-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T008 [US1] Add failing executor success-path tests for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T009 [US1] Add failing transport tests for `captions.update` request serialization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch the Red tests together for User Story 2:
Task: "T015 [US2] Add failing contract checks for OAuth, media-update, and delegation guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
Task: "T016 [US2] Add failing validation tests for media-only, invalid-body, and wrong-auth requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T017 [US2] Add failing delegated-update integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Launch the Red tests together for User Story 3:
Task: "T023 [US3] Add failing higher-layer summary coverage for `captions.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "T024 [US3] Add failing contract-artifact checks for quota and update-boundary visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the independent test for US1
5. Demo the internal `captions.update` wrapper once the updated-resource path is stable

### Incremental Delivery

1. Complete Setup and Foundational work
2. Deliver User Story 1 as the MVP typed wrapper
3. Add User Story 2 to harden auth and update preconditions
4. Add User Story 3 to finalize reviewability and downstream reuse support
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup and Foundational tasks
2. Once Foundational is complete:
   - Developer A handles US1 wrapper and integration work
   - Developer B prepares US2 contract and validation tests
   - Developer C prepares US3 review-surface and consumer tests after US1 stabilizes
3. Rejoin for the polish and full-suite validation phase

---

## Notes

- All tasks use the required checklist format with Task ID, optional `[P]`, optional story label, and exact file paths
- User story tasks map directly to the P1, P2, and P3 stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/spec.md`
- The suggested MVP scope is User Story 1 after Setup and Foundational completion
