# Tasks: YT-156 Layer 1 Resource-Family Module Reorganization

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code changes require reStructuredText docstrings for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature-level test and package scaffolding without moving endpoint behavior yet.

- [X] T001 [P] Add YT-156 contract artifact coverage for `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-resource-family-compatibility-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-response-normalizer-dispatch-contract.md` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py`
- [X] T002 [P] Create the resource-family package skeleton with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/__init__.py`
- [X] T003 [P] Add a resource-family inventory fixture listing the required YT-156 families in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T004 Run `python3 -m pytest tests/contract/test_layer1_resource_modules_contract.py tests/unit/test_layer1_resource_modules.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and record the expected Red failures for missing resource-family behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared registry seams that all resource-family moves depend on.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T005 Add failing tests for a resource-family wrapper registry and family lookup behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T006 Add failing tests for explicit response-normalizer registration with context-only, payload-only, and context-plus-payload handlers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T007 Implement the shared resource-family wrapper registry helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/__init__.py`
- [X] T008 Implement the shared response-normalizer dispatch helper without changing transport results in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T009 Add reStructuredText docstrings for new or changed registry and dispatch functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T010 Run `python3 -m pytest tests/unit/test_layer1_resource_modules.py tests/unit/test_youtube_transport.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix foundational failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: Foundation ready - resource-family implementation can begin.

---

## Phase 3: User Story 1 - Find Resource-Family Integration Code (Priority: P1) MVP

**Goal**: Maintainers can find Layer 1 wrappers, metadata, validators, and normalizers by resource family without broad-file traversal.

**Independent Test**: Select representative families and confirm their builder functions, wrapper classes, metadata, validators, and normalizer ownership are discoverable from resource-family modules while shared foundations remain centralized.

### Tests for User Story 1 (REQUIRED)

> Write these tests FIRST and confirm they fail or characterize the missing seam before implementation.

- [X] T011 [P] [US1] Add tests proving representative list-only and mixed-auth families expose wrapper builders from resource modules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T012 [US1] Add tests proving upload, mutation, delete, and OAuth-only families expose wrapper builders from resource modules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T013 [P] [US1] Add contract checks that every required family in the YT-156 contract has a resource module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py`
- [X] T014 [P] [US1] Add transport tests proving representative normalizer ownership is discoverable by family in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 1

- [X] T015 [US1] Move activities, guide categories, localization, members, memberships levels, video categories, and video abuse report reasons wrapper classes and builders into `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/members.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_categories.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_abuse_report_reasons.py`
- [X] T016 [US1] Move captions, channel banners, thumbnails, and watermarks wrapper classes, builders, constants, and validators into `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/thumbnails.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`
- [X] T017 [US1] Move channels and channel sections wrapper classes, builders, constants, and validators into `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`
- [X] T018 [US1] Move comments and comment threads wrapper classes, builders, constants, and validators into `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`
- [X] T019 [US1] Move playlist images, playlist items, playlists, search, subscriptions, and videos wrapper classes, builders, constants, and validators into `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`
- [X] T020 [US1] Register all resource-family builder exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/__init__.py`
- [X] T021 [US1] Move endpoint-specific response normalizers for representative families into their resource modules and register ownership in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T022 [US1] Add or preserve reStructuredText docstrings for every moved or changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`
- [X] T023 [US1] Refactor broad resource-owned definitions out of `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` while leaving compatibility imports for moved families
- [X] T024 [US1] Run `python3 -m pytest tests/unit/test_layer1_resource_modules.py tests/contract/test_layer1_resource_modules_contract.py tests/unit/test_youtube_transport.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US1 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`

**Checkpoint**: User Story 1 is independently testable as the MVP.

---

## Phase 4: User Story 2 - Compose Stable Layer 1 Capabilities (Priority: P2)

**Goal**: Future Layer 2 and Layer 3 authors can use resource-family access while existing callers keep using compatibility imports.

**Independent Test**: Import representative Layer 1 capabilities through `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and resource-family modules, then confirm each path exposes equivalent review surfaces and callable wrappers.

### Tests for User Story 2 (REQUIRED)

- [X] T025 [P] [US2] Add compatibility import tests for `mcp_server.integrations` package-level exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T026 [P] [US2] Add compatibility import tests for `mcp_server.integrations.wrappers` facade exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T027 [US2] Add resource-family access tests comparing old and new builder review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py`
- [X] T028 [P] [US2] Add consumer-summary regression tests proving representative higher-layer composition still reaches the same wrapper metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T029 [US2] Update package-level compatibility exports to re-export resource-family builders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T030 [US2] Update the `wrappers.py` compatibility facade to import and expose moved wrapper classes and builder functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T031 [US2] Update the `youtube.py` compatibility surface so existing YouTube transport and request-building imports remain stable in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T032 [US2] Update representative higher-layer imports only where needed to avoid circular imports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T033 [US2] Add or preserve reStructuredText docstrings for changed compatibility and consumer functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T034 [US2] Refactor export lists and imports to avoid circular imports while preserving compatibility in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T035 [US2] Run `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_layer1_resource_modules.py tests/contract/test_layer1_consumer_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US2 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Verify Behavior Preservation (Priority: P3)

**Goal**: Reviewers can verify the reorganization preserved the completed Layer 1 endpoint contracts and did not introduce new endpoint behavior.

**Independent Test**: Compare pre-refactor and post-refactor behavior through existing contract, unit, integration, and transport tests for endpoint metadata, validation, credentials, quota, response shape, and normalized failures.

### Tests for User Story 3 (REQUIRED)

- [X] T036 [P] [US3] Add response-dispatch equivalence tests for no-content, upload, download, list, update, delete, rating, reporting, search, and localization operations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T037 [P] [US3] Add full-inventory resource-family contract checks for YT-103 through YT-155 endpoint capabilities in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py`
- [X] T038 [P] [US3] Add integration checks proving representative wrappers still execute through the shared executor and reject invalid shapes before execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T039 [P] [US3] Add metadata regression checks proving quota, auth mode, selectors, optional fields, and caveat notes are unchanged in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`

### Implementation for User Story 3

- [X] T040 [US3] Replace the long operation-key response-normalization branch with explicit dispatch while preserving generic fallback parsing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T041 [US3] Register all remaining endpoint-specific response normalizers by resource family in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`
- [X] T042 [US3] Preserve upstream request construction, credential attachment, retry, observability, and normalized error behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T043 [US3] Add or preserve reStructuredText docstrings for all changed normalizer and dispatch functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`
- [X] T044 [US3] Refactor duplicate transitional normalizer paths while keeping all targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T045 [US3] Run `python3 -m pytest tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US3 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

