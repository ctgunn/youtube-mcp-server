# Tasks: Hosted Dependency Wiring for Secrets and Durable Sessions

**Input**: Design documents from `/specs/022-hosted-dependency-wiring/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/quickstart.md), [runtime-secret-access-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/contracts/runtime-secret-access-contract.md), [runtime-session-connectivity-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/contracts/runtime-session-connectivity-contract.md), [hosted-dependency-verification-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/contracts/hosted-dependency-verification-contract.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when dependencies are satisfied and files do not overlap
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Every task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish shared task scaffolding, constants, and empty test modules used by the implementation phases.

- [X] T001 Extend hosted dependency shared terminology helpers in `src/mcp_server/infrastructure_contract.py`
- [X] T002 [P] Create contract test modules for FND-022 in `tests/contract/test_runtime_secret_access_contract.py`, `tests/contract/test_runtime_session_connectivity_contract.py`, and `tests/contract/test_hosted_dependency_verification_contract.py`
- [X] T003 [P] Add base hosted dependency unit test scaffolding in `tests/unit/test_cloud_run_config.py`, `tests/unit/test_readiness_state.py`, and `tests/unit/test_durable_session_store.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared deployment, readiness, and verification primitives that MUST exist before any user story can be completed.

**⚠️ CRITICAL**: No user story work should be considered complete until this phase is done.

- [X] T004 [P] Add failing unit tests for dependency classification and deployment input validation in `tests/unit/test_cloud_run_config.py`, `tests/unit/test_readiness_state.py`, and `tests/unit/test_durable_session_config.py`
- [X] T005 [P] Add failing integration tests for shared dependency evidence and readiness behavior in `tests/integration/test_cloud_run_deployment_metadata.py`, `tests/integration/test_readiness_flow.py`, and `tests/integration/test_cloud_run_verification_flow.py`
- [X] T006 Implement shared deployment input and dependency evidence models in `src/mcp_server/deploy.py`
- [X] T007 Implement shared readiness classification helpers for secret-access and session-connectivity failures in `src/mcp_server/config.py` and `src/mcp_server/health.py`
- [X] T008 Refactor shared serialization and remediation helpers for hosted dependency evidence in `src/mcp_server/deploy.py`, `src/mcp_server/observability.py`, and `scripts/verify_cloud_run_foundation.py`

**Checkpoint**: Shared deployment, readiness, and verification primitives are ready for story-specific work.

---

## Phase 3: User Story 1 - Run the Hosted Service with Working Secret and Session Dependencies (Priority: P1) 🎯 MVP

**Goal**: Make the hosted deployment path produce a runtime that can access required secrets, reach the durable session backend, and complete a durable hosted session continuation flow.

**Independent Test**: Provision a hosted environment with the documented dependency wiring, deploy it, run hosted verification, confirm `/ready` reports healthy dependency state, and confirm at least one hosted session continuation flow succeeds without manual fixes.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add contract coverage for runtime secret access guarantees in `tests/contract/test_runtime_secret_access_contract.py`
- [X] T010 [P] [US1] Add contract coverage for runtime session connectivity guarantees in `tests/contract/test_runtime_session_connectivity_contract.py`
- [X] T011 [P] [US1] Add integration coverage for the healthy hosted dependency path in `tests/integration/test_cloud_run_verification_flow.py` and `tests/integration/test_iac_foundation_workflows.py`

### Implementation for User Story 1

- [X] T012 [P] [US1] Add runtime secret-access inputs and outputs to the GCP provider adapter in `infrastructure/gcp/variables.tf` and `infrastructure/gcp/outputs.tf`
- [X] T013 [P] [US1] Wire runtime secret access and service-account permissions in `infrastructure/gcp/main.tf`
- [X] T014 [P] [US1] Wire durable session connectivity prerequisites and outputs in `infrastructure/gcp/session.tf` and `infrastructure/gcp/README.md`
- [X] T015 [US1] Implement runtime secret-access and session-connectivity deployment parsing in `src/mcp_server/deploy.py`
- [X] T016 [US1] Implement hosted verification checks for healthy secret access and session continuation in `scripts/verify_cloud_run_foundation.py`
- [X] T017 [US1] Implement runtime session dependency handling for the healthy hosted path in `src/mcp_server/app.py`, `src/mcp_server/cloud_run_entrypoint.py`, and `src/mcp_server/transport/session_store.py`
- [X] T018 [US1] Refactor hosted dependency wiring for the healthy path while keeping US1 tests green in `src/mcp_server/deploy.py`, `src/mcp_server/transport/session_store.py`, and `tests/integration/test_cloud_run_verification_flow.py`

**Checkpoint**: User Story 1 should independently prove that a hosted environment can start, become ready, and continue a hosted session with correct dependency wiring.

---

## Phase 4: User Story 2 - Detect Missing Secret or Session Wiring Quickly (Priority: P2)

