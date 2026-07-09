# Tasks: Layer 2 Tool `playlistItems_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/data-model.md), [contracts/playlistItems_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/contracts/playlistItems_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/quickstart.md)

**Tests**: Test tasks are required for every phase. Each story starts with Red tests, then Green implementation, then Refactor/docstring verification. Completion requires a final `pytest` run and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundation is in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the YT-232 design decisions and implementation targets before writing Red tests.

- [X] T001 Verify the YT-232 scope, selector decisions, access mode, and pagination decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/research.md
- [X] T002 [P] Inspect existing Layer 2 list-tool patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T003 [P] Inspect the existing Layer 1 `playlistItems.list` wrapper metadata, selector rules, paging behavior, and API-key access expectation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py
- [X] T004 [P] Inspect current public export, resource-family, and default registry wiring patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing checks and minimal playlist-items module scaffolding that all user stories depend on.

**Critical**: No user story implementation should begin until these shared Red checks exist and fail for the missing or incomplete `playlistItems_list` public tool.

- [X] T005 [P] Add failing shared resource-family placement checks for `playlist_items` Layer 2 contracts in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T006 [P] Add failing shared scaffolding checks for `playlist_items` representative exports in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T007 [P] Add failing public-symbol export checks for `PLAYLIST_ITEMS_LIST_TOOL_NAME`, `PLAYLIST_ITEMS_LIST_INPUT_SCHEMA`, `PlaylistItemsListToolError`, and `build_playlist_items_list_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T008 [P] Add failing default catalog assertions that `playlistItems_list` is discoverable with operation key `playlistItems.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T009 [P] Add failing default dispatcher registration assertions for `playlistItems_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T010 Create the new Layer 2 playlist-items module scaffold with `PLAYLIST_ITEMS_LIST_TOOL_NAME`, `PLAYLIST_ITEMS_LIST_QUOTA_COST`, `PLAYLIST_ITEMS_LIST_INPUT_SCHEMA`, and `PlaylistItemsListToolError` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T011 Export the preliminary playlist-items list public symbols from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T012 Add reStructuredText docstrings for the new playlist-items scaffold functions and error class in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

**Checkpoint**: Foundation is ready when shared symbols, family placement, and registry expectations are represented by failing tests and minimal module scaffolding.

---

## Phase 3: User Story 1 - Retrieve Playlist Items Through a Public Tool (Priority: P1) MVP

**Goal**: Power users can call `playlistItems_list` with supported part selection and one supported selector, then receive a near-raw playlist-item collection with selected parts, selector context, paging context when applicable, quota context, access context, and returned fields preserved.

**Independent Test**: Invoke `playlistItems_list` with `{"part": "snippet,contentDetails", "playlistId": "PL123"}` and with `{"part": "id,snippet", "id": "playlist-item-123"}`, then verify the result preserves `playlistItems.list`, quota cost `1`, selected part context, selector context, returned `items`, paging context when present, and successful empty collection behavior.

### Tests for User Story 1 (Red)

- [X] T013 [P] [US1] Add contract tests for `playlistItems_list` identity, input schema, required `part`, exclusive `playlistId` or `id` selectors, and successful list result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T014 [P] [US1] Add unit tests for valid playlist-scoped arguments, valid identifier-based arguments, wrapper invocation, successful result mapping, upstream field preservation, paging context preservation, and empty successful result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T015 [P] [US1] Add integration tests for registering and executing successful `playlistItems_list` calls through `InMemoryToolDispatcher` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py

### Implementation for User Story 1 (Green)

- [X] T016 [US1] Implement `validate_playlist_items_list_arguments` for required `part`, exactly one selector from `playlistId` or `id`, playlist-scoped paging, and malformed selector rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T017 [US1] Implement `map_playlist_items_list_result` to preserve endpoint, quota cost `1`, requested parts, selector, paging, access context, `items`, `kind`, `etag`, `nextPageToken`, `prevPageToken`, and `pageInfo` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T018 [US1] Implement `build_playlist_items_list_handler` using `build_playlist_items_list_wrapper`, API-key access context, the validator, and result mapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T019 [US1] Implement `build_playlist_items_list_contract` and `build_playlist_items_list_tool_descriptor` for executable MCP registration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T020 [US1] Export `playlistItems_list` constants, builders, validator, mapper, and error class from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T021 [US1] Register `build_playlist_items_list_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

