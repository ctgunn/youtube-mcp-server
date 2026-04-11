# Tasks: YT-110 Layer 1 Endpoint `channels.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/quickstart.md)

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

**Purpose**: Confirm scope and prepare task-local test and contract entry points

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/quickstart.md`
- [X] T002 [P] Review current Layer 1 seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Create channels contract test scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channels.list` baseline coverage and registration seams before story work

**⚠️ CRITICAL**: No user story work should begin until this phase is complete

- [X] T004 Add failing baseline metadata/export tests for `channels.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T005 [P] Add failing baseline transport route tests for `channels.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Add failing baseline review-surface contract tests for `channels.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
- [X] T007 [P] Add failing baseline consumer summary tests for channels review behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T008 Implement baseline `channels.list` builder export wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Add or update foundational reStructuredText docstrings for channels export and shared helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Retrieve Channels by Supported Filters (Priority: P1) 🎯 MVP

**Goal**: Deliver typed `channels.list` retrieval through supported selector modes with normalized successful outcomes.

**Independent Test**: Run selector-specific calls for `id`, `forHandle`, username-style lookup (when supported), and `mine`, then verify normalized successful retrieval outcomes in wrapper/integration tests.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T010 [P] [US1] Add failing selector success-path unit tests for `id`, `forHandle`, username-style lookup, and `mine` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing transport request-construction tests for supported selectors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T012 [P] [US1] Add failing shared-executor integration tests for successful channels retrieval in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `ChannelsListWrapper` and `build_channels_list_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `channels.list` transport request and normalized success parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Implement channels list higher-layer summary behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for changed channels retrieval functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T017 [US1] Refactor selector retrieval implementation while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 should now work independently as the MVP.

---

## Phase 4: User Story 2 - Understand Auth and Quota Expectations Before Invocation (Priority: P2)

**Goal**: Make mixed-auth and quota behavior fully reviewable through wrapper metadata and contract surfaces.

**Independent Test**: Validate contract and review-surface tests show quota cost `1`, mixed/conditional auth guidance, selector-auth mapping, and username-style support caveats without reading implementation internals.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing metadata contract tests for quota and mixed-auth review fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T019 [P] [US2] Add failing channels contract tests for selector-auth guidance and caveat language in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
- [X] T020 [P] [US2] Add failing consumer contract tests for channels review summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement mixed-auth metadata and selector-auth notes for `channels.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T022 [US2] Update review-surface summary output for channels auth/quota visibility in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Update channels wrapper contract guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/layer1-channels-list-wrapper-contract.md`
- [X] T024 [US2] Update channels auth-filter contract guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/layer1-channels-list-auth-filter-contract.md`
- [X] T025 [US2] Add or update reStructuredText docstrings for metadata and summary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Refactor auth/quota review surfaces while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/layer1-channels-list-auth-filter-contract.md`

**Checkpoint**: User Stories 1 and 2 should both be independently testable.

---

## Phase 5: User Story 3 - Receive Clear Failures for Invalid or Unsupported Retrieval Requests (Priority: P3)

**Goal**: Preserve explicit boundaries for missing selector, conflicting selector, auth mismatch, and empty-result success behavior.

**Independent Test**: Submit no-selector, multi-selector conflict, auth-mismatch, and no-match requests and verify distinct normalized outcomes in unit, transport, integration, and contract tests.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing unit tests for missing-selector and conflicting-selector validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing transport tests for auth-mismatch and normalized failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T029 [P] [US3] Add failing integration tests for auth failure and no-match success boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing channels contract tests for invalid-combination and empty-result rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

### Implementation for User Story 3

- [X] T031 [US3] Implement selector exclusivity and auth-mismatch validation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T032 [US3] Implement normalized error and no-match handling updates in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T033 [US3] Update channels auth/filter contract for invalid-combination and empty-result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/layer1-channels-list-auth-filter-contract.md`
- [X] T034 [US3] Add or update reStructuredText docstrings for failure-boundary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T035 [US3] Refactor failure-boundary logic while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass, quickstart verification, and full-suite completion gate

- [X] T036 [P] Align feature artifacts for consistency in `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/quickstart.md`
- [X] T037 [P] Add cross-story regression assertions for channels metadata and summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T038 Run targeted quickstart validation commands from `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`
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
- **US3 (P3)**: Builds on the working US1 wrapper and US2 auth/quota review surfaces

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
Task: "T010 [US1] Add failing selector success-path unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T011 [US1] Add failing transport selector tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T012 [US1] Add failing integration selector success tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T018 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T019 [US2] Add failing channels contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py"
Task: "T020 [US2] Add failing consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [US3] Add failing selector-validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [US3] Add failing transport failure-mapping tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T030 [US3] Add failing channels contract boundary tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py"
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
2. Deliver US1 (core retrieval behavior)
3. Deliver US2 (auth/quota reviewability)
4. Deliver US3 (failure boundaries and edge handling)
5. Run Polish and full-suite completion gate

### Parallel Team Strategy

1. One engineer handles wrapper/transport changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
2. One engineer handles contract and consumer surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
3. One engineer handles Red tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`

---

## Notes

- `[P]` tasks indicate parallel opportunities with non-overlapping dependencies
- `[US1]`, `[US2]`, `[US3]` map directly to `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/spec.md`
- Every user story includes explicit Red, Green, and Refactor work
- Full completion requires `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
