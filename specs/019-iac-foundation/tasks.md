# Tasks: Infrastructure as Code Foundation

**Input**: Design documents from `/specs/019-iac-foundation/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run with `pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when tasks touch different files and have no unresolved dependencies
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the file scaffolding for the new infrastructure and test surfaces.

- [X] T001 Create the infrastructure scaffolding files in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/versions.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/main.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/session.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/outputs.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/terraform.tfvars.example`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/compose.yaml`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/.env.example`, and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`
- [X] T002 [P] Create the feature test scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the shared Red-Green-Refactor foundation for provisioning, deployment handoff, and local hosted-like verification.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T003 Add failing shared contract assertions for the new provisioning and local dependency contracts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [X] T004 [P] Add failing shared integration assertions for provisioning, deployment handoff, and local hosted-like workflow coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`
- [X] T005 [P] Add failing shared unit assertions for infrastructure input parsing and output normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py`
- [X] T006 Implement shared infrastructure handoff helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T007 Align shared environment and deployment variable guidance in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/.env.example`
- [X] T008 Refactor shared naming and failure guidance across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/.env.example` while keeping the foundational tests green

**Checkpoint**: Foundational test surfaces, shared helpers, and common variable conventions are in place.

---

## Phase 3: User Story 1 - Provision the Hosted Platform from Versioned Definitions (Priority: P1) 🎯 MVP

**Goal**: Deliver a versioned GCP infrastructure foundation that provisions the hosted runtime, runtime identity, secret integration points, and durable session backend.

**Independent Test**: Starting from an empty target environment, run the documented GCP provisioning workflow and verify the expected hosted resources and outputs are produced without undocumented console steps.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T009 [P] [US1] Add contract coverage for required GCP resources and provisioning outputs in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [X] T010 [P] [US1] Add integration coverage for the operator provisioning workflow in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`

### Implementation for User Story 1

- [X] T011 [P] [US1] Define the Terraform provider and root variable contract in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/versions.tf` and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf`
- [X] T012 [P] [US1] Define the Cloud Run service foundation, runtime identity, and secret integration resources in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/main.tf`
- [X] T013 [P] [US1] Define the Redis-compatible durable session backend and exported outputs in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/session.tf` and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/outputs.tf`
- [X] T014 [US1] Document the provisioning workflow, required tfvars, and expected outputs in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/terraform.tfvars.example`
- [X] T015 [US1] Refactor variable naming, output descriptions, and provisioning guidance across `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/outputs.tf`, and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md` while keeping US1 tests green

**Checkpoint**: User Story 1 is independently demonstrable as a reproducible infrastructure provisioning path.

---

## Phase 4: User Story 2 - Deploy the Application Through a Reproducible Hosted Path (Priority: P2)

**Goal**: Make the existing deployment flow consume the documented infrastructure outputs so application rollout is reproducible without source edits.

**Independent Test**: Use the provisioned infrastructure outputs plus an `IMAGE_REFERENCE` to run the deployment workflow and confirm the service can be deployed with documented injectable inputs only.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add contract coverage for the deployment handoff values consumed after infrastructure provisioning in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [X] T017 [P] [US2] Add integration coverage for the infrastructure-output-to-deployment-script workflow in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`

### Implementation for User Story 2

- [X] T018 [P] [US2] Implement deployment-input serialization and validation for IaC-produced outputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py`
- [X] T019 [US2] Update the deployment workflow to consume the documented infrastructure outputs in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`
- [X] T020 [US2] Align deployment documentation and examples with the infrastructure handoff contract in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/quickstart.md`
- [X] T021 [US2] Refactor deployment input naming, validation errors, and handoff guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`, and `/Users/ctgunn/Projects/youtube-mcp-server/README.md` while keeping US2 tests green

**Checkpoint**: User Story 2 is independently demonstrable as a reproducible deployment path that consumes infrastructure outputs.

---

## Phase 5: User Story 3 - Preserve a First-Class Local Path While Documenting Hosted-Like Verification (Priority: P3)

**Goal**: Keep the minimal local workflow unchanged while adding a separate repository-defined local dependency path for durable-session verification.

**Independent Test**: Verify the minimal local path runs without infrastructure provisioning, then start the hosted-like local dependency stack and confirm the durable-session verification path uses the documented Redis-backed configuration.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T022 [P] [US3] Add contract coverage for minimal-local versus hosted-like-local workflow guarantees in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [X] T023 [P] [US3] Add integration coverage for the minimal-local and hosted-like-local workflows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`

### Implementation for User Story 3

