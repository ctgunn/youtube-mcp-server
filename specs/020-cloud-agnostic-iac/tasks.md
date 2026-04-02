# Tasks: Cloud-Agnostic Infrastructure Module Strategy

**Input**: Design documents from `~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/`
**Prerequisites**: [plan.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/plan.md), [spec.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/spec.md), [research.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/research.md), [data-model.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md), [quickstart.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md), `~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project paths are used for this feature: `src/`, `tests/`, `infrastructure/`, `scripts/`, and `specs/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repository for portability work without changing the current deployment model

- [X] T001 Review and align the feature quickstart in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md with the implementation plan in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/plan.md
- [X] T002 [P] Create task-target placeholder notes for shared capability mapping in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/research.md
- [X] T003 [P] Confirm the existing portability baseline in ~/Projects/youtube-mcp-server/infrastructure/gcp/README.md and ~/Projects/youtube-mcp-server/infrastructure/local/README.md before code changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared vocabulary and regression protection that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add a shared portability fixture/helper module in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py
- [X] T005 [P] Add foundational contract assertions for shared capability categories in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py
- [X] T006 [P] Add foundational integration assertions for portability documentation touchpoints in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py
- [X] T007 Define the shared portability section headings and canonical terms in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md and ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/execution-mode-contract.md
- [X] T008 Align the feature planning docs with foundational portability terms in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/plan.md, ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/research.md, and ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Define a Shared Platform Contract Across Providers (Priority: P1) 🎯 MVP

**Goal**: Define one provider-neutral infrastructure contract that reinterprets the current GCP and local workflows through shared platform capabilities

**Independent Test**: Reviewers can read the shared contract and verify that hosted runtime, networking, identity, secrets, observability, and durable session support are defined once and map cleanly to the current GCP path without changing the application deployment model

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add contract tests for shared platform capability coverage in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py
- [X] T010 [P] [US1] Add integration tests for shared-platform wording in hosted infrastructure docs in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py

### Implementation for User Story 1

- [X] T011 [P] [US1] Refine the shared capability inventory and workflow guarantees in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md
- [X] T012 [P] [US1] Expand the shared contract entity definitions and validation rules in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md
- [X] T013 [US1] Reframe the current GCP foundation as the primary provider adapter in ~/Projects/youtube-mcp-server/infrastructure/gcp/README.md
- [X] T014 [US1] Update the operator-facing hosted deployment narrative to use shared-platform terminology in ~/Projects/youtube-mcp-server/README.md
- [X] T015 [US1] Refactor shared-platform cross-references and remove duplicate provider-specific language in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md and ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/research.md

**Checkpoint**: User Story 1 should now be independently reviewable as the MVP portability contract

---

## Phase 4: User Story 2 - Add or Adapt a Provider Path Without Rewriting the Platform Model (Priority: P2)

**Goal**: Prove portability by documenting a secondary provider adapter that maps to the shared contract without introducing a new deployment model

**Independent Test**: A maintainer can review the AWS adapter artifacts and verify that the same shared capabilities and deployment-model expectations are preserved, with partial or unsupported areas called out explicitly

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add contract tests for the AWS provider adapter mapping in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py
- [X] T017 [P] [US2] Add integration tests for secondary-provider workflow guidance in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py

### Implementation for User Story 2

- [X] T018 [P] [US2] Flesh out provider adapter fields, limitations, and mapping states in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md
- [X] T019 [P] [US2] Complete the secondary provider contract with capability-by-capability mapping expectations in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/aws-provider-adapter-contract.md
- [X] T020 [US2] Document the provider-adapter workflow and portability boundary in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md
- [X] T021 [US2] Add provider-expansion guidance and adapter-boundary decisions in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/research.md
- [X] T022 [US2] Refactor shared versus provider-specific terminology across ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md and ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/aws-provider-adapter-contract.md while keeping tests green

**Checkpoint**: User Stories 1 and 2 should both be independently reviewable and testable

---

## Phase 5: User Story 3 - Preserve Local-First Development While Explaining Hosted Variants (Priority: P3)

**Goal**: Keep minimal local execution first-class while relating minimal local, hosted-like local, and hosted deployment to the same shared contract

**Independent Test**: A developer can read the execution-mode docs and repository README and verify that minimal local remains cloud-free, hosted-like local remains a separate Redis-backed path, and hosted deployment clearly depends on a provider adapter

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T023 [P] [US3] Add contract tests for execution-mode separation and local-first guarantees in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py
- [X] T024 [P] [US3] Add integration tests for minimal-local versus hosted-like-local documentation in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py

### Implementation for User Story 3

