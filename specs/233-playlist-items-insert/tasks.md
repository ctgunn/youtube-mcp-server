# Tasks: Layer 2 Tool `playlistItems_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/data-model.md), [contracts/playlistItems_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/contracts/playlistItems_insert.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/quickstart.md)

**Tests**: Test tasks are required for every phase. Each story starts with Red tests, then Green implementation, then Refactor/docstring verification. Completion requires a final `pytest` run and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundation is in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the YT-233 design decisions and implementation targets before writing Red tests.

- [X] T001 Verify the YT-233 scope, OAuth decision, body-shape decision, result-shape decision, and safe-error decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/research.md
- [X] T002 [P] Inspect existing Layer 2 mutation-tool patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py
- [X] T003 [P] Inspect the existing Layer 1 `playlistItems.insert` wrapper metadata, required body shape, OAuth requirement, and quota cost in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py
- [X] T004 [P] Inspect current playlist-items public export, resource-family, and default registry wiring in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing checks and confirm the existing playlist-items Layer 2 module can host `playlistItems_insert`.

**Critical**: No user story implementation should begin until these shared Red checks exist and fail for the missing or incomplete `playlistItems_insert` public tool.

- [X] T005 [P] Add failing shared resource-family placement checks for `playlistItems_insert` Layer 2 contracts in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T006 [P] Add failing shared scaffolding checks for `PLAYLIST_ITEMS_INSERT_TOOL_NAME`, `PLAYLIST_ITEMS_INSERT_INPUT_SCHEMA`, and `build_playlist_items_insert_tool_descriptor` exports in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T007 [P] Add failing public-symbol export checks for `PLAYLIST_ITEMS_INSERT_TOOL_NAME`, `PLAYLIST_ITEMS_INSERT_QUOTA_COST`, `PlaylistItemsInsertToolError`, `build_playlist_items_insert_contract`, and `build_playlist_items_insert_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T008 [P] Add failing default catalog assertions that `playlistItems_insert` is discoverable with operation key `playlistItems.insert`, auth mode `oauth_required`, and quota cost `50` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T009 [P] Add failing default dispatcher registration assertions for `playlistItems_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T010 Add preliminary `playlistItems_insert` constants, input schema placeholder, caller examples placeholder, and `PlaylistItemsInsertToolError` scaffold in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T011 Export preliminary `playlistItems_insert` public symbols from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T012 Add reStructuredText docstrings for the new `playlistItems_insert` scaffold functions and error class in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

**Checkpoint**: Foundation is ready when shared symbols, family placement, and registry expectations are represented by failing tests and minimal module scaffolding.

---

## Phase 3: User Story 1 - Add Videos to Playlists Through a Public Tool (Priority: P1) MVP

**Goal**: Power users with OAuth-backed access can call `playlistItems_insert` with supported part selection and playlist/video assignment data, then receive a near-raw created playlist-item result with selected parts, assignment context, placement context when applicable, quota context, authorization context, and returned fields preserved.

**Independent Test**: Invoke `playlistItems_insert` with `{"part": "snippet", "body": {"snippet": {"playlistId": "PL123", "resourceId": {"kind": "youtube#video", "videoId": "video-123"}}}}` using OAuth-backed access, then verify the result preserves `playlistItems.insert`, quota cost `50`, selected part context, playlist/video assignment context, authorization context, and the created playlist-item resource.

### Tests for User Story 1 (Red)

- [X] T013 [P] [US1] Add contract tests for `playlistItems_insert` identity, input schema, required `part`, required `body`, OAuth mode, quota cost `50`, and created-resource result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T014 [P] [US1] Add unit tests for valid insertion arguments, wrapper invocation with OAuth context, successful result mapping, upstream field preservation, assignment context preservation, placement context preservation when supplied, and no credential leakage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T015 [P] [US1] Add integration tests for registering and executing successful `playlistItems_insert` calls through `InMemoryToolDispatcher` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py

### Implementation for User Story 1 (Green)

