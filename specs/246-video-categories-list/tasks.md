# Tasks: Layer 2 Tool `videoCategories_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/data-model.md), [contracts/videoCategories_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/contracts/videoCategories_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/plan.md`
- [X] T002 Inspect the existing Layer 1 `videoCategories.list` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_categories.py`
- [X] T003 [P] Inspect existing active category and selector patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T004 [P] Inspect existing localized read/list tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect shared family placement for `video_categories` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing `videoCategories_list` surface.

- [X] T007 [P] Add Red public export checks for `VIDEO_CATEGORIES_LIST_TOOL_NAME`, `VIDEO_CATEGORIES_LIST_QUOTA_COST`, and `build_video_categories_list_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `video_categories` family has a concrete Layer 2 module and list descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videoCategories_list` appears once with resource family `video_categories` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videoCategories_list` is discoverable through the tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red video-categories-family registration checks for `videoCategories_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_categories_registration.py`
- [X] T012 Add shared fake wrapper and executor helpers for video categories tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T013 Run foundational Red checks and confirm they fail for missing video categories symbols from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Retrieve Video Categories Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `videoCategories_list` with valid `part` and exactly one selector, then receive a near-raw category-list result with endpoint, quota, access, selected-part, selector, localization, and returned item context.

**Independent Test**: Invoke the tool handler with `{"part": "snippet", "regionCode": "US"}` and `{"part": "snippet", "id": "10"}` using a fake Layer 1 wrapper; verify one wrapper call and a result containing `endpoint: videoCategories.list`, `quotaCost: 1`, `requestedParts`, `selector`, `auth.mode: api_key`, and returned `items`.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videoCategories_list` tool identity, input schema, upstream identity, quota cost 1, API-key mode, active availability, list response convention, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_video_categories_list_arguments`, part splitting, selector extraction, optional localization handling, `map_video_categories_list_result`, and `build_video_categories_list_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T016 [P] [US1] Add integration tests proving `videoCategories_list` is registered and callable through the video-categories family registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_categories_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videoCategories_list` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Create the concrete video categories Layer 2 module with imports for `build_video_categories_list_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T019 [US1] Define `VIDEO_CATEGORIES_LIST_TOOL_NAME`, `VIDEO_CATEGORIES_LIST_QUOTA_COST`, selector constants, supported field constants, unsafe-detail keys, and `VIDEO_CATEGORIES_LIST_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T020 [US1] Implement `VideoCategoriesListToolError` and safe error detail sanitization support for category-list failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T021 [US1] Implement `validate_video_categories_list_arguments` requiring non-empty `part`, exactly one selector from `id` or `regionCode`, optional valid `hl`, and no unsupported additional fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T022 [US1] Implement part-selection, category-ID selector, region selector, and localization helpers that preserve caller context without fabricating labels or translations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T023 [US1] Implement `map_video_categories_list_result` to return endpoint, quota cost 1, requested parts, selector context, optional localization context, API-key auth context, items, active availability, and safe upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T024 [US1] Implement API-key auth context and `build_video_categories_list_handler` using the Layer 1 list wrapper once per valid call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T025 [US1] Implement `build_video_categories_list_contract` and `build_video_categories_list_tool_descriptor` with read-only active list response metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T026 [US1] Export `videoCategories_list` constants, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T027 [US1] Register `build_video_categories_list_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T028 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper or executor helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T030 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`
- [X] T031 [US1] Refactor US1 category-list execution code for consistency with active read/list helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Access, Selectors, and Localization Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videoCategories_list` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `1`, API-key access, required `part`, exactly-one-selector behavior, optional `hl`, empty-result behavior, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videoCategories.list`, quota cost `1`, API-key access, required `part`, `id` and `regionCode` selector guidance, optional `hl`, empty-success behavior, active availability, and no search/recommendation/analytics/ranking/summarization/enrichment/classification behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T032 [P] [US2] Add contract tests for metadata text, usage notes, caveats, quota visibility, API-key visibility, selector visibility, localization visibility, availability state, response boundary, empty-success policy, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`
- [X] T033 [P] [US2] Add catalog contract tests confirming `videoCategories_list` metadata exposes quota cost 1, API-key auth, required `part`, exactly-one-selector behavior, optional `hl`, and active availability before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T034 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videoCategories_list` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T035 [P] [US2] Add integration tests proving default registry metadata preserves `videoCategories_list` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T036 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T037 [US2] Add `VIDEO_CATEGORIES_LIST_DESCRIPTION`, `VIDEO_CATEGORIES_LIST_USAGE_NOTES`, and `VIDEO_CATEGORIES_LIST_CAVEATS` with quota cost 1, API-key access, required `part`, selector behavior, region behavior, ID behavior, optional `hl`, empty-success behavior, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T038 [US2] Add `VIDEO_CATEGORIES_LIST_CALLER_EXAMPLES` covering region lookup, category-ID lookup, localized lookup, populated success, empty success, missing `part`, missing selector, conflicting selectors, invalid `hl`, missing access, quota or upstream failure, and out-of-scope category-analysis request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T039 [US2] Update `build_video_categories_list_contract` and `build_video_categories_list_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, API-key details, selector details, localization details, and empty-success policy in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T040 [US2] Update shared examples or catalog entries if required so `videoCategories_list` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T041 [US2] Update `videoCategories_list` export coverage for caller-facing example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T042 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T043 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`
- [X] T044 [US2] Refactor US2 metadata and example wording for consistency with active read/list tools while preserving quota, API-key access, required `part`, selector, `hl`, empty-result, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Category Lookup Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation, access, quota, availability, deprecation, empty-success, and unexpected-upstream outcomes that remain distinct from successful populated category-list results.

