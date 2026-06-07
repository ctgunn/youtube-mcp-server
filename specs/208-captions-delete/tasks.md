# Tasks: YT-208 Layer 2 Tool `captions_delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/captions-delete-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/quickstart.md`

**Tests**: Test tasks are REQUIRED. Every user story includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code tasks include explicit reStructuredText docstring work for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase because it touches different files or only reads context.
- **[Story]**: User story label for story phases only.
- Every task includes an exact repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature context and implementation surface before writing failing tests.

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/plan.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/captions-delete-tool-contract.md` to extract the required `captions_delete` contract, test commands, and docstring obligations.
- [X] T002 [P] Review the existing captions Layer 2 implementation pattern in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T003 [P] Review the existing captions public exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
- [X] T004 [P] Review the default YouTube tool registration path in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T005 [P] Review the current captions tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared assumptions and guardrails that all stories depend on.

**Critical**: No user story work can begin until this phase is complete.

- [X] T006 Confirm the YT-108 Layer 1 `captions.delete` wrapper and builder are available in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`.
- [X] T007 Confirm the existing shared Layer 2 metadata and response-boundary helpers support mutation acknowledgment semantics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`.
- [X] T008 [P] Add a failing representative-catalog alignment test for future `captions_delete` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`.
- [X] T009 [P] Add a failing default-registry test requiring executable `captions_delete` registration in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T010 Run the focused foundational red checks `python3 -m pytest tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new `captions_delete` checks fail before implementation.

**Checkpoint**: Foundation ready - user story implementation can now begin in priority order or in parallel if separate workers coordinate file ownership.

---

## Phase 3: User Story 1 - Delete Caption Tracks Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `captions_delete` with eligible authorization and a caption-track identifier and receive a clear deletion acknowledgment mapped to `captions.delete`.

**Independent Test**: Invoke the concrete `captions_delete` descriptor handler with a valid `id` and confirm the result identifies `captions.delete`, quota cost `50`, deletion status, no-body success context, and no fabricated caption resource.

### Tests for User Story 1 (REQUIRED)

- [X] T011 [P] [US1] Add failing contract tests for `captions_delete` module exports, descriptor existence, and successful deletion result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`.
- [X] T012 [P] [US1] Add failing unit tests for `CAPTIONS_DELETE_INPUT_SCHEMA`, authorized `validate_captions_delete_arguments`, and `map_captions_delete_result` deletion acknowledgment behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`.
- [X] T013 [P] [US1] Add failing integration tests for registering and executing `captions_delete` through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`.
- [X] T014 [US1] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_captions.py tests/integration/test_youtube_captions_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US1 tests fail before implementation.

### Implementation for User Story 1

