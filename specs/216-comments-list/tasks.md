# Tasks: Layer 2 Tool `comments_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/contracts/comments_list.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/quickstart.md`

**Tests**: Test tasks are mandatory and appear before implementation in each story. Completion requires focused checks, a full `pytest` run, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently after shared foundation work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or only reads context
- **[Story]**: User story label for story phases only
- Every task includes an absolute file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation surface and feature artifacts before writing tests.

- [X] T001 Review the YT-216 plan and implementation structure in `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/plan.md`
- [X] T002 [P] Review the public interface contract for `comments_list` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/contracts/comments_list.md`
- [X] T003 [P] Review the existing Layer 1 `comments.list` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`
- [X] T004 [P] Review existing Layer 2 list-tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T005 [P] Review existing Layer 2 list-tool registration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red checks and module scaffolding that all stories rely on.

**Critical**: No user story implementation should begin until these failing shared tests are in place.

- [X] T006 Add failing scaffolding checks for `COMMENTS_LIST_TOOL_NAME`, `COMMENTS_LIST_QUOTA_COST`, and `build_comments_list_tool_descriptor` exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 [P] Add failing representative metadata coverage for `build_comments_list_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add failing default registry discovery check for `comments_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T009 Run the shared Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_list` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T010 Add the empty comments Layer 2 module shell and module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

**Checkpoint**: Shared Red tests exist and fail for missing `comments_list` support, and the resource-family module exists for story implementation.

---

## Phase 3: User Story 1 - Retrieve Comments Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `comments_list` with `part` and exactly one supported selector, then receive a near-raw comment list result with operation context.

**Independent Test**: Invoke the descriptor handler with `{"part": "id,snippet", "id": "comment-123"}` and `{"part": "snippet", "parentId": "comment-parent-123"}`, then confirm each result includes `endpoint: comments.list`, `quotaCost: 1`, requested parts, selector context, and returned comment items.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `comments_list` identity, required `part`, `id` selector, `parentId` selector, response boundary, and list result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T012 [P] [US1] Add failing unit tests for successful ID result mapping, parent reply result mapping, empty collection success, and one-wrapper-call handler execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T013 [P] [US1] Add failing dispatcher invocation tests for default `comments_list` ID lookup and parent reply lookup in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T014 [US1] Run the US1 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k list` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Add `COMMENTS_LIST_TOOL_NAME`, `COMMENTS_LIST_QUOTA_COST`, `COMMENTS_LIST_INPUT_SCHEMA`, and `CommentsListToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T016 [US1] Implement `build_comments_list_contract()` and list response-boundary metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T017 [US1] Implement `map_comments_list_result()` for comment items, requested parts, selected retrieval mode, text-format context, `kind`, `etag`, `nextPageToken`, and `pageInfo` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T018 [US1] Implement `validate_comments_list_arguments()` for required `part`, exactly one selector, non-empty `id`, and non-empty `parentId` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T019 [US1] Implement `build_comments_list_handler()` and `build_comments_list_tool_descriptor()` using the existing Layer 1 `build_comments_list_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T020 [US1] Export `comments_list` constants, error type, validator, mapper, contract builder, handler builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_comments_list_tool_descriptor()` in the default tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add reStructuredText docstrings for every new or modified `comments_list` function, helper, and test fake method touched for US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 1

- [X] T023 [US1] Refactor the US1 implementation for naming consistency with existing list tools in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T024 [US1] Run focused US1 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k list` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Auth, and Lookup Modes Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, usage notes, caveats, and examples and understand endpoint identity, quota cost 1, auth/access expectations, required `part`, supported selectors, pagination rules, text-format behavior, and out-of-scope workflows before invocation.

**Independent Test**: Review `comments_list` metadata and examples from the tool descriptor and confirm all required quota, auth, selector, pagination, text-format, no-body, empty-result, and out-of-scope workflow disclosures are visible.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing contract tests for quota, mixed auth disclosure, required `part`, selector rules, pagination restrictions, `textFormat`, empty-result policy, and out-of-scope workflow disclosures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T026 [P] [US2] Add failing shared representative contract test for safe `comments_list` public metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T027 [US2] Add failing caller example coverage for ID lookup, parent reply lookup, paginated parent lookup, plain-text lookup, empty success, missing selector, conflicting selectors, invalid ID, unsupported option, and access-sensitive failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T028 [US2] Run the US2 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_list` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T029 [US2] Add `COMMENTS_LIST_DESCRIPTION`, `COMMENTS_LIST_USAGE_NOTES`, `COMMENTS_LIST_CAVEATS`, and `COMMENTS_LIST_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T030 [US2] Populate `comments_list` response convention and metadata fields for quota, mixed auth, availability, selectors, pagination restrictions, text-format values, empty-result policy, and disallowed workflows in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T031 [US2] Add `comments_list` to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` imports and tuple in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T032 [US2] Export `COMMENTS_LIST_DESCRIPTION`, `COMMENTS_LIST_USAGE_NOTES`, `COMMENTS_LIST_CAVEATS`, and `COMMENTS_LIST_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for metadata and example helper functions changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 2

