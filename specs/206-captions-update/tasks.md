# Tasks: YT-206 Layer 2 Tool `captions_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code changes require reStructuredText docstrings for all new or modified functions.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with tasks that touch different files and do not depend on incomplete tasks
- **[Story]**: Which user story the task belongs to, such as `[US1]`
- All implementation tasks include exact repository paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature artifacts and existing implementation surface before adding tests or code.

- [X] T001 Review the YT-206 implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/plan.md
- [X] T002 [P] Review the public tool contract requirements in /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/contracts/captions-update-tool-contract.md
- [X] T003 [P] Review the existing concrete captions Layer 2 patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T004 [P] Review the existing Layer 1 captions.update wrapper contract in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared test and registration touchpoints that all user stories will use.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T005 Add failing catalog coverage that `captions_update` is expected in the supported YouTube tool inventory in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T006 [P] Add failing public export coverage for `captions_update` constants and descriptor builders in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T007 [P] Add failing registration coverage that the default YouTube tool registration surface includes `captions_update` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T008 Add the minimal `captions_update` public constants and export placeholders needed by later story tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T009 Export the minimal `captions_update` public names through /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T010 Register the placeholder `captions_update` descriptor in the default tool catalog or dispatcher registration path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T011 Add or update reStructuredText docstrings for foundational `captions_update` Python placeholders in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T012 Run foundational red-green checks for tool inventory and registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Update Caption Tracks Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `captions_update` for valid body-only and body-plus-media caption updates and receive a near-raw updated caption resource.

**Independent Test**: Invoke `captions_update` with eligible authorization and a valid caption update body, with and without supported replacement media, then confirm the result includes `captions.update`, quota cost `450`, requested parts, safe operation context, optional media summary, and the returned updated caption resource.

### Tests for User Story 1 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T013 [P] [US1] Add failing contract tests for `captions_update` descriptor identity, schema, handler presence, and updated-resource result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T014 [P] [US1] Add failing unit tests for valid body-only and body-plus-media `captions_update` handler calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T015 [P] [US1] Add failing integration tests for `captions_update` discovery and executable registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py
- [X] T016 [P] [US1] Add failing MCP routing tests for successful `captions_update` `tools/call` results in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py

### Implementation for User Story 1

- [X] T017 [US1] Import and wire the Layer 1 `build_captions_update_wrapper` dependency in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T018 [US1] Implement `CAPTIONS_UPDATE_INPUT_SCHEMA` for required `part`, required `body.id`, optional `body.snippet.isDraft`, optional `media`, optional `onBehalfOfContentOwner`, and optional `sync` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T019 [US1] Implement the default safe `captions_update` executor transport for representative updated-resource results in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T020 [US1] Implement `validate_captions_update_arguments` for valid authorized body-only and body-plus-media requests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T021 [US1] Implement `map_captions_update_result` preserving item, requestedParts, endpoint, quotaCost, update summary, optional media summary, and delegation summary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T022 [US1] Implement `build_captions_update_handler` and `build_captions_update_tool_descriptor` using the existing Layer 1 wrapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T023 [US1] Export `build_captions_update_handler`, `build_captions_update_tool_descriptor`, `map_captions_update_result`, and `validate_captions_update_arguments` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T024 [US1] Add or update reStructuredText docstrings for all User Story 1 Python functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T025 [US1] Run focused User Story 1 tests and keep them green in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T026 [US1] Refactor the User Story 1 result and handler implementation while preserving near-raw caption update behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: User Story 1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Update Rules Before Calling (Priority: P2)

**Goal**: A client developer can inspect `captions_update` before calling and see upstream identity, quota cost `450`, OAuth-required auth, required update body, optional media-replacement behavior, delegation guidance, and deprecated `sync` caveat.

**Independent Test**: Review the tool discovery entry, contract metadata, descriptions, and examples, then confirm all required cost/auth/update/media/delegation details are visible without implementation-only artifacts.

