# Tasks: Layer 2 Tool `playlistImages_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/data-model.md), [contracts/playlistImages_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/contracts/playlistImages_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/quickstart.md)

**Tests**: Test tasks are required for every phase. Each story starts with Red tests, then Green implementation, then Refactor/docstring verification. Completion requires a final `pytest` run and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundation is in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature workspace and implementation targets are ready before writing Red tests.

- [X] T001 Verify the YT-228 design artifacts and selector decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/research.md
- [X] T002 [P] Inspect existing Layer 2 list-tool patterns for `membershipsLevels_list`, `members_list`, and `channelSections_list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/
- [X] T003 [P] Inspect existing Layer 1 `playlistImages.list` metadata, selector, paging, and OAuth boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py
- [X] T004 [P] Inspect current default registry wiring patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing checks and public wiring expectations that block all user stories.

**Critical**: No user story implementation should begin until these shared Red checks exist and fail for the missing `playlistImages_list` public tool.

- [X] T005 [P] Add failing shared export checks for `PLAYLIST_IMAGES_LIST_*` symbols in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T006 [P] Add failing shared public metadata checks for `playlistImages_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T007 [P] Add failing catalog coverage for `playlistImages_list` discovery and representative examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 [P] Add failing default registry discovery coverage for `playlistImages_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py

**Checkpoint**: Foundation ready when shared Red checks fail because `playlistImages_list` symbols, metadata, and default registration are missing.

---

## Phase 3: User Story 1 - Retrieve Playlist Images Through a Public Tool (Priority: P1) MVP

**Goal**: Power users with OAuth-backed access can call `playlistImages_list` and receive a near-raw playlist-image collection with requested parts, selector context, paging context when present, quota context, and returned fields preserved.

**Independent Test**: Invoke `playlistImages_list` with `part` plus one selector from `playlistId` or `id`, then verify the result preserves `playlistImages.list` endpoint context, quota cost `1`, returned `items`, requested parts, selector context, paging context when applicable, and optional upstream fields.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add contract tests for `playlistImages_list` identity, input schema, exclusive selectors, and successful list result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py
- [X] T010 [P] [US1] Add unit tests for valid `part` with `playlistId`, valid `part` with `id`, successful result mapping, upstream field preservation, paging context preservation, and successful empty result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py
- [X] T011 [P] [US1] Add integration tests for registering and executing `playlistImages_list` successful OAuth-backed calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py

### Implementation for User Story 1 (Green)

- [X] T012 [US1] Create the Layer 2 playlist-images module with `PLAYLIST_IMAGES_LIST_TOOL_NAME`, quota cost `1`, supported selectors, input schema, and safe error class in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T013 [US1] Implement `validate_playlist_images_list_arguments` for required `part`, exactly one selector from `playlistId` or `id`, playlist-scoped paging, and malformed selector rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T014 [US1] Implement `map_playlist_images_list_result` to preserve endpoint, quota cost `1`, requested parts, selector, paging, OAuth context, `items`, `kind`, `etag`, `nextPageToken`, `prevPageToken`, and `pageInfo` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T015 [US1] Implement `build_playlist_images_list_handler` using `build_playlist_images_list_wrapper`, OAuth-required auth context, the validator, and result mapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T016 [US1] Implement `build_playlist_images_list_contract` and `build_playlist_images_list_tool_descriptor` for executable MCP registration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T017 [US1] Export `playlistImages_list` constants, builders, validator, mapper, and error class from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T018 [US1] Register `build_playlist_images_list_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

### Refactor and Validation for User Story 1

- [X] T019 [US1] Add or update reStructuredText docstrings for every new or changed Python function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T020 [US1] Run focused US1 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py

**Checkpoint**: US1 is independently functional when `playlistImages_list` can be discovered, invoked for playlist-scoped and direct-image retrieval, and returns near-raw list results with quota cost `1`.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, Selectors, and Parts Before Calling (Priority: P2)

**Goal**: Client developers can inspect `playlistImages_list` before invocation and understand endpoint identity, quota cost `1`, OAuth-required access, required part selection, `playlistId` and `id` selectors, selector-specific paging, and out-of-scope workflows.

**Independent Test**: Review discovery metadata, descriptions, usage notes, caveats, and examples for `playlistImages_list` and verify all required quota, auth, selector, paging, request, and boundary information is visible without invoking implementation internals.

### Tests for User Story 2 (Red)

- [X] T021 [P] [US2] Add contract tests for metadata, description, usage notes, caveats, examples, selector guidance, paging guidance, and safe public fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py
- [X] T022 [P] [US2] Add catalog tests for representative `playlistImages_list` examples covering playlist-scoped success, direct image success, empty result, validation failures, access failure, and out-of-scope rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T023 [P] [US2] Add shared metadata regression checks for quota cost `1`, OAuth-required auth, selector boundary, and paging caveats in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T024 [US2] Add `PLAYLIST_IMAGES_LIST_DESCRIPTION`, `PLAYLIST_IMAGES_LIST_USAGE_NOTES`, and `PLAYLIST_IMAGES_LIST_CAVEATS` with quota cost `1`, OAuth-required auth, `playlistId` selector, `id` selector, paging boundaries, and out-of-scope image-management constraints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T025 [US2] Add `PLAYLIST_IMAGES_LIST_CALLER_EXAMPLES` for playlist-scoped retrieval, direct image lookup, paged playlist-scoped retrieval, empty success, missing part, invalid part, missing selector, conflicting selector, paging-with-id rejection, authorization failure, and out-of-scope image-management rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T026 [US2] Add `playlistImages_list` to the shared representative contract set in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T027 [US2] Ensure `build_playlist_images_list_contract` exposes active availability plus OAuth, selector, paging, result-boundary, and unsupported-behavior caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py

