# Tasks: FND-012 Hosted Runtime Migration for Streaming MCP

**Input**: Design documents from `~/Projects/youtube-mcp-server/specs/012-hosted-runtime-migration/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the dependency and packaging baseline needed for the runtime migration.

- [X] T001 Create ASGI dependency manifest in `~/Projects/youtube-mcp-server/pyproject.toml`
- [X] T002 [P] Update container dependency installation for the ASGI runtime in `~/Projects/youtube-mcp-server/Dockerfile`
- [X] T003 [P] Document local dependency bootstrap for the migrated runtime in `~/Projects/youtube-mcp-server/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared runtime plumbing that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Create shared ASGI app factory scaffolding in `~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T005 [P] Add runtime lifecycle state helpers for startup and shutdown in `~/Projects/youtube-mcp-server/src/mcp_server/health.py`
- [X] T006 [P] Add runtime configuration support for the migrated entrypoint in `~/Projects/youtube-mcp-server/src/mcp_server/config.py`
- [X] T007 [P] Add shared hosted request logging hooks for the migrated runtime in `~/Projects/youtube-mcp-server/src/mcp_server/observability.py`
- [X] T008 Refactor application bootstrap wiring to serve both runtime lifecycle and MCP transport in `~/Projects/youtube-mcp-server/src/mcp_server/app.py`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Run Streaming MCP Reliably in Production (Priority: P1) 🎯 MVP

**Goal**: Serve the existing MCP streaming contract through a production-appropriate hosted runtime on Cloud Run.

**Independent Test**: Deploy the migrated service, initialize an MCP session, run a streamed `tools/call`, and verify concurrent sessions stay isolated without runtime-induced transport failures.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add hosted stream runtime contract coverage in `~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py`
- [X] T010 [P] [US1] Add hosted MCP route continuity checks for the migrated runtime in `~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`
- [X] T011 [P] [US1] Add concurrent streaming session integration coverage in `~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py`
- [X] T012 [P] [US1] Add hosted route execution coverage for ASGI-backed `/mcp` handling in `~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement the FastAPI/Uvicorn-hosted `/mcp` route adapter in `~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T014 [US1] Preserve streaming session isolation and SSE response bridging in `~/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py`
- [X] T015 [US1] Preserve hosted request classification and response mapping for the migrated runtime in `~/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T016 [US1] Update Cloud Run startup command for the migrated hosted runtime in `~/Projects/youtube-mcp-server/Dockerfile`
- [X] T017 [US1] Update deployment invocation for the migrated runtime in `~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`
- [X] T018 [US1] Refactor hosted runtime request bridging while keeping US1 tests green in `~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`

**Checkpoint**: User Story 1 should now be independently functional and deployable as the MVP.

---

## Phase 4: User Story 2 - Preserve Operational Confidence During Migration (Priority: P2)

**Goal**: Keep liveness, readiness, startup, shutdown, and observable runtime behavior correct after the runtime migration.

**Independent Test**: Start the migrated service locally and in hosted execution, verify readiness stays false until startup completes, then confirm `/health` and `/ready` remain correct through steady-state and shutdown transitions.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add readiness transition contract checks for the migrated runtime in `~/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py`
- [X] T020 [P] [US2] Add runtime observability contract checks for migrated request logging in `~/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py`
- [X] T021 [P] [US2] Add runtime lifecycle unit coverage for startup and shutdown states in `~/Projects/youtube-mcp-server/tests/unit/test_readiness_state.py`
- [X] T022 [P] [US2] Add runtime profile unit coverage for the ASGI entrypoint in `~/Projects/youtube-mcp-server/tests/unit/test_runtime_profiles.py`
- [X] T023 [P] [US2] Add readiness and hosted lifecycle integration coverage in `~/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py`
- [X] T024 [P] [US2] Add hosted request observability integration coverage for the migrated runtime in `~/Projects/youtube-mcp-server/tests/integration/test_request_observability.py`

### Implementation for User Story 2

- [X] T025 [US2] Implement explicit startup and shutdown lifecycle transitions in `~/Projects/youtube-mcp-server/src/mcp_server/health.py`
- [X] T026 [US2] Implement migrated runtime readiness gating and configuration validation in `~/Projects/youtube-mcp-server/src/mcp_server/config.py`
- [X] T027 [US2] Implement request correlation and structured runtime logging for the ASGI entrypoint in `~/Projects/youtube-mcp-server/src/mcp_server/observability.py`
- [X] T028 [US2] Wire lifecycle state into the hosted entrypoint for `/health` and `/ready` in `~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T029 [US2] Refactor lifecycle and observability plumbing while keeping US2 tests green in `~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`

**Checkpoint**: User Story 2 should be independently testable without depending on US3 documentation changes.

---

## Phase 5: User Story 3 - Verify the Hosted Runtime the Same Way in Local and Hosted Environments (Priority: P3)

**Goal**: Provide a clear, repeatable verification path for the migrated runtime in local and Cloud Run environments.

**Independent Test**: Follow the documented local validation flow and the hosted verification flow, confirming both complete the same core MCP checks and produce evidence without undocumented steps.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T030 [P] [US3] Add deployment asset integration coverage for the migrated runtime startup path in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py`
- [X] T031 [P] [US3] Add hosted verification integration coverage for the migrated runtime evidence flow in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T032 [P] [US3] Add deployment metadata integration coverage for migrated runtime settings in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py`
- [X] T033 [P] [US3] Add documentation example integration coverage for local and hosted runtime commands in `~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`

### Implementation for User Story 3

- [X] T034 [US3] Update hosted verification script for the migrated runtime workflow in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T035 [US3] Update deployment metadata capture for the migrated runtime in `~/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T036 [US3] Document local and Cloud Run verification flows for the migrated runtime in `~/Projects/youtube-mcp-server/README.md`
- [X] T037 [US3] Align quickstart validation steps with the implemented runtime commands in `~/Projects/youtube-mcp-server/specs/012-hosted-runtime-migration/quickstart.md`
- [X] T038 [US3] Refactor verification messaging and evidence output while keeping US3 tests green in `~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`