- [X] T025 [P] [US3] Complete execution-mode definitions and failure guarantees in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/execution-mode-contract.md
- [X] T026 [P] [US3] Map execution-mode entities and prerequisites in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md
- [X] T027 [US3] Update local-first portability guidance in ~/Projects/youtube-mcp-server/infrastructure/local/README.md
- [X] T028 [US3] Update the root developer workflow narrative to preserve minimal local and hosted-like local boundaries in ~/Projects/youtube-mcp-server/README.md
- [X] T029 [US3] Refactor execution-mode walkthroughs and validation steps in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md while keeping tests green

**Checkpoint**: All user stories should now be independently functional and reviewable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story regression protection, documentation alignment, and full-suite validation

- [X] T030 [P] Add regression assertions for shared-platform documentation links in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py
- [X] T031 [P] Add unit coverage for any shared capability mapping helpers introduced during implementation in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_agnostic_infrastructure_helpers.py
- [X] T032 Synchronize final wording across ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/spec.md, ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/plan.md, and ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/tasks.md
- [X] T033 Run quickstart validation against ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/quickstart.md and fix any inconsistencies in ~/Projects/youtube-mcp-server/README.md, ~/Projects/youtube-mcp-server/infrastructure/gcp/README.md, and ~/Projects/youtube-mcp-server/infrastructure/local/README.md
- [X] T034 Run the full repository test suite with `pytest` from ~/Projects/youtube-mcp-server and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2 and defines the MVP portability contract
- **User Story 2 (P2)**: Starts after US1 establishes the shared contract vocabulary
- **User Story 3 (P3)**: Starts after US1 establishes the shared contract vocabulary; can proceed in parallel with US2 once the shared contract is stable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Contract and documentation updates come before cross-file refactors
- Refactor only after story-specific tests pass
- Before marking the feature complete, run the full repository suite with `pytest`

### Story Completion Order

1. **US1**: Shared platform contract across providers
2. **US2**: Secondary provider adapter proof
3. **US3**: Local-first execution-mode alignment

### Parallel Opportunities

- `T002` and `T003` can run in parallel during setup
- `T005` and `T006` can run in parallel during the foundational phase
- `T009` and `T010` can run in parallel for US1 Red work
- `T011` and `T012` can run in parallel for US1 Green work
- `T016` and `T017` can run in parallel for US2 Red work
- `T018` and `T019` can run in parallel for US2 Green work
- `T023` and `T024` can run in parallel for US3 Red work
- `T025` and `T026` can run in parallel for US3 Green work
- Once US1 is complete, US2 and US3 can be staffed in parallel

---

## Parallel Example: User Story 1

```bash
# Launch US1 Red tests together
Task: "Add contract tests for shared platform capability coverage in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py"
Task: "Add integration tests for shared-platform wording in hosted infrastructure docs in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py"

# Launch US1 Green documentation/model work together
Task: "Refine the shared capability inventory and workflow guarantees in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/shared-platform-contract.md"
Task: "Expand the shared contract entity definitions and validation rules in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md"
```

## Parallel Example: User Story 2

```bash
# Launch US2 Red tests together
Task: "Add contract tests for the AWS provider adapter mapping in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py"
Task: "Add integration tests for secondary-provider workflow guidance in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py"

# Launch US2 Green design work together
Task: "Flesh out provider adapter fields, limitations, and mapping states in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md"
Task: "Complete the secondary provider contract with capability-by-capability mapping expectations in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/aws-provider-adapter-contract.md"
```

## Parallel Example: User Story 3

```bash
# Launch US3 Red tests together
Task: "Add contract tests for execution-mode separation and local-first guarantees in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_agnostic_infrastructure_contract.py"
Task: "Add integration tests for minimal-local versus hosted-like-local documentation in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py"

# Launch US3 Green design work together
Task: "Complete execution-mode definitions and failure guarantees in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/contracts/execution-mode-contract.md"
Task: "Map execution-mode entities and prerequisites in ~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/data-model.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the shared platform contract independently

### Incremental Delivery

1. Complete Setup + Foundational to establish shared portability vocabulary
2. Deliver US1 as the MVP portability contract
3. Deliver US2 to prove secondary-provider portability
4. Deliver US3 to lock local-first execution-mode behavior
5. Finish Polish with regression coverage and a full `pytest` run

### Parallel Team Strategy

1. One engineer completes Setup + Foundational
2. After US1 is stable:
   - Engineer A: US2 provider adapter work
   - Engineer B: US3 execution-mode work
3. Merge in Polish after both stories pass their own tests

---

## Notes

- All tasks use the required checklist format with task ID, optional `[P]`, optional `[US#]`, and exact file paths
- US1 is the suggested MVP scope
- Tests are included for foundational work and for every user story
- The final completion gate is a passing full repository `pytest` run
