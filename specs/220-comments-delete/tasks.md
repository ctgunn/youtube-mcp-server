# Tasks: Layer 2 Tool `comments_delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/data-model.md), [contracts/comments-delete-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/contracts/comments-delete-tool-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/quickstart.md)

**Tests**: Required. Every user story includes Red-Green-Refactor test tasks. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Python Documentation**: Required. Every new or modified Python function must receive a reStructuredText docstring before the related story is complete.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm current comments-family shape and implementation targets before writing Red tests.

- [X] T001 Review existing comments Layer 2 contracts, handlers, validators, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T002 [P] Review existing public exports for comments-family tools in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T003 [P] Review existing default tool registry wiring for comments-family descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red tests that prove the new public tool is absent from exports, representative metadata, and default registration until implemented.

**Critical**: No Green implementation work should begin until these Red tests exist and have been observed failing for the missing `comments_delete` Layer 2 surface.

- [X] T004 [P] Add failing scaffolding/export tests for `COMMENTS_DELETE_*`, `build_comments_delete_contract`, and `build_comments_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T005 [P] Add failing common metadata alignment tests for `comments_delete` against representative Layer 2 safety rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T006 [P] Add failing tool catalog tests for the `comments_delete` representative entry, OAuth-required auth mode, quota cost 50, and concrete contract alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T007 [P] Add failing default registry discovery tests for `comments_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T008 [P] Add failing comments-family registration tests for `comments_delete` descriptor discovery in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T009 Run the focused Red scaffold suite from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new `comments_delete` checks fail before implementation

**Checkpoint**: Shared Red coverage exists for exports, catalog metadata, and registry discovery.

---

## Phase 3: User Story 1 - Delete Existing Comments Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `comments_delete` with eligible OAuth and a valid target comment identifier, then receive a safe deletion acknowledgment for the endpoint-backed mutation.

**Independent Test**: Invoke the descriptor handler with a fake successful Layer 1 wrapper using `id`, then verify the result includes endpoint identity, quota cost 50, normalized target ID, safe OAuth context, delegated owner context when supplied, deletion status, and no fabricated deleted comment resource.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract tests for `comments_delete` identity, schema, descriptor, and successful deletion acknowledgment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for `COMMENTS_DELETE_INPUT_SCHEMA`, valid argument normalization, and `map_comments_delete_result` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T012 [P] [US1] Add failing integration tests proving the default comments registry can execute a successful `comments_delete` handler with a fake wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Add `comments_delete` constants, input schema, description, usage notes, caveats, and initial success examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T014 [US1] Implement `build_comments_delete_contract` and `build_comments_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T015 [US1] Implement target ID normalization, single-target validation, and successful deletion acknowledgment mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T016 [US1] Implement the `comments_delete` handler, OAuth context creation, Layer 1 wrapper call, and 204/no-content success handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T017 [US1] Export `COMMENTS_DELETE_*`, contract builder, descriptor builder, validator, and result mapper symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T018 [US1] Register `build_comments_delete_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T019 [US1] Add or update reStructuredText docstrings for every new or modified `comments_delete` function and fake wrapper method in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`

### Refactor and Validation for User Story 1

- [X] T020 [US1] Run US1 focused tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`
- [X] T021 [US1] Refactor the US1 implementation for naming, helper reuse, and endpoint-boundary clarity while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost and OAuth Before Deleting (Priority: P2)

**Goal**: A client developer can discover the tool and understand quota cost, OAuth requirement, target-comment requirement, destructive deletion behavior, no-body boundary, delegation context, acknowledgment result, and out-of-scope behavior before invocation.

**Independent Test**: Inspect public metadata, usage notes, caveats, representative examples, and catalog entries without invoking the handler, then verify all required caller-facing disclosures are present.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing contract tests for quota, OAuth, target ID requirement, destructive deletion behavior, no-body guidance, acknowledgment result, caveats, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T023 [P] [US2] Add failing representative catalog example tests for `comments_delete` alignment with the concrete contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T024 [P] [US2] Add failing common contract metadata tests proving safe public metadata does not expose secrets or unsafe diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`

### Implementation for User Story 2 (Green)

- [X] T025 [US2] Expand `COMMENTS_DELETE_USAGE_NOTES`, caveats, response boundary, destructive-operation metadata, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T026 [US2] Add or update the representative `comments_delete` contract entry used by shared examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T027 [US2] Ensure `build_comments_delete_contract` emits quota cost 50, OAuth-required auth mode, one-target rule, no-body rule, destructive deletion caveat, and safe response convention in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T028 [US2] Export any newly introduced `comments_delete` example or metadata symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T029 [US2] Add or update reStructuredText docstrings for modified metadata and example builder functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor and Validation for User Story 2

- [X] T030 [US2] Run US2 focused metadata tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T031 [US2] Refactor caller-facing text for brevity and consistency while preserving all metadata assertions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Comment Delete Requests Clearly (Priority: P3)

**Goal**: A caller receives safe, specific validation or upstream failure feedback for missing OAuth, missing target ID, malformed target ID, duplicate or conflicting target shapes, unsupported bodies, unsupported parameters, inaccessible comments, already deleted comments, quota failures, and upstream failures.

**Independent Test**: Submit representative invalid handler requests and fake upstream failures, then verify stable safe error categories and caller-facing guidance without secret leakage.

### Tests for User Story 3 (Red)

- [X] T032 [P] [US3] Add failing unit validation tests for missing `id`, empty ID, malformed ID, duplicate or conflicting target shapes, unsupported body, unsupported moderation fields, unsupported update fields, unsupported recovery instructions, unsupported options, and invalid delegation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`
- [X] T033 [P] [US3] Add failing contract tests for safe error sanitization and non-leakage of tokens, stack traces, raw request diagnostics, and unsafe upstream detail in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T034 [US3] Add failing unit handler tests for upstream category mapping including invalid request, authentication, authorization, quota, resource not found, already deleted target, endpoint unavailable, deprecated endpoint, and unexpected failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`

### Implementation for User Story 3 (Green)

- [X] T035 [US3] Implement `comments_delete` invalid-request helpers, single-target validation, no-body rejection, moderation/update/recovery field rejection, and unsupported-option rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T036 [US3] Implement upstream error mapping for `comments_delete` using shared safe categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T037 [US3] Ensure OAuth and delegated context errors are sanitized and never expose API keys, OAuth tokens, raw diagnostics, or stack traces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`
- [X] T038 [US3] Add or update reStructuredText docstrings for validation, auth, and error-mapping functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

