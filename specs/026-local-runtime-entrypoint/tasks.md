# Tasks: Local Runtime Ergonomics and Environment Entry Point

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/contracts/local-runtime-entrypoint-contract.md`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `[US1]`, `[US2]`, `[US3]`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared validation surfaces for the local-runtime workflow changes.

- [x] T001 Create a focused script-regression test module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_dev_local_script.py`
- [x] T002 [P] Create a feature-specific workflow coverage module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared script behavior and test scaffolding that every user story depends on.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [x] T003 Add failing regression tests for missing `.env.local` handling and hosted-mode selection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_dev_local_script.py`
- [x] T004 [P] Add failing integration checks for canonical entrypoint references and shared local workflow expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py`
- [x] T005 Implement deterministic `.env.local` loading, hosted-mode override handling, and operator-facing failure messaging in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/dev_local.sh`
- [x] T006 Refactor minimal-local and hosted-like mode branching for clarity and testability in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/dev_local.sh`

**Checkpoint**: Foundation ready. User stories can proceed in priority order and remain independently testable.

---

## Phase 3: User Story 1 - Start locally in one step (Priority: P1) 🎯 MVP

**Goal**: Make one canonical repository command the obvious minimal local startup path.

**Independent Test**: From a prepared repository workspace, run `bash scripts/dev_local.sh` and confirm the local server starts with baseline defaults from `.env.local` without any cloud infrastructure or hosted deployment inputs.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T007 [P] [US1] Add failing README assertions for the canonical `bash scripts/dev_local.sh` minimal startup flow in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [x] T008 [P] [US1] Add failing minimal-local workflow assertions for startup evidence and no-cloud prerequisites in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py`

### Implementation for User Story 1

- [x] T009 [US1] Update the minimal local runtime section to use `bash scripts/dev_local.sh` as the canonical startup path in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [x] T010 [US1] Document baseline `.env.local` expectations and local-start success checks in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [x] T011 [US1] Refactor duplicated minimal-local startup wording into one source of truth in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`

**Checkpoint**: User Story 1 should be fully functional and testable on its own.

---

## Phase 4: User Story 2 - Exercise hosted-like local behavior when needed (Priority: P2)

**Goal**: Preserve a simple companion workflow for Redis-backed hosted-like local verification without turning it into the default path.

**Independent Test**: Start `docker compose -f infrastructure/local/compose.yaml up -d`, run `LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh`, and verify the hosted-like local workflow is documented, uses the same entrypoint, and includes clear recovery guidance when the dependency is missing.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T012 [P] [US2] Add failing contract assertions for hosted-like companion workflow guarantees and failure guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [x] T013 [P] [US2] Add failing integration assertions for dependency bootstrap, entrypoint reuse, and shutdown flow in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py`

### Implementation for User Story 2

- [x] T014 [US2] Update hosted-like local verification instructions, dependency bootstrap, and failure recovery in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`
- [x] T015 [US2] Align hosted-like local example values and override guidance with the companion workflow in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/.env.example`
- [x] T016 [US2] Refactor hosted-like local wording and command sequencing across `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`

**Checkpoint**: User Story 2 should be independently testable without relying on User Story 1 implementation details beyond the shared entrypoint.

---

## Phase 5: User Story 3 - Understand which settings belong to local versus hosted execution (Priority: P3)

**Goal**: Make the baseline local defaults, hosted-like overrides, and hosted deployment-only inputs easy to distinguish.

**Independent Test**: Review `.env.local`, the root README, and the hosted-like local docs and confirm a maintainer can separate baseline local variables, hosted-like local overrides, and hosted deployment inputs without ambiguity.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T017 [P] [US3] Add failing documentation-boundary assertions for local versus hosted variables in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`
- [x] T018 [P] [US3] Add failing workflow-boundary assertions for baseline defaults versus hosted-like overrides in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py`

### Implementation for User Story 3

- [x] T019 [US3] Reorganize baseline local variable groups and override comments in `/Users/ctgunn/Projects/youtube-mcp-server/.env.local`
- [x] T020 [US3] Document baseline local variables, hosted-like overrides, and hosted deployment-only inputs in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [x] T021 [US3] Refactor variable terminology for consistency across `/Users/ctgunn/Projects/youtube-mcp-server/.env.local`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/.env.example`

**Checkpoint**: All three user stories should now be independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and full-suite proof.

