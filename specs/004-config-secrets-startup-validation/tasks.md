# Tasks: Config + Secrets + Startup Validation (FND-004)

**Input**: Design documents from `/specs/004-config-secrets-startup-validation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story so each story is independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the runtime config/readiness work surface used by all stories.

- [X] T001 Create runtime configuration module scaffold in src/mcp_server/config.py
- [X] T002 Create readiness state helper module scaffold in src/mcp_server/health.py
- [X] T003 [P] Create FND-004 test modules in tests/unit/test_runtime_config_validation.py, tests/integration/test_startup_config_validation_flow.py, and tests/contract/test_readiness_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared validation and transport plumbing that blocks all user stories until complete.

**⚠️ CRITICAL**: No user story implementation starts until this phase is complete.

- [X] T004 Add failing foundational redaction tests in tests/unit/test_envelope_contract.py
- [X] T005 [P] Add failing foundational startup bootstrap tests in tests/integration/test_startup_config_validation_flow.py
- [X] T006 [P] Add failing foundational transport path tests for /healthz and /readyz in tests/contract/test_readiness_contract.py
- [X] T007 Implement shared validation result and redaction utilities in src/mcp_server/config.py
- [X] T008 Implement base /healthz and /readyz transport routing in src/mcp_server/transport/http.py
- [X] T009 Wire startup validation state into app factory in src/mcp_server/app.py
- [X] T010 Refactor shared validation fixtures and helpers in tests/unit/test_runtime_config_validation.py and tests/integration/test_startup_config_validation_flow.py
- [X] T011 Record foundational Red-Green-Refactor execution notes in specs/004-config-secrets-startup-validation/quickstart.md

**Checkpoint**: Foundation complete; user stories can be implemented independently.

---

## Phase 3: User Story 1 - Fail Fast on Missing Required Configuration (Priority: P1) 🎯 MVP

**Goal**: Reject invalid startup configuration before the service can accept traffic.

**Independent Test**: Start app with missing/blank required configuration and verify startup fails with a clear non-sensitive configuration error.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T012 [P] [US1] Add failing unit tests for missing and blank required config keys in tests/unit/test_runtime_config_validation.py
- [X] T013 [P] [US1] Add failing integration tests for startup fail-fast behavior in tests/integration/test_startup_config_validation_flow.py
- [X] T014 [P] [US1] Add failing contract tests for CONFIG_VALIDATION_ERROR response shape in tests/contract/test_readiness_contract.py

### Implementation for User Story 1

- [X] T015 [US1] Implement required non-secret configuration rules in src/mcp_server/config.py
- [X] T016 [US1] Enforce fail-fast startup behavior in src/mcp_server/app.py
- [X] T017 [US1] Implement sanitized startup validation error mapping in src/mcp_server/protocol/envelope.py
- [X] T018 [US1] Refactor startup validation flow and remove duplication in src/mcp_server/config.py

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Deterministic Environment Profiles (Priority: P2)

**Goal**: Ensure `dev`, `staging`, and `prod` apply deterministic profile-specific config rules.

**Independent Test**: Run startup validation against each supported profile and verify deterministic pass/fail behavior; verify unsupported profiles fail clearly.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add failing unit tests for supported and unsupported profile values in tests/unit/test_runtime_profiles.py
- [X] T020 [P] [US2] Add failing integration profile matrix tests in tests/integration/test_profile_startup_matrix.py
- [X] T021 [P] [US2] Add failing contract assertions for unsupported profile errors in tests/contract/test_readiness_contract.py

### Implementation for User Story 2

- [X] T022 [US2] Implement RuntimeConfigProfile mapping and per-profile requirement selection in src/mcp_server/config.py
- [X] T023 [US2] Wire MCP_ENVIRONMENT profile resolution and deterministic defaults in src/mcp_server/app.py
- [X] T024 [US2] Document profile-specific requirement behavior in README.md
- [X] T025 [US2] Refactor profile resolution and requirement lookup helpers in src/mcp_server/config.py

**Checkpoint**: User Stories 1 and 2 both pass independently.

---

## Phase 5: User Story 3 - Readiness Reflects Config and Secret Validity (Priority: P3)

**Goal**: Make readiness report `ready` only when config and secrets are valid, otherwise `not_ready` with non-sensitive reasons.

**Independent Test**: Validate `/readyz` returns ready for valid config/secret state and not_ready when required secrets are missing or invalid.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing contract tests for /readyz ready/not_ready response shape in tests/contract/test_readiness_contract.py
- [X] T027 [P] [US3] Add failing integration tests for readiness transitions in tests/integration/test_readiness_flow.py
- [X] T028 [P] [US3] Add failing unit tests for secret requirement availability and reason codes in tests/unit/test_readiness_state.py

### Implementation for User Story 3

- [X] T029 [US3] Implement secret requirement validation and readiness state derivation in src/mcp_server/config.py
- [X] T030 [US3] Implement /readyz and /healthz responses with non-sensitive diagnostics in src/mcp_server/transport/http.py
- [X] T031 [US3] Propagate validation state from app bootstrap to transport readiness checks in src/mcp_server/app.py
- [X] T032 [US3] Refactor readiness response construction for reuse in src/mcp_server/transport/http.py

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, and full regression evidence.

- [X] T033 [P] Add required and secret-backed environment variable examples in .env.example
- [X] T034 [P] Update implementation and validation workflow guidance in specs/004-config-secrets-startup-validation/quickstart.md
- [X] T035 Add full regression and targeted suite evidence in specs/004-config-secrets-startup-validation/quickstart.md
- [X] T036 [P] Add regression coverage for secret-redaction edge cases in tests/unit/test_envelope_contract.py
- [X] T037 Update feature delivery notes and completion status in specs/004-config-secrets-startup-validation/plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user-story work.
- **Phase 3 (US1)**: Depends on Phase 2; MVP slice.
- **Phase 4 (US2)**: Depends on Phase 2; may run in parallel with US1 after foundation is complete.
- **Phase 5 (US3)**: Depends on Phase 2 and builds on readiness plumbing from foundational tasks.
- **Phase 6 (Polish)**: Depends on completion of selected user stories.

### User Story Dependency Graph

- **US1 (P1)**: Independent after Phase 2.
- **US2 (P2)**: Independent after Phase 2; uses shared config model but not US1 business flow.
- **US3 (P3)**: Independent after Phase 2; reuses shared config/profile outputs and transport readiness paths.

Suggested completion order: `US1 -> US2 -> US3`.

### Within Each User Story

- Write tests first and confirm failure (Red).
- Implement minimum code to pass tests (Green).
- Refactor with behavior preserved and re-run affected suites (Refactor).

---

## Parallel Execution Examples

### User Story 1

```bash
Task T012 in tests/unit/test_runtime_config_validation.py
Task T013 in tests/integration/test_startup_config_validation_flow.py
Task T014 in tests/contract/test_readiness_contract.py
```

### User Story 2

```bash
Task T019 in tests/unit/test_runtime_profiles.py
Task T020 in tests/integration/test_profile_startup_matrix.py
Task T021 in tests/contract/test_readiness_contract.py
```

### User Story 3

```bash
Task T026 in tests/contract/test_readiness_contract.py
Task T027 in tests/integration/test_readiness_flow.py
Task T028 in tests/unit/test_readiness_state.py
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) and validate independently.
3. Demo/deploy MVP fail-fast startup behavior.

### Incremental Delivery

1. Deliver US1 (startup fail-fast).
2. Deliver US2 (deterministic profile behavior).
3. Deliver US3 (readiness and secret validity signaling).
4. Finish Phase 6 polish and regression evidence.

### Parallel Team Strategy

1. Team completes Setup + Foundational phases together.
2. After Phase 2, one developer can own each user story track.
3. Merge by story checkpoints with regression validation between merges.

---

## Notes

- Every task follows the required checklist format.
- `[P]` indicates safe parallelism (different files or independent preconditions).
- `[US#]` labels are used only for user-story tasks.
- Keep implementation minimal in Green tasks; defer cleanup to explicit Refactor tasks.
