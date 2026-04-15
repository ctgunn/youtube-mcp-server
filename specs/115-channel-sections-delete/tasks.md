# Tasks: YT-115 Layer 1 Endpoint `channelSections.delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/`

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
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the execution targets, validation commands, and repo seams before code changes begin

- [X] T001 Review the feature implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/plan.md
- [X] T002 [P] Review the user stories and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md
- [X] T003 [P] Review the implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared `channelSections.delete` seams and baseline Red coverage in place before story work begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing baseline metadata and export coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T005 [P] Add failing baseline request-construction coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T006 [P] Add failing baseline contract-artifact coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py
- [X] T007 [P] Add failing baseline higher-layer summary coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T008 [P] Add failing baseline review-surface coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T009 Introduce shared `channelSections.delete` export and summary scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Delete a Channel Section Through a Typed Wrapper (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `channelSections.delete` wrapper that can delete a known channel section through the shared executor flow and return a stable normalized delete outcome

**Independent Test**: Submit a valid authorized `channelSections.delete` request for an existing section and confirm the wrapper executes through the shared executor and returns a normalized successful deletion result

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing happy-path wrapper tests for `channelSections.delete` metadata, required `id`, optional delegation, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T011 [P] [US1] Add failing transport tests for `DELETE` request construction and successful delete payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T012 [P] [US1] Add failing integration tests for authorized and delegated `channelSections.delete` execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T013 [US1] Implement `ChannelSectionsDeleteWrapper` and `build_channel_sections_delete_wrapper()` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T014 [US1] Implement `channelSections.delete` request building and successful delete-result normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T015 [US1] Wire `build_channel_sections_delete_wrapper` into the integration export surface in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T016 [US1] Add or update reStructuredText docstrings for changed delete wrapper and transport functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T017 [US1] Refactor the happy-path `channelSections.delete` implementation while keeping User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Understand OAuth Expectations Before Reuse (Priority: P2)

**Goal**: Make `channelSections.delete` reviewable for maintainers through clear metadata, higher-layer summaries, and feature-local contract documentation

**Independent Test**: Review the wrapper surface and YT-115 contract artifacts and confirm they clearly expose quota cost, OAuth-required access, delete preconditions, and optional delegation context without reading implementation internals

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract-artifact tests for `channelSections.delete` wrapper and auth-delete guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py
- [X] T019 [P] [US2] Add failing metadata review-surface tests for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T020 [P] [US2] Add failing higher-layer consumer summary tests for `channelSections.delete` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T021 [US2] Author maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-wrapper-contract.md
- [X] T022 [US2] Author OAuth and delete-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md
- [X] T023 [US2] Implement maintainer-visible review notes and request-shape metadata for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T024 [US2] Implement higher-layer `channelSections.delete` summary support in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T025 [US2] Add or update reStructuredText docstrings for changed review-surface and summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US2] Refactor contract wording and summary naming while keeping User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/contracts/layer1-channel-sections-delete-auth-delete-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Delete Requests (Priority: P3)

**Goal**: Preserve distinct validation, authorization, and target-state failure boundaries for `channelSections.delete`

**Independent Test**: Submit requests with missing authorization, malformed delete targets, unsupported fields, or unavailable sections and confirm the wrapper surfaces explicit normalized failures distinct from successful delete outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing negative-path wrapper tests for invalid identifiers, unsupported fields, and OAuth mismatch handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T028 [P] [US3] Add failing transport tests for auth, not-found, and unavailable-target `channelSections.delete` failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T029 [P] [US3] Add failing integration tests for preserved auth and target-state failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T030 [US3] Implement delete-request validation and OAuth enforcement boundaries for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T031 [US3] Implement normalized upstream failure mapping and target-state delete handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T032 [US3] Document invalid-request, auth, and target-state delete behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md
- [X] T033 [US3] Add or update reStructuredText docstrings for changed validation and failure-handling functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Refactor failure wording and delete-result consistency while keeping User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/quickstart.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and verification that affect multiple user stories

- [X] T035 [P] Tighten cross-story documentation consistency in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/research.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/quickstart.md
- [X] T036 [P] Review and normalize reStructuredText docstrings across touched integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T037 Run the YT-115 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T038 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story phases (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and defines the MVP delete wrapper
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the shared wrapper/export seam from Phase 2; it can proceed after US1 establishes the core wrapper path
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the working delete wrapper from US1; it can proceed after US2 if the review-surface wording is reused for failure guidance

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
- **Parallelizable after Foundation**: US2 contract/test work can begin while US1 implementation is underway; US3 Red tests can begin once the shared delete seam exists

---

## Parallel Examples

### Parallel Example: Foundational Phase

```text
T005 Add failing baseline request-construction coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T006 Add failing baseline contract-artifact coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py
T007 Add failing baseline higher-layer summary coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
T008 Add failing baseline review-surface coverage for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
```

### Parallel Example: User Story 1

```text
T010 Add failing happy-path wrapper tests for `channelSections.delete` metadata, required `id`, optional delegation, and OAuth enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T011 Add failing transport tests for `DELETE` request construction and successful delete payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T012 Add failing integration tests for authorized and delegated `channelSections.delete` execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

### Parallel Example: User Story 2

```text
T018 Add failing contract-artifact tests for `channelSections.delete` wrapper and auth-delete guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py
T019 Add failing metadata review-surface tests for `channelSections.delete` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
T020 Add failing higher-layer consumer summary tests for `channelSections.delete` reuse guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
```

### Parallel Example: User Story 3

```text
T027 Add failing negative-path wrapper tests for invalid identifiers, unsupported fields, and OAuth mismatch handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
T028 Add failing transport tests for auth, not-found, and unavailable-target `channelSections.delete` failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
T029 Add failing integration tests for preserved auth and target-state failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate User Story 1 independently using the authorized delete scenario
5. Stop for review if only the MVP wrapper path is needed

### Incremental Delivery

1. Complete Setup and Foundational phases to expose the shared `channelSections.delete` seam
2. Deliver User Story 1 for the working delete wrapper and normalized success result
3. Deliver User Story 2 for maintainer-facing review surfaces and contract reuse
4. Deliver User Story 3 for invalid and ineligible delete boundary handling
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
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md
- Each user story remains independently testable
- The final completion gate is a passing full repository suite plus `ruff check .`