### Tests for User Story 2 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T027 [P] [US2] Add failing contract tests for `captions_update` quota, auth, availability, response boundary, usage notes, caveats, and deprecated `sync` disclosure in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T028 [P] [US2] Add failing common contract tests that representative `captions_update` metadata stays safe and includes official quota/auth/update fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T029 [P] [US2] Add failing discovery tests that `tools/list` preserves safe `captions_update` metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py
- [X] T030 [P] [US2] Add failing example-alignment tests for authorized body-only update, body-plus-media update, delegated update, missing-body failure, media-without-body failure, and deprecated `sync` caveat in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py

### Implementation for User Story 2

- [X] T031 [US2] Implement `build_captions_update_contract` with quota cost `450`, OAuth-required auth, media-capable availability, usage notes, caveats, and response boundary metadata in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T032 [US2] Add `captions_update` representative examples and safe usage notes to /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T033 [US2] Add `captions_update` resource-family metadata where needed for catalog alignment in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py
- [X] T034 [US2] Ensure dispatcher discovery preserves `captions_update` safe metadata, input schema, quota, auth, availability, and usage notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T035 [US2] Export `build_captions_update_contract` and `CAPTIONS_UPDATE_QUOTA_COST` through /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T036 [US2] Add or update reStructuredText docstrings for all User Story 2 Python functions changed in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T037 [US2] Run focused User Story 2 discovery, contract, and example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T038 [US2] Refactor User Story 2 metadata wording to remove duplication while preserving caller-facing quota, auth, update, media, delegation, and deprecated-option visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Reject Unsupported Caption Update Requests Clearly (Priority: P3)

**Goal**: Invalid `captions_update` requests receive stable caller-facing validation and safe error categories for missing body, incomplete caption identity, unsupported media/update options, missing OAuth, invalid delegation, and upstream failures.

**Independent Test**: Submit representative invalid requests and upstream failure simulations, then confirm each response clearly identifies the violated caption-update rule without exposing secrets, caption file contents, stack traces, or raw media payloads.

### Tests for User Story 3 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T039 [P] [US3] Add failing unit tests for missing `part`, missing `body`, missing `body.id`, invalid `sync`, unsupported body shape, media without body, unsupported media descriptors, missing OAuth, and delegated update without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T040 [P] [US3] Add failing contract tests for safe `captions_update` error categories and endpoint-specific upstream mappings in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T041 [P] [US3] Add failing MCP routing tests for invalid `captions_update` `tools/call` requests returning safe structured errors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py
- [X] T042 [P] [US3] Add failing regression coverage that existing `captions_list` and `captions_insert` validation behavior is unchanged in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py

### Implementation for User Story 3

- [X] T043 [US3] Implement `CaptionsUpdateToolError` with safe category and details fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T044 [US3] Harden `validate_captions_update_arguments` for missing body, missing `body.id`, media-without-body, unsupported media descriptors, invalid `sync`, unsupported fields, missing OAuth, and delegated update without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T045 [US3] Implement upstream error mapping for `contentRequired`, `forbidden`, `captionNotFound`, quota, unavailable endpoint, and unexpected upstream failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T046 [US3] Ensure MCP `tools/call` error handling exposes safe `captions_update` error category, tool name, and remediation details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T047 [US3] Add or update reStructuredText docstrings for all User Story 3 Python functions changed in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T048 [US3] Run focused User Story 3 validation and routing tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T049 [US3] Refactor User Story 3 validation and error mapping to reuse shared Layer 2 conventions without changing caller-facing behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: All user stories should be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature, clean up cross-story rough edges, and capture final evidence.

