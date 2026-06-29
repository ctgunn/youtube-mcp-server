# Tasks: Layer 2 Tool `commentThreads_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/data-model.md), [contracts/commentThreads_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/contracts/commentThreads_insert.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/quickstart.md)

**Tests**: Test tasks are mandatory. Each user story starts with Red tests that must fail before Green implementation. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include reStructuredText docstring work for every new or modified function.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm local context, existing files, and feature scope before writing tests or implementation.

- [X] T001 Review YT-222 feature artifacts in /Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md
- [X] T002 [P] Inspect existing Layer 2 comment-thread module in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T003 [P] Inspect existing Layer 1 comment-thread insert wrapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py
- [X] T004 [P] Inspect existing comment-thread tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing coverage for exports, catalog registration, and contract discovery before user-story implementation.

**CRITICAL**: No user story implementation should begin until these Red tests are added and observed failing for missing `commentThreads_insert` Layer 2 support.

- [X] T005 [P] Add failing scaffold/export assertions for `COMMENT_THREADS_INSERT_*` symbols in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T006 [P] Add failing shared metadata assertions for `commentThreads_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T007 [P] Add failing default tool catalog assertions for `commentThreads_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 [P] Add failing default dispatcher registration assertions for `commentThreads_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T009 Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py -k commentThreads_insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm the new Red tests fail for missing implementation

**Checkpoint**: Shared Red coverage exists for public exports, discovery metadata, and default registration.

---

## Phase 3: User Story 1 - Create Top-Level Comment Threads Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `commentThreads_insert` with eligible OAuth, `part`, channel/video target context, and top-level comment text, then receive a near-raw created comment-thread result.

**Independent Test**: Invoke the descriptor handler from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py with a valid top-level create body and fake OAuth token, then verify one Layer 1 insert call, quota cost 50, created status, requested parts, safe auth context, target context, and returned item fields.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract test for `commentThreads_insert` identity, quota, OAuth auth, schema, and successful result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py
- [X] T011 [P] [US1] Add failing unit tests for accepted top-level create arguments and result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py
- [X] T012 [P] [US1] Add failing integration test for registering and executing `commentThreads_insert` through a dispatcher in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py
- [X] T013 [US1] Run `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py -k insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm the US1 Red tests fail

### Implementation for User Story 1 (Green)

- [X] T014 [US1] Add `COMMENT_THREADS_INSERT_TOOL_NAME`, `COMMENT_THREADS_INSERT_QUOTA_COST`, `COMMENT_THREADS_INSERT_INPUT_SCHEMA`, and success-oriented schema constants in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T015 [US1] Add `CommentThreadsInsertToolError`, accepted argument validation, requested-part normalization, target extraction, and OAuth auth-context helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T016 [US1] Add default insert transport, default executor handling, result mapper, handler builder, and descriptor builder for successful `commentThreads_insert` calls in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T017 [US1] Export `commentThreads_insert` constants, error type, contract builder, handler builder, descriptor builder, result mapper, and validator from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T018 [US1] Register `build_comment_threads_insert_tool_descriptor()` in the default dispatcher baseline list in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T019 [US1] Add or update reStructuredText docstrings for all new or modified `commentThreads_insert` functions and nested test fake methods in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py
- [X] T020 [US1] Run `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py -k insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm US1 tests pass

### Refactor for User Story 1

- [X] T021 [US1] Refactor success-path helpers for cohesion with existing `commentThreads_list` helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py while keeping US1 tests green

**Checkpoint**: User Story 1 is independently functional as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Top-Level Comment Rules Before Calling (Priority: P2)

**Goal**: A client developer can discover `commentThreads_insert` and understand endpoint identity, 50-unit quota cost, OAuth requirement, required body shape, delegation, and out-of-scope boundaries before invocation.

**Independent Test**: Inspect the tool contract, descriptor metadata, usage notes, caveats, and caller examples, then verify they expose `commentThreads.insert`, quota 50, OAuth-required auth, required `part`, required channel/video/top-level text fields, delegated owner context, and reply/list/moderation exclusions.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing metadata and usage-note contract tests for `commentThreads_insert` quota, OAuth, required body fields, delegation, response boundary, and exclusions in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py
- [X] T023 [P] [US2] Add failing shared metadata coverage for `commentThreads_insert` examples and safe public metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T024 [P] [US2] Add failing catalog and representative-example coverage for `commentThreads_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T025 [US2] Run `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py -k commentThreads_insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm the US2 Red tests fail

### Implementation for User Story 2 (Green)

- [X] T026 [US2] Add `COMMENT_THREADS_INSERT_DESCRIPTION`, `COMMENT_THREADS_INSERT_USAGE_NOTES`, `COMMENT_THREADS_INSERT_CAVEATS`, and `COMMENT_THREADS_INSERT_CALLER_EXAMPLES` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T027 [US2] Add `build_comment_threads_insert_contract()` with mutation response convention, near-raw response boundary, OAuth metadata, quota metadata, safe caveats, and example-ready usage notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T028 [US2] Add `commentThreads_insert` representative contract registration if required by existing coverage in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T029 [US2] Export US2 metadata constants and `build_comment_threads_insert_contract()` from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T030 [US2] Add or update reStructuredText docstrings for metadata/contract/example functions changed for US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T031 [US2] Run `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py -k commentThreads_insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm US2 tests pass

