# Tasks: YT-107 Layer 1 Endpoint `captions.download`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- This feature uses the existing Python service layout under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

## Phase 1: Setup (Shared Context)

**Purpose**: Load the feature context and confirm the exact modules and tests that this slice will change

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/quickstart.md`
- [X] T002 Review the existing caption integration seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put the shared captions.download seams and baseline Red tests in place before story work begins

**⚠️ CRITICAL**: No user story work should begin until this phase is complete

- [X] T003 Add failing baseline metadata and export coverage for `captions.download` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T004 [P] Add failing baseline request-construction coverage for `captions.download` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T005 [P] Add failing baseline contract-artifact coverage for `captions.download` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`
- [X] T006 [P] Add failing baseline higher-layer summary coverage for `captions.download` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T007 Introduce shared `captions.download` export and higher-layer summary scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T008 Add or update reStructuredText docstrings for foundational Python changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Download a Known Caption Track (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 caption-download wrapper that can retrieve caption content for a known caption track through the existing shared executor flow.

**Independent Test**: Invoke the new wrapper with authorized access and a valid caption track identifier, then verify that downloaded caption content and wrapper metadata are returned through the Layer 1 and higher-layer summary surfaces.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T009 [P] [US1] Add failing `id`-required and OAuth-required unit tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T010 [P] [US1] Add failing happy-path executor integration coverage for downloaded caption content in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement `CaptionsDownloadWrapper` and `build_captions_download_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T012 [US1] Implement `captions.download` request building and successful download-result parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T013 [US1] Implement higher-layer caption-download summarization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T014 [US1] Update the integration export surface for `captions.download` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T015 [US1] Add or update reStructuredText docstrings for changed `captions.download` Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T016 [US1] Refactor the happy-path `captions.download` flow while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 1 should now work independently as the MVP.

---

## Phase 4: User Story 2 - Request a Specific Output Variant (Priority: P2)

**Goal**: Extend the wrapper contract and execution path so callers can request supported translation and format-conversion variants without guessing the request shape.

**Independent Test**: Invoke the wrapper with a valid caption track identifier plus `tfmt` or `tlang`, then verify that the request contract accepts the option, the request builder preserves it, and the higher-layer summary exposes the option context.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T017 [P] [US2] Add failing unit coverage for optional `tfmt` and `tlang` validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T018 [P] [US2] Add failing transport coverage for `tfmt` and `tlang` propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement optional `tfmt` and `tlang` handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T020 [US2] Extend higher-layer caption-download summaries with output-variant metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T021 [US2] Document format-conversion and translation rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-access-format-contract.md`
- [X] T022 [US2] Add or update reStructuredText docstrings for output-option handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Refactor `tfmt` and `tlang` handling while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Stories 1 and 2 should both be independently testable.

---

## Phase 5: User Story 3 - Understand Access Restrictions Early (Priority: P3)

**Goal**: Make permission-sensitive, delegated, and failure-boundary behavior reviewable and enforceable so downstream transcript work can distinguish access problems from missing captions.

**Independent Test**: Invoke the wrapper with missing authorization, delegated access context, and normalized upstream failures, then verify that access-denied and not-found outcomes remain distinct and that contract artifacts explain the permission and delegation rules.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add failing authorization and failure-boundary unit coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T025 [P] [US3] Add failing delegation and normalized-failure integration coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T026 [US3] Add failing permission, delegation, and failure-boundary contract coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 3

- [X] T027 [US3] Implement permission-sensitive auth, delegation notes, and distinct normalized failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T028 [US3] Update permission, delegation, and failure-boundary documentation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/contracts/layer1-captions-download-access-format-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/quickstart.md`
- [X] T029 [US3] Add or update reStructuredText docstrings for permission and failure-boundary handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T030 [US3] Refactor permission and failure-boundary logic while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tighten cross-story coverage, validate the documented workflow, and complete full-suite verification

- [X] T031 [P] Tighten cross-story `captions.download` documentation consistency in `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/quickstart.md`
- [X] T032 [P] Add or refresh cross-story regression assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T033 Run the quickstart validation flow from `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T034 Run `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any remaining failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately
- **Foundational (Phase 2)**: Depends on Setup and blocks all story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and delivers the MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 because it extends the same wrapper and request-builder path with option handling
- **User Story 3 (Phase 5)**: Depends on User Story 1 because it extends the same wrapper and summary path with permission and failure-boundary behavior
- **Polish (Phase 6)**: Depends on all desired stories being complete

### User Story Dependencies

- **US1 (P1)**: No user-story dependency after Phase 2
- **US2 (P2)**: Builds on the working `captions.download` happy path from US1
- **US3 (P3)**: Builds on the working `captions.download` happy path from US1

### Within Each User Story

- Write tests first and confirm they fail before implementation
- Implement the minimum code needed to satisfy the failing tests
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after the story tests pass
- Re-run the affected targeted suites before moving forward
- Do not consider the feature complete until the full repository test suite and lint checks pass

### Story Completion Order

- **MVP order**: Setup → Foundational → US1
- **Full delivery order**: Setup → Foundational → US1 → US2 → US3 → Polish
- **Parallel note**: US2 and US3 both depend on US1 and both touch `wrappers.py`, `youtube.py`, and `consumer.py`, so they are safest to execute sequentially on a single branch

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests for US1 together:
Task: "T009 Add failing id-required and OAuth-required unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T010 Add failing happy-path executor integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch the Red tests for US2 together:
Task: "T017 Add failing unit coverage for optional tfmt and tlang validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T018 Add failing transport coverage for tfmt and tlang propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 3

```bash
# Launch the Red tests for US3 together:
Task: "T024 Add failing authorization and failure-boundary unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T025 Add failing delegation and normalized-failure integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate US1 independently with the targeted unit, integration, contract, and transport suites

### Incremental Delivery

1. Finish Setup and Foundational work to expose the shared `captions.download` seams
2. Deliver US1 as the first reusable wrapper increment
3. Add US2 to support output variants without breaking US1
4. Add US3 to harden permission, delegation, and failure-boundary behavior
5. Run Polish tasks to validate the documented workflow and full-suite health

### Parallel Team Strategy

1. One teammate can handle Foundational Red tests while another prepares the foundational export and summary scaffolding
2. Within each story, unit and integration Red tests marked `[P]` can be developed in parallel
3. Cross-story work should converge back to one branch owner before changing `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, or `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

---

## Notes

- `[P]` tasks are safe parallel opportunities because they touch different files or can be prepared independently before merge
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/spec.md`
- Every story includes explicit Red, Green, and Refactor work
- Full completion requires the final `python3 -m pytest` and `ruff check .` run from `/Users/ctgunn/Projects/youtube-mcp-server`
