# Tasks: Baseline Server Tools (FND-003)

**Input**: Design documents from `/specs/003-baseline-server-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-baseline-server-tools-contract.md, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared fixtures and baseline tool test scaffolding.

- [X] T001 Create baseline tool fixture builders for test payloads in ~/Projects/youtube-mcp-server/tests/unit/conftest.py
- [X] T002 [P] Add integration request helper utilities for baseline smoke flows in ~/Projects/youtube-mcp-server/tests/integration/conftest.py
- [X] T003 [P] Add contract payload helper utilities for `tools/call` baseline invocations in ~/Projects/youtube-mcp-server/tests/contract/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared baseline contracts and metadata plumbing required before story-level work.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add failing foundational envelope assertions for baseline tool success/error consistency in ~/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py
- [X] T005 [P] Add failing foundational routing assertions for baseline tool discovery and invocation entry points in ~/Projects/youtube-mcp-server/tests/unit/test_method_routing.py
- [X] T006 Implement shared server metadata loader for dispatcher bootstrap in ~/Projects/youtube-mcp-server/src/mcp_server/app.py
- [X] T007 Implement shared baseline tool descriptor constants for registry parity in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T008 Refactor dispatcher initialization to accept injected metadata while preserving existing behavior in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: Foundation is ready; user stories are independently executable.

---

## Phase 3: User Story 1 - Verify Service Reachability (Priority: P1) 🎯 MVP

**Goal**: Ensure `server_ping` provides reliable smoke-check status and timestamp output via MCP tool invocation.

**Independent Test**: Invoke `server_ping` through `tools/call` and confirm status/timestamp payload shape is returned consistently across repeated calls.

### Tests for User Story 1 (REQUIRED)

- [X] T009 [P] [US1] Add failing contract assertions for `server_ping` payload fields in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T010 [P] [US1] Add failing integration test for repeated `server_ping` invocations in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T011 [P] [US1] Add failing unit tests for `server_ping` payload generation in ~/Projects/youtube-mcp-server/tests/unit/test_baseline_server_tools.py

### Implementation for User Story 1

- [X] T012 [US1] Implement `server_ping` payload helper with required `status` and `timestamp` fields in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T013 [US1] Ensure `tools/call` response shape for `server_ping` remains MCP-envelope compliant in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T014 [US1] Refactor `server_ping` handler internals for readability while keeping US1 tests green in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Retrieve Server Metadata (Priority: P2)

**Goal**: Ensure `server_info` returns version, environment, and build metadata with safe fallbacks.

**Independent Test**: Invoke `server_info` with configured and partially missing metadata and verify required fields are present in successful responses.

### Tests for User Story 2 (REQUIRED)

- [X] T015 [P] [US2] Add failing contract assertions for `server_info` result schema in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T016 [P] [US2] Add failing integration tests for `server_info` configured and fallback scenarios in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T017 [P] [US2] Add failing unit tests for server metadata fallback behavior in ~/Projects/youtube-mcp-server/tests/unit/test_baseline_server_tools.py

### Implementation for User Story 2

- [X] T018 [US2] Register `server_info` with description and input schema in dispatcher defaults in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T019 [US2] Implement `server_info` handler returning `version`, `environment`, and `build` payload in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T020 [US2] Wire app bootstrap metadata into dispatcher construction for `server_info` execution in ~/Projects/youtube-mcp-server/src/mcp_server/app.py
- [X] T021 [US2] Refactor metadata-building helper logic while preserving US2 contract/integration coverage in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Confirm Registered Tools (Priority: P3)

**Goal**: Ensure `server_list_tools` reflects active registry tool names and descriptions, including baseline tools.

**Independent Test**: Invoke `server_list_tools` and validate returned entries include `server_ping`, `server_info`, and `server_list_tools`, then add an extra tool and verify the output updates.

### Tests for User Story 3 (REQUIRED)

- [X] T022 [P] [US3] Add failing contract assertions for `server_list_tools` result entries in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T023 [P] [US3] Add failing integration tests for dynamic registry reflection via `server_list_tools` in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T024 [P] [US3] Add failing unit tests for deterministic tool summary ordering in ~/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py

### Implementation for User Story 3

- [X] T025 [US3] Register `server_list_tools` with description and input schema in dispatcher defaults in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T026 [US3] Implement `server_list_tools` handler returning active registry name/description summaries in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T027 [US3] Ensure `server_list_tools` output remains aligned with `tools/list` descriptor contract in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T028 [US3] Refactor shared descriptor mapping between `list_tools` and `server_list_tools` paths in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation alignment, regression evidence, and cross-story consistency.

- [X] T029 [P] Update final baseline payload examples and coverage notes in ~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/contracts/mcp-baseline-server-tools-contract.md
- [X] T030 [P] Update execution evidence and smoke validation steps in ~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/quickstart.md
- [X] T031 Run full regression suite and record pass/fail evidence in ~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/quickstart.md
- [X] T032 [P] Update checklist notes with final verification status in ~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/checklists/requirements.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): No dependencies.
- Phase 2 (Foundational): Depends on Phase 1 and blocks all user story phases.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2; may execute in parallel with US1 after shared foundational tasks are complete.
- Phase 5 (US3): Depends on Phase 2; may execute in parallel with US1/US2 after shared foundational tasks are complete.
- Phase 6 (Polish): Depends on completion of all target user stories.

### User Story Dependencies

- US1 (P1): No dependency on other user stories.
- US2 (P2): No required dependency on US1; shares foundational dispatcher metadata plumbing.
- US3 (P3): No required dependency on US1/US2; shares foundational registry descriptors.

### Dependency Graph

- Setup -> Foundational -> {US1, US2, US3} -> Polish

### Within Each User Story

- Write failing tests first (Red).
- Implement minimal code to pass tests (Green).
- Refactor only after green and re-run affected suites (Refactor).

---

## Parallel Execution Examples

## Parallel Example: User Story 1

```bash
# Run US1 Red tasks in parallel
T009 tests/contract/test_mcp_transport_contract.py
T010 tests/integration/test_mcp_request_flow.py
T011 tests/unit/test_baseline_server_tools.py
```

## Parallel Example: User Story 2

```bash
# Run US2 Red tasks in parallel
T015 tests/contract/test_mcp_transport_contract.py
T016 tests/integration/test_mcp_request_flow.py
T017 tests/unit/test_baseline_server_tools.py
```

## Parallel Example: User Story 3

```bash
# Run US3 Red tasks in parallel
T022 tests/contract/test_mcp_transport_contract.py
T023 tests/integration/test_mcp_request_flow.py
T024 tests/unit/test_list_tools_method.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) Red -> Green -> Refactor.
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Deliver US1 and validate.
3. Deliver US2 and validate.
4. Deliver US3 and validate.
5. Complete Polish and final regression documentation.

### Parallel Team Strategy

1. Team completes Setup and Foundational together.
2. After Foundational, developers split across US1, US2, and US3 Red tasks in separate files.
3. Green/Refactor proceeds per story with shared regression reruns before polish.

---

## Notes

- All tasks follow the required checkbox, task ID, optional `[P]`, optional `[US#]`, and file-path format.
- `[P]` tasks are limited to work that can proceed without unresolved dependencies.
- Each user story remains independently testable via its documented independent test criteria.
