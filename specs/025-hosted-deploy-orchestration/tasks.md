# Tasks: Automated Hosted Deployment Orchestration

**Input**: Design documents from `/specs/025-hosted-deploy-orchestration/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/quickstart.md), [hosted-deployment-pipeline-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/contracts/hosted-deployment-pipeline-contract.md), [deployment-bootstrap-boundary-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/contracts/deployment-bootstrap-boundary-contract.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the shared workflow and test file surfaces used by the feature.

- [X] T001 Create the hosted deployment workflow scaffold in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml
- [X] T002 [P] Create the workflow test scaffolds in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_pipeline_helpers.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_pipeline_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py
- [X] T003 [P] Reserve the hosted deployment automation documentation section in /Users/ctgunn/Projects/youtube-mcp-server/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared deployment-record, workflow-stage, and verification helpers that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add failing unit coverage for workflow-run, stage-result, and artifact helper behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_pipeline_helpers.py
- [X] T005 Add failing contract coverage for required workflow stages, artifacts, and failure gates in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_pipeline_contract.py
- [X] T006 Implement shared workflow-run, stage-result, and artifact helper functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T007 Update /Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh to emit workflow-friendly deployment artifacts and preserve stage-specific failures
- [X] T008 Update /Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py to consume workflow artifacts and emit workflow-friendly verification output

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Deploy the Hosted Platform from a Branch Push (Priority: P1) 🎯 MVP

**Goal**: Make one qualifying push trigger the full repository-managed hosted rollout and fail the run if hosted verification fails.

**Independent Test**: Push a qualifying revision and confirm one workflow run performs tests, image publication, infrastructure reconciliation, deploy-script rollout, and hosted verification, with the run marked failed whenever hosted verification fails.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add failing contract coverage for push-triggered ordered deployment stages in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_pipeline_contract.py
- [X] T010 [P] [US1] Add failing integration coverage for the full push-to-verification workflow in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py
- [X] T011 [P] [US1] Add failing unit coverage for workflow stage orchestration and verification gating in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_pipeline_helpers.py

### Implementation for User Story 1

- [X] T012 [US1] Implement the push trigger and top-level workflow stages in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml
- [X] T013 [US1] Implement image publication, Terraform apply, and deploy-script handoff in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml
- [X] T014 [US1] Implement hosted verification gating and workflow artifact upload in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml
- [X] T015 [US1] Refactor workflow stage names, shared expressions, and artifact wiring in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py while keeping User Story 1 tests green

**Checkpoint**: User Story 1 should now be fully functional and independently testable.

---

## Phase 4: User Story 2 - Review and Trust Deployment Logic in Version Control (Priority: P2)

**Goal**: Keep infrastructure reconciliation, deploy-script rollout, and hosted verification reviewable in one checked-in path that does not bypass repository logic with an image-only update.

**Independent Test**: Inspect one workflow run and confirm it exports Terraform outputs, passes those outputs into the repository deploy script, and never uses a direct image-only platform update path.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add failing contract coverage for Terraform-output handoff and non-bypass deployment rules in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_handoff_contract.py
- [X] T017 [P] [US2] Add failing integration coverage for infrastructure-output-to-deploy-script flow in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_handoff.py
- [X] T018 [P] [US2] Add failing unit coverage for Terraform-output validation and deployment-input normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_pipeline_helpers.py

### Implementation for User Story 2

- [X] T019 [US2] Implement Terraform-output validation and deployment-input normalization in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T020 [US2] Update /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml to export Terraform outputs and invoke /Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh instead of any direct image-only deploy path
- [X] T021 [US2] Document the reviewed infrastructure-to-deploy-to-verify chain in /Users/ctgunn/Projects/youtube-mcp-server/README.md
- [X] T022 [US2] Refactor deployment handoff messaging, artifact names, and workflow comments in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py, /Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh, and /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml while keeping User Story 2 tests green

**Checkpoint**: User Stories 1 and 2 should both work, and the deployment path should remain fully reviewable from repository files and workflow artifacts.

---

## Phase 5: User Story 3 - Distinguish Automation from Secret Value Management (Priority: P3)

**Goal**: Make bootstrap prerequisites and the boundary between automation-managed secret wiring and operator-managed secret values explicit and enforceable.

**Independent Test**: Review the workflow and operator docs, then simulate missing bootstrap prerequisites or missing secret values and confirm the run fails with clear stage-specific guidance without exposing secret contents.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add failing contract coverage for bootstrap prerequisites and secret-boundary guarantees in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_bootstrap_contract.py
- [X] T024 [P] [US3] Add failing integration coverage for bootstrap failure scenarios and secret-boundary reporting in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_bootstrap_docs.py
- [X] T025 [P] [US3] Add failing unit coverage for bootstrap prerequisite classification and secret-boundary error mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_deployment_bootstrap_helpers.py

### Implementation for User Story 3

- [X] T026 [US3] Implement bootstrap prerequisite checks and secret-boundary failure handling in /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml
- [X] T027 [US3] Document bootstrap prerequisites and operator-managed secret responsibilities in /Users/ctgunn/Projects/youtube-mcp-server/README.md
- [X] T028 [US3] Document hosted bootstrap, secret wiring, and operator-managed secret-value boundaries in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md
- [X] T029 [US3] Refactor bootstrap guidance and failure wording across /Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml, /Users/ctgunn/Projects/youtube-mcp-server/README.md, and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md while keeping User Story 3 tests green

**Checkpoint**: All user stories should now be independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs, regression coverage, and full-suite validation across the whole feature.

- [X] T030 [P] Align operator examples and validation steps in /Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/quickstart.md with the implemented workflow
- [X] T031 [P] Add regression coverage for workflow artifacts and deployment observability in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deployment_observability_contract.py
- [X] T032 Validate the documented bootstrap and hosted deployment flow in /Users/ctgunn/Projects/youtube-mcp-server/README.md and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md against the implemented workflow
- [X] T033 Run `pytest` and `ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server and resolve any remaining failures before marking the feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; delivers the MVP deployment workflow.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because it hardens the same workflow handoff and artifact path.
- **User Story 3 (Phase 5)**: Depends on User Story 1 because it extends the same workflow with bootstrap and secret-boundary behavior.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies beyond Foundational phase.
- **User Story 2 (P2)**: Builds on the User Story 1 workflow file and deploy artifact path.
- **User Story 3 (P3)**: Builds on the User Story 1 workflow file and operator documentation path.

