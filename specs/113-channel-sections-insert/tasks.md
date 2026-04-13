# Tasks: YT-113 Layer 1 Endpoint `channelSections.insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md)

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

**Purpose**: Confirm scope, implementation seams, and verification entry points before code changes begin

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md`
- [X] T002 [P] Review current Layer 1 seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Review existing channel-sections and write-wrapper coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channelSections.insert` registration and baseline coverage before any story-specific work begins

**⚠️ CRITICAL**: No user story work should begin until this phase is complete

- [X] T004 Add failing baseline metadata and export tests for `channelSections.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T005 [P] Add failing baseline `POST` request-construction tests for `channelSections.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Add failing baseline review-surface contract tests for `channelSections.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- [X] T007 [P] Add failing baseline consumer review tests for channel-section create summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T008 Implement baseline `channelSections.insert` builder export wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Add or update foundational reStructuredText docstrings for changed exports and shared summary helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Create a Channel Section Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver typed `channelSections.insert` execution for valid authorized requests with normalized created-section outcomes.

**Independent Test**: Run one authorized `channelSections.insert` call with a supported `part`, a valid section type, and aligned `body`, then verify the wrapper returns the created channel section through the shared executor flow without raw request assembly.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T010 [P] [US1] Add failing wrapper metadata and supported create-request tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing `channelSections.insert` transport serialization tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T012 [P] [US1] Add failing shared-executor integration tests for successful `channelSections.insert` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `ChannelSectionsInsertWrapper`, section-type validators, and `build_channel_sections_insert_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `channelSections.insert` request execution and created-section result parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Implement channel-section create higher-layer summary behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for changed create-wrapper, transport, and summary functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T017 [US1] Refactor successful create-path naming and request-shape handling while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 should now work independently as the MVP.

---

## Phase 4: User Story 2 - Understand Write Preconditions Before Reuse (Priority: P2)

**Goal**: Make quota cost, OAuth-required behavior, section-type boundaries, title rules, and delegation guidance fully reviewable through wrapper metadata and contract artifacts.

**Independent Test**: Validate contract and review-surface tests show quota cost `50`, OAuth-required guidance, supported section-type rules, title requirements, and optional delegation inputs without reading implementation internals.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing metadata contract tests for `channelSections.insert` quota and auth review fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T019 [P] [US2] Add failing channel-sections contract tests for section-type guidance and review-surface wording in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- [X] T020 [P] [US2] Add failing consumer contract tests for channel-section create review summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement OAuth-required metadata, title guidance, and delegation review notes for `channelSections.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T022 [US2] Update channel-section create review summary output for auth, quota, and delegation visibility in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Update wrapper review guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-wrapper-contract.md`
- [X] T024 [US2] Update auth-write and section-type guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`
- [X] T025 [US2] Add or update reStructuredText docstrings for metadata and summary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Refactor auth and section-content review surfaces while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`

**Checkpoint**: User Stories 1 and 2 should both be independently testable.

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Create Requests (Priority: P3)

**Goal**: Preserve explicit boundaries for missing authorization, incomplete create bodies, unsupported content combinations, duplicate items, invalid delegation context, and normalized upstream create failures.

**Independent Test**: Submit unauthorized, incomplete-body, unsupported-type, duplicate-item, missing-title, and invalid-delegation requests and verify distinct normalized outcomes in unit, transport, integration, and contract tests.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing unit tests for missing authorization, incomplete create bodies, duplicate items, and invalid section-type combinations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing transport tests for invalid-create and normalized failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T029 [P] [US3] Add failing integration tests for auth failure, invalid delegation context, and normalized upstream create-failure outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing channel-sections contract tests for invalid-create, duplicate-item, title-required, and upstream-boundary rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

### Implementation for User Story 3

- [X] T031 [US3] Implement section-type alignment, duplicate-item rejection, title-required validation, and auth-enforcement behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T032 [US3] Implement normalized invalid-create and upstream create-failure handling for `channelSections.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T033 [US3] Update channel-sections auth-write contract for invalid-create, duplicate-item, title-required, and upstream-boundary rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`
- [X] T034 [US3] Add or update reStructuredText docstrings for failure-boundary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T035 [US3] Refactor failure-boundary logic while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass, quickstart verification, and full-suite completion gate

- [X] T036 [P] Align feature artifacts for consistency in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md`
- [X] T037 [P] Add cross-story regression assertions for channel-section create metadata and summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T038 Run targeted quickstart validation commands from `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- [X] T039 Run full-suite completion gate `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately
- **Foundational (Phase 2)**: Depends on Setup and blocks all story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and delivers MVP behavior
- **User Story 2 (Phase 4)**: Depends on US1 behavior and shared foundational seams
- **User Story 3 (Phase 5)**: Depends on US1 and US2 behavior on shared wrapper paths
- **Polish (Phase 6)**: Depends on all stories being complete

### User Story Dependencies

- **US1 (P1)**: No user-story dependency after Phase 2
- **US2 (P2)**: Builds on the working US1 wrapper and review surfaces
- **US3 (P3)**: Builds on the working US1 wrapper and US2 auth and content review surfaces

### Within Each User Story

- Red tests must be written first and fail before implementation
- Green implementation must be minimal and target failing tests only
- ReStructuredText docstrings must be updated for all changed Python functions before story completion
- Refactor work runs only after Green tests pass
- Story-targeted tests rerun before advancing
- Final completion requires full repository suite and lint checks

### Dependency Graph

- **T001-T003** → **T004-T009** → **T010-T017** → **T018-T026** → **T027-T035** → **T036-T039**
- **US1** depends on Foundational only
- **US2** depends on Foundational + US1
- **US3** depends on Foundational + US1 + US2

### Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001
- **Foundational**: T005, T006, and T007 can run in parallel after T004
- **US1**: T010, T011, and T012 can run in parallel
- **US2**: T018, T019, and T020 can run in parallel
- **US3**: T027, T028, T029, and T030 can run in parallel
- **Polish**: T036 and T037 can run in parallel before execution tasks T038-T039

---

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] Add failing wrapper metadata and supported create-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T011 [US1] Add failing `channelSections.insert` transport serialization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T012 [US1] Add failing shared-executor integration tests for successful `channelSections.insert` requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T018 [US2] Add failing metadata contract tests for `channelSections.insert` quota and auth review fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T019 [US2] Add failing channel-sections contract tests for section-type guidance and review-surface wording in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py"
Task: "T020 [US2] Add failing consumer contract tests for channel-section create review summaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [US3] Add failing unit tests for missing authorization, incomplete create bodies, duplicate items, and invalid section-type combinations in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [US3] Add failing transport tests for invalid-create and normalized failure handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T030 [US3] Add failing channel-sections contract tests for invalid-create, duplicate-item, title-required, and upstream-boundary rules in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. Validate US1 independently via unit, transport, and integration tests
4. Demo or merge MVP increment

### Incremental Delivery

1. Complete Setup + Foundational
2. Deliver US1 (core create behavior)
3. Deliver US2 (auth, quota, section-type, and delegation reviewability)
4. Deliver US3 (failure boundaries and edge handling)
5. Run Polish and full-suite completion gate

### Parallel Team Strategy

1. One engineer handles wrapper and transport changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
2. One engineer handles contract and consumer surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
3. One engineer handles Red tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`

---

## Notes

- `[P]` tasks indicate parallel opportunities with non-overlapping dependencies
- `[US1]`, `[US2]`, `[US3]` map directly to `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/spec.md`
- Every user story includes explicit Red, Green, and Refactor work
- Full completion requires `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