- [X] T050 [P] Review `captions_update` quickstart coverage and update implementation evidence placeholders in /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/quickstart.md
- [X] T051 [P] Review public examples and tests for absence of API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, caption file contents, and secret values in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T052 [P] Review reStructuredText docstrings for all new or changed `captions_update` Python functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T053 Run the full focused YT-206 validation command from /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/quickstart.md
- [X] T054 Run `python3 -m pytest` from /Users/ctgunn/Projects/youtube-mcp-server/. and fix any failures before completion
- [X] T055 Run `python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server/. and fix any failures before completion
- [X] T056 Record final validation evidence in /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and may run alongside US1 after placeholder exports exist, but final discovery metadata should be checked after US1 descriptor work.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can run alongside US1 after shared validation helper names are agreed, but final error behavior should be checked after US1 handler work.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on US2 or US3; delivers the executable MVP.
- **User Story 2 (P2)**: Independent metadata/discovery increment; benefits from US1 descriptor shape but must remain testable through discovery and contract tests.
- **User Story 3 (P3)**: Independent validation/error increment; benefits from US1 handler shape but must remain testable through invalid request and error mapping tests.

### Within Each User Story

- Red tests must be written and verified failing before implementation.
- Implement only enough Green behavior to pass the story tests.
- Update reStructuredText docstrings before story completion.
- Refactor only after story tests pass.
- Run focused tests after refactor.
- The feature is not complete until `python3 -m pytest` and `python3 -m ruff check .` pass after final code changes.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during setup.
- T006 and T007 can run in parallel with T005 during foundational Red work.
- T013, T014, T015, and T016 can run in parallel for User Story 1 Red tests.
- T027, T028, T029, and T030 can run in parallel for User Story 2 Red tests.
- T039, T040, T041, and T042 can run in parallel for User Story 3 Red tests.
- T050, T051, and T052 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "T013 [P] [US1] Add failing contract tests for `captions_update` descriptor identity, schema, handler presence, and updated-resource result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T014 [P] [US1] Add failing unit tests for valid body-only and body-plus-media `captions_update` handler calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T015 [P] [US1] Add failing integration tests for `captions_update` discovery and executable registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py"
Task: "T016 [P] [US1] Add failing MCP routing tests for successful `captions_update` `tools/call` results in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Parallel Example: User Story 2

```bash
Task: "T027 [P] [US2] Add failing contract tests for `captions_update` quota, auth, availability, response boundary, usage notes, caveats, and deprecated `sync` disclosure in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T028 [P] [US2] Add failing common contract tests that representative `captions_update` metadata stays safe and includes official quota/auth/update fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T029 [P] [US2] Add failing discovery tests that `tools/list` preserves safe `captions_update` metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py"
Task: "T030 [P] [US2] Add failing example-alignment tests for authorized body-only update, body-plus-media update, delegated update, missing-body failure, media-without-body failure, and deprecated `sync` caveat in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py"
```

## Parallel Example: User Story 3

```bash
Task: "T039 [P] [US3] Add failing unit tests for missing `part`, missing `body`, missing `body.id`, invalid `sync`, unsupported body shape, media without body, unsupported media descriptors, missing OAuth, and delegated update without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T040 [P] [US3] Add failing contract tests for safe `captions_update` error categories and endpoint-specific upstream mappings in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T041 [P] [US3] Add failing MCP routing tests for invalid `captions_update` `tools/call` requests returning safe structured errors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
Task: "T042 [P] [US3] Add failing regression coverage that existing `captions_list` and `captions_insert` validation behavior is unchanged in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational exports and registration expectations.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 independently with focused captions contract, unit, integration, and routing tests.
5. Stop for review or demo if only the executable update MVP is needed.

### Incremental Delivery

1. Setup plus Foundational gives a visible placeholder and failing tests for the new public tool.
2. User Story 1 adds executable body-only and body-plus-media update behavior.
3. User Story 2 enriches discovery, metadata, examples, quota, auth, and caveat visibility.
4. User Story 3 hardens invalid request handling and upstream error mapping.
5. Polish verifies the full repository and lint after final changes.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. After Foundational:
   - Developer A: User Story 1 handler/result behavior.
   - Developer B: User Story 2 metadata/discovery/examples.
   - Developer C: User Story 3 validation/error handling.
3. Integrate by running the focused YT-206 command, then `python3 -m pytest`, then `python3 -m ruff check .`.

## Notes

- [P] tasks touch separate files or are Red-test tasks that can be authored independently.
- `[US1]`, `[US2]`, and `[US3]` map directly to the prioritized user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/spec.md.
- Every changed Python function must have a reStructuredText docstring before its story is marked complete.
- Tests must fail before the corresponding implementation task begins.
