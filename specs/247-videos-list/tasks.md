# Tasks: Layer 2 Tool `videos_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/data-model.md), [contracts/videos_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/contracts/videos_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/plan.md`
- [X] T002 Inspect the existing Layer 1 `videos.list` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`
- [X] T003 [P] Inspect existing concrete list-tool implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`
- [X] T004 [P] Inspect existing active reference-list tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect shared family placement for `videos` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing `videos_list` surface.

- [X] T007 [P] Add Red public export checks for `VIDEOS_LIST_TOOL_NAME`, `VIDEOS_LIST_QUOTA_COST`, and `build_videos_list_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `videos` family has a concrete Layer 2 module and list descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videos_list` appears once with resource family `videos` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videos_list` is discoverable through the tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red videos-family registration checks for `videos_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T012 Add shared fake wrapper, fake executor, API-key, and OAuth helper classes for videos tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T013 Run foundational Red checks and confirm they fail for missing videos symbols from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Retrieve Video Resources Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `videos_list` with valid `part` and exactly one selector, then receive a near-raw video-list result with endpoint, quota, access, selected-part, selector, pagination when applicable, and returned item context.

**Independent Test**: Invoke the tool handler with `{"part": "snippet,contentDetails", "id": "abc123"}`, `{"part": "snippet,statistics", "chart": "mostPopular"}`, and `{"part": "snippet", "myRating": "like"}` using a fake Layer 1 wrapper; verify one wrapper call and a result containing `endpoint: videos.list`, `quotaCost: 1`, `requestedParts`, `selector`, selector-appropriate `auth`, `items`, and `empty`.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videos_list` tool identity, input schema, upstream identity, quota cost 1, conditional auth mode, active availability, list response convention, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_videos_list_arguments`, part splitting, selector extraction, pagination extraction, chart-refinement extraction, `map_videos_list_result`, and `build_videos_list_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T016 [P] [US1] Add integration tests proving `videos_list` is registered and callable through the videos family registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videos_list` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Create the concrete videos Layer 2 module with imports for `build_videos_list_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T019 [US1] Define `VIDEOS_LIST_TOOL_NAME`, `VIDEOS_LIST_QUOTA_COST`, selector constants, pagination constants, supported field constants, unsafe-detail keys, and `VIDEOS_LIST_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T020 [US1] Implement `VideosListToolError` and safe error detail sanitization support for video-list failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T021 [US1] Implement `validate_videos_list_arguments` requiring non-empty `part`, exactly one selector from `id`, `chart`, or `myRating`, collection-only pagination, chart-only refinements, and no unsupported additional fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T022 [US1] Implement part-selection, direct ID selector, chart selector, rating selector, pagination, and chart-refinement helpers that preserve caller context without fabricating video fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T023 [US1] Implement selector-specific API-key and OAuth auth context selection for `id`, `chart`, and `myRating` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T024 [US1] Implement `map_videos_list_result` to return endpoint, quota cost 1, requested parts, selector context, pagination context, chart refinement context, auth context, items, active availability, empty flag, and safe upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T025 [US1] Implement `build_videos_list_handler` using the Layer 1 list wrapper once per valid call with selector-appropriate auth in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T026 [US1] Implement `build_videos_list_contract` and `build_videos_list_tool_descriptor` with read-only active list response metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T027 [US1] Export `videos_list` constants, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_videos_list_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake executor, or auth helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T032 [US1] Refactor US1 video-list execution code for consistency with active read/list helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Parts, Selectors, Access, and Pagination Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videos_list` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `1`, conditional access, required `part`, exactly-one-selector behavior, pagination boundaries, chart refinements, empty-result behavior, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videos.list`, quota cost `1`, API-key-compatible `id` and `chart`, OAuth-required `myRating`, required `part`, selector guidance, pagination guidance, chart-refinement guidance, empty-success behavior, active availability, and no search/upload/update/delete/rating-mutation/transcript/analytics/ranking/summarization/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for metadata text, usage notes, caveats, quota visibility, conditional auth visibility, selector visibility, pagination visibility, chart-refinement visibility, availability state, response boundary, empty-success policy, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `videos_list` metadata exposes quota cost 1, conditional auth, required `part`, exactly-one-selector behavior, pagination boundaries, chart refinements, and active availability before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videos_list` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `videos_list` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `VIDEOS_LIST_DESCRIPTION`, `VIDEOS_LIST_USAGE_NOTES`, and `VIDEOS_LIST_CAVEATS` with quota cost 1, conditional access, required `part`, selector behavior, pagination behavior, chart refinement behavior, empty-success behavior, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T039 [US2] Add `VIDEOS_LIST_CALLER_EXAMPLES` covering direct ID lookup, chart lookup, rating lookup with OAuth, paginated chart traversal, populated success, empty success, missing `part`, missing selector, conflicting selectors, invalid pagination, missing API-key access, missing OAuth access, quota or upstream failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T040 [US2] Update `build_videos_list_contract` and `build_videos_list_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, conditional auth details, selector details, pagination details, chart-refinement details, and empty-success policy in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T041 [US2] Update shared examples or catalog entries if required so `videos_list` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `videos_list` export coverage for caller-facing example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with active read/list tools while preserving quota, conditional access, required `part`, selector, pagination, chart-refinement, empty-result, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Video List Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation, access, quota, availability, deprecation, empty-success, and unexpected-upstream outcomes that remain distinct from successful populated video-list results.