### Refactor and Validation for User Story 2

- [X] T028 [US2] Add or update reStructuredText docstrings for metadata, example, and contract helper functions touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T029 [US2] Run focused US2 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

**Checkpoint**: US2 is independently functional when callers can understand quota, OAuth access, selectors, paging, examples, and unsupported boundaries from public discovery surfaces alone.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Image List Requests Clearly (Priority: P3)

**Goal**: Callers receive deterministic safe validation and access feedback for malformed, unsupported, inaccessible, quota, unavailable, and unexpected playlist-image list outcomes.

**Independent Test**: Submit invalid or inaccessible `playlistImages_list` requests and verify each failure maps to a safe caller-facing category without leaking OAuth tokens, raw upstream bodies, stack traces, raw request context, or sensitive details.

### Tests for User Story 3 (Red)

- [X] T030 [P] [US3] Add unit tests for missing `part`, invalid `part`, missing selector, conflicting selectors, paging with `id`, blank `pageToken`, non-integer `maxResults`, out-of-range `maxResults`, unsupported fields, and unsupported media or mutation inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py
- [X] T031 [P] [US3] Add contract tests for safe error categories and sanitized diagnostics for invalid request, authentication, authorization, quota, not-found, unavailable, and upstream failure cases in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py
- [X] T032 [P] [US3] Add integration tests for dispatcher-level invalid request rejection and safe failure propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py

### Implementation for User Story 3 (Green)

- [X] T033 [US3] Extend `validate_playlist_images_list_arguments` to reject unsupported optional parameters, request bodies, mutation fields, media upload fields, playlist-management fields, analytics, ranking, summarization, enrichment fields, and selector-incompatible paging in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T034 [US3] Implement `_playlist_images_list_auth_context` to reject API-key-only execution and require OAuth-compatible access in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T035 [US3] Implement `_map_playlist_images_list_upstream_error` for invalid request, authentication, authorization, quota, not-found, endpoint unavailable, and upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T036 [US3] Ensure `PlaylistImagesListToolError` sanitizes details with shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py

### Refactor and Validation for User Story 3

- [X] T037 [US3] Add or update reStructuredText docstrings for validation, auth-context, error-mapping, and error classes touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T038 [US3] Run focused US3 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py

**Checkpoint**: US3 is independently functional when invalid and inaccessible requests fail with safe, specific, caller-facing outcomes and successful empty results remain distinct.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the full feature is coherent, documented, safe, and regression-free.

- [X] T039 [P] Review generated contract documentation against implemented public metadata in /Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/contracts/playlistImages_list.md
- [X] T040 [P] Review generated quickstart scenarios against implemented behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/quickstart.md
- [X] T041 Review all changed Python functions for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T042 Review all changed exports and registry wiring for minimal scope in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T043 Run the focused YT-228 verification command and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T044 Run `pytest` for the full repository test suite and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T045 Run `ruff check .` and fix lint failures in /Users/ctgunn/Projects/youtube-mcp-server/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all story implementation.
- **Phase 3 US1**: Depends on Phase 2; recommended MVP.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 once the module surface exists.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 once the validator/error surface exists.
- **Phase 6 Polish**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 after Phase 2; delivers callable MVP.
- **US2 (P2)**: Can be implemented independently after Phase 2, but benefits from US1 contract/descriptors existing.
- **US3 (P3)**: Can be implemented independently after Phase 2, but benefits from US1 validator/handler skeleton existing.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Contract and unit tests can usually be written in parallel.
- Implementation tasks touching the same Python module should be sequenced to reduce conflicts.
- Docstring tasks must be completed before the story checkpoint is considered done.
- Focused tests must pass before moving to final polish.

---

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel.
- **Foundation**: T005, T006, T007, and T008 can run in parallel because they touch different test files.
- **US1 Red tests**: T009, T010, and T011 can run in parallel.
- **US2 Red tests**: T021, T022, and T023 can run in parallel.
- **US3 Red tests**: T030, T031, and T032 can run in parallel.
- **Polish docs**: T039 and T040 can run in parallel.

## Parallel Example: User Story 1

```bash
# Launch US1 Red test authoring in parallel:
Task: "T009 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
Task: "T010 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py"
Task: "T011 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 metadata/example tests in parallel:
Task: "T021 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
Task: "T022 [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T023 [US2] Add shared metadata checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 invalid-request and safe-error tests in parallel:
Task: "T030 [US3] Add validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_images.py"
Task: "T031 [US3] Add safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py"
Task: "T032 [US3] Add dispatcher failure integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_images_registration.py"
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 only. This delivers a discoverable and callable `playlistImages_list` tool for successful OAuth-backed retrieval while preserving quota cost `1`, requested parts, selector context, paging context when applicable, returned playlist-image resources, and upstream fields.

### Incremental Delivery

1. **MVP**: US1 provides the callable playlist-image list tool and default registry wiring.
2. **Metadata hardening**: US2 makes quota, OAuth, selectors, paging, examples, and unsupported boundaries visible before invocation.
3. **Failure hardening**: US3 completes deterministic validation, safe error mapping, and inaccessible-resource handling.
4. **Polish**: Run focused verification, full `pytest`, and `ruff check .` before completion.

### Validation Checklist

- Every task uses `- [ ] T###` checklist format.
- User story phase tasks include `[US1]`, `[US2]`, or `[US3]`.
- Parallelizable tasks include `[P]`.
- Every task description includes an absolute file path.
- Test tasks precede implementation tasks in each user story.
- Python implementation phases include explicit reStructuredText docstring tasks.
- Final phase includes full repository test-suite and lint commands.