### Refactor for User Story 2

- [X] T032 [US2] Refactor duplicated metadata text while preserving explicit quota, OAuth, body-shape, delegation, and out-of-scope language in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Reject Unsupported Thread Creation Requests Clearly (Priority: P3)

**Goal**: A caller receives clear safe errors for missing OAuth, missing required create fields, invalid target context, unsupported reply/list/update/moderation/delete shapes, and upstream failures.

**Independent Test**: Submit invalid requests and fake upstream failures through the `commentThreads_insert` descriptor handler, then verify safe categories and details for validation, authentication, authorization, missing resources, disabled comments, quota, endpoint unavailable, deprecated endpoint, and unexpected failures without leaking credentials or raw diagnostics.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add failing unit validation tests for missing `part`, missing `body`, missing `body.snippet.channelId`, missing `body.snippet.videoId`, missing `body.snippet.topLevelComment.snippet.textOriginal`, blank text, unsupported reply fields, and unsupported optional fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py
- [X] T034 [P] [US3] Add failing unit upstream-error mapping tests for invalid request, authentication, authorization, quota, missing channel, missing video, disabled comments, endpoint unavailable, deprecated endpoint, and unexpected failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py
- [X] T035 [P] [US3] Add failing integration dispatcher rejection tests for invalid create shapes and missing OAuth in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py
- [X] T036 [P] [US3] Add failing safe-error metadata tests that reject credential, token, stack trace, and raw upstream diagnostic leakage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py
- [X] T037 [US3] Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_comment_threads_contract.py -k insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm the US3 Red tests fail

### Implementation for User Story 3 (Green)

