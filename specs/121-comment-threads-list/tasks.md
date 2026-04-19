# Tasks: YT-121 Layer 1 Endpoint `commentThreads.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python changes must include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Every task includes an exact file path

## Path Conventions

- Single project layout rooted at `/Users/ctgunn/Projects/youtube-mcp-server`
- Source code under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review the planned implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md
- [X] T002 Review the existing list-wrapper and comment retrieval patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T003 [P] Review the current Layer 1 retrieval coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration and transport seams that all comment-thread stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing foundational wrapper registration and review-surface coverage for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T005 [P] Add failing foundational transport coverage for the `GET /commentThreads` request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T006 [P] Create failing foundational contract-artifact coverage for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py
- [X] T007 [P] Add failing foundational higher-layer summary coverage for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T008 Implement `CommentThreadsListWrapper`, the builder, selector helpers, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T009 Implement foundational transport recognition and normalized payload parsing for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T010 Implement foundational higher-layer summary scaffolding for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T011 Refactor foundational helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Retrieve Comment Threads Through Supported Lookup Modes (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `commentThreads.list` wrapper that can retrieve threads by `videoId`, `allThreadsRelatedToChannelId`, and `id` through the shared executor flow and return stable normalized retrieval results

**Independent Test**: Submit valid `commentThreads.list` requests for video-based, channel-related, and ID-based lookup and confirm the wrapper executes through the shared executor and returns normalized successful results for matching threads

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Add failing happy-path wrapper tests for `commentThreads.list` metadata, required `part`, selector exclusivity, and supported selector handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T013 [P] [US1] Add failing transport tests for `GET /commentThreads` request construction and successful payload normalization for `videoId`, `allThreadsRelatedToChannelId`, and `id` selectors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T014 [P] [US1] Add failing integration tests for video-based, channel-related, and ID-based retrieval through `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T015 [US1] Implement the valid retrieval path, supported optional modifiers, and selector-aware execution for successful `commentThreads.list` calls in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T016 [US1] Implement normalized successful retrieval payload handling, including near-raw list responses and empty upstream successes, in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T017 [US1] Implement a higher-layer `commentThreads.list` summary method for successful outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T018 [US1] Add or update reStructuredText docstrings for the successful retrieval path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T019 [US1] Refactor the successful retrieval path while keeping the User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: User Story 1 should now support independently testable successful retrieval requests

---

## Phase 4: User Story 2 - Understand Lookup and Access Expectations Before Reuse (Priority: P2)

**Goal**: Make the `commentThreads.list` wrapper reviewable enough that maintainers can see quota, supported selectors, optional modifiers, and access expectations without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output to confirm quota cost `1`, supported `videoId`/`allThreadsRelatedToChannelId`/`id` paths, optional modifiers, and access expectations are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T020 [P] [US2] Add failing contract-artifact coverage for `commentThreads.list` wrapper and lookup-access guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py
- [X] T021 [P] [US2] Add failing review-surface metadata coverage for selector notes and optional fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T022 [P] [US2] Add failing higher-layer review-summary coverage for `commentThreads.list` source metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T023 [US2] Author maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md
- [X] T024 [US2] Author lookup and access guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md
- [X] T025 [US2] Update maintainer-visible review notes, auth metadata, and request-shape documentation for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T026 [US2] Update higher-layer `commentThreads.list` summary fields so review consumers can see source operation, auth mode, quota, selector, and optional modifier guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T027 [US2] Add or update reStructuredText docstrings for reviewability-oriented retrieval surfaces in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T028 [US2] Refactor review-surface wording and keep the User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md

**Checkpoint**: User Story 2 should now be independently testable through review surfaces and contract artifacts

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Unsupported Thread Retrieval Requests (Priority: P3)

**Goal**: Deliver deterministic validation and distinct normalized failures for malformed, unsupported, or ineligible comment-thread retrieval requests

**Independent Test**: Submit requests with missing selectors, conflicting selectors, unsupported modifiers, and ineligible access context, then confirm the wrapper returns distinct normalized failures separate from successful no-match retrieval outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T029 [P] [US3] Add failing invalid-request and access-mismatch unit coverage for `commentThreads.list` validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T030 [P] [US3] Add failing invalid-request, access-mismatch, and empty-result transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T031 [P] [US3] Add failing invalid and no-match integration coverage for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T032 [US3] Implement deterministic validation for missing selectors, conflicting selectors, unsupported fields, and selector-specific access enforcement in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T033 [US3] Implement normalized failure categorization and successful empty-result handling for `commentThreads.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Update higher-layer `commentThreads.list` summary compatibility for failure-path expectations in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T035 [US3] Document invalid-request, access-mismatch, and successful no-match retrieval behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md
- [X] T036 [US3] Add or update reStructuredText docstrings for the failure-path retrieval logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T037 [US3] Refactor invalid and unsupported retrieval handling while keeping the User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T038 [P] Reconcile feature-level documentation and task references across /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/layer1-comment-threads-list-lookup-auth-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md
- [X] T039 [P] Review all touched Python modules for reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T040 Run the YT-121 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T041 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the User Story 1 wrapper surface
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the retrieval surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion - no dependency on other user stories
- **User Story 2 (P2)**: Depends on the `commentThreads.list` wrapper surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the `commentThreads.list` wrapper surface from User Story 1 but remains independently testable through invalid and failure-path scenarios

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper metadata and validation before consumer summary updates
- Transport normalization before success or failure summaries that depend on it
- Core implementation before integration validation (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the targeted validation flow and then the full repository suite

### Parallel Opportunities

- `T003` can run in parallel with `T001` and `T002`
- `T005`, `T006`, and `T007` can run in parallel after `T004`
- Within **US1**, `T012`, `T013`, and `T014` can run in parallel
- Within **US2**, `T020`, `T021`, and `T022` can run in parallel
- Within **US3**, `T029`, `T030`, and `T031` can run in parallel
- In the polish phase, `T038` and `T039` can run in parallel

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract/test work can begin while US1 implementation is underway; US3 Red tests can begin once the shared retrieval seam exists

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing happy-path wrapper tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comment_threads_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request and access-mismatch unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing invalid-request, access-mismatch, and empty-result transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid and no-match integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported retrieval success paths independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure handling

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, and summary seam
2. Add User Story 1 to deliver the usable retrieval path
3. Add User Story 2 to make the retrieval contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unsupported request handling
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests and contract assertions
   - Developer C can prepare User Story 3 Red tests for invalid and failure paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