**Goal**: Make readiness and hosted verification distinguish secret-access failures from session-connectivity failures with actionable diagnostics.

**Independent Test**: Intentionally remove required secret-access wiring once and session-backend connectivity once, then confirm `/ready` and hosted verification report the correct failure class and remediation path for each case.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add contract coverage for hosted dependency failure classification in `tests/contract/test_hosted_dependency_verification_contract.py`
- [X] T020 [P] [US2] Add unit coverage for secret-access versus session-connectivity readiness classification in `tests/unit/test_readiness_state.py` and `tests/unit/test_cloud_run_config.py`
- [X] T021 [P] [US2] Add integration coverage for secret-access failure and session-connectivity failure paths in `tests/integration/test_readiness_flow.py` and `tests/integration/test_cloud_run_verification_flow.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement runtime secret-access failure classification in `src/mcp_server/config.py` and `src/mcp_server/health.py`
- [X] T023 [US2] Implement session-connectivity failure classification and dependency status reporting in `src/mcp_server/transport/session_store.py` and `src/mcp_server/health.py`
- [X] T024 [US2] Implement hosted verification output for dependency failure layers and remediation in `src/mcp_server/deploy.py` and `scripts/verify_cloud_run_foundation.py`
- [X] T025 [US2] Update hosted request startup behavior to preserve dependency diagnostics in `src/mcp_server/app.py` and `src/mcp_server/cloud_run_entrypoint.py`
- [X] T026 [US2] Refactor dependency failure wording and keep US2 tests green in `src/mcp_server/health.py`, `src/mcp_server/deploy.py`, and `tests/integration/test_readiness_flow.py`

**Checkpoint**: User Story 2 should independently prove that operators can diagnose whether a deployment failed because of secret-access wiring or session-connectivity wiring.

---

## Phase 5: User Story 3 - Understand the Required Hosted Connectivity Model (Priority: P3)

**Goal**: Make the provider-specific runtime identity, secret-access path, session-connectivity path, and remediation workflow explicit in contracts and operator documentation.

**Independent Test**: Use the runbook and contracts alone to explain the runtime identity, secret-access prerequisites, session-connectivity prerequisites, healthy verification path, and the remediation path for both dependency failure classes.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add contract coverage for operator-visible runtime identity and dependency model documentation in `tests/contract/test_runtime_secret_access_contract.py`, `tests/contract/test_runtime_session_connectivity_contract.py`, and `tests/contract/test_hosted_dependency_verification_contract.py`
- [X] T028 [P] [US3] Add documentation example coverage for the hosted dependency runbook in `tests/integration/test_cloud_run_docs_examples.py`

### Implementation for User Story 3

- [X] T029 [P] [US3] Update the GCP provider runbook for runtime identity, secret access, and session connectivity in `infrastructure/gcp/README.md` and `infrastructure/gcp/terraform.tfvars.example`
- [X] T030 [P] [US3] Update the main operator documentation for hosted dependency wiring in `README.md`
- [X] T031 [US3] Update deployment workflow guidance for dependency evidence handoff in `scripts/deploy_cloud_run.sh` and `src/mcp_server/deploy.py`
- [X] T032 [US3] Align the feature quickstart with the final hosted dependency workflow in `specs/022-hosted-dependency-wiring/quickstart.md`
- [X] T033 [US3] Refactor operator-facing dependency guidance and keep US3 tests green in `README.md`, `infrastructure/gcp/README.md`, and `specs/022-hosted-dependency-wiring/quickstart.md`

**Checkpoint**: User Story 3 should independently prove that operators and reviewers can understand and reproduce the provider-specific dependency model from documentation and contracts alone.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize regression coverage, documentation validation, observability safety, and full-suite completion proof.

- [X] T034 [P] Add regression coverage for deploy execution and dependency evidence defaults in `tests/unit/test_cloud_run_deploy_execution.py` and `tests/integration/test_cloud_run_deployment_assets.py`
- [X] T035 [P] Validate quickstart and operator-doc flows in `README.md`, `infrastructure/gcp/README.md`, and `specs/022-hosted-dependency-wiring/quickstart.md`
- [X] T036 Harden secret-safe logging and evidence output in `src/mcp_server/observability.py` and `tests/integration/test_security_request_observability.py`
- [X] T037 Run the full repository test suite with `pytest` and resolve any failures in `tests/`, `src/mcp_server/`, `scripts/`, and `infrastructure/gcp/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies; start immediately.
- **Phase 2: Foundational**: Depends on Phase 1; blocks all user stories until shared deployment, readiness, and verification primitives exist.
- **Phase 3: User Story 1**: Depends on Phase 2; forms the MVP.
- **Phase 4: User Story 2**: Depends on Phase 2 and may reuse US1 healthy-path behavior, but remains independently testable through failure diagnostics.
- **Phase 5: User Story 3**: Depends on Phase 2 and may reuse US1/US2 evidence models, but remains independently testable through documentation and contracts.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational; no dependency on US2 or US3.
- **US2 (P2)**: Can start after Foundational; benefits from US1 healthy-path wiring but remains independently testable using failure scenarios.
- **US3 (P3)**: Can start after Foundational; remains independently testable using docs and contract validation once the dependency model is settled.