### Refactor and Validation for User Story 1

- [X] T022 [US1] Add or update reStructuredText docstrings for every new or changed Python function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T023 [US1] Refactor `playlistItems_list` retrieval, result mapping, handler, exports, and registry wiring for consistency with existing Layer 2 list tools in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T024 [US1] Run focused US1 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and the touched playlist-items test files

**Checkpoint**: US1 is independently functional when `playlistItems_list` can be discovered, invoked for playlist-scoped and identifier-based retrieval, and returns near-raw list results with quota cost `1`.

---

## Phase 4: User Story 2 - Understand Cost, Selectors, Access, and Pagination Before Calling (Priority: P2)

**Goal**: Client developers can inspect `playlistItems_list` before invocation and understand endpoint identity, quota cost `1`, API-key access expectations, required part selection, `playlistId` and `id` selectors, selector-specific paging, empty-result behavior, examples, and out-of-scope workflows.

**Independent Test**: Review discovery metadata, descriptions, usage notes, caveats, and examples for `playlistItems_list`, then verify all required quota, access, selector, paging, request, empty-result, and boundary information is visible without invoking implementation internals.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add contract tests for metadata, description, usage notes, caveats, examples, selector guidance, paging guidance, empty-result guidance, availability state, and safe public fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T026 [P] [US2] Add catalog tests for representative `playlistItems_list` examples covering playlist-scoped success, paginated playlist traversal, identifier success, empty result, validation failures, access failure, and out-of-scope rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T027 [P] [US2] Add shared metadata regression checks for quota cost `1`, API-key access, selector boundary, pagination caveats, and list-only scope in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T028 [US2] Add `PLAYLIST_ITEMS_LIST_DESCRIPTION`, `PLAYLIST_ITEMS_LIST_USAGE_NOTES`, and `PLAYLIST_ITEMS_LIST_CAVEATS` with quota cost `1`, API-key access, `playlistId` selector, `id` selector, paging boundaries, empty-result behavior, and out-of-scope playlist-management constraints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T029 [US2] Add `PLAYLIST_ITEMS_LIST_CALLER_EXAMPLES` for playlist-scoped retrieval, paginated playlist traversal, identifier-based retrieval, empty success, missing part, invalid part, missing selector, conflicting selector, unsupported paging, access failure, and out-of-scope playlist-management rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T030 [US2] Add `playlistItems_list` to the shared representative contract set if required by catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T031 [US2] Ensure `build_playlist_items_list_contract` exposes active availability plus API-key access, selector, paging, list-result, safe error, and unsupported-behavior caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 2

- [X] T032 [US2] Add or update reStructuredText docstrings for metadata, example, contract, and descriptor helper functions touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T033 [US2] Refactor metadata wording to avoid duplication while preserving endpoint-specific quota, access, selector, paging, empty-result, and unsupported-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T034 [US2] Run focused US2 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/contract/test_youtube_common_contract.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py, and the touched contract test files

**Checkpoint**: US2 is independently functional when callers can understand quota, API-key access, selectors, paging, examples, empty-result behavior, and unsupported boundaries from public discovery surfaces alone.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Item List Requests Clearly (Priority: P3)

**Goal**: Callers receive deterministic safe validation and access feedback for missing `part`, invalid `part`, missing selectors, conflicting selectors, malformed identifiers, unsupported paging, unsupported fields, inaccessible requests, quota failures, unavailable service, deprecated behavior, and unexpected upstream failures.

**Independent Test**: Submit invalid or inaccessible `playlistItems_list` requests and verify each failure maps to a safe caller-facing category without leaking API keys, OAuth tokens, raw upstream bodies, stack traces, raw request context, or sensitive details; also verify successful empty results remain distinct.

### Tests for User Story 3 (Red)

