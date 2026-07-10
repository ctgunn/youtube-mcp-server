# Tasks: Layer 2 Tool `playlistItems_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/data-model.md), [contracts/playlistItems_update.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/contracts/playlistItems_update.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/quickstart.md)

**Tests**: Test tasks are required and must be written before implementation. Final completion requires focused tests, full `pytest`, and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the foundational phase.

## Phase 1: Setup

**Purpose**: Confirm local context and protect existing playlist-items behavior before adding `playlistItems_update`.

- [X] T001 Review YT-234 planning artifacts for target contract, request shape, examples, and verification commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/plan.md
- [X] T002 Inspect existing list/insert patterns and current update wrapper dependency in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T003 Run the current focused playlist-items baseline tests before edits from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py`

---

## Phase 2: Foundational

**Purpose**: Add failing shared discovery, export, and registry expectations that all user stories depend on.

**Critical**: No user story implementation should begin until these Red tests exist and fail for the missing `playlistItems_update` public tool.

- [X] T004 [P] Add failing shared export/scaffolding checks for `PLAYLIST_ITEMS_UPDATE_*` symbols and `build_playlist_items_update_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T005 [P] Add failing family-level contract checks for `playlistItems_update` metadata presence in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T006 [P] Add failing catalog contract checks that `playlistItems_update` appears with mutation metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T007 [P] Add failing default dispatcher registration checks for `playlistItems_update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T008 Run foundational Red checks and confirm they fail for missing `playlistItems_update` from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`

**Checkpoint**: Foundational Red coverage exists for shared exports, catalog metadata, and default registration.

---

## Phase 3: User Story 1 - Update Playlist Items Through a Public Tool (Priority: P1)

**Goal**: A caller with OAuth-backed access can call `playlistItems_update` with supported `part`, `body.id`, and writable `body.snippet` playlist/video context and receive a near-raw updated playlist-item result.

**Independent Test**: Invoke `playlistItems_update` through the descriptor or dispatcher with a valid OAuth-backed request and confirm the result includes `playlistItems.update`, quota cost `50`, selected parts, target identity, writable update context, authorization context, and returned playlist-item fields.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add failing contract tests for `playlistItems_update` public symbols, input schema, response convention, and updated-resource result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T010 [P] [US1] Add failing unit tests for valid `playlistItems_update` argument normalization, handler wrapper invocation, result mapping, and local executor response in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T011 [P] [US1] Add failing integration tests for direct descriptor registration and dispatcher execution of a valid `playlistItems_update` request in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T012 [US1] Run User Story 1 Red tests and confirm they fail for missing update behavior from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py`

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Import `build_playlist_items_update_wrapper` and add `PLAYLIST_ITEMS_UPDATE_TOOL_NAME`, `PLAYLIST_ITEMS_UPDATE_QUOTA_COST`, `PLAYLIST_ITEMS_UPDATE_SUPPORTED_PARTS`, and `PLAYLIST_ITEMS_UPDATE_INPUT_SCHEMA` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T014 [US1] Add `PlaylistItemsUpdateToolError`, update-specific part validation, update body validation, target identity helpers, and writable update context helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T015 [US1] Add `map_playlist_items_update_result`, `_playlist_items_update_auth_context`, `_default_playlist_items_update_executor`, and `build_playlist_items_update_handler` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T016 [US1] Add `build_playlist_items_update_contract` and `build_playlist_items_update_tool_descriptor` with near-raw updated-resource response boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T017 [US1] Export `playlistItems_update` constants, error class, validator, mapper, contract builder, handler builder, and descriptor builder in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T018 [US1] Export the new playlist-items update symbols from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T019 [US1] Register `build_playlist_items_update_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T020 [US1] Add or update reStructuredText docstrings for every new or changed `playlistItems_update` function and nested fake transport function in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 1

