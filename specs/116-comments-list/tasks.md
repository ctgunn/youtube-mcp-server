# Tasks: YT-116 Layer 1 Endpoint `comments.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/contracts/`

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
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the execution targets, validation commands, and repo seams before code changes begin

- [X] T001 Review the feature implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/plan.md
- [X] T002 [P] Review the user stories and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md
- [X] T003 [P] Review the implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared `comments.list` seams and baseline Red coverage in place before story work begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing baseline metadata and export coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T005 [P] Add failing baseline request-construction coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T006 [P] Add failing baseline contract-artifact coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [X] T007 [P] Add failing baseline higher-layer summary coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T008 [P] Add failing baseline review-surface coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T009 Introduce shared `comments.list` export and summary scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Retrieve Comments Through Supported Lookup Modes (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `comments.list` wrapper that can retrieve direct comments by `id` and replies by `parentId` through the shared executor flow and return stable normalized retrieval results

**Independent Test**: Submit valid `comments.list` requests for direct-comment lookup and parent-comment reply lookup and confirm the wrapper executes through the shared executor and returns normalized successful results for matching comments

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing happy-path wrapper tests for `comments.list` metadata, required `part`, selector exclusivity, and API-key enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T011 [P] [US1] Add failing transport tests for `GET /comments` request construction and successful payload normalization for `id` and `parentId` selectors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T012 [P] [US1] Add failing integration tests for direct-comment and reply retrieval through `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T013 [US1] Implement `CommentsListWrapper` and `build_comments_list_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T014 [US1] Implement `comments.list` request building and successful retrieval normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T015 [US1] Wire `build_comments_list_wrapper` into the integration export surface in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T016 [US1] Add or update reStructuredText docstrings for changed retrieval wrapper and transport functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T017 [US1] Refactor the happy-path `comments.list` implementation while keeping User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Understand Lookup and Access Expectations Before Reuse (Priority: P2)

**Goal**: Make `comments.list` reviewable for maintainers through clear metadata, higher-layer summaries, and feature-local contract documentation

**Independent Test**: Review the wrapper surface and YT-116 contract artifacts and confirm they clearly expose quota cost, supported `id` and `parentId` lookup modes, and access expectations without reading implementation internals

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract-artifact tests for `comments.list` wrapper and lookup-access guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [X] T019 [P] [US2] Add failing metadata review-surface tests for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T020 [P] [US2] Add failing higher-layer consumer summary tests for `comments.list` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T021 [US2] Author maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/contracts/layer1-comments-list-wrapper-contract.md
- [X] T022 [US2] Author lookup and access guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/contracts/layer1-comments-list-lookup-auth-contract.md
- [X] T023 [US2] Implement maintainer-visible review notes and request-shape metadata for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T024 [US2] Implement higher-layer `comments.list` summary support in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T025 [US2] Add or update reStructuredText docstrings for changed review-surface and summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US2] Refactor contract wording and summary naming while keeping User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/contracts/layer1-comments-list-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/contracts/layer1-comments-list-lookup-auth-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Unsupported Retrieval Requests (Priority: P3)

**Goal**: Preserve distinct validation, access-mismatch, and no-match result boundaries for `comments.list`

**Independent Test**: Submit requests with missing selectors, conflicting selectors, unsupported modifiers, or incompatible access context and confirm the wrapper surfaces explicit normalized failures distinct from successful no-match retrieval outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing negative-path wrapper tests for missing selectors, conflicting selectors, unsupported fields, and access mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T028 [P] [US3] Add failing transport tests for invalid-request, auth, and empty-result `comments.list` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T029 [P] [US3] Add failing integration tests for preserved selector and access failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T030 [US3] Implement selector validation and access-enforcement boundaries for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T031 [US3] Implement normalized upstream failure mapping and empty-result handling for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T032 [US3] Document invalid-request, access-mismatch, and successful no-match retrieval behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/research.md
- [X] T033 [US3] Add or update reStructuredText docstrings for changed validation and failure-handling functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Refactor failure wording and retrieval-result consistency while keeping User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/quickstart.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and verification that affect multiple user stories

- [X] T035 [P] Tighten cross-story documentation consistency in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/research.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/quickstart.md
- [X] T036 [P] Review and normalize reStructuredText docstrings across touched integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T037 Run the YT-116 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T038 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story phases (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and defines the MVP retrieval wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the shared wrapper/export seam from Phase 2; it can proceed after US1 establishes the core retrieval path
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the working retrieval wrapper from US1; it can proceed after US2 if the review-surface wording is reused for failure guidance

### Within Each User Story

- Tests MUST be written and fail before implementation begins
- Metadata and contract checks precede behavior changes where the story is review-surface focused
- Core wrapper and transport implementation precede docstring cleanup
- ReStructuredText docstrings must be updated before story completion
- Refactor only after story tests pass
- Before marking the feature complete, run the targeted validation flow and then the full repository suite

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract/test work can begin while US1 implementation is underway; US3 Red tests can begin once the shared retrieval seam exists

---

## Parallel Examples

### Parallel Example: Foundational Phase

```text
T005 Add failing baseline request-construction coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T006 Add failing baseline contract-artifact coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T007 Add failing baseline higher-layer summary coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
T008 Add failing baseline review-surface coverage for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
```

### Parallel Example: User Story 1

```text
T010 Add failing happy-path wrapper tests for `comments.list` metadata, required `part`, selector exclusivity, and API-key enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T011 Add failing transport tests for `GET /comments` request construction and successful payload normalization for `id` and `parentId` selectors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T012 Add failing integration tests for direct-comment and reply retrieval through `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

### Parallel Example: User Story 2

```text
T018 Add failing contract-artifact tests for `comments.list` wrapper and lookup-access guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T019 Add failing metadata review-surface tests for `comments.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
T020 Add failing higher-layer consumer summary tests for `comments.list` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
```

### Parallel Example: User Story 3

```text
T027 Add failing negative-path wrapper tests for missing selectors, conflicting selectors, unsupported fields, and access mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T028 Add failing transport tests for invalid-request, auth, and empty-result `comments.list` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T029 Add failing integration tests for preserved selector and access failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate User Story 1 independently using direct-comment and reply retrieval scenarios
5. Stop for review if only the MVP wrapper path is needed

### Incremental Delivery

1. Complete Setup and Foundational phases to expose the shared `comments.list` seam
2. Deliver User Story 1 for the working retrieval wrapper and normalized success results
3. Deliver User Story 2 for maintainer-facing review surfaces and contract reuse
4. Deliver User Story 3 for invalid, access-mismatch, and no-match boundary handling
5. Finish with cross-cutting polish and full-suite verification

### Parallel Team Strategy

1. One developer completes Phase 2 shared seam work
2. After Foundation:
   - Developer A takes US1 wrapper and transport implementation
   - Developer B takes US2 contract and consumer summary work
   - Developer C prepares US3 Red tests and negative-path expectations
3. Merge back in priority order with targeted validation after each story

---

## Notes

- `[P]` tasks touch different files or can proceed independently once stated prerequisites are met
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/116-comments-list/spec.md
- Each user story remains independently testable
- The final completion gate is a passing full repository suite plus `ruff check .`
