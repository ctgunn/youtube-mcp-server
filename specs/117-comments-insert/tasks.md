# Tasks: YT-117 Layer 1 Endpoint `comments.insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python changes must include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g. `US1`, `US2`, `US3`)
- Every task includes an exact file path

## Path Conventions

- Single project layout rooted at `/Users/ctgunn/Projects/youtube-mcp-server`
- Source code under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the execution targets, validation commands, and repo seams before code changes begin

- [ ] T001 Review the feature implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/plan.md
- [ ] T002 [P] Review the user stories and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md
- [ ] T003 [P] Review the implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared `comments.insert` seams and baseline Red coverage in place before story work begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add failing baseline metadata and export coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [ ] T005 [P] Add failing baseline request-construction coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [ ] T006 [P] Add failing baseline contract-artifact coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [ ] T007 [P] Add failing baseline higher-layer summary coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [ ] T008 [P] Add failing baseline review-surface coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [ ] T009 Introduce shared `comments.insert` export and summary scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create a Reply Comment Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `comments.insert` wrapper that can create a reply comment through the shared executor flow and return a stable normalized created-comment result

**Independent Test**: Submit a valid `comments.insert` reply-create request with supported `part`, a valid reply `body`, and eligible OAuth-backed access, then confirm the wrapper executes through the shared executor and returns a normalized created reply result

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Add failing happy-path wrapper tests for `comments.insert` metadata, required `part`, required `body`, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [ ] T011 [P] [US1] Add failing transport tests for `POST /comments` request construction and successful payload normalization for reply creation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [ ] T012 [P] [US1] Add failing integration tests for successful reply creation through `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [ ] T013 [US1] Implement `CommentsInsertWrapper`, reply-body validators, and `build_comments_insert_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [ ] T014 [US1] Implement `comments.insert` request building and successful created-comment normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [ ] T015 [US1] Wire `build_comments_insert_wrapper` into the integration export surface in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [ ] T016 [US1] Add or update reStructuredText docstrings for changed create-wrapper, transport, and export functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [ ] T017 [US1] Refactor the happy-path `comments.insert` implementation while keeping User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Understand Reply-Creation and Access Expectations Before Reuse (Priority: P2)

**Goal**: Make `comments.insert` reviewable for maintainers through clear metadata, higher-layer summaries, and feature-local contract documentation

**Independent Test**: Review the wrapper surface and YT-117 contract artifacts and confirm they clearly expose quota cost, OAuth-required behavior, reply-only create rules, and optional delegation guidance without reading implementation internals

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T018 [P] [US2] Add failing contract-artifact tests for `comments.insert` wrapper and auth-write guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [ ] T019 [P] [US2] Add failing metadata review-surface tests for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [ ] T020 [P] [US2] Add failing higher-layer consumer summary tests for `comments.insert` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [ ] T021 [US2] Author maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-wrapper-contract.md
- [ ] T022 [US2] Author auth and write guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-auth-write-contract.md
- [ ] T023 [US2] Implement maintainer-visible review notes and request-shape metadata for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [ ] T024 [US2] Implement higher-layer `comments.insert` summary support in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [ ] T025 [US2] Add or update reStructuredText docstrings for changed review-surface and summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [ ] T026 [US2] Refactor contract wording and summary naming while keeping User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/layer1-comments-insert-auth-write-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Reply Requests (Priority: P3)

**Goal**: Preserve distinct validation, auth-mismatch, and normalized upstream-failure boundaries for `comments.insert`

**Independent Test**: Submit requests with missing parent-comment reference, missing reply text, unsupported create shapes, incompatible optional write context, or missing OAuth-backed access and confirm the wrapper surfaces explicit normalized failures distinct from successful created-comment outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T027 [P] [US3] Add failing negative-path wrapper tests for missing reply fields, unsupported create fields, and auth mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [ ] T028 [P] [US3] Add failing transport tests for invalid-request, auth, and upstream-failure `comments.insert` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [ ] T029 [P] [US3] Add failing integration tests for preserved validation, auth, and upstream failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [ ] T030 [US3] Implement reply-body validation and auth-enforcement boundaries for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [ ] T031 [US3] Implement normalized upstream failure mapping and invalid-create handling for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [ ] T032 [US3] Document invalid-create, auth-mismatch, and normalized upstream-failure behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md
- [ ] T033 [US3] Add or update reStructuredText docstrings for changed validation and failure-handling functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [ ] T034 [US3] Refactor failure wording and create-result consistency while keeping User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/quickstart.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and verification that affect multiple user stories

- [ ] T035 [P] Tighten cross-story documentation consistency in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/research.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/quickstart.md
- [ ] T036 [P] Review and normalize reStructuredText docstrings across touched integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [ ] T037 Run the YT-117 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [ ] T038 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story phases (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and defines the MVP create wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the shared wrapper/export seam from Phase 2; it can proceed after US1 establishes the core create path
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the working create wrapper from US1; it can proceed after US2 if the review-surface wording is reused for failure guidance

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
- **Parallelizable after Foundation**: US2 contract/test work can begin while US1 implementation is underway; US3 Red tests can begin once the shared create seam exists

### Dependency Graph

- **T001-T003** → **T004-T009** → **T010-T017** → **T018-T026** → **T027-T034** → **T035-T038**
- **US1** depends on Foundational only
- **US2** depends on Foundational + US1
- **US3** depends on Foundational + US1 + US2

### Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001
- **Foundational**: T005, T006, T007, and T008 can run in parallel after T004
- **US1**: T010, T011, and T012 can run in parallel
- **US2**: T018, T019, and T020 can run in parallel
- **US3**: T027, T028, and T029 can run in parallel
- **Polish**: T035 and T036 can run in parallel before execution tasks T037-T038

---

## Parallel Examples

### Parallel Example: Foundational Phase

```text
T005 Add failing baseline request-construction coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T006 Add failing baseline contract-artifact coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T007 Add failing baseline higher-layer summary coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
T008 Add failing baseline review-surface coverage for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
```

### Parallel Example: User Story 1

```text
T010 Add failing happy-path wrapper tests for `comments.insert` metadata, required `part`, required `body`, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T011 Add failing transport tests for `POST /comments` request construction and successful payload normalization for reply creation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T012 Add failing integration tests for successful reply creation through `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

### Parallel Example: User Story 2

```text
T018 Add failing contract-artifact tests for `comments.insert` wrapper and auth-write guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T019 Add failing metadata review-surface tests for `comments.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
T020 Add failing higher-layer consumer summary tests for `comments.insert` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
```

### Parallel Example: User Story 3

```text
T027 Add failing negative-path wrapper tests for missing reply fields, unsupported create fields, and auth mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T028 Add failing transport tests for invalid-request, auth, and upstream-failure `comments.insert` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T029 Add failing integration tests for preserved validation, auth, and upstream failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate User Story 1 independently using reply-create scenarios
5. Stop for review if only the MVP wrapper path is needed

### Incremental Delivery

1. Complete Setup and Foundational phases to expose the shared `comments.insert` seam
2. Deliver User Story 1 for the working create wrapper and normalized success results
3. Deliver User Story 2 for maintainer-facing review surfaces and contract reuse
4. Deliver User Story 3 for invalid, auth-mismatch, and upstream-failure boundary handling
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
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/spec.md
- Each user story remains independently testable
- The final completion gate is a passing full repository suite plus `ruff check .`