- [X] T021 [US1] Refactor User Story 1 implementation for helper reuse with list/insert while preserving behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T022 [US1] Run User Story 1 focused tests and fix failures from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py`

**Checkpoint**: User Story 1 is independently functional as an MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Update Semantics Before Calling (Priority: P2)

**Goal**: A client developer can discover `playlistItems_update` and understand upstream identity, quota cost, OAuth requirement, part selection, target identity, writable update data, mutation result shape, availability, examples, and out-of-scope workflows before invocation.

**Independent Test**: Review the tool descriptor metadata and examples and confirm all caller-facing quota, OAuth, update-semantics, and boundary details are present without consulting implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T023 [P] [US2] Add failing metadata completeness tests for `playlistItems_update` description, usage notes, caveats, examples, quota, OAuth, target identity, writable data, and out-of-scope boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T024 [P] [US2] Add failing catalog tests for `playlistItems_update` quota, OAuth mode, operation key, response convention, and response boundary in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T025 [P] [US2] Add failing default registration metadata tests for `playlistItems_update` discovery output in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T026 [US2] Run User Story 2 Red tests and confirm they fail for incomplete caller-facing metadata from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 2 (Green)

- [X] T027 [US2] Add `PLAYLIST_ITEMS_UPDATE_DESCRIPTION`, `PLAYLIST_ITEMS_UPDATE_USAGE_NOTES`, and `PLAYLIST_ITEMS_UPDATE_CAVEATS` with quota, OAuth, required target identity, writable data, mutation semantics, and out-of-scope boundaries in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T028 [US2] Add `PLAYLIST_ITEMS_UPDATE_CALLER_EXAMPLES` covering success, missing part, invalid part, missing target identity, missing writable body, invalid body, unsupported field, authorization failure, quota/upstream failure, and unsupported workflow in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T029 [US2] Wire `PLAYLIST_ITEMS_UPDATE_DESCRIPTION`, usage notes, caveats, examples, response convention, and availability metadata into `build_playlist_items_update_contract` and `build_playlist_items_update_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T030 [US2] Export `PLAYLIST_ITEMS_UPDATE_DESCRIPTION`, `PLAYLIST_ITEMS_UPDATE_USAGE_NOTES`, `PLAYLIST_ITEMS_UPDATE_CAVEATS`, and `PLAYLIST_ITEMS_UPDATE_CALLER_EXAMPLES` from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T031 [US2] Add or update reStructuredText docstrings for any metadata or descriptor helper functions changed for User Story 2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 2

- [X] T032 [US2] Refactor User Story 2 metadata wording for consistency with `playlistItems_insert`, `channelSections_update`, and `playlistImages_update` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T033 [US2] Run User Story 2 focused tests and fix failures from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`

**Checkpoint**: User Story 2 is independently verifiable through public discovery metadata.

---

## Phase 5: User Story 3 - Reject Invalid Playlist Item Update Requests Clearly (Priority: P3)

**Goal**: A caller receives safe validation and access feedback for missing or invalid inputs, unsupported fields, missing OAuth access, and upstream update failures.

**Independent Test**: Submit representative invalid or ineligible `playlistItems_update` requests and confirm each failure is safely categorized with field guidance while secrets and raw diagnostics are sanitized.

### Tests for User Story 3 (Red)

- [X] T034 [P] [US3] Add failing unit validation tests for missing `part`, invalid `part`, missing `body`, non-object `body`, missing `body.id`, missing `body.snippet`, missing playlist id, missing video id, invalid resource kind, read-only fields, unsupported placement, unsupported content details, and unsupported top-level fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T035 [US3] Add failing unit tests for `PlaylistItemsUpdateToolError` detail sanitization and upstream error mapping categories in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py
- [X] T036 [P] [US3] Add failing integration tests for safe dispatcher errors from invalid `playlistItems_update` calls and missing OAuth execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py
- [X] T037 [P] [US3] Add failing contract tests that representative error examples for invalid request, authorization, quota, missing-resource, deprecated endpoint, unavailable endpoint, and unexpected upstream outcomes are present in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py
- [X] T038 [US3] Run User Story 3 Red tests and confirm they fail for incomplete validation/error behavior from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_playlist_items_contract.py`

### Implementation for User Story 3 (Green)

- [X] T039 [US3] Complete `validate_playlist_items_update_arguments` to normalize valid update requests and reject missing, malformed, read-only, unsupported, or conflicting fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T040 [US3] Complete `_map_playlist_items_update_upstream_error` to map invalid request, auth, authorization, quota, not found, unavailable, deprecated, transient, and unexpected categories safely in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T041 [US3] Ensure `build_playlist_items_update_handler` converts validation, OAuth, wrapper `ValueError`, and `NormalizedUpstreamError` failures into sanitized `PlaylistItemsUpdateToolError` responses in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T042 [US3] Add or update reStructuredText docstrings for all validation, error, auth, and handler functions changed for User Story 3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py

### Refactor and Validation for User Story 3