**Checkpoint**: All user stories should now be independently functional and verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete regression, cleanup, and release-readiness work that spans multiple user stories.

- [X] T039 [P] Run full regression coverage for the runtime migration in `~/Projects/youtube-mcp-server/tests/`
- [X] T040 [P] Add or update cross-story runtime configuration assertions in `~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_config.py`
- [X] T041 Clean up stale `http.server` runtime references across `~/Projects/youtube-mcp-server/src/mcp_server/` and `~/Projects/youtube-mcp-server/README.md`
- [X] T042 Execute quickstart validation and record final evidence in `~/Projects/youtube-mcp-server/specs/012-hosted-runtime-migration/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies. Start immediately.
- **Phase 2: Foundational**: Depends on Phase 1. Blocks all user stories.
- **Phase 3: User Story 1**: Depends on Phase 2. This is the MVP slice.
- **Phase 4: User Story 2**: Depends on Phase 2 and should be validated against the migrated runtime from US1.
- **Phase 5: User Story 3**: Depends on Phase 2 and should be completed after the runtime behavior from US1 and US2 is stable.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational. No dependency on US2 or US3.
- **US2 (P2)**: Starts after Foundational. Uses the migrated runtime entrypoint from US1 but remains independently testable through health/readiness and observability flows.
- **US3 (P3)**: Starts after Foundational. Depends on implemented runtime behavior from US1 and operational behavior from US2 to finalize verification assets and documentation.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Runtime and shared state changes come before deployment/doc updates in the same story.
- Refactor tasks happen only after story tests pass.
- Each story must pass its independent test before moving to the next priority.

### Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`.
- `T005`, `T006`, and `T007` can run in parallel after `T004`.
- US1 test tasks `T009` through `T012` can run in parallel.
- US2 test tasks `T019` through `T024` can run in parallel.
- US3 test tasks `T030` through `T033` can run in parallel.
- Polish tasks `T039` and `T040` can run in parallel after stories complete.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together
Task: "Add hosted stream runtime contract coverage in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add hosted MCP route continuity checks for the migrated runtime in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "Add concurrent streaming session integration coverage in ~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add hosted route execution coverage for ASGI-backed /mcp handling in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together
Task: "Add readiness transition contract checks for the migrated runtime in ~/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py"
Task: "Add runtime observability contract checks for migrated request logging in ~/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py"
Task: "Add runtime lifecycle unit coverage for startup and shutdown states in ~/Projects/youtube-mcp-server/tests/unit/test_readiness_state.py"
Task: "Add runtime profile unit coverage for the ASGI entrypoint in ~/Projects/youtube-mcp-server/tests/unit/test_runtime_profiles.py"
Task: "Add readiness and hosted lifecycle integration coverage in ~/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py"
Task: "Add hosted request observability integration coverage for the migrated runtime in ~/Projects/youtube-mcp-server/tests/integration/test_request_observability.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together
Task: "Add deployment asset integration coverage for the migrated runtime startup path in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py"
Task: "Add hosted verification integration coverage for the migrated runtime evidence flow in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "Add deployment metadata integration coverage for migrated runtime settings in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_metadata.py"
Task: "Add documentation example integration coverage for local and hosted runtime commands in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate the hosted streaming runtime on Cloud Run as the MVP.

### Incremental Delivery

1. Setup + Foundational establish the ASGI runtime baseline.
2. US1 delivers reliable hosted streaming behavior.
3. US2 adds operational confidence around readiness and observability.
4. US3 completes local/hosted verification and documentation parity.
5. Polish closes regression and cleanup gaps across all slices.

### Parallel Team Strategy

1. One developer handles Phase 1 and coordinates Phase 2 bootstrap.
2. After Phase 2:
   Developer A can lead US1 runtime serving changes.
   Developer B can prepare US2 readiness and observability tests.
   Developer C can prepare US3 verification and documentation tests.
3. Implementation merges in priority order: US1, then US2, then US3.

---

## Notes

- Every task uses the required checklist format with task ID, optional `[P]`, optional `[USx]`, and an exact file path.
- User story tasks are scoped so each story remains independently testable.
- The suggested MVP scope is Phase 3 only: User Story 1.
