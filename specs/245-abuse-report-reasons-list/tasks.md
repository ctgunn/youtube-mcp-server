# Tasks: Layer 2 Tool `videoAbuseReportReasons_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/data-model.md), [contracts/videoAbuseReportReasons_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/contracts/videoAbuseReportReasons_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/plan.md`
- [X] T002 Inspect the existing Layer 1 `videoAbuseReportReasons.list` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_abuse_report_reasons.py`
- [X] T003 [P] Inspect existing localized read/list Layer 2 patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- [X] T004 [P] Inspect existing localization-family list tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect shared family placement for `video_abuse_report_reasons` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until these tasks are complete and Red checks have been observed failing for the missing `videoAbuseReportReasons_list` surface.

- [X] T007 [P] Add Red public export checks for `VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME`, `VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST`, and `build_video_abuse_report_reasons_list_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `video_abuse_report_reasons` family has a concrete Layer 2 module and list descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videoAbuseReportReasons_list` appears once with resource family `video_abuse_report_reasons` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videoAbuseReportReasons_list` is discoverable through the tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red video-abuse-report-reasons-family registration checks for `videoAbuseReportReasons_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_abuse_report_reasons_registration.py`
- [X] T012 Add shared fake wrapper and executor helpers for video abuse report reasons tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T013 Run foundational Red checks and confirm they fail for missing video abuse report reasons symbols from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Retrieve Abuse Report Reasons Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `videoAbuseReportReasons_list` with valid `part` and `hl` inputs, then receive a near-raw reason-list result with endpoint, quota, access, selected-part, localization, and returned item context.

**Independent Test**: Invoke the tool handler with `{"part": "snippet", "hl": "en"}` using a fake Layer 1 wrapper; verify one wrapper call and a result containing `endpoint: videoAbuseReportReasons.list`, `quotaCost: 1`, `requestedParts`, `localization.hl`, `auth.mode: api_key`, and returned `items`.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videoAbuseReportReasons_list` tool identity, input schema, upstream identity, quota cost 1, API-key mode, list response convention, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_video_abuse_report_reasons_list_arguments`, part splitting, localization context handling, `map_video_abuse_report_reasons_list_result`, and `build_video_abuse_report_reasons_list_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T016 [P] [US1] Add integration tests proving `videoAbuseReportReasons_list` is registered and callable through the video-abuse-report-reasons family registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_abuse_report_reasons_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videoAbuseReportReasons_list` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Create the concrete video abuse report reasons Layer 2 module with imports for `build_video_abuse_report_reasons_list_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T019 [US1] Define `VIDEO_ABUSE_REPORT_REASONS_LIST_TOOL_NAME`, `VIDEO_ABUSE_REPORT_REASONS_LIST_QUOTA_COST`, supported field constants, unsafe-detail keys, and `VIDEO_ABUSE_REPORT_REASONS_LIST_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T020 [US1] Implement `VideoAbuseReportReasonsListToolError` and safe error detail sanitization support for reason-list failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T021 [US1] Implement `validate_video_abuse_report_reasons_list_arguments` requiring non-empty `part`, non-empty `hl`, and no unsupported additional fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T022 [US1] Implement part-selection and localization helpers that preserve requested parts and `hl` without fabricating labels or translations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T023 [US1] Implement `map_video_abuse_report_reasons_list_result` to return endpoint, quota cost 1, requested parts, localization context, API-key auth context, items, and safe upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T024 [US1] Implement API-key auth context and `build_video_abuse_report_reasons_list_handler` using the Layer 1 list wrapper once per valid call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T025 [US1] Implement `build_video_abuse_report_reasons_list_contract` and `build_video_abuse_report_reasons_list_tool_descriptor` with read-only list response metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T026 [US1] Export `videoAbuseReportReasons_list` constants, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T027 [US1] Register `build_video_abuse_report_reasons_list_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T028 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper or executor helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T030 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`
- [X] T031 [US1] Refactor US1 reason-list execution code for consistency with localized read/list helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Access, and Localization Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videoAbuseReportReasons_list` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `1`, API-key access, required `part`, required `hl`, localization behavior, empty-result behavior, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videoAbuseReportReasons.list`, quota cost `1`, API-key access, required `part`, required `hl`, localization behavior, empty-success behavior, active availability, and no report-submission/moderation/policy/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T032 [P] [US2] Add contract tests for metadata text, usage notes, caveats, quota visibility, API-key visibility, localization visibility, availability state, response boundary, empty-success policy, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`
- [X] T033 [P] [US2] Add catalog contract tests confirming `videoAbuseReportReasons_list` metadata exposes quota cost 1, API-key auth, required `part`, required `hl`, and localization requirements before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T034 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videoAbuseReportReasons_list` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T035 [P] [US2] Add integration tests proving default registry metadata preserves `videoAbuseReportReasons_list` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T036 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T037 [US2] Add `VIDEO_ABUSE_REPORT_REASONS_LIST_DESCRIPTION`, `VIDEO_ABUSE_REPORT_REASONS_LIST_USAGE_NOTES`, and `VIDEO_ABUSE_REPORT_REASONS_LIST_CAVEATS` with quota cost 1, API-key access, required `part`, required `hl`, localization behavior, empty-success behavior, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T038 [US2] Add `VIDEO_ABUSE_REPORT_REASONS_LIST_CALLER_EXAMPLES` covering localized reason lookup, populated success, empty success, missing `part`, missing `hl`, invalid `part`, invalid `hl`, missing access, quota or upstream failure, and out-of-scope report-submission request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T039 [US2] Update `build_video_abuse_report_reasons_list_contract` and `build_video_abuse_report_reasons_list_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, API-key details, localization details, and empty-success policy in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T040 [US2] Update shared examples or catalog entries if required so `videoAbuseReportReasons_list` replaces any representative placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T041 [US2] Update `videoAbuseReportReasons_list` export coverage for caller-facing example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T042 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T043 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`
- [X] T044 [US2] Refactor US2 metadata and example wording for consistency with localized read/list tools while preserving quota, API-key access, required `part`, required `hl`, empty-result, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Lookup Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation, access, quota, availability, deprecation, empty-success, and unexpected-upstream outcomes that remain distinct from successful populated reason-list results.

