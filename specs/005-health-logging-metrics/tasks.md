# Tasks: FND-005 Health, Logging, Error Model, Metrics

**Input**: Design documents from `/specs/005-health-logging-metrics/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish FND-005 task scaffolding and new test modules.

- [X] T001 Create FND-005 test module placeholders in `tests/contract/test_operational_observability_contract.py`, `tests/integration/test_request_observability.py`, and `tests/unit/test_metrics_state.py`
- [X] T002 [P] Create observability module placeholder in `src/mcp_server/observability.py`
- [X] T003 [P] Add FND-005 execution notes section in `~/Projects/youtube-mcp-server/specs/005-health-logging-metrics/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared request context, logging, and metrics primitives required by all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add failing unit tests for request context extraction and request ID generation in `tests/unit/test_request_context.py`
- [X] T005 [P] Add failing unit tests for metric counters and latency summary calculations in `tests/unit/test_metrics_state.py`
- [X] T006 [P] Add failing integration tests for invalid path instrumentation behavior in `tests/integration/test_request_observability.py`
- [X] T007 Implement shared `RequestContext` builder and endpoint classification helpers in `src/mcp_server/observability.py`
- [X] T008 [P] Implement in-memory metrics recorder (counts by endpoint/outcome and latency observations) in `src/mcp_server/observability.py`
- [X] T009 [P] Implement structured log event formatter with required fields in `src/mcp_server/observability.py`
- [X] T010 Wire foundational observability helpers into transport entrypoint without changing feature behavior in `src/mcp_server/transport/http.py`
- [X] T011 Refactor duplicated context/latency mapping logic after foundational tests pass in `src/mcp_server/observability.py` and `src/mcp_server/transport/http.py`

**Checkpoint**: Foundation ready; user story implementation can begin.

---

## Phase 3: User Story 1 - Verify Service Health (Priority: P1) 🎯 MVP

**Goal**: Operators can quickly assess liveness/readiness and receive accurate readiness reason metadata.

**Independent Test**: Call `/healthz` and `/readyz` under ready and not-ready startup states and validate payload contract plus request observability fields.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T012 [P] [US1] Add failing contract tests for `/healthz` and `/readyz` payload shape and status behavior in `tests/contract/test_operational_observability_contract.py`
- [X] T013 [P] [US1] Add failing integration tests for health/readiness request logging fields (`requestId`, `path`, `status`, `latencyMs`) in `tests/integration/test_request_observability.py`
- [X] T014 [US1] Add failing integration test for readiness not-ready reason metadata under invalid startup config in `tests/integration/test_readiness_flow.py`

### Implementation for User Story 1