- [X] T024 [P] [US3] Define the local Redis dependency stack in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/compose.yaml`
- [X] T025 [P] [US3] Document hosted-like local environment variables and startup steps in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/.env.example` and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`
- [X] T026 [US3] Update the minimal-local and hosted-like-local runtime guidance in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/quickstart.md`
- [X] T027 [US3] Refactor local workflow naming, teardown instructions, and verification guidance across `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/quickstart.md` while keeping US3 tests green

**Checkpoint**: User Story 3 is independently demonstrable as a separate hosted-like local verification path that does not break the minimal local workflow.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, regression proof, and completion evidence across all stories.

- [X] T028 [P] Add regression coverage for infrastructure and documentation examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`
- [X] T029 Validate the operator quickstarts and contract docs in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/019-iac-foundation/quickstart.md`
- [X] T030 Run the full repository test suite with `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any failures before marking the feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2
- **Phase 4: US2**: Depends on Phase 2 and on US1 outputs being available for deployment handoff
- **Phase 5: US3**: Depends on Phase 2 and does not depend on US1 or US2
- **Phase 6: Polish**: Depends on all selected user stories being complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 and is the MVP
- **US2 (P2)**: Builds on the infrastructure outputs created by US1
- **US3 (P3)**: Starts after Phase 2 and remains independent of US1/US2 delivery timing

### Within Each User Story

- Write the listed tests first and confirm they fail before implementation
- Implement the minimum code and documentation required to satisfy the story
- Refactor only after story tests pass
- Keep story validation independent before moving to the next checkpoint
- Do not treat targeted runs as completion evidence; `pytest` is the final completion gate

### Dependency Graph

- `Setup -> Foundational -> US1 -> US2 -> Polish`
- `Setup -> Foundational -> US3 -> Polish`

### Parallel Opportunities

- `T002`, `T004`, and `T005` can run in parallel after `T001`
- In US1, `T009` and `T010` can run in parallel, then `T011`, `T012`, and `T013` can run in parallel
- In US2, `T016` and `T017` can run in parallel, then `T018` can proceed independently before `T019`
- In US3, `T022` and `T023` can run in parallel, then `T024` and `T025` can run in parallel
- US3 can be implemented in parallel with US1 once Phase 2 is complete

---

## Parallel Example: User Story 1

```bash
Task: "T009 [US1] Add contract coverage for required GCP resources and provisioning outputs in tests/contract/test_iac_foundation_contract.py"
Task: "T010 [US1] Add integration coverage for the operator provisioning workflow in tests/integration/test_iac_foundation_workflows.py"

Task: "T011 [US1] Define the Terraform provider and root variable contract in infrastructure/gcp/versions.tf and infrastructure/gcp/variables.tf"
Task: "T012 [US1] Define the Cloud Run service foundation, runtime identity, and secret integration resources in infrastructure/gcp/main.tf"
Task: "T013 [US1] Define the Redis-compatible durable session backend and exported outputs in infrastructure/gcp/session.tf and infrastructure/gcp/outputs.tf"
```

## Parallel Example: User Story 2

```bash
Task: "T016 [US2] Add contract coverage for the deployment handoff values consumed after infrastructure provisioning in tests/contract/test_iac_foundation_contract.py"
Task: "T017 [US2] Add integration coverage for the infrastructure-output-to-deployment-script workflow in tests/integration/test_iac_foundation_workflows.py"
```

## Parallel Example: User Story 3

```bash
Task: "T022 [US3] Add contract coverage for minimal-local versus hosted-like-local workflow guarantees in tests/contract/test_iac_foundation_contract.py"
Task: "T023 [US3] Add integration coverage for the minimal-local and hosted-like-local workflows in tests/integration/test_iac_foundation_workflows.py"

Task: "T024 [US3] Define the local Redis dependency stack in infrastructure/local/compose.yaml"
Task: "T025 [US3] Document hosted-like local environment variables and startup steps in infrastructure/local/.env.example and infrastructure/local/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the provisioning workflow independently
5. Stop for review before taking on deployment handoff or local hosted-like work

### Incremental Delivery

1. Setup and foundation first
2. Deliver US1 as the first valuable increment
3. Deliver US2 once infrastructure outputs are stable
4. Deliver US3 in parallel with US1 or after US2, depending on staffing
5. Finish with polish and full-suite proof

### Parallel Team Strategy

1. One developer completes Setup and Foundational work
2. After Phase 2:
   - Developer A takes US1
   - Developer B takes US3
3. When US1 stabilizes, Developer C takes US2
4. Team reconverges for polish and the final `pytest` run

---

## Notes

- All tasks follow the required checklist format: checkbox, task ID, optional `[P]`, required story label for story phases, and exact file paths
- Story tasks are scoped so each user story remains independently testable
- US1 is the suggested MVP scope
- US2 intentionally depends on US1 outputs; US3 does not
- The final completion gate is a full repository `pytest` run
