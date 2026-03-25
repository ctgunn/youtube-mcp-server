# Tasks: Cloud Run Public Reachability for Remote MCP

**Input**: Design documents from `/specs/021-cloud-run-reachability/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/quickstart.md), [cloud-run-public-access-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/contracts/cloud-run-public-access-contract.md), [hosted-reachability-verification-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/contracts/hosted-reachability-verification-contract.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when dependencies are satisfied and files do not overlap
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Every task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the shared task scaffolding and constants used by all implementation phases.

- [X] T001 Extend public-access shared terminology helpers in `src/mcp_server/infrastructure_contract.py`
- [X] T002 [P] Add base public-access unit test scaffolding in `tests/unit/test_cloud_run_config.py`
- [X] T003 [P] Create FND-021 contract test modules in `tests/contract/test_cloud_run_public_access_contract.py` and `tests/contract/test_hosted_reachability_verification_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared deployment and verification primitives that MUST exist before any user story can be completed.

**⚠️ CRITICAL**: No user story work should be considered complete until this phase is done.

- [X] T004 [P] Add failing unit tests for public invocation deployment inputs and metadata validation in `tests/unit/test_cloud_run_config.py` and `tests/unit/test_cloud_run_deploy_execution.py`
- [X] T005 [P] Add failing integration tests for shared deployment-record and verification-evidence fields in `tests/integration/test_cloud_run_deployment_metadata.py` and `tests/integration/test_cloud_run_verification_flow.py`
- [X] T006 Implement shared deployment input and evidence models for `public_invocation_intent`, `connection_point`, and failure-layer fields in `src/mcp_server/deploy.py`
- [X] T007 Implement verifier CLI support for public-access intent and evidence output in `scripts/verify_cloud_run_foundation.py`
- [X] T008 Refactor shared remediation and evidence serialization paths in `src/mcp_server/deploy.py` and `scripts/verify_cloud_run_foundation.py`

**Checkpoint**: Shared deployment and verification primitives are ready for story-specific work.

---

## Phase 3: User Story 1 - Reach the Hosted MCP Service from a Trusted Remote Consumer (Priority: P1) 🎯 MVP

**Goal**: Make the hosted service publicly reachable for trusted remote consumers while preserving successful authenticated MCP access on the same endpoint.

**Independent Test**: Deploy a hosted environment configured for public remote MCP access, run the verifier against the published service URL, confirm the reachability check succeeds first, and then confirm an authenticated `/mcp` request succeeds.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add contract coverage for public connection-point and public reachability guarantees in `tests/contract/test_hosted_reachability_verification_contract.py`
- [X] T010 [P] [US1] Add integration coverage for the successful public-and-authenticated hosted path in `tests/integration/test_cloud_run_verification_flow.py`

### Implementation for User Story 1

- [X] T011 [P] [US1] Add public invocation input and output fields to the GCP provider adapter in `infrastructure/gcp/variables.tf` and `infrastructure/gcp/outputs.tf`
- [X] T012 [P] [US1] Wire public reachability configuration and connection-point documentation in `infrastructure/gcp/main.tf` and `infrastructure/gcp/README.md`
- [X] T013 [US1] Implement reachability-first hosted verification checks and connection-point assertions in `src/mcp_server/deploy.py`
- [X] T014 [US1] Implement public-reachability verification flow and CLI arguments in `scripts/verify_cloud_run_foundation.py`
- [X] T015 [US1] Refactor the US1 verification path and keep the story tests green in `src/mcp_server/deploy.py` and `tests/integration/test_cloud_run_verification_flow.py`

**Checkpoint**: User Story 1 should independently prove that a trusted remote consumer can reach the hosted service publicly and then authenticate successfully.

---

## Phase 4: User Story 2 - Configure Public Access Intentionally and Reproducibly (Priority: P2)

**Goal**: Make public access an explicit, reviewable, and repeatable part of the hosted deployment workflow instead of an implicit platform default.