### Refactor and Validation for User Story 3

- [X] T039 [US3] Run US3 focused validation and safe-error tests from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`
- [X] T040 [US3] Refactor validation and safe-error helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`

**Checkpoint**: All user stories are independently functional and safely validated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish verification, documentation, and cross-story cleanup after all desired user stories are complete.

- [X] T041 [P] Review and update implementation evidence placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/quickstart.md`
- [X] T042 [P] Verify the public contract remains aligned with final implementation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/contracts/comments-delete-tool-contract.md`
- [X] T043 Run the full focused feature suite from `/Users/ctgunn/Projects/youtube-mcp-server` covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T044 Run the full repository test suite with `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T045 Run code quality checks with `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T046 Fix any focused-suite, full-suite, or lint failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and related tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T047 Record final Red-Green-Refactor, focused test, full `pytest`, and `ruff check .` evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks Green implementation.
- **User Stories (Phase 3+)**: Depend on Foundational Red coverage.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Start after Foundational. This is the MVP and creates the callable deletion tool.
- **User Story 2 (P2)**: Start after Foundational. It can be implemented after or in parallel with US1 metadata work, but final metadata assertions depend on the US1 contract builder existing.
- **User Story 3 (P3)**: Start after Foundational. It can be implemented after or in parallel with US1 validation skeleton work, but final handler error assertions depend on the US1 descriptor and handler existing.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation should be the smallest endpoint-backed change that passes story tests.
- reStructuredText docstrings must be added or updated before the story checkpoint.
- Refactor only after focused story tests pass.
- Preserve user-story independence: do not add listing, reply creation, comment editing, moderation status changes, recovery, recommendations, ranking, summarization, sentiment, enrichment, or cross-endpoint behavior.

## Parallel Opportunities

- Setup tasks T002 and T003 can run in parallel after T001 is underway.
- Foundational Red tests T004-T008 touch different files and can run in parallel, then T009 verifies them together.
- US1 Red tests T010-T012 can run in parallel before US1 Green implementation.
- US2 Red tests T022-T024 can run in parallel before US2 metadata implementation.
- US3 Red tests T032-T033 can run in parallel before US3 validation and error implementation.
- Polish documentation checks T041 and T042 can run in parallel before final verification.

## Parallel Example: User Story 1

```bash
# Launch US1 Red tests together:
Task: "Add failing contract tests for `comments_delete` identity, schema, descriptor, and successful deletion acknowledgment in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
Task: "Add failing unit tests for `COMMENTS_DELETE_INPUT_SCHEMA`, valid argument normalization, and `map_comments_delete_result` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py"
Task: "Add failing integration tests proving the default comments registry can execute a successful `comments_delete` handler with a fake wrapper in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_comments_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 metadata Red tests together:
Task: "Add failing contract tests for quota, OAuth, target ID requirement, destructive deletion behavior, no-body guidance, acknowledgment result, caveats, and examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
Task: "Add failing representative catalog example tests for `comments_delete` alignment with the concrete contract in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "Add failing common contract metadata tests proving safe public metadata does not expose secrets or unsafe diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 validation/error Red tests together:
Task: "Add failing unit validation tests for missing `id`, empty ID, malformed ID, duplicate or conflicting target shapes, unsupported body, and unsupported options in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_comments.py"
Task: "Add failing contract tests for safe error sanitization in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_comments_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 Red tests T010-T012 and confirm they fail.
3. Complete US1 Green implementation T013-T019.
4. Complete US1 validation/refactor T020-T021.
5. Stop and validate that `comments_delete` can delete one comment through the public descriptor with safe acknowledgment output.

### Incremental Delivery

1. Deliver US1 as the callable endpoint-backed deletion tool.
2. Deliver US2 to make quota, OAuth, one-target rule, no-body, destructive behavior, and examples complete for client discovery.
3. Deliver US3 to harden unsupported request and upstream failure handling.
4. Run Phase 6 focused, full-suite, and lint checks before completion.

### Parallel Team Strategy

1. One engineer adds foundational Red coverage T004-T008.
2. After T009, separate engineers can prepare US1, US2, and US3 Red tests in parallel.
3. Coordinate Green implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` because most production changes share that file.

## Notes

- `[P]` tasks are marked only where work can proceed in different files or before shared implementation dependencies.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to prioritized user stories in the feature spec.
- Final completion requires full `pytest` and `ruff check .`; focused test runs alone are not sufficient.
- Python docstrings must be reStructuredText and cover purpose, inputs, outputs, raised errors where relevant, quota/auth behavior, and side effects where relevant.
