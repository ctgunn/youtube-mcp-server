---
description: "Task list for FND-001 MCP transport and handshake implementation"
---

# Tasks: MCP Transport + Handshake (FND-001)

**Input**: Design documents from `/specs/001-mcp-transport-handshake/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Red-Green-Refactor execution is mandatory per constitution and feature spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout at repository root: `src/`, `tests/`
- Feature docs are under `specs/001-mcp-transport-handshake/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish Python service and test scaffolding for MCP transport work.

- [X] T001 Create package skeleton and module init files in src/mcp_server/__init__.py, src/mcp_server/transport/__init__.py, src/mcp_server/protocol/__init__.py, src/mcp_server/tools/__init__.py
- [X] T002 Create application entrypoint scaffold in src/mcp_server/app.py and HTTP transport stub in src/mcp_server/transport/http.py
- [X] T003 [P] Create protocol module stubs in src/mcp_server/protocol/methods.py and src/mcp_server/protocol/envelope.py
- [X] T004 [P] Create dispatcher stub in src/mcp_server/tools/dispatcher.py
- [X] T005 [P] Create test directories and baseline conftest in tests/contract/conftest.py, tests/integration/conftest.py, tests/unit/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared request parsing, envelope shaping, and error mapping used by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Add Red tests for common envelope and error-shape contracts in tests/unit/test_envelope_contract.py
- [X] T007 Implement Green envelope/error helpers in src/mcp_server/protocol/envelope.py to satisfy T006
- [X] T008 Refactor envelope helpers for reuse and determinism, then re-run tests in tests/unit/test_envelope_contract.py
- [X] T009 Add Red tests for method routing and unsupported method behavior in tests/unit/test_method_routing.py
- [X] T010 Implement Green method router skeleton in src/mcp_server/protocol/methods.py to satisfy T009
- [X] T011 Refactor routing code paths and rerun tests in tests/unit/test_method_routing.py and tests/unit/test_envelope_contract.py
- [X] T012 Implement HTTP `/mcp` request parsing/wiring in src/mcp_server/transport/http.py and app integration in src/mcp_server/app.py

**Checkpoint**: Foundation ready; user story implementation can proceed.

---

## Phase 3: User Story 1 - Initialize MCP Session (Priority: P1) 🎯 MVP

**Goal**: Support MCP `initialize` handshake with capability declaration and structured errors.

**Independent Test**: Send valid and malformed initialize requests to `/mcp` and verify success/error envelopes.

### Tests for User Story 1 (REQUIRED)

- [X] T013 [P] [US1] Add Red contract tests for initialize success and malformed initialize in tests/contract/test_mcp_transport_contract.py
- [X] T014 [P] [US1] Add Red unit tests for initialize validation paths in tests/unit/test_initialize_method.py

### Implementation for User Story 1

- [X] T015 [US1] Implement Green initialize handler and capability payload in src/mcp_server/protocol/methods.py
- [X] T016 [US1] Wire initialize method dispatch through transport endpoint in src/mcp_server/transport/http.py
- [X] T017 [US1] Ensure initialize responses include requestId meta and no stack traces via src/mcp_server/protocol/envelope.py
- [X] T018 [US1] Refactor initialize logic for readability and rerun tests in tests/contract/test_mcp_transport_contract.py and tests/unit/test_initialize_method.py

**Checkpoint**: Initialize handshake is fully functional and testable.

---

## Phase 4: User Story 2 - Discover Registered Tools (Priority: P2)

**Goal**: Return deterministic tool listing through MCP `tools/list` flow.

**Independent Test**: Request tool listing and verify deterministic tool metadata envelope.

### Tests for User Story 2 (REQUIRED)

- [X] T019 [P] [US2] Add Red contract tests for tools/list success and empty-registry behavior in tests/contract/test_mcp_transport_contract.py
- [X] T020 [P] [US2] Add Red unit tests for list method behavior in tests/unit/test_list_tools_method.py

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement in-memory tool descriptor provider for FND-001 in src/mcp_server/tools/dispatcher.py
- [X] T022 [US2] Implement Green tools/list handler in src/mcp_server/protocol/methods.py
- [X] T023 [US2] Wire tools/list routing in src/mcp_server/transport/http.py
- [X] T024 [US2] Refactor list serialization ordering and rerun tests in tests/contract/test_mcp_transport_contract.py and tests/unit/test_list_tools_method.py

