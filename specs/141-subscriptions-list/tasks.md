# Tasks: YT-141 Layer 1 Endpoint `subscriptions.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (for example `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths in this task list follow the single-project structure captured in [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md)

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm the implementation seams, contract artifacts, and test surfaces before changing code

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md` to align scope
- [X] T002 Inspect the existing mixed-auth list-wrapper patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Inspect the relevant test seams in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared failing coverage and endpoint scaffolding that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing metadata and export coverage for `subscriptions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T005 [P] Add failing transport dispatch coverage for `subscriptions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Add failing feature-contract scaffold coverage for `subscriptions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- [X] T007 Implement the shared `subscriptions.list` builder, export, and transport dispatch scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T008 Add or update reStructuredText docstrings for foundational `subscriptions.list` scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T009 Refactor foundational `subscriptions.list` scaffolding while keeping foundational tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Retrieve Subscription Lists Through a Stable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Expose a typed internal `subscriptions.list` wrapper that supports successful public-compatible and OAuth-backed retrieval without raw upstream request assembly

**Independent Test**: Submit valid `subscriptions.list` requests using representative public-compatible and OAuth-backed selector modes and verify the wrapper returns normalized successful results with stable selector and continuation context for each supported lookup mode

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing unit tests for successful `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers` wrapper flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing integration tests for successful public-compatible and OAuth-backed `subscriptions.list` retrieval in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T012 [P] [US1] Add failing transport tests for `subscriptions.list` query construction and selector-context preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement the `SubscriptionsListWrapper` class, request shape, selector resolution, and success-path wrapper execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `subscriptions.list` response normalization with selector and continuation context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Export the finished `subscriptions.list` builder and related integration surface in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for successful retrieval behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T017 [US1] Refactor `subscriptions.list` success-path implementation while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 should now be independently functional and demoable as the MVP

---

## Phase 4: User Story 2 - Understand Filter Modes, Quota, and OAuth Boundaries Before Reuse (Priority: P2)

**Goal**: Make quota, selector modes, paging and ordering rules, and selector-aware OAuth expectations reviewable through wrapper metadata, feature contracts, and higher-layer summary surfaces

**Independent Test**: Review the wrapper contract and metadata surfaces and confirm they expose quota cost `1`, supported selector modes, collection-versus-direct lookup rules, and public-compatible versus OAuth-backed access expectations without reading implementation details

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing metadata contract tests for quota, conditional-auth notes, selector exclusivity, and paging or ordering guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T019 [P] [US2] Add failing feature-contract assertions for wrapper and filter-modes documentation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- [X] T020 [P] [US2] Add failing consumer summary contract tests for `selectorUsed`, `sourceOperation`, `sourceAuthMode`, `sourceAuthConditionNote`, and `sourceQuotaCost` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T021 [US2] Update `subscriptions.list` metadata notes, auth-condition guidance, and selector review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T022 [US2] Implement maintainer-facing subscription summary fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T023 [US2] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md` with the implemented review surfaces
- [X] T024 [US2] Add or update reStructuredText docstrings for review-surface behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T025 [US2] Refactor `subscriptions.list` review-surface wording while keeping US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Stories 1 and 2 should both work independently, with US2 proving the wrapper is reviewable for reuse

---

## Phase 5: User Story 3 - Distinguish Invalid, Unsupported, and Under-Authorized Requests Clearly (Priority: P3)

**Goal**: Preserve distinct invalid-request, access-related, upstream-failure, and successful empty-result behavior for missing selectors, conflicting selectors, unsupported paging or ordering, and incompatible auth usage

**Independent Test**: Submit requests with missing selectors, conflicting selectors, unsupported paging or ordering, and incompatible auth modes and verify the wrapper returns distinct normalized outcomes from successful empty retrievals and normalized upstream failures

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing unit tests for missing selectors, conflicting selectors, unsupported paging or ordering, and incompatible auth mode in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T027 [P] [US3] Add failing integration tests for `invalid_request` versus access-related failure versus empty-result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing transport and feature-contract tests for invalid filter combinations, unsupported paging, and failure-boundary guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`

### Implementation for User Story 3