- [X] T038 [US3] Implement strict invalid-request validation for required part, body, channel ID, video ID, nested top-level comment text, delegation value, unsupported reply/list/update/moderation/delete/search/generated-response fields, and unsupported top-level shapes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T039 [US3] Implement safe upstream error mapping for normalized insert failures including invalid metadata, text required, text too long, forbidden, ineligible account, channel not found, video not found, comments disabled, quota exhausted, deprecated endpoint, and unexpected failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T040 [US3] Extend the default insert transport with representative success and failure fixtures for missing video, missing channel, disabled comments, quota exhaustion, and authorization failure in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py
- [X] T041 [US3] Add or update reStructuredText docstrings for every validation, error-mapping, transport, and fake-wrapper function changed for US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py
- [X] T042 [US3] Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_comment_threads_contract.py -k insert` from /Users/ctgunn/Projects/youtube-mcp-server and confirm US3 tests pass

### Refactor for User Story 3

- [X] T043 [US3] Refactor validation and error helpers for safe detail sanitization and consistency with existing Layer 2 tools in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation, and required full-suite validation across all stories.

- [X] T044 [P] Update implementation evidence placeholders or notes in /Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/quickstart.md after focused verification commands are run
- [X] T045 [P] Review and align generated contract details with implementation behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/contracts/commentThreads_insert.md
- [X] T046 Run focused feature suite `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from /Users/ctgunn/Projects/youtube-mcp-server and fix any failures
- [X] T047 Run full repository suite `PYTHONPATH=src python3 -m pytest` from /Users/ctgunn/Projects/youtube-mcp-server and fix any failures before feature completion
- [X] T048 Run lint command `PYTHONPATH=src python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server and fix any failures before feature completion
- [X] T049 Review reStructuredText docstrings for every new or modified Python function in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, and changed tests under /Users/ctgunn/Projects/youtube-mcp-server/tests/
- [X] T050 Verify no public metadata, examples, success results, errors, or logs expose API keys, OAuth tokens, stack traces, raw credential payloads, or unsafe upstream diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py and related tests under /Users/ctgunn/Projects/youtube-mcp-server/tests/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks user-story implementation until shared Red coverage is added and observed failing.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be developed after or alongside US1, but metadata tasks are easier once US1 descriptor scaffolding exists.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can be developed after or alongside US1, but validation tasks are easier once US1 handler scaffolding exists.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; delivers MVP callable creation behavior.
- **US2 (P2)**: Can start after Foundational; benefits from US1 constants/descriptor but remains independently testable through metadata and examples.
- **US3 (P3)**: Can start after Foundational; benefits from US1 validator/handler scaffolding but remains independently testable through invalid requests and safe errors.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Shared schema, constants, and validators must exist before handler and descriptor work.
- Handler and descriptor work must exist before dispatcher registration can pass.
- reStructuredText docstrings must be added or updated before each story checkpoint.
- Refactor tasks occur only after focused story tests pass.
- Full repository test-suite and lint checks run in the final phase before completion.

---

## Parallel Opportunities

- Setup inspections T002, T003, and T004 can run in parallel.
- Foundational Red tasks T005, T006, T007, and T008 can run in parallel because they touch separate test files.
- US1 Red test tasks T010, T011, and T012 can run in parallel before T013.
- US2 Red test tasks T022, T023, and T024 can run in parallel before T025.
- US3 Red test tasks T033, T034, T035, and T036 can run in parallel before T037.
- Polish documentation checks T044 and T045 can run in parallel.

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] Add failing contract test for commentThreads_insert identity and success result in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
Task: "T011 [US1] Add failing unit tests for accepted create arguments and result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py"
Task: "T012 [US1] Add failing integration test for dispatcher execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
Task: "T023 [US2] Add failing shared metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T024 [US2] Add failing catalog and representative-example coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py"
Task: "T035 [US3] Add failing dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py"
Task: "T036 [US3] Add failing safe-error metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational Red coverage.
3. Complete Phase 3 User Story 1.
4. Stop and validate `commentThreads_insert` can create a top-level comment-thread result independently through focused contract, unit, and integration tests.

### Incremental Delivery

1. Add US1 success-path callable behavior and verify independently.
2. Add US2 discoverability, metadata, examples, and contract clarity; verify independently.
3. Add US3 validation and safe error behavior; verify independently.
4. Run focused feature suite, full repository suite, and lint checks before completion.

### Parallel Team Strategy

1. Complete Setup and Foundational phases together.
2. Assign US1 success behavior, US2 metadata/examples, and US3 validation/error behavior to separate developers after shared Red coverage exists.
3. Coordinate shared edits in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py to avoid conflicts, then integrate through the focused feature suite.

## Notes

- `[P]` tasks use different files or can be performed without depending on incomplete tasks.
- `[US1]`, `[US2]`, and `[US3]` labels map to the prioritized user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md.
- Every Python code change must include reStructuredText docstrings for all new or modified functions before the story checkpoint.
- The feature is not complete until focused tests, full `pytest`, and `ruff check .` pass from /Users/ctgunn/Projects/youtube-mcp-server.
