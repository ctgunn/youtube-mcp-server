# Tasks: Layer 2 Tool `commentThreads_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/data-model.md), [contracts/commentThreads_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/contracts/commentThreads_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/quickstart.md)

**Tests**: Required. Every user story includes Red-Green-Refactor test tasks. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Python Documentation**: Required. Every new or modified Python function must receive a reStructuredText docstring before the related story is complete.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm current Layer 1 comment-thread wrapper behavior, Layer 2 list-tool patterns, and target files before writing Red tests.

- [X] T001 Review the Layer 1 `commentThreads.list` wrapper metadata, selector validation, and auth mode in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`
- [X] T002 [P] Review existing Layer 2 list tool patterns for schemas, contracts, handlers, validators, examples, and result mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T003 [P] Review public export conventions for YouTube common resource-family modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T004 [P] Review default tool registry wiring for endpoint-backed descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T005 [P] Review existing representative catalog coverage expectations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red tests that prove the new public tool is absent from exports, representative metadata, and default registration until implemented.

**Critical**: No Green implementation work should begin until these Red tests exist and have been observed failing for the missing `commentThreads_list` Layer 2 surface.

- [X] T006 [P] Add failing scaffolding/export tests for `COMMENT_THREADS_LIST_*`, `build_comment_threads_list_contract`, and `build_comment_threads_list_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 [P] Add failing common metadata alignment tests for `commentThreads_list` against representative Layer 2 safety rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add failing tool catalog tests for the `commentThreads_list` representative entry, API-key auth mode, quota cost 1, selector list, and concrete contract alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T009 [P] Add failing default registry discovery tests for `commentThreads_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T010 [P] Add failing comment-thread family registration tests for `commentThreads_list` descriptor discovery in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`
- [X] T011 Run the focused Red scaffold suite from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new `commentThreads_list` checks fail before implementation

**Checkpoint**: Shared Red coverage exists for exports, catalog metadata, and registry discovery.

---

## Phase 3: User Story 1 - Retrieve Comment Threads Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `commentThreads_list` with API-key access, supported `part`, and exactly one selector, then receive a near-raw comment-thread list result for video-based, channel-related, or ID-based retrieval.

**Independent Test**: Invoke the descriptor handler with a fake successful Layer 1 wrapper using `videoId`, `allThreadsRelatedToChannelId`, and `id`, then verify the result includes endpoint identity, quota cost 1, requested parts, selector context, item collection, pagination context when present, and no unrelated reply-only, mutation, ranking, or enrichment data.

### Tests for User Story 1 (Red)

- [X] T012 [P] [US1] Add failing contract tests for `commentThreads_list` identity, input schema, descriptor shape, video-based result, channel-related result, and ID-based result in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`
- [X] T013 [P] [US1] Add failing unit tests for `COMMENT_THREADS_LIST_INPUT_SCHEMA`, valid selector normalization, `validate_comment_threads_list_arguments`, and `map_comment_threads_list_result` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`
- [X] T014 [P] [US1] Add failing integration tests proving the default comment-thread registry can execute successful `commentThreads_list` calls with fake wrapper responses in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Create the Layer 2 comment-thread resource-family module with `COMMENT_THREADS_LIST_*` constants, input schema, description, usage notes, caveats, and initial success examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T016 [US1] Implement `build_comment_threads_list_contract` and `build_comment_threads_list_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T017 [US1] Implement selector validation for `part`, `videoId`, `allThreadsRelatedToChannelId`, and `id` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T018 [US1] Implement `map_comment_threads_list_result` to preserve endpoint, quota cost, requested parts, selector, text format, options, items, `kind`, `etag`, `nextPageToken`, and `pageInfo` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T019 [US1] Implement the `commentThreads_list` handler, API-key auth context creation, Layer 1 wrapper call, and successful empty collection handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T020 [US1] Export `COMMENT_THREADS_LIST_*`, contract builder, descriptor builder, handler builder, validator, and result mapper symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_comment_threads_list_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add or update reStructuredText docstrings for every new or modified `commentThreads_list` function and fake wrapper method in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`

### Refactor and Validation for User Story 1