- [x] T022 [P] Validate the quickstart flows against `/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/quickstart.md`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/dev_local.sh`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/README.md`
- [x] T023 [P] Remove redundant assertions and tighten regression coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_dev_local_script.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py`
- [x] T024 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and other touched files before completion
- [x] T025 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any remaining lint issues in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/dev_local.sh`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/.env.local`, and related touched files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies. Start immediately.
- **Phase 2: Foundational**: Depends on Phase 1. Blocks all user stories because the shared startup script behavior and feature-specific test scaffolding must be in place first.
- **Phase 3: User Story 1**: Depends on Phase 2.
- **Phase 4: User Story 2**: Depends on Phase 2. Recommended after US1 because it extends the canonical entrypoint story, but it is independently testable.
- **Phase 5: User Story 3**: Depends on Phase 2. Recommended after US1 and US2 because it clarifies the variable model already documented there, but it is independently testable.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependency Graph

- **US1 (P1)**: Starts after Phase 2. No hard dependency on other user stories.
- **US2 (P2)**: Starts after Phase 2. No hard dependency on US1, but benefits from US1 README alignment already being present.
- **US3 (P3)**: Starts after Phase 2. No hard dependency on US1 or US2, but benefits from the final local-workflow terminology established there.

Recommended completion order:

1. **US1** for MVP
2. **US2** for hosted-like local verification
3. **US3** for variable-boundary clarity

### Within Each User Story

- Tests must be written and fail before implementation.
- Documentation and contract assertions should fail before script or README changes begin.
- Shared script behavior changes should land before story-specific docs that depend on them.
- Refactor only after the story tests pass.
- Full repository validation with `pytest` is required before the feature is complete.

---

## Parallel Opportunities

- **Setup**: `T001` and `T002` touch different new test files and can run in parallel.
- **Foundational**: `T003` and `T004` can run in parallel before `T005`; `T006` follows `T005`.
- **US1**: `T007` and `T008` can run in parallel; `T009` and `T010` are sequential README updates; `T011` follows them as refactor.
- **US2**: `T012` and `T013` can run in parallel; `T014` and `T015` touch different local-workflow files and can proceed in parallel once tests are in place; `T016` follows as cross-doc refactor.
- **US3**: `T017` and `T018` can run in parallel; `T019` and `T020` can proceed in parallel once tests are written; `T021` follows as terminology refactor.
- **Polish**: `T022` and `T023` can run in parallel before the final repository validation tasks.

---

## Parallel Example: User Story 1

```bash
Task: "T007 [US1] Add failing README assertions for the canonical bash scripts/dev_local.sh minimal startup flow in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
Task: "T008 [US1] Add failing minimal-local workflow assertions for startup evidence and no-cloud prerequisites in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py"
```

## Parallel Example: User Story 2

```bash
Task: "T012 [US2] Add failing contract assertions for hosted-like companion workflow guarantees and failure guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_iac_foundation_contract.py"
Task: "T013 [US2] Add failing integration assertions for dependency bootstrap, entrypoint reuse, and shutdown flow in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_agnostic_infrastructure_workflows.py"
Task: "T015 [US2] Align hosted-like local example values and override guidance with the companion workflow in /Users/ctgunn/Projects/youtube-mcp-server/infrastructure/local/.env.example"
```

## Parallel Example: User Story 3

```bash
Task: "T017 [US3] Add failing documentation-boundary assertions for local versus hosted variables in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_iac_foundation_workflows.py"
Task: "T018 [US3] Add failing workflow-boundary assertions for baseline defaults versus hosted-like overrides in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_local_runtime_entrypoint.py"
Task: "T019 [US3] Reorganize baseline local variable groups and override comments in /Users/ctgunn/Projects/youtube-mcp-server/.env.local"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the minimal local startup path independently with `bash scripts/dev_local.sh`
5. Stop and review before expanding scope

### Incremental Delivery

1. Finish Setup and Foundational work so the shared script and tests are stable.
2. Deliver US1 and validate the canonical minimal local startup path.
3. Deliver US2 and validate the hosted-like local companion flow.
4. Deliver US3 and validate variable-boundary clarity across docs and defaults.
5. Run Phase 6 polish and the full repository validation commands.

### Parallel Team Strategy

1. One developer completes Setup and Foundational tasks.
2. After Phase 2:
   - Developer A can own US1 README and minimal-local workflow tasks.
   - Developer B can own US2 hosted-like local docs and contract tasks.
   - Developer C can own US3 local-defaults and variable-boundary tasks.
3. Merge story work back together for the final polish and repository validation phase.

---

## Notes

- All tasks follow the required checklist format.
- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase.
- User story labels map directly to the priorities in `spec.md`.
- Each user story includes explicit Red, Green, and Refactor work.
- Do not treat targeted test runs as final completion evidence; `pytest` and `ruff check .` are required before completion.
