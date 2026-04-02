# Tasks: Automated Hosted Network Bootstrap Reconciliation

**Input**: Design documents from `/specs/028-hosted-network-bootstrap/`
**Prerequisites**: [plan.md](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/plan.md), [spec.md](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/spec.md), [data-model.md](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/data-model.md), contracts in [~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts), [quickstart.md](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature-specific test surfaces used across the implementation

- [X] T001 Create contract and integration test scaffolds in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py` and `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py`
- [X] T002 [P] Create documentation and unit test scaffolds in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_docs.py` and `~/Projects/youtube-mcp-server/tests/unit/test_hosted_network_bootstrap_failure_helpers.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared helper and regression surfaces that every user story depends on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add reusable bootstrap failure-classification helpers and workflow-summary extension points in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T004 [P] Extend shared workflow ordering coverage in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py`
- [X] T005 [P] Extend shared bootstrap helper coverage in `~/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_bootstrap_helpers.py`
- [X] T006 Update shared contract aggregation assertions for FND-028 in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py`

**Checkpoint**: Foundation ready. User story work can now proceed in priority order or in parallel if staffed.

---

## Phase 3: User Story 1 - Reconcile Network Prerequisites Before Hosted Rollout (Priority: P1) 🎯 MVP

**Goal**: Make the primary automatic pipeline and manual fallback explicitly guarantee managed network reconciliation before application rollout for environments that require the hosted network path.

**Independent Test**: Trigger the hosted deployment path and confirm the reviewed automation surfaces and workflow artifacts show `infrastructure_reconcile` completing before deploy, with deploy blocked when network reconciliation fails.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T007 [P] [US1] Add failing contract assertions for ordered network-bootstrap semantics in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py`
- [X] T008 [P] [US1] Add failing integration coverage for reconcile-before-deploy ordering in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py`

### Implementation for User Story 1

- [X] T009 [US1] Update the pipeline behavior contract in `~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-pipeline-contract.md`
- [X] T010 [P] [US1] Update primary automatic pipeline semantics in `~/Projects/youtube-mcp-server/cloudbuild.yaml`
- [X] T011 [P] [US1] Update fallback workflow semantics in `~/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml`
- [X] T012 [US1] Refactor shared stage-order serialization and regression assertions in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py` and `~/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py`

**Checkpoint**: User Story 1 is independently testable when the pipeline contract and automation surfaces make network reconciliation an explicit pre-deploy gate.

---

## Phase 4: User Story 2 - Distinguish Bootstrap Failure from Application Failure (Priority: P2)

**Goal**: Make workflow outputs and deployment evidence distinguish bootstrap-input failure, managed network reconcile failure, deployment failure, and hosted verification failure.

**Independent Test**: Simulate failed runs across bootstrap, reconcile, deploy, and verification paths and confirm the recorded outputs classify the failing layer without ambiguity.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T013 [P] [US2] Add failing unit coverage for bootstrap-vs-network-vs-deploy-vs-verification classification in `~/Projects/youtube-mcp-server/tests/unit/test_hosted_network_bootstrap_failure_helpers.py`
- [X] T014 [P] [US2] Add failing integration coverage for operator-visible failure boundaries in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py`
- [X] T015 [P] [US2] Add failing contract assertions for failure taxonomy expectations in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py`

### Implementation for User Story 2

- [X] T016 [US2] Implement bootstrap failure classification and workflow summary fields in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T017 [US2] Update the failure-boundary contract in `~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-failure-boundary-contract.md`
- [X] T018 [US2] Refactor remediation wording and regression assertions in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py` and `~/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py`

**Checkpoint**: User Story 2 is independently testable when failed runs can be classified by boundary from workflow artifacts and deployment evidence alone.

---

## Phase 5: User Story 3 - Publish One Clear Bootstrap Boundary for Hosted Automation (Priority: P3)

**Goal**: Document the remaining one-time bootstrap inputs clearly while keeping recurring managed hosted networking inside the automated deployment path.

**Independent Test**: Review the repository and GCP runbooks and confirm they describe the same boundary: one-time external setup remains limited to automation access, environment inputs, and operator-managed secret values, while recurring network provisioning stays inside the automated pipeline.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T019 [P] [US3] Add failing contract assertions for the remaining prerequisite boundary in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py`
- [X] T020 [P] [US3] Add failing documentation integration coverage in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_docs.py`

### Implementation for User Story 3

- [X] T021 [P] [US3] Update the prerequisite-boundary contract in `~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-prerequisite-contract.md`
- [X] T022 [P] [US3] Update hosted bootstrap guidance in `~/Projects/youtube-mcp-server/infrastructure/gcp/README.md`
- [X] T023 [US3] Update repository-level hosted deployment guidance in `~/Projects/youtube-mcp-server/README.md`
- [X] T024 [US3] Refactor prerequisite language across `~/Projects/youtube-mcp-server/README.md` and `~/Projects/youtube-mcp-server/infrastructure/gcp/README.md` to keep local and hosted paths separate

**Checkpoint**: User Story 3 is independently testable when the runbooks make the bootstrap boundary explicit and eliminate any implication of recurring manual network provisioning.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story validation, cleanup, and final repository verification

- [X] T025 [P] Validate the operator flow in `~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/quickstart.md` against the final workflow and documentation behavior
- [X] T026 [P] Add cross-story regression coverage in `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py` and `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py`
- [X] T027 Run targeted feature validation in `~/Projects/youtube-mcp-server/tests/unit/test_hosted_network_bootstrap_failure_helpers.py`, `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py`, `~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_docs.py`, and `~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py`
- [X] T028 Run the full repository validation with `pytest` and `ruff check .` from `~/Projects/youtube-mcp-server` and fix any failures in affected files before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1. Blocks all user-story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2. This is the MVP slice.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and should build on the stage semantics introduced in User Story 1.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and should align with the finalized boundary language from User Stories 1 and 2.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after foundational work.
- **User Story 2 (P2)**: Depends on the shared stage-order and serialization surface established in User Story 1.
- **User Story 3 (P3)**: Depends on the final bootstrap and failure-boundary semantics from User Stories 1 and 2 so documentation matches shipped behavior.

### Within Each User Story

- Write the listed tests first and confirm they fail before implementation.
- Implement the minimum contract, workflow, helper, and documentation changes needed to make those tests pass.
- Refactor only after the story-specific tests are green.
- Do not mark the story complete until its independent test criteria are satisfied.
- Before final completion, run the full repository suite and fix any failures.

### Suggested Execution Order

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 User Story 1
4. Validate MVP behavior
5. Phase 4 User Story 2
6. Phase 5 User Story 3
7. Phase 6 Polish

---

## Parallel Opportunities

- T001 and T002 can run in parallel because they create separate test files.
- T004 and T005 can run in parallel because they touch different shared regression files.
- Within User Story 1, T007 and T008 can run in parallel, and T010 and T011 can run in parallel.
- Within User Story 2, T013, T014, and T015 can run in parallel.
- Within User Story 3, T019 and T020 can run in parallel, and T021 and T022 can run in parallel.
- In Phase 6, T025 and T026 can run in parallel before targeted and full-suite validation.

## Parallel Example: User Story 1

```bash
Task: "Add failing contract assertions for ordered network-bootstrap semantics in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py"
Task: "Add failing integration coverage for reconcile-before-deploy ordering in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py"

Task: "Update primary automatic pipeline semantics in ~/Projects/youtube-mcp-server/cloudbuild.yaml"
Task: "Update fallback workflow semantics in ~/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml"
```

## Parallel Example: User Story 2

```bash
Task: "Add failing unit coverage for bootstrap-vs-network-vs-deploy-vs-verification classification in ~/Projects/youtube-mcp-server/tests/unit/test_hosted_network_bootstrap_failure_helpers.py"
Task: "Add failing integration coverage for operator-visible failure boundaries in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_flow.py"
Task: "Add failing contract assertions for failure taxonomy expectations in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add failing contract assertions for the remaining prerequisite boundary in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_network_bootstrap_contract.py"
Task: "Add failing documentation integration coverage in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_network_bootstrap_docs.py"

Task: "Update the prerequisite-boundary contract in ~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/contracts/hosted-network-bootstrap-prerequisite-contract.md"
Task: "Update hosted bootstrap guidance in ~/Projects/youtube-mcp-server/infrastructure/gcp/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the hosted deployment path independently with the User Story 1 test criteria.
5. Stop and review before expanding failure taxonomy or documentation scope.

### Incremental Delivery

1. Finish Setup and Foundational work to establish shared test and helper surfaces.
2. Deliver User Story 1 to make network reconciliation an explicit pre-deploy gate.
3. Deliver User Story 2 to make failure boundaries operator-readable.
4. Deliver User Story 3 to align runbooks with the shipped automation boundary.
5. Finish with targeted regression checks and a full repository test-suite run.

### Parallel Team Strategy

1. One engineer handles Phase 1 and Phase 2.
2. After Phase 2, one engineer can own User Story 1 while another prepares the failing tests for User Story 2.
3. Once User Story 2 semantics are settled, documentation work for User Story 3 can proceed in parallel with final regression cleanup.

---

## Notes

- Every task follows the required checklist format: checkbox, task ID, optional `[P]`, required story label for user-story phases, and exact file path.
- User stories remain independently testable and are ordered P1 → P2 → P3.
- Red tasks come before Green tasks in every user-story phase.
- The final completion gate is a passing full repository run with `pytest` and `ruff check .`.
