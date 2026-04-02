# Tasks: FND-006 Cloud Run Foundation Deployment

**Input**: Design documents from `/specs/006-cloud-run-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout at repository root with `src/`, `tests/`, and top-level deployment/docs files

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the deployment asset and verification scaffolding for this feature

- [X] T001 Create deployment asset scaffolding in `~/Projects/youtube-mcp-server/Dockerfile`, `~/Projects/youtube-mcp-server/.dockerignore`, and `~/Projects/youtube-mcp-server/scripts/`
- [X] T002 [P] Create hosted verification scaffolding in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py` and `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T003 [P] Create deployment contract test scaffolding in `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py` and `~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared deployment configuration and verification primitives required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing unit coverage for deployment input validation in `~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_config.py`
- [X] T005 [P] Add failing contract coverage for required deployment settings and verification evidence in `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py`
- [X] T006 [P] Add failing integration coverage for verification ordering and failure gating in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T007 Implement shared deployment and verification data structures in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T008 [P] Implement verification request helpers and evidence serialization in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T009 [P] Document shared deployment inputs and evidence requirements in `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/quickstart.md` and `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/contracts/cloud-run-foundation-contract.md`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Deploy a Reproducible Service Revision (Priority: P1) 🎯 MVP

**Goal**: Give operators a repeatable way to build and deploy one hosted revision with explicit runtime settings

**Independent Test**: Execute the documented deployment workflow in a clean environment and confirm the produced revision exposes the configured runtime identity, scaling bounds, concurrency, timeout, and endpoint URL

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add contract test for required deployment workflow fields in `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py`
- [X] T011 [P] [US1] Add integration test for deployment asset assembly in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py`

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement container build definition for the MCP service in `~/Projects/youtube-mcp-server/Dockerfile`
- [X] T013 [P] [US1] Implement container ignore rules for reproducible builds in `~/Projects/youtube-mcp-server/.dockerignore`
- [X] T014 [US1] Implement deployment command assembly and revision setting validation in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T015 [US1] Implement operator deployment script with explicit runtime settings in `~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`
- [X] T016 [US1] Document the reproducible deployment workflow and required inputs in `~/Projects/youtube-mcp-server/README.md` and `~/Projects/youtube-mcp-server/.env.example`
- [X] T017 [US1] Refactor deployment packaging and workflow defaults while keeping `~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_config.py`, `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py`, and `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py` green

**Checkpoint**: User Story 1 is independently deployable and reviewable as the MVP

---

## Phase 4: User Story 2 - Verify Operational Readiness After Deployment (Priority: P1)

**Goal**: Let operators prove the hosted revision is live and ready before exposing it to clients

**Independent Test**: Run hosted verification against a deployed endpoint and confirm `/healthz` and `/readyz` pass for valid configuration and fail with machine-readable evidence for invalid configuration

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add contract test for liveness/readiness verification evidence in `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py`
- [X] T019 [P] [US2] Add integration test for hosted `/healthz` and `/readyz` verification flow in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

### Implementation for User Story 2

- [X] T020 [P] [US2] Implement liveness and readiness verification steps in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T021 [US2] Implement readiness failure classification and evidence recording in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T022 [US2] Document hosted health/readiness verification and remediation flow in `~/Projects/youtube-mcp-server/README.md` and `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/quickstart.md`
- [X] T023 [US2] Refactor health/readiness verification output structure while keeping `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py` and `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py` green

**Checkpoint**: User Stories 1 and 2 both work independently, and operators can stop at readiness verification

---

## Phase 5: User Story 3 - Prove End-to-End MCP Baseline Behavior (Priority: P2)

**Goal**: Let MCP clients prove the hosted endpoint can initialize, list tools, and invoke a baseline tool successfully

**Independent Test**: Run hosted MCP verification against a ready deployed endpoint and confirm initialize, list-tools, and one baseline tool call all succeed with recorded evidence

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add contract test for hosted MCP verification stages in `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py`
- [X] T025 [P] [US3] Add integration test for initialize, list-tools, and baseline tool verification in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

### Implementation for User Story 3

- [X] T026 [P] [US3] Implement hosted MCP initialize and list-tools verification steps in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T027 [P] [US3] Implement baseline tool invocation verification and pass/fail evidence capture in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T028 [US3] Implement MCP-stage failure gating and overall verification result calculation in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T029 [US3] Document hosted MCP verification commands and expected evidence in `~/Projects/youtube-mcp-server/README.md` and `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/quickstart.md`
- [X] T030 [US3] Refactor hosted verification sequencing and evidence formatting while keeping `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`, `~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py`, and `~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py` green

**Checkpoint**: All user stories are independently functional and the full hosted verification flow passes

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression, documentation alignment, and release-ready validation across all stories

- [X] T031 [P] Add regression coverage for deployment documentation examples in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [X] T032 Update feature documentation and captured execution guidance in `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/quickstart.md` and `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/tasks.md`
- [X] T033 Run full regression validation and record results in `~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and uses deployment artifacts from US1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and requires hosted verification primitives from US2
- **Polish (Phase 6)**: Depends on completion of all targeted user stories