- [X] T023 [US1] Run US1 focused tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`
- [X] T024 [US1] Refactor the US1 implementation for naming, helper reuse, result-boundary clarity, and endpoint-family cohesion while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Auth, and Filter Modes Before Calling (Priority: P2)

**Goal**: A client developer can discover the tool and understand quota cost, API-key auth expectations, access-sensitive moderation-status caveats, supported selectors, selector-specific optional-parameter restrictions, no-body boundary, response shape, and out-of-scope behavior before invocation.

**Independent Test**: Inspect public metadata, usage notes, caveats, representative examples, and catalog entries without invoking the handler, then verify all required caller-facing disclosures are present.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing contract tests for quota cost 1, API-key auth disclosure, required `part`, supported selectors, selector-specific restrictions, no-body guidance, response convention, caveats, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`
- [X] T026 [P] [US2] Add failing representative catalog example tests for `commentThreads_list` alignment with the concrete contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T027 [P] [US2] Add failing common contract metadata tests proving `commentThreads_list` public metadata is safe and exposes quota, auth, selector, and access-caveat fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`

### Implementation for User Story 2 (Green)

- [X] T028 [US2] Expand `COMMENT_THREADS_LIST_USAGE_NOTES`, caveats, response boundary, selector disclosure, access-sensitive moderation-status disclosure, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T029 [US2] Add or update the representative `commentThreads_list` contract entry used by shared examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T030 [US2] Ensure `build_comment_threads_list_contract` emits quota cost 1, API-key auth mode, `part` requirement, selector list, no-body rule, optional-parameter restrictions, and safe response convention in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T031 [US2] Export any newly introduced `commentThreads_list` example or metadata symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T032 [US2] Add or update reStructuredText docstrings for modified metadata and example builder functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor and Validation for User Story 2

- [X] T033 [US2] Run US2 focused metadata tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T034 [US2] Refactor caller-facing text for brevity and consistency while preserving all metadata assertions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Comment Thread List Requests Clearly (Priority: P3)

**Goal**: A caller receives safe, specific validation or upstream failure feedback for missing `part`, missing selector, conflicting selectors, malformed selectors, unsupported options, invalid pagination, invalid text format, invalid moderation status, access-sensitive moderation failures, disabled comments, missing resources, quota failures, and unexpected upstream failures.

**Independent Test**: Submit representative invalid handler requests and fake upstream failures, then verify stable safe error categories and caller-facing guidance without secret leakage.

### Tests for User Story 3 (Red)

- [X] T035 [P] [US3] Add failing unit validation tests for missing `part`, missing selector, multiple selectors, empty selectors, unsupported `id` modifiers, invalid `maxResults`, invalid `moderationStatus`, invalid `order`, invalid `pageToken`, invalid `searchTerms`, invalid `textFormat`, request body, reply-listing fields, mutation fields, and unsupported analysis fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`
- [X] T036 [P] [US3] Add failing contract tests for safe error sanitization and non-leakage of API keys, OAuth tokens, stack traces, raw request diagnostics, and unsafe upstream details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`
- [X] T037 [US3] Add failing unit handler tests for upstream category mapping including invalid request, authentication, authorization, quota, disabled comments, channel not found, video not found, thread not found, endpoint unavailable, deprecated endpoint, and unexpected failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`
- [X] T038 [US3] Add failing integration tests proving dispatcher execution returns safe failures for conflicting selectors and unsupported `id` modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`

### Implementation for User Story 3 (Green)

- [X] T039 [US3] Implement `commentThreads_list` invalid-request helpers, selector conflict validation, no-body rejection, unsupported `id` modifier rejection, and unsupported workflow field rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T040 [US3] Implement validation for `maxResults`, `moderationStatus`, `order`, `pageToken`, `searchTerms`, and `textFormat` using endpoint-native limits in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T041 [US3] Implement upstream error mapping for `commentThreads_list` using shared safe categories with safe reasons for `commentsDisabled`, `channelNotFound`, `videoNotFound`, and `commentThreadNotFound` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T042 [US3] Ensure API-key and access-sensitive errors are sanitized and never expose API keys, OAuth tokens, raw diagnostics, or stack traces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T043 [US3] Add or update reStructuredText docstrings for validation, auth, and error-mapping functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

### Refactor and Validation for User Story 3

- [X] T044 [US3] Run US3 focused validation and safe-error tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`
- [X] T045 [US3] Refactor validation and safe-error helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

**Checkpoint**: All user stories are independently functional and safely validated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish verification, documentation, and cross-story cleanup after all desired user stories are complete.