**Independent Test**: Submit missing `part`, empty `part`, non-string `part`, missing selector, conflicting selectors, malformed `id`, malformed `chart`, malformed `myRating`, invalid pagination, incompatible chart refinements, unsupported fields, search inputs, upload/update/delete instructions, rating mutation instructions, transcript instructions, analytics instructions, missing API-key access, missing OAuth access, empty upstream success, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category or empty-success result and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [P] [US3] Add unit validation tests for missing `part`, empty `part`, non-string `part`, malformed `part`, unsupported top-level fields, search text, upload instructions, update instructions, delete instructions, rating mutation instructions, transcript instructions, analytics instructions, ranking modifiers, summarization modifiers, and enrichment modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T047 [US3] Add unit selector validation tests for missing selector, multiple selectors, empty `id`, malformed `id`, empty `chart`, unsupported `chart`, empty `myRating`, unsupported `myRating`, unsupported selector shape, and ambiguous selector values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T048 [US3] Add unit pagination and chart-refinement validation tests for empty `pageToken`, non-string `pageToken`, invalid `maxResults`, out-of-range `maxResults`, pagination with `id`, `regionCode` without `chart`, `videoCategoryId` without `chart`, malformed `regionCode`, and malformed `videoCategoryId` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T049 [US3] Add unit handler tests for missing API-key access, missing OAuth access for `myRating`, invalid auth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T050 [US3] Add unit result and upstream error mapping tests for empty upstream success, resource not found, quota failure, invalid request, authorization failure, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T051 [P] [US3] Add contract tests proving failure examples cover invalid request, access failure, quota/upstream failure, deprecated behavior, endpoint unavailable, empty success, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T052 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T053 [US3] Extend `validate_videos_list_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, malformed, and unsupported `part` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T054 [US3] Extend `validate_videos_list_arguments` to return field-specific errors for missing selector, conflicting selectors, empty selector, malformed selector, unsupported selector, and ambiguous selector values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T055 [US3] Extend `validate_videos_list_arguments` to return field-specific errors for empty, non-string, malformed, incompatible, and unsupported `pageToken`, `maxResults`, `regionCode`, and `videoCategoryId` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T056 [US3] Extend `validate_videos_list_arguments` to reject out-of-scope fields such as `q`, `uploadMode`, `body`, `media`, `rating`, `includeTranscript`, `analytics`, `recommend`, `rankResults`, `summarize`, and `enrich` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T057 [US3] Implement missing or invalid API-key access rejection for `id` and `chart` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T058 [US3] Implement missing or invalid OAuth access rejection for `myRating` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T059 [US3] Implement upstream error mapping for authentication, authorization, quota, invalid request, resource not found, unavailable endpoint, deprecated endpoint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T060 [US3] Ensure video-list result mapping preserves empty `items` as successful empty results with endpoint, quota, requested parts, selector, pagination, chart refinement, and auth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T061 [US3] Ensure video-list error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

### Refactor and Validation for User Story 3

- [X] T062 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T063 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake executor, or auth helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T064 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T065 [US3] Refactor US3 validation and error mapping for consistency with active read/list helpers while preserving videos-list-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, empty-result, quota, availability, deprecation, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T066 [P] Review `videos_list` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/contracts/videos_list.md`
- [X] T067 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/quickstart.md`
- [X] T068 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T069 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T070 Run the complete focused YT-247 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/quickstart.md`
- [X] T071 Run `ruff check .` and fix lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T072 Run full repository test suite `pytest` and fix all failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T073 Confirm `git status --short` contains only intended YT-247 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable video-list tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `videos.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `videos.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, T005, and T006 can run in parallel during setup because they inspect different files.
- T007, T008, T009, T010, and T011 can be written in parallel because they target different contract, unit, and integration test files.
- T014, T015, and T016 can be written in parallel because they target contract, unit, and integration test files.
- T033, T034, T035, and T036 can be written in parallel because they target separate metadata-oriented test files.
- T046 and T051 can run in parallel because they touch unit validation tests and contract failure examples in different files; T047, T048, T049, and T050 should be serialized because they touch the same unit-test file.
- T066, T067, T068, and T069 can run in parallel during polish because they inspect or update documentation and docstrings in different scopes.

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T015 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T016 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T033 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T034 [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T035 [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T036 [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T046 [US3] Add invalid request unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T051 [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videos_list` can execute successful direct ID, chart, and rating video-list paths through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, access, selector, pagination, and chart-refinement guidance complete.
3. Deliver US3 to harden invalid requests, access failures, empty results, quota failures, endpoint failures, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.

## Independent Test Criteria Summary

- **US1**: A valid direct ID lookup, chart lookup, and rating lookup invoke the Layer 1 wrapper once and return near-raw video-list results with endpoint, quota, selector, pagination where applicable, access, and items context.
- **US2**: Tool discovery metadata and examples disclose `videos.list`, quota cost `1`, conditional access, required `part`, selector rules, pagination rules, chart refinements, active availability, empty-result behavior, and out-of-scope behavior before invocation.
- **US3**: Invalid, unsupported, access-failed, quota-failed, unavailable, deprecated, unexpected-upstream, and empty-success cases return distinct safe outcomes with sanitized details.

## Notes

- `[P]` tasks touch different files or are inspection-only and can run in parallel.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md).
- Every Python implementation or test-helper function added or modified by these tasks must include a reStructuredText docstring before the related story checkpoint is complete.
- Final feature completion requires the focused YT-247 command, full `pytest`, and `ruff check .` to pass after final code changes.