**Independent Test**: Starting from a deployment path that does not yet express public remote MCP intent, follow the documented GCP workflow, inspect the deployment record and docs, and confirm that public invocation intent and the published connection point are explicit in the review artifacts.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add contract coverage for intentional public invocation workflow requirements in `tests/contract/test_cloud_run_public_access_contract.py`
- [X] T017 [P] [US2] Add documentation example coverage for explicit public-access setup in `tests/integration/test_cloud_run_docs_examples.py`

### Implementation for User Story 2

- [X] T018 [P] [US2] Add public invocation examples and operator inputs to `infrastructure/gcp/terraform.tfvars.example` and `infrastructure/gcp/README.md`
- [X] T019 [P] [US2] Emit public-access intent and published connection point in deployment metadata in `src/mcp_server/deploy.py` and `tests/integration/test_cloud_run_deployment_metadata.py`
- [X] T020 [US2] Update deployment input parsing and command rendering for intentional public access in `src/mcp_server/deploy.py` and `tests/unit/test_cloud_run_config.py`
- [X] T021 [US2] Update the operator deployment workflow for intentional public access in `scripts/deploy_cloud_run.sh` and `README.md`
- [X] T022 [US2] Refactor public-access review wording and keep the story tests green in `README.md` and `infrastructure/gcp/README.md`

**Checkpoint**: User Story 2 should independently prove that public access is configured intentionally and leaves reviewable evidence in deployment and documentation artifacts.

---

## Phase 5: User Story 3 - Distinguish Reachability Failures from Authentication Failures (Priority: P3)

**Goal**: Make cloud-level denial and MCP-layer denial reproducibly distinguishable in verification evidence and operator diagnostics.

**Independent Test**: Run the hosted verification flow once against an environment that is not publicly reachable and once against a publicly reachable environment without valid MCP credentials, then confirm the evidence reports distinct failure layers and remediations.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add contract coverage for failure-layer evidence and remediation guidance in `tests/contract/test_hosted_reachability_verification_contract.py`
- [X] T024 [P] [US3] Add integration coverage for cloud-level denial versus MCP-layer denial in `tests/integration/test_cloud_run_verification_flow.py`
- [X] T025 [P] [US3] Add deployment asset regression coverage for denial diagnostics in `tests/integration/test_cloud_run_deployment_assets.py`

### Implementation for User Story 3

- [X] T026 [US3] Implement failure-layer, `request_reached_application`, and remediation evidence in `src/mcp_server/deploy.py`
- [X] T027 [US3] Preserve MCP-layer denial mapping while surfacing platform denial separately in `src/mcp_server/transport/http.py` and `src/mcp_server/security.py`
- [X] T028 [US3] Update hosted verification output and operator diagnostics examples in `scripts/verify_cloud_run_foundation.py` and `README.md`
- [X] T029 [US3] Refactor denial diagnostics and keep the story tests green in `src/mcp_server/deploy.py` and `scripts/verify_cloud_run_foundation.py`

**Checkpoint**: User Story 3 should independently prove that operators can tell whether a failure stopped at Cloud Run reachability or at MCP authentication.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize regression coverage, documentation validation, observability safety, and full-suite completion proof.