- [X] T046 [P] Review and update implementation evidence placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/quickstart.md`
- [X] T047 [P] Verify the public contract remains aligned with final implementation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/contracts/commentThreads_list.md`
- [X] T048 Run the full focused feature suite from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T049 Run the full repository test suite with `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T050 Run code quality checks with `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T051 Fix any focused-suite, full-suite, or lint failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and related tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T052 Record final Red-Green-Refactor, focused test, full `pytest`, and `ruff check .` evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks Green implementation.
- **User Stories (Phase 3+)**: Depend on Foundational Red coverage.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Start after Foundational. This is the MVP and creates the callable endpoint-backed `commentThreads_list` tool.
- **User Story 2 (P2)**: Start after Foundational. It can be implemented after or in parallel with US1 metadata work, but final metadata assertions depend on the US1 contract builder existing.
- **User Story 3 (P3)**: Start after Foundational. It can be implemented after or in parallel with US1 validation skeleton work, but final handler error assertions depend on the US1 descriptor and handler existing.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation should be the smallest endpoint-backed change that passes story tests.
- reStructuredText docstrings must be added or updated before the story checkpoint.
- Refactor only after focused story tests pass.
- Preserve user-story independence: do not add reply-only listing, thread creation, comment insertion, comment editing, comment deletion, moderation actions, recommendations, ranking, summarization, sentiment, enrichment, or cross-endpoint behavior.

## Parallel Opportunities

- Setup tasks T002-T005 can run in parallel after T001 is underway.
- Foundational Red tests T006-T010 touch different files and can run in parallel, then T011 verifies them together.
- US1 Red tests T012-T014 can run in parallel before US1 Green implementation.
- US2 Red tests T025-T027 can run in parallel before US2 metadata implementation.
- US3 Red tests T035-T036 can run in parallel before US3 validation and error implementation.
- Polish documentation checks T046 and T047 can run in parallel before final verification.

## Parallel Example: User Story 1

```bash
# Launch US1 Red tests together:
Task: "Add failing contract tests for `commentThreads_list` identity, input schema, descriptor shape, video-based result, channel-related result, and ID-based result in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
Task: "Add failing unit tests for `COMMENT_THREADS_LIST_INPUT_SCHEMA`, valid selector normalization, `validate_comment_threads_list_arguments`, and `map_comment_threads_list_result` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py"
Task: "Add failing integration tests proving the default comment-thread registry can execute successful `commentThreads_list` calls with fake wrapper responses in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comment_threads_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 metadata Red tests together:
Task: "Add failing contract tests for quota cost 1, API-key auth disclosure, required `part`, supported selectors, selector-specific restrictions, no-body guidance, response convention, caveats, and examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
Task: "Add failing representative catalog example tests for `commentThreads_list` alignment with the concrete contract in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "Add failing common contract metadata tests proving `commentThreads_list` public metadata is safe and exposes quota, auth, selector, and access-caveat fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 validation/error Red tests together:
Task: "Add failing unit validation tests for missing `part`, missing selector, multiple selectors, empty selectors, unsupported `id` modifiers, invalid pagination, invalid text format, request body, and unsupported workflow fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comment_threads.py"
Task: "Add failing contract tests for safe error sanitization in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comment_threads_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 Red tests T012-T014 and confirm they fail.
3. Complete US1 Green implementation T015-T022.
4. Complete US1 validation/refactor T023-T024.
5. Stop and validate that `commentThreads_list` can retrieve comment threads through the public descriptor with safe near-raw list output.

### Incremental Delivery

1. Deliver US1 as the callable endpoint-backed comment-thread list tool.
2. Deliver US2 to make quota, API-key auth, selector rules, optional-parameter restrictions, no-body behavior, and examples complete for client discovery.
3. Deliver US3 to harden unsupported request and upstream failure handling.
4. Run Phase 6 focused, full-suite, and lint checks before completion.

### Parallel Team Strategy

1. One engineer adds foundational Red coverage T006-T010.
2. After T011, separate engineers can prepare US1, US2, and US3 Red tests in parallel.
3. Coordinate Green implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` because most production changes share that file.

## Notes

- `[P]` tasks are marked only where work can proceed in different files or before shared implementation dependencies.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to prioritized user stories in the feature spec.
- Final completion requires full `pytest` and `ruff check .`; focused test runs alone are not sufficient.
- Python docstrings must be reStructuredText and cover purpose, inputs, outputs, raised errors where relevant, quota/auth behavior, and side effects where relevant.