- [X] T015 [US1] Ensure `/healthz` and `/readyz` responses remain contract-compliant with machine-readable statuses in `src/mcp_server/health.py` and `src/mcp_server/transport/http.py`
- [X] T016 [US1] Propagate generated request IDs for health/readiness requests into response metadata and request logs in `src/mcp_server/transport/http.py`
- [X] T017 [US1] Emit metrics for health/readiness request count, outcome, and latency observations in `src/mcp_server/observability.py` and `src/mcp_server/transport/http.py`
- [X] T018 [US1] Refactor health/readiness handling to share one instrumentation path while keeping tests green in `src/mcp_server/transport/http.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Trace Request Execution (Priority: P1)

**Goal**: Developers can trace MCP request lifecycle by request ID with path, tool, status, and latency.

**Independent Test**: Execute MCP initialize/tools/list/tools/call requests with and without request IDs and verify correlated structured log output with tool attribution.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add failing integration tests for MCP request correlation and generated request IDs in `tests/integration/test_request_observability.py`
- [X] T020 [P] [US2] Add failing integration tests for tool call log field coverage (`toolName`, `status`, `latencyMs`) in `tests/integration/test_mcp_request_flow.py`
- [X] T021 [US2] Add failing contract tests for request ID correlation behavior on MCP responses in `tests/contract/test_mcp_transport_contract.py`

### Implementation for User Story 2

- [X] T022 [US2] Add request ID fallback generation for MCP payloads missing `id` in `src/mcp_server/protocol/methods.py` and `src/mcp_server/transport/http.py`
- [X] T023 [US2] Add tool-aware structured logging emission for `tools/call` requests in `src/mcp_server/transport/http.py` and `src/mcp_server/observability.py`
- [X] T024 [US2] Ensure request correlation values are consistent across logs and response envelopes in `src/mcp_server/protocol/envelope.py` and `src/mcp_server/protocol/methods.py`
- [X] T025 [US2] Refactor MCP route instrumentation to minimize branching duplication while preserving behavior in `src/mcp_server/transport/http.py`

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Receive Consistent Errors and Metrics (Priority: P2)

**Goal**: Clients receive consistent `code/message/details` errors and operators receive request count/outcome/latency metrics with percentile-ready data.

**Independent Test**: Trigger malformed payloads, unknown method/tool, and internal error paths; validate normalized error shape and metric emission for success/error traffic.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing unit tests asserting all error responses include `code`, `message`, and `details` keys in `tests/unit/test_envelope_contract.py`
- [X] T027 [P] [US3] Add failing contract tests for normalized errors across invalid path/method/tool scenarios in `tests/contract/test_operational_observability_contract.py`
- [X] T028 [P] [US3] Add failing integration tests for metrics totals, success/error segmentation, and latency summary outputs in `tests/integration/test_request_observability.py`

### Implementation for User Story 3

- [X] T029 [US3] Harden error normalization and sanitization paths to guarantee `code/message/details` on all client-visible failures in `src/mcp_server/protocol/envelope.py`, `src/mcp_server/protocol/methods.py`, and `src/mcp_server/transport/http.py`
- [X] T030 [US3] Implement endpoint and tool dimension metrics recording for both success and error outcomes in `src/mcp_server/observability.py` and `src/mcp_server/transport/http.py`
- [X] T031 [US3] Expose latency percentile-capable metric snapshot helpers for test assertions in `src/mcp_server/observability.py`
- [X] T032 [US3] Refactor error/metrics glue code to reduce duplication and preserve contract compatibility in `src/mcp_server/protocol/methods.py` and `src/mcp_server/transport/http.py`

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression safety, documentation, and cross-story hardening.

- [X] T033 [P] Add regression tests for mixed endpoint traffic (`/healthz`, `/readyz`, `/mcp`, invalid path) in `tests/integration/test_request_observability.py`
- [X] T034 Update operator-facing observability contract notes and examples in `~/Projects/youtube-mcp-server/specs/005-health-logging-metrics/contracts/operational-observability-contract.md`
- [X] T035 Run and record full regression test evidence in `~/Projects/youtube-mcp-server/specs/005-health-logging-metrics/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run in parallel with Phase 3 after foundation is stable.
- **Phase 5 (US3)**: Depends on Phase 2 completion and benefits from Phase 4 instrumentation hooks.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational instrumentation exists.
- **US2 (P1)**: Independent after foundational instrumentation exists; no hard dependency on US1 behavior.
- **US3 (P2)**: Depends on shared instrumentation and MCP path handling from foundational work; independent from US1 business behavior.

### Dependency Graph

- Foundation: `T001 -> T004/T005/T006 -> T007/T008/T009 -> T010 -> T011`
- US1: `T012/T013/T014 -> T015/T016/T017 -> T018`
- US2: `T019/T020/T021 -> T022/T023/T024 -> T025`
- US3: `T026/T027/T028 -> T029/T030/T031 -> T032`
- Polish: `T033/T034 -> T035`

### Within Each User Story

- Red tests first and failing (`T012-014`, `T019-021`, `T026-028`)
- Green implementation next (`T015-017`, `T022-024`, `T029-031`)
- Refactor only after green tests pass (`T018`, `T025`, `T032`)

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T012 [US1] contract health/readiness tests in tests/contract/test_operational_observability_contract.py"
Task: "T013 [US1] integration observability tests in tests/integration/test_request_observability.py"
```

### User Story 2

```bash
Task: "T019 [US2] request ID correlation tests in tests/integration/test_request_observability.py"
Task: "T020 [US2] tool logging tests in tests/integration/test_mcp_request_flow.py"
```

### User Story 3

```bash
Task: "T026 [US3] error envelope unit tests in tests/unit/test_envelope_contract.py"
Task: "T028 [US3] metrics integration tests in tests/integration/test_request_observability.py"
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) and validate `/healthz` + `/readyz` operational behavior.
3. Stop for MVP verification against the independent test criteria.

### Incremental Delivery

1. Ship US1 after foundational completion.
2. Add US2 tracing and correlation behavior.
3. Add US3 error-model and metrics hardening.
4. Finish with polish regression and documentation updates.

### Parallel Team Strategy

1. One engineer completes foundational tasks (`T004-T011`).
2. Then parallelize story work:
   - Engineer A: US1 (`T012-T018`)
   - Engineer B: US2 (`T019-T025`)
   - Engineer C: US3 (`T026-T032`)

---

## Notes

- [P] tasks indicate different files and no blocking dependency on incomplete tasks.
- [US1]/[US2]/[US3] labels map directly to spec user stories.
- All tasks include explicit file paths and are immediately executable.
- Keep response contract compatibility checks active while adding observability behavior.