**Independent Test**: Submit missing `part`, empty `part`, non-string `part`, missing `hl`, empty `hl`, malformed `hl`, unsupported fields, report-submission inputs, moderation instructions, policy-evaluation fields, missing API-key access, empty upstream success, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category or empty-success result and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T045 [P] [US3] Add unit validation tests for missing `part`, empty `part`, non-string `part`, malformed `part`, unsupported top-level fields, video identifier attempts, reason identifier attempts, report text attempts, paging controls, selector attempts, moderation instructions, policy-evaluation instructions, ranking modifiers, summarization modifiers, and enrichment modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T046 [US3] Add unit localization validation tests for missing `hl`, empty `hl`, non-string `hl`, whitespace `hl`, malformed `hl`, conflicting localization input, and unsupported display-language shapes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T047 [US3] Add unit handler tests for missing API-key access, invalid auth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T048 [US3] Add unit result and upstream error mapping tests for empty upstream success, quota failure, invalid request, authorization failure, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T049 [P] [US3] Add contract tests proving failure examples cover invalid request, access failure, quota/upstream failure, deprecated behavior, endpoint unavailable, empty success, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`
- [X] T050 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T051 [US3] Extend `validate_video_abuse_report_reasons_list_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, malformed, and unsupported `part` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T052 [US3] Extend `validate_video_abuse_report_reasons_list_arguments` to return field-specific errors for missing, empty, non-string, whitespace, malformed, conflicting, and unsupported `hl` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T053 [US3] Extend `validate_video_abuse_report_reasons_list_arguments` to reject out-of-scope fields such as `videoId`, `reasonId`, `reportText`, `pageToken`, `id`, `regionCode`, `moderationStatus`, `evaluatePolicy`, `rankResults`, `summarize`, and `enrich` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T054 [US3] Implement missing or invalid API-key access rejection before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T055 [US3] Implement upstream error mapping for authentication, authorization, quota, invalid request, unavailable endpoint, deprecated endpoint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T056 [US3] Ensure reason-list result mapping preserves empty `items` as successful empty results with endpoint, quota, requested parts, localization, and auth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T057 [US3] Ensure reason-list error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`

### Refactor and Validation for User Story 3

- [X] T058 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T059 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper or executor helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T060 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T061 [US3] Refactor US3 validation and error mapping for consistency with localized read/list helpers while preserving reason-list-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, empty-result, quota, availability, deprecation, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T062 [P] Review `videoAbuseReportReasons_list` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/contracts/videoAbuseReportReasons_list.md`
- [X] T063 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/quickstart.md`
- [X] T064 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`
- [X] T065 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`
- [X] T066 Run the complete focused YT-245 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/245-abuse-report-reasons-list/quickstart.md`
- [X] T067 Run `ruff check .` and fix lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T068 Run full repository test suite `pytest` and fix all failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T069 Confirm `git status --short` contains only intended YT-245 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable reason-list tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `video_abuse_report_reasons.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `video_abuse_report_reasons.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, T005, and T006 can run in parallel during setup because they inspect different files.
- T007, T008, T009, T010, and T011 can be written in parallel because they target different contract, unit, and integration test files.
- T014, T015, and T016 can be written in parallel because they target contract, unit, and integration test files.
- T032, T033, T034, and T035 can be written in parallel because they target separate metadata-oriented test files.
- T045 and T049 can run in parallel because they touch unit validation tests and contract failure examples in different files; T046, T047, and T048 should be serialized because they touch the same unit-test file.
- T062, T063, T064, and T065 can run in parallel during polish because they inspect or update documentation and docstrings in different scopes.

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py"
Task: "T015 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py"
Task: "T016 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_video_abuse_report_reasons_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T032 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py"
Task: "T033 [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T034 [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T035 [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T045 [US3] Add invalid request unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py"
Task: "T049 [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videoAbuseReportReasons_list` can execute a successful localized reason-list path through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. US1 delivers executable endpoint-backed reason-list lookup with safe success context.
2. US2 makes quota, API-key access, localization requirements, examples, empty-result behavior, and out-of-scope boundaries discoverable before invocation.
3. US3 completes invalid request, access, empty-result, quota, availability, deprecation, and upstream failure boundaries.
4. Polish runs focused tests, full `pytest`, `ruff check .`, docstring review, and final status review.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. Assign one person to US1 implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_abuse_report_reasons.py`.
3. Assign another person to US2 metadata tests and catalog assertions.
4. Assign another person to US3 validation tests, coordinating edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_video_abuse_report_reasons.py`.

## Task Summary

- **Total tasks**: 69
- **Setup tasks**: 6
- **Foundational tasks**: 7
- **User Story 1 tasks**: 18
- **User Story 2 tasks**: 13
- **User Story 3 tasks**: 17
- **Polish tasks**: 8

## Independent Test Criteria

- **US1**: Handler and registry calls with `{"part": "snippet", "hl": "en"}` return endpoint, quota, requested parts, localization, auth mode, and returned items through one Layer 1 wrapper call.
- **US2**: Tool discovery metadata, description, usage notes, caveats, and examples expose endpoint identity, quota cost `1`, API-key access, required inputs, localization, empty-success behavior, and out-of-scope boundaries before invocation.
- **US3**: Invalid, access, empty-success, quota, availability, deprecation, and upstream scenarios return deterministic safe categories or success shapes without leaking credentials or unsafe diagnostics.

## Suggested MVP Scope

Complete Phase 1, Phase 2, and Phase 3 only. This delivers the independently callable `videoAbuseReportReasons_list` lookup path before metadata polish and broad failure-boundary hardening.
