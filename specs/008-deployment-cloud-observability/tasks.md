# Tasks: FND-008 Deployment Execution + Cloud Run Observability

**Input**: Design documents from `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/`
**Prerequisites**: `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/plan.md`, `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/spec.md`, `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/research.md`, `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/data-model.md`, `~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/contracts/deployment-observability-contract.md`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the dedicated test surfaces and task scaffolding for FND-008 work.

- [X] T001 Create deployment execution unit test module in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_deploy_execution.py
- [X] T002 [P] Create deployment metadata integration test module in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py
- [X] T003 [P] Create deployment observability contract test module in ~/Projects/youtube-mcp-server/tests/contract/test_deployment_observability_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared deployment-result and hosted log plumbing that every story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement shared `DeploymentRunRecord` and `RuntimeSettingsSnapshot` helpers in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T005 [P] Implement shared hosted runtime log emission helper alongside in-memory recording in ~/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T006 [P] Add shared shell-to-Python deployment result handoff utilities in ~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh and ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Execute a Hosted Deployment in One Workflow (Priority: P1) 🎯 MVP

**Goal**: Replace render-only deployment behavior with one executable operator workflow that performs the hosted deploy and reports success or failure clearly.

**Independent Test**: Run the deployment workflow with valid and invalid inputs and confirm it executes the deploy path for valid input, stops before reporting success on invalid input, and no manual command reconstruction is required.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Add red unit tests for deploy execution success and failure handling in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_deploy_execution.py
- [X] T008 [P] [US1] Add red integration tests for executable deploy workflow behavior in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py

### Implementation for User Story 1

- [X] T009 [US1] Implement deploy command execution helpers in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T010 [US1] Update the operator deployment workflow to execute the hosted deploy command in ~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh
- [X] T011 [US1] Refactor deployment execution flow and re-run US1 suites in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_deploy_execution.py and ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py

**Checkpoint**: User Story 1 is independently functional when one command executes a hosted deploy and reports failure without manual fallback steps.

---

## Phase 4: User Story 2 - Capture Revision Metadata for Verification and Audit (Priority: P1)

**Goal**: Produce one operator-visible deployment record containing revision identity, hosted URL, runtime settings, and incomplete-metadata handling.

**Independent Test**: Complete one deployment run and verify that the resulting deployment record includes revision name, service URL, runtime identity, environment profile, scaling bounds, concurrency, and timeout, while partial metadata capture is reported as `incomplete`.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T012 [P] [US2] Add red contract tests for deployment outcome record requirements in ~/Projects/youtube-mcp-server/tests/contract/test_deployment_observability_contract.py
- [X] T013 [P] [US2] Add red integration tests for revision metadata capture and incomplete outcomes in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py

### Implementation for User Story 2

- [X] T014 [US2] Implement deployment outcome record serialization and metadata extraction in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T015 [US2] Update deployment workflow output to emit revision and runtime metadata records in ~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh
- [X] T016 [US2] Document deployment record consumption for verification in ~/Projects/youtube-mcp-server/README.md and ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T017 [US2] Refactor deployment metadata shaping and re-run US2 suites in ~/Projects/youtube-mcp-server/tests/contract/test_deployment_observability_contract.py and ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py

**Checkpoint**: User Story 2 is independently functional when operators can inspect one retained deployment record and verify what revision and runtime settings were deployed.

---

## Phase 5: User Story 3 - Inspect Hosted Runtime Logs for Request Diagnostics (Priority: P2)

**Goal**: Emit structured hosted runtime logs that operators can use to trace probe, MCP, and failure traffic by request ID, path, status, latency, and tool name where applicable.

**Independent Test**: Send `/healthz`, `/readyz`, successful `/mcp`, failed `/mcp`, and unsupported-path requests to the hosted runtime path and confirm each request emits one structured log event with the required fields, with `toolName` only present for tool calls.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T018 [P] [US3] Add red contract tests for hosted structured log event requirements in ~/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py
- [X] T019 [P] [US3] Add red integration tests for probe, MCP, and failure log emission in ~/Projects/youtube-mcp-server/tests/integration/test_request_observability.py and ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py

