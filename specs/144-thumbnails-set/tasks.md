# Tasks: YT-144 Layer 1 Endpoint `thumbnails.set`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts)

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
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review the planned implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md
- [X] T002 Review the YT-144 contract, research, and data-model artifacts in /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-wrapper-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md
- [X] T003 [P] Review the existing Layer 1 wrapper, transport, consumer, and export patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T004 [P] Review the current Layer 1 metadata, transport, integration, and consumer coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration, contract-test seam, and transport recognition that all YT-144 user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add failing foundational wrapper registration and review-surface coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T006 [P] Add failing foundational transport coverage for the `POST /thumbnails/set` request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T007 [P] Add failing foundational contract-artifact coverage for thumbnail wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py
- [X] T008 [P] Add failing foundational higher-layer summary coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T009 Implement `thumbnails.set` wrapper registration, builder metadata, request-shape metadata, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T010 Implement foundational transport recognition and normalized payload parsing for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T011 Implement foundational higher-layer summary scaffolding for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T012 Refactor foundational helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Update a Video Thumbnail Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `thumbnails.set` wrapper that can update one video's thumbnail from a valid authorized `videoId`-plus-upload request through the shared executor flow and return a stable normalized update result

**Independent Test**: Submit a valid authorized `thumbnails.set` request with `videoId` and `media`, then confirm the wrapper executes through the shared executor and returns a normalized successful result containing the targeted video identity and thumbnail-update acknowledgment

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add failing happy-path wrapper tests for `thumbnails.set` metadata, required `videoId` plus `media` rules, and successful execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T014 [P] [US1] Add failing transport tests for `POST /thumbnails/set` request construction, upload-aware request serialization, and successful payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T015 [P] [US1] Add failing integration tests for valid thumbnail updates through `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T016 [US1] Implement the valid update path, required `videoId` plus upload enforcement, and successful authorized execution for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T017 [US1] Implement normalized successful thumbnail-update payload handling for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T018 [US1] Implement a higher-layer `thumbnails.set` summary method for successful outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T019 [US1] Add or update reStructuredText docstrings for the successful thumbnail-update path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US1] Refactor the successful thumbnail-update path while keeping the User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: User Story 1 should now support independently testable successful thumbnail updates

---

## Phase 4: User Story 2 - Review Quota, OAuth, and Upload Expectations Before Reuse (Priority: P2)

**Goal**: Make the `thumbnails.set` wrapper reviewable enough that maintainers can see quota, OAuth-required access, required update inputs, and unsupported upload-request guidance without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, research artifact, quickstart guidance, and higher-layer summary output to confirm quota cost `50`, OAuth-required access, required `videoId` and `media` inputs, and unsupported-request guidance are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T021 [P] [US2] Add failing contract-artifact coverage for `thumbnails.set` wrapper requirements in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py
- [X] T022 [P] [US2] Add failing review-surface metadata coverage for quota visibility, auth mode, required fields, and maintainer-facing upload notes in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T023 [P] [US2] Add failing higher-layer review-summary coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T024 [US2] Implement quota, OAuth, and update-boundary review notes for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T025 [US2] Update the higher-layer `thumbnails.set` summary to preserve reviewable quota, auth, and target-video guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US2] Align the feature-local contract and operator guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md
- [X] T027 [US2] Add or update reStructuredText docstrings for review-surface and summary changes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T028 [US2] Refactor the review-surface and summary wording while keeping the User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py

**Checkpoint**: User Story 2 should now be independently testable through metadata, contract, and consumer review surfaces

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Thumbnail Uploads Clearly (Priority: P3)

**Goal**: Distinguish malformed requests, unsupported upload shapes, missing OAuth access, target-video restrictions, and upstream thumbnail-update failures from successful update outcomes

**Independent Test**: Submit requests missing `videoId`, using unsupported upload shapes, lacking OAuth access, and receiving a target-video or upstream update failure, then confirm the outcomes remain explicitly distinct from one another and from successful thumbnail-update acknowledgments

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T029 [P] [US3] Add failing invalid-request and auth-boundary coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T030 [P] [US3] Add failing invalid-request, target-video, and upstream-update transport coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T031 [P] [US3] Add failing invalid, unauthorized, target-restricted, and upstream-rejected integration coverage for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T032 [US3] Implement deterministic validation for missing required input, unsupported fields, and malformed upload payloads in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T033 [US3] Implement normalized invalid-request, access-related failure, target-video failure, and upstream update failure handling for `thumbnails.set` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Document invalid-request, access-failure, target-video-failure, and upstream-update-failure behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md
- [X] T035 [US3] Add or update reStructuredText docstrings for the failure-path thumbnail-update logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T036 [US3] Refactor invalid, access-related, target-video, and upstream-update failure handling while keeping the User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T037 [P] Reconcile feature-level documentation and task references across /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/contracts/layer1-thumbnails-set-auth-upload-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md
- [X] T038 [P] Review all touched Python modules for reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T039 Run the YT-144 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py
- [X] T040 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server with `python3 -m pytest` and `python3 -m ruff check .`, then resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the wrapper surface introduced by User Story 1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the update surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion and has no dependency on other stories
- **User Story 2 (P2)**: Depends on the `thumbnails.set` wrapper and summary surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the `thumbnails.set` wrapper and transport surface from User Story 1 but remains independently testable through invalid-request and failure-boundary scenarios

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper metadata and validation before consumer summary updates
- Transport normalization before success or failure summaries that depend on it
- Core implementation before integration validation (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the targeted validation flow and then the full repository suite

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract and review-surface Red tests can begin while US1 implementation is underway; US3 Red tests can begin once the shared update seam exists

### Dependency Graph

- Phase 1 → Phase 2 → US1 → US2
- Phase 1 → Phase 2 → US1 → US3
- US2 and US3 → Phase 6

### Parallel Opportunities

- `T003` and `T004` can run in parallel after `T001`
- `T006`, `T007`, and `T008` can run in parallel after `T005`
- Within **US1**, `T013`, `T014`, and `T015` can run in parallel
- Within **US2**, `T021`, `T022`, and `T023` can run in parallel
- Within **US3**, `T029`, `T030`, and `T031` can run in parallel
- In the polish phase, `T037` and `T038` can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing happy-path wrapper tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request and auth-boundary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing invalid-request, target-video, and upstream-update transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid, unauthorized, target-restricted, and upstream-rejected integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported thumbnail-update success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure hardening

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, summary, and contract-test seam
2. Add User Story 1 to deliver the usable thumbnail-update path
3. Add User Story 2 to make the update contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unauthorized request handling
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests and contract assertions
   - Developer C can prepare User Story 3 Red tests for invalid and upstream-failure paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
