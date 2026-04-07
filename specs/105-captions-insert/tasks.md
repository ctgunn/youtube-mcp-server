# Tasks: YT-105 Layer 1 Endpoint `captions.insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align the feature-local implementation guide and design artifacts before code changes begin

- [X] T001 Sync implementation targets and verification commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/quickstart.md
- [X] T002 [P] Sync request-shape and review-surface terminology in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/data-model.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core transport and contract groundwork that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add shared validator support for metadata-plus-upload request rules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py
- [X] T004 [P] Add upload-aware non-GET request construction support for caption writes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T005 [P] Export the planned `captions.insert` wrapper builder in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T006 Add foundational transport regression coverage for upload-sensitive request construction in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Caption Track Through a Typed Wrapper (Priority: P1) 🎯 MVP

**Goal**: Add a typed internal `captions.insert` wrapper that can execute a valid caption-creation request and return a created caption resource through the existing Layer 1 executor flow

**Independent Test**: Invoke `captions.insert` with valid caption metadata and valid media-upload input, then confirm the wrapper exposes the expected metadata and returns a created caption resource shape through the shared executor path

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing wrapper metadata and create-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T008 [P] [US1] Add failing executor success-path tests for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T009 [US1] Implement `CaptionsInsertWrapper` and `build_captions_insert_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T010 [US1] Wire the `captions.insert` wrapper export into /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T011 [US1] Implement `captions.insert` request execution and created-resource parsing in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T012 [US1] Add or update reStructuredText docstrings for `captions.insert` wrapper and request-building functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T013 [US1] Refactor `captions.insert` success-path naming and request-shape handling while keeping US1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: User Story 1 should now be independently functional and testable

---

## Phase 4: User Story 2 - Understand Authorization and Upload Preconditions Before Reuse (Priority: P2)

**Goal**: Make OAuth-only behavior, metadata-plus-upload preconditions, and optional delegation context explicit enough that higher-layer authors cannot mistake `captions.insert` for a public or metadata-only path

**Independent Test**: Review the wrapper contract and exercise validation failures to confirm that metadata-only, upload-only, and unauthorized requests are rejected before execution and that optional delegation guidance remains visible

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T014 [P] [US2] Add failing contract checks for OAuth, upload, and delegation guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py
- [X] T015 [P] [US2] Add failing validation tests for metadata-only, upload-only, and wrong-auth requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py

### Implementation for User Story 2

- [X] T016 [US2] Implement OAuth-only and metadata-plus-upload validation for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T017 [US2] Implement upload-sensitive request serialization and delegation-field handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T018 [US2] Update auth and upload contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-auth-upload-contract.md
- [X] T019 [US2] Add or update reStructuredText docstrings for changed validation and request-building functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T020 [US2] Refactor auth, upload, and delegation validation while keeping US2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Review Caption-Creation Readiness for Follow-on Work (Priority: P3)

**Goal**: Make the `captions.insert` wrapper reviewable for downstream caption-management work by surfacing quota, request boundaries, auth, upload guidance, and created-resource visibility in contracts and higher-layer summaries

**Independent Test**: Review the feature-local contracts and higher-layer summary behavior to confirm a reviewer can verify quota cost `400`, OAuth-only access, upload requirements, optional delegation guidance, and created-resource readiness without external docs

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T021 [P] [US3] Add failing higher-layer summary coverage for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T022 [P] [US3] Add failing contract-artifact checks for quota and request-boundary visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py

### Implementation for User Story 3

- [X] T023 [US3] Extend higher-layer summary support for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T024 [US3] Finalize `captions.insert` review-surface notes for quota, upload, and delegation visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T025 [US3] Sync wrapper-contract language with the final review surface in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-wrapper-contract.md
- [X] T026 [US3] Add or update reStructuredText docstrings for changed higher-layer summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T027 [US3] Refactor `captions.insert` review-surface wording and story-3 assertions while keeping US3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, regression coverage, and repository-wide validation

- [X] T028 [P] Validate the implementation flow and command list against /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/quickstart.md
- [X] T029 [P] Review shared caption regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T030 Review final reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T031 Run the targeted YT-105 validation commands documented in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/quickstart.md
- [X] T032 Run the full repository test suite and lint commands documented in /Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/quickstart.md and fix any failures across /Users/ctgunn/Projects/youtube-mcp-server/src/ and /Users/ctgunn/Projects/youtube-mcp-server/tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and delivers the MVP caption-creation wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the US1 wrapper seam to enforce auth and upload preconditions
- **User Story 3 (P3)**: Starts after US1 and US2 because the final review surface depends on the completed wrapper behavior and validation rules

### Within Each User Story

- Write tests first and confirm they fail before implementation
- Implement the minimum code needed to satisfy the failing tests
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass and keep the story-specific tests green
- Before marking the feature complete, run the full repository test suite and fix any failures

### Dependency Graph

- **T001-T002** → **T003-T006** → **T007-T013** → **T014-T020** → **T021-T027** → **T028-T032**
- **US1** depends on Foundational only
- **US2** depends on Foundational and the completed US1 wrapper seam
- **US3** depends on US1 and US2

### Parallel Opportunities

- **Setup**: T002 can run alongside T001 once the quickstart scope is known
- **Foundational**: T004 and T005 can run in parallel after T003; T006 follows the foundational transport seam
- **US1**: T007 and T008 can run in parallel
- **US2**: T014 and T015 can run in parallel
- **US3**: T021 and T022 can run in parallel
- **Polish**: T028 and T029 can run in parallel before the final validation tasks

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests together for User Story 1:
Task: "T007 [US1] Add failing wrapper metadata and create-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T008 [US1] Add failing executor success-path tests for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch the Red tests together for User Story 2:
Task: "T014 [US2] Add failing contract checks for OAuth, upload, and delegation guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
Task: "T015 [US2] Add failing validation tests for metadata-only, upload-only, and wrong-auth requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Launch the Red tests together for User Story 3:
Task: "T021 [US3] Add failing higher-layer summary coverage for `captions.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "T022 [US3] Add failing contract-artifact checks for quota and request-boundary visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the independent test for US1
5. Demo the internal `captions.insert` wrapper once the created-resource path is stable

### Incremental Delivery

1. Complete Setup and Foundational work
2. Deliver User Story 1 as the MVP typed wrapper
3. Add User Story 2 to harden auth and upload preconditions
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
- User story tasks map directly to the P1, P2, and P3 stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/spec.md`
- The suggested MVP scope is User Story 1 after Setup and Foundational completion
