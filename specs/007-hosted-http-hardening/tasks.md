# Tasks: FND-007 Hosted Probe Semantics + HTTP Hardening

**Input**: Design documents from `/specs/007-hosted-http-hardening/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout at repository root with `src/`, `tests/`, and feature docs under `specs/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the hosted HTTP hardening test and contract scaffolding for this feature

- [X] T001 Create FND-007 task scaffolding references in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/tasks.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md`
- [X] T002 [P] Create hosted HTTP unit test scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py`
- [X] T003 [P] Create hosted route integration test scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared hosted request-classification and response-mapping primitives required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing unit tests for hosted request classification and status selection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py`
- [X] T005 [P] Add failing integration tests for Cloud Run entrypoint method and path routing in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T006 [P] Add failing contract coverage for hosted route semantics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`
- [X] T007 Implement shared hosted request classification and response metadata helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T008 [P] Implement hosted JSON response-writing and content-type helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T009 [P] Document foundational hosted status-mapping rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`
- [X] T010 Refactor shared classification and response-mapping paths while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py` green

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Trust Hosted Readiness Signals (Priority: P1) 🎯 MVP

**Goal**: Make hosted `/readyz` and `/healthz` trustworthy for operators and platform probes by aligning HTTP status with actual readiness and liveness state

**Independent Test**: Call hosted `/readyz` under ready and not-ready startup states and hosted `/healthz` under normal operation; verify that status codes and machine-readable bodies match the service state

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Add failing contract tests for `/healthz` and `/readyz` hosted status semantics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py`
- [X] T012 [P] [US1] Add failing integration tests for ready and not-ready hosted probe responses in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py`
- [X] T013 [US1] Add failing unit tests for readiness outcome-to-status mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement hosted readiness status mapping for ready and not-ready states in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T015 [US1] Preserve lightweight liveness and readiness payload behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/health.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T016 [US1] Document hosted probe expectations and retry guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`
- [X] T017 [US1] Refactor probe route handling to use one shared readiness/liveness decision path while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py` green

**Checkpoint**: User Story 1 is independently functional and testable as the MVP

---

## Phase 4: User Story 2 - Get Predictable Hosted MCP Route Behavior (Priority: P1)

**Goal**: Make hosted `/mcp` deterministic for valid requests, malformed requests, unsupported methods, and unsupported media types

**Independent Test**: Send valid, malformed, unsupported-method, and unsupported-content-type requests to hosted `/mcp`; verify expected HTTP status, JSON content type, and success or structured error envelope

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract tests for hosted `/mcp` status codes and error envelopes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`
- [X] T019 [P] [US2] Add failing integration tests for malformed JSON and unsupported media type handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T020 [US2] Add failing integration tests for successful hosted MCP request content-type and response handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement hosted `/mcp` request validation for JSON decoding and supported media types in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T022 [US2] Implement hosted MCP status-code mapping for success and client-error outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T023 [US2] Preserve normalized MCP error payloads and request correlation for hosted failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T024 [US2] Document hosted MCP request rules and failure semantics in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`
- [X] T025 [US2] Refactor hosted MCP response handling to minimize branching while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py` green

**Checkpoint**: User Stories 1 and 2 both work independently, and hosted MCP behavior is deterministic

---

## Phase 5: User Story 3 - Detect Unsupported Hosted Routes Quickly (Priority: P2)

**Goal**: Make unsupported paths and unsupported methods easy to distinguish so operators and client integrators can diagnose misrouted traffic quickly

**Independent Test**: Send requests to unknown hosted paths and supported paths with unsupported methods; verify the service returns the correct not-found or method-related status plus machine-readable JSON errors where bodies are returned

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing contract tests for unknown-path and unsupported-method behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py`
- [X] T027 [P] [US3] Add failing integration tests for unknown-path and wrong-method hosted requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T028 [US3] Add failing unit tests for `method_not_allowed` versus `not_found` classification in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py`

### Implementation for User Story 3

- [X] T029 [US3] Implement unknown-path and unsupported-method classification in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T030 [US3] Implement machine-readable JSON error responses for unsupported hosted requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`
- [X] T031 [US3] Document unsupported-route diagnostics and expected statuses in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`
- [X] T032 [US3] Refactor route classification and error-body selection while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py` green

**Checkpoint**: All user stories are independently functional and unsupported hosted traffic is diagnosable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression, local-to-hosted parity validation, and cross-story documentation cleanup

- [X] T033 [P] Add regression coverage for local-to-hosted status parity across `/healthz`, `/readyz`, `/mcp`, and unknown paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T034 [P] Update feature execution notes and validation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/tasks.md`
- [X] T035 Run and record full regression validation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1 completion and blocks all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 2 completion and uses the shared response-mapping primitives from US1
- **Phase 5 (US3)**: Depends on Phase 2 completion and benefits from the route-classification behavior stabilized in US1 and US2
- **Phase 6 (Polish)**: Depends on completion of all targeted user stories

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational and is the suggested MVP
- **US2 (P1)**: Can start after Foundational but is safest after US1 establishes probe and response-mapping behavior
- **US3 (P2)**: Can start after Foundational but depends on shared route classification and is easiest after US2 hardens hosted request failures

### Dependency Graph

- Foundation: `T001 -> T004/T005/T006 -> T007/T008/T009 -> T010`
- US1: `T011/T012/T013 -> T014/T015/T016 -> T017`
- US2: `T018/T019/T020 -> T021/T022/T023/T024 -> T025`
- US3: `T026/T027/T028 -> T029/T030/T031 -> T032`
- Polish: `T033/T034 -> T035`

### Within Each User Story

- Red tests before Green implementation
- Green implementation before Refactor
- Refactor before dependent story completion
- Re-run affected automated suites before marking the story done

### Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`
- `T005`, `T006`, `T008`, and `T009` can run in parallel after `T004`
- `T011` and `T012` can run in parallel for US1
- `T018` and `T019` can run in parallel for US2
- `T026` and `T027` can run in parallel for US3
- `T033` and `T034` can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 Red tasks together
Task: "Add failing contract tests for /healthz and /readyz hosted status semantics in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py"
Task: "Add failing integration tests for ready and not-ready hosted probe responses in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py"
```

## Parallel Example: User Story 2

```bash
# Launch User Story 2 Red tasks together
Task: "Add failing contract tests for hosted /mcp status codes and error envelopes in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "Add failing integration tests for malformed JSON and unsupported media type handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 3

```bash
# Launch User Story 3 Red tasks together
Task: "Add failing contract tests for unknown-path and unsupported-method behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py"
Task: "Add failing integration tests for unknown-path and wrong-method hosted requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate hosted `/readyz` and `/healthz` independently against the story test criteria
5. Stop for MVP review before widening scope

### Incremental Delivery

1. Finish Setup + Foundational to establish shared hosted HTTP classification and response-mapping primitives
2. Deliver US1 for trustworthy readiness and liveness probe semantics
3. Deliver US2 for deterministic hosted MCP behavior
4. Deliver US3 for unsupported-route diagnostics
5. Finish with Polish and full regression validation

### Parallel Team Strategy

1. One developer completes Setup and Foundational tasks
2. After foundation stabilizes:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Finish with shared polish and regression validation

---

## Notes

- All tasks use the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` for story phases, and exact file paths
- Suggested MVP scope is **Phase 3 / User Story 1**
- Each user story includes explicit Red, Green, and Refactor work so it can be implemented and tested independently