### Within Each User Story

- Write failing contract, unit, and integration tests first.
- Implement the minimum code and documentation changes needed to satisfy those tests.
- Refactor only after the story tests pass.
- Before marking the feature complete, run the full repository test suite with `pytest` and fix all failures.

### Suggested Completion Order

1. Phase 1
2. Phase 2
3. Phase 3 (MVP)
4. Validate and demo US1 independently
5. Phase 4
6. Validate and demo US2 independently
7. Phase 5
8. Validate and demo US3 independently
9. Phase 6

---

## Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`.
- `T004` and `T005` can run in parallel once Phase 1 is complete.
- `T009`, `T010`, and `T011` can run in parallel for US1.
- `T012`, `T013`, and `T014` can run in parallel for US1.
- `T019`, `T020`, and `T021` can run in parallel for US2.
- `T027` and `T028` can run in parallel for US3.
- `T029` and `T030` can run in parallel for US3.
- `T034`, `T035`, and `T036` can run in parallel before the final `pytest` run in `T037`.

## Parallel Example: User Story 1

```bash
# Run the US1 failing tests together:
Task: "Add contract coverage for runtime secret access guarantees in tests/contract/test_runtime_secret_access_contract.py"
Task: "Add contract coverage for runtime session connectivity guarantees in tests/contract/test_runtime_session_connectivity_contract.py"
Task: "Add integration coverage for the healthy hosted dependency path in tests/integration/test_cloud_run_verification_flow.py and tests/integration/test_iac_foundation_workflows.py"

# Implement the US1 provider wiring together:
Task: "Add runtime secret-access inputs and outputs to the GCP provider adapter in infrastructure/gcp/variables.tf and infrastructure/gcp/outputs.tf"
Task: "Wire runtime secret access and service-account permissions in infrastructure/gcp/main.tf"
Task: "Wire durable session connectivity prerequisites and outputs in infrastructure/gcp/session.tf and infrastructure/gcp/README.md"
```

## Parallel Example: User Story 2

```bash
# Run the US2 red tests together:
Task: "Add contract coverage for hosted dependency failure classification in tests/contract/test_hosted_dependency_verification_contract.py"
Task: "Add unit coverage for secret-access versus session-connectivity readiness classification in tests/unit/test_readiness_state.py and tests/unit/test_cloud_run_config.py"
Task: "Add integration coverage for secret-access failure and session-connectivity failure paths in tests/integration/test_readiness_flow.py and tests/integration/test_cloud_run_verification_flow.py"
```

## Parallel Example: User Story 3

```bash
# Run the US3 red tests together:
Task: "Add contract coverage for operator-visible runtime identity and dependency model documentation in tests/contract/test_runtime_secret_access_contract.py, tests/contract/test_runtime_session_connectivity_contract.py, and tests/contract/test_hosted_dependency_verification_contract.py"
Task: "Add documentation example coverage for the hosted dependency runbook in tests/integration/test_cloud_run_docs_examples.py"

# Implement the US3 documentation updates together:
Task: "Update the GCP provider runbook for runtime identity, secret access, and session connectivity in infrastructure/gcp/README.md and infrastructure/gcp/terraform.tfvars.example"
Task: "Update the main operator documentation for hosted dependency wiring in README.md"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the healthy hosted dependency path independently
5. Demo or ship the MVP if ready

### Incremental Delivery

1. Finish Setup and Foundational work once.
2. Deliver US1 as the MVP for healthy hosted dependency wiring.
3. Deliver US2 to make dependency failures diagnosable and actionable.
4. Deliver US3 to complete the operator-facing dependency model and runbook.
5. Finish with cross-cutting regressions, docs validation, and the full `pytest` run.

### Parallel Team Strategy

1. One engineer completes Phase 1 and coordinates Phase 2 shared primitives.
2. After Foundational work is done:
   - Engineer A focuses on US1 provider wiring and healthy-path verification.
   - Engineer B focuses on US2 readiness and failure classification.
   - Engineer C focuses on US3 contracts and operator documentation.
3. Merge into Phase 6 for final regression coverage and full-suite validation.

---

## Notes

- `[P]` tasks modify different files and are safe parallel candidates once dependencies are satisfied.
- `[US1]`, `[US2]`, and `[US3]` map directly to the stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/spec.md).
- Every story includes explicit Red, Green, and Refactor work.
- Targeted test runs are not completion proof; `pytest` in `T037` is the completion gate.
- The recommended MVP scope is **User Story 1 only** after Setup and Foundational work.