- [X] T016 [US1] Implement `PLAYLIST_ITEMS_INSERT_TOOL_NAME`, `PLAYLIST_ITEMS_INSERT_QUOTA_COST`, supported part constants, OAuth metadata constants, and insertion input schema in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T017 [US1] Implement `validate_playlist_items_insert_arguments` for required `part`, required `body.snippet.playlistId`, required `body.snippet.resourceId.videoId`, supported resource kind, and supported placement context in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T018 [US1] Implement `map_playlist_items_insert_result` to preserve endpoint, quota cost `50`, requested parts, assignment context, placement context when applicable, OAuth context, created playlist-item fields, `kind`, and `etag` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T019 [US1] Implement `_playlist_items_insert_auth_context` and `build_playlist_items_insert_handler` using `build_playlist_items_insert_wrapper`, OAuth-backed credential context, the validator, and result mapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T020 [US1] Implement `_default_playlist_items_insert_executor` with representative created playlist-item data for local dispatcher execution in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T021 [US1] Implement `build_playlist_items_insert_contract` and `build_playlist_items_insert_tool_descriptor` for executable MCP registration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T022 [US1] Export `playlistItems_insert` constants, builders, validator, mapper, and error class from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T023 [US1] Register `build_playlist_items_insert_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

### Refactor and Validation for User Story 1

- [X] T024 [US1] Add or update reStructuredText docstrings for every new or changed Python function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T025 [US1] Refactor `playlistItems_insert` mutation validation, result mapping, handler, exports, and registry wiring for consistency with existing Layer 2 mutation tools in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T026 [US1] Run focused US1 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and the touched playlist-items test files

**Checkpoint**: US1 is independently functional when `playlistItems_insert` can be discovered, invoked for a valid OAuth-backed playlist-item insertion, and returns a near-raw created-resource result with quota cost `50`.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Insert Requirements Before Calling (Priority: P2)

**Goal**: Client developers can inspect `playlistItems_insert` before invocation and understand endpoint identity, quota cost `50`, OAuth-backed access, required part selection, playlist/video assignment data, supported placement behavior, mutation result shape, examples, and out-of-scope workflows.

**Independent Test**: Review discovery metadata, descriptions, usage notes, caveats, and examples for `playlistItems_insert`, then verify all required quota, OAuth, part-selection, body-shape, placement, mutation-result, and boundary information is visible without invoking implementation internals.

### Tests for User Story 2 (Red)

- [X] T027 [P] [US2] Add contract tests for `playlistItems_insert` metadata, description, usage notes, caveats, examples, OAuth guidance, quota cost `50`, supported placement guidance, availability state, and safe public fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T028 [P] [US2] Add catalog tests for representative `playlistItems_insert` examples covering OAuth-backed success, supported placement, missing part, invalid part, missing playlist identifier, missing video reference, invalid body, unsupported placement, authorization failure, quota or upstream failure, and out-of-scope rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T029 [P] [US2] Add shared metadata regression checks for quota cost `50`, OAuth-backed access, mutation boundary, body requirements, placement caveats, and insert-only scope in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T030 [US2] Add `PLAYLIST_ITEMS_INSERT_DESCRIPTION`, `PLAYLIST_ITEMS_INSERT_USAGE_NOTES`, and `PLAYLIST_ITEMS_INSERT_CAVEATS` with quota cost `50`, OAuth-backed access, required part selection, required playlist/video assignment body, supported placement behavior, and out-of-scope playlist-management constraints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T031 [US2] Add `PLAYLIST_ITEMS_INSERT_CALLER_EXAMPLES` for OAuth-backed insertion, supported placement, missing part, invalid part, missing playlist identifier, missing video reference, invalid body, unsupported placement, authorization failure, quota or upstream insertion failure, and out-of-scope playlist-management rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T032 [US2] Add `playlistItems_insert` to the shared representative contract set if required by catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T033 [US2] Ensure `build_playlist_items_insert_contract` exposes active availability plus OAuth-backed access, quota cost `50`, mutation result, safe error, supported placement, and unsupported-behavior caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 2

- [X] T034 [US2] Add or update reStructuredText docstrings for metadata, example, contract, and descriptor helper functions touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T035 [US2] Refactor metadata wording to avoid duplication while preserving endpoint-specific quota, OAuth, part-selection, body-shape, placement, mutation-result, and unsupported-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T036 [US2] Run focused US2 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/contract/test_youtube_common_contract.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py, and the touched contract test files

**Checkpoint**: US2 is independently functional when callers can understand quota, OAuth-backed access, required part selection, assignment body, placement behavior, examples, mutation result shape, and unsupported boundaries from public discovery surfaces alone.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Item Insert Requests Clearly (Priority: P3)

**Goal**: Callers receive deterministic safe validation and access feedback for missing or invalid `part`, missing or invalid body, missing playlist identifier, missing video reference, unsupported placement, read-only fields, missing OAuth access, authorization failures, quota failures, duplicate or ineligible videos, unavailable service, deprecated behavior, and unexpected upstream failures.

**Independent Test**: Submit invalid or inaccessible `playlistItems_insert` requests and verify each failure maps to a safe caller-facing category without leaking API keys, OAuth tokens, raw upstream bodies, stack traces, raw request context, or sensitive details; also verify valid upstream-created resources remain distinct from local validation failures.

### Tests for User Story 3 (Red)

- [X] T037 [P] [US3] Add unit tests for missing `part`, invalid `part`, missing `body`, non-object `body`, missing `body.snippet`, missing `body.snippet.playlistId`, missing `body.snippet.resourceId.videoId`, invalid resource kind, read-only fields, unsupported optional fields, unsupported placement, conflicting placement details, and out-of-scope workflow inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T038 [P] [US3] Add contract tests for safe error categories and sanitized diagnostics for invalid request, missing OAuth access, authorization failure, quota failure, duplicate or ineligible video, missing-resource outcome, unavailable service, deprecated behavior, and unexpected upstream failure cases in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T039 [P] [US3] Add integration tests for dispatcher-level invalid insert request rejection, OAuth failure propagation, quota failure propagation, duplicate or ineligible video propagation, and safe upstream failure propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py

### Implementation for User Story 3 (Green)

- [X] T040 [US3] Extend `validate_playlist_items_insert_arguments` to reject unsupported optional parameters, read-only fields, malformed resource identity, unsupported placement details, duplicate or conflicting placement details, playlist-management fields, analytics fields, ranking fields, summarization fields, enrichment fields, and automated curation fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T041 [US3] Implement `_map_playlist_items_insert_upstream_error` for invalid request, authentication failure, authorization failure, quota failure, duplicate or ineligible resource, missing resource, endpoint unavailable, deprecated behavior, and unexpected upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T042 [US3] Ensure `PlaylistItemsInsertToolError` and handler failure paths sanitize details with shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T043 [US3] Ensure dispatcher-level `playlistItems_insert` errors preserve safe categories and do not expose OAuth tokens, API keys, raw upstream bodies, stack traces, or unsafe request context in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 3

- [X] T044 [US3] Add or update reStructuredText docstrings for validation, OAuth access-context, error-mapping, handler failure, and error classes touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T045 [US3] Refactor validation and safe error mapping to align with `comments_insert`, `commentThreads_insert`, `channelSections_insert`, `playlistImages_insert`, and shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T046 [US3] Run focused US3 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/unit/test_youtube_playlist_items.py tests/contract/test_youtube_playlist_items_contract.py tests/integration/test_youtube_playlist_items_registration.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and the touched playlist-items test files

**Checkpoint**: US3 is independently functional when invalid and inaccessible insertion requests fail with safe, specific, caller-facing outcomes and successful created-resource results remain distinct.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the full feature is coherent, documented, safe, and regression-free.

- [X] T047 [P] Review generated contract documentation against implemented public metadata in /Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/contracts/playlistItems_insert.md
- [X] T048 [P] Review generated quickstart scenarios against implemented behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/233-playlist-items-insert/quickstart.md
- [X] T049 Review all changed Python functions for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, and changed playlist-items tests under /Users/ctgunn/Projects/youtube-mcp-server/tests/
- [X] T050 Review all changed exports and registry wiring for minimal scope in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T051 Run the focused YT-233 verification command from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and touched tests under /Users/ctgunn/Projects/youtube-mcp-server/tests/
- [X] T052 Run the full repository test suite from /Users/ctgunn/Projects/youtube-mcp-server with `pytest` and fix all failures before considering YT-233 complete in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server and /Users/ctgunn/Projects/youtube-mcp-server/tests
- [X] T053 Run repository lint from /Users/ctgunn/Projects/youtube-mcp-server with `ruff check .` and fix all violations before considering YT-233 complete in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server and /Users/ctgunn/Projects/youtube-mcp-server/tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all story implementation.
- **Phase 3 US1**: Depends on Phase 2; recommended MVP.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 once the module and descriptor surface exists.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 once the validator and handler surfaces exist.
- **Phase 6 Polish**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 after Phase 2; delivers callable MVP.
- **US2 (P2)**: Can be implemented independently after Phase 2, but benefits from US1 contract/descriptors existing.
- **US3 (P3)**: Can be implemented independently after Phase 2, but benefits from US1 validator/handler skeleton existing.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Contract, unit, and integration tests can usually be written in parallel.
- Implementation tasks touching the same Python module should be sequenced to reduce conflicts.
- Docstring tasks must be completed before the story checkpoint is considered done.
- Focused tests must pass before moving to final polish.
- Full `pytest` and `ruff check .` must pass before the feature is considered complete.

---

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel.
- **Foundation**: T005, T006, T007, T008, and T009 can run in parallel because they touch different test files.
- **US1 Red tests**: T013, T014, and T015 can run in parallel.
- **US2 Red tests**: T027, T028, and T029 can run in parallel.
- **US3 Red tests**: T037, T038, and T039 can run in parallel.
- **Polish docs**: T047 and T048 can run in parallel.

## Parallel Example: User Story 1

```bash
Task: "T013 [P] [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T014 [P] [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T015 [P] [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T027 [P] [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T028 [P] [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T029 [P] [US2] Add shared metadata checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T037 [P] [US3] Add validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T038 [P] [US3] Add safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T039 [P] [US3] Add dispatcher failure integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 only. This delivers a discoverable and callable `playlistItems_insert` tool for successful playlist item insertion while preserving quota cost `50`, requested parts, assignment context, placement context when applicable, OAuth context, returned created playlist-item resource, and upstream fields.

### Incremental Delivery

1. **MVP**: US1 provides the callable playlist-item insert tool and default registry wiring.
2. **Metadata hardening**: US2 makes quota, OAuth-backed access, required part selection, body shape, placement behavior, examples, mutation result behavior, and unsupported boundaries visible before invocation.
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