### Within Each User Story

- Tests MUST be written and fail before implementation begins.
- Workflow and helper changes come before documentation refactor tasks.
- Refactor only after story-specific tests pass.
- Before marking the feature complete, run the full repository suite with `pytest` and `ruff check .`.

## Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel after the workflow file exists.
- Foundational tests can run before foundational helper implementation begins.
- For User Story 1, the contract, integration, and unit Red tests can run in parallel.
- For User Story 2, the contract, integration, and unit Red tests can run in parallel.
- For User Story 3, the contract, integration, and unit Red tests can run in parallel.
- Polish tasks `T030` and `T031` can run in parallel once all user stories are complete.

## Parallel Example: User Story 1

```bash
Task: "T009 [US1] Add failing contract coverage in tests/contract/test_hosted_deployment_pipeline_contract.py"
Task: "T010 [US1] Add failing integration coverage in tests/integration/test_hosted_deployment_workflow.py"
Task: "T011 [US1] Add failing unit coverage in tests/unit/test_hosted_deployment_pipeline_helpers.py"
```

## Parallel Example: User Story 2

```bash
Task: "T016 [US2] Add failing contract coverage in tests/contract/test_hosted_deployment_handoff_contract.py"
Task: "T017 [US2] Add failing integration coverage in tests/integration/test_hosted_deployment_handoff.py"
Task: "T018 [US2] Add failing unit coverage in tests/unit/test_hosted_deployment_pipeline_helpers.py"
```

## Parallel Example: User Story 3

```bash
Task: "T023 [US3] Add failing contract coverage in tests/contract/test_hosted_deployment_bootstrap_contract.py"
Task: "T024 [US3] Add failing integration coverage in tests/integration/test_hosted_deployment_bootstrap_docs.py"
Task: "T025 [US3] Add failing unit coverage in tests/unit/test_hosted_deployment_bootstrap_helpers.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the hosted push-triggered workflow independently before expanding the handoff and bootstrap scope.

### Incremental Delivery

1. Deliver the push-triggered workflow with hosted verification gating in User Story 1.
2. Harden the repository-managed infrastructure-to-deploy handoff in User Story 2.
3. Add explicit bootstrap and secret-boundary behavior in User Story 3.
4. Finish with cross-cutting docs, regression coverage, and full-suite validation.

### Parallel Team Strategy

1. One developer completes Setup and Foundational work.
2. After User Story 1 is stable, one developer can own User Story 2 while another owns User Story 3 because their Red tests and most documentation work touch different files.
3. Rejoin for Polish and full-suite validation.

## Notes

- All tasks follow the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` on story tasks, clear action, and exact file path.
- The suggested MVP scope is User Story 1 only.
- Do not treat targeted test runs as completion evidence; the final gate is `pytest` plus `ruff check .`.
