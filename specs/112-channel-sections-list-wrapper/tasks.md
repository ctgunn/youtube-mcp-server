# Tasks: YT-112 Layer 1 Endpoint `channelSections.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/quickstart.md)

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

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/quickstart.md`
- [X] T002 [P] Review current Layer 1 seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Review existing list-wrapper coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channelSections.list` registration and baseline coverage before any story-specific work begins

**⚠️ CRITICAL**: No user story work should begin until this phase is complete

- [X] T004 Add failing baseline metadata and export tests for `channelSections.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T005 [P] Add failing baseline `GET` request-construction tests for `channelSections.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Add failing baseline review-surface contract tests for `channelSections.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- [X] T007 [P] Add failing baseline consumer review tests for channel-sections summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T008 Implement baseline `channelSections.list` builder export wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Add or update foundational reStructuredText docstrings for changed exports and shared summary helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: Foundation ready. User story implementation can begin.

---

## Phase 3: User Story 1 - Retrieve Channel Sections by Supported Filters (Priority: P1) 🎯 MVP

**Goal**: Deliver typed `channelSections.list` execution for valid selector-driven requests with normalized retrieval outcomes.

**Independent Test**: Run valid `channelSections.list` calls with supported `channelId` and `id` selectors, then verify the wrapper returns matched channel sections through the shared executor flow without raw request assembly.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T010 [P] [US1] Add failing wrapper metadata and supported selector-request tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing `channelSections.list` transport serialization tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T012 [P] [US1] Add failing shared-executor integration tests for successful `channelSections.list` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `ChannelSectionsListWrapper` and `build_channel_sections_list_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `channelSections.list` request execution and normalized list-result parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Implement channel-sections higher-layer summary behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for changed channel-sections wrapper, transport, and summary functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T017 [US1] Refactor successful retrieval-path naming and selector handling while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 should now work independently as the MVP.

---

## Phase 4: User Story 2 - Understand Filter, Auth, and Availability Expectations Before Reuse (Priority: P2)

**Goal**: Make quota cost, mixed-auth behavior, supported selectors, and lifecycle-note guidance fully reviewable through wrapper metadata and contract artifacts.

**Independent Test**: Validate contract and review-surface tests show quota cost `1`, mixed or conditional auth guidance, supported selectors, and lifecycle-note expectations without reading implementation internals.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing metadata contract tests for `channelSections.list` quota, auth, and lifecycle review fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T019 [P] [US2] Add failing channel-sections contract tests for selector guidance and review-surface wording in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
- [X] T020 [P] [US2] Add failing consumer contract tests for channel-sections review summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement mixed-auth metadata and lifecycle-ready review notes for `channelSections.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T022 [US2] Update channel-sections review summary output for auth, quota, and caveat visibility in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Update wrapper review guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md`
- [X] T024 [US2] Update auth-filter and lifecycle guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md`
- [X] T025 [US2] Add or update reStructuredText docstrings for metadata and summary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Refactor auth and caveat review surfaces while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md`

**Checkpoint**: User Stories 1 and 2 should both be independently testable.

---

## Phase 5: User Story 3 - Fail Clearly for Invalid, Unsupported, or Ineligible Retrieval Requests (Priority: P3)

**Goal**: Preserve explicit boundaries for missing selectors, conflicting selectors, unsupported retrieval modifiers, auth mismatches, and valid empty results.

**Independent Test**: Submit missing-selector, conflicting-selector, unsupported-modifier, and unauthorized `mine` requests and verify distinct normalized outcomes in unit, transport, integration, and contract tests.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add failing unit tests for missing selectors, conflicting selectors, unsupported retrieval modifiers, and `mine` auth mismatches in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing transport tests for invalid-selector and normalized failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T029 [P] [US3] Add failing integration tests for auth failure, empty-result success, and unsupported-request outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing channel-sections contract tests for invalid-combination, lifecycle-note, and empty-result rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`

### Implementation for User Story 3

- [X] T031 [US3] Implement selector-auth enforcement and unsupported-modifier validation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T032 [US3] Implement normalized invalid-request, auth-failure, and empty-result handling for `channelSections.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T033 [US3] Update channel-sections auth-filter contract for invalid-combination, empty-result, and lifecycle-note rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-auth-filter-contract.md`
- [X] T034 [US3] Add or update reStructuredText docstrings for failure-boundary changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T035 [US3] Refactor failure-boundary logic while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All three user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass, quickstart verification, and full-suite completion gate

- [X] T036 [P] Align feature artifacts for consistency in `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/quickstart.md`
- [X] T037 [P] Add cross-story regression assertions for channel-sections metadata and summaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T038 Run targeted quickstart validation commands from `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`
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
- **US3 (P3)**: Builds on the working US1 wrapper and US2 auth and caveat review surfaces

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
Task: "T010 [US1] Add failing wrapper metadata and supported selector-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T011 [US1] Add failing `channelSections.list` transport serialization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T012 [US1] Add failing shared-executor integration tests for successful `channelSections.list` requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T018 [US2] Add failing metadata contract tests for `channelSections.list` quota, auth, and lifecycle review fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T019 [US2] Add failing channel-sections contract tests for selector guidance and review-surface wording in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py"
Task: "T020 [US2] Add failing consumer contract tests for channel-sections review summaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [US3] Add failing unit tests for missing selectors, conflicting selectors, unsupported retrieval modifiers, and `mine` auth mismatches in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [US3] Add failing transport tests for invalid-selector and normalized failure handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T030 [US3] Add failing channel-sections contract tests for invalid-combination, lifecycle-note, and empty-result rules in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py"
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
3. Deliver US2 (auth, quota, and caveat reviewability)
4. Deliver US3 (failure boundaries and edge handling)
5. Run Polish and full-suite completion gate

### Parallel Team Strategy

1. One engineer handles wrapper and transport changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
2. One engineer handles contract and consumer surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
3. One engineer handles Red tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`

---

## Notes

- `[P]` tasks indicate parallel opportunities with non-overlapping dependencies
- `[US1]`, `[US2]`, `[US3]` map directly to `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/spec.md`
- Every user story includes explicit Red, Green, and Refactor work
- Full completion requires `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