### Implementation for User Story 3

- [X] T020 [US3] Implement structured stdout/stderr hosted log emission in ~/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T021 [US3] Wire hosted request log emission through runtime request handling in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py and ~/Projects/youtube-mcp-server/src/mcp_server/app.py
- [X] T022 [US3] Refactor hosted log emission to preserve in-memory parity and re-run US3 suites in ~/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py and ~/Projects/youtube-mcp-server/tests/integration/test_request_observability.py

**Checkpoint**: User Story 3 is independently functional when hosted runtime traffic emits structured request logs visible to operators without breaking existing response behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize cross-story documentation, validation, and regression coverage.

- [X] T023 [P] Update operator examples for deployment records and hosted log inspection in ~/Projects/youtube-mcp-server/README.md and ~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/quickstart.md
- [X] T024 Run full regression coverage across ~/Projects/youtube-mcp-server/tests/unit/, ~/Projects/youtube-mcp-server/tests/integration/, and ~/Projects/youtube-mcp-server/tests/contract/
- [X] T025 [P] Validate deployed verification handoff examples against ~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh and ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2; recommended MVP slice.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and builds directly on the executable deployment flow from User Story 1.
- **User Story 3 (Phase 5)**: Depends on Phase 2; can proceed after foundational work, though it is lower priority than the deployment slices.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1**: No dependency on other user stories after foundational work is done.
- **US2**: Depends on US1 because deployment metadata is produced by the executable deployment workflow.
- **US3**: No hard dependency on US1 or US2 after foundational work, but hosted validation value increases once deployment execution is complete.

### Within Each User Story

- Red tests MUST be written and fail before implementation starts.
- Shared helpers and models come before workflow or runtime wiring.
- Implementation stays minimal until story tests pass.
- Refactor happens only after story tests are green, followed by rerunning affected suites.

### Suggested Execution Order

1. Complete Phase 1.
2. Complete Phase 2.
3. Complete Phase 3 (US1) as the MVP.
4. Complete Phase 4 (US2).
5. Complete Phase 5 (US3).
6. Finish Phase 6.

---

## Parallel Opportunities

- T002 and T003 can run in parallel after T001.
- T005 and T006 can run in parallel after T004.
- T007 and T008 can run in parallel inside US1.
- T012 and T013 can run in parallel inside US2.
- T018 and T019 can run in parallel inside US3.
- T023 and T025 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "Add red unit tests for deploy execution success and failure handling in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_deploy_execution.py"
Task: "Add red integration tests for executable deploy workflow behavior in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add red contract tests for deployment outcome record requirements in ~/Projects/youtube-mcp-server/tests/contract/test_deployment_observability_contract.py"
Task: "Add red integration tests for revision metadata capture and incomplete outcomes in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add red contract tests for hosted structured log event requirements in ~/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py"
Task: "Add red integration tests for probe, MCP, and failure log emission in ~/Projects/youtube-mcp-server/tests/integration/test_request_observability.py and ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Finish Setup and Foundational phases.
2. Deliver User Story 1 so operators can execute one hosted deployment workflow end to end.
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Add US1 to replace render-only deployment behavior.
2. Add US2 to make the deployment output audit- and verification-ready.
3. Add US3 to expose hosted runtime logs for operator diagnostics.
4. Finish with cross-story regression and docs updates.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational phases.
2. After Phase 2:
   - Engineer A can take US1.
   - Engineer B can prepare US3 in parallel.
3. US2 follows once the executable deployment workflow from US1 is available.

---

## Notes

- Every task follows the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` in story phases, and exact file path.
- Tests are intentionally front-loaded in each story to enforce Red-Green-Refactor.
- User Story 1 is the suggested MVP scope.
