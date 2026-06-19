# Tasks: Layer 2 Tool `comments_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/contracts/comments-update-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/quickstart.md`

**Tests**: Test tasks are mandatory and appear before implementation in each story. Completion requires focused checks, a full `pytest` run, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently after shared foundation work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or only reads context
- **[Story]**: User story label for story phases only
- Every task includes an absolute file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation surface and feature artifacts before writing tests.

- [X] T001 Review the YT-218 implementation plan in `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/plan.md`
- [X] T002 [P] Review the public MCP contract for `comments_update` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/contracts/comments-update-tool-contract.md`
- [X] T003 [P] Review the data entities and state transitions for `comments_update` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/data-model.md`
- [X] T004 [P] Review the existing Layer 1 `comments.update` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`
- [X] T005 [P] Review the current Layer 2 comments family implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red checks for exports, catalog visibility, and registry discovery that all stories rely on.

**Critical**: No user story implementation should begin until these failing shared tests are in place.

- [X] T006 Add failing scaffolding checks for `COMMENTS_UPDATE_TOOL_NAME`, `COMMENTS_UPDATE_QUOTA_COST`, `build_comments_update_contract`, and `build_comments_update_tool_descriptor` exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 [P] Add failing representative catalog checks for `comments_update` identity, quota cost 50, OAuth-required auth, updated-resource convention, and concrete-contract alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T008 [P] Add failing default registry discovery checks for `comments_update` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T009 Add failing shared metadata safety checks for the `comments_update` public contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T010 Run foundational Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Shared Red tests exist and fail for missing `comments_update` exports, catalog metadata, and registry discovery.

---

## Phase 3: User Story 1 - Update Existing Comments Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `comments_update` with eligible OAuth, supported part selection, and a valid update body, then receive a near-raw updated comment result.

**Independent Test**: Invoke the descriptor handler with `{"part": "snippet", "body": {"id": "comment-123", "snippet": {"textOriginal": "Updated comment text."}}}` and confirm the result includes `endpoint: comments.update`, `quotaCost: 50`, `updated: true`, requested parts, writable-field context, safe auth context, and the returned updated comment item.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `comments_update` identity, required `part`, required update body, OAuth-required auth, response boundary, and updated comment result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T012 [P] [US1] Add failing unit tests for valid update argument validation, updated comment result mapping, delegated context summary, and one-wrapper-call handler execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T013 [P] [US1] Add failing dispatcher invocation tests for executable `comments_update` authorized comment editing in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T014 [US1] Run the US1 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Add `COMMENTS_UPDATE_TOOL_NAME`, `COMMENTS_UPDATE_QUOTA_COST`, `COMMENTS_UPDATE_INPUT_SCHEMA`, and `CommentsUpdateToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T016 [US1] Implement `validate_comments_update_arguments()` for required `part`, required `body`, required `body.id`, required `body.snippet.textOriginal`, supported `snippet` part, and optional `onBehalfOfContentOwner` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T017 [US1] Implement `map_comments_update_result()` for endpoint, quota cost, updated status, requested parts, writable-field context, returned item, safe auth summary, safe delegation summary, and preserved upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T018 [US1] Implement `_comments_update_auth_context()` using OAuth-required credentials without exposing credential values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T019 [US1] Implement `build_comments_update_handler()` and `build_comments_update_tool_descriptor()` using the existing Layer 1 `build_comments_update_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T020 [US1] Export `comments_update` constants, error type, validator, mapper, contract builder, handler builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_comments_update_tool_descriptor()` in the default tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add reStructuredText docstrings for every new or modified `comments_update` function, helper, and test fake method touched for US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 1

- [X] T023 [US1] Refactor US1 names and updated-resource result helpers to match existing mutation-tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T024 [US1] Run focused US1 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Writable Fields Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, usage notes, caveats, and examples and understand endpoint identity, quota cost 50, OAuth requirements, required part selection, target-comment rule, writable text rule, optional delegation, response boundary, read-only field caveats, and out-of-scope workflows before invocation.

**Independent Test**: Review `comments_update` metadata and examples from the tool descriptor and confirm all required quota, OAuth, part, target-comment, writable-text, read-only-field, delegation, successful result, and unsupported workflow disclosures are visible.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing contract tests for quota cost 50, OAuth-required auth, active availability, required `part`, required `body`, required `body.id`, required `body.snippet.textOriginal`, optional delegation context, writable-field guidance, and response convention metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T026 [P] [US2] Add failing shared representative contract tests for `comments_update` public metadata alignment and safety in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T027 [US2] Add failing caller example coverage for authorized comment update, delegated owner context, missing OAuth, missing part, missing target comment ID, missing updated text, unsupported writable part, read-only field failure, unsupported option, and target-comment failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T028 [US2] Run the US2 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T029 [US2] Implement `build_comments_update_contract()` with upstream identity, quota cost 50, OAuth-required auth, active availability, input contract, response convention, response boundary, writable-field convention, and error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T030 [US2] Add `COMMENTS_UPDATE_DESCRIPTION`, `COMMENTS_UPDATE_USAGE_NOTES`, `COMMENTS_UPDATE_CAVEATS`, and `COMMENTS_UPDATE_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T031 [US2] Add `comments_update` representative concrete-contract alignment to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T032 [US2] Export `COMMENTS_UPDATE_DESCRIPTION`, `COMMENTS_UPDATE_USAGE_NOTES`, `COMMENTS_UPDATE_CAVEATS`, and `COMMENTS_UPDATE_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for every metadata, contract, and representative-catalog function changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 2

