# Tasks: Layer 2 Tool `playlistImages_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/data-model.md), [contracts/playlistImages_update.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/contracts/playlistImages_update.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/quickstart.md)

**Tests**: Test tasks are mandatory and ordered Red before Green for every story. Completion requires a passing full repository `pytest` run and `ruff check .` after final code changes. Every new or changed Python function must have a reStructuredText docstring before its story is complete.

**Organization**: Tasks are grouped by user story so `playlistImages_update` can be implemented as an MVP first, then expanded with discovery/examples and validation/error coverage.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to a user story from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/plan.md`
- [X] T002 Inspect existing playlist-images Layer 2 list and insert patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T003 [P] Inspect existing Layer 1 `playlistImages.update` wrapper behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`
- [X] T004 [P] Inspect existing playlist-images test coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared test scaffolding and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until these tasks are complete.

- [X] T005 Add Red scaffold/export expectations for future `PLAYLIST_IMAGES_UPDATE_*` public symbols in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 Add Red default catalog and dispatcher registration expectations for `playlistImages_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T007 Add shared fake update wrapper and executor helpers for playlist-image update tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`
- [X] T008 Add reStructuredText docstrings to new fake update wrapper and executor helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`
- [X] T009 Run the foundational Red checks with `pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Update Playlist Images Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `playlistImages_update` with OAuth-backed access, required `part`, target-identifying `body`, and required `media`, then receive a near-raw updated playlist-image result.

**Independent Test**: Invoke the handler or dispatcher with a valid playlist-image update request and confirm the result includes `endpoint`, quota cost `50`, requested parts, safe body context, safe media context, OAuth mode, and returned playlist-image fields.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add contract tests for `playlistImages_update` identity, input schema, quota cost `50`, OAuth mode, and mutation result contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py`
- [X] T011 [P] [US1] Add unit tests for valid argument normalization, target identity context, safe media summaries, successful wrapper invocation, and near-raw result mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`
- [X] T012 [P] [US1] Add integration tests for default registry discovery and dispatcher invocation of `playlistImages_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py`
- [X] T013 [US1] Run the US1 Red tests and confirm they fail for missing `playlistImages_update` behavior from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T014 [US1] Import `build_playlist_images_update_wrapper` for Layer 2 use in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T015 [US1] Add `PLAYLIST_IMAGES_UPDATE_TOOL_NAME`, `PLAYLIST_IMAGES_UPDATE_QUOTA_COST`, supported parts, and `PLAYLIST_IMAGES_UPDATE_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T016 [US1] Add `PlaylistImagesUpdateToolError` with sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T017 [US1] Implement `validate_playlist_images_update_arguments()` with required `part`, target-identifying `body`, and `media` normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T018 [US1] Implement safe update body and media context helpers that preserve `body.id` and omit raw upload content in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T019 [US1] Implement `map_playlist_images_update_result()` preserving returned playlist-image fields and operation context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T020 [US1] Implement `_default_playlist_images_update_executor()` with deterministic safe updated-resource data in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T021 [US1] Implement `_playlist_images_update_auth_context()` and `build_playlist_images_update_handler()` using `build_playlist_images_update_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T022 [US1] Implement `build_playlist_images_update_contract()` and `build_playlist_images_update_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T023 [US1] Export `playlistImages_update` constants, validators, mappers, builders, descriptor, and error symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T024 [US1] Register `build_playlist_images_update_tool_descriptor()` in the default tool catalog in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T025 [US1] Add or update reStructuredText docstrings for every new or modified `playlistImages_update` function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T026 [US1] Refactor `playlistImages_update` helper names and result mapping for consistency with `playlistImages_list` and `playlistImages_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T027 [US1] Run US1 focused tests with `pytest tests/contract/test_youtube_playlist_images_contract.py tests/unit/test_youtube_playlist_images.py tests/integration/test_youtube_playlist_images_registration.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and is the suggested MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, Update Semantics, and Upload Requirements Before Calling (Priority: P2)

**Goal**: A client developer can inspect `playlistImages_update` and understand endpoint identity, quota cost, OAuth requirement, required `part`, required target metadata body, required media upload, examples, and out-of-scope boundaries before invocation.

**Independent Test**: Review tool metadata, description, usage notes, caveats, and examples from discovery output and confirm they expose quota cost `50`, OAuth-required access, required body/media inputs, update semantics, target identity, and unsupported workflows.

### Tests for User Story 2 (Red)

- [X] T028 [P] [US2] Add contract tests for discovery metadata, usage notes, caveats, quota visibility, OAuth visibility, target identity visibility, upload visibility, and response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py`
- [X] T029 [P] [US2] Add catalog tests that compare representative `playlistImages_update` examples with the concrete descriptor metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T030 [P] [US2] Add integration tests proving default registry metadata preserves `playlistImages_update` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T031 [US2] Run the US2 Red tests and confirm metadata/example checks fail before implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T032 [US2] Add `PLAYLIST_IMAGES_UPDATE_DESCRIPTION`, `PLAYLIST_IMAGES_UPDATE_USAGE_NOTES`, and `PLAYLIST_IMAGES_UPDATE_CAVEATS` with quota, OAuth, body, media, target identity, mutation, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T033 [US2] Add `PLAYLIST_IMAGES_UPDATE_CALLER_EXAMPLES` for success, missing part, invalid part, missing target identity, missing body, invalid body, missing media, unsupported media, OAuth failure, missing-resource or quota upstream failure, and out-of-scope requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T034 [US2] Attach examples and full metadata from `build_playlist_images_update_contract()` to `build_playlist_images_update_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T035 [US2] Update representative tool catalog expectations for `playlistImages_update` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` if catalog tests require representative examples outside the concrete descriptor