- [X] T035 [P] [US3] Add unit tests for missing `part`, invalid `part`, missing selector, conflicting selectors, blank `playlistId`, blank `id`, non-string selector values, duplicate or excessive identifier input, blank `pageToken`, non-integer `maxResults`, out-of-range `maxResults`, selector-incompatible paging, unsupported fields, and out-of-scope enrichment or mutation inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T036 [P] [US3] Add contract tests for safe error categories and sanitized diagnostics for invalid request, access failure, quota failure, missing-resource or no-match outcome, unavailable service, deprecated behavior, and unexpected upstream failure cases in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T037 [P] [US3] Add integration tests for dispatcher-level invalid request rejection, access failure propagation, empty successful result propagation, and safe upstream failure propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py

### Implementation for User Story 3 (Green)

- [X] T038 [US3] Extend `validate_playlist_items_list_arguments` to reject unsupported optional parameters, request bodies, mutation fields, media upload fields, playlist-management fields, analytics, ranking, summarization, enrichment fields, and selector-incompatible paging in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T039 [US3] Implement `_playlist_items_list_access_context` to expose API-key access expectations safely and categorize missing, invalid, or insufficient access in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T040 [US3] Implement `_map_playlist_items_list_upstream_error` for invalid request, access failure, quota failure, missing resource, endpoint unavailable, deprecated behavior, and unexpected upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T041 [US3] Ensure `PlaylistItemsListToolError` and handler failure paths sanitize details with shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 3

- [X] T042 [US3] Add or update reStructuredText docstrings for validation, access-context, error-mapping, handler failure, and error classes touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T043 [US3] Refactor validation and safe error mapping to align with `playlistImages_list`, `comments_list`, `commentThreads_list`, and shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T044 [US3] Run focused US3 tests from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/unit/test_youtube_playlist_items.py tests/contract/test_youtube_playlist_items_contract.py tests/integration/test_youtube_playlist_items_registration.py` and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py and the touched playlist-items test files

**Checkpoint**: US3 is independently functional when invalid and inaccessible requests fail with safe, specific, caller-facing outcomes and successful empty results remain distinct.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the full feature is coherent, documented, safe, and regression-free.

- [X] T045 [P] Review generated contract documentation against implemented public metadata in /Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/contracts/playlistItems_list.md
- [X] T046 [P] Review generated quickstart scenarios against implemented behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/quickstart.md
- [X] T047 Review all changed Python functions for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, and changed playlist-items tests under /Users/ctgunn/Projects/youtube-mcp-server/tests/
- [X] T048 Review all changed exports and registry wiring for minimal scope in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T049 Run the focused YT-232 verification command from /Users/ctgunn/Projects/youtube-mcp-server with `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` and fix failures in the touched files
- [X] T050 Run the full repository test suite from /Users/ctgunn/Projects/youtube-mcp-server with `pytest` and fix all failures before considering YT-232 complete
- [X] T051 Run repository lint from /Users/ctgunn/Projects/youtube-mcp-server with `ruff check .` and fix all violations before considering YT-232 complete

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
- **US2 Red tests**: T025, T026, and T027 can run in parallel.
- **US3 Red tests**: T035, T036, and T037 can run in parallel.
- **Polish docs**: T045 and T046 can run in parallel.

## Parallel Example: User Story 1

```bash
Task: "T013 [P] [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T014 [P] [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T015 [P] [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T025 [P] [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T026 [P] [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T027 [P] [US2] Add shared metadata checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T035 [P] [US3] Add validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py"
Task: "T036 [P] [US3] Add safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py"
Task: "T037 [P] [US3] Add dispatcher failure integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py"
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 only. This delivers a discoverable and callable `playlistItems_list` tool for successful playlist item retrieval while preserving quota cost `1`, requested parts, selector context, paging context when applicable, returned playlist item resources, and upstream fields.

### Incremental Delivery

1. **MVP**: US1 provides the callable playlist-item list tool and default registry wiring.
2. **Metadata hardening**: US2 makes quota, API-key access, selectors, paging, examples, empty-result behavior, and unsupported boundaries visible before invocation.
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
