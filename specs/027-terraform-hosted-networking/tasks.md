# Tasks: Terraform-Managed Hosted Networking for Durable Sessions

**Input**: Design documents from `/specs/027-terraform-hosted-networking/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared fixtures and examples used across the implementation

- [X] T001 Create shared managed-network Terraform output fixtures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py
- [X] T002 [P] Create shared managed-network deployment fixtures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py
- [X] T003 [P] Create shared managed-network verification fixtures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and test scaffolding that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing foundational contract coverage for managed networking inputs and outputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py
- [X] T005 [P] Add failing foundational handoff coverage for managed networking evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_handoff_contract.py
- [X] T006 [P] Add failing foundational documentation coverage for managed networking examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py
- [X] T007 Implement the shared managed-networking input model in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/terraform.tfvars.example
- [X] T008 Implement the shared managed-networking output contract in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/outputs.tf
- [X] T009 Extend deployment mapping and deployment-record models for managed networking evidence in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Provision Hosted Networking with Infrastructure Code (Priority: P1) 🎯 MVP

**Goal**: Make the supported GCP durable-session network layer fully Terraform-managed so operators no longer need to create VPC, subnet, or connectivity resources manually.

**Independent Test**: Apply the supported GCP infrastructure definition in a clean environment and confirm the required VPC, subnet, Cloud Run connectivity path, and Redis network relationship are created without separate manual networking steps.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add contract coverage for Terraform-managed VPC, subnet, and Cloud Run connectivity resources in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py
- [X] T011 [P] [US1] Add integration coverage for clean-environment durable-session network provisioning in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py

### Implementation for User Story 1

- [X] T012 [US1] Implement Terraform-managed VPC and subnet resources in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/network.tf
- [X] T013 [US1] Implement the managed Cloud Run connectivity resource in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/network.tf
- [X] T014 [US1] Wire Cloud Run and Redis to the managed networking resources in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/main.tf and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/session.tf
- [X] T015 [US1] Refactor Terraform validations and managed-network example inputs in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/terraform.tfvars.example

**Checkpoint**: User Story 1 should now provision the hosted network layer independently and serve as the MVP for this feature.

---

## Phase 4: User Story 2 - Feed Hosted Networking Outputs into Deployment and Verification (Priority: P2)

**Goal**: Extend the Terraform-output handoff and deployment evidence so rollout and hosted verification can trace the managed network path without manual reconstruction.

**Independent Test**: Export infrastructure outputs after a successful apply and confirm the deployment and hosted verification flow can identify the managed connectivity path directly from the reviewed handoff artifacts.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add unit coverage for managed-networking Terraform output mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py
- [X] T017 [P] [US2] Add contract coverage for managed-network output handoff into deployment evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_handoff_contract.py
- [X] T018 [P] [US2] Add integration coverage for managed-network deployment evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_handoff.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py

### Implementation for User Story 2

- [X] T019 [US2] Export managed-network references for deploy and verify handoff in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/outputs.tf
- [X] T020 [US2] Extend deployment input normalization and deployment-record serialization for managed-network evidence in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T021 [US2] Update deploy and hosted-verification handoff examples in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md and /Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh
- [X] T022 [US2] Refactor managed-network output naming and evidence wording in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md

**Checkpoint**: User Story 2 should now expose a reviewable managed-network handoff from Terraform reconciliation through deployment evidence and hosted verification.

---

## Phase 5: User Story 3 - Remove Manual Networking Prerequisites from the GCP Runbook (Priority: P3)

**Goal**: Update operator documentation so the supported GCP path documents Terraform-managed networking before application rollout and keeps local workflows clearly separate.

**Independent Test**: Review the supported GCP runbook and top-level operator guidance and confirm they no longer instruct manual VPC, subnet, or Cloud Run connectivity creation for durable sessions.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add contract coverage for manual-network-prerequisite removal in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_runtime_session_connectivity_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py
- [X] T024 [P] [US3] Add integration coverage for GCP runbook boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_bootstrap_docs.py

### Implementation for User Story 3

- [X] T025 [US3] Update the supported GCP runbook to remove manual VPC, subnet, and connectivity prerequisites in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md
- [X] T026 [US3] Update top-level local-versus-hosted networking guidance in /Users/ctgunn/Projects/youtube-mcp-server/README.md and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md
- [X] T027 [US3] Refactor remediation and ownership-boundary language across infrastructure examples in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/terraform.tfvars.example and /Users/ctgunn/Projects/youtube-mcp-server/README.md

**Checkpoint**: All user stories should now be independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cross-story cleanup

- [X] T028 [P] Validate the documented operator flows against /Users/ctgunn/Projects/youtube-mcp-server/specs/027-terraform-hosted-networking/quickstart.md
- [X] T029 Run targeted lint and managed-network regression checks from /Users/ctgunn/Projects/youtube-mcp-server against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_handoff_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py
- [X] T030 Run the full repository test suite from /Users/ctgunn/Projects/youtube-mcp-server using `pytest` and resolve failures in impacted files before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. Blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and uses the managed-network resources from User Story 1.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and should land after User Story 1 defines the supported managed-network path.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependency on other user stories.
- **User Story 2 (P2)**: Depends on User Story 1 because the output handoff must describe the managed network path created there.
- **User Story 3 (P3)**: Depends on User Story 1 for the final supported workflow and should align with User Story 2 handoff terminology where possible.

### Within Each User Story

- Tests MUST be written and fail before implementation begins.
- Infrastructure and contract changes come before deployment and documentation updates.
- Refactor only after the story tests pass.
- Before marking the story or the feature complete, run the full repository test suite and fix failures.

### Dependency Graph

- **Phase 1** → **Phase 2** → **US1**
- **US1** → **US2**
- **US1** → **US3**
- **US2 + US3** → **Phase 6**

---

## Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001.
- **Foundational**: T005 and T006 can run in parallel after T004; T007 and T008 can proceed in parallel once failing tests are in place.
- **User Story 1**: T010 and T011 can run in parallel; T012 and T013 can be split if the managed network and connectivity resource definitions are kept separate in `/infrastructure/gcp/network.tf`.
- **User Story 2**: T016, T017, and T018 can run in parallel; T019 and T020 can proceed in parallel once the expected output names are settled.
- **User Story 3**: T023 and T024 can run in parallel; T025 and T026 can run in parallel because they touch different documentation surfaces.

## Parallel Example: User Story 1

```bash
Task: "Add contract coverage for Terraform-managed VPC, subnet, and Cloud Run connectivity resources in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py"
Task: "Add integration coverage for clean-environment durable-session network provisioning in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py"
```

```bash
Task: "Implement Terraform-managed VPC and subnet resources in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/network.tf"
Task: "Implement the managed Cloud Run connectivity resource in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/network.tf"
```

## Parallel Example: User Story 2

```bash
Task: "Add unit coverage for managed-networking Terraform output mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_iac_foundation_inputs.py"
Task: "Add contract coverage for managed-network output handoff into deployment evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_handoff_contract.py"
Task: "Add integration coverage for managed-network deployment evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_handoff.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add contract coverage for manual-network-prerequisite removal in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_runtime_session_connectivity_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py"
Task: "Add integration coverage for GCP runbook boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_bootstrap_docs.py"
```

```bash
Task: "Update the supported GCP runbook to remove manual VPC, subnet, and connectivity prerequisites in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md"
Task: "Update top-level local-versus-hosted networking guidance in /Users/ctgunn/Projects/youtube-mcp-server/README.md and /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate that a clean supported GCP environment can provision the managed durable-session network layer without manual prerequisites.
5. Stop and review before expanding the output handoff and documentation surfaces.

