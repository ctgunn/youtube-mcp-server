# Tasks: YT-120 Layer 1 Endpoint `comments.delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature-specific implementation surface and existing test/doc artifacts before code changes begin

- [X] T001 Review the implementation scope and file map in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/plan.md`
- [X] T002 Review the user stories, independent test criteria, and acceptance scenarios in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/spec.md`
- [X] T003 [P] Review delete-boundary decisions and validation expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared seams that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add a `comments.delete` execution helper alongside existing comment helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T005 Add baseline import/export coverage for `build_comments_delete_wrapper` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T006 Add feature-local contract references for delete review coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Delete a Comment Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed internal `comments.delete` wrapper that accepts a valid authorized delete request and returns a normalized deletion acknowledgment

**Independent Test**: Submit one valid authorized delete request for an existing comment and verify that the wrapper returns a normalized successful deletion outcome with the target comment identity preserved

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add unit tests for `comments.delete` metadata, required `id`, optional `onBehalfOfContentOwner`, and OAuth enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T008 [P] [US1] Add transport tests for `DELETE /comments` request construction and normalized delete acknowledgment payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T009 [P] [US1] Add integration coverage for executing `comments.delete` through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T010 [US1] Implement the `CommentsDeleteWrapper` call path with OAuth-required enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T011 [US1] Implement `build_comments_delete_wrapper` metadata and request shape for `comments.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T012 [US1] Implement the normalized `comments.delete` transport payload and request routing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T013 [US1] Export `build_comments_delete_wrapper` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T014 [US1] Add or update reStructuredText docstrings for all new or changed `comments.delete` functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T015 [US1] Refactor the `comments.delete` wrapper and transport flow while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py` green

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Understand OAuth Expectations Before Reuse (Priority: P2)

**Goal**: Make quota, OAuth, delete preconditions, and optional delegation guidance reviewable through wrapper metadata, feature-local contracts, and higher-layer summaries

**Independent Test**: Review the wrapper metadata and feature-local contracts and verify that a maintainer can identify quota cost `50`, OAuth-required behavior, and minimum delete preconditions without reading implementation internals

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add contract tests for `comments.delete` wrapper and auth-delete artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`
- [X] T017 [P] [US2] Add metadata review-surface tests for `comments.delete` identity, quota, auth mode, and notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T018 [P] [US2] Add higher-layer summary tests for `comments.delete` reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T019 [US2] Update `comments.delete` wrapper notes and review-surface details for quota, OAuth, delete preconditions, and optional delegation guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T020 [US2] Implement a higher-layer `comments.delete` summary path in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T021 [US2] Align the feature-local wrapper contract with the implemented review surface in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-wrapper-contract.md`
- [X] T022 [US2] Align the feature-local auth-delete contract with the implemented authorization and delete-precondition behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-auth-delete-contract.md`
- [X] T023 [US2] Add or update reStructuredText docstrings for changed higher-layer summary functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T024 [US2] Refactor metadata, summary wording, and contract text while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` green

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Delete Requests (Priority: P3)

**Goal**: Preserve distinct normalized outcomes for invalid request shapes, missing authorization, unavailable targets, and normalized upstream delete failures

**Independent Test**: Submit malformed, unauthorized, and unavailable-target delete requests and verify that the wrapper and transport produce explicit normalized outcomes distinct from successful deletion acknowledgments

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T025 [P] [US3] Add unit tests for unsupported identifier shapes and invalid optional delegation handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T026 [P] [US3] Add transport tests for normalized `invalid_request`, `auth`, and target-state or upstream delete failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T027 [P] [US3] Add integration and contract coverage for distinct failure-boundary messaging in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py`

### Implementation for User Story 3

- [X] T028 [US3] Tighten `comments.delete` request validation and unsupported-input handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T029 [US3] Implement normalized failure categorization for `comments.delete` transport errors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T030 [US3] Update the auth-delete contract with invalid-shape, unavailable-target, and upstream-boundary guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/layer1-comments-delete-auth-delete-contract.md`
- [X] T031 [US3] Update the data model failure-boundary and outcome wording to match implementation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/data-model.md`
- [X] T032 [US3] Add or update reStructuredText docstrings for changed validation and failure-normalization functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T033 [US3] Refactor failure wording and delete-boundary naming while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py` green

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T034 [P] Update the implementation walkthrough and verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/quickstart.md`
- [X] T035 [P] Review shared reStructuredText docstrings across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T036 Run targeted YT-120 validation from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_comments_contract.py`
- [X] T037 Run the full repository test suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest` and fix any failures before completion
- [X] T038 Run lint validation from `/Users/ctgunn/Projects/youtube-mcp-server` with `ruff check .` and fix any remaining issues before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - this is the MVP and has no dependency on other stories
- **User Story 2 (P2)**: Depends on User Story 1 because review-surface and summary work builds on the working `comments.delete` wrapper
- **User Story 3 (P3)**: Depends on User Story 1 and User Story 2 because failure-boundary validation relies on the implemented wrapper, transport, and review contracts

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper and transport implementation before exports or higher-layer summaries
- Contract and review-surface alignment before story completion
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run all affected test suites
- Before marking the story or feature complete, run the full repository test suite and fix any failures

### Parallel Opportunities

- T003 can run in parallel with T001-T002
- T004-T006 touch different files and can be prepared in parallel once setup review is complete
- Within **US1**, T007-T009 can run in parallel
- Within **US2**, T016-T018 can run in parallel
- Within **US3**, T025-T027 can run in parallel
- T034-T035 can run in parallel during polish

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "T007 [US1] unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T008 [US1] transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T009 [US1] integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "T016 [US2] contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py"
Task: "T017 [US2] metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T018 [US2] consumer summary tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "T025 [US3] unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T026 [US3] transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T027 [US3] integration and contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate User Story 1 independently using the US1 test tasks
5. Demo or review the internal wrapper before expanding to review-surface and failure-boundary refinements

### Incremental Delivery

1. Complete Setup + Foundational to prepare the `comments.delete` seams
2. Deliver User Story 1 as the working internal delete wrapper
3. Add User Story 2 to make the wrapper reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid-request, authorization, and unavailable-target failure handling
5. Finish with quickstart cleanup plus full-suite test and lint validation

### Parallel Team Strategy

With multiple developers:

1. One developer handles foundational helper/test scaffolding
2. After foundation is ready:
   - Developer A: US1 wrapper and transport implementation
   - Developer B: US2 contract and consumer-summary work after US1 lands
   - Developer C: US3 failure-boundary work after US1/US2 seams are established
3. Rejoin for polish, full-suite validation, and lint cleanup

---

## Notes

- All tasks use the required checklist format: checkbox, Task ID, optional `[P]`, required `[US#]` for story tasks, and exact file paths
- Suggested MVP scope is **User Story 1 only**
- User story tasks are organized so each story can be implemented, tested, and reviewed independently