- [X] T030 [P] Add regression coverage for deploy execution and public-access defaults in `tests/unit/test_cloud_run_deploy_execution.py` and `tests/unit/test_cloud_run_security_gate.py`
- [X] T031 [P] Validate quickstart and operator-doc flows in `README.md`, `infrastructure/gcp/README.md`, and `specs/021-cloud-run-reachability/quickstart.md`
- [X] T032 Harden secret-safe verification and observability output in `src/mcp_server/observability.py` and `tests/integration/test_security_request_observability.py`
- [X] T033 Run the full repository test suite with `pytest` and resolve any failures in `tests/`, `src/mcp_server/`, `scripts/`, and `infrastructure/gcp/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies; start immediately.
- **Phase 2: Foundational**: Depends on Phase 1; blocks all user stories until shared deployment and verification primitives exist.
- **Phase 3: User Story 1**: Depends on Phase 2; forms the MVP.
- **Phase 4: User Story 2**: Depends on Phase 2; may reuse US1 deployment metadata changes but remains independently testable through operator workflow evidence.
- **Phase 5: User Story 3**: Depends on Phase 2; builds on shared verification primitives and may layer on US1 verification behavior.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational; no dependency on US2 or US3.
- **US2 (P2)**: Can start after Foundational; should integrate with existing deployment metadata but remain independently testable from its documentation and release-evidence workflow.
- **US3 (P3)**: Can start after Foundational; depends conceptually on the hosted verification path but remains independently testable via denial diagnostics.

### Within Each User Story

- Write failing contract and integration tests first.
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
- `T011` and `T012` can run in parallel for US1.
- `T016` and `T017` can run in parallel for US2.
- `T018` and `T019` can run in parallel for US2.
- `T023`, `T024`, and `T025` can run in parallel for US3.
- `T030`, `T031`, and `T032` can run in parallel before the final `pytest` run in `T033`.

## Parallel Example: User Story 1

```bash
# Run the US1 failing tests together:
Task: "Add contract coverage for public connection-point and public reachability guarantees in tests/contract/test_hosted_reachability_verification_contract.py"
Task: "Add integration coverage for the successful public-and-authenticated hosted path in tests/integration/test_cloud_run_verification_flow.py"

# Implement the US1 provider-adapter plumbing together:
Task: "Add public invocation input and output fields to the GCP provider adapter in infrastructure/gcp/variables.tf and infrastructure/gcp/outputs.tf"
Task: "Wire public reachability configuration and connection-point documentation in infrastructure/gcp/main.tf and infrastructure/gcp/README.md"
```

## Parallel Example: User Story 2

```bash
# Run the US2 red tests together:
Task: "Add contract coverage for intentional public invocation workflow requirements in tests/contract/test_cloud_run_public_access_contract.py"
Task: "Add documentation example coverage for explicit public-access setup in tests/integration/test_cloud_run_docs_examples.py"

# Implement the US2 operator workflow updates together:
Task: "Add public invocation examples and operator inputs to infrastructure/gcp/terraform.tfvars.example and infrastructure/gcp/README.md"
Task: "Emit public-access intent and published connection point in deployment metadata in src/mcp_server/deploy.py and tests/integration/test_cloud_run_deployment_metadata.py"
```

## Parallel Example: User Story 3

```bash
# Run the US3 failing diagnostics tests together:
Task: "Add contract coverage for failure-layer evidence and remediation guidance in tests/contract/test_hosted_reachability_verification_contract.py"
Task: "Add integration coverage for cloud-level denial versus MCP-layer denial in tests/integration/test_cloud_run_verification_flow.py"
Task: "Add deployment asset regression coverage for denial diagnostics in tests/integration/test_cloud_run_deployment_assets.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the public-and-authenticated path independently
5. Demo or ship the MVP if ready

### Incremental Delivery

1. Finish Setup and Foundational work once.
2. Deliver US1 as the MVP for public remote reachability.
3. Deliver US2 to make that reachability intentional and reproducible for operators.
4. Deliver US3 to complete the denial-diagnostics and remediation workflow.
5. Finish with cross-cutting regressions, docs validation, and the full `pytest` run.

### Parallel Team Strategy

1. One engineer completes Phase 1 and coordinates Phase 2 shared primitives.
2. After Foundational work is done:
   - Engineer A focuses on US1 verification and hosted path behavior.
   - Engineer B focuses on US2 provider-adapter and deployment workflow artifacts.
   - Engineer C focuses on US3 denial diagnostics and evidence modeling.
3. Merge into Phase 6 for final regression coverage and full-suite validation.

---

## Notes

- `[P]` tasks modify different files and are safe parallel candidates once dependencies are satisfied.
- `[US1]`, `[US2]`, and `[US3]` map directly to the stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/spec.md).
- Every story includes explicit Red, Green, and Refactor work.
- Targeted test runs are not completion proof; `pytest` in `T033` is the completion gate.
- The recommended MVP scope is **User Story 1 only** after Setup and Foundational work.