### Incremental Delivery

1. Finish Setup + Foundational to stabilize shared fixtures, output mapping, and test expectations.
2. Deliver User Story 1 to create the Terraform-managed hosted network layer.
3. Deliver User Story 2 to expose that managed path through deployment evidence and hosted verification.
4. Deliver User Story 3 to remove stale manual-prerequisite guidance and preserve local-first documentation boundaries.
5. Finish with cross-cutting validation and the full repository test run.

### Parallel Team Strategy

1. One developer completes Setup + Foundational.
2. After User Story 1 starts, split network-resource authoring and provisioning-test authoring.
3. After User Story 1 lands:
   - Developer A: User Story 2 output handoff and deployment evidence.
   - Developer B: User Story 3 operator documentation and boundary cleanup.
4. Rejoin for Phase 6 validation and full-suite regression coverage.

---

## Notes

- All tasks use the required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- `[P]` marks tasks that can run in parallel without depending on incomplete work in the same files.
- User stories remain independently testable:
  - **US1**: Clean Terraform provisioning of the managed durable-session network layer.
  - **US2**: Reviewable output handoff from Terraform into deployment and verification.
  - **US3**: Runbook and README guidance with manual networking prerequisites removed.
- Do not treat targeted test runs as completion evidence. The final completion gate is T030.