- [X] T034 [US2] Refactor repeated quota, auth, selector, pagination, and caveat wording while preserving required caller-facing text in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T035 [US2] Run focused US2 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_list` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently verifiable through public discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Comment List Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation or mapped upstream failure feedback for missing `part`, missing selectors, conflicting selectors, invalid identifiers, unsupported pagination with `id`, invalid page sizes, invalid text formats, unsupported options, access failures, not-found responses, quota failures, unavailable endpoints, deprecation, and unexpected upstream failures.

**Independent Test**: Submit representative invalid requests and fake upstream failures to the handler and confirm each response uses the shared Layer 2 category with safe details and no leaked API keys, OAuth tokens, stack traces, or raw unsafe diagnostics.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Add failing unit validation tests for missing `part`, missing selector, combined selectors, empty `id`, empty `parentId`, unsupported `maxResults` with `id`, unsupported `pageToken` with `id`, invalid page size, invalid `textFormat`, and request body fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T037 [US3] Add failing unit tests for upstream error mapping to `invalid_request`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T038 [P] [US3] Add failing contract test proving public errors and results do not leak API keys, OAuth tokens, stack traces, or raw unsafe diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T039 [US3] Run the US3 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py -k list` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T040 [US3] Extend `validate_comments_list_arguments()` for pagination restrictions, page-size bounds, text-format values, unsupported fields, and selector-specific validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T041 [US3] Implement `_comments_list_auth_context()` or equivalent auth helper for API-key and access-sensitive retrieval context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T042 [US3] Implement `_map_comments_list_upstream_error()` for shared Layer 2 categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T043 [US3] Wire validation, auth context, and upstream error mapping into `build_comments_list_handler()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T044 [US3] Add or update reStructuredText docstrings for every validator, auth helper, error mapper, and fake wrapper method changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 3

- [X] T045 [US3] Refactor comment-list validation and error mapping to avoid duplicating unrelated list-tool logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T046 [US3] Run focused US3 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py -k list` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional and failure behavior is caller-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation alignment, and repository-wide quality checks.

- [X] T047 [P] Verify the implementation matches quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/quickstart.md`
- [X] T048 [P] Review all changed Python functions for reStructuredText docstrings covering purpose, inputs, outputs, quota cost, auth behavior, selector rules, pagination behavior, text-format behavior, no-match behavior, and result shape in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T049 [P] Review public exports for stale or missing `comments_list` symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T050 [P] Review default registry ordering and metadata for `comments_list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T051 Run focused feature verification with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T052 Run `ruff check .` and fix any lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T053 Run the full repository test suite with `pytest` and fix any failing tests before completion from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T054 Record final focused test, full-suite, and lint evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can proceed after US1 contract builder exists; metadata work is independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational and can proceed after US1 handler skeleton exists; validation work is independently testable.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Core tool execution and comment list result; no dependency on US2 or US3.
- **US2 (P2)**: Metadata and examples; relies on the contract/descriptor shape created by US1 but can be reviewed independently through discovery metadata.
- **US3 (P3)**: Validation and error handling; relies on the handler and error type created by US1 but can be tested independently through invalid requests and fake upstream failures.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation must be the smallest endpoint-backed code needed to satisfy that story.
- reStructuredText docstrings must be complete before story completion.
- Refactor tasks must preserve behavior and rerun focused tests.
- The feature is not complete until full `pytest` and `ruff check .` pass.

## Parallel Opportunities

- Setup tasks T002, T003, T004, and T005 can run in parallel because they only read different files.
- Foundational tests T006, T007, and T008 touch different test files and can be drafted in parallel.
- US1 Red tests T011, T012, and T013 touch different files and can be drafted in parallel.
- US2 Red tests T025 and T026 touch different files and can be drafted in parallel; T027 shares a file with T025 and should be coordinated.
- US3 Red tests T036 and T037 share one file and should be sequenced; T038 can run in parallel in the contract test file if coordinated with US2 edits.
- Polish review tasks T047, T048, T049, and T050 can run in parallel before final command tasks.

## Parallel Example: User Story 1

```bash
Task: "T011 Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
Task: "T012 Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py"
Task: "T013 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T025 Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
Task: "T026 Add representative metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T036 Add invalid-request validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py"
Task: "T038 Add no-leak contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for `comments_list` execution and comment-list results.
3. Stop and validate US1 independently with the focused list tests.
4. Use US1 as the demoable MVP because it exposes the public tool and successful retrieval paths.

### Incremental Delivery

1. Add US1 to expose and execute the tool.
2. Add US2 to harden public metadata, caveats, and examples.
3. Add US3 to complete validation and safe upstream error behavior.
4. Finish with focused checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One contributor drafts shared export/registry tests while another drafts story-level contract tests.
2. After Foundational Red checks are in place, implementation can split by file ownership: comments module, exports/dispatcher, and tests.
3. Coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` because all stories eventually modify that file.

## Independent Test Criteria Summary

- **US1**: Valid `id` and `parentId` retrieval requests return `comments.list` results with quota cost 1, requested parts, selector context, text-format context, and returned comment collection fields.
- **US2**: Tool discovery metadata, usage notes, caveats, and examples visibly disclose upstream identity, quota cost 1, auth/access expectations, required `part`, selector rules, pagination restrictions, text-format behavior, empty-result policy, and out-of-scope behaviors.
- **US3**: Invalid inputs and fake upstream failures return shared safe Layer 2 categories with actionable details and no leaked API keys, OAuth tokens, stack traces, or unsafe diagnostics.

## Notes

- `[P]` tasks are intentionally conservative; tasks sharing the same Python file should be coordinated even when logically independent.
- Every Python code task must preserve or add reStructuredText docstrings before the story checkpoint.
- Do not implement comment-thread discovery, reply creation, editing, moderation status changes, deletion, search, sentiment, ranking, summarization, analytics, or enrichment behavior.
