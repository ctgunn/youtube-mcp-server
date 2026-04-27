# Tasks: YT-130 Layer 1 Endpoint `playlistImages.update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm feature scope, source touchpoints, and validation commands before code changes begin

- [X] T001 Review the implementation flow and validation commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md
- [X] T002 Review the YT-130 decisions and entities in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/data-model.md
- [X] T003 [P] Review the wrapper, transport, consumer, and export seams in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T004 [P] Review existing playlist-image and update-oriented test coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration, transport routing, and contract-test seam that all YT-130 stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add failing foundational wrapper registration and review-surface coverage for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T006 [P] Add failing foundational transport-routing coverage for the `PUT /playlistImages` request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T007 [P] Add failing foundational playlist-image wrapper contract coverage for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py
- [X] T008 [P] Add failing foundational higher-layer summary seam coverage for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T009 Implement `playlistImages.update` wrapper registration, builder metadata, request-shape metadata, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T010 Implement foundational transport recognition and normalized update-payload parsing hooks for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T011 Implement foundational higher-layer summary scaffolding for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T012 Refactor foundational helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Update a Playlist Image Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `playlistImages.update` wrapper that can update playlist images from valid authorized identifier-plus-metadata-plus-media requests through the shared executor flow and return stable normalized update results

**Independent Test**: Submit a valid authorized `playlistImages.update` request with `part`, `body`, and `media`, then confirm the wrapper executes through the shared executor and returns a normalized successful result containing the updated playlist-image data and request context

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add failing happy-path wrapper tests for `playlistImages.update` metadata, required `part` plus `body` plus `media` rules, and successful execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T014 [P] [US1] Add failing transport tests for `PUT /playlistImages` request construction, upload-aware request serialization, and successful payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T015 [P] [US1] Add failing integration tests for valid playlist-image updates through `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T016 [US1] Implement the valid update path, required identifier-plus-metadata-plus-media enforcement, and successful authorized execution for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T017 [US1] Implement normalized successful update payload handling for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T018 [US1] Implement a higher-layer `playlistImages.update` summary method for successful outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T019 [US1] Add or update reStructuredText docstrings for the successful update path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US1] Refactor the successful update path while keeping the User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: User Story 1 should now support independently testable successful playlist-image updates

---

## Phase 4: User Story 2 - Review Update and Authorization Expectations Before Reuse (Priority: P2)

**Goal**: Make the `playlistImages.update` wrapper reviewable enough that maintainers can see quota, OAuth-required access, required update inputs, and unsupported media-request guidance without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, research artifact, quickstart guidance, and higher-layer summary output to confirm quota cost `50`, OAuth-required access, required `body` and `media` inputs, and unsupported-request guidance are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T021 [P] [US2] Add failing contract-artifact coverage for `playlistImages.update` wrapper requirements in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py
- [X] T022 [P] [US2] Add failing review-surface metadata coverage for quota visibility, auth mode, required fields, and maintainer-facing media-update notes in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T023 [P] [US2] Add failing higher-layer review-summary coverage for `playlistImages.update` source metadata, auth expectations, and update-input guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T024 [US2] Finalize maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md
- [X] T025 [US2] Finalize authorization, media-update, and invalid-shape guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md
- [X] T026 [US2] Update maintainer-visible review notes, quota metadata, required field metadata, and media-update guidance for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T027 [US2] Update higher-layer `playlistImages.update` summary fields so review consumers can see source operation, auth mode, quota, and update-input guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T028 [US2] Align the feature decisions and quickstart guidance with the review surfaces in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md
- [X] T029 [US2] Add or update reStructuredText docstrings for reviewability-oriented wrapper and summary surfaces in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T030 [US2] Refactor OAuth and media-update review wording while keeping the User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md

**Checkpoint**: User Story 2 should now be independently testable through review surfaces and contract artifacts

---

## Phase 5: User Story 3 - Reject Invalid or Unauthorized Update Requests Clearly (Priority: P3)

**Goal**: Deliver deterministic validation and distinct normalized outcomes for malformed, unauthorized, or upstream-rejected playlist-image update requests

**Independent Test**: Submit requests with missing required identifiers, missing metadata, missing media input, malformed media payloads, and missing OAuth access, then confirm the wrapper returns explicit invalid-request and access-related failures separate from authorized upstream update failures

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T031 [P] [US3] Add failing invalid-request unit coverage for missing `part`, missing `body`, missing `media`, and malformed media payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T032 [P] [US3] Add failing invalid-request, access-failure, and upstream-update-failure transport coverage for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T033 [P] [US3] Add failing invalid, unauthorized, and upstream-rejected integration coverage for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T034 [US3] Implement deterministic validation for missing required input and malformed media-update payloads in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T035 [US3] Implement normalized invalid-request, access-related failure, and upstream update failure handling for `playlistImages.update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T036 [US3] Update higher-layer `playlistImages.update` summary compatibility for invalid-request, access-failure, and upstream-update-failure expectations in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T037 [US3] Document invalid-request, access-failure, and upstream-update-failure behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md
- [X] T038 [US3] Add or update reStructuredText docstrings for the failure-path update logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T039 [US3] Refactor invalid, access-related, and upstream-update-failure handling while keeping the User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T040 [P] Reconcile feature-level documentation and task references across /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md
- [X] T041 [P] Review all touched Python modules for reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T042 Run the YT-130 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py
- [X] T043 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

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
- **User Story 2 (P2)**: Depends on the `playlistImages.update` wrapper and summary surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the `playlistImages.update` wrapper and transport surface from User Story 1 but remains independently testable through invalid-request and access-related scenarios

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper metadata and validation before consumer summary updates
- Transport normalization before success or failure summaries that depend on it
- Core implementation before integration validation (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the targeted validation flow and then the full repository suite

### Dependency Graph

- **T001-T004** → **T005-T012** → **T013-T020** → **T021-T030** → **T031-T039** → **T040-T043**
- **US1** depends on Foundational only
- **US2** depends on the completed US1 wrapper and summary review surface
- **US3** depends on the completed US1 wrapper and transport seam plus the clarified review wording from US2

### Parallel Opportunities

- `T003` and `T004` can run in parallel after `T001`
- `T006`, `T007`, and `T008` can run in parallel after `T005`
- Within **US1**, `T013`, `T014`, and `T015` can run in parallel
- Within **US2**, `T021`, `T022`, and `T023` can run in parallel
- Within **US3**, `T031`, `T032`, and `T033` can run in parallel
- In the polish phase, `T040` and `T041` can run in parallel

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract and review-surface Red tests can begin while US1 implementation is underway; US3 Red tests can begin once the shared update seam exists

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
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing invalid-request, access-failure, and upstream-update-failure transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid, unauthorized, and upstream-rejected integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported update success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure hardening

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, summary, and contract-test seam
2. Add User Story 1 to deliver the usable update path
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
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
