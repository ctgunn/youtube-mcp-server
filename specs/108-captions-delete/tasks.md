# Tasks: YT-108 Layer 1 Endpoint `captions.delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- This feature uses the existing Python service layout under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

## Phase 1: Setup (Shared Context)

**Purpose**: Load the feature context and align the implementation scope before code changes begin

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md`
- [X] T002 [P] Review the existing caption integration seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared `captions.delete` seams and baseline Red tests in place before story work begins

**⚠️ CRITICAL**: No user story work should begin until this phase is complete

- [X] T003 Add failing baseline metadata and export coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T004 [P] Add failing baseline request-construction coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T005 [P] Add failing baseline contract-artifact coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`
- [X] T006 [P] Add failing baseline higher-layer summary coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T007 Introduce shared `captions.delete` export and higher-layer summary scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T008 Add or update reStructuredText docstrings for foundational Python changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Remove an Owned Caption Track (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 caption-delete wrapper that can delete a known caption track through the existing shared executor flow and surface a stable delete outcome.

**Independent Test**: Invoke the new wrapper with authorized access and a valid caption track identifier, then verify that the deletion completes successfully and the wrapper or higher-layer summary surfaces a normalized delete result.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T009 [P] [US1] Add failing `id`-required and OAuth-required unit tests for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T010 [P] [US1] Add failing happy-path executor integration coverage for successful caption deletion in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing transport coverage for `DELETE` caption requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement `CaptionsDeleteWrapper` and `build_captions_delete_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T013 [US1] Implement `captions.delete` request building and successful delete-result parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T014 [US1] Implement higher-layer caption-delete summarization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T015 [US1] Update the integration export surface for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for changed `captions.delete` Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T017 [US1] Refactor the happy-path `captions.delete` flow while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 1 should now work independently as the MVP.

---

## Phase 4: User Story 2 - Use Delegated Content-Owner Access Correctly (Priority: P2)

**Goal**: Extend the wrapper contract and execution path so callers can supply supported content-owner delegation context without guessing when it is accepted or how it is surfaced.

**Independent Test**: Invoke the wrapper with a valid caption track identifier plus `onBehalfOfContentOwner`, then verify that the request contract accepts the delegated path, the request builder preserves the delegation input, and the contract artifacts explain the delegation rules.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing unit coverage for optional `onBehalfOfContentOwner` delegation validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T019 [P] [US2] Add failing transport coverage for `onBehalfOfContentOwner` propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T020 [P] [US2] Add failing delegated-delete integration coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement optional `onBehalfOfContentOwner` handling for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T022 [US2] Extend higher-layer caption-delete summaries with delegation metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Document delegated ownership rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md`
- [X] T024 [US2] Add or update reStructuredText docstrings for delegated deletion handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T025 [US2] Refactor delegated delete handling while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Stories 1 and 2 should both be independently testable.

---

## Phase 5: User Story 3 - Fail Clearly When Deletion Is Not Allowed (Priority: P3)

**Goal**: Make permission, ownership, and missing-target behavior reviewable and enforceable so downstream caption-management work can distinguish why deletion failed.

**Independent Test**: Invoke the wrapper with missing authorization, unsupported or ownership-blocked delegated access, and normalized upstream failures, then verify that access-denied and not-found outcomes remain distinct and that contract artifacts explain the failure rules.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing authorization and failure-boundary unit coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T027 [P] [US3] Add failing normalized-failure integration coverage for `captions.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing permission, ownership, and failure-boundary contract coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 3

- [X] T029 [US3] Implement ownership-sensitive auth notes and distinct normalized failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T030 [US3] Update permission, ownership, and failure-boundary documentation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/contracts/layer1-captions-delete-auth-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md`
- [X] T031 [US3] Add or update reStructuredText docstrings for permission and failure-boundary handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T032 [US3] Refactor permission and failure-boundary logic while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tighten cross-story coverage, validate the documented workflow, and complete full-suite verification

- [X] T033 [P] Tighten cross-story `captions.delete` documentation consistency in `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md`
- [X] T034 [P] Add or refresh cross-story regression assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T035 Run the quickstart validation flow from `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T036 Run `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any remaining failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately
- **Foundational (Phase 2)**: Depends on Setup and blocks all story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and delivers the MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 because it extends the same wrapper and request-builder path with delegation handling
- **User Story 3 (Phase 5)**: Depends on User Story 1 and User Story 2 because it extends the same wrapper and summary path with ownership and failure-boundary behavior
- **Polish (Phase 6)**: Depends on all desired stories being complete

### User Story Dependencies

- **US1 (P1)**: No user-story dependency after Phase 2
- **US2 (P2)**: Builds on the working `captions.delete` happy path from US1
- **US3 (P3)**: Builds on the working `captions.delete` happy path from US1 and the delegated path from US2

### Within Each User Story

- Write tests first and confirm they fail before implementation
- Implement the minimum code needed to satisfy the failing tests
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after the story tests pass
- Re-run the affected targeted suites before moving forward
- Do not consider the feature complete until the full repository test suite and lint checks pass

### Dependency Graph

- **T001-T002** → **T003-T008** → **T009-T017** → **T018-T025** → **T026-T032** → **T033-T036**
- **US1** depends on Foundational only
- **US2** depends on Foundational and the completed US1 delete path
- **US3** depends on US1 and US2

### Parallel Opportunities

- **Setup**: T002 can run alongside T001
- **Foundational**: T004, T005, and T006 can run in parallel after T003
- **US1**: T009, T010, and T011 can run in parallel
- **US2**: T018, T019, and T020 can run in parallel
- **US3**: T026, T027, and T028 can run in parallel
- **Polish**: T033 and T034 can run in parallel before the final validation tasks

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests for US1 together:
Task: "T009 Add failing id-required and OAuth-required unit tests for captions.delete in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T010 Add failing happy-path executor integration coverage for successful caption deletion in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T011 Add failing transport coverage for DELETE caption requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch the Red tests for US2 together:
Task: "T018 Add failing unit coverage for optional onBehalfOfContentOwner delegation validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T019 Add failing transport coverage for onBehalfOfContentOwner propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T020 Add failing delegated-delete integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Launch the Red tests for US3 together:
Task: "T026 Add failing authorization and failure-boundary unit coverage for captions.delete in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T027 Add failing normalized-failure integration coverage for captions.delete in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T028 Add failing permission, ownership, and failure-boundary contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate US1 independently with the targeted unit, integration, contract, and transport suites

### Incremental Delivery

1. Finish Setup and Foundational work to expose the shared `captions.delete` seams
2. Deliver US1 as the first reusable delete-wrapper increment
3. Add US2 to support delegated content-owner deletion without breaking US1
4. Add US3 to harden ownership, permission, and failure-boundary behavior
5. Run Polish tasks to validate the documented workflow and full-suite health

### Parallel Team Strategy

1. One teammate can handle Foundational Red tests while another prepares the foundational export and summary scaffolding
2. Within each story, Red tests marked `[P]` can be developed in parallel
3. Cross-story work should converge back to one branch owner before changing `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, or `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

---

## Notes

- `[P]` tasks are safe parallel opportunities because they touch different files or can be prepared independently before merge
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md`
- Every story includes explicit Red, Green, and Refactor work
- Full completion requires the final `python3 -m pytest` and `ruff check .` run from `/Users/ctgunn/Projects/youtube-mcp-server`