**Checkpoint**: Tool discovery works independently with deterministic output.

---

## Phase 5: User Story 3 - Invoke Tool via MCP Path (Priority: P3)

**Goal**: Invoke registered tool and return structured success/error envelopes.

**Independent Test**: Invoke `server_ping` successfully and verify `RESOURCE_NOT_FOUND` for unknown tool.

### Tests for User Story 3 (REQUIRED)

- [X] T025 [P] [US3] Add Red contract tests for tools/call success and unknown tool error in tests/contract/test_mcp_transport_contract.py
- [X] T026 [P] [US3] Add Red unit tests for invocation error mapping in tests/unit/test_invoke_error_mapping.py
- [X] T027 [P] [US3] Add Red integration flow test for initialize -> tools/list -> tools/call in tests/integration/test_mcp_request_flow.py

### Implementation for User Story 3

- [X] T028 [P] [US3] Implement baseline callable `server_ping` behavior in src/mcp_server/tools/dispatcher.py
- [X] T029 [US3] Implement Green tools/call handler and invocation routing in src/mcp_server/protocol/methods.py
- [X] T030 [US3] Wire tools/call path and error mapping in src/mcp_server/transport/http.py
- [X] T031 [US3] Refactor invocation and error-path code while preserving envelopes; rerun tests in tests/contract/test_mcp_transport_contract.py, tests/unit/test_invoke_error_mapping.py, and tests/integration/test_mcp_request_flow.py

**Checkpoint**: Invocation path works and remains independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality and documentation pass spanning all user stories.

- [X] T032 [P] Add test execution commands and FND-001 usage notes to /Users/ctgunn/Projects/youtube-mcp-server/specs/001-mcp-transport-handshake/quickstart.md
- [X] T033 Validate contract doc and implementation parity in /Users/ctgunn/Projects/youtube-mcp-server/specs/001-mcp-transport-handshake/contracts/mcp-transport-contract.md
- [X] T034 Run full FND-001 suites and capture results in /Users/ctgunn/Projects/youtube-mcp-server/specs/001-mcp-transport-handshake/checklists/requirements.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Phase 1 and blocks all stories.
- User stories (Phase 3-5): depend on Phase 2 completion.
- Polish (Phase 6): depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: starts after Foundational phase.
- **US2 (P2)**: starts after Foundational; functionally independent but can reuse US1 transport utilities.
- **US3 (P3)**: starts after Foundational; depends on list/dispatch scaffolding from US2.

### Within Each User Story

- Red tests MUST be written and fail before implementation.
- Green implementation MUST be minimal and satisfy failing tests.
- Refactor MUST preserve behavior and be followed by full affected test reruns.

### Dependency Graph

- Foundational -> US1 -> US2 -> US3 -> Polish
- Parallel opportunities exist inside each phase where tasks are marked `[P]`.

---

## Parallel Example: User Story 3

```bash
# Red tests in parallel:
Task: "T025 [US3] contract tests in tests/contract/test_mcp_transport_contract.py"
Task: "T026 [US3] unit tests in tests/unit/test_invoke_error_mapping.py"
Task: "T027 [US3] integration flow in tests/integration/test_mcp_request_flow.py"

# Green implementation in parallel where safe:
Task: "T028 [US3] baseline dispatcher callable in src/mcp_server/tools/dispatcher.py"
Task: "T030 [US3] transport wiring in src/mcp_server/transport/http.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Complete US1 Red -> Green -> Refactor.
3. Validate initialize handshake with contract + unit tests.
4. Demo initialization readiness.

### Incremental Delivery

1. Deliver US1 (initialize).
2. Deliver US2 (list tools) and validate independently.
3. Deliver US3 (invoke tool) and validate end-to-end flow.
4. Apply polish and rerun complete suite.

### Parallel Team Strategy

1. Engineer A: Red tests for current story.
2. Engineer B: Green implementation for previous approved failing tests.
3. Engineer C: Refactor and regression reruns after Green passes.

---

## Notes

- All tasks follow required checkbox/ID/label/path format.
- `[P]` indicates safe parallelism with no unresolved file conflicts.
- Red-Green-Refactor evidence must be preserved in PR notes.