- [X] T015 [US1] Add `CAPTIONS_DELETE_TOOL_NAME`, `CAPTIONS_DELETE_QUOTA_COST`, `CAPTIONS_DELETE_INPUT_SCHEMA`, description, usage notes, caveats, and `CaptionsDeleteToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T016 [US1] Add the default safe delete transport and delete executor helpers for local execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T017 [US1] Implement `build_captions_delete_contract` with upstream identity `captions.delete`, quota cost `50`, OAuth-required auth, required `id`, optional delegation, mutation acknowledgment response convention, and near-raw response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T018 [US1] Implement `validate_captions_delete_arguments`, `map_captions_delete_result`, `build_captions_delete_handler`, and `build_captions_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T019 [US1] Export `captions_delete` constants, error class, contract builder, handler builder, descriptor builder, mapper, and validator from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
- [X] T020 [US1] Register `build_captions_delete_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified `captions_delete` Python function and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`.
- [X] T022 [US1] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_captions.py tests/integration/test_youtube_captions_registration.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US1 tests pass.
- [X] T023 [US1] Refactor the `captions_delete` implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` to remove duplication with existing captions helpers while preserving the passing US1 tests.

**Checkpoint**: User Story 1 is independently functional and provides the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Delegation Before Calling (Priority: P2)

**Goal**: A client developer can inspect `captions_delete` before calling and see upstream identity, quota cost `50`, OAuth-required auth, required `id`, destructive deletion behavior, optional delegation, no-body request behavior, and no-content acknowledgment semantics.

**Independent Test**: Review tool metadata, discovery output, and examples and confirm a caller can prepare a valid request without consulting implementation-only artifacts.

### Tests for User Story 2 (REQUIRED)

- [X] T024 [P] [US2] Add failing contract tests for `captions_delete` metadata, usage notes, caveats, response convention, and response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`.
- [X] T025 [P] [US2] Add failing shared metadata safety checks for `captions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`.
- [X] T026 [P] [US2] Add failing representative example alignment checks for `captions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`.
- [X] T027 [P] [US2] Add failing default-discovery metadata assertions for `captions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T028 [US2] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US2 tests fail before implementation.

### Implementation for User Story 2

- [X] T029 [US2] Add `captions_delete` representative metadata to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`.
- [X] T030 [US2] Update `captions_delete` metadata text, usage notes, and caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` so discovery exposes `captions.delete`, `Quota cost: 50`, OAuth-required auth, `id`, `onBehalfOfContentOwner`, no request body, destructive deletion, and `204 No Content` acknowledgment.
- [X] T031 [US2] Ensure public metadata safety validation for `captions_delete` passes without exposing API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T032 [US2] Add or update reStructuredText docstrings for every new or modified metadata/example Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`.
- [X] T033 [US2] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US2 tests pass.
- [X] T034 [US2] Refactor metadata and usage-note wording in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` to remove duplicate prose while preserving the passing US2 tests.

**Checkpoint**: User Story 2 is independently inspectable and metadata-complete.

---

## Phase 5: User Story 3 - Reject Unsupported Caption Delete Requests Clearly (Priority: P3)

**Goal**: Invalid, unauthorized, unsupported, repeated, or upstream-failed `captions_delete` requests produce clear safe error categories and remediation guidance.

**Independent Test**: Submit representative invalid requests and fake upstream failures and confirm each failure maps to the expected safe category without leaking sensitive details.

### Tests for User Story 3 (REQUIRED)

- [X] T035 [P] [US3] Add failing parameterized validation tests for missing `id`, blank `id`, unsupported fields, body-like input, missing OAuth, and delegated owner without OAuth in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`.
- [X] T036 [P] [US3] Add failing unit tests for `validate_captions_delete_arguments` safe details and unsupported request-shape handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`.
- [X] T037 [P] [US3] Add failing upstream error mapping tests for `forbidden`, `captionNotFound`, quota exhaustion, transient unavailability, invalid request, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`.
- [X] T038 [P] [US3] Add failing dispatcher rejection tests for invalid `captions_delete` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`.
- [X] T039 [US3] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_captions.py tests/integration/test_youtube_captions_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US3 tests fail before implementation.

### Implementation for User Story 3

- [X] T040 [US3] Implement missing-id, blank-id, unsupported-field, no-body, delegation, and OAuth validation branches for `captions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T041 [US3] Implement safe upstream error mapping for `captions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, including `forbidden` to `authorization_failed` and `captionNotFound` to `resource_not_found`.
- [X] T042 [US3] Ensure `CaptionsDeleteToolError` details never expose API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T043 [US3] Add or update reStructuredText docstrings for every new or modified validation, error-mapping, and fake-wrapper test helper function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`.
- [X] T044 [US3] Run `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_captions.py tests/integration/test_youtube_captions_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US3 tests pass.
- [X] T045 [US3] Refactor validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` to reuse existing captions helper patterns without changing public behavior.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and feature-wide evidence.