- [X] T029 [US3] Implement selector-specific validation, paging and ordering guards, and incompatible auth failures for `subscriptions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T030 [US3] Implement normalized empty-result and failure-boundary handling for `subscriptions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T031 [US3] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-filter-modes-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md` with the final validation and failure-boundary behavior
- [X] T032 [US3] Add or update reStructuredText docstrings for validation and failure-path behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T033 [US3] Refactor `subscriptions.list` validation and failure wording while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, quickstart alignment, and full validation

- [X] T034 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/contracts/layer1-subscriptions-list-wrapper-contract.md` for final consistency with the implemented wrapper
- [X] T035 [P] Run the quickstart validation steps and update any stale commands or file references in `/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/quickstart.md`
- [X] T036 Review reStructuredText docstrings across touched Python modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T037 Run the targeted `subscriptions.list` validation suite in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T038 Run the full repository test suite and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`
- [X] T039 Run final lint validation for touched integration modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational completion and delivers the MVP
- **User Story 2 (P2)**: Starts after Foundational completion and depends on the `subscriptions.list` wrapper surface introduced by US1
- **User Story 3 (P3)**: Starts after Foundational completion and depends on the basic retrieval path introduced by US1

### Within Each User Story

- Red tests MUST be written and fail before implementation
- Wrapper validation and transport behavior come before higher-layer summary refinement
- reStructuredText docstrings MUST be updated before the story is complete
- Refactor only after story tests pass
- Before feature completion, run the full repository test suite and fix any failures

### Story Completion Order

- Foundational coverage → US1 → US2 and US3 → Polish
- **Suggested MVP scope**: Complete through US1 before taking on US2 or US3

### Dependency Graph

- Phase 1 → Phase 2 → US1 → US2
- Phase 1 → Phase 2 → US1 → US3
- US2 and US3 → Phase 6

### Parallel Opportunities

- T003 can run in parallel with T001-T002 during Setup
- T005 and T006 can run in parallel during Foundational Red work
- T010, T011, and T012 can run in parallel for US1 Red work
- T018, T019, and T020 can run in parallel for US2 Red work
- T026, T027, and T028 can run in parallel for US3 Red work
- T034 and T035 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "T010 Add failing unit tests for successful channelId, id, mine, myRecentSubscribers, and mySubscribers wrapper flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T011 Add failing integration tests for successful public-compatible and OAuth-backed subscriptions.list retrieval in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T012 Add failing transport tests for subscriptions.list query construction and selector-context preservation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "T018 Add failing metadata contract tests for quota, conditional-auth notes, selector exclusivity, and paging or ordering guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T019 Add failing feature-contract assertions for wrapper and filter-modes documentation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py"
Task: "T020 Add failing consumer summary contract tests for selectorUsed, sourceOperation, sourceAuthMode, sourceAuthConditionNote, and sourceQuotaCost in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "T026 Add failing unit tests for missing selectors, conflicting selectors, unsupported paging or ordering, and incompatible auth mode in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T027 Add failing integration tests for invalid_request versus access-related failure versus empty-result boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T028 Add failing transport and feature-contract tests for invalid filter combinations, unsupported paging, and failure-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported public-compatible and OAuth-backed retrieval flows independently

### Incremental Delivery

1. Finish Setup and Foundational coverage
2. Deliver US1 as the first usable internal wrapper increment
3. Add US2 review-surface completeness
4. Add US3 failure-boundary hardening
5. Finish with targeted and full-suite validation

### Parallel Team Strategy

1. One contributor handles failing coverage in Phase 2 while another prepares wrapper and transport implementation notes from the design docs
2. After US1 lands, US2 and US3 can proceed in parallel because one focuses on review surfaces and the other on failure-boundary handling
3. Rejoin for Phase 6 full-suite validation and final documentation alignment

---

## Notes

- All tasks follow the required checklist format with task ID, optional `[P]`, optional story label, and exact file paths
- `[P]` tasks are limited to work that can proceed on different files or independent test surfaces
- Each user story is independently testable per [/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/141-subscriptions-list/spec.md)
- Completion requires both targeted validation and a passing full repository test-suite run