- [X] T034 [US2] Refactor repeated quota, OAuth, target-comment, writable-text, read-only-field, delegation, and out-of-scope wording while preserving required caller-facing text in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T035 [US2] Run focused US2 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently verifiable through public discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Comment Update Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation or mapped upstream failure feedback for missing OAuth, missing part, missing body, missing comment ID, missing snippet, missing updated text, unsupported writable parts, read-only fields, inaccessible target comments, quota failures, endpoint failures, and unexpected upstream failures.

**Independent Test**: Submit representative invalid requests and fake upstream failures to the handler and confirm each response uses the shared Layer 2 category with safe details and no leaked API keys, OAuth tokens, stack traces, raw request bodies, or unsafe diagnostics.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Add failing unit validation tests for missing `part`, missing `body`, missing `body.id`, missing `body.snippet`, blank `body.snippet.textOriginal`, unsupported parts, read-only snippet fields, immutable parent fields, moderation fields, deletion fields, listing fields, search fields, and unsupported extra parameters in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T037 [US3] Add failing unit tests for upstream error mapping to `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T038 [P] [US3] Add failing contract tests proving public metadata, results, and errors do not leak API keys, OAuth tokens, stack traces, raw credential payloads, raw request bodies, or unsafe upstream diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T039 [P] [US3] Add failing dispatcher tests for missing OAuth, invalid update body, unsupported writable part, read-only field update, missing target comment, and safe failure propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T040 [US3] Run the US3 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T041 [US3] Extend `validate_comments_update_arguments()` for unsupported body fields, read-only fields, immutable parent relationships, insert-only fields, moderation fields, delete fields, list/search fields, generated rewrite instructions, and unsupported optional parameters in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T042 [US3] Implement `_map_comments_update_upstream_error()` for shared Layer 2 categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T043 [US3] Wire validation, OAuth context, upstream error mapping, and safe `ValueError` conversion into `build_comments_update_handler()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T044 [US3] Add safe default local transport behavior for successful updated comments, target-not-found simulation, inaccessible target simulation, ineligible-account simulation, quota failure simulation, and authorization failure simulation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T045 [US3] Add or update reStructuredText docstrings for every validator, auth helper, error mapper, default transport, and fake wrapper method changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 3

- [X] T046 [US3] Refactor `comments_update` validation and error mapping to share safe helper patterns with `comments_list` and `comments_insert` without changing public behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T047 [US3] Run focused US3 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py -k comments_update` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional and failure behavior is caller-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation alignment, and repository-wide quality checks.

- [X] T048 [P] Verify the implementation matches quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/quickstart.md`
- [X] T049 [P] Review all changed Python functions for reStructuredText docstrings covering purpose, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, target-comment rule, writable-field boundary, mutation result, and failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T050 [P] Review public exports for stale or missing `comments_update` symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T051 [P] Review default registry ordering and metadata for `comments_update` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T052 [P] Review representative catalog alignment for `comments_update` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T053 Run focused feature verification with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T054 Run `ruff check .` and fix any lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T055 Run the full repository test suite with `pytest` and fix any failing tests before completion from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T056 Record final focused test, full-suite, and lint evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/218-comments-update/quickstart.md`

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

- **US1 (P1)**: Core tool execution and updated comment result; no dependency on US2 or US3.
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
2. Complete Phase 3 for `comments_update` execution and updated-comment results.
3. Stop and validate US1 independently with the focused update tests.
4. Use US1 as the demoable MVP because it exposes the public tool and successful comment-edit path.

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

- **US1**: Valid authorized comment update returns `comments.update` result context with quota cost 50, requested parts, updated status, writable-field context, safe auth context, safe delegation context when supplied, and returned updated comment fields.
- **US2**: Tool discovery metadata, usage notes, caveats, and examples visibly disclose upstream identity, quota cost 50, OAuth requirement, required part, target-comment rule, writable-text rule, read-only-field boundary, delegation behavior, response boundary, and out-of-scope behaviors.
- **US3**: Invalid inputs and fake upstream failures return shared safe Layer 2 categories with actionable details and no leaked API keys, OAuth tokens, stack traces, raw request bodies, or unsafe diagnostics.

## Notes

- `[P]` tasks are intentionally conservative; tasks sharing the same Python file should be coordinated even when logically independent.
- Every Python code task must preserve or add reStructuredText docstrings before the story checkpoint.
- Do not implement comment listing, reply creation, top-level comment-thread creation, moderation status changes, deletion, generated rewrites, search, sentiment, ranking, summarization, analytics, or enrichment behavior.
