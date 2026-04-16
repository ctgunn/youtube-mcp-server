# Tasks: YT-118 Layer 1 Endpoint `comments.update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/`

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
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the execution targets, validation commands, and repo seams before code changes begin

- [X] T001 Review the feature implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/plan.md
- [X] T002 [P] Review the user stories and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md
- [X] T003 [P] Review the implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared `comments.update` seams and baseline Red coverage in place before story work begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing baseline metadata and export coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T005 [P] Add failing baseline request-construction coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T006 [P] Add failing baseline contract-artifact coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [X] T007 [P] Add failing baseline higher-layer summary coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T008 [P] Add failing baseline review-surface coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T009 Introduce shared `comments.update` export and summary scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Update an Existing Comment Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `comments.update` wrapper that can revise an existing comment through the shared executor flow and return a stable normalized updated-comment result

**Independent Test**: Submit a valid `comments.update` request with supported `part`, a valid writable `body`, and eligible OAuth-backed access, then confirm the wrapper executes through the shared executor and returns a normalized updated comment result

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing happy-path wrapper tests for `comments.update` metadata, required `part`, required `body.id`, required `body.snippet.textOriginal`, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T011 [P] [US1] Add failing transport tests for `PUT /comments` request construction and successful payload normalization for comment updates in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T012 [P] [US1] Add failing integration tests for successful comment updates through `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T013 [US1] Implement `CommentsUpdateWrapper`, writable-field validators, and `build_comments_update_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T014 [US1] Implement `comments.update` request building and successful updated-comment normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T015 [US1] Wire `build_comments_update_wrapper` into the integration export surface in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T016 [US1] Add or update reStructuredText docstrings for changed update-wrapper, transport, and export functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T017 [US1] Refactor the happy-path `comments.update` implementation while keeping User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Understand Writable Fields and Edit Boundaries Before Reuse (Priority: P2)

**Goal**: Make `comments.update` reviewable for maintainers through clear metadata, higher-layer summaries, and feature-local contract documentation

**Independent Test**: Review the wrapper surface and YT-118 contract artifacts and confirm they clearly expose quota cost, OAuth-required behavior, writable fields, and unsupported immutable-field guidance without reading implementation internals

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract-artifact tests for `comments.update` wrapper and auth-write guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [X] T019 [P] [US2] Add failing metadata review-surface tests for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T020 [P] [US2] Add failing higher-layer consumer summary tests for `comments.update` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T021 [US2] Author maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md
- [X] T022 [US2] Author auth and write guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md
- [X] T023 [US2] Implement maintainer-visible review notes and request-shape metadata for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T024 [US2] Implement higher-layer `comments.update` summary support in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T025 [US2] Add or update reStructuredText docstrings for changed review-surface and summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US2] Refactor contract wording and summary naming while keeping User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/layer1-comments-update-auth-write-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Comment-Edit Requests (Priority: P3)

**Goal**: Preserve distinct validation, auth-mismatch, immutable-field, and normalized upstream-failure boundaries for `comments.update`

**Independent Test**: Submit requests with missing comment identifier, missing updated text, unsupported immutable-field changes, incompatible optional write context, or missing OAuth-backed access and confirm the wrapper surfaces explicit normalized failures distinct from successful updated-comment outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing negative-path wrapper tests for missing edit fields, unsupported immutable fields, and auth mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T028 [P] [US3] Add failing transport tests for invalid-request, immutable-field, auth, and upstream-failure `comments.update` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T029 [P] [US3] Add failing integration tests for preserved validation, auth, immutable-field, and upstream failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T030 [US3] Implement writable-field validation and auth-enforcement boundaries for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T031 [US3] Implement normalized upstream failure mapping and invalid-update handling for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T032 [US3] Document invalid-update, auth-mismatch, immutable-field, and normalized upstream-failure behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md
- [X] T033 [US3] Add or update reStructuredText docstrings for changed validation and failure-handling functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Refactor failure wording and update-result consistency while keeping User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and verification that affect multiple user stories

- [X] T035 [P] Tighten cross-story documentation consistency in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/research.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md
- [X] T036 [P] Review and normalize reStructuredText docstrings across touched integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T037 Run the YT-118 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T038 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story phases (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and defines the MVP update wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the shared wrapper/export seam from Phase 2; it can proceed after US1 establishes the core update path
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the working update wrapper from US1; it can proceed after US2 if the review-surface wording is reused for failure guidance

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
- **Parallelizable after Foundation**: US2 contract/test work can begin while US1 implementation is underway; US3 Red tests can begin once the shared update seam exists

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
T005 Add failing baseline request-construction coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T006 Add failing baseline contract-artifact coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T007 Add failing baseline higher-layer summary coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
T008 Add failing baseline review-surface coverage for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
```

### Parallel Example: User Story 1

```text
T010 Add failing happy-path wrapper tests for `comments.update` metadata, required `part`, required `body.id`, required `body.snippet.textOriginal`, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T011 Add failing transport tests for `PUT /comments` request construction and successful payload normalization for comment updates in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T012 Add failing integration tests for successful comment updates through `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

### Parallel Example: User Story 2

```text
T018 Add failing contract-artifact tests for `comments.update` wrapper and auth-write guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
T019 Add failing metadata review-surface tests for `comments.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
T020 Add failing higher-layer consumer summary tests for `comments.update` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
```

### Parallel Example: User Story 3

```text
T027 Add failing negative-path wrapper tests for missing edit fields, unsupported immutable fields, and auth mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T028 Add failing transport tests for invalid-request, immutable-field, auth, and upstream-failure `comments.update` outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T029 Add failing integration tests for preserved validation, auth, immutable-field, and upstream failure boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate User Story 1 independently using comment-edit scenarios
5. Stop for review if only the MVP wrapper path is needed

### Incremental Delivery

1. Complete Setup and Foundational phases to expose the shared `comments.update` seam
2. Deliver User Story 1 for the working update wrapper and normalized success results
3. Deliver User Story 2 for maintainer-facing review surfaces and contract reuse
4. Deliver User Story 3 for invalid, auth-mismatch, immutable-field, and upstream-failure boundary handling
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
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/spec.md
- Each user story remains independently testable
- The final completion gate is a passing full repository suite plus `ruff check .`
