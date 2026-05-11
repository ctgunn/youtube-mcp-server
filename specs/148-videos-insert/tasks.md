# Tasks: YT-148 Layer 1 Endpoint `videos.insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/quickstart.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/`

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
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review the planned implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/quickstart.md
- [X] T002 Review the YT-148 contract, research, and data-model artifacts in /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-wrapper-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-auth-upload-contract.md
- [X] T003 [P] Review the existing Layer 1 wrapper, transport, consumer, and export patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T004 [P] Review the current Layer 1 metadata, transport, integration, and consumer coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration, contract-test seam, and transport recognition that all YT-148 user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add failing foundational wrapper registration and review-surface coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T006 [P] Add failing foundational transport coverage for the `POST /videos` request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T007 [P] Add failing foundational contract-artifact coverage for video-create wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py
- [X] T008 [P] Add failing foundational higher-layer summary coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T009 Implement `VideosInsertWrapper`, the builder, upload validators, request-shape metadata, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T010 Implement foundational transport recognition and normalized payload parsing for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T011 Implement foundational higher-layer summary scaffolding for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T012 Refactor foundational helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Video Through a Reusable Internal Upload Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `videos.insert` wrapper that can create one video from a valid authorized metadata-plus-upload request through the shared executor flow and return a stable normalized created-video result

**Independent Test**: Submit a valid authorized `videos.insert` request with `part`, `body`, and `media`, plus one valid resumable-mode request if that mode is supported, then confirm the wrapper executes through the shared executor and returns a normalized successful result containing created-video identity and upload-mode context

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add failing happy-path wrapper tests for valid standard-upload and supported resumable-upload create requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T014 [P] [US1] Add failing transport tests for authorized `POST /videos` request construction and successful created-video payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T015 [P] [US1] Add failing integration tests for end-to-end `videos.insert` creation through the shared executor in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T016 [US1] Implement metadata-plus-upload request validation and supported upload-mode selection for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T017 [US1] Implement `POST /videos` request building and successful create-result normalization for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T018 [US1] Implement created-video higher-layer summary behavior for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T019 [US1] Add or update reStructuredText docstrings for the `videos.insert` wrapper, transport, and consumer summary functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US1] Refactor `videos.insert` create-path naming and helper reuse while keeping User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Review High-Cost Upload Rules Before Reuse (Priority: P2)

**Goal**: Make the `videos.insert` wrapper reviewable for quota visibility, OAuth-only behavior, supported upload modes, and audit/private-default caveats before downstream reuse

**Independent Test**: Review the maintainer-facing wrapper metadata, feature-local contracts, and higher-layer summary output for `videos.insert`, then confirm they clearly expose the 1600-unit quota cost, required access mode, supported upload modes, and audit/private-default caveat without reading transport implementation

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T021 [P] [US2] Add failing contract-artifact coverage for `videos.insert` wrapper identity, quota visibility, upload-mode guidance, and audit/private-default caveat visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py
- [X] T022 [P] [US2] Add failing review-surface metadata coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T023 [P] [US2] Add failing higher-layer review-summary coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T024 [US2] Update maintainer-facing `videos.insert` metadata notes, quota visibility, upload-mode review fields, and audit/private-default caveat visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T025 [US2] Update the `videos.insert` higher-layer summary surface to preserve source operation, auth mode, quota cost, upload guidance, and caveat visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T026 [US2] Align the feature-local review artifacts with implemented `videos.insert` metadata behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-wrapper-contract.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/layer1-videos-insert-auth-upload-contract.md
- [X] T027 [US2] Add or update reStructuredText docstrings for changed review-surface and summary functions tied to `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T028 [US2] Refactor duplicated quota, upload, and caveat wording while keeping User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/contracts/

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Reject Unsupported Upload Requests Clearly (Priority: P3)

**Goal**: Preserve clear boundaries between invalid request shapes, missing OAuth-compatible access, policy-related upstream refusals, and successful caveat-sensitive video creation outcomes

**Independent Test**: Submit `videos.insert` requests with missing `part`, missing `body`, missing `media`, unsupported upload-mode combinations, and incompatible auth context, then confirm the system returns distinct normalized outcomes separate from successful created-video results

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T029 [P] [US3] Add failing invalid-request and auth-boundary unit coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T030 [P] [US3] Add failing invalid-request, unauthorized, resumable-boundary, and policy-related transport coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T031 [P] [US3] Add failing invalid, unauthorized, and policy-sensitive integration coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T032 [US3] Tighten invalid-shape, unsupported-upload-mode, and OAuth-only enforcement for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T033 [US3] Implement distinct normalized failure mapping for `videos.insert` invalid-request, access-related, and policy-related upstream outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T034 [US3] Update `videos.insert` higher-layer summary handling so caveat-sensitive success stays distinct from invalid and unauthorized outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T035 [US3] Add or update reStructuredText docstrings for changed `videos.insert` validation and failure-handling functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T036 [US3] Refactor invalid-request and failure-boundary helper names while keeping User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, artifact alignment, and full-suite readiness across all user stories

- [X] T037 [P] Reconcile the YT-148 implementation with the executable guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/quickstart.md and update any stale feature-local planning artifacts under /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/
- [X] T038 [P] Add any remaining cross-story regression coverage for `videos.insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T039 Review all touched Python modules for required reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T040 Run the YT-148 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T041 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server with `python3 -m pytest` and `python3 -m ruff check .`, then resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the wrapper and summary surface introduced by User Story 1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the create-path surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion and has no dependency on other stories
- **User Story 2 (P2)**: Depends on the `videos.insert` wrapper and summary surface from User Story 1 but remains independently testable through review artifacts and metadata summaries
- **User Story 3 (P3)**: Depends on the `videos.insert` wrapper and transport surface from User Story 1 but remains independently testable through invalid-request, unauthorized, and policy-boundary scenarios

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
- **Parallelizable after Foundation**: US2 contract and review-surface Red tests can begin while US1 implementation is underway; US3 Red tests can begin once the shared create seam exists

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
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request and auth-boundary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing invalid-request, unauthorized, resumable-boundary, and policy-related transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid, unauthorized, and policy-sensitive integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported video-creation success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure hardening

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, summary, and contract-test seam
2. Add User Story 1 to deliver the usable video-create path
3. Add User Story 2 to make the create contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unauthorized request handling plus policy-boundary clarity
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests and contract assertions
   - Developer C can prepare User Story 3 Red tests for invalid, unauthorized, and policy-boundary paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/148-videos-insert/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
