# Tasks: Tool Registry + Dispatcher (FND-002)

**Input**: Design documents from `/specs/002-tool-registry-dispatcher/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tool-registry-dispatch-contract.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared test scaffolding and implementation entry points.

- [X] T001 Add FND-002 test fixture helpers for sample tool definitions in `tests/unit/conftest.py`
- [X] T002 [P] Add integration helper for custom dispatcher wiring in `tests/integration/conftest.py`
- [X] T003 [P] Add contract helper for reusable MCP request payload builders in `tests/contract/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Complete shared registry/dispatch infrastructure required by all stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Define normalized tool key helper and registry entry shape in `src/mcp_server/tools/dispatcher.py`
- [X] T005 Extend dispatcher construction to accept explicit tool registration input in `src/mcp_server/tools/dispatcher.py`
- [X] T006 Add shared dispatch argument-shape guard for MCP call handling in `src/mcp_server/protocol/methods.py`
- [X] T007 Align shared envelope error detail expectations with FND-002 contract in `tests/unit/test_envelope_contract.py`

**Checkpoint**: Foundation ready for independently testable user stories.

---

## Phase 3: User Story 1 - Register MCP Tools (Priority: P1) MVP

**Goal**: Allow developers to register tools with required attributes and deterministic listing behavior.

**Independent Test**: Register a valid sample tool and verify it appears in `tools/list`; attempt invalid and duplicate registrations and verify structured rejection.

### Tests for User Story 1 (REQUIRED)

- [X] T008 [US1] Add failing registry validation tests for missing fields in `tests/unit/test_tool_registry.py`
- [X] T009 [P] [US1] Add failing duplicate-name rejection tests in `tests/unit/test_tool_registry_duplicates.py`
- [X] T010 [P] [US1] Add failing deterministic tool listing tests in `tests/unit/test_list_tools_method.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement `register_tool` validation and required attributes enforcement in `src/mcp_server/tools/dispatcher.py`
- [X] T012 [US1] Implement duplicate normalized-name rejection in `src/mcp_server/tools/dispatcher.py`
- [X] T013 [US1] Implement deterministic list ordering and descriptor shaping in `src/mcp_server/tools/dispatcher.py`
- [X] T014 [US1] Refactor registration/list internals to remove duplication while preserving behavior in `src/mcp_server/tools/dispatcher.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Dispatch Valid Tool Calls (Priority: P2)

**Goal**: Route valid invocation requests to registered handlers and block invalid inputs with structured validation errors.

**Independent Test**: Call a registered tool with valid arguments and verify structured success; call with invalid argument shape and verify structured `INVALID_ARGUMENT` response without handler execution.

### Tests for User Story 2 (REQUIRED)

- [X] T015 [P] [US2] Add failing unit tests for successful dispatch routing in `tests/unit/test_method_routing.py`
- [X] T016 [P] [US2] Add failing unit tests for invalid `arguments` handling in `tests/unit/test_invoke_error_mapping.py`
- [X] T017 [P] [US2] Add failing integration coverage for register-list-call happy path in `tests/integration/test_mcp_request_flow.py`
- [X] T018 [P] [US2] Add failing contract assertions for call argument validation errors in `tests/contract/test_mcp_transport_contract.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement contract-aware argument validation before handler execution in `src/mcp_server/tools/dispatcher.py`
- [X] T020 [US2] Implement dispatch path updates for valid call routing and result shaping in `src/mcp_server/protocol/methods.py`
- [X] T021 [US2] Integrate dispatcher validation exceptions with MCP-safe error mapping in `src/mcp_server/protocol/methods.py`
- [X] T022 [US2] Refactor call-path validation and execution flow for readability with tests kept green in `src/mcp_server/protocol/methods.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Handle Unknown Tool Calls Safely (Priority: P3)

**Goal**: Return deterministic `RESOURCE_NOT_FOUND` behavior for unknown tool calls with troubleshooting details.

**Independent Test**: Invoke an unregistered tool name and verify structured `RESOURCE_NOT_FOUND` response including requested tool name, with no handler execution side effects.

### Tests for User Story 3 (REQUIRED)

- [X] T023 [P] [US3] Add failing unit tests for unknown tool detail payload in `tests/unit/test_invoke_error_mapping.py`
- [X] T024 [P] [US3] Add failing integration tests for unknown tool request behavior in `tests/integration/test_mcp_request_flow.py`
- [X] T025 [P] [US3] Add failing contract checks for unknown tool error envelope in `tests/contract/test_mcp_transport_contract.py`

### Implementation for User Story 3

- [X] T026 [US3] Implement unknown-tool lookup failure mapping with request tool detail in `src/mcp_server/protocol/methods.py`
- [X] T027 [US3] Ensure unknown-tool paths bypass handler execution and keep deterministic errors in `src/mcp_server/tools/dispatcher.py`
- [X] T028 [US3] Refactor unknown-tool error mapping constants/messages for consistency in `src/mcp_server/protocol/methods.py`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks, docs alignment, and regression evidence.

- [X] T029 [P] Update FND-002 quickstart verification notes with final command evidence in `specs/002-tool-registry-dispatcher/quickstart.md`
- [X] T030 [P] Update FND-002 contract notes for final error/detail behavior in `specs/002-tool-registry-dispatcher/contracts/mcp-tool-registry-dispatch-contract.md`
- [X] T031 Run full regression suite and record final status in `specs/002-tool-registry-dispatcher/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user story phases.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and US1 registry lifecycle outputs.
- **Phase 5 (US3)**: Depends on Phase 2 and US2 call-path behavior.
- **Phase 6 (Polish)**: Depends on completion of all implemented user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; establishes registry lifecycle MVP.
- **US2 (P2)**: Depends on US1 registration and lookup behavior.
- **US3 (P3)**: Depends on US2 dispatch/error pathways.

### Within Each User Story

- Tests first and failing (Red).
- Minimal code to pass tests (Green).
- Refactor only after tests pass; rerun affected suites (Refactor).

---

## Parallel Execution Examples

## Parallel Example: User Story 1

```bash
# Parallel Red tasks for US1
T008 tests/unit/test_tool_registry.py
T009 tests/unit/test_tool_registry_duplicates.py
T010 tests/unit/test_list_tools_method.py
```

## Parallel Example: User Story 2

```bash
# Parallel Red tasks for US2
T015 tests/unit/test_method_routing.py
T016 tests/unit/test_invoke_error_mapping.py
T017 tests/integration/test_mcp_request_flow.py
T018 tests/contract/test_mcp_transport_contract.py
```

## Parallel Example: User Story 3

```bash
# Parallel Red tasks for US3
T023 tests/unit/test_invoke_error_mapping.py
T024 tests/integration/test_mcp_request_flow.py
T025 tests/contract/test_mcp_transport_contract.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Deliver US1 (registry lifecycle).
2. Deliver US2 (valid dispatch and argument validation).
3. Deliver US3 (unknown-tool safety behavior).
4. Complete Phase 6 polish and regression evidence.

### Parallel Team Strategy

1. Team completes Phase 1 and Phase 2 together.
2. One developer drives US1 Green tasks while others prepare US2/US3 Red tasks in separate files.
3. Execute story phases in dependency order while maximizing parallel test authoring.

---

## Notes

- [P] tasks are limited to work in different files with no blocking dependency on incomplete tasks.
- Story labels map directly to spec user stories for traceability.
- Every task includes an explicit file path and follows required checklist format.