- [X] T043 [US3] Refactor safe invalid-request helpers and error category mapping to avoid duplication with insert/list behavior while preserving update-specific messages in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T044 [US3] Run User Story 3 focused tests and fix failures from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_playlist_items_contract.py`

**Checkpoint**: All user stories are independently functional and failure-safe.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Verify the complete YT-234 feature, documentation alignment, and repository quality.

- [X] T045 [P] Update any YT-234 quickstart evidence notes if implementation behavior differs from the planned examples in /Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/quickstart.md
- [X] T046 [P] Review feature contract wording against implemented metadata and adjust only if needed in /Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/contracts/playlistItems_update.md
- [X] T047 Run combined focused YT-234 suites and fix failures from /Users/ctgunn/Projects/youtube-mcp-server using `pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
- [X] T048 Run the full repository test suite and fix every failure from /Users/ctgunn/Projects/youtube-mcp-server using `pytest`
- [X] T049 Run repository lint and fix every reported issue from /Users/ctgunn/Projects/youtube-mcp-server using `ruff check .`
- [X] T050 Verify all new or modified Python functions have reStructuredText docstrings with purpose, inputs, outputs, raised errors when relevant, and side effects when relevant in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py
- [X] T051 Verify git diff is scoped to YT-234 implementation, tests, and documentation before handoff in /Users/ctgunn/Projects/youtube-mcp-server

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1; creates shared Red tests that block implementation.
- **Phase 3 User Story 1**: Depends on Phase 2; recommended MVP.
- **Phase 4 User Story 2**: Depends on Phase 2 and can begin after the descriptor/contract skeleton from User Story 1 exists.
- **Phase 5 User Story 3**: Depends on Phase 2 and can begin after the update validator/error class skeleton from User Story 1 exists.
- **Phase 6 Polish**: Depends on selected user stories being complete; full feature completion depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: Core execution path; no dependency on US2 or US3 after foundational Red tests.
- **US2 (P2)**: Metadata/documentation path; can be developed in parallel with US3 after US1 descriptor names and constants are introduced.
- **US3 (P3)**: Validation/error path; can be developed in parallel with US2 after US1 error class and validator skeleton are introduced.

### Completion Order

1. Setup and foundational Red tests.
2. US1 as the MVP: valid update request works end-to-end.
3. US2: public metadata and examples are complete.
4. US3: invalid and ineligible requests fail safely.
5. Polish: focused tests, full `pytest`, `ruff check .`, docstring audit, and scoped diff review.

---

## Parallel Execution Examples

### Foundational

```text
Task: T004 Add export/scaffolding Red tests in tests/unit/test_youtube_common_scaffolding.py
Task: T005 Add family contract Red tests in tests/contract/test_youtube_common_contract.py
Task: T006 Add catalog Red tests in tests/contract/test_youtube_tool_catalog_contract.py
Task: T007 Add registration Red tests in tests/integration/test_youtube_tool_registration.py
```

### User Story 1

```text
Task: T009 Add contract Red tests in tests/contract/test_youtube_playlist_items_contract.py
Task: T010 Add unit Red tests in tests/unit/test_youtube_playlist_items.py
Task: T011 Add integration Red tests in tests/integration/test_youtube_playlist_items_registration.py
```

### User Story 2

```text
Task: T023 Add metadata contract Red tests in tests/contract/test_youtube_playlist_items_contract.py
Task: T024 Add catalog Red tests in tests/contract/test_youtube_tool_catalog_contract.py
Task: T025 Add registration metadata Red tests in tests/integration/test_youtube_tool_registration.py
```

### User Story 3

```text
Task: T034 Add validation Red tests in tests/unit/test_youtube_playlist_items.py
Task: T036 Add dispatcher error Red tests in tests/integration/test_youtube_playlist_items_registration.py
Task: T037 Add error example contract Red tests in tests/contract/test_youtube_playlist_items_contract.py
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 only.
3. Validate `playlistItems_update` can execute a representative valid update through focused contract/unit/integration tests.
4. Stop for review if only the MVP is desired.

### Incremental Delivery

1. Deliver US1 for valid update execution.
2. Deliver US2 for discoverability, quota, OAuth, examples, and semantic clarity.
3. Deliver US3 for robust validation and safe error handling.
4. Run polish validation and hand off with full-suite evidence.

### Quality Gates

- Red tests must be added and observed failing before Green implementation for each story.
- Every Python code task must include or be followed by a docstring task before the story is complete.
- Targeted tests are not final completion evidence.
- Full `pytest` and `ruff check .` must pass before the feature is considered complete.