- [X] T046 [P] Run the complete focused YT-208 validation command `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix failures in the touched files.
- [X] T047 [P] Run MCP discovery and routing guard tests `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py` from `/Users/ctgunn/Projects/youtube-mcp-server` if `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` or `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` changed.
- [X] T048 [P] Run Layer 1 guard tests `python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server` if `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py` changed.
- [X] T049 Review all changed public metadata, examples, errors, and logs for secret safety in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T050 Review every new or modified Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and touched files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T051 Run the quickstart validation checklist from `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/quickstart.md`.
- [X] T052 Run the full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure before considering YT-208 complete.
- [X] T053 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every lint finding before considering YT-208 complete.
- [X] T054 Update implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/quickstart.md` with focused test, full-suite, lint, safety-review, and docstring-review outcomes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; delivers the MVP executable tool.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be developed after or alongside US1 if file edits are coordinated, but it is easiest after US1 creates the concrete tool contract.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be developed after or alongside US1 if file edits are coordinated, but it is easiest after US1 creates the concrete validator and handler.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 after Foundational; establishes the executable `captions_delete` MVP.
- **US2 (P2)**: Depends on the `captions_delete` contract surface created by US1 for simplest execution; remains independently testable through discovery and metadata.
- **US3 (P3)**: Depends on the `captions_delete` validator and handler created by US1 for simplest execution; remains independently testable through invalid request and error-mapping checks.

### Within Each User Story

- Red tests must be written and run before implementation.
- Green implementation must be the minimum code required to pass that story's tests.
- reStructuredText docstrings must be added or updated before a story is marked complete.
- Refactor only after tests pass; rerun the affected focused test command afterward.
- Final completion requires `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Parallel Opportunities

- Setup review tasks T002, T003, T004, and T005 can run in parallel.
- Foundational red tests T008 and T009 can be written in parallel because they touch different test files.
- US1 red tests T011, T012, and T013 can be written in parallel because they touch different test files.
- US2 red tests T024, T025, T026, and T027 can be written in parallel because they touch different test files.
- US3 red tests T035, T036, T037, and T038 can be split by test file, with coordination for shared edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`.
- Polish guard runs T046, T047, and T048 can run in parallel when their file-change conditions apply.

---

## Parallel Example: User Story 1

```bash
# Launch Red test-writing work in parallel:
Task: "T011 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T012 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T013 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch metadata Red test-writing work in parallel:
Task: "T024 [US2] Add captions contract metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T025 [US2] Add shared metadata safety checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T026 [US2] Add representative catalog checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T027 [US2] Add default discovery checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
# Launch validation/error Red test-writing work in parallel:
Task: "T035 [US3] Add validation parameter cases in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T036 [US3] Add unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T038 [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup review.
2. Complete Phase 2 foundational red checks.
3. Complete Phase 3 US1 to add executable `captions_delete` with deletion acknowledgment.
4. Stop and validate US1 independently with `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_captions.py tests/integration/test_youtube_captions_registration.py`.

### Incremental Delivery

1. Add US1 for the executable delete tool and basic deletion acknowledgment.
2. Add US2 for complete quota/auth/delegation/destructive metadata visibility.
3. Add US3 for invalid request and upstream error mapping.
4. Finish Phase 6 with focused validation, full-suite validation, lint, quickstart evidence, safety review, and docstring review.

### Parallel Team Strategy

With multiple workers:

1. Complete Setup and Foundational together.
2. Assign US1 implementation ownership to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the US1 tests.
3. Assign US2 metadata ownership to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` and metadata assertions after US1 creates the concrete contract.
4. Assign US3 validation/error ownership to `captions_delete` validation and error mapping after US1 creates the concrete validator and handler.

---

## Notes

- `[P]` tasks touch different files or are read-only and can run in parallel within the phase.
- `[US1]`, `[US2]`, and `[US3]` labels map tasks to prioritized user stories from `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md`.
- Tests must fail before implementation for each story.
- Avoid adding persistence, hosted transport changes, bulk deletion, deletion undo, recovery, transcript summarization, enrichment, or heuristic behavior.
- Do not expose API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or secret values in public metadata, examples, errors, docs, tests, or logs.
