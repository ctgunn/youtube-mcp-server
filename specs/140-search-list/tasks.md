# Tasks: YT-140 Layer 1 Endpoint `search.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the YT-140 implementation seam, artifact scope, and test targets before code changes begin

- [X] T001 Review feature scope and independent test criteria in /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/spec.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/plan.md
- [X] T002 [P] Review search-shape, auth, and quota-caveat decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/data-model.md
- [X] T003 [P] Review wrapper and auth-refinement contract expectations in /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared `search.list` registration, execution, and review seams that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Add failing shared registration and transport coverage for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T005 Add minimal `search.list` scaffolding in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T006 Refactor shared `search.list` scaffolding and add reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: Foundation ready, `search.list` seams exist, and user story work can begin

---

## Phase 3: User Story 1 - Run a Reusable Search Query Through Layer 1 (Priority: P1) 🎯 MVP

**Goal**: Deliver a callable internal `search.list` wrapper that executes a supported search request and returns a normalized populated or empty result set

**Independent Test**: Submit a valid supported `search.list` request with `part` and `q`, then confirm the wrapper returns a normalized search result set and preserves empty-result searches as successful outcomes

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add failing wrapper success-path tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T008 [P] [US1] Add failing transport success-path tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T009 [P] [US1] Add failing integration success-path tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T010 [US1] Implement the `SearchListWrapper` class, `build_search_list_wrapper` factory, and supported request validator in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T011 [US1] Implement `search.list` request construction and normalized populated and empty result handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T012 [US1] Export the `search.list` builder and search-summary entry points in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T013 [US1] Add or update reStructuredText docstrings for the `search.list` success-path code in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T014 [US1] Refactor the `search.list` success path while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: User Story 1 is independently functional and can execute supported `search.list` requests through the internal Layer 1 wrapper

---

## Phase 4: User Story 2 - Understand Search Scope, Quota, and Refinement Options Before Reuse (Priority: P2)

**Goal**: Make quota cost, quota caveat, conditional-auth expectations, and supported refinement boundaries reviewable without reading transport internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output and confirm they expose quota cost `100`, the quota caveat, required `part` and `q`, supported refinements, and restricted-auth guidance for `search.list`

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add failing metadata review-surface tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T016 [P] [US2] Add failing consumer-summary tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T017 [P] [US2] Add failing feature-contract review tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py

### Implementation for User Story 2

- [X] T018 [US2] Implement `search.list` review-surface metadata, quota caveat, and refinement notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T019 [US2] Implement the higher-layer `search.list` summary output in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US2] Create or update `search.list` contract verification in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py
- [X] T021 [US2] Update /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-wrapper-contract.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md to match the implemented review surface and search guidance
- [X] T022 [US2] Add or update reStructuredText docstrings for review-surface and summary changes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T023 [US2] Refactor review-surface and summary wording while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py green

**Checkpoint**: User Story 2 is independently testable through metadata, contract, and consumer review surfaces

---

## Phase 5: User Story 3 - Distinguish Invalid, Unsupported, and Restricted Search Requests Clearly (Priority: P3)

**Goal**: Distinguish malformed requests, incompatible refinements, restricted-auth failures, and upstream search failures from successful populated and empty search outcomes

**Independent Test**: Submit requests missing `part` or `q`, using incompatible search refinements, lacking stronger authorization for restricted filters, and receiving an upstream failure, then confirm the outcomes remain explicitly distinct from one another and from successful populated and empty search results

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add failing invalid-request and auth-boundary tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T025 [P] [US3] Add failing transport error-normalization tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T026 [P] [US3] Add failing integration failure-boundary tests for `search.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T027 [US3] Implement `search.list` request validation for required inputs, incompatible refinement combinations, and restricted-filter auth boundaries in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T028 [US3] Implement `search.list` failure-category handling and failure-path payload fallbacks in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T029 [US3] Update failure-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/layer1-search-list-auth-refinement-contract.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md
- [X] T030 [US3] Add or update reStructuredText docstrings for `search.list` validation and failure-path logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T031 [US3] Refactor `search.list` failure handling while keeping /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py green

**Checkpoint**: All user stories are independently functional and their failure boundaries are reviewable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation-aligned validation and full-suite proof

- [X] T032 [P] Run quickstart validation steps from /Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/quickstart.md
- [X] T033 [P] Review touched reStructuredText docstrings across /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T034 Run the full repository test suite and resolve any failing tests with `python3 -m pytest` and `python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2 and is the MVP slice
- **User Story 2 (P2)**: Starts after Phase 2 and depends on the US1 wrapper path existing, but remains independently testable through review surfaces
- **User Story 3 (P3)**: Starts after Phase 2 and depends on the US1 execution path existing, but remains independently testable through explicit failure-boundary scenarios

### Within Each User Story

- Red tests MUST be written and fail before implementation
- Wrapper and transport behavior before consumer or contract-surface refinement
- Core implementation before refactor
- ReStructuredText docstrings before closing the story
- Full repository validation before the feature is complete

### Story Completion Order

1. Phase 1 Setup
2. Phase 2 Foundational
3. User Story 1 (MVP)
4. User Story 2
5. User Story 3
6. Phase 6 Polish

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests for User Story 1 together:
Task: "T007 Add failing wrapper success-path tests in tests/unit/test_layer1_foundation.py"
Task: "T008 Add failing transport success-path tests in tests/unit/test_youtube_transport.py"
Task: "T009 Add failing integration success-path tests in tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch the review-surface Red tests for User Story 2 together:
Task: "T015 Add failing metadata review-surface tests in tests/contract/test_layer1_metadata_contract.py"
Task: "T016 Add failing consumer-summary tests in tests/contract/test_layer1_consumer_contract.py"
Task: "T017 Add failing feature-contract review tests in tests/contract/test_layer1_search_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch the failure-boundary Red tests for User Story 3 together:
Task: "T024 Add failing invalid-request and auth-boundary tests in tests/unit/test_layer1_foundation.py"
Task: "T025 Add failing transport error-normalization tests in tests/unit/test_youtube_transport.py"
Task: "T026 Add failing integration failure-boundary tests in tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup
2. Complete Phase 2 Foundational
3. Complete Phase 3 User Story 1
4. Stop and validate the internal `search.list` success path independently

### Incremental Delivery

1. Complete Setup and Foundational work to expose the shared `search.list` seam
2. Deliver User Story 1 for the callable search wrapper
3. Deliver User Story 2 for reviewable quota, caveat, auth, and refinement guidance
4. Deliver User Story 3 for explicit invalid-request, restricted-auth, and upstream-failure boundaries
5. Finish with quickstart validation and full-suite proof

### Parallel Team Strategy

1. One engineer completes Setup and Foundational work
2. After Phase 2:
   - Engineer A can drive US1 success-path implementation
   - Engineer B can prepare US2 contract and consumer Red tests
   - Engineer C can prepare US3 failure-boundary Red tests
3. Merge story work in priority order with full-suite validation at the end

---

## Notes

- All task lines use the required checklist format
- `[P]` tasks are limited to work that can proceed in parallel without incomplete-task dependencies
- User story labels appear only on user story phase tasks
- Each user story remains independently testable based on the criteria listed above