### User Story Dependencies

- **US1**: Can start immediately after Phase 2 and is the suggested MVP
- **US2**: Requires a deployable revision from US1 but remains independently testable once that revision exists
- **US3**: Requires a ready hosted revision from US2 and remains independently testable through hosted MCP verification

### Within Each User Story

- Red tests before Green implementation
- Implementation before Refactor
- Refactor before moving to the next dependent story
- Re-run affected automated suites before marking the story complete

### Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`
- `T005`, `T006`, `T008`, and `T009` can run in parallel after `T004`
- `T010` and `T011` can run in parallel for US1
- `T012` and `T013` can run in parallel for US1
- `T018` and `T019` can run in parallel for US2
- `T024` and `T025` can run in parallel for US3
- `T026` and `T027` can run in parallel for US3

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 Red tasks together
Task: "Add contract test for required deployment workflow fields in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py"
Task: "Add integration test for deployment asset assembly in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py"

# Launch User Story 1 Green tasks that touch separate files
Task: "Implement container build definition for the MCP service in ~/Projects/youtube-mcp-server/Dockerfile"
Task: "Implement container ignore rules for reproducible builds in ~/Projects/youtube-mcp-server/.dockerignore"
```

## Parallel Example: User Story 2

```bash
# Launch User Story 2 Red tasks together
Task: "Add contract test for liveness/readiness verification evidence in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py"
Task: "Add integration test for hosted /healthz and /readyz verification flow in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
```

## Parallel Example: User Story 3

```bash
# Launch User Story 3 Red tasks together
Task: "Add contract test for hosted MCP verification stages in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py"
Task: "Add integration test for initialize, list-tools, and baseline tool verification in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"

# Launch User Story 3 Green tasks that touch separate functions in the verification script
Task: "Implement hosted MCP initialize and list-tools verification steps in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py"
Task: "Implement baseline tool invocation verification and pass/fail evidence capture in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate one reproducible hosted deployment
5. Stop for review before hosted verification expansion

### Incremental Delivery

1. Finish Setup + Foundational to establish shared deployment primitives
2. Deliver US1 for reproducible hosted revision creation
3. Deliver US2 for hosted health/readiness verification
4. Deliver US3 for hosted MCP initialize/list-tools/baseline-tool verification
5. Finish with Polish and full regression validation

### Parallel Team Strategy

1. One developer completes Setup and Foundational tasks
2. A second developer can take US1 documentation/assets while shared verification helpers are stabilized
3. After US1, one developer can focus on US2 readiness evidence while another prepares US3 MCP verification tests

---

## Notes

- All tasks use the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` for story phases, and exact file paths
- Suggested MVP scope is **Phase 3 / User Story 1**
- User-story independence is preserved by assigning a standalone verification goal and checkpoint to each story