**Independent Test**: Submit missing `part`, empty `part`, non-string `part`, missing selector, conflicting selectors, malformed `regionCode`, empty `id`, invalid `hl`, unsupported fields, search inputs, video identifiers, channel identifiers, analytics instructions, classification instructions, missing API-key access, empty upstream success, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category or empty-success result and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T045 [P] [US3] Add unit validation tests for missing `part`, empty `part`, non-string `part`, malformed `part`, unsupported top-level fields, paging controls, ordering controls, search text, video identifiers, channel identifiers, analytics instructions, classification instructions, ranking modifiers, summarization modifiers, and enrichment modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T046 [US3] Add unit selector validation tests for missing selector, both `id` and `regionCode`, empty `id`, malformed `id`, malformed `regionCode`, unsupported selector shape, and ambiguous selector values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T047 [US3] Add unit localization validation tests for empty `hl`, non-string `hl`, whitespace `hl`, malformed `hl`, conflicting localization input, and unsupported display-language shapes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T048 [US3] Add unit handler tests for missing API-key access, invalid auth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T049 [US3] Add unit result and upstream error mapping tests for empty upstream success, resource not found, quota failure, invalid request, authorization failure, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T050 [P] [US3] Add contract tests proving failure examples cover invalid request, access failure, quota/upstream failure, deprecated behavior, endpoint unavailable, empty success, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`
- [X] T051 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T052 [US3] Extend `validate_video_categories_list_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, malformed, and unsupported `part` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T053 [US3] Extend `validate_video_categories_list_arguments` to return field-specific errors for missing selector, conflicting selectors, empty selector, malformed selector, unsupported selector, and ambiguous selector values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T054 [US3] Extend `validate_video_categories_list_arguments` to return field-specific errors for empty, non-string, whitespace, malformed, conflicting, and unsupported `hl` inputs when supplied in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T055 [US3] Extend `validate_video_categories_list_arguments` to reject out-of-scope fields such as `pageToken`, `order`, `q`, `videoId`, `channelId`, `analytics`, `classifyVideo`, `rankResults`, `summarize`, and `enrich` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T056 [US3] Implement missing or invalid API-key access rejection before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T057 [US3] Implement upstream error mapping for authentication, authorization, quota, invalid request, resource not found, unavailable endpoint, deprecated endpoint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T058 [US3] Ensure category-list result mapping preserves empty `items` as successful empty results with endpoint, quota, requested parts, selector, optional localization, and auth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T059 [US3] Ensure category-list error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`

### Refactor and Validation for User Story 3

- [X] T060 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T061 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper or executor helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T062 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T063 [US3] Refactor US3 validation and error mapping for consistency with active read/list helpers while preserving category-list-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, empty-result, quota, availability, deprecation, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T064 [P] Review `videoCategories_list` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/contracts/videoCategories_list.md`
- [X] T065 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/quickstart.md`
- [X] T066 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- [X] T067 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py`
- [X] T068 Run the complete focused YT-246 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/quickstart.md`
- [X] T069 Run `ruff check .` and fix lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T070 Run full repository test suite `pytest` and fix all failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T071 Confirm `git status --short` contains only intended YT-246 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable category-list tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `video_categories.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `video_categories.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, T005, and T006 can run in parallel during setup because they inspect different files.
- T007, T008, T009, T010, and T011 can be written in parallel because they target different contract, unit, and integration test files.
- T014, T015, and T016 can be written in parallel because they target contract, unit, and integration test files.
- T032, T033, T034, and T035 can be written in parallel because they target separate metadata-oriented test files.
- T045 and T050 can run in parallel because they touch unit validation tests and contract failure examples in different files; T046, T047, T048, and T049 should be serialized because they touch the same unit-test file.
- T064, T065, T066, and T067 can run in parallel during polish because they inspect or update documentation and docstrings in different scopes.

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py"
Task: "T015 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py"
Task: "T016 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_categories_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T032 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py"
Task: "T033 [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T034 [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T035 [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T045 [US3] Add invalid request unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_categories.py"
Task: "T050 [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videoCategories_list` can execute successful region, ID, and localized category-list paths through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, access, selector, and localization guidance complete.
3. Deliver US3 to harden invalid requests, access failures, empty results, quota failures, endpoint failures, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.

## Independent Test Criteria Summary

- **US1**: A valid region lookup, category-ID lookup, and localized lookup invoke the Layer 1 wrapper once and return near-raw category-list results with endpoint, quota, selector, localization, access, and items context.
- **US2**: Tool discovery metadata and examples disclose `videoCategories.list`, quota cost `1`, API-key access, required `part`, selector rules, optional `hl`, active availability, empty-result behavior, and out-of-scope behavior before invocation.
- **US3**: Invalid, unsupported, access-failed, quota-failed, unavailable, deprecated, unexpected-upstream, and empty-success cases return distinct safe outcomes with sanitized details.

## Notes

- `[P]` tasks touch different files or are inspection-only and can run in parallel.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md).
- Every Python implementation or test-helper function added or modified by these tasks must include a reStructuredText docstring before the related story checkpoint is complete.
- Final feature completion requires the focused YT-246 command, full `pytest`, and `ruff check .` to pass after final code changes.
