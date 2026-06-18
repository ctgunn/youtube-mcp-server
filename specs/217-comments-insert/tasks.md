# Tasks: Layer 2 Tool `comments_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/contracts/comments-insert-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/quickstart.md`

**Tests**: Test tasks are mandatory and appear before implementation in each story. Completion requires focused checks, a full `pytest` run, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently after shared foundation work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or only reads context
- **[Story]**: User story label for story phases only
- Every task includes an absolute file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation surface and feature artifacts before writing tests.

- [X] T001 Review the YT-217 implementation plan in `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/plan.md`
- [X] T002 [P] Review the public MCP contract for `comments_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/contracts/comments-insert-tool-contract.md`
- [X] T003 [P] Review the data entities and state transitions for `comments_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/data-model.md`
- [X] T004 [P] Review the existing Layer 1 `comments.insert` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`
- [X] T005 [P] Review the current Layer 2 comments family implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red checks for exports, catalog visibility, and registry discovery that all stories rely on.

**Critical**: No user story implementation should begin until these failing shared tests are in place.

- [X] T006 Add failing scaffolding checks for `COMMENTS_INSERT_TOOL_NAME`, `COMMENTS_INSERT_QUOTA_COST`, `build_comments_insert_contract`, and `build_comments_insert_tool_descriptor` exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 [P] Add failing representative catalog checks for `comments_insert` identity, quota cost 50, OAuth-required auth, and concrete-contract alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T008 [P] Add failing default registry discovery checks for `comments_insert` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T009 Add failing shared metadata safety checks for the `comments_insert` public contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T010 Run foundational Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Shared Red tests exist and fail for missing `comments_insert` exports, catalog metadata, and registry discovery.

---

## Phase 3: User Story 1 - Create Reply Comments Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `comments_insert` with eligible OAuth, supported part selection, and a valid reply body, then receive a near-raw created comment result.

**Independent Test**: Invoke the descriptor handler with `{"part": "snippet", "body": {"snippet": {"parentId": "comment-parent-123", "textOriginal": "Thanks for the feedback."}}}` and confirm the result includes `endpoint: comments.insert`, `quotaCost: 50`, `created: true`, requested parts, safe auth context, and the returned created comment item.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `comments_insert` identity, required `part`, required reply body, OAuth-required auth, response boundary, and created comment result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T012 [P] [US1] Add failing unit tests for valid reply argument validation, created comment result mapping, delegated context summary, and one-wrapper-call handler execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T013 [P] [US1] Add failing dispatcher invocation tests for executable `comments_insert` authorized reply creation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T014 [US1] Run the US1 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Add `COMMENTS_INSERT_TOOL_NAME`, `COMMENTS_INSERT_QUOTA_COST`, `COMMENTS_INSERT_INPUT_SCHEMA`, and `CommentsInsertToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T016 [US1] Implement `validate_comments_insert_arguments()` for required `part`, required `body`, required `body.snippet.parentId`, required `body.snippet.textOriginal`, and optional `onBehalfOfContentOwner` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T017 [US1] Implement `map_comments_insert_result()` for endpoint, quota cost, created status, requested parts, returned item, safe auth summary, safe delegation summary, and preserved upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T018 [US1] Implement `_comments_insert_auth_context()` using OAuth-required credentials without exposing credential values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T019 [US1] Implement `build_comments_insert_handler()` and `build_comments_insert_tool_descriptor()` using the existing Layer 1 `build_comments_insert_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T020 [US1] Export `comments_insert` constants, error type, validator, mapper, contract builder, handler builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_comments_insert_tool_descriptor()` in the default tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add reStructuredText docstrings for every new or modified `comments_insert` function, helper, and test fake method touched for US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 1

- [X] T023 [US1] Refactor US1 names and result-shape helpers to match existing mutation-tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T024 [US1] Run focused US1 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Reply Rules Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, usage notes, caveats, and examples and understand endpoint identity, quota cost 50, OAuth requirements, required part selection, parent-comment rule, reply text rule, optional delegation, response boundary, and out-of-scope workflows before invocation.

**Independent Test**: Review `comments_insert` metadata and examples from the tool descriptor and confirm all required quota, OAuth, part, parent-comment, reply-text, delegation, successful result, and unsupported workflow disclosures are visible.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing contract tests for quota cost 50, OAuth-required auth, active availability, required `part`, required `body`, required `body.snippet.parentId`, required `body.snippet.textOriginal`, optional delegation context, and response convention metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T026 [P] [US2] Add failing shared representative contract tests for `comments_insert` public metadata alignment and safety in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T027 [US2] Add failing caller example coverage for authorized reply creation, delegated owner context, missing OAuth, missing part, missing parent comment, missing reply text, unsupported top-level create shape, unsupported option, and parent-comment failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T028 [US2] Run the US2 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T029 [US2] Implement `build_comments_insert_contract()` with upstream identity, quota cost 50, OAuth-required auth, active availability, input contract, response convention, response boundary, and error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T030 [US2] Add `COMMENTS_INSERT_DESCRIPTION`, `COMMENTS_INSERT_USAGE_NOTES`, `COMMENTS_INSERT_CAVEATS`, and `COMMENTS_INSERT_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T031 [US2] Add `comments_insert` representative concrete-contract alignment to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T032 [US2] Export `COMMENTS_INSERT_DESCRIPTION`, `COMMENTS_INSERT_USAGE_NOTES`, `COMMENTS_INSERT_CAVEATS`, and `COMMENTS_INSERT_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for every metadata, contract, and representative-catalog function changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 2