**Checkpoint**: All user stories are independently functional and contract-preserving.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation alignment, and complete repository validation.

- [X] T046 [P] Update feature quickstart verification notes with final focused commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/quickstart.md`
- [X] T047 [P] Update feature contracts if implementation preserves compatibility through different facade wording than planned in `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-resource-family-compatibility-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/contracts/layer1-response-normalizer-dispatch-contract.md`
- [X] T048 [P] Review all changed Python files for reStructuredText docstrings on every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`
- [X] T049 Run focused Layer 1 verification `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_layer1_resource_modules.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`
- [X] T050 Run full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/` or `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T051 Run lint validation `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any issues before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/` or `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T052 Confirm no public MCP tool or hosted transport behavior changed by reviewing `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and documenting any unexpected diff before completion in `/Users/ctgunn/Projects/youtube-mcp-server/specs/156-layer1-resource-modules/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and provides the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run alongside US1 only if ownership avoids the same files, but safest sequence is after US1 resource modules exist
- **User Story 3 (Phase 5)**: Depends on Foundational completion; safest sequence is after US1 resource modules exist because dispatch ownership depends on family modules
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP. Can start after Foundational. No dependency on US2 or US3.
- **User Story 2 (P2)**: Can start after Foundational, but depends on at least the resource-family modules created by US1 for meaningful new access-path comparison.
- **User Story 3 (P3)**: Can start after Foundational, but depends on resource-family modules from US1 for family-owned normalizer registration.

### Within Each User Story

- Red tests must be written and must fail or characterize missing seams before Green implementation.
- Resource-family modules and registries must exist before compatibility facades point at them.
- Compatibility imports must pass before deleting broad-file transitional definitions.
- Response-normalizer dispatch must pass targeted transport tests before broad conditional paths are removed.
- Docstring tasks must complete before each story checkpoint.
- Refactor tasks must keep focused tests green before moving to the next story.

### Parallel Opportunities

- T001, T002, and T003 can run in parallel during setup because they touch separate files.
- T011, T013, and T014 can run in parallel for US1; T012 shares `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_resource_modules.py` with T011 and should coordinate.
- T015 through T019 can be split by resource-family ownership if each worker owns distinct files under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`.
- T025 and T028 can run in parallel for US2 because they touch separate test files; T026 and T027 share one file and should coordinate.
- T036 through T039 can run in parallel for US3 because they touch separate test files.
- T046, T047, and T048 can run in parallel during polish because they touch docs and code review separately.

---

## Parallel Example: User Story 1

```bash
Task: "T013 [US1] Add contract checks that every required family in the YT-156 contract has a resource module in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py"
Task: "T014 [US1] Add transport tests proving representative normalizer ownership is discoverable by family in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T015 [US1] Move small list-only resource families into /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/"
Task: "T016 [US1] Move upload and watermark resource families into /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/"
```

## Parallel Example: User Story 2

```bash
Task: "T025 [US2] Add compatibility import tests for package-level exports in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [US2] Add consumer-summary regression tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T036 [US3] Add response-dispatch equivalence tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T037 [US3] Add full-inventory contract checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py"
Task: "T038 [US3] Add shared executor integration checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T039 [US3] Add metadata regression checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational registry and dispatch seams.
3. Complete Phase 3 User Story 1.
4. Stop and validate US1 independently with `python3 -m pytest tests/unit/test_layer1_resource_modules.py tests/contract/test_layer1_resource_modules_contract.py tests/unit/test_youtube_transport.py`.

### Incremental Delivery

1. Add resource-family modules and discoverability first.
2. Add compatibility and composition checks without changing endpoint behavior.
3. Add response-normalizer dispatch and full behavior-preservation evidence.
4. Finish with focused Layer 1 verification, full `python3 -m pytest`, and `python3 -m ruff check .`.

### Parallel Team Strategy

1. Complete setup and foundational registry tasks together.
2. Split resource-family moves by file ownership under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/`.
3. Assign compatibility facade work to one owner for `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`.
4. Assign response-normalizer dispatch work to one owner for `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`.

---

## Summary

- Total tasks: 52
- Setup tasks: 4
- Foundational tasks: 6
- User Story 1 tasks: 14
- User Story 2 tasks: 11
- User Story 3 tasks: 10
- Polish tasks: 7
- MVP scope: Phase 1 + Phase 2 + User Story 1
- Final required validation: `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