### Refactor and Validation for User Story 2

- [X] T036 [US2] Add or update reStructuredText docstrings for modified metadata or descriptor helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T037 [US2] Refactor metadata wording to remove duplicated shared-contract prose while keeping endpoint-specific quota, OAuth, body, media, and target identity details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T038 [US2] Run US2 focused tests with `pytest tests/contract/test_youtube_playlist_images_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently verifiable through discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Image Update Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation and access feedback for missing or invalid part selection, target metadata, upload content, OAuth access, unsupported fields, missing resources, and upstream update failures.

**Independent Test**: Submit invalid or ineligible `playlistImages_update` requests and confirm each returns a safe category and sanitized details distinct from successful update results.

### Tests for User Story 3 (Red)

- [X] T039 [P] [US3] Add unit tests for missing `part`, invalid `part`, duplicate `part`, missing `body`, malformed `body`, body missing `id`, body missing `snippet`, body missing `snippet.playlistId`, unsupported body fields, missing `media`, malformed `media`, missing `media.mimeType`, missing `media.content`, unsupported media type, unsupported optional fields, and raw media sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`
- [X] T040 [US3] Add unit tests for missing OAuth, authorization failure, quota failure, media eligibility failure, resource-not-found, endpoint-unavailable, upstream-failure, and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`
- [X] T041 [P] [US3] Add contract tests for safe error categories and invalid request examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py`
- [X] T042 [US3] Run the US3 Red tests and confirm validation and error mapping checks fail before implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T043 [US3] Implement strict invalid-request validation for unsupported part, target identity, body, media, and extra-field cases in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T044 [US3] Implement OAuth-required auth context handling for `playlistImages_update` with safe `authentication_failed` errors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T045 [US3] Implement normalized upstream error mapping for authorization, quota, media eligibility, missing resource, endpoint unavailable, and unexpected failure cases in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T046 [US3] Ensure all `playlistImages_update` errors sanitize OAuth tokens, raw media content, stack traces, raw upstream bodies, raw request context, and unsafe diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`

### Refactor and Validation for User Story 3

- [X] T047 [US3] Add or update reStructuredText docstrings for validation, auth, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T048 [US3] Refactor validation and error helpers to stay local to `playlistImages_update` unless shared safely with `playlistImages_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T049 [US3] Run US3 focused tests with `pytest tests/unit/test_youtube_playlist_images.py tests/contract/test_youtube_playlist_images_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional and validation failures are caller-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify cross-story behavior, documentation, style, and full repository health.

- [X] T050 [P] Review the public contract against the final implementation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/contracts/playlistImages_update.md`
- [X] T051 [P] Review quickstart implementation evidence expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/quickstart.md`
- [X] T052 [P] Review all changed Python functions for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T053 Run the complete focused YT-230 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/quickstart.md`
- [X] T054 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failing tests before completion
- [X] T055 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any lint failures before completion
- [X] T056 Run `git status --short` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm only intended YT-230 files and implementation files changed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP executable tool.
- **User Story 2 (Phase 4)**: Depends on Foundational and can run in parallel with US1 after shared constants and descriptor shape are coordinated, but sequential delivery after US1 is safer.
- **User Story 3 (Phase 5)**: Depends on Foundational and can run in parallel with US1/US2 after validator and error-helper ownership is coordinated, but sequential delivery after US1 is safer.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after Foundational; suggested MVP.
- **User Story 2 (P2)**: Can be tested independently through metadata and examples, but uses descriptor and contract builders introduced by US1.
- **User Story 3 (P3)**: Can be tested independently through invalid calls, but uses validator and error type introduced by US1.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation tasks.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstring tasks must finish before story checkpoint validation.
- Refactor tasks must preserve behavior and keep focused tests green.
- Final completion requires `pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.

## Parallel Opportunities

- T003 and T004 can run in parallel during setup.
- T010, T011, and T012 can run in parallel because they target contract, unit, and integration test files.
- T028, T029, and T030 can run in parallel because they target separate metadata-oriented test files.
- T039 and T041 can run in parallel because they target unit and contract files; T040 targets the same unit file as T039 and should run sequentially.
- T050, T051, and T052 can run in parallel during polish because they inspect documentation and docstrings in different scopes.

## Parallel Example: User Story 1

```bash
# Launch Red test authoring for User Story 1:
Task: "T010 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
Task: "T011 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py"
Task: "T012 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch Red metadata tests for User Story 2:
Task: "T028 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
Task: "T029 [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T030 [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
# Launch Red validation tests for User Story 3 with file ownership coordination:
Task: "T039 [US3] Add invalid request unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py"
Task: "T041 [US3] Add error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational Red tests and shared helpers.
3. Complete Phase 3 User Story 1.
4. Stop and validate `playlistImages_update` can be discovered and invoked successfully with valid OAuth-backed `part`, target-identifying `body`, and `media` arguments.

### Incremental Delivery

1. Deliver US1 for the executable endpoint-backed tool.
2. Add US2 to make quota, OAuth, body, media, target identity, examples, and out-of-scope boundaries discoverable before invocation.
3. Add US3 to harden validation and safe error categorization.
4. Complete Phase 6 with focused verification, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. Assign one person to US1 implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`.
3. Assign another person to US2 metadata tests and catalog assertions.
4. Assign another person to US3 validation tests, coordinating edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py`.

## Task Summary

- **Total tasks**: 56
- **Setup tasks**: 4
- **Foundational tasks**: 5
- **User Story 1 tasks**: 18
- **User Story 2 tasks**: 11
- **User Story 3 tasks**: 11
- **Polish tasks**: 7
- **Suggested MVP scope**: Phase 1, Phase 2, and Phase 3 only