- [X] T034 [US2] Refactor repeated quota, OAuth, parent-comment, reply-text, delegation, and out-of-scope wording while preserving required caller-facing text in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T035 [US2] Run focused US2 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently verifiable through public discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Reply Creation Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation or mapped upstream failure feedback for missing OAuth, missing part, missing body, missing snippet, missing parent ID, missing reply text, unsupported top-level create shapes, unsupported fields, inaccessible parent comments, quota failures, endpoint failures, and unexpected upstream failures.

**Independent Test**: Submit representative invalid requests and fake upstream failures to the handler and confirm each response uses the shared Layer 2 category with safe details and no leaked API keys, OAuth tokens, stack traces, raw request bodies, or unsafe diagnostics.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Add failing unit validation tests for missing `part`, missing `body`, missing `body.snippet`, missing `body.snippet.parentId`, blank `body.snippet.textOriginal`, unsupported top-level thread fields, unsupported update fields, unsupported moderation fields, unsupported delete fields, and unsupported extra parameters in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T037 [US3] Add failing unit tests for upstream error mapping to `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T038 [P] [US3] Add failing contract tests proving public metadata, results, and errors do not leak API keys, OAuth tokens, stack traces, raw credential payloads, or unsafe upstream diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T039 [P] [US3] Add failing dispatcher tests for missing OAuth, invalid reply body, unsupported top-level create shape, and safe failure propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T040 [US3] Run the US3 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T041 [US3] Extend `validate_comments_insert_arguments()` for unsupported body fields, read-only fields, top-level thread creation fields, update fields, moderation fields, delete fields, search instructions, automated response instructions, and unsupported optional parameters in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T042 [US3] Implement `_map_comments_insert_upstream_error()` for shared Layer 2 categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T043 [US3] Wire validation, OAuth context, upstream error mapping, and safe `ValueError` conversion into `build_comments_insert_handler()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T044 [US3] Add safe default local transport behavior for successful created comments, parent-not-found simulation, private parent simulation, disabled-reply simulation, quota failure simulation, and authorization failure simulation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T045 [US3] Add or update reStructuredText docstrings for every validator, auth helper, error mapper, default transport, and fake wrapper method changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 3

- [X] T046 [US3] Refactor `comments_insert` validation and error mapping to share safe helper patterns with `comments_list` without changing public behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T047 [US3] Run focused US3 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_insert` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional and failure behavior is caller-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation alignment, and repository-wide quality checks.

- [X] T048 [P] Verify the implementation matches quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/quickstart.md`
- [X] T049 [P] Review all changed Python functions for reStructuredText docstrings covering purpose, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, parent-comment rule, reply-content rule, mutation result, and failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T050 [P] Review public exports for stale or missing `comments_insert` symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T051 [P] Review default registry ordering and metadata for `comments_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T052 [P] Review representative catalog alignment for `comments_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T053 Run focused feature verification with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T054 Run `ruff check .` and fix any lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T055 Run the full repository test suite with `pytest` and fix any failing tests before completion from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T056 Record final focused test, full-suite, and lint evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can proceed after US1 contract/descriptor shape exists; metadata work is independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational and can proceed after US1 handler/error skeleton exists; validation work is independently testable.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Core tool execution and created comment result; no dependency on US2 or US3.
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
- Foundational tests T006, T007, T008, and T009 touch different test files and can be drafted in parallel.
- US1 Red tests T011, T012, and T013 touch different files and can be drafted in parallel.
- US2 Red tests T025 and T026 touch different files and can be drafted in parallel; T027 shares a file with T025 and should be coordinated.
- US3 Red tests T036 and T037 share one file and should be sequenced; T038 and T039 can run in parallel because they touch different files.
- Polish review tasks T048, T049, T050, T051, and T052 can run in parallel before final command tasks.

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
Task: "T039 Add dispatcher failure tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for `comments_insert` execution and created-comment results.
3. Stop and validate US1 independently with the focused insert tests.
4. Use US1 as the demoable MVP because it exposes the public tool and successful reply-creation path.

### Incremental Delivery

1. Add US1 to expose and execute the tool.
2. Add US2 to harden public metadata, caveats, and examples.
3. Add US3 to complete validation and safe upstream error behavior.
4. Finish with focused checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One contributor drafts shared export/registry tests while another drafts story-level contract tests.
2. After Foundational Red checks are in place, implementation can split by file ownership: comments module, exports/dispatcher, examples, and tests.
3. Coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` because all stories eventually modify that file.

## Independent Test Criteria Summary

- **US1**: Valid authorized reply creation returns `comments.insert` result context with quota cost 50, requested parts, created status, safe auth context, safe delegation context when supplied, and returned created comment fields.
- **US2**: Tool discovery metadata, usage notes, caveats, and examples visibly disclose upstream identity, quota cost 50, OAuth requirement, required part, parent-comment rule, reply-text rule, delegation behavior, response boundary, and out-of-scope behaviors.
- **US3**: Invalid inputs and fake upstream failures return shared safe Layer 2 categories with actionable details and no leaked API keys, OAuth tokens, stack traces, raw request bodies, or unsafe diagnostics.

## Notes

- `[P]` tasks are intentionally conservative; tasks sharing the same Python file should be coordinated even when logically independent.
- Every Python code task must preserve or add reStructuredText docstrings before the story checkpoint.
- Do not implement comment listing, top-level comment-thread creation, editing, moderation status changes, deletion, generated replies, search, sentiment, ranking, summarization, analytics, or enrichment behavior.
